# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from enum import Enum, auto
from logging import getLogger
from random import choice
from typing import Callable, List, Union

from .node import Node
from .region import VOICE_TO_REGION

StrategyCallable = Callable[
    [List[Node], int, Union[int, None], Union[str, None]], List[Node]
]

_log = getLogger(__name__)
__all__ = ("Strategy", "STRATEGIES")


class Strategy(Enum):
    SHARD = auto()
    LOCATION = auto()
    USAGE = auto()
    RANDOM = auto()


def shard_strategy(
    nodes: list[Node], guild_id: int, shard_count: int | None, _: str | None
) -> list[Node]:
    if shard_count is None:
        shard_count = 1

    shard_id = (guild_id >> 22) % shard_count

    return list(
        filter(lambda node: node.shard_ids is None or shard_id in node.shard_ids, nodes)
    )


_REGION_REGEX = re.compile(r"(?:vip-)?(?P<region>[a-z-]{1,15})\d{1,5}\.discord\.media")


def location_strategy(
    nodes: list[Node], _: int, __: int | None, endpoint: str | None
) -> list[Node]:
    if endpoint is None:
        return nodes

    match = _REGION_REGEX.match(endpoint)

    if not match:
        _log.error("Failed to find the region in an endpoint, defaulting to all nodes.")
        return nodes

    region = VOICE_TO_REGION.get(match.group("region"))

    if not region:
        _log.error(
            "Failed to match endpoint %s (match: %s) to a region, "
            "defaulting to all nodes.",
            endpoint,
            match.group("region"),
        )
        return nodes

    regional_nodes = list(
        filter(lambda node: node.regions is not None and region in node.regions, nodes)
    )

    if not regional_nodes:
        _log.error("No nodes found for the region, defaulting to all nodes.")
        return nodes

    return regional_nodes


def usage_strategy(
    nodes: list[Node], _: int, __: int | None, ___: str | None
) -> list[Node]:
    # max() would be nice, however if all nodes have no stats, it returns the first.

    lowest = None

    for node in nodes:
        weight = node.weight

        if lowest is None or weight < lowest:
            lowest = weight

    if lowest is None:
        return nodes

    return list(filter(lambda node: node.weight == lowest, nodes))


STRATEGIES: dict[Strategy, StrategyCallable] = {
    Strategy.SHARD: shard_strategy,
    Strategy.LOCATION: location_strategy,
    Strategy.USAGE: usage_strategy,
    # Random should return one.
    # Since it is usually to filter out lists at the end of a chain.
    Strategy.RANDOM: lambda nodes, _, __, ___: [choice(nodes)],
}
