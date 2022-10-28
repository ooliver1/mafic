# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .typings import PluginData


@dataclass(repr=True)
class Plugin:
    name: str
    version: str

    @classmethod
    def from_data(cls, data: PluginData) -> Self:
        return cls(name=data["name"], version=data["version"])
