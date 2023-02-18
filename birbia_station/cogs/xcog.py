import discord
import requests
from discord.ext import commands
from random import randint

from ..utils.scraper_bypass import DelayedScraper


class XCog(commands.Cog):
    Logo = "https://i.imgur.com/uLAimaY.png"
    MaxSauce = 342185

    def __init__(self, bot):
        self.bot = bot

        self.dscraper = DelayedScraper()

    def __sauceCheck(self, sauceID):
        if sauceID is None:
            return -2
        elif len(sauceID) == 6:
            try:
                sauceID = int(sauceID)
                if sauceID <= self.MaxSauce:
                    return sauceID
                else:
                    return -1
            except ValueError:
                return -1
        else:
            return -1

    def doujinEmbedMaker(self, sauce: int):
        doujinData = self.dscraper.webscrape_doujin(sauce)

        embed = discord.Embed(
            colour=discord.Colour.red(),
            title="Doujin #{}".format(sauce),
        )

        embed.set_author(name='Doujinshi', icon_url=self.Logo)
        embed.set_thumbnail(url=doujinData['cover'])

        embed.add_field(
            name='Title',
            value=doujinData['titles']['english'],
            inline=False
        )

        if doujinData['titles']['japanese'] != "":
            embed.add_field(
                name='Original Title',
                value=doujinData['titles']['original'],
                inline=False
            )

        tags = ", ".join(doujinData['tags'])
        embed.add_field(
            name='Categories',
            value=tags,
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

    @commands.command(name="doujin", help="Grabs a doujin from the sauce.")
    async def doujin(self, ctx, opt=None, *, sauce=None):
        if opt is None:
            sauce = randint(1, self.MaxSauce)

        elif opt == '-s':
            checker = self.__sauceCheck(sauce)

            if checker == -1:
                return await ctx.send("Doujinshi sauce not found.")

        embed = self.doujinEmbedMaker(sauce)
        await ctx.send(embed=embed)
