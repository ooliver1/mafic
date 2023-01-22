# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .typings import TrackInfo, TrackWithInfo

__all__ = ("Track",)


class Track:
    """Represents a track.

    Parameters
    ----------
    track_id:
        The ID of the track.
    title:
        The title of the track.
    identifier:
        The identifier of the track.
    uri:
        The URI of the track.
    source:
        The source of the track.
    stream:
        Whether the track is a stream.
    seekable:
        Whether the track is seekable.
    position:
        The current position of the track.
    length:
        The length of the track.

    Attributes
    ----------
    id:
        The ID of the track. This is base64 encoded data used by Lavalink.
    title:
        The title of the track.
    author:
        The author of the track.
    identifier:
        The identifier of the track. This is the ID of the track on the source.
    uri:
        The URI of the track.
    source:
        The source of the track.
    stream:
        Whether the track is a stream.
    seekable:
        Whether the track is seekable.
    position:
        The current position of the track.
    length:
        The length of the track.
    """

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
        """Create a track from the raw data.

        Parameters
        ----------
        track:
            The ID of the track.
        info:
            The track info.

        Returns
        -------
        Track:
            The track.
        """

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
        """Create a track from the raw data, bundled with the track and info.

        Parameters
        ----------
        data:
            The track and info.

        Returns
        -------
        Track:
            The track.
        """

        return cls.from_data(track=data["encoded"], info=data["info"])
