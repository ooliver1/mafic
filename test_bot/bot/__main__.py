from __future__ import annotations

from asyncio import sleep
from logging import DEBUG, getLogger
from os import getenv

from botbase import BotBase
from nextcord import Intents, Interaction

from mafic import Group, NodePool, Player, Region

getLogger("mafic").setLevel(DEBUG)


class TestBot(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ready_ran = False
        self.pool = NodePool(self)

    async def on_ready(self):
        if self.ready_ran:
            return

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

        self.ready_ran = True


intents = Intents.none()
intents.guilds = True
intents.voice_states = True
bot = TestBot(intents=intents, shard_ids=[0, 1], shard_count=2)


@bot.slash_command()
async def join(inter: Interaction):
    """Join your voice channel."""

    if not inter.user.voice:
        return await inter.response.send_message("You are not in a voice channel.")

    channel = inter.user.voice.channel
    await channel.connect(cls=Player)
    await inter.send(f"Joined {channel.mention}.")


@bot.slash_command()
async def play(inter: Interaction, query: str):
    """Play a song.

    query:
        The song to search or play.
    """

    if not inter.guild.voice_client:
        await join(inter)

    player: Player = inter.guild.voice_client

    tracks = await player.fetch_tracks(query)

    if not tracks:
        return await inter.response.send_message("No tracks found.")

    # TODO: handle playlists
    await player.play(tracks[0])


bot.run(getenv("TOKEN"))
