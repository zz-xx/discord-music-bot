import os
import platform

import discord
from discord.ext import commands
from discord_slash import SlashContext


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name}")
        print(f"Discord.py API version: {discord.__version__}")
        print(f"Python version: {platform.python_version()}")
        print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        print("-------------------")

        await self.bot.change_presence(activity=discord.Streaming(name='Use slash commands.', url='https://www.twitch.tv/pewdiepie'))


    @commands.Cog.listener()
    async def on_slash_command(self, ctx: SlashContext):
        fullCommandName = ctx.name
        split = fullCommandName.split(" ")
        executedCommand = str(split[0])
        print(
            f"Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.guild.id}) by {ctx.author} (ID: {ctx.author.id})"
        )


def setup(bot):
    bot.add_cog(Events(bot))
