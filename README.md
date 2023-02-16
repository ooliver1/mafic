# Mafic

[![MIT License](https://custom-icon-badges.demolab.com/github/license/ooliver1/mafic?color=845ec2&logo=code-square)](https://github.com/ooliver1/mafic/blob/master/LICENSE "License File")
[![Releases](https://custom-icon-badges.demolab.com/github/v/release/ooliver1/mafic?display_name=tag&include_prereleases&sort=semver&logo=commit&color=c25db8)](https://github.com/ooliver1/mafic/releases "Mafic Releases")
[![Discord](https://img.shields.io/discord/864563184919773226?color=f062a4&logo=discord&logoColor=white)](https://discord.gg/mMvUABNegY "Discord Server")
[![Lint Workflow Status](https://custom-icon-badges.demolab.com/github/actions/workflow/status/ooliver1/mafic/lint.yml?label=lint&logo=codescan-checkmark&color=ff738c)](https://github.com/ooliver1/mafic/actions/workflows/lint.yml "Lint Workflow")
[![PyPI - Status](https://img.shields.io/pypi/status/mafic?color=ff9075&label=PyPI&logo=pypi&logoColor=white)](https://pypi.org/project/mafic "Mafic PyPI Project")
[![Open Issues](https://custom-icon-badges.demolab.com/github/issues-raw/ooliver1/mafic?logo=issue-opened&color=ffb263)](https://github.com/ooliver1/mafic/issues "Open Issues")
[![Open PRs](https://custom-icon-badges.demolab.com/github/issues-pr-raw/ooliver1/mafic?logo=git-pull-request&color=ffd55f)](https://github.com/ooliver1/mafic/pulls "Open Pull Requests")
[![Read the Docs](https://img.shields.io/readthedocs/mafic?logo=read%20the%20docs&logoColor=white&color=f9f871)](https://mafic.readthedocs.io/en/latest/)

A properly typehinted lavalink client for discord.py, nextcord, disnake and py-cord.

## Installation

```bash
pip install mafic
```

> **Note**
> Use `python -m`, `py -m`, `python3 -m` or similar if that is how you install packages.
> Generally windows uses `py -m pip` and linux uses `python3 -m pip`

## Discord Server

[Join the Discord Server](https://discord.gg/mMvUABNegY) for support and updates.

## Documentation

[Read the docs](https://mafic.readthedocs.io/en/latest/).

## Features

- Fully customisable node balancing.
- Multi-node support.
- Filters.
- Full API coverage.
- Properly typehinted for Pyright strict.

## Usage

Go to the [Lavalink Repository](https://github.com/freyacodes/lavalink#server-configuration)
to set up a Lavalink node.

```python
import os

import mafic
import nextcord
from nextcord.ext import commands


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pool = mafic.NodePool(self)
        self.loop.create_task(self.add_nodes())

    async def add_nodes(self):
        await self.pool.create_node(
            host="127.0.0.1",
            port=2333,
            label="MAIN",
            password="<password>",
        )


bot = MyBot(intents=nextcord.Intents(guilds=True, voice_states=True))


@bot.slash_command(dm_permission=False)
async def play(inter: nextcord.Interaction, query: str):
    if not inter.guild.voice_client:
        player = await inter.user.voice.channel.connect(cls=mafic.Player)
    else:
        player = inter.guild.voice_client

    tracks = await player.fetch_tracks(query)

    if not tracks:
        return await inter.send("No tracks found.")

    track = tracks[0]

    await player.play(track)

    await inter.send(f"Playing {track.title}.")


bot.run(...)
```
