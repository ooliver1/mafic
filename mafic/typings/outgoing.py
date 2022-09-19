# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, Union

from ..__libraries import VoiceServerUpdatePayload
from .misc import PayloadWithGuild

if TYPE_CHECKING:
    from typing_extensions import NotRequired

__all__ = (
    "ChannelMix",
    "ConfigureResumingPayload",
    "DestroyPayload",
    "Distortion",
    "EQBand",
    "FilterPayload",
    "Karaoke",
    "LavalinkVoiceState",
    "LowPass",
    "OutgoingMessage",
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


class LavalinkVoiceState(TypedDict, total=False):
    guildId: str
    sessionId: str
    event: VoiceServerUpdatePayload


class VoiceStatePayload(PayloadWithGuild):
    op: Literal["voiceUpdate"]
    sessionId: str
    event: VoiceServerUpdatePayload


class PlayPayload(PayloadWithGuild):
    op: Literal["play"]
    track: str
    startTime: NotRequired[str]
    endTime: NotRequired[str]
    volume: NotRequired[str]
    noReplace: NotRequired[bool]
    pause: NotRequired[bool]


class StopPayload(PayloadWithGuild):
    op: Literal["stop"]


class PausePayload(PayloadWithGuild):
    op: Literal["pause"]
    pause: bool


class SeekPayload(PayloadWithGuild):
    op: Literal["seek"]
    position: int


class VolumePayload(PayloadWithGuild):
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


class FilterPayload(PayloadWithGuild):
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


class DestroyPayload(PayloadWithGuild):
    op: Literal["destroy"]


class ConfigureResumingPayload(TypedDict):
    op: Literal["configureResuming"]
    key: str | None
    timeout: int


OutgoingMessage = Union[
    VoiceStatePayload,
    PlayPayload,
    StopPayload,
    PausePayload,
    SeekPayload,
    VolumePayload,
    FilterPayload,
    DestroyPayload,
    ConfigureResumingPayload,
]
