import discord
from discord.ext import commands
from random import randint

from ..utils.scraper_bypass import DelayedScraper


class XCog(commands.Cog):
    Logo = "https://i.imgur.com/uLAimaY.png"
    MinSauce = 2

    def __init__(self, bot):
        self.bot = bot

        self.dscraper = DelayedScraper()
        self.MaxSauce = self.dscraper.webscrape_doujin_maxcount()

    def __sauceCheck(self, sauceID) -> int:
        """
        Checks whether the sauce is valid.


        returns -1 if it exceeds the MaxSauce. Will redirect to official site to try and find the original.

        returns -2 if sauce is lower than MinSauce. Normally MinSauce = 2.

        returns -3 if it cannot translate the argument to a valid int sauce.
        """

        if sauceID is None:
            return None

        try:
            sauceID = int(sauceID)

            if sauceID < self.MinSauce:
                return -2

            if sauceID > self.MaxSauce:
                return -1

            return sauceID
        except ValueError:
            return -3

    def doujin_embed_maker(self, sauce: int) -> discord.Embed:
        """
        Creates a Discord embed with the doujin's information, thumbnail and link.
        """

        doujinData = self.dscraper.webscrape_doujin(sauce)

        embed = discord.Embed(
            colour=discord.Colour.red(),
            title=f"Doujin #{sauce}",
        )

        embed.set_author(name='Doujinshi', icon_url=self.Logo)
        embed.set_thumbnail(url=doujinData['cover'])

        embed.add_field(
            name='Title',
            value=doujinData['titles']['english'],
            inline=False
        )

        if doujinData['titles']['original'] != "":
            embed.add_field(
                name='Original Title',
                value=doujinData['titles']['original'],
                inline=False
            )

        if len(doujinData['tags']) != 0:
            embed.add_field(
                name='Categories',
                value=", ".join(doujinData['tags']),
                inline=False
            )

        embed.add_field(
            name="Pages",
            value=doujinData['pages'],
            inline=False
        )

        embed.add_field(
            name="Doujin Online",
            value=doujinData['url'],
            inline=False
        )

        return embed

    async def send_not_found(self, ctx: commands.Context, sauce: int):
        """
        Redirects the user with a Discord embed to an official link if sauce not found at source.
        """

        embed = discord.Embed(
            colour=discord.Colour.red(),
            title=f"Doujin #{sauce}"
        )

        embed.add_field(
            name="We couldn't find your doujin in our sources, but here's the official link:",
            value=self.dscraper.WebRoot + str(sauce),
            inline=False
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

        self.MaxSauce = self.dscraper.webscrape_doujin_maxcount()

        if opt is not None:
            if opt == '-s':
                if sauce is None:
                    return await ctx.send("You didn't specify the sauce. Did you want ketchup?")

                if self.__sauceCheck(sauce) == -3:
                    return await ctx.send("Sauce is invalid.")

                if self.__sauceCheck(sauce) == -1:
                    return await self.send_not_found(ctx, sauce)

                if self.__sauceCheck(sauce) == -2:
                    return await ctx.send("There's nothing lower than 2.")
            else:
                return await ctx.send("Unknown option. Use ***-s*** for a specific doujin.")
        else:
            sauce = randint(self.MinSauce, self.MaxSauce)

        doujin = self.doujin_embed_maker(sauce)
        await ctx.send(embed=doujin)
