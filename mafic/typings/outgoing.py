# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, TypedDict, Union

from .common import Filters, VoiceState

__all__ = (
    "OutgoingMessage",
    "UpdatePlayerPayload",
    "UpdateSessionPayload",
    "UnmarkAddressPayload",
)


class UpdateSessionPayload(TypedDict, total=False):
    resumingKey: str | None
    timeout: int


class UpdatePlayerPayload(TypedDict, total=False):
    encodedTrack: str | None
    identifier: str
    position: int
    endTime: int
    volume: int
    paused: bool
    filters: Filters
    voice: VoiceState


class UnmarkAddressPayload(TypedDict):
    address: str


OutgoingMessage = Union[
    UpdatePlayerPayload, UpdateSessionPayload, List[str], UnmarkAddressPayload
]
