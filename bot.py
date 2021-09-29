import json
import os
import platform
import random
import sys

import discord
from discord.ext import tasks
from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext

from helpers import core


if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


'''bot = Bot(
    command_prefix=config["bot_prefix"],
    case_insensitive=True,
    intents=discord.Intents.all(),
    help_command=None,
) '''
bot = core.Bot(
    command_prefix=config["bot_prefix"],
    case_insensitive=True,
    intents=discord.Intents.all(),
    help_command=None,
    config_file = "config.json"
)
bot.load_config()
#print(bot.config)
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

bot.run(config["token"])
