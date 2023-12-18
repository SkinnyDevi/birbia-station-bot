import discord
import asyncio
import os

from discord.ext import commands

from src.core.logger import BirbiaLogger
from src.core.language import BirbiaLanguage
from src.core.music.audiosearchers.audiosearcher import AudioSearcher
from src.core.music.birbia_queue import BirbiaQueue
from src.core.exceptions import UnknownUrlAudioSearcherError, InstaPostNotVideoError


class MusicCog(commands.Cog):
    # fallback
    DISCONNECT_DELAY = 600  # 300s = 5 min
    CMD_TIMEOUT = 2  # seconds

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vc: discord.VoiceClient = None
        self.allow_cmd = True
        self.loop_current = False
        self.music_queue = BirbiaQueue()
        self.audio_search = AudioSearcher()
        self.__language = BirbiaLanguage.instance()

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
                disconnect_audio = discord.FFmpegPCMAudio(
                    f"{os.getcwd()}/src/audios/vc_disconnect.mp3"
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
        self.loop_current = False

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

        await ctx.send(self.__language.timeout_warn)

    def __queue_next(self):
        """
        Queues another audio for playback.
        """

        if self.music_queue.now() is not None and self.loop_current:
            next_song = self.music_queue.now().regenerate()
        elif self.music_queue.is_queue_empty():
            self.music_queue.now_to_history()
            return
        else:
            next_song = self.music_queue.next()

        if self.vc is not None:
            self.vc.play(next_song.pcm_audio, after=lambda e=None: self.__queue_next())

    async def __play_audio(self, ctx: commands.Context):
        """
        Plays the next audio from the queue to the voicechat.
        """

        up_next = self.music_queue.up_next()
        if self.vc is None or not self.vc.is_connected():
            self.vc = await up_next.get_requester_vc().connect()

            if self.vc is None:
                return await ctx.send(self.__language.cant_enter_vc)
        else:
            await self.vc.move_to(up_next.get_requester_vc())

        next_song = self.music_queue.next()
        if self.vc is not None:
            self.vc.play(next_song.pcm_audio, after=lambda e=None: self.__queue_next())

    @commands.command(
        name="play", help="Play audio through Birbia's most famous radio station."
    )
    async def play(self, ctx: commands.Context, *args):
        """
        Bot command used to search and play a song/audio/video/short from a supported platform.
        """

        if not self.allow_cmd:
            return await self.__timeout_warn(ctx)

        song_query = " ".join(args)

        if song_query in {"", " "}:
            return await ctx.send(self.__language.play_empty_query)

        requester_in_voice = ctx.author.voice

        if requester_in_voice is None:
            await self.__command_timeout()
            return await ctx.send(self.__language.no_vc)

        await ctx.send(self.__language.play_fetching_query)

        try:
            audio_obj = self.audio_search.search(song_query)
        except InstaPostNotVideoError as error:
            BirbiaLogger.error(str(error))
            return await ctx.send(self.__language.play_ig_not_video)
        except NotImplementedError as error:
            BirbiaLogger.error(str(error))
            return await ctx.send(f"***Error*** - Not Implemented: {error}")
        except UnknownUrlAudioSearcherError as error:
            BirbiaLogger.error(str(error))
            return await ctx.send(self.__language.play_platform_not_supported)
        except Exception as error:
            await ctx.send(self.__language.play_failed_error)
            BirbiaLogger.error("An error ocurred while searching for the audio:", error)

        if audio_obj is None:
            return await ctx.send(self.__language.play_failed_query)

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
            await ctx.send(self.__language.play_failed_error)
            BirbiaLogger.error(
                "An error ocurred while trying to play the requested audio:", error
            )

    @commands.command(name="pause", help="Pause Birbia's radio station.")
    async def pause(self, ctx: commands.Context):
        """
        Pauses the current audio playing.
        """

        if not self.allow_cmd:
            await self.__timeout_warn(ctx)

        if self.vc is None:
            return await ctx.send(self.__language.no_vc)

        if self.vc.is_playing() and not self.vc.is_paused():
            self.vc.pause()
            await ctx.send(self.__language.action_pause)
            await self.__command_timeout()
        else:
            await ctx.send(self.__language.action_pause_empty)

    @commands.command(
        name="resume", help="Resume the audio frozen in Birbia's radio station."
    )
    async def resume(self, ctx: commands.Context):
        """
        Resumes the paused audio.
        """

        if not self.allow_cmd:
            return await self.__timeout_warn(ctx)

        if self.vc is None:
            return await ctx.send(self.__language.no_vc)

        if self.vc.is_paused():
            self.vc.resume()
            await ctx.send(self.__language.action_resume)
            await self.__command_timeout()
        else:
            await ctx.send(self.__language.action_resume_empty)

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

        if self.vc is None:
            return await ctx.send(self.__language.no_vc)

        if self.vc is not None and self.vc.is_connected():
            if self.music_queue.queue_length() == 0 and self.music_queue.now() is None:
                return await ctx.send(self.__language.action_skip_empty)

            self.vc.stop()
            await ctx.send(self.__language.action_skip)
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

        if self.vc is None:
            return await ctx.send(self.__language.no_vc)

        q = ""
        counter = 0
        for audio in self.music_queue.get_queue():
            if counter > 15:
                break

            q += f"{counter+1}. [{audio.title}]({audio.url}) - {audio.get_duration()}\n"
            counter += 1

        if self.music_queue.is_queue_empty():
            return await ctx.send(self.__language.queue_empty)

        await ctx.send(
            embed=discord.Embed(
                title=self.__language.queue_title,
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

        if self.vc is None:
            return await ctx.send(self.__language.no_vc)

        now = self.music_queue.now()
        if now is None:
            await self.__command_timeout()
            return await ctx.send(self.__language.now_empty)

        song = f"[{now.title}]({now.url}) - {now.get_duration()}"
        await ctx.send(
            embed=discord.Embed(
                title=self.__language.now_title,
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
            return await ctx.send(self.__language.no_vc)

        self.music_queue.empty_queue()
        await ctx.send(self.__language.action_clear)
        await self.__command_timeout()

    @commands.command(name="loop", help="Loops the current audio playing")
    async def loop(self, ctx: commands.Context):
        if not self.allow_cmd:
            await self.__timeout_warn(ctx)

        if self.vc is None:
            return await ctx.send(self.__language.no_vc)

        if self.loop_current:
            await self.__command_timeout()
            return await ctx.send(self.__language.play_loop_already_on)

        if self.music_queue.now() is None:
            await self.__command_timeout()
            return await ctx.send(self.__language.now_empty)

        self.loop_current = True

        await ctx.send(self.__language.play_loop_on)
        await self.__command_timeout()

    @commands.command(name="unloop", help="Removes looping the current song")
    async def unloop(self, ctx: commands.Context):
        if not self.allow_cmd:
            await self.__timeout_warn(ctx)

        if self.vc is None:
            return await ctx.send(self.__language.no_vc)

        if not self.loop_current:
            await self.__command_timeout()
            return await ctx.send(self.__language.play_loop_already_off)

        if self.music_queue.now() is None:
            await self.__command_timeout()
            return await ctx.send(self.__language.now_empty)

        self.loop_current = False

        await ctx.send(self.__language.play_loop_off)
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

        if self.vc is None:
            return await ctx.send(self.__language.no_vc)

        await self.__disconnect()
        await ctx.send(self.__language.action_stop)
        await self.__command_timeout()

    @commands.command(name="join", help="Allows Birbia to join your party!")
    async def join(self, ctx: commands.Context):
        """
        Join the bot to the requesting user's voice channel.
        """

        vc = ctx.author.voice

        if self.vc is not None and self.vc.channel != vc.channel:
            await self.vc.move_to(vc.channel)
            await self.__timeout_quit()
            return

        if vc is None:
            return await ctx.send(self.__language.no_vc)

        if self.vc is not None:
            return await ctx.send(self.__language.already_in_vc)

        self.vc: discord.VoiceClient = await vc.channel.connect()
        await self.__timeout_quit()
