import os
import asyncio
import discord

from discord.ext import commands

from cogs.music import music_cog
from cogs.help import help_cog

isDev = False
prefix = "birbia-beta " if isDev else "birbia "
bot = commands.Bot(command_prefix=prefix,
                   intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Birbia's Radio Station is Live!")


async def main():
    bot.remove_command("help")

    await bot.add_cog(music_cog(bot))
    await bot.add_cog(help_cog(bot))


asyncio.run(main())

try:
    bot.run(os.environ.get("POETRY_TOKEN" if not isDev else "POETRY_DEV_TOKEN"))
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\n\n\n")
