# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from asyncio import create_task, sleep
from logging import getLogger
from typing import TYPE_CHECKING, cast

from aiohttp import ClientSession, WSMsgType

from mafic.typings.http import TrackWithInfo

from .__libraries import ExponentialBackoff, dumps, loads
from .errors import TrackLoadException
from .ip import (
    BalancingIPRoutePlannerStatus,
    NanoIPRoutePlannerStatus,
    RotatingIPRoutePlannerStatus,
    RotatingNanoIPRoutePlannerStatus,
)
from .playlist import Playlist
from .plugin import Plugin
from .track import Track

if TYPE_CHECKING:
    from asyncio import Task
    from typing import Any

    from aiohttp import ClientWebSocketResponse

    from .__libraries import Client, VoiceServerUpdatePayload
    from .filter import Filter
    from .ip import RoutePlannerStatus
    from .player import Player
    from .typings import (
        BalancingIPRouteDetails,
        Coro,
        EventPayload,
        GetTracks,
        IncomingMessage,
        NanoIPRouteDetails,
        OutgoingMessage,
        PlayPayload,
        PluginData,
        RotatingIPRouteDetails,
        RotatingNanoIPRouteDetails,
        RoutePlannerStatus as RoutePlannerStatusPayload,
        TrackInfo,
    )

_log = getLogger(__name__)
URL_REGEX = re.compile(r"https?://")


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
        "_rest_uri",
        "_ws",
        "_ws_uri",
        "_ws_task",
        "players",
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

        self._rest_uri = f"http{'s' if secure else ''}://{host}:{port}"
        self._ws_uri = f"ws{'s' if secure else ''}://{host}:{port}"
        self._resume_key = resume_key or f"{host}:{port}:{label}"

        self._ws: ClientWebSocketResponse | None = None
        self._ws_task: Task[None] | None = None

        self._available = False

        self.players: dict[int, Player] = {}

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

        _log.info(
            "Connecting to lavalink at %s...",
            self._rest_uri,
            extra={"label": self._label},
        )

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

    async def __send(self, data: OutgoingMessage) -> None:
        if self._ws is None:
            raise RuntimeError(
                "Websocket is not connected but attempted to send, report this."
            )

        _log.debug("Sending message to websocket.", extra={"label": self._label})
        await self._ws.send_json(data, dumps=dumps)

    async def _handle_msg(self, data: IncomingMessage) -> None:
        _log.debug("Received event with op %s", data["op"])

        if data["op"] == "playerUpdate":
            guild_id = int(data["guildId"])
            player = self.players.get(guild_id)

            if player is None:
                _log.error(
                    "Could not find player for guild %s, discarding event.", guild_id
                )

            # TODO: update player
        elif data["op"] == "stats":
            # TODO
            ...
        elif data["op"] == "event":
            await self._handle_event(data)
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
            _log.warn("Unknown incoming event type %s", event_type)

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

        return self.__send(
            {
                "op": "voiceUpdate",
                "guildId": str(guild_id),
                "sessionId": session_id,
                "event": data,
            }
        )

    def configure_resuming(self) -> Coro[None]:
        _log.info(
            "Sending resume configuration to lavalink with resume key %s.",
            self._resume_key,
            extra={"label": self._label},
        )

        return self.__send(
            {
                "op": "configureResuming",
                "key": self._resume_key,
                "timeout": 60,
            }
        )

    def destroy(self, guild_id: int) -> Coro[None]:
        _log.debug("Sending request to destroy player", extra={"label": self._label})

        return self.__send(
            {
                "op": "destroy",
                "guildId": str(guild_id),
            }
        )

    def play(
        self,
        *,
        guild_id: int,
        track: str,
        start_time: int | None,
        end_time: int | None,
        volume: int | None,
        no_replace: bool | None,
        pause: bool | None,
    ) -> Coro[None]:
        data: PlayPayload = {
            "op": "play",
            "guildId": str(guild_id),
            "track": track,
        }

        if start_time is not None:
            data["startTime"] = str(start_time)

        if end_time is not None:
            data["endTime"] = str(end_time)

        if volume is not None:
            data["volume"] = str(volume)

        if no_replace is not None:
            data["noReplace"] = no_replace

        if pause is not None:
            data["pause"] = pause

        return self.__send(data)

    def stop(self, guild_id: int) -> Coro[None]:
        return self.__send(
            {
                "op": "stop",
                "guildId": str(guild_id),
            }
        )

    def pause(self, guild_id: int, pause: bool) -> Coro[None]:
        return self.__send(
            {
                "op": "pause",
                "guildId": str(guild_id),
                "pause": pause,
            }
        )

    def seek(self, guild_id: int, position: int) -> Coro[None]:
        return self.__send(
            {
                "op": "seek",
                "guildId": str(guild_id),
                "position": position,
            }
        )

    def volume(self, guild_id: int, volume: int) -> Coro[None]:
        return self.__send(
            {
                "op": "volume",
                "guildId": str(guild_id),
                "volume": volume,
            }
        )

    def filter(self, guild_id: int, filter: Filter) -> Coro[None]:
        return self.__send(
            {
                "op": "filters",
                "guildId": str(guild_id),
                # Lavalink uses inline filter properties, this adds every one of them.
                **filter.payload,
            }
        )

    # TODO: API routes:

    async def _create_session(self) -> ClientSession:
        return ClientSession(json_serialize=dumps)

    async def __request(
        self,
        method: str,
        path: str,
        json: Any | None = None,
        params: dict[str, str] | None = None,
    ) -> Any:
        if self.__session is None:
            self.__session = await self._create_session()

        session = self.__session
        uri = self._rest_uri + path

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
        data: GetTracks = await self.__request(
            "GET", "/loadtracks", params={"identifier": query}
        )

        if data["loadType"] == "NO_MATCHES":
            return []
        elif data["loadType"] == "TRACK_LOADED":
            return [Track.from_data(**data["tracks"][0])]
        elif data["loadType"] == "PLAYLIST_LOADED":
            return Playlist(info=data["playlistInfo"], tracks=data["tracks"])
        elif data["loadType"] == "SEARCH_RESULT":
            return [Track.from_data(**track) for track in data["tracks"]]
        elif data["loadType"] == "LOAD_FAILED":
            raise TrackLoadException(**data["exception"])
        else:
            _log.warning("Unknown load type recieved: %s", data["loadType"])

    async def decode_track(self, track: str) -> Track:
        # TODO: handle errors from lavalink
        info: TrackInfo = await self.__request(
            "GET", "/decodetrack", params={"track": track}
        )

        return Track.from_data(track=track, info=info)

    async def decode_tracks(self, tracks: list[str]) -> list[Track]:
        track_data: list[TrackWithInfo] = await self.__request(
            "POST", "/decodetracks", json=tracks
        )

        return [Track.from_data(**track) for track in track_data]

    async def fetch_plugins(self) -> list[Plugin]:
        plugins: list[PluginData] = await self.__request("GET", "/plugins")

        return [Plugin(**plugins) for plugins in plugins]

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
