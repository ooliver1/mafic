# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Union

if TYPE_CHECKING:
    from typing import Literal

    from .misc import FriendlyException

__all__ = (
    "GetTracks",
    "PlaylistInfo",
    "PluginData",
    "Tracks",
    "TrackInfo",
    "TrackWithInfo",
    "TracksFailed",
)


class PlaylistInfo(TypedDict):
    name: str
    selectedTrack: int


class TrackInfo(TypedDict):
    identifier: str
    isSeekable: bool
    author: str
    length: int
    isStream: bool
    position: int
    sourceName: str
    title: str
    uri: str


class TrackWithInfo(TypedDict):
    track: str
    info: TrackInfo


class Tracks(TypedDict):
    loadType: Literal["TRACK_LOADED", "PLAYLIST_LOADED", "SEARCH_RESULT", "NO_MATCHES"]
    playlistInfo: PlaylistInfo
    tracks: list[TrackWithInfo]


class TracksFailed(TypedDict):
    loadType: Literal["LOAD_FAILED"]
    playlistInfo: PlaylistInfo
    tracks: list[TrackWithInfo]
    exception: FriendlyException


GetTracks = Union[Tracks, TracksFailed]


class PluginData(TypedDict):
    name: str
    version: str
