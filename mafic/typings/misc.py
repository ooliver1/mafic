# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, Coroutine, TypedDict, TypeVar

__all__ = (
    "Coro",
    "PayloadWithGuild",
)
T = TypeVar("T")

Coro = Coroutine[Any, Any, T]


class PayloadWithGuild(TypedDict):
    guildId: str
