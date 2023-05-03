"""Contains a decorator to merge properties and classmethods."""
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Type, TypeVar, cast

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")
R = TypeVar("R")

__all__ = ("classproperty",)


class _ClassPropertyDescriptor(Generic[T, R]):
    """A descriptor that mimics the behavior of a property, but for classmethods."""

    def __init__(self, fget: classmethod[T, ..., R] | staticmethod[..., R]) -> None:
        self.fget = fget

    def __get__(self, instance: T, owner: type[T] | None = None) -> R:
        if owner is None:
            owner = cast(Type[T], type(instance))
        return self.fget.__get__(instance, owner)()


def classproperty(
    func: Callable[[T], R] | classmethod[T, ..., R] | staticmethod[..., R]
) -> _ClassPropertyDescriptor[T, R]:
    """Contains a decorator to mimic the behavior of a property, but for classmethods.

    Parameters
    ----------
    func:
        The function to decorate.
    """
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return _ClassPropertyDescriptor(func)
