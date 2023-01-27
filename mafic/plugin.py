# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .typings import PluginData


__all__ = ("Plugin",)


class Plugin:
    """Represents a plugin.

    Parameters
    ----------
    data:
        The raw data to use to create the plugin.

    Attributes
    ----------
    name: :class:`str`
        The name of the plugin.
    version: :class:`str`
        The version of the plugin.
    """

    __slots__ = ("name", "version")

    def __init__(self, data: PluginData) -> None:
        self.name: str = data["name"]
        self.version: str = data["version"]
