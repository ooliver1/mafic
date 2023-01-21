# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .typings import PluginData


__all__ = ("Plugin",)


@dataclass(repr=True)
class Plugin:
    """Represents a plugin.

    Attributes
    ----------
    name:
        The name of the plugin.
    version:
        The version of the plugin.
    """

    name: str
    version: str

    @classmethod
    def from_data(cls, data: PluginData) -> Self:
        """Create a plugin from raw Lavalink data.

        Parameters
        ----------
        data:
            The plugin data.

        Returns
        -------
        Plugin:
            The plugin.
        """

        return cls(name=data["name"], version=data["version"])
