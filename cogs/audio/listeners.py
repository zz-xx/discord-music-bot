from datetime import datetime

import discord
import wavelink
from discord.ext import commands

from cogs.audio.disconnect import Disconnect


class Listeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.member.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """_summary_

        Args:
            member (discord.member.Member): _description_
            before (discord.VoiceState): _description_
            after (discord.VoiceState): _description_
        """
        if member.bot and member.id == self.bot.user.id:
            if after.channel is None:
                voice_channel = self.bot.get_channel(before.channel.id)
                await voice_channel.send(
                    f"Disconnected on {discord.utils.format_dt(datetime.now())}."
                )
                await Disconnect.disconnect_player(self.bot, member.guild)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting.

        Args:
            node (wavelink.Node): _description_
        """
        print(f"Node: <{node.identifier}> is ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_end(
        self, player: wavelink.Player, track: wavelink.Track, reason
    ):
        """_summary_

        Args:
            player (wavelink.Player): _description_
            track (wavelink.Track): _description_
            reason (_type_): _description_
        """

        if not player.queue.is_empty:
            new = await player.queue.get_wait()
            voice_channel = self.bot.get_channel(player.channel.id)
            await voice_channel.send(
                f"Playback {reason} for **{track.title}**. Now playing **{new.title}**."
            )

            try:
                await player.play(new)
            except wavelink.LavalinkException as e:
                await voice_channel.send(
                    f"Lavalink error - {e} while playing {new.title}. Try again after some time."
                )
                new = await player.queue.get_wait()
                await player.play(new)

        else:
            await player.stop()

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(
        self, player: wavelink.Player, track: wavelink.Track, threshold
    ):
        """_summary_

        Args:
            player (wavelink.Player): _description_
            track (wavelink.Track): _description_
            threshold (_type_): _description_
        """
        if not player.queue.is_empty:
            await voice_channel.send(
                f"Lavalink track stuck - {threshold} while playing {track.title}. Try again after some time."
            )
            new = await player.queue.get_wait()
            voice_channel = self.bot.get_channel(player.channel.id)
            await voice_channel.send(f"Now playing {new.title}.")
            await player.play(new)
        else:
            await player.stop()

    @commands.Cog.listener()
    async def on_wavelink_track_exception(
        self, player: wavelink.Player, track: wavelink.Track, error
    ):
        """_summary_

        Args:
            player (wavelink.Player): _description_
            track (wavelink.Track): _description_
            error (_type_): _description_
        """
        if not player.queue.is_empty:
            new = await player.queue.get_wait()
            voice_channel = self.bot.get_channel(player.channel.id)
            await voice_channel.send(
                f"Lavalink error - {error} while playing {track.title}. Try again after some time."
            )
            await voice_channel.send(f"Now playing {new.title}.")
            await player.play(new)
        else:
            await player.stop()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Listeners(bot))
