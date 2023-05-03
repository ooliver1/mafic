# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, List, TypedDict, Union

if TYPE_CHECKING:
    from .common import Filters, VoiceStateRequest

__all__ = (
    "DecodeTrackParams",
    "OutgoingMessage",
    "OutgoingParams",
    "TrackLoadParams",
    "UnmarkAddressPayload",
    "UpdatePlayerPayload",
    "UpdatePlayerParams",
    "UpdateSessionPayload",
)


class UpdateSessionPayload(TypedDict, total=False):
    # V3
    resumingKey: str | None
    # V4
    resuming: bool
    timeout: int


class UpdatePlayerPayload(TypedDict, total=False):
    encodedTrack: str | None
    identifier: str
    position: int
    endTime: int
    volume: int
    paused: bool
    filters: Filters
    voice: VoiceStateRequest


class UnmarkAddressPayload(TypedDict):
    address: str


class UpdatePlayerParams(TypedDict):
    noReplace: str


class TrackLoadParams(TypedDict):
    identifier: str


class DecodeTrackParams(TypedDict):
    encodedTrack: str


OutgoingMessage = Union[
    UpdatePlayerPayload, UpdateSessionPayload, List[str], UnmarkAddressPayload
]


OutgoingParams = Union[UpdatePlayerParams, TrackLoadParams, DecodeTrackParams]
