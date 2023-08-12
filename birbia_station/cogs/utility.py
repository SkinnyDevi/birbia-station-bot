import time
from discord.ext import commands

from ..core.logger import BirbiaLogger


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name="ping", help="Returns sender's ping in ms.")
    async def ping(self, ctx):
        """
        Returns sender's ping in ms.
        """

        await ctx.send(f"Pong - {round(self.bot.latency * 1000)}ms")

    @commands.command(
        name="invite", help="Generates invites, default = 1 use per invite."
    )
    async def invite(self, ctx: commands.Context, uses: int = 1):
        """
        Generates invites, default = 1 use per invite.
        """

        uses = int(uses)

        if uses < 1:
            return await ctx.send("Invite uses cannot be 0.")

        invite = await ctx.channel.create_invite(max_uses=uses)
        invite_send = f"Invite generated. \nMax uses: {uses}\n{invite}"
        await ctx.send(invite_send)
        BirbiaLogger.info(
            f"Invite generated with {uses} uses for {ctx.message.author}."
        )

    @commands.command(name="purge", help="Removes X number of messages recursively,")
    async def purge(self, ctx: commands.Context, nmessages: int = None):
        """
        Deletes recursively n number of messages.
        """

        if nmessages is None:
            return await ctx.send("You must specify the number of messages to purge.")

        channel = ctx.channel

        await channel.purge(limit=nmessages + 1)
        await ctx.send(f"Purged {nmessages} messages.")

        time.sleep(2)
        await channel.purge(limit=1, check=lambda m: m.author == self.bot.user)
