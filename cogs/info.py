from datetime import datetime
import json
import os
import psutil
from random import choice
import sys

import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

#really didn't want to do this
GUILD_IDS = [435683837641621514]


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="info",
        description="Get some useful (or not) information about the bot.",
        guild_ids=GUILD_IDS,
    )
    async def info(self, ctx: SlashContext):
        """
        Get some information about the bot.
        """

        app_info = await ctx.bot.application_info()
        process = psutil.Process(os.getpid())

        description = (
            "<:info:483340220859678763> [**Bot Info**](https://bot.x86.fun/)\n"
        )
        description += f"`{ctx.bot.user.name} is a simple and modular Discord bot written in Python.`\n\u200b\n"

        description += "<:server:483088255403687948> **Server**\n"
        description += "Click [**here**](https://discord.gg/rzYybFd)\n\u200b\n"

        # this is lazy implementation, will change it later
        description += "<:version:483351547489681409> **Version**\n "
        description += "`0.0.0 alpha`\n\u200b\n"

        description += "<:cpu:483063252331528192> **CPU Usage**\n"
        description += f"`{psutil.cpu_percent()} %`\n\u200b\n"

        description += "<:RAM:483083485171548162> **RAM Usage**\n"
        description += f"`{psutil.virtual_memory()[2]} %`\n\u200b\n"

        description += "<:process:483340180405616660> **Process Memory**\n"
        description += f"`{round(process.memory_info()[0]/1048576.0, 2)} MB`\n\u200b\n"

        description += "<:python:483063299416784931> **Python**\n"
        description += f"`{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}`\n\u200b\n"

        description += "<:discord:483063472767238164> **discord.py**\n"
        description += f"`{discord.__version__}`\n\u200b\n"

        description += "<:owner:483088166711066644> **Owner**\n"
        description += f"<@{app_info.owner.id}>\n\u200b\n"

        description += "<:ping:483063277656735744> **Ping**\n"
        description += f"`{round(ctx.bot.latency*1000, 2)} ms`\n\u200b\n"

        # description += '<:uptime:483098847581569034> **Uptime**\n'
        # description += f'`{(datetime.now() - ctx.bot.startTime).days} days {(datetime.now() - ctx.bot.startTime).seconds//300} hours {((datetime.now() - ctx.bot.startTime).seconds//60)%60} minutes and {divmod((datetime.now() - ctx.bot.startTime).seconds, 60)[1]} seconds`\n\u200b\n'

        description += "<:guild:483063322460160000> **Guilds**\n"
        description += f"`{len(ctx.bot.guilds)}`\n\u200b\n"

        description += "<:user:483063436029198336> **Users**\n"
        description += (
            f"`{sum(not member.bot for member in ctx.bot.get_all_members())}`\n\u200b\n"
        )

        description += "<a:bot:483065552559144990> **Commands**\n"
        description += f"`{len(ctx.bot.commands)}`\n\u200b\n"

        description += "<:shard:483063413635809311> **Shards**\n"
        description += f"`{ctx.bot.shard_count}`\n\u200b\n"

        description += "<:notice:483340299578507264> **Announcements**\n"
        # description += f"```tex\n$   {ctx.bot.announcements}\n```"
        description += f"```tex\n$   {'ctx.bot.announcements'}\n```"

        color = "".join([choice("0123456789ABCDEF") for x in range(6)])
        color = int(color, 16)
        embed = discord.Embed(color=discord.Color(value=color))
        embed.description = description
        embed.set_thumbnail(url=ctx.bot.user.avatar_url_as(format="png", size=256))
        embed.set_footer(
            text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}",
            icon_url=ctx.author.avatar_url,
        )

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="serverinfo",
        description="Get some useful (or not) information about the server.",
        guild_ids=GUILD_IDS,
    )
    async def serverinfo(self, ctx: SlashContext):
        """Display information about the current guild, such as owner, region, emojis, and roles."""

        guild = ctx.guild

        color = "".join([choice("0123456789ABCDEF") for x in range(6)])
        color = int(color, 16)
        embed = discord.Embed(title=guild.name, color=discord.Color(value=color))
        embed.description = str(guild.id)

        embed.set_thumbnail(url=guild.icon_url)

        embed.add_field(name="Owner", value=str(guild.owner))

        embed.add_field(name="Members", value=len(ctx.guild.members))

        embed.add_field(name="Text channels", value=len(guild.text_channels))
        embed.add_field(name="Voice channels", value=len(guild.voice_channels))
        embed.add_field(name="Custom emojis", value=len(guild.emojis) or None)
        embed.add_field(name="Custom roles", value=len(guild.roles) - 1 or None)
        embed.add_field(name="Region", value=str(guild.region))
        embed.add_field(name="Created at", value=guild.created_at.ctime())

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="userinfo",
        description="Get some useful (or not) information about the server.",
        guild_ids=GUILD_IDS,
    )
    async def userinfo(self, ctx: SlashContext):
        """Display information about a user, such as status and roles."""

        user = ctx.author
        embed = discord.Embed(title=f"{str(user)}")
        embed.colour = user.color

        embed.description = str(user.id)
        if user.activity:
            embed.description += f" | Playing **{user.activity}**"

        embed.set_thumbnail(url=user.avatar_url_as(format="png", size=128))

        embed.add_field(name="Nickname", value=user.nick)
        embed.add_field(name="Bot user?", value="Yes" if user.bot else "No")

        # This is a bit awkward. Basically we don't want the bot to just say Dnd.
        if user.status.name == "dnd":
            status = "Do Not Disturb"
        else:
            status = user.status.name.capitalize()
        embed.add_field(name="Status", value=status)

        embed.add_field(name="Color", value=str(user.color))

        embed.add_field(name="Joined guild at", value=user.joined_at.ctime())
        embed.add_field(name="Joined Discord at", value=user.created_at.ctime())

        # This is crap.
        roles = ", ".join((role.name for role in user.roles if not role.is_default()))[
            :1024
        ]
        if roles:
            embed.add_field(name="Roles", value=roles, inline=False)

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="ping",
        description="Check if the bot is alive.",
        guild_ids=GUILD_IDS,
    )
    async def ping(self, context: SlashContext):
        """
        Check if the bot is alive.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x42F56C,
        )
        await context.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
