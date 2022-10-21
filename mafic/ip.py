# SPDX-License-Identifier: MIT

from __future__ import annotations

from abc import ABC
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .typings import (
        BalancingIPRouteDetails,
        BaseDetails,
        FailingIPAddress,
        IPBlock as IPBlockPayload,
        NanoIPRouteDetails,
        RotatingIPRouteDetails,
        RotatingNanoIPRouteDetails,
    )

__all__ = (
    "IPRoutePlannerType",
    "IPBlockType",
    "IPBlock",
    "FailingAddress",
    "BaseIPRoutePlannerStatus",
    "BalancingIPRoutePlannerStatus",
    "NanoIPRoutePlannerStatus",
    "RotatingIPRoutePlannerStatus",
    "RotatingNanoIPRoutePlannerStatus",
    "RoutePlannerStatus",
)


class IPRoutePlannerType(Enum):
    ROTATING_IP = "RotatingIPRoutePlanner"
    NANO_IP = "NanoIPRoutePlanner"
    ROTATING_NANO_IP = "RotatingNanoIPRoutePlanner"
    BALANCING_IP = "BalancingIPRoutePlanner"


class IPBlockType(Enum):
    V4 = "Inet4Address"
    V6 = "Inet6Address"


class IPBlock:
    __slots__ = ("size", "type")

    def __init__(self, data: IPBlockPayload) -> None:
        self.size: int = int(data["size"])
        self.type: IPBlockType = IPBlockType(data["type"])


class FailingAddress:
    __slots__ = ("address", "time")

    def __init__(self, data: FailingIPAddress) -> None:
        self.address: str = data["address"]
        self.time: datetime = datetime.fromtimestamp(data["failingTimestamp"])


class BaseIPRoutePlannerStatus(ABC):
    __slots__ = ("failing_addresses", "ip_block")

    type: IPRoutePlannerType

    def __init__(self, data: BaseDetails) -> None:
        self.ip_block = IPBlock(data["ipBlock"])
        self.failing_addresses = [
            FailingAddress(addr) for addr in data["failingAddresses"]
        ]


class RotatingIPRoutePlannerStatus(BaseIPRoutePlannerStatus):
    __slots__ = ("current_address", "ip_index", "rotate_index")

    type = IPRoutePlannerType.ROTATING_IP

    def __init__(self, data: RotatingIPRouteDetails) -> None:
        super().__init__(data)
        self.rotate_index: int = int(data["rotateIndex"])
        self.ip_index: int = int(data["ipIndex"])
        self.current_address: str = data["currentAddress"]


class NanoIPRoutePlannerStatus(BaseIPRoutePlannerStatus):
    __slots__ = ("current_address_index",)

    type = IPRoutePlannerType.NANO_IP

    def __init__(self, data: NanoIPRouteDetails) -> None:
        super().__init__(data)
        self.current_address_index: int = int(data["currentAddressIndex"])


class RotatingNanoIPRoutePlannerStatus(BaseIPRoutePlannerStatus):
    __slots__ = ("block_index", "current_address_index")

    type = IPRoutePlannerType.ROTATING_NANO_IP

    def __init__(self, data: RotatingNanoIPRouteDetails) -> None:
        super().__init__(data)
        self.block_index: int = int(data["blockIndex"])
        self.current_address_index: int = int(data["currentAddressIndex"])


class BalancingIPRoutePlannerStatus(BaseIPRoutePlannerStatus):
    __slots__ = ("current_address_index", "ip_index", "rotate_index")

    type = IPRoutePlannerType.BALANCING_IP

    def __init__(self, data: BalancingIPRouteDetails) -> None:
        super().__init__(data)


RoutePlannerStatus = Union[
    RotatingIPRoutePlannerStatus,
    NanoIPRoutePlannerStatus,
    RotatingNanoIPRoutePlannerStatus,
    BalancingIPRoutePlannerStatus,
]
