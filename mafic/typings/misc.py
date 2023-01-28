# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, Coroutine, Literal, TypedDict, TypeVar

__all__ = (
    "Coro",
    "LavalinkException",
    "ExceptionSeverity",
    "PayloadWithGuild",
)
T = TypeVar("T")

Coro = Coroutine[Any, Any, T]
ExceptionSeverity = Literal["COMMON", "SUSPICIOUS", "FAULT"]


class LavalinkException(TypedDict):
    severity: ExceptionSeverity
    message: str
    cause: str


class PayloadWithGuild(TypedDict):
    guildId: str
