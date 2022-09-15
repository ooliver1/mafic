# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, Union

from ..__libraries import VoiceServerUpdatePayload

if TYPE_CHECKING:
    from typing_extensions import NotRequired

__all__ = (
    "ChannelMix",
    "DestroyPayload",
    "Distortion",
    "EQBand",
    "FilterPayload",
    "Karaoke",
    "LavalinkVoiceState",
    "LowPass",
    "OutgoingMessage",
    "OutgoingMessagePayload",
    "PausePayload",
    "PlayPayload",
    "Rotation",
    "SeekPayload",
    "StopPayload",
    "Timescale",
    "Tremolo",
    "Vibrato",
    "VoiceStatePayload",
    "VolumePayload",
)


class OutgoingMessagePayload(TypedDict):
    guildId: str


class LavalinkVoiceState(TypedDict, total=False):
    guildId: str
    sessionId: str
    event: VoiceServerUpdatePayload


class VoiceStatePayload(OutgoingMessagePayload):
    op: Literal["voiceUpdate"]
    sessionId: str
    event: VoiceServerUpdatePayload


class PlayPayload(OutgoingMessagePayload):
    op: Literal["play"]
    track: str
    startTime: str
    endTime: str
    volume: str
    noReplace: bool
    pause: bool


class StopPayload(OutgoingMessagePayload):
    op: Literal["stop"]


class PausePayload(OutgoingMessagePayload):
    op: Literal["pause"]
    pause: bool


class SeekPayload(OutgoingMessagePayload):
    op: Literal["seek"]
    position: int


class VolumePayload(OutgoingMessagePayload):
    op: Literal["volume"]
    volume: int


class EQBand(TypedDict):
    band: int
    gain: float


class Karaoke(TypedDict):
    level: float
    monoLevel: float
    filterBand: float
    filterWidth: float


class Timescale(TypedDict):
    speed: float
    pitch: float
    rate: float


class Tremolo(TypedDict):
    frequency: float
    depth: float


class Vibrato(TypedDict):
    frequency: float
    depth: float


class Rotation(TypedDict):
    rotationHz: float


class Distortion(TypedDict):
    sinOffset: float
    sinScale: float
    cosOffset: float
    cosScale: float
    tanOffset: float
    tanScale: float
    offset: float
    scale: float


class ChannelMix(TypedDict):
    leftToLeft: float
    leftToRight: float
    rightToLeft: float
    rightToRight: float


class LowPass(TypedDict):
    smoothing: float


class FilterPayload(OutgoingMessagePayload):
    op: Literal["filters"]
    volume: NotRequired[float]
    equalizer: NotRequired[list[EQBand]]
    karaoke: NotRequired[Karaoke]
    timescale: NotRequired[Timescale]
    tremolo: NotRequired[Tremolo]
    vibrato: NotRequired[Vibrato]
    rotation: NotRequired[Rotation]
    distortion: NotRequired[Distortion]
    channelMix: NotRequired[ChannelMix]
    lowPass: NotRequired[LowPass]


class DestroyPayload(OutgoingMessagePayload):
    op: Literal["destroy"]


OutgoingMessage = Union[
    VoiceStatePayload,
    PlayPayload,
    StopPayload,
    PausePayload,
    SeekPayload,
    VolumePayload,
    FilterPayload,
    DestroyPayload,
]
