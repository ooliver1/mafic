# SPDX-License-Identifier: MIT


__all__ = ("UnsupportedVersionWarning", "UnknownVersionWarning")


class UnsupportedVersionWarning(UserWarning):
    """Represents a warning for an unsupported version of Lavalink."""

    message: str = (
        "The version of Lavalink you are using is not supported by Mafic. "
        "It should still work but not all features are supported."
    )


class UnknownVersionWarning(UserWarning):
    """Represents a warning for an unknown version of Lavalink."""

    message: str = (
        "The version of Lavalink you are using is unknown to Mafic. "
        "It should still work but not all features are supported."
    )
