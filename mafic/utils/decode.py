# SPDX-License-Identifier: MIT

from __future__ import annotations

from base64 import b64decode
from typing import Iterator

__all__ = ("decode_track",)


def _bytes_to_int(bytes: list[int]) -> int:
    result = 0
    for b in bytes:
        result = result * 256 + b

    return result


class _TrackDataIterator(Iterator[int]):
    TRACK_INFO_VERSIONED = 1

    def __init__(self, data: bytes):
        self.iterable = iter(data)

        # https://github.com/sedmelluq/lavaplayer/blob/97a8efecfe3cb79da4d7d0422de0179e18c30947/main/src/main/java/com/sedmelluq/discord/lavaplayer/tools/io/MessageInput.java#L37
        value = self.read_int(bit_length=4)
        self.flags = (value & 0xC0000000) >> 30
        self.size = value & 0x3FFFFFFF
        self.version = (
            self.read_int(bit_length=1)
            if (self.flags & self.TRACK_INFO_VERSIONED) != 0
            else 1
        )
        self.__previous_null = False
        """A value which only bool cares about, string sets it when it leaves."""

    def __next__(self) -> int:
        b = next(self.iterable)

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

        if (byte := next(self)) != 0 or (byte := next(self)) != 43:
            raise ValueError(
                "Attempted to traverse a track id "
                f"and came across an unexpected character: {byte}."
            )

        return self.read_str()


def decode_track(track: str):
    raw = b64decode(track)
    iterator = _TrackDataIterator(raw)

    title = iterator.read_str()
    author = iterator.read_str()
    length = iterator.read_int()
    ident = iterator.read_str()
    is_stream = iterator.read_bool()
    if iterator.version >= 2:
        uri = iterator.read_nullable_str()
    else:
        uri = None

    position = iterator.read_int()

    del title, author, length, ident, is_stream, uri, position
