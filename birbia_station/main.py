import os
import asyncio
import discord

from discord.ext import commands
from dotenv import load_dotenv

from .cogs.music import MusicCog
from .cogs.help import HelpCog
from .cogs.utility import UtilityCog
from .cogs.xcog import XCog

from .core.logger import BirbiaLogger

load_dotenv()

is_dev = True
prefix = "birbia-beta " if is_dev else "birbia "
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())


@bot.event
async def on_ready():
    BirbiaLogger.info("Birbia's Radio Station is Live!")


cogs = [MusicCog(bot), UtilityCog(bot), XCog(bot), HelpCog(bot)]


async def main():
    bot.remove_command("help")

    await asyncio.gather(*[bot.add_cog(c) for c in cogs])


def start_bot():
    asyncio.run(main())

    try:
        bot.run(os.environ.get("POETRY_DEV_TOKEN" if is_dev else "POETRY_TOKEN"))
    except discord.errors.HTTPException:
        BirbiaLogger.error("BLOCKED BY RATE LIMITS")
