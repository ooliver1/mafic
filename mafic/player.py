# SPDX-License-Identifier: MIT

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from .__libraries import VoiceProtocol
from .pool import NodePool

if TYPE_CHECKING:
    from .__libraries import (
        Client,
        Connectable,
        GuildChannel,
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
        self._node = node

        self._guild_id: int | None = None
        self._session_id: str | None = None
        self._server_state: VoiceServerUpdatePayload | None = None

    async def on_voice_state_update(self, data: GuildVoiceStatePayload) -> None:
        raise NotImplementedError

    async def on_voice_server_update(self, data: VoiceServerUpdatePayload) -> None:
        if self._node is None:
            _log.debug("Getting best node for player", extra={"guild": self._guild_id})
            self._node = NodePool.get_node(
                guild_id=data["guild_id"], endpoint=data["endpoint"]
            )

        self._server_state = data

        if self._guild_id is None or self._session_id is None:
            _log.warn("Ignoring voice server update as guild and session are unknown.")
            return

        await self._node.send_voice_server_update(
            guild_id=self._guild_id, session_id=self._session_id, data=data
        )

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

    async def disconnect(self, *, force: bool) -> None:
        self.cleanup()
