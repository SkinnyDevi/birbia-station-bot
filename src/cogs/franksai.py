import asyncio
import discord
import hashlib
from discord.ext import commands

from src.api.franks.FranksAPI import FranksAPI
from src.api.franks.FranksChatInstance import FranksChatInstance, FranksChatID
from src.core.language import BirbiaLanguage
from src.core.logger import BirbiaLogger


class FranksAICog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.__language = BirbiaLanguage.instance()
        chat_name = f"{self.__language.get_prefix()}_COMMON_CHAT"
        self.__COMMON_USER = discord.User(
            data={
                "id": self.__consistent_hash(chat_name.lower()),
                "username": chat_name.lower(),
                "discriminator": chat_name.lower(),
                "bot": False,
                "avatar": "",
            },
            state=None,
        )

        self.__api = FranksAPI()
        self.__instances: dict[int, FranksChatInstance] = {}
        BirbiaLogger.info("Initialized AI cog successfully.")

    def __consistent_hash(self, s: str):
        """Creates a consistent hash for each common chat."""

        return int(hashlib.md5(s.encode()).hexdigest(), 16)

    def __delete_chat(self, user: discord.User):
        """
        Deletes the chat with the AI from the API.

        Returns:
        - [0] Success.
        - [-1] An error occurred while trying to get the sessions.
        - [-2] No chat found to close.
        """

        session_id: FranksChatID | None = None
        if user.id in self.__instances.keys():
            instance = self.__instances[user.id]
            instance.close_chat()
            session_id = instance.session_id
        else:
            sessions = self.__api.get_sessions()

            if sessions is None:
                return -1  # An error occurred while trying to get the sessions.

            for session in sessions.results:
                if session.name == str(user.id):
                    session_id = session.uid
                    break

        if session_id is None:
            return -2  # No chat found to close.

        output = self.__api.delete_session(session_id)
        
        if output is None:
            BirbiaLogger.warn("Chat closed, but no delete response was received.")
            return 0
        elif output.success:
            if user.id in self.__instances.keys():
                del self.__instances[user.id]
            return 0

        return -1

    def __new_chat(self, user: discord.User):
        """
        Creates a new chat with the AI.

        Returns:
        - [0] Success.
        - [-1] An error occurred while trying to create a new chat.
        """

        output = self.__delete_chat(user)
        if output == -1:
            return -1

        session = self.__api.create_session(str(user.id))
        if session is None:
            return -1  # An error occurred while trying to create a new chat.

        self.__instances[user.id] = FranksChatInstance(user, session.uid)
        self.__instances[user.id].ext_on_close = lambda inst_user: self.__delete_chat(
            inst_user
        )

        return 0

    def clean_query(self, message: discord.Message):
        """
        Removes the username from the message.
        """

        msg = message.clean_content.replace(f"@{self.bot.user.name}", "").strip()
        BirbiaLogger.debug(f"Message: {msg}")

        return msg

    async def __ask(
        self, ctx: commands.Context = None, message: discord.Message = None, *args
    ):
        """Asks the AI a question."""

        if ctx is None and message is None:
            raise ValueError("Either ctx or message must be provided.")

        async def send_msg(msg: str):
            if ctx is not None:
                post = await ctx.reply(msg)
            else:
                post = await message.reply(msg)

            return post

        if ctx is not None:
            # The query is made in a private chat.
            requester = ctx.author
            chat_author = requester
            ai_query = " ".join(args)
        else:
            # The query is made in the common chat.
            chat_author = self.__COMMON_USER
            requester = message.author
            ai_query = self.clean_query(message)

        instance_id = chat_author.id
        if instance_id not in self.__instances.keys():
            output = self.__new_chat(chat_author)
            if output != 0:
                await send_msg(self.__language.ai_init_error)
                return -1

        instance = self.__instances[instance_id]
        if not instance.live:
            await instance.start_chat()

        if not instance.can_ask():
            await send_msg(self.__language.ai_not_ready)
            return -1

        prcs_msg = await send_msg(self.__language.ai_processing)
        msg_parts = await instance.send_message(ai_query, requester)
        if msg_parts == -1:
            await send_msg(self.__language.ai_error)
            return -1

        await prcs_msg.edit(content=msg_parts.pop(0))

        async def coro_send(msg: str):
            from random import uniform

            await send_msg(msg)
            await asyncio.sleep(uniform(0.5, 2.5))

        coros = [coro_send(part) for part in msg_parts]
        if len(coros) > 0:
            await asyncio.gather(*coros)

        return 0

    async def __close_chat(self, ctx: commands.Context, user: discord.User):
        """Closes the chat with the AI."""

        output = self.__delete_chat(user)

        match output:
            case -1:
                await ctx.send(self.__language.ai_chat_close_error)
            case -2:
                await ctx.send(self.__language.ai_chat_closed_not_found)
            case 0:
                await ctx.send(self.__language.ai_chat_closed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Overrides the on_message event to allow the AI to answer questions upon mentioned. This query is made in the common chat."""

        if self.bot.user in message.mentions:
            await self.__ask(None, message)

    @commands.command(name="ask", help="Ask a question to an AI.")
    async def gptask(self, ctx: commands.Context, *args):
        """Ask a question to an AI. This query is made in a privat user chat."""

        await self.__ask(ctx, None, *args)

    @commands.command(name="reset", help="Closes the common chat with the AI.")
    async def gptcommonreset(self, ctx: commands.Context):
        """Closes the common chat with the AI."""

        await self.__close_chat(ctx, self.__COMMON_USER)

    @commands.command(name="newchat", help="Closes the chat with the AI.")
    async def gptreset(self, ctx: commands.Context):
        """Closes the chat with the AI."""

        await self.__close_chat(ctx, ctx.author)
