# SPDX-License-Identifier: MIT

from __future__ import annotations

from enum import Enum

__all__ = ("SearchType",)


class SearchType(Enum):
    """Represents a search type for Lavalink.

    .. danger::

        Many of these require plugins to be used.

        `LavaSrc <https://github.com/TopiSenpai/LavaSrc>`_:
            - :attr:`SPOTIFY_SEARCH`
            - :attr:`SPOTIFY_RECOMMENDATIONS`
            - :attr:`APPLE_MUSIC`
            - :attr:`DEEZER_SEARCH`
            - :attr:`DEEZER_ISRC`
            - :attr:`YANDEX`

        `DuncteBot <https://github.com/DuncteBot/skybot-lavalink-plugin>`_:
            - :attr:`SPEECH`
    """

    YOUTUBE = "ytsearch"
    YOUTUBE_MUSIC = "ytmsearch"
    SOUNDCLOUD = "scsearch"

    # Plugins

    # LavaSrc
    SPOTIFY_SEARCH = "spsearch"
    SPOTIFY_RECOMMENDATIONS = "sprec"
    APPLE_MUSIC = "amsearch"
    DEEZER_SEARCH = "dzsearch"
    DEEZER_ISRC = "dzisrc"
    YANDEX_MUSIC = "ymsearch"

    # DuncteBot
    TTS = "speak"
