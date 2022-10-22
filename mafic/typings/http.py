# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, Union

if TYPE_CHECKING:
    from .misc import FriendlyException

__all__ = (
    "BalancingIPRouteDetails",
    "BalancingIPRoutePlanner",
    "BaseDetails",
    "EmptyRoutePlanner",
    "FailingIPAddress",
    "GetTracks",
    "IPBlock",
    "NanoIPRouteDetails",
    "NanoIPRoutePlanner",
    "PlaylistInfo",
    "PluginData",
    "RotatingIPRouteDetails",
    "RotatingIPRoutePlanner",
    "RotatingNanoIPRouteDetails",
    "RotatingNanoIPRoutePlanner",
    "RoutePlannerStatus",
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


class IPBlock(TypedDict):
    type: Literal["Inet4Address", "Inet6Address"]
    size: str


class FailingIPAddress(TypedDict):
    address: str
    failingTimestamp: int
    failingTime: str


class BaseDetails(TypedDict):
    ipBlock: IPBlock
    failingAddresses: list[FailingIPAddress]


class RotatingIPRouteDetails(BaseDetails):
    rotateIndex: str
    ipIndex: str
    currentAddress: str


# Fields are named class
RotatingIPRoutePlanner = TypedDict(
    "RotatingIPRoutePlanner",
    {
        "class": Literal["RotatingIpRoutePlanner"],
        "details": RotatingIPRouteDetails,
    },
)


class NanoIPRouteDetails(BaseDetails):
    currentAddressIndex: str


NanoIPRoutePlanner = TypedDict(
    "NanoIPRoutePlanner",
    {
        "class": Literal["NanoIpRoutePlanner"],
        "details": NanoIPRouteDetails,
    },
)


class RotatingNanoIPRouteDetails(BaseDetails):
    blockIndex: str
    currentAddressIndex: str


RotatingNanoIPRoutePlanner = TypedDict(
    "RotatingNanoIPRoutePlanner",
    {
        "class": Literal["RotatingNanoIpRoutePlanner"],
        "details": RotatingNanoIPRouteDetails,
    },
)


class BalancingIPRouteDetails(BaseDetails):
    ...


BalancingIPRoutePlanner = TypedDict(
    "BalancingIPRoutePlanner",
    {
        "class": Literal["BalancingIpRoutePlanner"],
        "details": BalancingIPRouteDetails,
    },
)


EmptyRoutePlanner = TypedDict("EmptyRoutePlanner", {"class": None, "details": None})

RoutePlannerStatus = Union[
    RotatingIPRoutePlanner,
    NanoIPRoutePlanner,
    RotatingNanoIPRoutePlanner,
    BalancingIPRoutePlanner,
    EmptyRoutePlanner,
]
