# SPDX-License-Identifier: MIT

from __future__ import annotations

from asyncio import create_task, sleep
from logging import getLogger
from typing import TYPE_CHECKING, cast

from aiohttp import ClientSession, WSMsgType

from .__libraries import ExponentialBackoff, dumps, loads

if TYPE_CHECKING:
    from asyncio import Task

    from aiohttp import ClientWebSocketResponse

    from .__libraries import Client, VoiceServerUpdatePayload
    from .player import Player
    from .typings import (
        Coro,
        EventPayload,
        IncomingMessage,
        OutgoingMessage,
        PlayPayload,
    )

_log = getLogger(__name__)


class Node:
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
            self.__session = ClientSession()

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
        self._ws = await session.ws_connect(  # pyright: ignore[reportUnknownMemberType]
            self._ws_uri,
            timeout=self._timeout,
            heartbeat=self._heartbeat,
            headers=headers,
        )
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

    # TODO: play
    # TODO: stop
    # TODO: pause
    # TODO: seek
    # TODO: volume
    # TODO: filter
    # TODO: API routes:
    # TODO: fetch tracks
    # TODO: decode track
    # TODO: plugins
    # TODO: route planner status
    # TODO: unmark failed address
    # TODO: unmark all failed addresses
