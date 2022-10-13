import discord
from discord.ext import commands


class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.CMDS = [
            ["help", "Displayes all of Birbia's available actions."],
            ["play", "Play audio through Birbia's most famous radio station."],
            ["pause", "Pause Birbia's radio station."],
            ["resume", "Resume the audio frozen in Birbia's radio station."],
            ["skip", "Skip that one song you don't like from Birbia's radio station."],
            ["queue [q]", "Display Birbia's radio station pending play requests."],
            ["clear", "Removes every current request from Birbia's radio station."],
            ["leave [stop]", "Make Birbia's Radio Station stop for the day."],
            ["now", "Display the radio's currently playing song."]
        ]

    @commands.command(name="help", help="Displayes all of Birbia's available actions.")
    async def help(self, ctx):
        help = discord.Embed(
            title="Commands [aliases]",
            description="All available commands provided by Birbia.",
            color=0xff5900
        )

        for cmd in self.CMDS:
            help.add_field(name=cmd[0], value=cmd[1])

        await ctx.send(embed=help)
