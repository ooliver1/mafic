# SPDX-License-Identifier: MIT

from __future__ import annotations

from random import choice
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import ClassVar, Optional

    from aiohttp import ClientSession

    from .__libraries import Client
    from .node import Node


class NodePool:
    _nodes: ClassVar[dict[str, Node]] = {}

    @property
    def nodes(self) -> dict[str, Node]:
        return self._nodes

    @classmethod
    def create_node(
        cls,
        *,
        host: str,
        port: int,
        label: str,
        password: str,
        client: Client,
        secure: bool = False,
        heartbeat: int = 30,
        timeout: float = 10,
        session: ClientSession | None = None,
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
        )

        # TODO: assign dicts for regions and such
        cls._nodes[label] = node

        return node

    @classmethod
    def get_node(cls, *, guild_id: str | int, endpoint: Optional[str]) -> Node:
        # TODO: use guild id, endpoint and other stuff like usage to determine node

        return choice(list(cls._nodes.values()))