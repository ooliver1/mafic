# SPDX-License-Identifier: MIT
# pyright: reportImportCycles=false
# Player import.

from __future__ import annotations

import re
import warnings
from asyncio import Event, TimeoutError, create_task, gather, sleep, wait_for
from logging import getLogger
from traceback import print_exc
from typing import TYPE_CHECKING, Generic, cast

import aiohttp
import yarl

from mafic.typings.http import TrackWithInfo

from .__libraries import MISSING, ExponentialBackoff, dumps, loads
from .errors import *
from .ip import (
    BalancingIPRoutePlannerStatus,
    NanoIPRoutePlannerStatus,
    RotatingIPRoutePlannerStatus,
    RotatingNanoIPRoutePlannerStatus,
)
from .playlist import Playlist
from .plugin import Plugin
from .region import Group, Region, VoiceRegion
from .stats import NodeStats
from .track import Track
from .type_variables import ClientT
from .warnings import *

if TYPE_CHECKING:
    from asyncio import Task
    from typing import Any, Literal, Sequence

    from aiohttp import ClientWebSocketResponse

    from .__libraries import VoiceServerUpdatePayload
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
        Player as PlayerPayload,
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
) -> list[VoiceRegion] | None:
    """Converts a list of voice regions, regions and groups into a list of regions.

    Parameters
    ----------
    regions:
        The list of regions to convert.

    Returns
    -------
    :class:`list`\\[:class:`Region`] | None
        The converted list of regions.
    """

    if not regions:
        return None

    actual_regions: list[VoiceRegion] = []

    for item in regions:
        if isinstance(item, Group):
            for region in item.value:
                actual_regions.append(region.value)
        elif isinstance(item, Region):
            actual_regions.append(item.value)
        elif isinstance(
            item, VoiceRegion
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            actual_regions.append(item)
        else:
            raise TypeError(
                f"Expected Group, Region, or VoiceRegion, got {type(item)!r}."
            )

    return actual_regions


class Node(Generic[ClientT]):
    """Represents a Lavalink node.

    .. warning::

        This class should not be instantiated manually.
        Instead, use :meth:`NodePool.create_node`.

    Parameters
    ----------
    host:
        The host of the node, used to connect.
    port:
        The port of the node, used to connect.
    label:
        The label of the node, used to identify the node.
    password:
        The password of the node, used to authenticate the connection.
    client:
        The client that the node is attached to.
    secure:
        Whether the node is using a secure connection.
        This determines whether the node uses HTTP or HTTPS, WS or WSS.
    heartbeat:
        The interval at which the node will send a heartbeat to the client.
    timeout:
        The amount of time the node will wait for a response before raising a timeout
        error.
    session: :data:`~typing.Optional`\\[:class:`aiohttp.ClientSession`]
        The session to use for the node.
        If not provided, a new session will be created.
    resume_key:
        The key to use when resuming the node.
        If not provided, the key will be generated from the host, port and label.
    regions:
        The voice regions that the node can be used in.
        This is used to determine when to use this node.
    shard_ids:
        The shard IDs that the node can be used in.
        This is used to determine when to use this node.

    Attributes
    ----------
    regions: :data:`~typing.Optional`\\[:class:`list`\\[:class:`~mafic.region.VoiceRegion`]]
        The regions that the node can be used in.
        This is used to determine when to use this node.
    shard_ids: :data:`~typing.Optional`\\[:class:`list`\\[:class:`int`]]
        The shard IDs that the node can be used in.
        This is used to determine when to use this node.
    """

    __slots__ = (
        "__password",
        "__session",
        "_available",
        "_client",
        "_heartbeat",
        "_host",
        "_label",
        "_players",
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
        client: ClientT,
        secure: bool = False,
        heartbeat: int = 30,
        timeout: float = 10,
        session: aiohttp.ClientSession | None = None,
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
        self.regions: list[VoiceRegion] | None = _wrap_regions(regions)

        self._rest_uri = yarl.URL.build(
            scheme=f"http{'s'*secure}", host=host, port=port
        )
        self._ws_uri = yarl.URL.build(scheme=f"ws{'s'*secure}", host=host, port=port)
        self._resume_key = resume_key or f"{host}:{port}:{label}"

        self._ws: ClientWebSocketResponse | None = None
        self._ws_task: Task[None] | None = None

        self._available = False
        self._ready = Event()

        self._players: dict[int, Player[ClientT]] = {}

        self._stats: NodeStats | None = None
        self._session_id: str | None = None

    @property
    def host(self) -> str:
        """The host of the node."""

        return self._host

    @property
    def port(self) -> int:
        """The port of the node."""

        return self._port

    @property
    def label(self) -> str:
        """The label of the node."""

        return self._label

    @property
    def client(self) -> ClientT:
        """The client that the node is attached to."""

        return self._client

    @property
    def secure(self) -> bool:
        """Whether the node is using a secure connection."""

        return self._secure

    @property
    def stats(self) -> NodeStats | None:
        """The stats of the node.

        This will be ``None`` if the node has not sent stats yet.
        This could be if it is not connected, or if stats sending is disabled on the
        node.
        """
        return self._stats

    @property
    def available(self) -> bool:
        """Whether the node is available.

        This is ``False`` if the node is not connected, or if it is not ready.
        """

        return self._available

    @property
    def weight(self) -> float:
        """The weight of the node.

        This is used to determine which node to use when multiple nodes are available.

        Notes
        -----
        The weight is calculated based on the following:

        - The number of players connected to the node.
        - The load of the node.
        - The number of UDP frames nulled.
        - The number of UDP frames that are lost.
        - If the node memory is very close to full.

        If the node has not sent stats yet, then a high value will be returned.
        This is so that the node will be used if it is the only one available,
        or if stats sending is disabled on the node.
        """

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

    @property
    def players(self) -> list[Player[ClientT]]:
        """The players connected to the node.

        .. versionchanged:: 2.0

            This is now a list.
        """

        return [*self._players.values()]

    def get_player(self, guild_id: int) -> Player[ClientT] | None:
        """Get a player from the node.

        Parameters
        ----------
        guild_id:
            The guild ID to get the player for.

        Returns
        -------
        :data:`~typing.Optional`\\[:class:`Player`]
            The player for the guild, if found.
        """

        return self._players.get(guild_id)

    def add_player(self, guild_id: int, player: Player[ClientT]) -> None:
        """Add a player to the node.

        Parameters
        ----------
        guild_id:
            The guild ID to add the player for.
        player:
            The player to add.
        """

        self._players[guild_id] = player

    def remove_player(self, guild_id: int) -> None:
        """Remove a player from the node.

        .. note::

            This does not disconnect the player from the voice channel.
            This simply exists to remove the player from the node cache.

        Parameters
        ----------
        guild_id:
            The guild ID to remove the player for.
        """

        self._players.pop(guild_id, None)

    async def _check_version(self) -> None:
        """Check the version of the node.

        Raises
        ------
        :exc:`RuntimeError`
            If the
            - major version is not 3
            - minor version is less than 7

            This is because the rest api is in 3.7, and v4 will have breaking changes.

        Warns
        -----
        :class:`UnsupportedVersionWarning`
            If the minor version is greater than 7.
            Some features may not work.
        """

        if self._rest_uri.path.endswith("/v3") or self._ws_uri.path.endswith(
            "/websocket"
        ):
            # This process was already ran likely.
            return

        if self.__session is None:
            self.__session = await self._create_session()

        async with self.__session.get(
            self._rest_uri / "version",
            headers={"Authorization": self.__password},
        ) as resp:
            # Only the major and minor are needed.
            version = await resp.text()

            try:
                major, minor, _ = version.split(".", maxsplit=2)
            except ValueError:
                message = UnknownVersionWarning.message
                warnings.warn(message, UnknownVersionWarning)
            else:
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

            self._rest_uri /= "v3"
            self._ws_uri /= "v3/websocket"

    async def _connect_to_websocket(
        self, headers: dict[str, str], session: aiohttp.ClientSession
    ) -> None:
        """Connect to the websocket of the node.

        Parameters
        ----------
        headers:
            The headers to use for the websocket connection.
        session:
            The session to use for the websocket connection.
        """

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

    async def connect(
        self, *, backoff: ExponentialBackoff[Literal[False]] | None = None
    ) -> None:
        """Connect to the node.

        Parameters
        ----------
        backoff:
            The backoff to use when reconnecting.

        Raises
        ------
        NodeAlreadyConnected
            If the node is already connected.
        asyncio.TimeoutError
            If the connection times out.
            You can change the timeout with the `timeout` parameter.
        """

        if self._ws is not None:
            raise NodeAlreadyConnected()

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
        try:
            await self._connect_to_websocket(headers=headers, session=session)
        except Exception:
            _log.error(
                "Failed to connect to lavalink at %s",
                self._rest_uri,
                extra={"label": self._label},
            )
            print_exc()

            backoff = backoff or ExponentialBackoff()
            delay = backoff.delay()
            _log.info(
                "Retrying connection to lavalink at %s in %s seconds...",
                self._rest_uri,
                delay,
                extra={"label": self._label},
            )
            await sleep(delay)

            create_task(self.connect(backoff=backoff))

        _log.info("Connected to lavalink.", extra={"label": self._label})

        _log.debug(
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
            await self.sync_players()
            self._available = True

    async def _ws_listener(self) -> None:
        """Listen for messages from the websocket."""

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
            _type: aiohttp.WSMsgType = (
                msg.type
            )  # pyright: ignore[reportUnknownMemberType]

            if _type is aiohttp.WSMsgType.CLOSED:
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
                create_task(self.connect(backoff=backoff))
                return
            else:
                _log.debug(
                    "Creating task to handle websocket message.",
                    extra={"label": self._label},
                )
                create_task(self._handle_msg(msg.json(loads=loads)))

    async def _handle_msg(self, data: IncomingMessage) -> None:
        """Handle a message from the websocket.

        Parameters
        ----------
        data:
            The data to handle.
        """

        _log.debug("Received event with op %s", data["op"])
        _log.debug("Event data: %s", data)

        if data["op"] == "playerUpdate":
            guild_id = int(data["guildId"])
            player = self.get_player(guild_id)

            if player is None:
                if data["state"]["connected"] is True:
                    _log.error(
                        "Could not find player for guild %s, discarding event.",
                        guild_id,
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

            _log.debug(
                "Received session ID %s", session_id, extra={"label": self._label}
            )
            self._session_id = session_id

            if resumed:
                _log.info(
                    "Successfully resumed connection with lavalink.",
                    extra={"label": self._label},
                )
            else:
                _log.debug(
                    "Sending configuration to resume with key %s",
                    self._resume_key,
                    extra={"label": self._label},
                )
                await self.configure_resuming()

            self._ready.set()
        else:
            # Of course pyright considers this to be `Never`, so this is to keep types.
            op = cast(str, data["op"])
            _log.warn("Unknown incoming message op code %s", op)

    async def _handle_event(self, data: EventPayload) -> None:
        """Handle an event from the websocket.

        Parameters
        ----------
        data:
            The data to handle.
        """

        if not (player := self.get_player(int(data["guildId"]))):
            _log.error(
                "Could not find player for guild %s, discarding event.", data["guildId"]
            )
            return

        player.dispatch_event(data)

    def voice_update(
        self,
        guild_id: int,
        session_id: str,
        data: VoiceServerUpdatePayload,
    ) -> Coro[None]:
        """Send a voice update to the node.

        Parameters
        ----------
        guild_id:
            The guild ID to send the update for.
        session_id:
            The **Discord** session ID to send.
        data:
            The voice server update payload to send.

        Raises
        ------
        :exc:`ValueError`
            If the endpoint in the payload is ``None``.
        """

        _log.debug(
            "Sending player update to lavalink.",
            extra={"label": self._label, "guild": guild_id},
        )
        if data["endpoint"] is None:
            raise ValueError("Discord did not provide an endpoint.")

        return self.__request(
            "PATCH",
            f"sessions/{self._session_id}/players/{guild_id}",
            {
                "voice": {
                    "sessionId": session_id,
                    "endpoint": data["endpoint"],
                    "token": data["token"],
                },
            },
        )

    def configure_resuming(self) -> Coro[None]:
        """Configure the node to resume."""

        _log.info(
            "Sending resume configuration to lavalink with resume key %s.",
            self._resume_key,
            extra={"label": self._label},
        )

        return self.__request(
            "PATCH",
            f"sessions/{self._session_id}",
            {
                "resumingKey": self._resume_key,
                "timeout": 60,
            },
        )

    def destroy(self, guild_id: int) -> Coro[None]:
        """Destroy a player.

        Parameters
        ----------
        guild_id:
            The guild ID to destroy the player for.
        """

        _log.debug("Sending request to destroy player", extra={"label": self._label})

        return self.__request(
            "DELETE", f"sessions/{self._session_id}/players/{guild_id}"
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
        """Update a player.

        Parameters
        ----------
        guild_id:
            The guild ID to update the player for.
        track:
            The track to update the player with.
            Setting this to ``None`` will clear the track.
        position:
            The position to update the player with.
        end_time:
            The position in the track to stop playing.
        volume:
            The volume to set.
        no_replace:
            Whether to replace the current track or leave it playing.
        pause:
            Whether to pause the player.
        filter:
            The filter to apply to the player.
        """

        data: UpdatePlayerPayload = {}

        if track is not MISSING:
            data["encodedTrack"] = track.id if track is not None else None

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
            query: UpdatePlayerParams | None = {"noReplace": str(no_replace)}
        else:
            query = None

        _log.debug(
            "Sending player update to lavalink with data %s.",
            data,
            extra={"label": self._label, "guild": guild_id},
        )

        return self.__request(
            "PATCH",
            f"sessions/{self._session_id}/players/{guild_id}",
            data,
            query,
        )

    async def _create_session(self) -> aiohttp.ClientSession:
        """Create a new session for the node."""

        return aiohttp.ClientSession(json_serialize=dumps)

    async def __request(
        self,
        method: str,
        path: str,
        json: OutgoingMessage | None = None,
        params: OutgoingParams | None = None,
    ) -> Any:
        """Send a request to the node.

        Parameters
        ----------
        method:
            The HTTP method to use.
        path:
            The path to send the request to, without ``/v3``
        json:
            The JSON to send.
        params:
            The query parameters to send.

        Returns
        -------
        :data:`~typing.Any`
            The JSON response from the node.
        """

        if self.__session is None:
            self.__session = await self._create_session()

        session = self.__session
        uri = self._rest_uri / path

        _log.debug(
            "Sending %s request to %s and data %s.",
            method,
            uri,
            json,
            extra={"label": self._label},
        )
        async with session.request(
            method,
            uri,
            json=json,
            params=params,
            headers={"Authorization": self.__password},
        ) as resp:
            _log.debug("Received status %s from lavalink.", resp.status)
            if resp.status == 204:
                return None

            if not (200 <= resp.status < 300):
                text = await resp.text()

                if resp.status == 400:
                    raise HTTPBadRequest(text)
                if resp.status == 401:
                    raise HTTPUnauthorized(text)
                elif resp.status == 404:
                    raise HTTPNotFound(text)
                else:
                    raise HTTPException(status=resp.status, message=text)

            _log.debug(
                "Received status %s from lavalink from path %s", resp.status, path
            )

            json = await resp.json(loads=loads)
            _log.debug("Received raw data %s from %s", json, path)
            return json

    async def fetch_tracks(
        self, query: str, *, search_type: str
    ) -> list[Track] | Playlist | None:
        """Fetch tracks from the node.

        Parameters
        ----------
        query:
            The query to search for.
        search_type:
            The search type to use.

        Returns
        -------
        :class:`list`\\[:class:`Track`]
            A list of tracks if the load type is ``TRACK_LOADED`` or ``SEARCH_RESULT``.
        :class:`Playlist`
            A playlist if the load type is ``PLAYLIST_LOADED``.
        None
            If the load type is ``NO_MATCHES``.
        """

        if not URL_REGEX.match(query):
            query = f"{search_type}:{query}"

        data: TrackLoadingResult = await self.__request(
            "GET", "loadtracks", params={"identifier": query}
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
        """Decode a track from the encoded base64 data.

        Parameters
        ----------
        track:
            The encoded track data.

        Returns
        -------
        :class:`Track`
            The decoded track.

        See Also
        --------
        :meth:`decode_tracks`
        """

        info: TrackInfo = await self.__request(
            "GET", "decodetrack", params={"encodedTrack": track}
        )

        return Track.from_data(track=track, info=info)

    async def decode_tracks(self, tracks: list[str]) -> list[Track]:
        """Decode a list of tracks from the encoded base64 data.

        Parameters
        ----------
        tracks:
            The encoded track data.

        Returns
        -------
        :class:`list`\\[:class:`Track`]
            The decoded tracks.

        See Also
        --------
        :meth:`decode_track`
        """

        track_data: list[TrackWithInfo] = await self.__request(
            "POST", "decodetracks", json=tracks
        )

        return [Track.from_data_with_info(track) for track in track_data]

    async def fetch_plugins(self) -> list[Plugin]:
        """Fetch the plugins from the node.

        Returns
        -------
        :class:`list`\\[:class:`Plugin`]
            The plugins from the node.
        """

        plugins: list[PluginData] = await self.__request("GET", "plugins")

        return [Plugin(plugin) for plugin in plugins]

    async def fetch_route_planner_status(self) -> RoutePlannerStatus | None:
        """Fetch the route planner status from the node.

        Returns
        -------
        :data:`.RoutePlannerStatus`
            The route planner status from the node.
        """

        data: RoutePlannerStatusPayload = await self.__request(
            "GET", "routeplanner/status"
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
        """Unmark a failed address so it can be used again.

        Parameters
        ----------
        address:
            The address to unmark.
        """

        await self.__request(
            "POST", "routeplanner/free/address", json={"address": address}
        )

    async def unmark_all_addresses(self) -> None:
        """Unmark all failed addresses so they can be used again."""

        await self.__request("POST", "routeplanner/free/all")

    async def _add_unknown_player(self, player_id: int, state: PlayerPayload) -> None:
        """Add an unknown player to the node.

        Parameters
        ----------
        player_id:
            The guild ID of the player.
        state:
            The state of the player.
        """

        guild = self.client.get_guild(player_id)
        if guild is None:
            guild = await self.client.fetch_guild(player_id)

        voice_state = guild.me.voice

        if voice_state is None:
            return

        channel = voice_state.channel

        if channel is None:
            return

        # Circular, pool -> node -> player -> pool
        from .player import Player

        player = Player(self.client, channel)

        player.set_state(state)

        self._players[player_id] = player

    async def _remove_unknown_player(self, player_id: int) -> None:
        """Remove an unknown player from the node.

        Parameters
        ----------
        player_id:
            The guild ID of the player.
        """

        await self._players[player_id].disconnect(force=True)
        self.remove_player(player_id)

    async def sync_players(self) -> None:
        """Sync the players with the node.

        .. note::

            This method is called automatically when the client is ready.
            You should not need to call this method yourself.
        """

        players: list[PlayerPayload] = await self.__request(
            "GET", f"sessions/{self._session_id}/players"
        )
        actual_players = {int(player["guildId"]): player for player in players}
        actual_player_ids = set(actual_players.keys())
        expected_player_ids = set(self._players.keys())

        await gather(
            *(
                self._add_unknown_player(player_id, actual_players[player_id])
                for player_id in actual_player_ids - expected_player_ids
            ),
            *(
                self._remove_unknown_player(player_id)
                for player_id in expected_player_ids - actual_player_ids
            ),
        )
