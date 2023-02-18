import os
import asyncio
import discord

from discord.ext import commands

from .cogs.music import MusicCog
from .cogs.help import HelpCog
from .cogs.utility import UtilityCog
from .cogs.xcog import XCog

isDev = False
prefix = "birbia-beta " if isDev else "birbia "
bot = commands.Bot(command_prefix=prefix,
                   intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Birbia's Radio Station is Live!")


async def main():
    bot.remove_command("help")

    await bot.add_cog(MusicCog(bot))
    await bot.add_cog(UtilityCog(bot))
    await bot.add_cog(XCog(bot))
    await bot.add_cog(HelpCog(bot))


def start_bot():
    asyncio.run(main())

    try:
        bot.run(os.environ.get(
            "POETRY_DEV_TOKEN" if isDev else "POETRY_TOKEN"))
    except discord.errors.HTTPException:
        print("\n\n\nBLOCKED BY RATE LIMITS\n\n\n")


start_bot()
