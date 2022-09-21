# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, Coroutine, Literal, TypedDict, TypeVar

__all__ = (
    "Coro",
    "ExceptionSeverity",
    "PayloadWithGuild",
)
T = TypeVar("T")

Coro = Coroutine[Any, Any, T]
ExceptionSeverity = Literal["COMMON", "SUSPICIOUS", "FAULT"]


class PayloadWithGuild(TypedDict):
    guildId: str


class FriendlyException(TypedDict):
    severity: ExceptionSeverity
    message: str


class FriendlyWithCause(FriendlyException):
    cause: str
