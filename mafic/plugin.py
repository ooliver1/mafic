# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass


@dataclass(repr=True)
class Plugin:
    name: str
    version: str
