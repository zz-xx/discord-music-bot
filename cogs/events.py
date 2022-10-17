import os
import platform

import discord
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """_summary_"""

        print(f"Logged in as {self.bot.user.name}")
        print(f"Discord.py API version: {discord.__version__}")
        print(f"Python version: {platform.python_version()}")
        print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        print("-------------------")

        await self.bot.change_presence(
            activity=discord.Streaming(
                name="Use slash commands.",
                url="https://www.twitch.tv/pewdiepie",
                platform="Twitch",
                twitch_name="pewdiepie",
            )
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Events(bot))
