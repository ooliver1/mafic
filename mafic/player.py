# SPDX-License-Identifier: MIT

from __future__ import annotations

from logging import getLogger
from time import time
from typing import TYPE_CHECKING

from .__libraries import GuildChannel, StageChannel, VoiceChannel, VoiceProtocol
from .playlist import Playlist
from .pool import NodePool
from .search_type import SearchType
from .track import Track

if TYPE_CHECKING:
    from .__libraries import (
        Client,
        Connectable,
        Guild,
        GuildVoiceStatePayload,
        VoiceServerUpdatePayload,
    )
    from .node import Node
    from .typings import PlayerUpdateState


_log = getLogger(__name__)


class Player(VoiceProtocol):
    __slots__ = (
        "_connected",
        "_guild_id",
        "_last_update",
        "_node",
        "_ping",
        "_position",
        "_server_state",
        "_session_id",
        "channel",
        "client",
        "guild",
    )

    def __init__(
        self,
        client: Client,
        channel: Connectable,
        *,
        node: Node | None = None,
    ) -> None:
        self.client: Client = client
        self.channel: Connectable = channel

        if not isinstance(self.channel, GuildChannel):
            raise TypeError("Voice channel must be a GuildChannel.")

        self.guild: Guild = self.channel.guild

        self._node = node

        self._guild_id: int = self.guild.id
        self._session_id: str | None = None
        self._server_state: VoiceServerUpdatePayload | None = None
        self._connected: bool = False
        self._position: int = 0
        self._last_update: int = 0
        self._ping = 0
        self._current: Track | None = None

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def position(self) -> int:
        pos = self._position

        if self._connected and self._current is not None:
            # Add the time since the last update to the position.
            # If the track total time is less than that, use that.
            pos = min(
                self._current.length, pos + int((time() - self._last_update) * 1000)
            )

        return pos

    @property
    def ping(self) -> int:
        return self._ping

    @property
    def node(self) -> Node:
        if self._node is None:
            _log.warning(
                "Unable to use best node, player not connected, finding random node.",
                extra={"guild": self._guild_id},
            )
            return NodePool.get_random_node()

        return self._node

    def update_state(self, state: PlayerUpdateState) -> None:
        self._last_update = state["time"]
        self._position = state.get("position", 0)
        self._connected = state["connected"]
        self._ping = state["ping"]

    # If people are so in love with the VoiceClient interface
    def is_connected(self):
        return self._connected

    async def _dispatch_player_update(self) -> None:
        if self._node is None:
            _log.debug("Recieved voice update before node was found.")
            return

        if self._session_id is None:
            _log.debug("Receieved player update before session ID was set.")
            return

        if self._server_state is None:
            _log.debug("Receieved player update before server state was found")
            return

        await self._node.voice_update(
            guild_id=self._guild_id,
            session_id=self._session_id,
            data=self._server_state,
        )

    async def on_voice_state_update(self, data: GuildVoiceStatePayload) -> None:
        before_session_id = self._session_id
        self._session_id = data["session_id"]

        channel_id = data["channel_id"]
        channel = self.guild.get_channel(int(channel_id))
        assert isinstance(channel, (StageChannel, VoiceChannel))

        self.channel = channel

        if self._session_id != before_session_id:
            await self._dispatch_player_update()

    async def on_voice_server_update(self, data: VoiceServerUpdatePayload) -> None:
        # Fetch the best node as we either don't know the best one yet.
        # Or the node we were using was not the best one (endpoint optimisation).
        if (
            self._node is None
            or self._server_state is None
            or self._server_state["endpoint"] != data["endpoint"]
        ):
            _log.debug("Getting best node for player", extra={"guild": self._guild_id})
            self._node = NodePool.get_node(
                guild_id=data["guild_id"], endpoint=data["endpoint"]
            )

        self._node.players[self._guild_id] = self

        self._guild_id = int(data["guild_id"])
        self._server_state = data

        await self._dispatch_player_update()

    async def connect(
        self,
        *,
        timeout: float,
        reconnect: bool,
        self_mute: bool = False,
        self_deaf: bool = False,
    ) -> None:
        if not isinstance(self.channel, GuildChannel):
            raise TypeError("Voice channel must be a GuildChannel.")

        _log.debug("Connecting to voice channel %s", self.channel.id)

        await self.channel.guild.change_voice_state(
            channel=self.channel, self_mute=self_mute, self_deaf=self_deaf
        )
        self._connected = True

    async def disconnect(self, *, force: bool = False) -> None:
        try:
            _log.debug(
                "Disconnecting from voice channel.",
                extra={"guild": self._guild_id},
            )
            await self.guild.change_voice_state(channel=None)
        finally:
            self.cleanup()
            self._connected = False

    async def destroy(self) -> None:
        _log.debug(
            "Disconnecting player and destroying client.",
            extra={"guild": self._guild_id},
        )
        await self.disconnect()

        if self._node is not None:
            self._node.players.pop(self.guild.id, None)
            await self._node.destroy(guild_id=self.guild.id)

    async def fetch_tracks(
        self, query: str, search_type: SearchType | str = SearchType.YOUTUBE
    ) -> list[Track] | Playlist | None:
        node = self.node

        raw_type: str
        if isinstance(search_type, SearchType):
            raw_type = search_type.value
        else:
            raw_type = search_type

        return await node.fetch_tracks(query, search_type=raw_type)

    # TODO: controls:
    # TODO: play
    # TODO: pause
    # TODO: stop
    # TODO: filter
    # TODO: volume
    # TODO: seek
    # TODO: pause
