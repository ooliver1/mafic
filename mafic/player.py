# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from .libraries import VoiceProtocol

if TYPE_CHECKING:
    from .libraries import (
        Client,
        Connectable,
        GuildVoiceStatePayload,
        VoiceServerUpdatePayload,
    )


class Player(VoiceProtocol):
    def __init__(self, client: Client, channel: Connectable) -> None:
        self.client: Client = client
        self.channel: Connectable = channel

    async def on_voice_state_update(self, data: GuildVoiceStatePayload) -> None:
        raise NotImplementedError

    async def on_voice_server_update(self, data: VoiceServerUpdatePayload) -> None:
        raise NotImplementedError

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        raise NotImplementedError

    async def disconnect(self, *, force: bool) -> None:
        self.cleanup()
