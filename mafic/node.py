# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
import warnings
from asyncio import Event, TimeoutError, create_task, sleep, wait_for
from logging import getLogger
from typing import TYPE_CHECKING, cast

from aiohttp import ClientSession, WSMsgType
from yarl import URL

from mafic.typings.http import TrackWithInfo

from .__libraries import MISSING, ExponentialBackoff, dumps, loads
from .errors import TrackLoadException
from .ip import (
    BalancingIPRoutePlannerStatus,
    NanoIPRoutePlannerStatus,
    RotatingIPRoutePlannerStatus,
    RotatingNanoIPRoutePlannerStatus,
)
from .playlist import Playlist
from .plugin import Plugin
from .region import VOICE_TO_REGION, Group, Region, VoiceRegion
from .stats import NodeStats
from .track import Track
from .warnings import UnsupportedVersionWarning

if TYPE_CHECKING:
    from asyncio import Task
    from typing import Any, Sequence

    from aiohttp import ClientWebSocketResponse

    from .__libraries import Client, VoiceServerUpdatePayload
    from .filter import Filter
    from .ip import RoutePlannerStatus
    from .player import Player
    from .typings import (
        BalancingIPRouteDetails,
        Coro,
        EventPayload,
        IncomingMessage,
        NanoIPRouteDetails,
        OutgoingMessage,
        OutgoingParams,
        PluginData,
        RotatingIPRouteDetails,
        RotatingNanoIPRouteDetails,
        RoutePlannerStatus as RoutePlannerStatusPayload,
        TrackInfo,
        TrackLoadingResult,
        UpdatePlayerParams,
        UpdatePlayerPayload,
    )

_log = getLogger(__name__)
URL_REGEX = re.compile(r"https?://")

__all__ = ("Node",)


def _wrap_regions(
    regions: Sequence[Group | Region | VoiceRegion] | None,
) -> list[Region] | None:
    if not regions:
        return None

    actual_regions: list[Region] = []

    for item in regions:
        if isinstance(item, Group):
            actual_regions.extend(item.value)
        elif isinstance(item, Region):
            actual_regions.append(item)
        elif isinstance(
            item, VoiceRegion
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            actual_regions.append(VOICE_TO_REGION[item.value])
        else:
            raise TypeError(
                f"Expected Group, Region, or VoiceRegion, got {type(item)!r}."
            )

    return actual_regions


class Node:
    __slots__ = (
        "__password",
        "__session",
        "_available",
        "_client",
        "_heartbeat",
        "_host",
        "_label",
        "_port",
        "_resume_key",
        "_secure",
        "_timeout",
        "_ready",
        "_rest_uri",
        "_session_id",
        "_stats",
        "_ws",
        "_ws_uri",
        "_ws_task",
        "players",
        "regions",
        "shard_ids",
    )

    def __init__(
        self,
        *,
        host: str,
        port: int,
        label: str,
        password: str,
        client: Client,
        secure: bool = False,
        heartbeat: int = 30,
        timeout: float = 10,
        session: ClientSession | None = None,
        resume_key: str | None = None,
        regions: Sequence[Group | Region | VoiceRegion] | None = None,
        shard_ids: Sequence[int] | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._label = label
        self.__password = password
        self._secure = secure
        self._heartbeat = heartbeat
        self._timeout = timeout
        self._client = client
        self.__session = session
        self.shard_ids: Sequence[int] | None = shard_ids
        self.regions: list[Region] | None = _wrap_regions(regions)

        self._rest_uri = URL.build(scheme=f"http{'s'*secure}", host=host, port=port)
        self._ws_uri = URL.build(scheme=f"ws{'s'*secure}", host=host, port=port)
        self._resume_key = resume_key or f"{host}:{port}:{label}"

        self._ws: ClientWebSocketResponse | None = None
        self._ws_task: Task[None] | None = None

        self._available = False
        self._ready = Event()

        self.players: dict[int, Player] = {}

        self._stats: NodeStats | None = None
        self._session_id: str | None = None

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def label(self) -> str:
        return self._label

    @property
    def client(self) -> Client:
        return self._client

    @property
    def secure(self) -> bool:
        return self._secure

    @property
    def stats(self) -> NodeStats | None:
        return self._stats

    @property
    def available(self) -> bool:
        return self._available

    @property
    def weight(self) -> float:
        if self._stats is None:
            # Stats haven't been set yet, so we'll just return a high value.
            # This is so we can properly balance known nodes.
            # If stats sending is turned off
            # - that's on the user
            # - they likely have done it on all if they have multiple, so it is equal
            return 6.63e34

        stats = self._stats

        players = stats.playing_player_count

        # These are exponential equations.

        # Load is *basically* a percentage (I know it isn't but it is close enough).

        # | cores | load | weight |
        # |-------|------|--------|
        # | 1     | 0.1  | 16     |
        # | 1     | 0.5  | 114    |
        # | 1     | 0.75 | 388    |
        # | 1     | 1    | 1315   |
        # | 3     | 0.1  | 12     |
        # | 3     | 1    | 51     |
        # | 3     | 2    | 259    |
        # | 3     | 3    | 1315   |
        cpu = 1.05 ** (100 * (stats.cpu.system_load / stats.cpu.cores)) * 10 - 10

        # | null frames | weight |
        # | ----------- | ------ |
        # | 10          | 30     |
        # | 20          | 62     |
        # | 100         | 382    |
        # | 250         | 1456   |

        frame_stats = stats.frame_stats
        if frame_stats is None:
            null = 0
            deficit = 0
        else:
            null = 1.03 ** (frame_stats.nulled / 6) * 600 - 600
            deficit = 1.03 ** (frame_stats.deficit / 6) * 600 - 600

        # High memory usage isnt bad, but we generally don't want to overload it.
        # Especially due to the chance of regular GC pauses.

        # | memory usage | weight |
        # | ------------ | ------ |
        # | 96%          | 0      |
        # | 97%          | 9      |
        # | 98%          | 99     |
        # | 99%          | 999    |
        # | 99.5%        | 3161   |
        # | 100%         | 9999   |

        mem_stats = stats.memory
        mem = max(10 ** (100 * (mem_stats.used / mem_stats.reservable) - 96), 1) - 1

        return players + cpu + null + deficit + mem

    async def _check_version(self) -> None:
        if self.__session is None:
            self.__session = await self._create_session()

        async with self.__session.get(self._rest_uri / "version") as resp:
            # Only the major and minor are needed.
            json = await resp.json()
            version: str = json["version"]
            major, minor, _ = version.split(".", maxsplit=2)
            major = int(major)
            minor = int(minor)

            if major != 3:
                raise RuntimeError(
                    f"Unsupported lavalink version {version} (expected 3.7.x)"
                )
            elif minor < 7:
                raise RuntimeError(
                    f"Unsupported lavalink version {version} (expected 3.7.x)"
                )
            elif minor > 7:
                message = UnsupportedVersionWarning.message
                warnings.warn(message, UnsupportedVersionWarning)

            self._rest_uri /= "/v3"
            self._ws_uri /= "/v3/websocket"

    async def _connect_to_websocket(
        self, headers: dict[str, str], session: ClientSession
    ) -> None:
        try:
            self._ws = (
                await session.ws_connect(  # pyright: ignore[reportUnknownMemberType]
                    self._ws_uri,
                    timeout=self._timeout,
                    heartbeat=self._heartbeat,
                    headers=headers,
                )
            )
        except Exception as e:
            _log.error(
                "Failed to connect to lavalink at %s: %s",
                self._rest_uri,
                e,
                extra={"label": self._label},
            )
            raise

    async def connect(self) -> None:
        _log.info("Waiting for client to be ready...", extra={"label": self._label})
        await self._client.wait_until_ready()
        assert self._client.user is not None

        if self.__session is None:
            self.__session = await self._create_session()

        session = self.__session

        headers: dict[str, str] = {
            "Authorization": self.__password,
            "User-Id": str(self._client.user.id),
            "Client-Name": f"Mafic/{__import__('mafic').__version__}",
            "Resume-Key": self._resume_key,
        }

        _log.debug("Checking lavalink version...", extra={"label": self._label})
        await self._check_version()

        _log.info(
            "Connecting to lavalink at %s...",
            self._rest_uri,
            extra={"label": self._label},
        )
        await self._connect_to_websocket(headers=headers, session=session)
        _log.info("Connected to lavalink.", extra={"label": self._label})

        _log.debug(
            "Creating task to send configuration to resume with key %s",
            self._resume_key,
            extra={"label": self._label},
        )
        create_task(self.configure_resuming())

        _log.info(
            "Creating task for websocket listener...", extra={"label": self._label}
        )
        self._ws_task = create_task(
            self._ws_listener(), name=f"mafic node {self._label}"
        )

        try:
            _log.debug("Waiting for ready", extra={"label": self._label})
            await wait_for(self._ready.wait(), timeout=self._timeout)
        except TimeoutError:
            _log.error(
                "Timed out waiting for node to become ready.",
                extra={"label": self._label},
            )
            raise
        else:
            _log.info(
                "Node %s is now available.", self._label, extra={"label": self._label}
            )
            self._available = True

    async def _ws_listener(self) -> None:
        backoff = ExponentialBackoff()

        if self._ws is None:
            _log.error(
                "No websocket was found, aborting listener.",
                extra={"label": self._label},
            )
            raise RuntimeError(
                "Websocket is not connected but attempted to listen, report this."
            )

        # To catch closing messages, we cannot use async for.
        while True:
            msg = await self._ws.receive()

            _log.debug("Received message from websocket.", extra={"label": self._label})

            # Please aiohttp, fix your typehints.
            _type: WSMsgType = msg.type  # pyright: ignore[reportUnknownMemberType]

            if _type is WSMsgType.CLOSED:
                self._available = False
                close_code = self._ws.close_code
                self._ws = None

                wait_time = backoff.delay()
                _log.warn(
                    "Websocket was closed from host %s port %s with RFC 6455 code %s. "
                    "Reconnecting in %.2fs",
                    self._host,
                    self._port,
                    close_code,
                    wait_time,
                    extra={"label": self._label},
                )

                await sleep(wait_time)
                create_task(self.connect())
                return
            else:
                _log.debug(
                    "Creating task to handle websocket message.",
                    extra={"label": self._label},
                )
                create_task(self._handle_msg(msg.json(loads=loads)))

    async def _handle_msg(self, data: IncomingMessage) -> None:
        _log.debug("Received event with op %s", data["op"])
        _log.debug("Event data: %s", data)

        if data["op"] == "playerUpdate":
            guild_id = int(data["guildId"])
            player = self.players.get(guild_id)

            if player is None:
                _log.error(
                    "Could not find player for guild %s, discarding event.", guild_id
                )
                return

            player.update_state(data["state"])
        elif data["op"] == "stats":
            self._stats = NodeStats(data)
        elif data["op"] == "event":
            await self._handle_event(data)
        elif data["op"] == "ready":
            resumed = data["resumed"]
            session_id = data["sessionId"]

            if resumed:
                _log.info(
                    "Successfully resumed connection with lavalink.",
                    extra={"label": self._label},
                )

            _log.debug(
                "Received session ID %s", session_id, extra={"label": self._label}
            )
            self._session_id = session_id
            self._ready.set()
        else:
            # Of course pyright considers this to be `Never`, so this is to keep types.
            op = cast(str, data["op"])
            _log.warn("Unknown incoming message op code %s", op)

    async def _handle_event(self, data: EventPayload) -> None:
        if data["type"] == "WebSocketClosedEvent":
            # TODO:
            ...
        elif data["type"] == "TrackStartEvent":
            # We do not care about track starts, the user is already aware of it.
            return
        elif data["type"] == "TrackEndEvent":
            # TODO:
            ...
        elif data["type"] == "TrackExceptionEvent":
            # TODO:
            ...
        elif data["type"] == "TrackStuckEvent":
            # TODO:
            ...
        else:
            # Pyright expects this to never happen, so do I, I really hope.
            # Nobody expects the Spanish Inquisition, neither does pyright.

            event_type = cast(str, data["type"])
            _log.warning("Unknown incoming event type %s", event_type)

    def voice_update(
        self,
        guild_id: int,
        session_id: str,
        data: VoiceServerUpdatePayload,
    ) -> Coro[None]:
        _log.debug(
            "Sending player update to lavalink with data %s.",
            data,
            extra={"label": self._label, "guild": guild_id},
        )
        if data["endpoint"] is None:
            raise ValueError("Discord did not provide an endpoint.")

        return self.__request(
            "PATCH",
            f"/sessions/{self._session_id}/players/{guild_id}",
            {
                "voice": {
                    "sessionId": session_id,
                    "endpoint": data["endpoint"],
                    "token": data["token"],
                },
            },
        )

    def configure_resuming(self) -> Coro[None]:
        _log.info(
            "Sending resume configuration to lavalink with resume key %s.",
            self._resume_key,
            extra={"label": self._label},
        )

        return self.__request(
            "PATCH",
            f"/sessions/{self._session_id}",
            {
                "resumingKey": self._resume_key,
                "timeout": 60,
            },
        )

    def destroy(self, guild_id: int) -> Coro[None]:
        _log.debug("Sending request to destroy player", extra={"label": self._label})

        return self.__request(
            "DELETE", f"/sessions/{self._session_id}/players/{guild_id}"
        )

    def update(
        self,
        *,
        guild_id: int,
        track: Track | None = MISSING,
        position: int | None = None,
        end_time: int | None = None,
        volume: int | None = None,
        no_replace: bool | None = None,
        pause: bool | None = None,
        filter: Filter | None = None,
    ) -> Coro[None]:
        data: UpdatePlayerPayload = {}

        if track is not MISSING:
            data["encodedTrack"] = track.identifier if track is not None else None

        if position is not None:
            data["position"] = position

        if end_time is not None:
            data["endTime"] = end_time

        if volume is not None:
            data["volume"] = volume

        if pause is not None:
            data["paused"] = pause

        if filter is not None:
            data["filters"] = filter.payload

        if no_replace is not None:
            query: UpdatePlayerParams | None = {"noReplace": no_replace}
        else:
            query = None

        _log.debug(
            "Sending player update to lavalink with data %s.",
            data,
            extra={"label": self._label, "guild": guild_id},
        )

        return self.__request(
            "PATCH",
            f"/sessions/{self._session_id}/players/{guild_id}",
            data,
            query,
        )

    async def _create_session(self) -> ClientSession:
        return ClientSession(json_serialize=dumps)

    async def __request(
        self,
        method: str,
        path: str,
        json: OutgoingMessage | None = None,
        params: OutgoingParams | None = None,
    ) -> Any:
        if self.__session is None:
            self.__session = await self._create_session()

        session = self.__session
        uri = self._rest_uri / path

        async with session.request(
            method,
            uri,
            json=json,
            params=params,
            headers={"Authorization": self.__password},
        ) as resp:
            if not (200 <= resp.status < 300):
                # TODO: raise proper error
                raise RuntimeError(f"Got status code {resp.status} from lavalink.")

            _log.debug(
                "Received status %s from lavalink from path %s", resp.status, path
            )

            json = await resp.json(loads=loads)
            _log.debug("Received raw data %s", json)
            return json

    async def fetch_tracks(
        self, query: str, *, search_type: str
    ) -> list[Track] | Playlist | None:
        if not URL_REGEX.match(query):
            query = f"{search_type}:{query}"

        # TODO: handle errors from lavalink
        data: TrackLoadingResult = await self.__request(
            "GET", "/loadtracks", params={"identifier": query}
        )

        if data["loadType"] == "NO_MATCHES":
            return []
        elif data["loadType"] == "TRACK_LOADED":
            return [Track.from_data_with_info(data["tracks"][0])]
        elif data["loadType"] == "PLAYLIST_LOADED":
            return Playlist(info=data["playlistInfo"], tracks=data["tracks"])
        elif data["loadType"] == "SEARCH_RESULT":
            return [Track.from_data_with_info(track) for track in data["tracks"]]
        elif data["loadType"] == "LOAD_FAILED":
            raise TrackLoadException.from_data(data["exception"])
        else:
            _log.warning("Unknown load type recieved: %s", data["loadType"])

    async def decode_track(self, track: str) -> Track:
        # TODO: handle errors from lavalink
        info: TrackInfo = await self.__request(
            "GET", "/decodetrack", params={"encodedTrack": track}
        )

        return Track.from_data(track=track, info=info)

    async def decode_tracks(self, tracks: list[str]) -> list[Track]:
        track_data: list[TrackWithInfo] = await self.__request(
            "POST", "/decodetracks", json=tracks
        )

        return [Track.from_data_with_info(track) for track in track_data]

    async def fetch_plugins(self) -> list[Plugin]:
        plugins: list[PluginData] = await self.__request("GET", "/plugins")

        return [Plugin.from_data(plugin) for plugin in plugins]

    async def fetch_route_planner_status(self) -> RoutePlannerStatus | None:
        data: RoutePlannerStatusPayload = await self.__request(
            "GET", "/routeplanner/status"
        )

        if data["class"] == "RotatingIpRoutePlanner":
            return RotatingIPRoutePlannerStatus(
                cast(RotatingIPRouteDetails, data["details"])
            )
        elif data["class"] == "NanoIpRoutePlanner":
            return NanoIPRoutePlannerStatus(cast(NanoIPRouteDetails, data["details"]))
        elif data["class"] == "RotatingNanoIpRoutePlanner":
            return RotatingNanoIPRoutePlannerStatus(
                cast(RotatingNanoIPRouteDetails, data["details"])
            )
        elif data["class"] == "BalancingIpRoutePlanner":
            return BalancingIPRoutePlannerStatus(
                cast(BalancingIPRouteDetails, data["details"])
            )
        elif data["class"] is None:
            return None
        else:
            raise RuntimeError(f"Unknown route planner class {data['class']}.")

    async def unmark_failed_address(self, address: str) -> None:
        await self.__request(
            "POST", "/routeplanner/free/address", json={"address": address}
        )

    async def unmark_all_addresses(self) -> None:
        await self.__request("POST", "/routeplanner/free/all")
