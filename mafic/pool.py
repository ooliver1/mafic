# SPDX-License-Identifier: MIT

from __future__ import annotations

from logging import getLogger
from random import choice
from typing import TYPE_CHECKING, Generic, TypeVar

from .__libraries import Client
from .errors import NoNodesAvailable
from .node import Node
from .strategy import STRATEGIES, Strategy

if TYPE_CHECKING:
    from typing import ClassVar, Sequence, Union

    from aiohttp import ClientSession

    from .region import Group, Region, VoiceRegion
    from .strategy import StrategyCallable

    StrategyList = Union[
        Sequence[Strategy],
        StrategyCallable,
        Sequence[StrategyCallable],
        Sequence[Union[Strategy, StrategyCallable]],
    ]


ClientT = TypeVar("ClientT", bound=Client)
__all__ = ("NodePool",)


_log = getLogger(__name__)


class NodePool(Generic[ClientT]):
    __slots__ = ()
    _nodes: ClassVar[dict[str, Node]] = {}
    _node_regions: ClassVar[dict[Region, set[Node]]] = {}
    _node_shards: ClassVar[dict[int, set[Node]]] = {}
    _client: ClientT | None = None
    _default_strategies: StrategyList = [
        Strategy.SHARD,
        Strategy.LOCATION,
        Strategy.USAGE,
    ]

    def __init__(
        self,
        client: ClientT,
        default_strategies: StrategyList | None = None,
    ) -> None:
        NodePool._client = client

        if default_strategies is not None:
            NodePool._default_strategies = default_strategies

    @property
    def nodes(self) -> dict[str, Node]:
        return self._nodes

    async def create_node(
        self,
        *,
        host: str,
        port: int,
        label: str,
        password: str,
        secure: bool = False,
        heartbeat: int = 30,
        timeout: float = 10,
        session: ClientSession | None = None,
        resume_key: str | None = None,
        regions: Sequence[Group | Region | VoiceRegion] | None = None,
        shard_ids: Sequence[int] | None = None,
    ) -> Node:
        assert self._client is not None, "NodePool has not been initialized."

        node = Node(
            host=host,
            port=port,
            label=label,
            password=password,
            client=self._client,
            secure=secure,
            heartbeat=heartbeat,
            timeout=timeout,
            session=session,
            resume_key=resume_key,
            regions=regions,
            shard_ids=shard_ids,
        )

        self._nodes[label] = node

        # Add to dictionaries, creating a set or extending it if needed.
        if node.regions:
            for region in node.regions:
                self._node_regions[region] = {
                    node,
                    *self._node_regions.get(region, set()),
                }

        if node.shard_ids:
            for shard_id in node.shard_ids:
                self._node_shards[shard_id] = {
                    node,
                    *self._node_shards.get(shard_id, set()),
                }

        _log.info("Created node, connecting it...", extra={"label": label})
        await node.connect()

        return node

    @classmethod
    def get_node(
        cls,
        *,
        guild_id: str | int,
        endpoint: str | None,
        strategies: StrategyList | None = None,
    ) -> Node:
        assert cls._client is not None, "NodePool has not been initialized."

        actual_strategies: Sequence[StrategyCallable | Strategy]

        strategies = strategies or cls._default_strategies

        if callable(strategies):
            actual_strategies = [strategies]
        else:
            actual_strategies = strategies

        nodes = cls._nodes.values()

        for strategy in actual_strategies:
            if isinstance(strategy, Strategy):
                strategy = STRATEGIES[strategy]

            nodes = strategy(
                list(nodes), int(guild_id), cls._client.shard_count, endpoint
            )

            _log.debug(
                "Strategy %s returned nodes %s.",
                strategy.__name__,
                ", ".join(n.label for n in nodes),
            )

            if len(nodes) == 1:
                return nodes[0]
            elif len(nodes) == 0:
                raise NoNodesAvailable

        return choice(list(nodes))

    @classmethod
    def get_random_node(cls) -> Node:
        return choice(list(cls._nodes.values()))
