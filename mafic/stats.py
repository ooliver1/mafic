# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .typings import CPU, FrameStats as FrameStatsPayload, Memory, Stats


__all__ = (
    "CPUStats",
    "FrameStats",
    "MemoryStats",
    "NodeStats",
)


class CPUStats:
    """Represents CPU stats for a node.

    Attributes
    ----------
    cores: :class:`int`
        The number of cores the node has.
    system_load: :class:`int`
        The load on the whole system lavalink is on..
    lavalink_load: :class:`int`
        The load Lavalink is using.
    """

    __slots__ = ("cores", "system_load", "lavalink_load")

    def __init__(self, payload: CPU) -> None:
        self.cores: int = payload["cores"]
        self.system_load: int = payload["systemLoad"]
        self.lavalink_load: int = payload["lavalinkLoad"]


class MemoryStats:
    """Represents memory stats for a node.

    Attributes
    ----------
    free: :class:`int`
        The amount of free memory.
    used: :class:`int`
        The amount of used memory.
    allocated: :class:`int`
        The amount of allocated memory.
    reservable: :class:`int`
        The amount of reservable memory for the node. Set by ``-Xmx`` for Java.
    """

    __slots__ = ("free", "used", "allocated", "reservable")

    def __init__(self, payload: Memory) -> None:
        self.free: int = payload["free"]
        self.used: int = payload["used"]
        self.allocated: int = payload["allocated"]
        self.reservable: int = payload["reservable"]


class FrameStats:
    """Represents frame stats for a node.

    Attributes
    ----------
    sent: :class:`int`
        The amount of frames sent.
    nulled: :class:`int`
        The amount of frames nulled.
    deficit: :class:`int`
        The amount of frames deficit.
    """

    __slots__ = ("sent", "nulled", "deficit")

    def __init__(self, payload: FrameStatsPayload) -> None:
        self.sent: int = payload["sent"]
        self.nulled: int = payload["nulled"]
        self.deficit: int = payload["deficit"]


class NodeStats:
    """Represents stats for a node.

    Attributes
    ----------
    player_count: :class:`int`
        The amount of players connected to the node.
    playing_player_count: :class:`int`
        The amount of players playing on the node.
    uptime: :class:`datetime.timedelta`
        The uptime of the node.
    memory: :class:`MemoryStats`
        The memory stats of the node.
    cpu: :class:`CPUStats`
        The CPU stats of the node.
    frame_stats: :data:`~typing.Optional`\\[:class:`FrameStats`]
        The frame stats of the node.
    """

    __slots__ = (
        "cpu",
        "frame_stats",
        "memory",
        "player_count",
        "playing_player_count",
        "uptime",
    )

    def __init__(self, data: Stats) -> None:
        self.player_count: int = data["players"]
        self.playing_player_count: int = data["playingPlayers"]
        self.uptime: timedelta = timedelta(seconds=data["uptime"])
        self.memory: MemoryStats = MemoryStats(data["memory"])
        self.cpu: CPUStats = CPUStats(data["cpu"])
        self.frame_stats: FrameStats | None = (
            FrameStats(data["frameStats"]) if "frameStats" in data else None
        )
