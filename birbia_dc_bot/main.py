import os
import asyncio
import discord

from discord.ext import commands

from cogs.music import music_cog
from cogs.help import help_cog

bot = commands.Bot(command_prefix="birbia ", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Birbia's Radio Station is Live!")


async def main():
    bot.remove_command("help")

    await bot.add_cog(music_cog(bot))
    await bot.add_cog(help_cog(bot))


asyncio.run(main())

try:
    bot.run(os.environ.get("TOKEN"))
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")