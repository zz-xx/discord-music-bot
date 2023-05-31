from datetime import datetime

import discord
import wavelink
from discord.ext import commands

from cogs.audio.disconnect import Disconnect


class Listeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting.
        Args:
            node (wavelink.Node): _description_
        """
        print(f"Node: <{node.id}> is ready!")

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


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Listeners(bot))
