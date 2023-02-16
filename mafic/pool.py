# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from logging import getLogger
from random import choice
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

from .errors import NoNodesAvailable
from .node import Node
from .strategy import Strategy, StrategyCallable, call_strategy
from .type_variables import ClientT
from .utils import classproperty

if TYPE_CHECKING:
    from typing import ClassVar

    import aiohttp

    from .region import Group, Region, VoiceRegion


T = TypeVar("T")
__all__ = ("NodePool",)

_log = getLogger(__name__)


StrategyList = Union[
    StrategyCallable[ClientT],
    Sequence[Strategy],
    Sequence[StrategyCallable[ClientT]],
    Sequence[Union[Strategy, StrategyCallable[ClientT]]],
]
"""A type hint for a list of strategies to select the best node.

This can either be:

- A single :data:`.StrategyCallable`.
- A sequence of :class:`.Strategy`\\s.
- A sequence of :data:`.StrategyCallable`\\s.
- A sequence of :class:`.Strategy`\\s and :data:`.StrategyCallable`\\s.
"""


class NodePool(Generic[ClientT]):
    """A class that manages nodes and chooses them based on strategies.

    Parameters
    ----------
    client:
        The client to use to connect to the nodes.
    default_strategies:
        The default strategies to use when selecting a node. Defaults to
        [:attr:`Strategy.SHARD`, :attr:`Strategy.LOCATION`, :attr:`Strategy.USAGE`].
    """

    __slots__ = ()

    # Generics as expected, do not work in class variables.
    # Don't fear, the public methods using this are typed well.
    _nodes: ClassVar[dict[str, Node[Any]]] = {}
    _node_regions: ClassVar[dict[VoiceRegion, set[Node[Any]]]] = {}
    _node_shards: ClassVar[dict[int, set[Node[Any]]]] = {}
    _client: ClientT | None = None

    def __init__(
        self,
        client: ClientT,
        default_strategies: StrategyList[ClientT] | None = None,
    ) -> None:
        NodePool._client = client

        NodePool._default_strategies = (
            [
                Strategy.SHARD,
                Strategy.LOCATION,
                Strategy.USAGE,
            ]
            if default_strategies is None
            else default_strategies
        )

    @classproperty
    def label_to_node(cls) -> dict[str, Node[ClientT]]:
        """A dictionary mapping node labels to nodes."""

        return cls._nodes

    @classproperty
    def nodes(cls) -> list[Node[ClientT]]:
        """A list of all nodes."""

        return list(cls._nodes.values())

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
        session: aiohttp.ClientSession | None = None,
        resume_key: str | None = None,
        regions: Sequence[Group | Region | VoiceRegion] | None = None,
        shard_ids: Sequence[int] | None = None,
    ) -> Node[ClientT]:
        """Create a node and connect it.

        The parameters here relate to :class:`Node`.

        Parameters
        ----------
        host:
            The host of the node to connect to.
        port:
            The port of the node to connect to.
        label:
            The label of the node used to identify it.
        password:
            The password of the node to authenticate.
        secure:
            Whether to use SSL (TLS) or not.
        heartbeat:
            The interval to send heartbeats to the node websocket connection.
        timeout:
            The timeout to use for the node websocket connection.
        session: :data:`~typing.Optional`\\ [:class:`aiohttp.ClientSession`]
            The session to use for the node websocket connection.
        resume_key:
            The key to use to resume the node websocket connection.
            This is used to resume a connection if the connection is lost.
            Defaults to using the `host`, `port` and `label`.
        regions:
            The regions this node is best to connect to.
            This is used to determine if this is the best node for a connection
            with :attr:`Strategy.LOCATION`.
        shard_ids:
            The shard IDs this node is best to connect to.
            This is used to determine if this is the best node for a connection
            with :attr:`Strategy.SHARD`.

        Returns
        -------
        :class:`Node`
            The created node.

        Raises
        ------
        RuntimeError
            If the node pool has not been initialized.
        """

        if self._client is None:
            raise RuntimeError("NodePool has not been initialized.")

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

        self._nodes[label] = node
        return node

    @classmethod
    def get_node(
        cls,
        *,
        guild_id: str | int,
        endpoint: str | None,
        strategies: StrategyList[ClientT] | None = None,
    ) -> Node[ClientT]:
        """Get a node based on the given strategies.

        Parameters
        ----------
        guild_id:
            The guild ID to get a node for.
        endpoint:
            The endpoint to get a node for.
        strategies:
            The strategies to use to get a node. If not provided, the default
            strategies will be used.

        Returns
        -------
        :class:`Node`
            The node to use.

        Raises
        ------
        RuntimeError
            If the node pool has not been initialized.
        """

        if cls._client is None:
            raise RuntimeError("NodePool has not been initialized.")

        actual_strategies: Sequence[StrategyCallable[ClientT] | Strategy]

        strategies = strategies or cls._default_strategies

        if callable(strategies):
            actual_strategies = [strategies]
        else:
            actual_strategies = strategies

        nodes = cls.nodes

        for strategy in actual_strategies:
            if isinstance(strategy, Strategy):
                strategy_callable = partial(call_strategy, strategy)
            else:
                strategy_callable = strategy

            nodes = strategy_callable(
                nodes, int(guild_id), cls._client.shard_count, endpoint
            )

            _log.debug(
                "Strategy %s returned nodes %s.",
                strategy.__name__ if callable(strategy) else strategy.name,
                ", ".join(n.label for n in nodes),
            )

            if len(nodes) == 1:
                return nodes[0]
            elif len(nodes) == 0:
                raise NoNodesAvailable

        return choice(nodes)

    @classmethod
    def get_random_node(cls) -> Node[ClientT]:
        """Get a random node.

        Returns
        -------
        :class:`Node`
            The random node.

        Raises
        ------
        ValueError
            If there are no nodes.
        """

        if node := choice(list(cls._nodes.values())):
            return node

        raise NoNodesAvailable
