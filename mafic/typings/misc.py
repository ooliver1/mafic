# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Coroutine
from typing import Any, Literal, TypedDict, TypeVar

__all__ = (
    "Coro",
    "LavalinkException",
    "ExceptionSeverity",
    "PayloadWithGuild",
)
T = TypeVar("T")

Coro = Coroutine[Any, Any, T]
ExceptionSeverity = Literal[
    # V3
    "COMMON",
    "SUSPICIOUS",
    "FAULT",
    # V4
    "common",
    "suspicious",
    "fault",
]


class LavalinkException(TypedDict):
    severity: ExceptionSeverity
    message: str
    cause: str


class PayloadWithGuild(TypedDict):
    guildId: str
