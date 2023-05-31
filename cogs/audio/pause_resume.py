import wavelink
from discord.ext import commands


class PauseResume(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="pause", with_app_command=True)
    async def pause_command(self, ctx: commands.Context):
        """Pause.
        Args:
            ctx (commands.Context): _description_
        """
        if not ctx.author.voice:
            await ctx.send("You are not connected to any voice channel.")
            return

        vc: wavelink.Player = ctx.voice_client

        if vc is None:
            await ctx.send("Bot is not playing anything.")
            return
        if vc:
            if ctx.voice_client.channel.id != ctx.author.voice.channel.id:
                await ctx.send("Join VC the bot is playing in to use `skip`.")
                return

        if not vc.queue.is_empty:
            await vc.pause()

    @commands.hybrid_command(name="resume", with_app_command=True)
    async def resume_command(self, ctx: commands.Context):
        """Resume.
        Args:
            ctx (commands.Context): _description_
        """
        if not ctx.author.voice:
            await ctx.send("You are not connected to any voice channel.")
            return

        vc: wavelink.Player = ctx.voice_client

        if vc is None:
            await ctx.send("Bot is not playing anything.")
            return
        if vc:
            if ctx.voice_client.channel.id != ctx.author.voice.channel.id:
                await ctx.send("Join VC the bot is playing in to use `skip`.")
                return

        if not vc.queue.is_empty:
            await vc.resume()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PauseResume(bot))
