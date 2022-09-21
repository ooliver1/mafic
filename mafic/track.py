# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .typings import TrackInfo

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

    def __init__(self, track: str, info: TrackInfo) -> None:
        self.id = track

        self.title: str = info["title"]
        self.author: str = info["author"]

        self.identifier: str = info["identifier"]
        self.uri: str = info["uri"]
        self.source: str = info["sourceName"]

        self.stream: bool = info["isStream"]
        self.seekable: bool = info["isSeekable"]

        self.position: int = info["position"]
        self.length: int = info["length"]
