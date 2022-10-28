# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .typings import FriendlyException

__all__ = (
    "LibraryCompatibilityError",
    "MaficException",
    "MultipleCompatibleLibraries",
    "NoCompatibleLibraries",
    "PlayerNotConnected",
    "TrackLoadException",
)


class MaficException(Exception):
    ...


class LibraryCompatibilityError(MaficException):
    ...


class NoCompatibleLibraries(LibraryCompatibilityError):
    def __init__(self) -> None:
        super().__init__(
            "No compatible libraries were found. Please install one of the following: "
            "nextcord, disnake, py-cord, discord.py or discord."
        )


class MultipleCompatibleLibraries(LibraryCompatibilityError):
    def __init__(self, libraries: list[str]) -> None:
        super().__init__(
            f"Multiple compatible libraries were found: {', '.join(libraries)}. "
            "Please remove all but one of the libraries."
        )


class TrackLoadException(MaficException):
    def __init__(self, *, message: str, severity: str) -> None:
        super().__init__(f"The track could not be loaded: {message} ({severity} error)")

    @classmethod
    def from_data(cls, data: FriendlyException) -> Self:
        return cls(message=data["message"], severity=data["severity"])


class PlayerNotConnected(MaficException):
    def __init__(self) -> None:
        super().__init__("The player is not connected to a voice channel.")
