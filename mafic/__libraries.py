# SPDX-License-Identifier: MIT

from __future__ import annotations

from os import getenv
from typing import Any

from pkg_resources import DistributionNotFound, get_distribution

from .errors import MultipleCompatibleLibraries, NoCompatibleLibraries

__all__ = (
    "Client",
    "Connectable",
    "ExponentialBackoff",
    "GuildChannel",
    "GuildVoiceStatePayload",
    "VoiceProtocol",
    "VoiceServerUpdatePayload",
    "dumps",
    "loads",
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

        simplefilter("ignore", RuntimeWarning)

        simplefilter("ignore", DistributionWarning)


library = found[0]


if library == "nextcord":
    from nextcord import Client, VoiceProtocol
    from nextcord.abc import Connectable, GuildChannel
    from nextcord.backoff import ExponentialBackoff
    from nextcord.types.voice import (
        GuildVoiceState as GuildVoiceStatePayload,
        VoiceServerUpdate as VoiceServerUpdatePayload,
    )
elif library == "disnake":
    from disnake import Client, VoiceProtocol
    from disnake.abc import Connectable, GuildChannel
    from disnake.backoff import ExponentialBackoff
    from disnake.types.voice import (
        GuildVoiceState as GuildVoiceStatePayload,
        VoiceServerUpdate as VoiceServerUpdatePayload,
    )
else:
    from discord import Client, VoiceProtocol
    from discord.abc import Connectable, GuildChannel
    from discord.backoff import ExponentialBackoff
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
