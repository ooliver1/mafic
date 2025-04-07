# SPDX-License-Identifier: MIT
# ruff: noqa: PGH003

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from os import getenv
from typing import TYPE_CHECKING, Any

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
        version(library)
    except PackageNotFoundError:
        pass
    else:
        found.append(library)


if not getenv("MAFIC_IGNORE_LIBRARY_CHECK"):
    if len(found) == 0:
        raise NoCompatibleLibraries
    elif len(found) > 1:
        raise MultipleCompatibleLibraries(found)

    if found[0] == "nextcord":
        from warnings import simplefilter

        # Ignore RuntimeWarning as we import the warning to filter :}
        simplefilter("ignore", RuntimeWarning)
        try:
            from nextcord.health_check import DistributionWarning
        except ImportError:
            # nextcord >= 3.0
            pass
        else:
            simplefilter("ignore", DistributionWarning)
        finally:
            simplefilter("always", RuntimeWarning)


library = found[0]


if library == "nextcord":
    from nextcord import version_info
elif library == "disnake":
    from disnake import version_info
else:
    from discord import version_info


if library == "nextcord":
    if version_info.major not in (2, 3):
        msg = "Mafic requires version 2 or 3 of nextcord."
        raise RuntimeError(msg)
elif version_info.major != 2:
    msg = f"Mafic requires version 2 of {library}."
    raise RuntimeError(msg)


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
                VoiceServerUpdateEvent as VoiceServerUpdatePayload,
            )
        else:
            from disnake.types.voice import (
                # Pyright rules are unnecessarily long.
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
            GuildVoiceState as GuildVoiceStatePayload,  # noqa: TCH004
            VoiceServerUpdate as VoiceServerUpdatePayload,  # noqa: TCH004
        )


try:
    from orjson import dumps as _dumps, loads

    def dumps(obj: Any) -> str:  # noqa: ANN401
        return _dumps(obj).decode()

except ImportError:
    from json import dumps, loads
