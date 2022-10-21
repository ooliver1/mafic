# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Optional

    from .typings import (
        ChannelMix as ChannelMixPayload,
        Distortion as DistortionPayload,
        EQBand as EQBandPayload,
        Karaoke as KaraokePayload,
        LowPass as LowPassPayload,
        RawFilterPayload as FilterPayload,
        Rotation as RotationPayload,
        Timescale as TimescalePayload,
        Tremolo as TremoloPayload,
        Vibrato as VibratoPayload,
    )


__all__ = (
    "ChannelMix",
    "Distortion",
    "EQBand",
    "Karaoke",
    "LowPass",
    "Rotation",
    "Timescale",
    "Tremolo",
    "Vibrato",
)


@dataclass(repr=True)
class EQBand:
    band: int
    gain: float

    @property
    def payload(self) -> EQBandPayload:
        return {"band": self.band, "gain": self.gain}


@dataclass(repr=True)
class Equalizer:
    bands: list[EQBand]

    @property
    def payload(self) -> list[EQBandPayload]:
        return [band.payload for band in self.bands]


@dataclass(repr=True)
class Karaoke:
    level: float
    mono_level: float
    filter_band: float
    filter_width: float

    @property
    def payload(self) -> KaraokePayload:
        return {
            "level": self.level,
            "monoLevel": self.mono_level,
            "filterBand": self.filter_band,
            "filterWidth": self.filter_width,
        }


@dataclass(repr=True)
class Timescale:
    speed: float
    pitch: float
    rate: float

    @property
    def payload(self) -> TimescalePayload:
        return {
            "speed": self.speed,
            "pitch": self.pitch,
            "rate": self.rate,
        }


@dataclass(repr=True)
class Tremolo:
    frequency: float
    depth: float

    @property
    def payload(self) -> TremoloPayload:
        return {
            "frequency": self.frequency,
            "depth": self.depth,
        }


@dataclass(repr=True)
class Vibrato:
    frequency: float
    depth: float

    @property
    def payload(self) -> VibratoPayload:
        return {
            "frequency": self.frequency,
            "depth": self.depth,
        }


@dataclass(repr=True)
class Rotation:
    rotation_hz: float

    @property
    def payload(self) -> RotationPayload:
        return {"rotationHz": self.rotation_hz}


@dataclass(repr=True)
class Distortion:
    sin_offset: float
    sin_scale: float
    cos_offset: float
    cos_scale: float
    tan_offset: float
    tan_scale: float
    offset: float
    scale: float

    @property
    def payload(self) -> DistortionPayload:
        return {
            "sinOffset": self.sin_offset,
            "sinScale": self.sin_scale,
            "cosOffset": self.cos_offset,
            "cosScale": self.cos_scale,
            "tanOffset": self.tan_offset,
            "tanScale": self.tan_scale,
            "offset": self.offset,
            "scale": self.scale,
        }


@dataclass(repr=True)
class ChannelMix:
    left_to_left: float
    left_to_right: float
    right_to_left: float
    right_to_right: float

    @property
    def payload(self) -> ChannelMixPayload:
        return {
            "leftToLeft": self.left_to_left,
            "leftToRight": self.left_to_right,
            "rightToLeft": self.right_to_left,
            "rightToRight": self.right_to_right,
        }


@dataclass(repr=True)
class LowPass:
    smoothing: float

    @property
    def payload(self) -> LowPassPayload:
        return {"smoothing": self.smoothing}


@dataclass(repr=True)
class Filter:
    equalizer: Optional[Equalizer]
    karaoke: Optional[Karaoke]
    timescale: Optional[Timescale]
    tremolo: Optional[Tremolo]
    vibrato: Optional[Vibrato]
    rotation: Optional[Rotation]
    distortion: Optional[Distortion]
    channel_mix: Optional[ChannelMix]
    low_pass: Optional[LowPass]
    volume: Optional[float]

    @property
    def payload(self) -> FilterPayload:
        payload: FilterPayload = {}

        if self.equalizer:
            payload["equalizer"] = self.equalizer.payload

        if self.karaoke:
            payload["karaoke"] = self.karaoke.payload

        if self.timescale:
            payload["timescale"] = self.timescale.payload

        if self.tremolo:
            payload["tremolo"] = self.tremolo.payload

        if self.vibrato:
            payload["vibrato"] = self.vibrato.payload

        if self.rotation:
            payload["rotation"] = self.rotation.payload

        if self.distortion:
            payload["distortion"] = self.distortion.payload

        if self.channel_mix:
            payload["channelMix"] = self.channel_mix.payload

        if self.low_pass:
            payload["lowPass"] = self.low_pass.payload

        if self.volume:
            payload["volume"] = self.volume

        return payload

    def __or__(self, other: Any) -> Filter:
        if not isinstance(other, Filter):
            raise TypeError(f"Expected Filter instance, not {type(other)!r}")

        return Filter(
            equalizer=other.equalizer or self.equalizer,
            karaoke=other.karaoke or self.karaoke,
            timescale=other.timescale or self.timescale,
            tremolo=other.tremolo or self.tremolo,
            vibrato=other.vibrato or self.vibrato,
            rotation=other.rotation or self.rotation,
            distortion=other.distortion or self.distortion,
            channel_mix=other.channel_mix or self.channel_mix,
            low_pass=other.low_pass or self.low_pass,
            volume=other.volume or self.volume,
        )

    def __ior__(self, other: Any) -> None:
        if not isinstance(other, Filter):
            raise TypeError(f"Expected Filter instance, not {type(other)!r}")

        self.equalizer = other.equalizer or self.equalizer
        self.karaoke = other.karaoke or self.karaoke
        self.timescale = other.timescale or self.timescale
        self.tremolo = other.tremolo or self.tremolo
        self.vibrato = other.vibrato or self.vibrato
        self.rotation = other.rotation or self.rotation
        self.distortion = other.distortion or self.distortion
        self.channel_mix = other.channel_mix or self.channel_mix
        self.low_pass = other.low_pass or self.low_pass
        self.volume = other.volume or self.volume

    def __and__(self, other: Any) -> Filter:
        if not isinstance(other, Filter):
            raise TypeError(f"Expected Filter instance, not {type(other)!r}")

        return Filter(
            equalizer=self.equalizer or other.equalizer,
            karaoke=self.karaoke or other.karaoke,
            timescale=self.timescale or other.timescale,
            tremolo=self.tremolo or other.tremolo,
            vibrato=self.vibrato or other.vibrato,
            rotation=self.rotation or other.rotation,
            distortion=self.distortion or other.distortion,
            channel_mix=self.channel_mix or other.channel_mix,
            low_pass=self.low_pass or other.low_pass,
            volume=self.volume or other.volume,
        )

    def __iand__(self, other: Any) -> None:
        if not isinstance(other, Filter):
            raise TypeError(f"Expected Filter instance, not {type(other)!r}")

        self.equalizer = self.equalizer or other.equalizer
        self.karaoke = self.karaoke or other.karaoke
        self.timescale = self.timescale or other.timescale
        self.tremolo = self.tremolo or other.tremolo
        self.vibrato = self.vibrato or other.vibrato
        self.rotation = self.rotation or other.rotation
        self.distortion = self.distortion or other.distortion
        self.channel_mix = self.channel_mix or other.channel_mix
        self.low_pass = self.low_pass or other.low_pass
        self.volume = self.volume or other.volume
