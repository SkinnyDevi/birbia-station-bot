import asyncio
import discord
from os import environ
from discord.ext import commands
from dotenv import load_dotenv

from src.cogs.music import MusicCog
from src.cogs.help import HelpCog
from src.cogs.utility import UtilityCog
from src.cogs.xcog import XCog
from src.core.logger import BirbiaLogger
from src.constants.version import __version__


load_dotenv()

dev_prefix = environ.get("DEV_PREFIX")
prefix = environ.get("PREFIX")

is_dev = environ.get("ENV_IS_DEV") == "True"
bot_prefix = dev_prefix if is_dev else prefix
bot = commands.Bot(command_prefix=f"{bot_prefix} ", intents=discord.Intents.all())


@bot.event
async def on_ready():
    BirbiaLogger.info("Running Cache module with the following config:")
    BirbiaLogger.info(f" - MAX CACHE ENTRIES: {environ.get('MAX_CACHE_ENTRIES')}")

    if is_dev:
        BirbiaLogger.warn("Running bot in development mode")

    BirbiaLogger.info(f"Birbia's Radio Station ({__version__}) is Live!")


cogs = [MusicCog(bot), UtilityCog(bot), XCog(bot), HelpCog(bot)]


async def main():
    bot.remove_command("help")

    await asyncio.gather(*[bot.add_cog(c) for c in cogs])


def start_bot():
    asyncio.run(main())

    try:
        bot.run(environ.get("BOT_DEV_TOKEN" if is_dev else "BOT_TOKEN"))
    except discord.errors.HTTPException:
        BirbiaLogger.error("BLOCKED BY RATE LIMITS")


if __name__ == "__main__":
    start_bot()
