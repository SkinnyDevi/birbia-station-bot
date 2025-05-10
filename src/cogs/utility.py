import time
from discord.ext import commands

from src.core.logger import BirbiaLogger
from src.core.language import BirbiaLanguage


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.__language = BirbiaLanguage.instance()

    @commands.command(name="ping", help="Returns sender's ping in ms.")
    async def ping(self, ctx):
        """
        Returns sender's ping in ms.
        """

        await ctx.send(f"Pong! - {round(self.bot.latency * 1000)}ms")

    @commands.command(
        name="invite", help="Generates invites, default = 1 use per invite."
    )
    async def invite(self, ctx: commands.Context, uses: str = "1"):
        """
        Generates invites, default = 1 use per invite.
        """

        uses = int(uses)

        if uses < 1:
            return await ctx.send(self.__language.invite_zero)

        invite = await ctx.channel.create_invite(max_uses=uses)
        await ctx.send(self.__language.invite_gen.format(uses=uses, invite=invite))
        BirbiaLogger.info(
            f"Invite generated with {uses} uses for {ctx.message.author}."
        )

    @commands.command(name="purge", help="Removes X number of messages recursively,")
    async def purge(self, ctx: commands.Context, nmessages: int = None):
        """
        Deletes recursively n number of messages.
        """

        if nmessages is None:
            return await ctx.send(self.__language.purge_amount)

        channel = ctx.channel

        await channel.purge(limit=nmessages + 1)
        await ctx.send(self.__language.purge_success.format(nmsgs=nmessages))

        time.sleep(2)
        await channel.purge(limit=1, check=lambda m: m.author == self.bot.user)
