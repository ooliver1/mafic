# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections import OrderedDict
from functools import reduce
from logging import getLogger
from operator import or_
from time import time
from typing import TYPE_CHECKING

from .__libraries import GuildChannel, StageChannel, VoiceChannel, VoiceProtocol
from .errors import PlayerNotConnected
from .filter import Filter
from .playlist import Playlist
from .pool import NodePool
from .search_type import SearchType
from .track import Track

if TYPE_CHECKING:
    from .__libraries import (
        Client,
        Connectable,
        Guild,
        GuildVoiceStatePayload,
        VoiceServerUpdatePayload,
    )
    from .node import Node
    from .typings import PlayerUpdateState


_log = getLogger(__name__)
__all__ = ("Player",)


class Player(VoiceProtocol):
    def __init__(
        self,
        client: Client,
        channel: Connectable,
        *,
        node: Node | None = None,
    ) -> None:
        self.client: Client = client
        self.channel: Connectable = channel

        if not isinstance(self.channel, GuildChannel):
            raise TypeError("Voice channel must be a GuildChannel.")

        self.guild: Guild = self.channel.guild

        self._node = node

        self._guild_id: int = self.guild.id
        self._session_id: str | None = None
        self._server_state: VoiceServerUpdatePayload | None = None
        self._connected: bool = False
        self._position: int = 0
        self._last_update: int = 0
        self._ping = -1
        self._current: Track | None = None
        self._filters: OrderedDict[str, Filter] = OrderedDict()

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def position(self) -> int:
        pos = self._position

        if self._connected and self._current is not None:
            # Add the time since the last update to the position.
            # If the track total time is less than that, use that.
            pos = min(
                self._current.length, pos + int((time() - self._last_update) * 1000)
            )

        return pos

    @property
    def ping(self) -> int:
        return self._ping

    @property
    def node(self) -> Node:
        if self._node is None:
            _log.warning(
                "Unable to use best node, player not connected, finding random node.",
                extra={"guild": self._guild_id},
            )
            return NodePool.get_random_node()

        return self._node

    def update_state(self, state: PlayerUpdateState) -> None:
        self._last_update = state["time"]
        self._position = state.get("position", 0)
        self._connected = state["connected"]
        self._ping = state.get("ping", -1)

    # If people are so in love with the VoiceClient interface
    def is_connected(self) -> bool:
        return self._connected

    async def _dispatch_player_update(self) -> None:
        if self._node is None:
            _log.debug("Recieved voice update before node was found.")
            return

        if self._session_id is None:
            _log.debug("Receieved player update before session ID was set.")
            return

        if self._server_state is None:
            _log.debug("Receieved player update before server state was found")
            return

        await self._node.voice_update(
            guild_id=self._guild_id,
            session_id=self._session_id,
            data=self._server_state,
        )

    async def on_voice_state_update(self, data: GuildVoiceStatePayload) -> None:
        before_session_id = self._session_id
        self._session_id = data["session_id"]

        channel_id = data["channel_id"]
        channel = self.guild.get_channel(int(channel_id))
        assert isinstance(channel, (StageChannel, VoiceChannel))

        self.channel = channel

        if self._session_id != before_session_id:
            await self._dispatch_player_update()

    async def on_voice_server_update(self, data: VoiceServerUpdatePayload) -> None:
        # Fetch the best node as we either don't know the best one yet.
        # Or the node we were using was not the best one (endpoint optimisation).
        if (
            self._node is None
            or self._server_state is None
            or self._server_state["endpoint"] != data["endpoint"]
        ):
            _log.debug("Getting best node for player", extra={"guild": self._guild_id})
            self._node = NodePool.get_node(
                guild_id=data["guild_id"], endpoint=data["endpoint"]
            )

        self._node.players[self._guild_id] = self

        self._guild_id = int(data["guild_id"])
        self._server_state = data

        await self._dispatch_player_update()

    async def connect(
        self,
        *,
        timeout: float,
        reconnect: bool,
        self_mute: bool = False,
        self_deaf: bool = False,
    ) -> None:
        if not isinstance(self.channel, GuildChannel):
            raise TypeError("Voice channel must be a GuildChannel.")

        _log.debug("Connecting to voice channel %s", self.channel.id)

        await self.channel.guild.change_voice_state(
            channel=self.channel, self_mute=self_mute, self_deaf=self_deaf
        )
        self._connected = True

    async def disconnect(self, *, force: bool = False) -> None:
        try:
            _log.debug(
                "Disconnecting from voice channel.",
                extra={"guild": self._guild_id},
            )
            await self.guild.change_voice_state(channel=None)
        finally:
            self.cleanup()
            self._connected = False

    async def destroy(self) -> None:
        _log.debug(
            "Disconnecting player and destroying client.",
            extra={"guild": self._guild_id},
        )
        await self.disconnect()

        if self._node is not None:
            self._node.players.pop(self.guild.id, None)
            await self._node.destroy(guild_id=self.guild.id)

    async def fetch_tracks(
        self, query: str, search_type: SearchType | str = SearchType.YOUTUBE
    ) -> list[Track] | Playlist | None:
        node = self.node

        raw_type: str
        if isinstance(search_type, SearchType):
            raw_type = search_type.value
        else:
            raw_type = search_type

        return await node.fetch_tracks(query, search_type=raw_type)

    async def play(
        self,
        track: Track,
        /,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        volume: int | None = None,
        replace: bool = True,
        pause: bool | None = None,
    ) -> None:
        if self._node is None or not self._connected:
            raise PlayerNotConnected

        await self._node.play(
            guild_id=self._guild_id,
            track=track,
            start_time=start_time,
            end_time=end_time,
            volume=volume,
            no_replace=not replace,
            pause=pause,
        )

        self._current = track

    async def pause(self, pause: bool = True) -> None:
        if self._node is None or not self._connected:
            raise PlayerNotConnected

        await self._node.pause(guild_id=self._guild_id, pause=pause)

    async def resume(self) -> None:
        await self.pause(False)

    async def stop(self) -> None:
        if self._node is None or not self._connected:
            raise PlayerNotConnected

        await self._node.stop(guild_id=self._guild_id)

    async def _update_filters(self, *, fast_apply: bool) -> None:
        if self._node is None or not self._connected:
            raise PlayerNotConnected

        await self._node.filter(
            guild_id=self._guild_id, filter=reduce(or_, self._filters.values())
        )

        if fast_apply:
            await self.seek(self.position)

    async def add_filter(
        self, filter: Filter, /, *, label: str, fast_apply: bool = False
    ) -> None:
        self._filters[label] = filter

        await self._update_filters(fast_apply=True)

    async def remove_filter(self, label: str, *, fast_apply: bool = False) -> None:
        self._filters.pop(label, None)

        await self._update_filters(fast_apply=True)

    async def clear_filters(self, *, fast_apply: bool = False) -> None:
        self._filters.clear()

        await self._update_filters(fast_apply=True)

    async def set_volume(self, volume: int, /) -> None:
        if self._node is None or not self._connected:
            raise PlayerNotConnected

        await self._node.volume(guild_id=self._guild_id, volume=volume)

    async def seek(self, position: int, /) -> None:
        if self._node is None or not self._connected:
            raise PlayerNotConnected

        await self._node.seek(guild_id=self._guild_id, position=position)
        self._position = position
