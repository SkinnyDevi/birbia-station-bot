import discord
import requests
from discord.ext import commands
from bs4 import BeautifulSoup
from random import randint


class XCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webRoot = 'https://www.nhentai.net/g/'
        self.maxSauce = 342185

    def __sauceCheck(self, sauceID):
        if sauceID is None:
            return -2
        elif len(sauceID) == 6:
            try:
                sauceID = int(sauceID)
                if sauceID <= self.maxSauce:
                    return sauceID
                else:
                    return -1
            except ValueError:
                return -1
        else:
            return -1

    @commands.command(name="doujin", help="Grabs a doujin from the sauce.")
    async def doujin(self, ctx, opt=None, *, sauce=None):
        self.webRoot = 'https://www.nhentai.net/g/'
        self.maxSauce = 342185

        def doujinContents(doujinshi):
            request = requests.get(doujinshi)
            searchAssign = BeautifulSoup(request.text, "html.parser")

            coverUrl = []  # doujinshi Cover
            for img in searchAssign.findAll(
                    'img', attrs={'class': 'lazyload', 'width': '350'}
            ):
                coverUrl.append(img['data-src'])

            doujinTitle = []  # titles
            for span in searchAssign.findAll('span', attrs={'class': 'pretty'}):
                span = list(span)
                for titles in span:
                    doujinTitle.append(titles)

            doujinTags = []  # tags
            for a in searchAssign.findAll('a', attrs={'class': 'tag'}):
                hrefs = a['href']
                if '/tag/' in hrefs:
                    hrefs = list(hrefs)
                    for x in range(5):
                        hrefs.pop(0)
                    hrefs.pop(-1)
                    doujinTags.append("".join(hrefs))

            return coverUrl, doujinTitle, doujinTags

        logo = "https://i.imgur.com/uLAimaY.png"
        if opt is None:
            sauce = randint(1, self.maxSauce)
            doujinSite = self.webRoot + str(sauce)
            contents = doujinContents(doujinSite)
            embed = discord.Embed(
                colour=discord.Colour.red(),
                title="Doujin #{}".format(sauce),
            )
            embed.set_author(name='Doujinshi', icon_url=logo)
            embed.set_thumbnail(url="".join(contents[0]))
            embed.add_field(
                name='Titulo',
                value=contents[1][0],
                inline=False
            )
            embed.add_field(
                name='Titulo Original',
                value=contents[1][1],
                inline=False
            )
            tags = ", ".join(contents[2])
            embed.add_field(
                name='Categorias',
                value=tags,
                inline=False
            )
            embed.add_field(
                name="Doujin Online",
                value=doujinSite,
                inline=False
            )

            await ctx.send(embed=embed)
        elif opt == '-s':
            checker = self.__sauceCheck(sauce)

            if checker == -1:
                await ctx.send("El código para el doujinshi no es valido.")
            elif checker == -2:
                await ctx.send("Como busco el doujinshi sin la salsa?")
            else:
                doujinSite = self.webRoot + str(sauce)
                contents = doujinContents(doujinSite)
                embed = discord.Embed(
                    colour=discord.Colour.red(),
                    title="Doujin #{}".format(sauce),
                )
                embed.set_author(name='Doujinshi', icon_url=logo)
                embed.set_thumbnail(url="".join(contents[0]))
                embed.add_field(
                    name='Titulo',
                    value=contents[1][0],
                    inline=False
                )
                embed.add_field(
                    name='Titulo Original',
                    value=contents[1][1],
                    inline=False
                )
                tags = ", ".join(contents[2])
                embed.add_field(
                    name='Categorias',
                    value=tags,
                    inline=False
                )
                embed.add_field(
                    name="Doujin Online",
                    value=doujinSite,
                    inline=False
                )

                await ctx.send(embed=embed)
