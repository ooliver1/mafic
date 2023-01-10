# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, Union

if TYPE_CHECKING:
    from typing_extensions import NotRequired

    from .misc import FriendlyException


__all__ = (
    "GenericTracks",
    "NoMatches",
    "PlaylistInfo",
    "PlaylistTracks",
    "TrackInfo",
    "TrackWithInfo",
    "TracksFailed",
    "PluginData",
    "IPBlock",
    "FailingIPAddress",
    "BaseDetails",
    "RotatingIPRouteDetails",
    "NanoIPRouteDetails",
    "RotatingNanoIPRouteDetails",
    "BalancingIPRouteDetails",
    "ConfigureResumingResponse",
    "Version",
    "Git",
    "Info",
    "VoiceState",
    "GetTracks",
    "RotatingIPRoutePlanner",
    "NanoIPRoutePlanner",
    "RotatingNanoIPRoutePlanner",
    "BalancingIPRoutePlanner",
    "EmptyRoutePlanner",
    "RoutePlannerStatus",
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
    encoded: str
    info: TrackInfo


class PlaylistTracks(TypedDict):
    loadType: Literal["PLAYLIST_LOADED"]
    playlistInfo: PlaylistInfo


class GenericTracks(TypedDict):
    loadType: Literal["TRACK_LOADED", "SEARCH_RESULT"]
    tracks: list[TrackWithInfo]


class TracksFailed(TypedDict):
    loadType: Literal["LOAD_FAILED"]
    exception: NotRequired[FriendlyException]


class NoMatches(TypedDict):
    loadType: Literal["NO_MATCHES"]


GetTracks = Union[PlaylistTracks, GenericTracks, TracksFailed, NoMatches]


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


class VoiceState(TypedDict):
    token: str
    endpoint: str
    sessionId: str
    connected: bool
    ping: int
