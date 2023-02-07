"""A simple example of using Mafic."""

from __future__ import annotations

import traceback
from logging import DEBUG, getLogger
from os import getenv
from typing import Any

from nextcord import Intents, Interaction, Member
from nextcord.abc import Connectable
from nextcord.ext import commands

from mafic import NodePool, Player, Playlist, Track, TrackEndEvent

getLogger("mafic").setLevel(DEBUG)


class Bot(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.ready_ran = False
        self.pool = NodePool(self)

    async def on_ready(self):
        if self.ready_ran:
            return

        await self.pool.create_node(
            host="127.0.0.1",
            port=6969,
            label="MAIN",
            password="haha",
        )

        self.ready_ran = True


bot = Bot(intents=Intents(guilds=True, voice_states=True))


class MyPlayer(Player[Bot]):
    def __init__(self, client: Bot, channel: Connectable) -> None:
        super().__init__(client, channel)

        # Mafic does not provide a queue system right now, low priority.
        self.queue: list[Track] = []


@bot.slash_command(dm_permission=False)
async def join(inter: Interaction[Bot]):
    """Join your voice channel."""

    assert isinstance(inter.user, Member)

    if not inter.user.voice or not inter.user.voice.channel:
        return await inter.response.send_message("You are not in a voice channel.")

    channel = inter.user.voice.channel

    # This apparently **must** only be `Client`.
    await channel.connect(cls=MyPlayer)  # pyright: ignore[reportGeneralTypeIssues]
    await inter.send(f"Joined {channel.mention}.")


@bot.slash_command(dm_permission=False)
async def play(inter: Interaction[Bot], query: str):
    """Play a song.

    query:
        The song to search or play.
    """

    assert inter.guild is not None

    if not inter.guild.voice_client:
        await join(inter)

    player: MyPlayer = (
        inter.guild.voice_client
    )  # pyright: ignore[reportGeneralTypeIssues]

    tracks = await player.fetch_tracks(query)

    if not tracks:
        return await inter.send("No tracks found.")

    if isinstance(tracks, Playlist):
        tracks = tracks.tracks
        if len(tracks) > 1:
            player.queue.extend(tracks[1:])

    track = tracks[0]

    await player.play(track)

    await inter.send(f"Playing {track}")


@bot.listen()
async def on_track_end(event: TrackEndEvent):
    assert isinstance(event.player, MyPlayer)

    if event.player.queue:
        await event.player.play(event.player.queue.pop(0))


@bot.event
async def on_application_command_error(inter: Interaction[Bot], error: Exception):
    traceback.print_exception(type(error), error, error.__traceback__)
    await inter.send(f"An error occurred: {error}")


STATS = """```
Uptime: {uptime}
Memory: {used:.0f}MiB : {free:.0f}MiB / {allocated:.0f}MiB -- {reservable:.0f}MiB
CPU: {system_load:.2f}% : {lavalink_load:.2f}%
Players: {player_count}
Playing Players: {playing_player_count}
```"""

bot.run(getenv("TOKEN"))
