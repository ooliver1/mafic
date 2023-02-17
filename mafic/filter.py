# SPDX-License-Identifier: MIT
# Reference to filter meanings can be found in:
# https://github.com/natanbc/lavadsp

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from typing_extensions import Self

    from .typings import (
        ChannelMix as ChannelMixPayload,
        Distortion as DistortionPayload,
        EQBand as EQBandPayload,
        Filters,
        Karaoke as KaraokePayload,
        LowPass as LowPassPayload,
        Rotation as RotationPayload,
        Timescale as TimescalePayload,
        Tremolo as TremoloPayload,
        Vibrato as VibratoPayload,
    )


__all__ = (
    "ChannelMix",
    "Distortion",
    "EQBand",
    "Equalizer",
    "Filter",
    "Karaoke",
    "LowPass",
    "Rotation",
    "Timescale",
    "Tremolo",
    "Vibrato",
)


@dataclass(unsafe_hash=True)
class EQBand:
    """Represents an `equaliser`_ band.

    .. _equaliser: https://en.wikipedia.org/wiki/Equalization_(audio)

    Attributes
    ----------
    band: :class:`int`
        The band to set the gain of. Must be between ``0`` and ``14``.
    gain: :class:`float`
        The gain to set the band to. Must be between ``-0.25`` and ``1.0``.
    """

    band: int
    gain: float

    @property
    def payload(self) -> EQBandPayload:
        """Generate the raw Lavalink payload for this band."""

        return {"band": self.band, "gain": self.gain}


@dataclass(unsafe_hash=True)
class Equalizer:
    """Represents an `equaliser`_.

    .. _equaliser: https://en.wikipedia.org/wiki/Equalization_(audio)

    Attributes
    ----------
    bands: :class:`list`\\[:class:`EQBand`]
        The bands to set the gains of.
    """

    bands: list[EQBand]

    @property
    def payload(self) -> list[EQBandPayload]:
        return [band.payload for band in self.bands]

    @classmethod
    def from_payload(cls, payload: list[EQBandPayload]) -> Self:
        return cls(
            bands=[EQBand(band=band["band"], gain=band["gain"]) for band in payload]
        )


@dataclass(unsafe_hash=True)
class Karaoke:
    """Represents a filter which can be used to eliminate part of a band.

    This usually targets vocals, to sound like karaoke music.

    Attributes
    ----------
    level: :data:`~typing.Optional`\\[:class:`float`]
        The level of the karaoke effect. Must be between ``0.0`` and ``1.0``.
        Where ``0.0`` is no effect and ``1.0`` is full effect.
        This defaults to ``1.0``.
    mono_level: :data:`~typing.Optional`\\[:class:`float`]
        The level of the mono effect. Must be between ``0.0`` and ``1.0``.
        Where ``0.0`` is no effect and ``1.0`` is full effect.
        This defaults to ``1.0``.
    filter_band: :data:`~typing.Optional`\\[:class:`float`]
        The frequency of the filter band in Hz.
        This defaults to ``220.0``.
    filter_width: :data:`~typing.Optional`\\[:class:`float`]
        The width of the filter band.
        This defaults to ``100.0``.
    """

    level: float | None = None
    mono_level: float | None = None
    filter_band: float | None = None
    filter_width: float | None = None

    @property
    def payload(self) -> KaraokePayload:
        """Generate the raw Lavalink payload for this filter."""

        data: KaraokePayload = {}

        if self.level is not None:
            data["level"] = self.level

        if self.mono_level is not None:
            data["monoLevel"] = self.mono_level

        if self.filter_band is not None:
            data["filterBand"] = self.filter_band

        if self.filter_width is not None:
            data["filterWidth"] = self.filter_width

        return data

    @classmethod
    def from_payload(cls, payload: KaraokePayload) -> Self:
        return cls(
            level=payload.get("level"),
            mono_level=payload.get("monoLevel"),
            filter_band=payload.get("filterBand"),
            filter_width=payload.get("filterWidth"),
        )


@dataclass(unsafe_hash=True)
class Timescale:
    """Represents a filter which can be used to change the speed,
    pitch and rate of audio.

    Attributes
    ----------
    speed: :data:`~typing.Optional`\\[:class:`float`]
        The speed of the audio. Must be at least ``0.0``. ``1.0`` is normal speed.
    pitch: :data:`~typing.Optional`\\[:class:`float`]
        The pitch of the audio. Must be at least ``0.0``. ``1.0`` is normal pitch.
    rate: :data:`~typing.Optional`\\[:class:`float`]
        The rate of the audio. Must be at least ``0.0``. ``1.0`` is normal rate.
    """

    speed: float | None = None
    pitch: float | None = None
    rate: float | None = None

    @property
    def payload(self) -> TimescalePayload:
        """Generate the raw Lavalink payload for this filter."""

        data: TimescalePayload = {}

        if self.speed is not None:
            data["speed"] = self.speed

        if self.pitch is not None:
            data["pitch"] = self.pitch

        if self.rate is not None:
            data["rate"] = self.rate

        return data

    @classmethod
    def from_payload(cls, payload: TimescalePayload) -> Self:
        return cls(
            speed=payload.get("speed"),
            pitch=payload.get("pitch"),
            rate=payload.get("rate"),
        )


@dataclass(unsafe_hash=True)
class Tremolo:
    """Represents a filter which can be used to add a `tremolo`_ effect to audio.

    Tremolo oscillates the volume of the audio.

    .. _tremolo: https://en.wikipedia.org/wiki/Tremolo

    Attributes
    ----------
    frequency: :data:`~typing.Optional`\\[:class:`float`]
        The frequency of the tremolo effect. Must be at least ``0.0``.
        This defaults to ``2.0``.
    depth: :data:`~typing.Optional`\\[:class:`float`]
        The depth of the tremolo effect. Must be between ``0.0`` and ``1.0``.
        Where ``0.0`` is no effect and ``1.0`` is full effect.
        This defaults to ``0.5``.
    """

    frequency: float | None = None
    depth: float | None = None

    @property
    def payload(self) -> TremoloPayload:
        """Generate the raw Lavalink payload for this filter."""

        data: TremoloPayload = {}

        if self.frequency is not None:
            data["frequency"] = self.frequency

        if self.depth is not None:
            data["depth"] = self.depth

        return data

    @classmethod
    def from_payload(cls, payload: TremoloPayload) -> Self:
        return cls(
            frequency=payload.get("frequency"),
            depth=payload.get("depth"),
        )


@dataclass(repr=True)
class Vibrato:
    """Represents a filter which can be used to add a `vibrato`_ effect to audio.

    Vibrato oscillates the pitch of the audio.

    .. _vibrato: https://en.wikipedia.org/wiki/Vibrato

    Attributes
    ----------
    frequency: :data:`~typing.Optional`\\[:class:`float`]
        The frequency of the vibrato effect. Must be at least ``0.0``.
        This defaults to ``2.0``.
    depth: :data:`~typing.Optional`\\[:class:`float`]
        The depth of the vibrato effect. Must be between ``0.0`` and ``1.0``.
        Where ``0.0`` is no effect and ``1.0`` is full effect.
        This defaults to ``0.5``.
    """

    frequency: float | None = None
    depth: float | None = None

    @property
    def payload(self) -> VibratoPayload:
        """Generate the raw Lavalink payload for this filter."""

        data: VibratoPayload = {}

        if self.frequency is not None:
            data["frequency"] = self.frequency

        if self.depth is not None:
            data["depth"] = self.depth

        return data

    @classmethod
    def from_payload(cls, payload: VibratoPayload) -> Self:
        return cls(
            frequency=payload.get("frequency"),
            depth=payload.get("depth"),
        )


@dataclass(unsafe_hash=True)
class Rotation:
    """Represents a filter which can be used to add a rotating effect to audio.

    An example can be with `"8D audio" (without the reverb)`_.

    .. _"8D audio" (without the reverb): https://youtu.be/QB9EB8mTKcc>

    Attributes
    ----------
    rotation_hz: :data:`~typing.Optional`\\[:class:`float`]
        The rotation speed in Hz. Must be at least ``0.0``.
        ``0.2`` is similar to the example above.
    """

    rotation_hz: float | None = None

    @property
    def payload(self) -> RotationPayload:
        """Generate the raw Lavalink payload for this filter."""

        data: RotationPayload = {}

        if self.rotation_hz is not None:
            data["rotationHz"] = self.rotation_hz

        return data

    @classmethod
    def from_payload(cls, payload: RotationPayload) -> Self:
        return cls(
            rotation_hz=payload.get("rotationHz"),
        )


@dataclass(unsafe_hash=True)
class Distortion:
    """Represents a filter which can be used to add a distortion effect to audio.

    This applies sine, cosine and tangent distortion to the audio.
    The formula that is used::

        sample_sin = sin_offset + math.sin(sample * sin_scale);
        sample_cos = cos_offset + math.cos(sample * cos_scale);
        sample_tan = tan_offset + math.tan(sample * tan_scale);
        sample = max(
            -1,
            min(
                1,
                offset +
                scale * sample_sin * sample_cos * sample_tan
            )
        )

    Attributes
    ----------
    sin_offset: :data:`~typing.Optional`\\[:class:`float`]
        The offset of the sine distortion.
        This defaults to ``0.0``.
    sin_scale: :data:`~typing.Optional`\\[:class:`float`]
        The scale of the sine distortion.
        This defaults to ``1.0``.
    cos_offset: :data:`~typing.Optional`\\[:class:`float`]
        The offset of the cosine distortion.
        This defaults to ``0.0``.
    cos_scale: :data:`~typing.Optional`\\[:class:`float`]
        The scale of the cosine distortion.
        This defaults to ``1.0``.
    tan_offset: :data:`~typing.Optional`\\[:class:`float`]
        The offset of the tangent distortion.
        This defaults to ``0.0``.
    tan_scale: :data:`~typing.Optional`\\[:class:`float`]
        The scale of the tangent distortion.
        This defaults to ``1.0``.
    offset: :data:`~typing.Optional`\\[:class:`float`]
        The offset of the distortion.
        This defaults to ``0.0``.
    scale: :data:`~typing.Optional`\\[:class:`float`]
        The scale of the distortion.
        This defaults to ``1.0``.
    """

    sin_offset: float | None = None
    sin_scale: float | None = None
    cos_offset: float | None = None
    cos_scale: float | None = None
    tan_offset: float | None = None
    tan_scale: float | None = None
    offset: float | None = None
    scale: float | None = None

    @property
    def payload(self) -> DistortionPayload:
        """Generate the raw Lavalink payload for this filter."""

        data: DistortionPayload = {}

        if self.sin_offset is not None:
            data["sinOffset"] = self.sin_offset

        if self.sin_scale is not None:
            data["sinScale"] = self.sin_scale

        if self.cos_offset is not None:
            data["cosOffset"] = self.cos_offset

        if self.cos_scale is not None:
            data["cosScale"] = self.cos_scale

        if self.tan_offset is not None:
            data["tanOffset"] = self.tan_offset

        if self.tan_scale is not None:
            data["tanScale"] = self.tan_scale

        if self.offset is not None:
            data["offset"] = self.offset

        if self.scale is not None:
            data["scale"] = self.scale

        return data

    @classmethod
    def from_payload(cls, payload: DistortionPayload) -> Self:
        return cls(
            sin_offset=payload.get("sinOffset"),
            sin_scale=payload.get("sinScale"),
            cos_offset=payload.get("cosOffset"),
            cos_scale=payload.get("cosScale"),
            tan_offset=payload.get("tanOffset"),
            tan_scale=payload.get("tanScale"),
            offset=payload.get("offset"),
            scale=payload.get("scale"),
        )


@dataclass(unsafe_hash=True)
class ChannelMix:
    """Represents a filter which can be used to mix the audio channels.

    Setting all of these to ``0.5`` will make the audio mono.

    Attributes
    ----------
    left_to_left: :data:`~typing.Optional`\\[:class:`float`]
        The amount of the left channel to mix into the left channel.
        This defaults to ``1.0``.
    left_to_right: :data:`~typing.Optional`\\[:class:`float`]
        The amount of the left channel to mix into the right channel.
        This defaults to ``0.0``.
    right_to_left: :data:`~typing.Optional`\\[:class:`float`]
        The amount of the right channel to mix into the left channel.
        This defaults to ``0.0``.
    right_to_right: :data:`~typing.Optional`\\[:class:`float`]
        The amount of the right channel to mix into the right channel.
        This defaults to ``1.0``.
    """

    left_to_left: float | None = None
    left_to_right: float | None = None
    right_to_left: float | None = None
    right_to_right: float | None = None

    @property
    def payload(self) -> ChannelMixPayload:
        """Generate the raw Lavalink payload for this filter."""

        data: ChannelMixPayload = {}

        if self.left_to_left is not None:
            data["leftToLeft"] = self.left_to_left

        if self.left_to_right is not None:
            data["leftToRight"] = self.left_to_right

        if self.right_to_left is not None:
            data["rightToLeft"] = self.right_to_left

        if self.right_to_right is not None:
            data["rightToRight"] = self.right_to_right

        return data

    @classmethod
    def from_payload(cls, payload: ChannelMixPayload) -> Self:
        return cls(
            left_to_left=payload.get("leftToLeft"),
            left_to_right=payload.get("leftToRight"),
            right_to_left=payload.get("rightToLeft"),
            right_to_right=payload.get("rightToRight"),
        )


@dataclass(unsafe_hash=True)
class LowPass:
    """Represents a filter which can be used to apply a `low pass filter` to audio.

    High frequencies are suppressed, while low frequencies are passed through.

    .. _low pass filter: http://phrogz.net/js/framerate-independent-low-pass-filter.html

    Attributes
    ----------
    smoothing: :data:`~typing.Optional`\\[:class:`float`]
        The smoothing of the low pass filter.
        This defaults to ``0.0``.
    """

    smoothing: float | None = None

    @property
    def payload(self) -> LowPassPayload:
        """Generate the raw Lavalink payload for this filter."""

        data: LowPassPayload = {}

        if self.smoothing is not None:
            data["smoothing"] = self.smoothing

        return data

    @classmethod
    def from_payload(cls, payload: LowPassPayload) -> Self:
        return cls(smoothing=payload.get("smoothing"))


@dataclass(unsafe_hash=True)
class Filter:
    """Represents a filter which can be applied to audio.

    .. container:: operations

        .. describe:: x | y

            Merges two filters together, favouring attributes from y.

        .. describe:: x |= y

            Merges two filters together, favouring attributes from x, assigning to x.

        .. describe:: x & y

            Merges two filters together, favouring attributes from x.

        .. describe:: x &= y

            Merges two filters together, favouring attributes from y, assigning to x.

    Attributes
    ----------
    equalizer: :data:`~typing.Optional`\\[:class:`Equalizer`]
        The equalizer to use.
    karaoke: :data:`~typing.Optional`\\[:class:`Karaoke`]
        The karaoke filter to use.
    timescale: :data:`~typing.Optional`\\[:class:`Timescale`]
        The timescale filter to use.
    tremolo: :data:`~typing.Optional`\\[:class:`Tremolo`]
        The tremolo filter to use.
    vibrato: :data:`~typing.Optional`\\[:class:`Vibrato`]
        The vibrato filter to use.
    rotation: :data:`~typing.Optional`\\[:class:`Rotation`]
        The rotation filter to use.
    distortion: :data:`~typing.Optional`\\[:class:`Distortion`]
        The distortion filter to use.
    channel_mix: :data:`~typing.Optional`\\[:class:`ChannelMix`]
        The channel mix filter to use.
    low_pass: :data:`~typing.Optional`\\[:class:`LowPass`]
        The low pass filter to use.
    volume: :data:`~typing.Optional`\\[:class:`float`]
        The volume to use.
    """

    equalizer: Equalizer | None = None
    karaoke: Karaoke | None = None
    timescale: Timescale | None = None
    tremolo: Tremolo | None = None
    vibrato: Vibrato | None = None
    rotation: Rotation | None = None
    distortion: Distortion | None = None
    channel_mix: ChannelMix | None = None
    low_pass: LowPass | None = None
    volume: float | None = None

    @property
    def payload(self) -> Filters:
        """Generate the raw Lavalink payload for this filter."""

        payload: Filters = {}

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

    @classmethod
    def from_payload(cls, data: Filters) -> Self:
        """Generate a filter from a raw Lavalink payload."""

        self = cls()

        if "equalizer" in data:
            self.equalizer = Equalizer.from_payload(data["equalizer"])

        if "karaoke" in data:
            self.karaoke = Karaoke.from_payload(data["karaoke"])

        if "timescale" in data:
            self.timescale = Timescale.from_payload(data["timescale"])

        if "tremolo" in data:
            self.tremolo = Tremolo.from_payload(data["tremolo"])

        if "vibrato" in data:
            self.vibrato = Vibrato.from_payload(data["vibrato"])

        if "rotation" in data:
            self.rotation = Rotation.from_payload(data["rotation"])

        if "distortion" in data:
            self.distortion = Distortion.from_payload(data["distortion"])

        if "channelMix" in data:
            self.channel_mix = ChannelMix.from_payload(data["channelMix"])

        if "lowPass" in data:
            self.low_pass = LowPass.from_payload(data["lowPass"])

        if "volume" in data:
            self.volume = data["volume"]

        return self

    def __or__(self, other: Any) -> Filter:
        # A | B uses A and replaces B, like dictionaries.

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
        # Like __or__ but |=

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
        # A & B uses A and only B if A does not have that field.

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
        # Like __and__ but &=

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


# TODO: people like easy default filters, add some default EQ and combo filters
