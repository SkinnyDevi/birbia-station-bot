import discord
import pkg_resources
from discord.ext import commands

from ..constants import help_commands as cmds


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def __add_version_number(self, embed: discord.Embed) -> discord.Embed:
        embed.add_field(
            name="Version",
            value=pkg_resources.get_distribution("birbia-station-bot").version,
        )

        return embed

    def __add_to_embed(self, embed: discord.Embed, commands: dict) -> discord.Embed:
        for cmd in commands.keys():
            embed.add_field(name=cmd, value=commands[cmd])

        return embed

    def general_help(self) -> discord.Embed:
        help = discord.Embed(
            title="Commands",
            description="All available command categories provided by Birbia.\nUse 'birbia [category] to see all commands from that category.",
            color=0xFF5900,
        )

        return self.__add_to_embed(help, cmds.GENERAL_CMDS)

    def music_help(self) -> discord.Embed:
        music = discord.Embed(
            title="Music Commands [aliases]",
            description="Available commands to control Birbia's Radio Station.",
            color=0x8CDDFF,
        )

        return self.__add_to_embed(music, cmds.MUSIC_CMDS)

    def doujin_help(self) -> discord.Embed:
        doujin = discord.Embed(
            title="Doujin Commands",
            description="Search and discover new doujins.",
            color=0xE495FC,
        )

        return self.__add_to_embed(doujin, cmds.DOUJIN_CMDS)

    @commands.command(name="help", help="Displayes all of Birbia's available actions.")
    async def help(self, ctx: commands.Context, category: str = None):
        match category:
            case "music":
                embed = self.music_help()
            case "doujin":
                embed = self.doujin_help()
            case _:
                embed = self.general_help()

        await ctx.send(embed=self.__add_version_number(embed))
