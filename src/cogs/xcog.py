import discord
from discord.ext import commands
from random import randint

from src.core.doujin.scraper import DoujinWebScraper


class XCog(commands.Cog):
    LOGO = "https://i.imgur.com/uLAimaY.png"
    MIN_SAUCE = 2

    def __init__(self, bot):
        self.bot = bot

        self.dscraper = DoujinWebScraper()
        self.MAX_SAUCE = self.dscraper.doujin_maxcount()

    def __sauceCheck(self, sauce_id) -> int:
        """
        Checks whether the sauce is valid.


        returns -1 if it exceeds the MAX_SAUCE. Will redirect to official site to try and find the original.

        returns -2 if sauce is lower than MIN_SAUCE. Normally MIN_SAUCE = 2.

        returns -3 if it cannot translate the argument to a valid int sauce.
        """

        if sauce_id is None:
            return None

        try:
            sauce_id = int(sauce_id)

            if sauce_id < self.MIN_SAUCE:
                return -2

            if sauce_id > self.MAX_SAUCE:
                return -1

            return sauce_id
        except ValueError:
            return -3

    def doujin_embed_maker(self, sauce: int) -> discord.Embed:
        """
        Creates a Discord embed with the doujin's information, thumbnail and link.
        """

        doujin_data = self.dscraper.doujin(sauce)

        embed = discord.Embed(
            color=0xE495FC,
            title=f"Doujin #{sauce}",
        )

        embed.set_author(name="Doujinshi", icon_url=self.LOGO)
        # TODO: assert that covers display correctly
        embed.set_thumbnail(url=doujin_data.cover)

        embed.add_field(name="Title", value=doujin_data.titles["english"], inline=False)

        if doujin_data.titles["original"] != "":
            embed.add_field(
                name="Original Title",
                value=doujin_data.titles["original"],
                inline=False,
            )

        if len(doujin_data.tags) != 0:
            embed.add_field(
                name="Categories", value=", ".join(doujin_data.tags), inline=False
            )

        embed.add_field(name="Pages", value=doujin_data.pages, inline=False)

        embed.add_field(name="Doujin Online", value=doujin_data.url, inline=False)

        return embed

    async def send_not_found(self, ctx: commands.Context, sauce: int):
        """
        Redirects the user with a Discord embed to an official link if sauce not found at source.
        """

        embed = discord.Embed(colour=discord.Colour.red(), title=f"Doujin #{sauce}")

        embed.add_field(
            name="We couldn't find your doujin in our sources, but here's the official link:",
            value=self.dscraper.WEB_ROOT + str(sauce),
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command(name="doujin", help="Grabs a doujin from the sauce.")
    async def doujin(self, ctx: commands.Context, opt=None, *, sauce=None):
        """
        Gets a random doujin from the source and retrieves it's information.

        Arguments:
        * -s: specify doujin to retrieve with a specific sauce.
                * Example: 'doujin -s 177013'
        """

        self.MAX_SAUCE = self.dscraper.doujin_maxcount()

        if opt is not None:
            if opt == "-s":
                if sauce is None:
                    return await ctx.send(
                        "You didn't specify the sauce. Did you want ketchup?"
                    )

                match self.__sauceCheck(sauce):
                    case -3:
                        return await ctx.send("Sauce is invalid.")
                    case -2:
                        return await ctx.send("There's nothing lower than 2.")
                    case -1:
                        return await self.send_not_found(ctx, sauce)
            else:
                return await ctx.send(
                    "Unknown option. Use ***-s*** for a specific doujin."
                )
        else:
            sauce = randint(self.MIN_SAUCE, self.MAX_SAUCE)

        doujin = self.doujin_embed_maker(sauce)
        await ctx.send(embed=doujin)
