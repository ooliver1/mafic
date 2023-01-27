# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from .track import Track

if TYPE_CHECKING:
    from .typings import PlaylistInfo, TrackWithInfo

__all__ = ("Playlist",)


class Playlist:
    """Represents a playlist.

    Attributes
    ----------
    name: :class:`str`
        The name of the playlist.
    selected_track: :class:`int`
        The index of the selected track, if any.
    tracks: :class:`list`\\[:class:`Track`]
        A list of tracks in the playlist.
    """

    __slots__ = ("name", "selected_track", "tracks")

    def __init__(self, *, info: PlaylistInfo, tracks: list[TrackWithInfo]):
        self.name: str = info["name"]
        self.selected_track: int = info["selectedTrack"]
        self.tracks: list[Track] = [
            Track.from_data_with_info(track) for track in tracks
        ]
