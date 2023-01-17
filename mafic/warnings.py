# SPDX-License-Identifier: MIT


__all__ = ("UnsupportedVersionWarning",)


class UnsupportedVersionWarning(UserWarning):
    message: str = (
        "The version of Lavalink you are using is not supported by Mafic. "
        "It should still work but not all features are supported."
    )