# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from .__libraries import VoiceProtocol
from .pool import NodePool

if TYPE_CHECKING:
    from .__libraries import (
        Client,
        Connectable,
        GuildVoiceStatePayload,
        VoiceServerUpdatePayload,
    )
    from .node import Node


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
            self._node = NodePool.get_node(
                guild_id=data["guild_id"], endpoint=data["endpoint"]
            )

        self._server_state = data

        if self._guild_id is None or self._session_id is None:
            return

        await self._node.send_voice_server_update(
            guild_id=self._guild_id, session_id=self._session_id, data=data
        )

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        raise NotImplementedError

    async def disconnect(self, *, force: bool) -> None:
        self.cleanup()
