from __future__ import annotations

from asyncio import sleep
from os import getenv

from botbase import BotBase
from nextcord import Intents, Interaction

from mafic import NodePool, Player


class TestBot(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ready_ran = False
        self.pool = NodePool()

    async def on_ready(self):
        if self.ready_ran:
            return

        # Account for docker still starting up.
        await sleep(5)
        await self.pool.create_node(
            host=getenv("LAVALINK_HOST"),
            port=6969,
            label="main",
            password="haha",
            client=self,
        )

        self.ready_ran = True


intents = Intents.none()
intents.guilds = True
intents.voice_states = True
bot = TestBot(intents=intents)


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
