# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from enum import Enum, auto
from logging import getLogger
from random import choice
from typing import Callable, List, Optional

from .node import Node
from .type_variables import ClientT

StrategyCallable = Callable[
    [List[Node[ClientT]], int, Optional[int], Optional[str]], List[Node[ClientT]]
]
"""Represents a strategy callable.

This accepts ``nodes``, ``guild_id``, ``shard_count`` and ``endpoint`` and returns
a list of nodes.
"""

_log = getLogger(__name__)
__all__ = ("Strategy", "call_strategy")


class Strategy(Enum):
    """Represents a strategy for selecting a node."""

    LOCATION = auto()
    """Selects a node based on the region the guild is in."""

    RANDOM = auto()
    """Selects a random node."""

    SHARD = auto()
    """Selects a node based on the shard ID of the guild."""

    USAGE = auto()
    """Selects a node based on the least used node."""


def shard_strategy(
    nodes: list[Node[ClientT]], guild_id: int, shard_count: int | None, _: str | None
) -> list[Node[ClientT]]:
    """Selects a node based on the shard ID of the guild.

    Parameters
    ----------
    nodes:
        The nodes to select from.
    guild_id:
        The ID of the guild to select a node for.
    shard_count:
        The number of shards the bot is using.
    _:
        Unused parameter.
    """

    if shard_count is None:
        shard_count = 1

    shard_id = (guild_id >> 22) % shard_count

    return list(
        filter(lambda node: node.shard_ids is None or shard_id in node.shard_ids, nodes)
    )


_REGION_REGEX = re.compile(r"(?:vip-)?(?P<region>[a-z-]{1,15})\d{1,5}\.discord\.media")


def location_strategy(
    nodes: list[Node[ClientT]], _: int, __: int | None, endpoint: str | None
) -> list[Node[ClientT]]:
    """Selects a node based on the region the guild is in.

    Parameters
    ----------
    nodes:
        The nodes to select from.
    _:
        Unused parameter.
    __:
        Unused parameter.
    endpoint:
        The endpoint of the guild to select a node for.
    """

    if endpoint is None:
        return nodes

    match = _REGION_REGEX.match(endpoint)

    if not match:
        _log.error("Failed to find the region in an endpoint, defaulting to all nodes.")
        return nodes

    voice_region = match.group("region")

    if not voice_region:
        _log.error(
            "Failed to match endpoint %s (match: %s) to a region, "
            "defaulting to all nodes.",
            endpoint,
            match.group("region"),
        )
        return nodes

    regional_nodes = list(
        filter(
            lambda node: node.regions is not None and voice_region in node.regions,
            nodes,
        )
    )

    if not regional_nodes:
        _log.error("No nodes found for the region, defaulting to all nodes.")
        return nodes

    return regional_nodes


def usage_strategy(
    nodes: list[Node[ClientT]], _: int, __: int | None, ___: str | None
) -> list[Node[ClientT]]:
    """Selects a node based on the least used node.

    This is calculated using :attr:`Node.weight`.

    Parameters
    ----------
    nodes:
        The nodes to select from.
    _:
        Unused parameter.
    __:
        Unused parameter.
    ___:
        Unused parameter.
    """

    # max() would be nice, however if all nodes have no stats, it returns the first.

    lowest = None

    for node in nodes:
        weight = node.weight

        if lowest is None or weight < lowest:
            lowest = weight

    if lowest is None:
        return nodes

    return list(filter(lambda node: node.weight == lowest, nodes))


def random_strategy(
    nodes: list[Node[ClientT]], _: int, __: int | None, ___: str | None
) -> list[Node[ClientT]]:
    """Selects a random node.

    Parameters
    ----------
    nodes:
        The nodes to select from.
    _:
        Unused parameter.
    __:
        Unused parameter.
    ___:
        Unused parameter.
    """

    return [choice(nodes)]


# Used for ClientT preservation.
def call_strategy(
    strategy: Strategy,
    nodes: list[Node[ClientT]],
    guild_id: int,
    shard_count: int | None,
    endpoint: str | None,
) -> list[Node[ClientT]]:
    """Calls a strategy.

    Parameters
    ----------
    strategy:
        The strategy to call.
    nodes:
        The nodes to select from.
    guild_id:
        The ID of the guild to select a node for.
    shard_count:
        The number of shards the bot is using.
    endpoint:
        The endpoint of the voice client to select a node for.
    """

    if strategy is Strategy.LOCATION:
        return location_strategy(nodes, guild_id, shard_count, endpoint)
    elif strategy is Strategy.RANDOM:
        return random_strategy(nodes, guild_id, shard_count, endpoint)
    elif strategy is Strategy.SHARD:
        return shard_strategy(nodes, guild_id, shard_count, endpoint)
    elif strategy is Strategy.USAGE:
        return usage_strategy(nodes, guild_id, shard_count, endpoint)
    else:
        raise ValueError(f"Unknown strategy {strategy}")
