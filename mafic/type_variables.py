# SPDX-License-Identifier: MIT
# This was originally made to avoid the import cycle of
# mafic.pool -> mafic.node -> mafic.pool
# pool wants Node, node wants ClientT

from typing import TypeVar

from .__libraries import Client

__all__ = ("ClientT",)
ClientT = TypeVar("ClientT", bound=Client)
"""A type hint for a client that is (optionally a subclass of) your library's client.

- :class:`dpy:discord.Client` for discord.py.
- :class:`nextcord.Client` for nextcord.
- :class:`disnake.Client` for disnake.
- :class:`pyc:discord.Client` for py-cord.

This is used in :class:`.NodePool` to type hint the client used to create
:class:`Node`\\s and :class:`Player`\\s. :attr:`Node.client` will be of this type.
"""
