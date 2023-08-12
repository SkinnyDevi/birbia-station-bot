import discord
import asyncio
import os

from discord.ext import commands

from ..core.logger import BirbiaLogger
from ..core.music.audiosearchers.youtube import YtAudioSearcher
from ..core.music.birbia_queue import BirbiaQueue, BirbiaAudio


class MusicCog(commands.Cog):
    # fallback
    DISCONNECT_DELAY = 600  # 300s = 5 min
    CMD_TIMEOUT = 2  # seconds

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vc: discord.VoiceClient = None
        self.allow_cmd = True
        self.music_queue = BirbiaQueue()
        self.audio_search: YtAudioSearcher = YtAudioSearcher()

        self.started_quit_timeout = False

        MusicCog.DISCONNECT_DELAY = int(
            os.environ.get("DISCONNECT_DELAY")
        )  # 300s = 5 min
        MusicCog.CMD_TIMEOUT = int(os.environ.get("CMD_TIMEOUT"))  # seconds

        BirbiaLogger.info("Running Music Cog with following config:")
        BirbiaLogger.info(f" - DISCONNECT DELAY: {MusicCog.DISCONNECT_DELAY}")
        BirbiaLogger.info(f" - CMD TIMEOUT: {MusicCog.CMD_TIMEOUT}")

    async def __disconnect(self):
        """
        Disconnects the bot from the voice channel by playing an audio file.
        """
        if len(self.vc.channel.members) > 0 and not self.vc.is_playing():
            try:
                disconnect_audio = discord.FFmpegOpusAudio(
                    os.getcwd() + "birbia_station/audios/vc_disconnect.mp3",
                    **BirbiaAudio.FFMPEG_CFG,
                )

                self.vc.play(disconnect_audio)

                while self.vc.is_playing():
                    await asyncio.sleep(0.75)

            except Exception as error:
                BirbiaLogger.error("Could not play disconnect audio.", error)

        await self.vc.disconnect()

        self.music_queue.reset()
        self.vc = None
        self.started_quit_timeout = False

    async def __timeout_quit(self):
        """
        Creates a timer when connected to voicechat

        If it doesn't play anything within the {DISCONNECT_DELAY}, it will automatically
        leave the voicechat.
        """
        if self.started_quit_timeout:
            return

        time = 0
        self.started_quit_timeout = True

        is_vc_connected = True
        while is_vc_connected:
            if self.vc is None or not self.vc.is_connected():
                is_vc_connected = False
                continue

            await asyncio.sleep(1)

            time += 1

            if self.vc is not None and self.vc.is_playing() and not self.vc.is_paused():
                time = 0
            if time >= MusicCog.DISCONNECT_DELAY:
                await self.__disconnect()
                is_vc_connected = False

    async def __command_timeout(self):
        """
        A timeout of 2 seconds to wait for each command.
        """
        self.allow_cmd = False
        await asyncio.sleep(MusicCog.CMD_TIMEOUT)
        self.allow_cmd = True

    async def __timeout_warn(self, ctx: commands.Context):
        """
        Warns the user if they are still in command timeout.
        """

        await ctx.send(
            "Birbia warns you to wait at least 2 seconds before running the next command."
        )

    def __queue_next(self):
        """
        Queues another audio for playback.
        """

        if self.music_queue.queue_length() == 0:
            return

        next_song = self.music_queue.next()
        self.vc.play(next_song.pcm_audio, after=lambda e=None: self.__queue_next())

    async def __play_audio(self, ctx: commands.Context):
        """
        Plays the next audio from the queue to the voicechat.
        """

        up_next = self.music_queue.up_next()
        if self.vc is None or not self.vc.is_connected():
            self.vc = await up_next.get_requester_vc().connect()

            if self.vc is None:
                return await ctx.send(
                    "Birbia could not enter your voice chat. This is illegal. We will take action."
                )
        else:
            await self.vc.move_to(up_next.get_requester_vc())

        next_song = self.music_queue.next()
        self.vc.play(next_song.pcm_audio, after=lambda e=None: self.__queue_next())

    @commands.command(
        name="play", help="Play audio through Birbia's most famous radio station."
    )
    async def play(self, ctx: commands.Context, *args):
        """
        Bot command used to search and play a song/audio/video/short from a supported platform.
        """

        song_query = " ".join(args)

        if song_query == "" or song_query == " ":
            return await ctx.send(
                "Don't play with Birbia. What is that you want to listen to?"
            )

        requester_in_voice = ctx.author.voice

        if requester_in_voice is None:
            self.__command_timeout(ctx)
            return await ctx.send(
                "To use Birbia Radio, please connect to a voice channel first."
            )

        if not self.allow_cmd:
            return await self.__timeout_warn(ctx)

        await ctx.send("Birbia is sending it's hawks to fetch your audio...")

        # As of now, only search on YT
        # Later, a URl detecter will be implemented
        # to allow the handling and delegation of correct links
        # to it's respective OnlineAudioSearcher class

        audio_obj = self.audio_search.search(song_query)

        if audio_obj is None:
            return await ctx.send(
                "Birbia sent out it's fastest eagles, but could not get your audio back. Try again!"
            )

        try:
            audio_obj.set_requester_vc(requester_in_voice.channel)
            self.music_queue.add_to_queue(audio_obj)

            new_audio = discord.Embed(title="Added to radio queue!", color=0xFF5900)
            new_audio.add_field(
                name=f"{audio_obj.title}",
                value=f"{audio_obj.url} - {audio_obj.get_duration()}",
            )
            await ctx.send(embed=new_audio)

            if self.vc is None or not self.vc.is_playing():
                await self.__play_audio(ctx)

            await self.__command_timeout()
            await self.__timeout_quit()
        except Exception as error:
            BirbiaLogger.error(
                "An error ocurred while trying to play the requested audio", error
            )

    @commands.command(name="pause", help="Pause Birbia's radio station.")
    async def pause(self, ctx: commands.Context):
        """
        Pauses the current audio playing.
        """

        if not self.allow_cmd:
            await self.__timeout_warn(ctx)

        if self.vc.is_playing() and not self.vc.is_paused():
            self.vc.pause()
            await ctx.send("Birbia paused the current audio in it's radio station.")
            await self.__command_timeout()
        else:
            await ctx.send("Birbia's radio station has nothing to pause!")

    @commands.command(
        name="resume", help="Resume the audio frozen in Birbia's radio station."
    )
    async def resume(self, ctx: commands.Context):
        """
        Resumes the paused audio.
        """

        if not self.allow_cmd:
            return await self.__timeout_warn(ctx)

        if self.vc.is_paused():
            self.vc.resume()
            await ctx.send("Birbia has resumed playing on it's radio station!")
            await self.__command_timeout()
        else:
            await ctx.send("Birbia has got nothing to resume in it's radio station.")

    @commands.command(
        name="skip",
        help="Skip that one song you don't like from Birbia's radio station.",
    )
    async def skip(self, ctx: commands.Context):
        """
        Skips the current song onto the next in queue.
        """

        if not self.allow_cmd:
            return await self.__timeout_warn(ctx)

        if self.vc is not None and self.vc.is_connected():
            if self.music_queue.queue_length() == 0:
                return await ctx.send(
                    "Birbia has nothing to skip! The queue is currently empty."
                )

            self.vc.stop()
            await ctx.send("Birbia skipped a song. It seems you didn't like it.")
            await self.__command_timeout()

    @commands.command(
        name="queue",
        aliases=["q"],
        help="Display Birbia's radio station pending play requests.",
    )
    async def queue(self, ctx: commands.Context):
        """
        Displays the queue with the pending songs left for playback.
        """

        if not self.allow_cmd:
            return await self.__timeout_warn(ctx)

        q = ""
        counter = 0
        for audio in self.music_queue.get_queue():
            if counter > 15:
                break

            q += f"{counter+1}. [{audio.title}]({audio.url}) - {audio.get_duration()}\n"
            counter += 1

        if self.music_queue.is_queue_empty():
            return await ctx.send(
                "Birbia radio station is currently waiting for new requests. Send one!"
            )

        await ctx.send(
            embed=discord.Embed(
                title="Birbia Station's Pending Requests",
                color=0xFF5900,
                description=q,
            )
        )
        await self.__command_timeout()

    @commands.command(name="now", help="Display the radio's currently playing song.")
    async def now(self, ctx: commands.Context):
        """
        Gets the name and duration of the audio currently playing.
        """

        if not self.allow_cmd:
            return await self.__timeout_warn(ctx)

        now = self.music_queue.now()
        if now is None:
            await self.__command_timeout()
            return await ctx.send(
                "Birbia's radio isn't playing anything right now. Submit a request now with ***birbia play***!"
            )

        song = f"[{now.title}]({now.url}) - {now.get_duration()}"
        await ctx.send(
            embed=discord.Embed(
                title="Birbia Station's Currently Playing Song",
                color=0xFF5900,
                description=song,
            )
        )
        await self.__command_timeout()

    @commands.command(
        name="clear", help="Removes every current request from Birbia's radio station"
    )
    async def clear(self, ctx: commands.Context):
        """
        Clears the queue.
        """

        if not self.allow_cmd:
            await self.__timeout_warn(ctx)

        if self.vc is None:
            return await ctx.send(
                "To use Birbia Radio, please connect to a voice channel first."
            )

        self.music_queue.empty_queue()
        await ctx.send("Cleared all requests from Birbia's Radio Station.")
        await self.__command_timeout()

    @commands.command(
        name="leave",
        aliases=["stop"],
        help="Make Birbia's Radio Station stop for the day.",
    )
    async def leave(self, ctx: commands.Context):
        """
        Stops audio playback and leaves the voicechat.
        """

        if not self.allow_cmd:
            await self.__timeout_warn(ctx)

        await self.__disconnect()
        await ctx.send("Birbia's Radio Station will stop for today sadly.")
        await self.__command_timeout()

    @commands.command(name="join", help="Allows Birbia to join your party!")
    async def join(self, ctx: commands.Context):
        """
        Join the bot to the requesting user's voice channel.
        """

        vc = ctx.author.voice

        if vc is None:
            return await ctx.send(
                "To use Birbia Radio, please connect to a voice channel first."
            )

        self.vc: discord.VoiceClient = await vc.channel.connect()
        await self.__timeout_quit()
