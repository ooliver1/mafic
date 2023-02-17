# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from .misc import PayloadWithGuild

if TYPE_CHECKING:
    from typing_extensions import NotRequired

__all__ = (
    "Filters",
    "ChannelMix",
    "EQBand",
    "Distortion",
    "Filters",
    "Karaoke",
    "LowPass",
    "Player",
    "PlaylistInfo",
    "Rotation",
    "Timescale",
    "TrackInfo",
    "TrackWithInfo",
    "Tremolo",
    "Vibrato",
    "VoiceState",
    "VoiceStateRequest",
    "Memory",
    "CPU",
    "FrameStats",
    "Stats",
)


class EQBand(TypedDict):
    band: int
    gain: float


class Karaoke(TypedDict, total=False):
    level: float
    monoLevel: float
    filterBand: float
    filterWidth: float


class Timescale(TypedDict, total=False):
    speed: float
    pitch: float
    rate: float


class Tremolo(TypedDict, total=False):
    frequency: float
    depth: float


class Vibrato(TypedDict, total=False):
    frequency: float
    depth: float


class Rotation(TypedDict, total=False):
    rotationHz: float


class Distortion(TypedDict, total=False):
    sinOffset: float
    sinScale: float
    cosOffset: float
    cosScale: float
    tanOffset: float
    tanScale: float
    offset: float
    scale: float


class ChannelMix(TypedDict, total=False):
    leftToLeft: float
    leftToRight: float
    rightToLeft: float
    rightToRight: float


class LowPass(TypedDict, total=False):
    smoothing: float


class Filters(TypedDict, total=False):
    volume: float
    equalizer: list[EQBand]
    karaoke: Karaoke
    timescale: Timescale
    tremolo: Tremolo
    vibrato: Vibrato
    rotation: Rotation
    distortion: Distortion
    channelMix: ChannelMix
    lowPass: LowPass


class Player(PayloadWithGuild):
    track: TrackWithInfo | None
    volume: int
    paused: bool
    voice: VoiceState
    filters: Filters


class VoiceStateRequest(TypedDict):
    token: str
    endpoint: str
    sessionId: str


class VoiceState(VoiceStateRequest):
    connected: bool
    ping: int


class PlaylistInfo(TypedDict):
    name: str
    selectedTrack: int


class TrackInfo(TypedDict):
    identifier: str
    isSeekable: bool
    author: str
    length: int
    isStream: bool
    position: int
    title: str
    uri: str
    sourceName: str


class TrackWithInfo(TypedDict):
    encoded: str
    info: TrackInfo


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


class Stats(TypedDict):
    op: Literal["stats"]
    players: int
    playingPlayers: int
    uptime: int
    memory: Memory
    cpu: CPU
    frameStats: NotRequired[FrameStats]
