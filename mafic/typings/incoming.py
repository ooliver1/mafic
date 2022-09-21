# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Union

from .misc import PayloadWithGuild

if TYPE_CHECKING:
    from typing import Literal

    from typing_extensions import NotRequired

    from .misc import FriendlyWithCause

__all__ = (
    "EventPayload",
    "PlayerUpdatePayload",
    "StatsPayload",
    "IncomingMessage",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStartEvent",
    "TrackStuckEvent",
)


class PlayerUpdateState(TypedDict):
    time: int
    position: NotRequired[int]
    connected: bool
    ping: int


class PlayerUpdatePayload(PayloadWithGuild):
    op: Literal["playerUpdate"]
    state: PlayerUpdateState


class Memory(TypedDict):
    free: int
    used: int
    allocated: int
    reservable: int


class CPU(TypedDict):
    cores: int
    systemLoad: int
    lavalinkLoad: int


class FrameStats(TypedDict):
    sent: int
    nulled: int
    deficit: int


class StatsPayload(TypedDict):
    op: Literal["stats"]
    players: int
    playingPlayers: int
    uptime: int
    memory: Memory
    cpu: CPU
    frameStats: NotRequired[FrameStats]


class WebSocketClosedEvent(PayloadWithGuild):
    op: Literal["event"]
    type: Literal["WebSocketClosedEvent"]
    code: int
    reason: str
    byRemote: bool


class TrackStartEvent(PayloadWithGuild):
    op: Literal["event"]
    type: Literal["TrackStartEvent"]
    track: str


class TrackEndEvent(PayloadWithGuild):
    op: Literal["event"]
    type: Literal["TrackEndEvent"]
    track: str
    reason: Literal[
        "FINISHED",
        "LOAD_FAILED",
        "STOPPED",
        "REPLACED",
        "CLEANUP",
    ]


class TrackExceptionEvent(PayloadWithGuild):
    op: Literal["event"]
    type: Literal["TrackExceptionEvent"]
    track: str
    error: FriendlyWithCause


class TrackStuckEvent(PayloadWithGuild):
    op: Literal["event"]
    type: Literal["TrackStuckEvent"]
    track: str
    thresholdMs: int


EventPayload = Union[
    WebSocketClosedEvent,
    TrackStartEvent,
    TrackEndEvent,
    TrackExceptionEvent,
    TrackStuckEvent,
]


IncomingMessage = Union[
    PlayerUpdatePayload,
    StatsPayload,
    EventPayload,
]
