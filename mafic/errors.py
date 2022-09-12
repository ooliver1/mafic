# SPDX-License-Identifier: MIT

from __future__ import annotations

__all__ = ("maficException", "LibraryCompatibilityError", "NoCompatibleLibraries")


class maficException(Exception):
    """The base exception for mafic errors."""


class LibraryCompatibilityError(maficException):
    """An error raised when no compatible libraries are found."""


class NoCompatibleLibraries(LibraryCompatibilityError):
    """An error raised when no compatible libraries are found."""

    def __init__(self):
        super().__init__(
            "No compatible libraries were found. Please install one of the following: "
            "nextcord, disnake, py-cord, discord.py or discord."
        )


class MultipleCompatibleLibraries(LibraryCompatibilityError):
    """An error raised when multiple compatible libraries are found."""

    def __init__(self, libraries: list[str]):
        super().__init__(
            f"Multiple compatible libraries were found: {', '.join(libraries)}. "
            "Please remove all but one of the libraries."
        )
