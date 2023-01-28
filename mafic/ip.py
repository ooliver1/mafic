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
    """The type of IP route planner.

    More info about what planner to use can be found in the lavalink `docs`_.

    .. _docs: https://github.com/freyacodes/Lavalink/blob/master/ROUTEPLANNERS.md
    """

    ROTATING_IP = "RotatingIPRoutePlanner"
    """IP address used is switched on ban.

    This represents ``RotateOnBan`` in config."""

    NANO_IP = "NanoIPRoutePlanner"
    """IP address used is switched on clock update.

    This reprersents ``NanoSwitch`` in config.
    """

    ROTATING_NANO_IP = "RotatingNanoIPRoutePlanner"
    """IP address used is switched on clock update, rotates to a different block on ban.

    This represents ``RotatingNanoSwitch`` in config.
    """

    BALANCING_IP = "BalancingIPRoutePlanner"
    """IP address used is selected randomly.

    This represents ``LoadBalance`` in config.
    """


class IPBlockType(Enum):
    """The type of IP block."""

    V4 = "Inet4Address"
    """Represents an `IPv4`_ address.

    .. _IPv4: https://en.wikipedia.org/wiki/Internet_Protocol_version_4
    """

    V6 = "Inet6Address"
    """Represents an `IPv6`_ address.

    .. _IPv6: https://en.wikipedia.org/wiki/IPv6
    """


class IPBlock:
    """Represents an IP block.

    Attributes
    ----------
    size: :class:`int`
        The size of the block - the number of addresses in the block.
    type: :class:`IPBlockType`
        The type of the block.
    """

    __slots__ = ("size", "type")

    def __init__(self, data: IPBlockPayload) -> None:
        self.size: int = int(data["size"])
        self.type: IPBlockType = IPBlockType(data["type"])


class FailingAddress:
    """Represents a failing IP address.

    Attributes
    ----------
    address: :class:`str`
        The IP address.
    time: :class:`datetime.datetime`
        The time the address was added to the list of failing addresses.
    """

    __slots__ = ("address", "time")

    def __init__(self, data: FailingIPAddress) -> None:
        self.address: str = data["address"]
        self.time: datetime = datetime.fromtimestamp(data["failingTimestamp"])


class BaseIPRoutePlannerStatus(ABC):
    """An :term:`abstract base class` representing the status of an IP route planner.

    Attributes
    ----------
    failing_addresses: :class:`list`\\[:class:`FailingAddress`]
        The list of failing addresses.
    ip_block: :class:`IPBlock`
        The IP block.
    type: :class:`IPRoutePlannerType`
        The type of route planner.
    """

    __slots__ = ("failing_addresses", "ip_block")

    type: IPRoutePlannerType

    def __init__(self, data: BaseDetails) -> None:
        self.ip_block: IPBlock = IPBlock(data["ipBlock"])
        self.failing_addresses: list[FailingAddress] = [
            FailingAddress(addr) for addr in data["failingAddresses"]
        ]


class RotatingIPRoutePlannerStatus(BaseIPRoutePlannerStatus):
    """Represents the status of a rotating IP route planner.

    Attributes
    ----------
    type: :data:`~typing.Literal`\\[:attr:`IPRoutePlannerType.ROTATING_IP`]
        The type of route planner. This will always be
        :attr:`IPRoutePlannerType.ROTATING_IP`.
    current_address: :class:`str`
        The current IP address.
    ip_index: :class:`int`
        The offset of the current IP address.
    rotate_index: :class:`int`
        The number of rotations.
    """

    __slots__ = ("current_address", "ip_index", "rotate_index")

    type = IPRoutePlannerType.ROTATING_IP

    def __init__(self, data: RotatingIPRouteDetails) -> None:
        super().__init__(data)
        self.rotate_index: int = int(data["rotateIndex"])
        self.ip_index: int = int(data["ipIndex"])
        self.current_address: str = data["currentAddress"]


class NanoIPRoutePlannerStatus(BaseIPRoutePlannerStatus):
    """Represents the status of a nano IP route planner.

    Attributes
    ----------
    type: :data:`~typing.Literal`\\[:attr:`IPRoutePlannerType.NANO_IP`]
        The type of route planner. This will always be
        :attr:`IPRoutePlannerType.NANO_IP`.
    current_address_index: :class:`int`
        The index of the current address.
    """

    __slots__ = ("current_address_index",)

    type = IPRoutePlannerType.NANO_IP

    def __init__(self, data: NanoIPRouteDetails) -> None:
        super().__init__(data)
        self.current_address_index: int = int(data["currentAddressIndex"])


class RotatingNanoIPRoutePlannerStatus(BaseIPRoutePlannerStatus):
    """Represents the status of a rotating nano IP route planner.

    Attributes
    ----------
    type: :data:`~typing.Literal`\\[:attr:`IPRoutePlannerType.ROTATING_NANO_IP`]
        The type of route planner. This will always be
        :attr:`IPRoutePlannerType.ROTATING_NANO_IP`.
    block_index: :class:`int`
        The index of the current block.
    current_address_index: :class:`int`
        The index of the current address.
    """

    __slots__ = ("block_index", "current_address_index")

    type = IPRoutePlannerType.ROTATING_NANO_IP

    def __init__(self, data: RotatingNanoIPRouteDetails) -> None:
        super().__init__(data)
        self.block_index: int = int(data["blockIndex"])
        self.current_address_index: int = int(data["currentAddressIndex"])


class BalancingIPRoutePlannerStatus(BaseIPRoutePlannerStatus):
    """Represents the status of a balancing IP route planner.

    Attributes
    ----------
    type: :data:`~typing.Literal`\\[:attr:`IPRoutePlannerType.BALANCING_IP`]
        The type of route planner. This will always be
        :attr:`IPRoutePlannerType.BALANCING_IP`.
    current_address_index: :class:`int`
        The index of the current address.
    ip_index: :class:`int`
        The offset of the current IP block in the IP block list.
    rotate_index: :class:`int`
        The number of rotations.
    """

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
"""Represents the status of an IP route planner. This can be one of the following:

- :class:`RotatingIPRoutePlannerStatus`
- :class:`NanoIPRoutePlannerStatus`
- :class:`RotatingNanoIPRoutePlannerStatus`
- :class:`BalancingIPRoutePlannerStatus`

To determine the type of route planner, check the :attr:`BaseIPRoutePlannerStatus.type`
attribute.
"""
