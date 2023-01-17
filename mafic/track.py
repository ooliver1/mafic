# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .typings import TrackInfo, TrackWithInfo

__all__ = ("Track",)


class Track:
    __slots__ = (
        "author",
        "id",
        "identifier",
        "length",
        "position",
        "seekable",
        "source",
        "stream",
        "title",
        "uri",
    )

    def __init__(
        self,
        *,
        track_id: str,
        title: str,
        author: str,
        identifier: str,
        uri: str | None,
        source: str,
        stream: bool,
        seekable: bool,
        position: int = 0,
        length: int,
    ) -> None:
        self.id: str = track_id

        self.title: str = title
        self.author: str = author

        self.identifier: str = identifier
        self.uri: str | None = uri
        self.source: str = source

        self.stream: bool = stream

        self.seekable: bool = seekable

        self.position: int = position
        self.length: int = length

    @classmethod
    def from_data(cls, *, track: str, info: TrackInfo) -> Self:
        return cls(
            track_id=track,
            title=info["title"],
            author=info["author"],
            identifier=info["identifier"],
            uri=info["uri"],
            source=info["sourceName"],
            stream=info["isStream"],
            seekable=info["isSeekable"],
            position=info["position"],
            length=info["length"],
        )

    @classmethod
    def from_data_with_info(cls, data: TrackWithInfo) -> Self:
        return cls.from_data(track=data["encoded"], info=data["info"])
