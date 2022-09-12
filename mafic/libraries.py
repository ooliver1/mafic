# SPDX-License-Identifier: MIT

from __future__ import annotations

from pkg_resources import DistributionNotFound, get_distribution

from .errors import MultipleCompatibleLibraries, NoCompatibleLibraries

__all__ = ("VoiceProtocol",)

libraries = ("nextcord", "disnake", "py-cord", "discord.py", "discord")
found: list[str] = []


for library in libraries:
    try:
        get_distribution(library)
    except DistributionNotFound:
        pass
    else:
        found.append(library)


if len(found) == 0:
    raise NoCompatibleLibraries
elif len(found) > 1:
    raise MultipleCompatibleLibraries(found)


library = found[0]


if library == "nextcord":
    from nextcord import VoiceProtocol
elif library == "disnake":
    from disnake import VoiceProtocol
else:
    from discord import VoiceProtocol
