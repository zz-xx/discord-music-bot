import os

import discord
from discord.ext import commands
from discord_slash import SlashCommand

from helpers import core


intents = discord.Intents.default()

intents.bans = False
intents.dm_messages = False
intents.integrations = False
intents.invites = False
intents.reactions = False
intents.typing = False
intents.webhooks = False
intents.presences = True
intents.members = True

bot = core.Bot(
    command_prefix="",
    case_insensitive=True,
    intents=intents,
    help_command=None,
    config_file = "config.json"
)

bot.load_config()
bot.command_prefix = commands.when_mentioned_or(bot.config['bot_prefix'])
bot.load_spotify_client()

slash = SlashCommand(bot, sync_commands=True)


if __name__ == "__main__":

    for dirpath, dirnames, filenames in os.walk("cogs"):
        for filename in filenames:
            if filename.endswith(".py"):
                fullpath = os.path.join(dirpath, filename).split(os.path.sep)
                module = ".".join(fullpath)[:-3]
                print(module)

                try:
                    bot.load_extension(module)
                except Exception as error:
                    print(f"Unable to load {module}: {error}")

bot.run(bot.config['token'])
