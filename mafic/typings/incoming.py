# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Union

from .common import Stats, TrackWithInfo
from .misc import PayloadWithGuild

if TYPE_CHECKING:
    from typing import Literal

    from typing_extensions import NotRequired

    from .misc import LavalinkException

__all__ = (
    "EventPayload",
    "PlayerUpdatePayload",
    "PlayerUpdateState",
    "IncomingMessage",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStartEvent",
    "TrackStuckEvent",
    "WebSocketClosedEvent",
)


class PlayerUpdateState(TypedDict):
    time: int
    position: NotRequired[int]
    connected: bool
    ping: int


class PlayerUpdatePayload(PayloadWithGuild):
    op: Literal["playerUpdate"]
    state: PlayerUpdateState


class WebSocketClosedEvent(PayloadWithGuild):
    op: Literal["event"]
    type: Literal["WebSocketClosedEvent"]
    code: int
    reason: str
    byRemote: bool


class TrackStartEvent(PayloadWithGuild):
    op: Literal["event"]
    type: Literal["TrackStartEvent"]
    # V3
    encodedTrack: NotRequired[str]
    # V4
    track: NotRequired[TrackWithInfo]


class TrackEndEvent(PayloadWithGuild):
    op: Literal["event"]
    type: Literal["TrackEndEvent"]
    # V3
    encodedTrack: NotRequired[str]
    # V4
    track: NotRequired[TrackWithInfo]
    reason: Literal[
        # V3
        "FINISHED",
        "LOAD_FAILED",
        "STOPPED",
        "REPLACED",
        "CLEANUP",
        # V4
        "finished",
        "loadFailed",
        "stopped",
        "replaced",
        "cleanup",
    ]


class TrackExceptionEvent(PayloadWithGuild):
    op: Literal["event"]
    type: Literal["TrackExceptionEvent"]
    # V3
    encodedTrack: NotRequired[str]
    # V4
    track: NotRequired[TrackWithInfo]
    exception: LavalinkException


class TrackStuckEvent(PayloadWithGuild):
    op: Literal["event"]
    type: Literal["TrackStuckEvent"]
    # V3
    encodedTrack: NotRequired[str]
    # V4
    track: NotRequired[TrackWithInfo]
    thresholdMs: int


class ReadyPayload(TypedDict):
    op: Literal["ready"]
    resumed: bool
    sessionId: str


EventPayload = Union[
    WebSocketClosedEvent,
    TrackStartEvent,
    TrackEndEvent,
    TrackExceptionEvent,
    TrackStuckEvent,
]


IncomingMessage = Union[
    PlayerUpdatePayload,
    Stats,
    EventPayload,
    ReadyPayload,
]
