"""Very basic bot to test mafic."""

from __future__ import annotations

import asyncio
import traceback
from asyncio import gather
from logging import DEBUG, getLogger
from os import environ, getenv
from typing import TYPE_CHECKING

import orjson
from botbase import BotBase
from nextcord import Intents, Interaction

from mafic import (
    EQBand,
    Equalizer,
    Filter,
    Group,
    NodePool,
    Player,
    Playlist,
    Region,
    Track,
    TrackEndEvent,
    VoiceRegion,
)

if TYPE_CHECKING:
    from typing import TypedDict

    from nextcord.abc import Connectable
    from typing_extensions import NotRequired

    from mafic import Node

    class LavalinkInfo(TypedDict):
        host: str
        port: int
        password: str
        regions: NotRequired[list[str]]
        shard_ids: NotRequired[list[int]]
        label: str


REGION_CLS = [Group, Region, VoiceRegion]

getLogger("mafic").setLevel(DEBUG)


class TestBot(BotBase):
    def __init__(self) -> None:
        super().__init__(
            shard_count=2 if getenv("TEST_BALANCING") else None,
            shard_ids=[0, 1] if getenv("TEST_BALANCING") else None,
            intents=Intents(guilds=True, voice_states=True),
            db_enabled=False,
        )

        self.pool = NodePool(self)

    # Gateway-proxy is used to keep gateway connections alive.
    # This is added in testing to ensure resuming a connection works, even over restart.
    async def launch_shard(
        self, _gateway: str, shard_id: int, *, initial: bool = False
    ) -> None:
        return await super().launch_shard(
            environ["GW_PROXY"], shard_id, initial=initial
        )

    async def before_identify_hook(
        self, _shard_id: int | None, *, initial: bool = False  # noqa: ARG002
    ) -> None:
        # gateway-proxy
        return

    async def add_nodes(self) -> None:  # noqa: PLR0912
        with open(environ["LAVALINK_FILE"], "rb") as f:
            data: list[LavalinkInfo] = orjson.loads(f.read())

        try:
            with open("lavalink.txt") as f:
                session_id = f.read()
        except FileNotFoundError:
            session_id = None

        for node in data:
            regions: list[Group | Region | VoiceRegion] | None = None
            if "regions" in node:
                regions = []
                for region_str in node["regions"]:
                    for cls in REGION_CLS:
                        if region_str in cls.__members__:
                            region = cls[region_str]
                            break
                    else:
                        msg = f"Invalid region: {region_str}"
                        raise ValueError(msg)

                    regions.append(region)

            if environ["LAVALINK_FILE"] == "lavalink/multi-nodes.json":
                await asyncio.sleep(10)

            for tries in range(5):
                try:
                    await self.pool.create_node(
                        host=node["host"],
                        port=node["port"],
                        password=node["password"],
                        regions=regions,
                        label=node["label"],
                        shard_ids=node.get("shard_ids"),
                        resuming_session_id=session_id,
                    )
                except:  # noqa: E722
                    traceback.print_exc()
                    await asyncio.sleep(tries * 2)
                else:
                    break

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        await gather(self.add_nodes(), super().start(token, reconnect=reconnect))

    async def on_node_ready(self, node: Node) -> None:
        # ! DO NOT USE A TEXT FILE FOR REAL DATA STORAGE
        # ! THIS IS FOR TESTING ONLY
        with open("lavalink.txt", "w") as f:
            f.write(node.session_id)


bot = TestBot()


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

    await inter.response.defer()

    channel = inter.user.voice.channel

    try:
        await channel.connect(cls=MyPlayer, timeout=5)
    except asyncio.TimeoutError:
        return await inter.send("Timed out connecting to voice channel.")

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
    return None


@bot.slash_command()
async def stop(inter: Interaction):
    """Stop playing."""
    if not inter.guild.voice_client:
        return await inter.send("I am not in a voice channel.")

    player: MyPlayer = inter.guild.voice_client

    await player.stop()
    await inter.send("Stopped playing.")
    return None


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
    return None


# Test bot, do not have an open close command.
@bot.slash_command()
async def close(inter: Interaction):
    await inter.send("Closing bot.")
    await bot.close()


@bot.slash_command()
async def transfer(inter: Interaction):
    await bot.pool.remove_node(inter.guild.voice_client.node)
    await inter.send("Transferred node.")


@bot.slash_command()
async def boost(inter: Interaction):
    if not inter.guild.voice_client:
        return await inter.send("I am not in a voice channel.")

    player: MyPlayer = inter.guild.voice_client

    bassboost_equalizer = Equalizer([EQBand(idx, 0.30) for idx in range(0, 15)])

    bassboost_filter = Filter(bassboost_equalizer)
    await player.add_filter(bassboost_filter, label="boost")

    await inter.send("Boost enabled.")
    return None


@bot.slash_command()
async def unboost(inter: Interaction):
    if not inter.guild.voice_client:
        return await inter.send("I am not in a voice channel.")

    player: MyPlayer = inter.guild.voice_client

    await player.remove_filter("boost")

    await inter.send("Boost disabled.")
    return None


bot.run(getenv("TOKEN"))
