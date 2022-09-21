# SPDX-License-Identifier: MIT

from __future__ import annotations

from enum import Enum

__all__ = ("SearchType",)


class SearchType(Enum):
    YOUTUBE = "ytsearch"
    YOUTUBE_MUSIC = "ytmsearch"
    SOUNDCLOUD = "scsearch"
