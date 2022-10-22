# SPDX-License-Identifier: MIT

from __future__ import annotations

from logging import getLogger
from random import choice
from typing import TYPE_CHECKING, Generic, TypeVar

from .__libraries import Client
from .node import Node

if TYPE_CHECKING:
    from typing import ClassVar

    from aiohttp import ClientSession


ClientT = TypeVar("ClientT", bound=Client)


_log = getLogger(__name__)


class NodePool(Generic[ClientT]):
    __slots__ = ()
    _nodes: ClassVar[dict[str, Node]] = {}

    @property
    def nodes(self) -> dict[str, Node]:
        return self._nodes

    @classmethod
    async def create_node(
        cls,
        *,
        host: str,
        port: int,
        label: str,
        password: str,
        client: ClientT,
        secure: bool = False,
        heartbeat: int = 30,
        timeout: float = 10,
        session: ClientSession | None = None,
        resume_key: str | None = None,
    ) -> Node:
        node = Node(
            host=host,
            port=port,
            label=label,
            password=password,
            client=client,
            secure=secure,
            heartbeat=heartbeat,
            timeout=timeout,
            session=session,
            resume_key=resume_key,
        )

        # TODO: assign dicts for regions and such
        cls._nodes[label] = node

        _log.info("Created node, connecting it...", extra={"label": label})
        await node.connect()

        return node

    @classmethod
    def get_node(cls, *, guild_id: str | int, endpoint: str | None) -> Node:
        # TODO: use guild id, endpoint and other stuff like usage to determine node

        return choice(list(cls._nodes.values()))

    @classmethod
    def get_random_node(cls) -> Node:
        return choice(list(cls._nodes.values()))
