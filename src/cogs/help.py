import discord
from discord.ext import commands

from src.core.logger import BirbiaLogger
from src.constants import version
from src.core.language import BirbiaLanguage


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.__language = BirbiaLanguage.instance()
        BirbiaLogger.info("Initialized Help cog successfully.")

    def __add_version_number(self, embed: discord.Embed) -> discord.Embed:
        embed.add_field(
            name=self.__language.version,
            value=version.__version__,
        )

        return embed

    def __add_to_embed(self, embed: discord.Embed, commands: dict) -> discord.Embed:
        """Adds the commands to the embed."""

        try:
            del commands["description"]
            del commands["title"]
        except KeyError:
            pass
        finally:
            for cmd, v in commands.items():
                embed.add_field(name=cmd, value=v)

        return embed

    def general_help(self) -> discord.Embed:
        """Creates the general help embed."""

        help = discord.Embed(
            title=self.__language.commands,
            description=self.__language.get_cmd_help("general", "description"),
            color=0xFF5900,
        )

        return self.__add_to_embed(
            help, self.__language.help_commands["general"].copy()
        )

    def music_help(self) -> discord.Embed:
        """Creates the music help embed."""

        music = discord.Embed(
            title=self.__language.get_cmd_help("music", "title"),
            description=self.__language.get_cmd_help("music", "description"),
            color=0x8CDDFF,
        )

        return self.__add_to_embed(music, self.__language.help_commands["music"].copy())

    def doujin_help(self) -> discord.Embed:
        """Creates the doujin help embed."""

        doujin = discord.Embed(
            title=self.__language.get_cmd_help("doujin", "title"),
            description=self.__language.get_cmd_help("doujin", "description"),
            color=0xE495FC,
        )

        return self.__add_to_embed(
            doujin, self.__language.help_commands["doujin"].copy()
        )

    def ai_help(self) -> discord.Embed:
        """Creates the AI help embed."""

        ai = discord.Embed(
            title=self.__language.get_cmd_help("ai", "title"),
            description=self.__language.get_cmd_help("ai", "description"),
            color=0xD0D2D6,
        )

        return self.__add_to_embed(ai, self.__language.help_commands["ai"].copy())
    
    def utility_help(self) -> discord.Embed:
        """Creates the Utility help embed."""

        utility = discord.Embed(
            title=self.__language.get_cmd_help("ai", "title"),
            description=self.__language.get_cmd_help("ai", "description"),
            color=0x80ff80,
        )

        return self.__add_to_embed(utility, self.__language.help_commands["utility"].copy())

    @commands.command(name="help", help="Displayes all of Birbia's available actions.")
    async def help(self, ctx: commands.Context, category: str = None):
        """Displays the help embed."""

        match category:
            case "music":
                embed = self.music_help()
            case "doujin":
                embed = self.doujin_help()
            case "ai":
                embed = self.ai_help()
            case "utility":
                embed = self.utility_help()
            case _:
                embed = self.general_help()

        await ctx.send(embed=self.__add_version_number(embed))
