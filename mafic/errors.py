# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .typings import ExceptionSeverity, LavalinkException

__all__ = (
    "HTTPBadRequest",
    "HTTPException",
    "HTTPNotFound",
    "HTTPUnauthorized",
    "LibraryCompatibilityError",
    "MaficException",
    "MultipleCompatibleLibraries",
    "NoCompatibleLibraries",
    "NoNodesAvailable",
    "NodeAlreadyConnected",
    "PlayerException",
    "PlayerNotConnected",
    "TrackLoadException",
)


class MaficException(Exception):
    """The base exception class for custom exceptions raised by Mafic."""


class LibraryCompatibilityError(MaficException):
    """An issue occured when trying to find a compatible library."""


class NoCompatibleLibraries(LibraryCompatibilityError):
    """No compatible library was found."""

    def __init__(self) -> None:
        super().__init__(
            "No compatible libraries were found. Please install one of the following: "
            "nextcord, disnake, py-cord, discord.py or discord."
        )


class MultipleCompatibleLibraries(LibraryCompatibilityError):
    """Multiple compatible libraries were found.

    Mafic makes no attempt to assume which library you are using.
    """

    def __init__(self, libraries: list[str]) -> None:
        super().__init__(
            f"Multiple compatible libraries were found: {', '.join(libraries)}. "
            "Please remove all but one of the libraries."
        )


class PlayerException(MaficException):
    """An issue occured when trying to play a track."""


class TrackLoadException(PlayerException):
    """This is raised when a track could not be loaded.

    Attributes
    ----------
    message: :class:`str`
        The message returned by the node.
    severity: :data:`~typing.Literal`\\[``"COMMON"``, ``"SUSPICIOUS"``, ``"FATAL"``]
        The severity of the error.
    """

    def __init__(
        self, *, message: str, severity: ExceptionSeverity, cause: str
    ) -> None:
        super().__init__(f"The track could not be loaded: {message} ({severity} error)")

        self.message: str = message
        self.severity: ExceptionSeverity = severity

    @classmethod
    def from_data(cls, data: LavalinkException) -> Self:
        """Construct a new TrackLoadException from raw Lavalink data.

        Parameters
        ----------
        data:
            The raw data from Lavalink.

        Returns
        -------
        TrackLoadException
            The constructed exception.
        """

        return cls(
            message=data["message"], severity=data["severity"], cause=data["cause"]
        )


class PlayerNotConnected(PlayerException):
    """This is raised when a player is not connected to a voice channel."""

    def __init__(self) -> None:
        super().__init__("The player is not connected to a voice channel.")


class NodeAlreadyConnected(MaficException):
    """This is raised when a node is already connected to Mafic."""

    def __init__(self) -> None:
        super().__init__("The node is already connected to Mafic.")


class NoNodesAvailable(MaficException):
    """This is raised when no nodes are available to handle a player."""

    def __init__(self) -> None:
        super().__init__("No nodes are available to handle this player.")


class HTTPException(MaficException):
    """An issue occured when trying to make a request to the Lavalink REST API."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(f"An HTTP error occured: {message} ({status})")

        self.status: int = status
        self.message: str = message


class HTTPBadRequest(HTTPException):
    """This is raised when a bad request is made to the Lavalink REST API."""

    def __init__(self, message: str) -> None:
        super().__init__(400, message)


class HTTPUnauthorized(HTTPException):
    """This is raised when an unauthorized request is made to the Lavalink REST API."""

    def __init__(self, message: str) -> None:
        super().__init__(401, message)


class HTTPNotFound(HTTPException):
    """This is raised when a request is made to a non-existent endpoint."""

    def __init__(self, message: str) -> None:
        super().__init__(404, message)
