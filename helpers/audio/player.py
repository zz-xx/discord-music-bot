from asyncio import TimeoutError
import datetime as dt
from os import chdir

import discord
from discord.ext.commands.core import check
import wavelink
from discord_slash.model import ButtonStyle, ContextMenuType
from discord_slash.utils.manage_components import (
    create_button,
    create_actionrow,
    create_select,
    create_select_option,
    wait_for_component,
)

from helpers.audio.exception_handler import *
from helpers.audio.queue import Queue


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()
        self.eq_levels = [0.0] * 15

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlreadyConnectedToChannel

        if (channel := getattr(ctx.author.voice, "channel", channel)) is None:
            raise NoVoiceChannel

        await super().connect(channel.id)
        return channel

    async def teardown(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise NoTracksFound

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)
        elif len(tracks) == 1:
            self.queue.add(tracks[0])
            await ctx.send(f"Added {tracks[0].title} to the queue.")
        else:
            if (track := await self.choose_track(ctx, tracks)) is not None:
                self.queue.add(track)
                await ctx.send(f"Added {track.title} to the queue.")

        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def choose_track(self, ctx, tracks):

        search_results = [
            f"{t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
            for i, t in enumerate(tracks[:5])
        ]
        number_emotes = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        options = [
            create_select_option(
                search_results[i], value=str(i), emoji=number_emotes[i]
            )
            for i in range(0, 5)
        ]
        select = create_select(
            options=options,
            placeholder="🎵 Choose a song 🎵",  # the placeholder text to show when no options have been chosen
            min_values=1,  # the minimum number of options a user must select
            max_values=1,
            custom_id="select",
        )

        ar = create_actionrow(select)
        msg = await ctx.send(
            "🔎 **Search results**", components=[ar]
        )  # like action row with buttons but without * in front of the variable

        while True:
            try:
                button_ctx = await wait_for_component(
                    self.bot, components=ar, timeout=60
                )
                await button_ctx.send(
                    f"You selected **{search_results[int(button_ctx.selected_options[0])]}**!",
                    hidden=True,
                )
                # print(button_ctx.selected_options)
                return tracks[int(button_ctx.selected_options[0])]

            except TimeoutError:
                ar["components"][0]["disabled"] = True
                await msg.edit(content="⏳ **Timed out** ⏳", components=[ar])
                break

    async def start_playback(self):
        await self.play(self.queue.current_track)

    async def advance(self):
        try:
            if (track := self.queue.get_next_track()) is not None:
                await self.play(track)
        except QueueIsEmpty:
            pass

    async def repeat_track(self):
        await self.play(self.queue.current_track)
