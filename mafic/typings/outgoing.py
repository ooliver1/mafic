# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Union

if TYPE_CHECKING:
    from typing_extensions import NotRequired


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


class ConfigureResumingPayload(TypedDict, total=False):
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


OutgoingMessage = Union[
    UpdatePlayerPayload,
    ConfigureResumingPayload,
]
