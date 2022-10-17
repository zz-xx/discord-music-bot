import asyncio

import discord

from core.bot import Bot
from cogs.audio import context_menu_commands

# t
bot = Bot(intents=discord.Intents.all())


async def main():
    await bot.load_extension("cogs.audio.disconnect")
    await bot.load_extension("cogs.audio.listeners")
    await bot.load_extension("cogs.audio.play")
    await bot.load_extension("cogs.audio.skip")
    await bot.load_extension("cogs.audio.queue")
    await bot.load_extension("cogs.events")
    
    context_menu_commands.init(bot)


asyncio.run(main())

bot.run(bot.config["token"])
