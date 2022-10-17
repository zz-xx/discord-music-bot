from typing import Union

import discord
import wavelink
from discord import app_commands
from discord.ext import commands

bot: Union[commands.Bot, None]


async def context_menu_play(itx: discord.Interaction, message: discord.Message):
    """_summary_

    Args:
        itx (discord.Interaction): _description_
        message (discord.Message): _description_
    """
    if not itx.user.voice:
        await itx.response.send_message("You are not connected to any voice channel.")
        return

    voice_client = discord.utils.get(bot.voice_clients, guild=itx.guild)

    partial = wavelink.PartialTrack(query=message.content, cls=wavelink.YouTubeTrack)
    if not partial:
        await itx.response.send_message("No tracks found.")

    if not voice_client:
        vc: wavelink.Player = await itx.user.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
        print("player initialized")
        await itx.response.defer(ephemeral=True)
        track = await vc.play(partial)
        await itx.followup.send(f"Now playing: {track.title}")
        print(f"track title - {track.title}")

    else:
        if voice_client.channel.id != itx.user.voice.channel.id:
            await itx.response.send_message(
                "Bot is already playing in a voice channel."
            )
            return

        vc: wavelink.Player = itx.guild.voice_client
        await vc.queue.put_wait(partial)
        await itx.response.send_message(f"Added {partial.title} to the queue.")

        if not vc.is_playing() and not vc.queue.is_empty:
            await itx.channel.send(f"Now playing: {partial.title}")
            await vc.play(await vc.queue.get_wait())


async def context_menu_play_next(itx: discord.Interaction, message: discord.Message):
    """_summary_

    Args:
        itx (discord.Interaction): _description_
        message (discord.Message): _description_
    """
    if not itx.user.voice:
        await itx.response.send_message("You are not connected to any voice channel.")
        return

    voice_client = discord.utils.get(bot.voice_clients, guild=itx.guild)
    if voice_client is None:
        await itx.response.send_message("Bot is not playing anything.")
        return
    else:
        if voice_client.channel.id != itx.user.voice.channel.id:
            await itx.response.send_message(
                "Bot is already playing in a voice channel."
            )
            return

        vc: wavelink.Player = itx.guild.voice_client

        partial = wavelink.PartialTrack(
            query=message.content, cls=wavelink.YouTubeTrack
        )
        if not partial:
            await itx.response.send_message("No tracks found.")
            return

        await itx.response.defer(ephemeral=True)
        vc.queue.put_at_front(partial)
        await itx.followup.send(f"Playing {partial.title} next.")

        if not vc.is_playing() and not vc.queue.is_empty:
            await itx.response.defer(ephemeral=True)
            await vc.play(await vc.queue.get_wait())
            await itx.followup.send(f"Now playing: {partial.title}")


play_context_menu = app_commands.ContextMenu(
    name="play",
    callback=context_menu_play,
)

play_next_context_menu = app_commands.ContextMenu(
    name="play-next",
    callback=context_menu_play_next,
)


def init(input_bot: commands.Bot):
    """_summary_

    Args:
        input_bot (commands.Bot): _description_
    """
    global bot
    bot = input_bot
    bot.tree.add_command(play_context_menu)
    bot.tree.add_command(play_next_context_menu)
