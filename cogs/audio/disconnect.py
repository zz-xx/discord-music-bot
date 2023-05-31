from datetime import datetime

import discord
from discord.ext import commands


class Disconnect(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="disconnect", with_app_command=True)
    async def disconnect_command(self, ctx: commands.Context):
        """Disconnect bot
        Args:
            ctx (commands.Context): _description_
        """

        if not ctx.author.voice:
            await ctx.send("You are not connected to any voice channel.")
            return

        if ctx.voice_client.channel is None:
            await ctx.send("Bot is not playing anything.")
            return

        if ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await ctx.send(
                "Join the voice channel the bot is playing in to disconnect it."
            )
            return

        await Disconnect.disconnect_player(self.bot, ctx.guild)
        await ctx.send(
            f"Disconnected by {ctx.author.mention} on {discord.utils.format_dt(datetime.now())} ."
        )

    @staticmethod
    async def disconnect_player(bot: commands.Bot, guild: discord.Guild):
        """_summary_
        Args:
            bot (commands.Bot): _description_
            guild (discord.Guild): _description_
        """
        player = bot.node.get_player(guild)

        # need to check this because this will be fired two times
        # if disconnected using commands
        if player is not None:
            await player.stop()
            player.queue.clear()
            player.cleanup()
            await player.disconnect()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Disconnect(bot))
