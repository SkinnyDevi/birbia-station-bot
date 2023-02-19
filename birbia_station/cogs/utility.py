import discord
import time
from discord.ext import commands


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name="ping", help="Returns sender's ping in ms.")
    async def ping(self, ctx):
        """
        Returns sender's ping in ms
        """

        await ctx.send(f'Pong - {round(self.bot.latency * 1000)}ms')

    @commands.command(name="invite", help="Generates invites, default = 1 use per invite.")
    async def invite(self, ctx: commands.Context, uses: int):
        """
        Generates invites, default = 1 use per invite
        """

        uses = int(uses)

        if uses < 1:
            return await ctx.send("Invite uses cannot be 0.")

        invite = await ctx.channel.create_invite(max_uses=uses)
        inviteSend = f"Invite generated. \nMax uses: {uses}\n{invite}"
        await ctx.send(inviteSend)
        print(
            f'Invite generated with {uses} uses for {ctx.message.author} max uses.')

    @commands.command(name="purge", help="Removes X number of messages recursively,")
    async def purge(self, ctx: commands.Context, nmessages: int):
        channel: discord.TextChannel = ctx.channel

        def is_bot(m: discord.Message):
            return m.author == self.bot.user

        await channel.purge(limit=nmessages)
        await ctx.send(f'Purged {nmessages} messages.')

        time.sleep(3)
        await channel.purge(limit=1, check=is_bot)
