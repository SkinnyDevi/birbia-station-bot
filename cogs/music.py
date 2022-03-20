import discord
import time
import asyncio
import pathlib
from datetime import timedelta
from discord.ext import commands
from youtube_dl import YoutubeDL
from decouple import config


class AudioSourceTracked(discord.AudioSource):
    def __init__(self, source):
        self._source = source
        self.count_20ms = 0

    def read(self) -> bytes:
        data = self._source.read()
        if data:
            self.count_20ms += 1
        return data

    @property
    def progress(self) -> float:
        return (self.count_20ms * 0.02)  # count_20ms * 20ms


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.allow_cmd = True

        self.is_playing = False
        self.is_paused = False
        self.queue = []
        self.playing = None

        self.YDL_CFG = {'format': 'bestaudio/best',
                        'noplaylist': 'True', 'audioformat': 'wav', 'noplaylist': 'True', 'no-cache-dir': 'True'}
        self.FFMPEG_CFG = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = None

    def _getSrcUrl(self):
        return self.queue[0][0]['source']

    def search_audio(self, query):
        query = (query.split("&")[0], query)[
            query.find("&") == -1]  # remove any url params

        if query.find("shorts/") != -1:
            query = 'https://www.youtube.com/watch?v=' + \
                query.split("shorts/")[1]

        with YoutubeDL(self.YDL_CFG) as ydl:
            try:
                ydl.cache.remove()
                info = ydl.extract_info(f"ytsearch:{query}", download=False)[
                    'entries'][0]
            except Exception as error:
                raise Exception(
                    "There was an error trying to find the specified youtube video: " + str(error))
        return {'source': info['formats'][0]['url'], 'title': info['title'], "yt_url": 'https://www.youtube.com/watch?v=' + info['id'], 'length': info['duration']}

    def queue_next(self):
        if len(self.queue) == 0:
            self.is_playing = False
            self.playing = None
            self.audiotracker = None
            return

        self.is_playing = True

        source = discord.FFmpegPCMAudio(
            self._getSrcUrl(), **self.FFMPEG_CFG)
        # source = discord.FFmpegPCMAudio(
        #     self._getSrcUrl(), **self.FFMPEG_CFG, executable=f"{pathlib.Path().resolve()}/{config('ffmpeg')}")
        self.vc.play(source, after=lambda e: self.queue_next())

        self.playing = self.queue.pop(0)

    async def play_audio(self, ctx):
        if len(self.queue) == 0:
            self.is_playing = False
            return

        self.is_playing = True

        if self.vc is None or not self.vc.is_connected():
            self.vc = await self.queue[0][1].connect()

            if self.vc is None:
                await ctx.send("Birbia could not enter your voice chat. This is illegal. We will take action.")
                return
        else:
            await self.vc.move_to(self.queue[0][1])

        source = discord.FFmpegPCMAudio(
            self._getSrcUrl(), **self.FFMPEG_CFG)
        # source = discord.FFmpegPCMAudio(
        #     self._getSrcUrl(), **self.FFMPEG_CFG, executable=f"{pathlib.Path().resolve()}/{config('ffmpeg')}")
        self.vc.play(source, after=lambda e: self.queue_next())

        self.playing = self.queue.pop(0)

    async def _command_timeout(self):
        self.allow_cmd = False
        await asyncio.sleep(3)
        self.allow_cmd = True

    async def _timeout_warn(self, ctx):
        await ctx.send("Birbia warns you to wait at least 3 seconds before running the next command.")

    @commands.command(name="play", help="Play audio through Birbia's most famous radio station.")
    async def play(self, ctx, *args):
        params = " ".join(args)

        if params == "" or params == " ":
            await ctx.send("Don't play with Birbia. What is that you want to listen to?")
            return

        vc = ctx.author.voice

        if vc is None:
            await ctx.send("To use Birbia Radio, please connect to a voice channel first.")
        elif self.is_paused:
            if self.allow_cmd:
                self.vc.resume()
                await self._command_timeout()
            else:
                await self._timeout_warn(ctx)
        else:
            if self.allow_cmd:
                vc = vc.channel
                await ctx.send("Birbia is sending it's hawks to fetch your audio...")
                try:
                    audio = self.search_audio(params)
                    if isinstance(type(audio), type(True)):
                        await ctx.send("Birbia sent out it's fastest eagles, but could not get your audio back. Try again!")
                    else:
                        self.queue.append([audio, vc])
                        newaudio = discord.Embed(
                            title="Added to radio queue!", color=0xff5900)

                        audio_length = timedelta(seconds=int(audio['length']))
                        audio_length = (str(audio_length)[2:], audio_length)[
                            int(audio['length']) > 3600]

                        newaudio.add_field(
                            name=f"{audio['title']}", value=f"{audio['yt_url']} - {audio_length}")
                        await ctx.send(embed=newaudio)

                        if self.is_playing is False:
                            await self.play_audio(ctx)

                        await self._command_timeout()
                except Exception:
                    await ctx.send("Birbia had a tough battle and could not send back your audio. Try ***stopping*** and ***playing*** again the Birbia Station.")
            else:
                await self._timeout_warn(ctx)

    @commands.command(name="pause", help="Pause Birbia's radio station.")
    async def pause(self, ctx):
        if self.allow_cmd:
            if self.is_playing:
                self.vc.pause()
                self.is_paused = True
                self.is_playing = False
                await ctx.send("Birbia paused the current audio in it's radio station.")
                await self._command_timeout()
            else:
                await ctx.send("Birbia's radio station has nothing to pause!")
        else:
            await self._timeout_warn(ctx)

    @commands.command(name="resume", help="Resume the audio frozen in Birbia's radio station.")
    async def resume(self, ctx):
        if self.allow_cmd:
            if self.is_paused:
                self.vc.resume()
                self.is_paused = False
                self.is_playing = True
                await ctx.send("Birbia has resumed playing on it's radio station!")
                await self._command_timeout()
            else:
                await ctx.send("Birbia has got nothing to resume in it's radio station.")
        else:
            await self._timeout_warn(ctx)

    @commands.command(name="skip", help="Skip that one song you don't like from Birbia's radio station.")
    async def skip(self, ctx):
        if self.allow_cmd:
            if self.vc is not None and self.vc:
                self.vc.stop()
                time.sleep(1)
                await self.play_audio(ctx)
                await ctx.send("Birbia skipped a song. It seems you didn't like it.")
                await self._command_timeout()
        else:
            await self._timeout_warn(ctx)

    @commands.command(name="queue", aliases=["q"], help="Display Birbia's radio station pending play requests.")
    async def queue(self, ctx):
        if self.allow_cmd:
            q = ""

            for i in range(0, len(self.queue)):
                if i > 15:
                    break
                audio_length = timedelta(
                    seconds=int(self.queue[i][0]['length']))
                audio_length = (str(audio_length)[2:], audio_length)[
                    int(self.queue[i][0]['length']) > 3600]
                q += f"{i+1}. [{self.queue[i][0]['title']}]({self.queue[i][0]['yt_url']}) - {audio_length}\n"

            if self.queue != []:
                await ctx.send(embed=discord.Embed(
                    title="Birbia Station's Pending Requests", color=0xff5900, description=q))
                await self._command_timeout()
            else:
                await ctx.send("Birbia radio station is currently waiting for new requests. Send one!")
        else:
            await self._timeout_warn(ctx)

    @commands.command(name="now", help="Display the radio's currently playing song.")
    async def now(self, ctx):
        if self.allow_cmd:
            if self.playing is not None:
                audio_length = timedelta(
                    seconds=int(self.playing[0]['length']))
                audio_length = (str(audio_length)[2:], audio_length)[
                    int(self.playing[0]['length']) > 3600]
                song = f"[{self.playing[0]['title']}]({self.playing[0]['yt_url']}) - {audio_length}"

                await ctx.send(embed=discord.Embed(
                    title="Birbia Station's Currently Playing Song", color=0xff5900, description=song))
                await self._command_timeout()
            else:
                await ctx.send("Birbia's radio isn't playing anything right now. Submit a request now with ***birbia play***!")
                await self._command_timeout()
        else:
            await self._timeout_warn(ctx)

    @commands.command(name="clear", help="Removes every current request from Birbia's radio station")
    async def clear(self, ctx):
        if self.allow_cmd:
            if self.vc is not None:
                self.queue = []
                await ctx.send("Cleared all requests from Birbia's Radio Station.")
                await self._command_timeout()
            else:
                await ctx.send("To use Birbia Radio, please connect to a voice channel first.")
        else:
            await self._timeout_warn(ctx)

    @commands.command(name="leave", aliases=["stop"], help="Make Birbia's Radio Station stop for the day.")
    async def leave(self, ctx):
        if self.allow_cmd:
            self.is_playing = False
            self.is_paused = False
            self.queue = []
            await self.vc.disconnect()
            await ctx.send("Birbia's Radio Station will stop for today sadly.")
            await self._command_timeout()
        else:
            await self._timeout_warn(ctx)
