# SPDX-License-Identifier: MIT
# ruff: noqa: UP013
# `class` in `TypedDict` does not work as that is a reserved keyword

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Optional, TypedDict, Union

if TYPE_CHECKING:
    from typing_extensions import NotRequired

    from .common import PlaylistInfo, TrackWithInfo
    from .misc import LavalinkException


__all__ = (
    "BalancingIPRouteDetails",
    "BalancingIPRoutePlanner",
    "BalancingIPRoutePlanner",
    "BaseDetails",
    "ConfigureResumingResponse",
    "EmptyRoutePlanner",
    "EmptyRoutePlanner",
    "Error",
    "FailingIPAddress",
    "GenericTracks",
    "Git",
    "Git",
    "IPBlock",
    "Info",
    "Info",
    "NanoIPRouteDetails",
    "NanoIPRoutePlanner",
    "NanoIPRoutePlanner",
    "NoMatches",
    "PlaylistTracks",
    "PluginData",
    "RotatingIPRouteDetails",
    "RotatingIPRoutePlanner",
    "RotatingIPRoutePlanner",
    "RotatingNanoIPRouteDetails",
    "RotatingNanoIPRoutePlanner",
    "RotatingNanoIPRoutePlanner",
    "RoutePlannerStatus",
    "RoutePlannerStatus",
    "TrackLoadingResult",
    "TracksFailed",
    "Version",
)


# V3


class PlaylistTracks(TypedDict):
    loadType: Literal["PLAYLIST_LOADED"]
    playlistInfo: PlaylistInfo
    tracks: list[TrackWithInfo]


class GenericTracks(TypedDict):
    loadType: Literal["TRACK_LOADED", "SEARCH_RESULT"]
    tracks: list[TrackWithInfo]


class TracksFailed(TypedDict):
    loadType: Literal["LOAD_FAILED"]
    exception: LavalinkException


class NoMatches(TypedDict):
    loadType: Literal["NO_MATCHES"]


# V4


class TrackLoadedV4(TypedDict):
    loadType: Literal["track"]
    data: TrackWithInfo


class PlaylistLoadedV4(TypedDict):
    loadType: Literal["playlist"]
    data: PlaylistDataV4


class PlaylistDataV4(TypedDict):
    info: PlaylistInfo
    pluginInfo: dict[str, Any]
    tracks: list[TrackWithInfo]


class SearchResultV4(TypedDict):
    loadType: Literal["search"]
    data: list[TrackWithInfo]


class SearchEmptyV4(TypedDict):
    loadType: Literal["empty"]


class LoadErrorV4(TypedDict):
    loadType: Literal["error"]
    data: LavalinkException


TrackLoadingResult = Union[
    PlaylistTracks,
    GenericTracks,
    TracksFailed,
    NoMatches,
    TrackLoadedV4,
    PlaylistLoadedV4,
    SearchResultV4,
    SearchEmptyV4,
    LoadErrorV4,
]


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
        "class": Optional[Literal["NanoIpRoutePlanner"]],
        "details": Optional[NanoIPRouteDetails],
    },
)


class RotatingNanoIPRouteDetails(BaseDetails):
    blockIndex: str
    currentAddressIndex: str


RotatingNanoIPRoutePlanner = TypedDict(
    "RotatingNanoIPRoutePlanner",
    {
        "class": Optional[Literal["RotatingNanoIpRoutePlanner"]],
        "details": Optional[RotatingNanoIPRouteDetails],
    },
)


class BalancingIPRouteDetails(BaseDetails): ...


BalancingIPRoutePlanner = TypedDict(
    "BalancingIPRoutePlanner",
    {
        "class": Optional[Literal["BalancingIpRoutePlanner"]],
        "details": Optional[BalancingIPRouteDetails],
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


class ConfigureResumingResponse(TypedDict):
    resumingKey: str | None
    timeout: int


class Version(TypedDict):
    semver: str
    major: int
    minor: int
    patch: int
    preRelease: str | None


class Git(TypedDict):
    branch: str
    commit: str
    commitTime: int


class Info(TypedDict):
    version: Version
    buildTime: int
    git: Git
    jvm: str
    lavaplayer: str
    sourceManagers: list[str]
    filters: list[str]
    plugins: list[PluginData]


class Error(TypedDict):
    timestamp: int
    status: int
    error: str
    trace: NotRequired[str]
    message: str
    path: str
