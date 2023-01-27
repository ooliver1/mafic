# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Callable, Generic, TypeVar

T = TypeVar("T")

__all__ = ("classproperty",)


class _ClassPropertyDescriptor(Generic[T]):
    """A descriptor that mimics the behavior of a property, but for classmethods."""

    def __init__(self, fget: classmethod[T] | staticmethod[T], fset: None = None):
        self.fget = fget

    def __get__(self, instance: object, owner: type | None = None) -> T:
        if owner is None:
            owner = type(instance)
        return self.fget.__get__(instance, owner)()


def classproperty(
    func: Callable[..., T] | classmethod[T] | staticmethod[T]
) -> _ClassPropertyDescriptor[T]:
    """A decorator that mimics the behavior of a property, but for classmethods.

    Parameters
    ----------
    func:
        The function to decorate.
    """

    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return _ClassPropertyDescriptor(func)
