# SPDX-License-Identifier: MIT

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from .__libraries import GuildChannel, StageChannel, VoiceChannel, VoiceProtocol
from .pool import NodePool

if TYPE_CHECKING:
    from .__libraries import (
        Client,
        Connectable,
        Guild,
        GuildVoiceStatePayload,
        VoiceServerUpdatePayload,
    )
    from .node import Node


_log = getLogger(__name__)


class Player(VoiceProtocol):
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

    @property
    def connected(self) -> bool:
        return self._connected

    # If people are so in love with the VoiceClient interface
    def is_connected(self):
        return self._connected

    async def _dispatch_player_update(
        self, data: GuildVoiceStatePayload | VoiceServerUpdatePayload
    ) -> None:
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
            await self._dispatch_player_update(data)

    async def on_voice_server_update(self, data: VoiceServerUpdatePayload) -> None:
        if self._node is None:
            _log.debug("Getting best node for player", extra={"guild": self._guild_id})
            self._node = NodePool.get_node(
                guild_id=data["guild_id"], endpoint=data["endpoint"]
            )

        self._node.players[self._guild_id] = self

        self._guild_id = int(data["guild_id"])
        self._server_state = data

        await self._dispatch_player_update(data)

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
