# SPDX-License-Identifier: MIT
# pyright: reportImportCycles=false
# Player import.

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Generic, TypeVar

from .__libraries import VoiceProtocol

if TYPE_CHECKING:
    from .track import Track
    from .typings import (
        LavalinkException,
        TrackEndEvent as TrackEndEventPayload,
        TrackExceptionEvent as TrackExceptionEventPayload,
        TrackStuckEvent as TrackStuckEventPayload,
        WebSocketClosedEvent as WebSocketClosedEventPayload,
    )


# This needs HKTs in python - as Player is generic on ClientT.
PlayerT = TypeVar("PlayerT", bound=VoiceProtocol)

__all__ = (
    "EndReason",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStartEvent",
    "TrackStuckEvent",
    "WebSocketClosedEvent",
)


class EndReason(str, Enum):
    """Represents the reason why a track ended."""

    FINISHED = "FINISHED"
    """The track finished playing."""

    LOAD_FAILED = "LOAD_FAILED"
    """The track failed to load."""

    STOPPED = "STOPPED"
    """The track was stopped."""

    REPLACED = "REPLACED"
    """The track was replaced."""

    CLEANUP = "CLEANUP"
    """The track was cleaned up."""


class WebSocketClosedEvent(Generic[PlayerT]):
    """Represents an event when the connection to Discord is lost.

    Attributes
    ----------
    code: :class:`int`
        The close code.
        Find what this can be in the Discord `docs`_.

        .. _docs: https://discord.com/developers/docs/topics/opcodes-and-status-codes#close-event-codes.
    reason: :class:`str`
        The close reason.
    by_discord: :class:`bool`
        Whether the close was initiated by Discord.
    player: :class:`Player`
        The player that the event was dispatched from.
    """

    __slots__ = ("code", "reason", "by_discord", "player")

    def __init__(self, *, payload: WebSocketClosedEventPayload, player: PlayerT):
        self.code: int = payload["code"]
        self.reason: str = payload["reason"]
        self.by_discord: bool = payload["byRemote"]
        self.player: PlayerT = player

    def __repr__(self) -> str:
        return (
            f"<WebSocketClosedEvent code={self.code} reason={self.reason!r} "
            f"by_discord={self.by_discord}>"
        )


class TrackStartEvent(Generic[PlayerT]):
    """Represents an event when a track starts playing.

    Attributes
    ----------
    track: :class:`Track`
        The track that started playing.
    player: :class:`Player`
        The player that the event was dispatched from.
    """

    __slots__ = ("track", "player")

    def __init__(self, *, track: Track, player: PlayerT):
        self.track: Track = track
        self.player: PlayerT = player

    def __repr__(self) -> str:
        return f"<TrackStartEvent track={self.track!r}>"


class TrackEndEvent(Generic[PlayerT]):
    """Represents an event when a track ends.

    Attributes
    ----------
    track: :class:`Track`
        The track that ended.
    reason: :class:`EndReason`
        The reason why the track ended.
    player: :class:`Player`
        The player that the event was dispatched from.
    """

    __slots__ = ("track", "reason", "player")

    def __init__(self, *, track: Track, payload: TrackEndEventPayload, player: PlayerT):
        self.track: Track = track
        self.reason: EndReason = EndReason(payload["reason"])
        self.player: PlayerT = player

    def __repr__(self) -> str:
        return f"<TrackEndEvent track={self.track!r} reason={self.reason!r}>"


class TrackExceptionEvent(Generic[PlayerT]):
    """Represents an event when an exception occurs while playing a track.

    Attributes
    ----------
    track: :class:`Track`
        The track that caused the exception.
    exception: :class:`Exception`
        The exception that was raised.
    player: :class:`Player`
        The player that the event was dispatched from.
    """

    __slots__ = ("track", "exception", "player")

    def __init__(
        self,
        *,
        track: Track,
        payload: TrackExceptionEventPayload,
        player: PlayerT,
    ):
        self.track: Track = track
        self.exception: LavalinkException = payload["exception"]
        self.player: PlayerT = player

    def __repr__(self) -> str:
        return (
            f"<TrackExceptionEvent track={self.track!r} exception={self.exception!r}>"
        )


class TrackStuckEvent(Generic[PlayerT]):
    """Represents an event when a track gets stuck.

    Attributes
    ----------
    track: :class:`Track`
        The track that got stuck.
    threshold_ms: :class:`int`
        The threshold in milliseconds that was exceeded.
    player: :class:`Player`
        The player that the event was dispatched from.
    """

    __slots__ = ("track", "threshold_ms", "player")

    def __init__(
        self, *, track: Track, payload: TrackStuckEventPayload, player: PlayerT
    ):
        self.track: Track = track
        self.threshold_ms: int = payload["thresholdMs"]
        self.player: PlayerT = player

    def __repr__(self) -> str:
        return (
            f"<TrackStuckEvent track={self.track!r} threshold_ms={self.threshold_ms}>"
        )
