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
    def __init__(self, payload: CPU) -> None:
        self.cores: int = payload["cores"]
        self.system_load: int = payload["systemLoad"]
        self.lavalink_load: int = payload["lavalinkLoad"]


class MemoryStats:
    def __init__(self, payload: Memory) -> None:
        self.free: int = payload["free"]
        self.used: int = payload["used"]
        self.allocated: int = payload["allocated"]
        self.reservable: int = payload["reservable"]


class FrameStats:
    def __init__(self, payload: FrameStatsPayload) -> None:
        self.sent: int = payload["sent"]
        self.nulled: int = payload["nulled"]
        self.deficit: int = payload["deficit"]


class NodeStats:
    def __init__(self, data: Stats) -> None:
        self.player_count: int = data["players"]
        self.playing_player_count: int = data["playingPlayers"]
        self.uptime: timedelta = timedelta(seconds=data["uptime"])
        self.memory: MemoryStats = MemoryStats(data["memory"])
        self.cpu: CPUStats = CPUStats(data["cpu"])
        self.frame_stats: FrameStats | None = (
            FrameStats(data["frameStats"]) if data["frameStats"] is not None else None
        )
