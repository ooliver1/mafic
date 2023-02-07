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
    id: :class:`str`
        The ID of the track. This is base64 encoded data used by Lavalink.
    title: :class:`str`
        The title of the track.
    author: :class:`str`
        The author of the track.
    identifier: :class:`str`
        The identifier of the track. This is the ID of the track on the source.
    uri: :data:`~typing.Optional`\\[:class:`str`]
        The URI of the track.
    source: :class:`str`
        The source of the track.
    stream: :class:`bool`
        Whether the track is a stream.
    seekable: :class:`bool`
        Whether the track is seekable.
    position: :class:`int`
        The current position of the track.
    length: :class:`int`
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
        :class:`Track`
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
        :class:`Track`
            The track.
        """

        return cls.from_data(track=data["encoded"], info=data["info"])

    def __repr__(self) -> str:
        attrs = (
            ("id", self.id),
            ("title", self.title),
            ("author", self.author),
            ("identifier", self.identifier),
            ("uri", self.uri),
            ("source", self.source),
            ("stream", self.stream),
            ("seekable", self.seekable),
            ("position", self.position),
            ("length", self.length),
        )

        resolved = " ".join(f"{name}={value!r}" for name, value in attrs)
        return f"<{type(self).__name__} {resolved}>"
