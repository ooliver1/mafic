# SPDX-License-Identifier: MIT

from __future__ import annotations

from base64 import b64decode
from typing import Iterator

from ..track import Track

__all__ = ("decode_track",)


def _bytes_to_int(bytes: list[int]) -> int:
    result = 0
    for b in bytes:
        result = result * 256 + b

    return result


class _TrackDataIterator(Iterator[int]):
    __slots__ = ("__previous_null", "flags", "__iterable", "size", "version")

    _TRACK_INFO_VERSIONED = 1
    _FLAG_MASK = 0xC0000000

    def __init__(self, data: bytes):
        self.__iterable = iter(data)

        # https://github.com/sedmelluq/lavaplayer/blob/97a8efecfe3cb79da4d7d0422de0179e18c30947/main/src/main/java/com/sedmelluq/discord/lavaplayer/tools/io/MessageInput.java#L37
        value = self.read_int(bit_length=4)
        self.flags = (value & self._FLAG_MASK) >> 30
        self.size = value & 0x3FFFFFFF
        self.version = (
            self.read_int(bit_length=1) & 0xFF
            if (self.flags & self._TRACK_INFO_VERSIONED) != 0
            else 1
        )
        self.__previous_null = False
        """A value which only bool cares about, string sets it when it leaves."""

    def __next__(self) -> int:
        b = next(self.__iterable)

        try:
            if self.__previous_null and b:
                self.__previous_null = False
        # Somehow this can have an AttributeError on creation?
        except AttributeError:
            pass

        return b

    def read_line(self) -> list[int]:
        line: list[int] = []

        # Checks against NULL bytes - end of "line".
        # Check "or not line" to skip multiple prefixed NULL bytes.
        while byte := next(self) or not line:
            # ASCII for header beginning.
            if byte <= 0x20 and not line:
                continue

            line.append(byte)

        self.__previous_null = True
        return line

    def read_str(self) -> str:
        # Support all unicode code points.
        return "".join(map(chr, self.read_line()))

    def read_int(self, *, bit_length: int = 8) -> int:
        return _bytes_to_int([next(self) for _ in range(bit_length)])

    def read_bool(self) -> bool:
        if self.__previous_null:
            self.__previous_null = False
            return False

        return bool(next(self))

    def read_nullable_str(self) -> str | None:
        # URLs seem to be prefixed with `+`
        exists = self.read_bool()

        if not exists:
            return None

        if (byte := next(self)) != 0:
            raise ValueError(
                "Attempted to traverse a track id "
                f"and came across an unexpected character: {byte}."
            )

        return self.read_str()


def decode_track(track_id: str) -> Track:
    """Decode a track id into a Track object.

    .. warning::

        This still needs a lot of testing and may not work for many tracks.
        Custom fields on plugins are not implemented and positions in tracks
        may not work. Use at your own risk.

    Parameters
    ----------
    track_id:
        The track id to decode.

    Returns
    -------
    Track:
        The decoded track.
    """

    raw = b64decode(track_id)
    print(raw)
    iterator = _TrackDataIterator(raw)

    # https://github.com/sedmelluq/lavaplayer/blob/97a8efecfe3cb79da4d7d0422de0179e18c30947/main/src/main/java/com/sedmelluq/discord/lavaplayer/player/DefaultAudioPlayerManager.java#L268
    title = iterator.read_str()
    author = iterator.read_str()
    length = iterator.read_int()
    identifier = iterator.read_str()
    stream = iterator.read_bool()
    if iterator.version >= 2:
        uri = iterator.read_nullable_str()
        if uri is not None:
            while not uri.startswith("http"):
                uri = uri[1:]
    else:
        uri = None

    source = iterator.read_str()

    # HACK: Needs testing with an encoded track with a position.
    # Who knows how you get that!?!?!?!?!??!?!?
    try:
        position = iterator.read_int()
    except StopIteration:
        position = 0

    # TODO: remove once tested enough
    # print("title:".ljust(20), title)
    # print("author:".ljust(20), author)
    # print("length:".ljust(20), length)
    # print("identifier:".ljust(20), identifier)
    # print("stream:".ljust(20), stream)
    # print("uri:".ljust(20), uri)
    # print("source:".ljust(20), source)
    # print("position:".ljust(20), position)

    return Track(
        track_id=track_id,
        title=title,
        author=author,
        length=length,
        identifier=identifier,
        stream=stream,
        uri=uri,
        source=source,
        # https://github.com/sedmelluq/lavaplayer/blob/84f0d36a6b32a40bf9ab290ca5590d578ddc5d24/main/src/main/java/com/sedmelluq/discord/lavaplayer/track/BaseAudioTrack.java#L71
        seekable=not stream,
        position=position,
    )
