# SPDX-License-Identifier: MIT

from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING, Any

from pkg_resources import get_distribution  # pyright: ignore[reportUnknownVariableType]
from pkg_resources import DistributionNotFound

from .errors import MultipleCompatibleLibraries, NoCompatibleLibraries

__all__ = (
    "Client",
    "Connectable",
    "ExponentialBackoff",
    "Guild",
    "GuildChannel",
    "GuildVoiceStatePayload",
    "MISSING",
    "StageChannel",
    "VoiceChannel",
    "VoiceProtocol",
    "VoiceServerUpdatePayload",
    "dumps",
    "loads",
    "version_info",
)

libraries = ("nextcord", "disnake", "py-cord", "discord.py", "discord")
found: list[str] = []


for library in libraries:
    try:
        get_distribution(library)
    except DistributionNotFound:
        pass
    else:
        found.append(library)


if not getenv("MAFIC_IGNORE_LIBRARY_CHECK", False):
    if len(found) == 0:
        raise NoCompatibleLibraries
    elif len(found) > 1:
        raise MultipleCompatibleLibraries(found)
else:
    if found[0] == "nextcord":
        from warnings import simplefilter

        # Ignore RuntimeWarning as we import the warning to filter :}
        simplefilter("ignore", RuntimeWarning)
        from nextcord.health_check import DistributionWarning

        simplefilter("always", RuntimeWarning)

        simplefilter("ignore", DistributionWarning)


library = found[0]


if library == "nextcord":
    from nextcord import (
        Client,
        Guild,
        StageChannel,
        VoiceChannel,
        VoiceProtocol,
        version_info,
    )
    from nextcord.abc import Connectable, GuildChannel
    from nextcord.backoff import ExponentialBackoff
    from nextcord.utils import MISSING

    if TYPE_CHECKING:
        from nextcord.types.voice import (
            GuildVoiceState as GuildVoiceStatePayload,
            VoiceServerUpdate as VoiceServerUpdatePayload,
        )
elif library == "disnake":
    from disnake import (
        Client,
        Guild,
        StageChannel,
        VoiceChannel,
        VoiceProtocol,
        version_info,
    )
    from disnake.abc import Connectable, GuildChannel
    from disnake.backoff import ExponentialBackoff
    from disnake.utils import MISSING

    if TYPE_CHECKING:
        if version_info >= (2, 6):
            from disnake.types.gateway import (
                VoiceServerUpdateEvent as VoiceServerUpdatePayload,  # pyright: ignore
            )
        else:
            from disnake.types.voice import (
                VoiceServerUpdate as VoiceServerUpdatePayload,  # pyright: ignore
            )
        from disnake.types.voice import GuildVoiceState as GuildVoiceStatePayload
else:
    from discord import (
        Client,
        Guild,
        StageChannel,
        VoiceChannel,
        VoiceProtocol,
        version_info,
    )
    from discord.abc import Connectable, GuildChannel
    from discord.backoff import ExponentialBackoff
    from discord.utils import MISSING

    if TYPE_CHECKING:
        from discord.types.voice import (
            GuildVoiceState as GuildVoiceStatePayload,
            VoiceServerUpdate as VoiceServerUpdatePayload,
        )


try:
    from orjson import dumps as _dumps, loads

    def dumps(obj: Any) -> str:
        return _dumps(obj).decode()

except ImportError:
    from json import dumps, loads


if version_info.major != 2:
    raise RuntimeError(f"Mafic requires version 2 of {library}.")
