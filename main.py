from discord.ext import commands
from decouple import config

from cogs.music import music_cog
from cogs.help import help_cog

bot = commands.Bot(command_prefix="birbia ")
bot.remove_command("help")

bot.add_cog(music_cog(bot))
bot.add_cog(help_cog(bot))

print("Birbia's Radio Station is Live!")
bot.run(config("TOKEN"))
