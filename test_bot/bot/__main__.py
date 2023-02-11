"""Very basic bot to test mafic."""

from __future__ import annotations

import traceback
from asyncio import sleep
from logging import DEBUG, getLogger
from os import getenv

from botbase import BotBase
from nextcord import Intents, Interaction
from nextcord.abc import Connectable

from mafic import Group, NodePool, Player, Playlist, Region, Track, TrackEndEvent

getLogger("mafic").setLevel(DEBUG)


class TestBot(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ready_ran = False
        self.pool = NodePool(self)

    async def on_ready(self):
        if self.ready_ran:
            return

        # Excessively test pool balancing.
        if getenv("TEST_BALANCING"):
            # Account for docker still starting up.
            await sleep(5)
            await self.pool.create_node(
                host="127.0.0.1",
                port=6962,
                label="US-noshard",
                password="haha",
                regions=[Group.WEST, Region.OCEANIA, Region.EAST_ASIA],
            )
            await self.pool.create_node(
                host="127.0.0.1",
                port=6963,
                label="EU-noshard",
                password="haha",
                regions=[
                    Group.CENTRAL,
                    Region.WEST_ASIA,
                    Region.NORTH_ASIA,
                    Region.SOUTH_ASIA,
                ],
            )
            await self.pool.create_node(
                host="127.0.0.1",
                port=6964,
                label="US-shard0",
                password="haha",
                regions=[Group.WEST, Region.OCEANIA, Region.EAST_ASIA],
                shard_ids=[0],
            )
            await self.pool.create_node(
                host="127.0.0.1",
                port=6965,
                label="US-shard1",
                password="haha",
                regions=[Group.WEST, Region.OCEANIA, Region.EAST_ASIA],
                shard_ids=[1],
            )
            await self.pool.create_node(
                host="127.0.0.1",
                port=6966,
                label="EU-shard0-1",
                password="haha",
                regions=[
                    Group.CENTRAL,
                    Region.WEST_ASIA,
                    Region.NORTH_ASIA,
                    Region.SOUTH_ASIA,
                ],
                shard_ids=[0],
            )
            await self.pool.create_node(
                host="127.0.0.1",
                port=6967,
                label="EU-shard0-2",
                password="haha",
                regions=[
                    Group.CENTRAL,
                    Region.WEST_ASIA,
                    Region.NORTH_ASIA,
                    Region.SOUTH_ASIA,
                ],
                shard_ids=[0],
            )
            await self.pool.create_node(
                host="127.0.0.1",
                port=6968,
                label="EU-shard1-1",
                password="haha",
                regions=[
                    Group.CENTRAL,
                    Region.WEST_ASIA,
                    Region.NORTH_ASIA,
                    Region.SOUTH_ASIA,
                ],
                shard_ids=[1],
            )
            await self.pool.create_node(
                host="127.0.0.1",
                port=6969,
                label="EU-shard1-2",
                password="haha",
                regions=[
                    Group.CENTRAL,
                    Region.WEST_ASIA,
                    Region.NORTH_ASIA,
                    Region.SOUTH_ASIA,
                ],
                shard_ids=[1],
            )
        else:
            await self.pool.create_node(
                host="127.0.0.1",
                port=6969,
                label="MAIN",
                password="haha",
            )

        self.ready_ran = True


intents = Intents.none()
intents.guilds = True
intents.voice_states = True

if getenv("TEST_BALANCING"):
    bot = TestBot(intents=intents, shard_ids=[0, 1], shard_count=2)
else:
    bot = TestBot(intents=intents)


class MyPlayer(Player[TestBot]):
    def __init__(self, client: TestBot, channel: Connectable) -> None:
        super().__init__(client, channel)

        # Mafic does not provide a queue system right now, low priority.
        self.queue: list[Track] = []


@bot.slash_command()
async def join(inter: Interaction):
    """Join your voice channel."""

    if not inter.user.voice:
        return await inter.response.send_message("You are not in a voice channel.")

    channel = inter.user.voice.channel
    await channel.connect(cls=MyPlayer)
    await inter.send(f"Joined {channel.mention}.")


@bot.slash_command()
async def play(inter: Interaction, query: str):
    """Play a song.

    query:
        The song to search or play.
    """

    if not inter.guild.voice_client:
        await join(inter)

    player: MyPlayer = inter.guild.voice_client

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


@bot.slash_command()
async def stop(inter: Interaction):
    """Stop playing."""

    if not inter.guild.voice_client:
        return await inter.send("I am not in a voice channel.")

    player: MyPlayer = inter.guild.voice_client

    await player.stop()
    await inter.send("Stopped playing.")


@bot.listen()
async def on_track_end(event: TrackEndEvent[MyPlayer]):
    if event.player.queue:
        await event.player.play(event.player.queue.pop(0))


@bot.event
async def on_application_command_error(inter: Interaction, error: Exception):
    traceback.print_exception(type(error), error, error.__traceback__)
    await inter.send(f"An error occurred: {error}")


STATS = """```
Uptime: {uptime}
Memory: {used:.0f}MiB : {free:.0f}MiB / {allocated:.0f}MiB -- {reservable:.0f}MiB
CPU: {system_load:.2f}% : {lavalink_load:.2f}%
Players: {player_count}
Playing Players: {playing_player_count}
```"""


@bot.slash_command()
async def stats(inter: Interaction):
    node = bot.pool.nodes[0]

    stats = node.stats

    if not stats:
        return await inter.send("No stats available.")

    await inter.send(
        STATS.format(
            uptime=stats.uptime,
            used=stats.memory.used / 1024 / 1024,
            free=stats.memory.free / 1024 / 1024,
            allocated=stats.memory.allocated / 1024 / 1024,
            reservable=stats.memory.reservable / 1024 / 1024,
            system_load=stats.cpu.system_load * 100,
            lavalink_load=stats.cpu.lavalink_load * 100,
            player_count=stats.player_count,
            playing_player_count=stats.playing_player_count,
        )
    )


bot.run(getenv("TOKEN"))
