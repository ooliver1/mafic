# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, Coroutine, TypeVar

__all__ = ("Coro",)
T = TypeVar("T")

Coro = Coroutine[Any, Any, T]
