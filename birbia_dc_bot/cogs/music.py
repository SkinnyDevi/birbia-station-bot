import discord
import time
import asyncio
from discord.ext import commands
from youtube_dl import YoutubeDL

YT_BASE_URL = 'https://www.youtube.com/watch?v='
YT_SHORTS_URL = "https://www.youtube.com/shorts/"
URL_TESTS = [
    "http://www.youtube.com/watch?v=-wtIMTCHWuI",
    "http://www.youtube.com/v/-wtIMTCHWuI?version=3",
    "http://youtu.be/-wtIMTCHWuI",
    "https://youtube.com/shorts/I1I1i1i1I1I?feature=share",
    "https://www.youtube.com/shorts/1ioBJ-3NXx"
]


def urlCorrector(url):
    """
    Corrects any URLs passed in to find the correct audio.
    """

    if len(url.split("?v=")) >= 2:
        return YT_BASE_URL + url.split("?v=")[1][:11]
    if len(url.split("/v/")) >= 2:
        return YT_BASE_URL + url.split("/v/")[1][:11]
    if len(url.split("/youtu.be/")) >= 2:
        return YT_BASE_URL + url.split("/youtu.be/")[1][:11]
    if len(url.split("/shorts/")) >= 2:
        return YT_BASE_URL + url.split("/shorts/")[1][:11]


def testUrls():
    for t in URL_TESTS:
        if urlCorrector(t) is None:
            return -1
    return 0


class AudioSourceTracked(discord.AudioSource):
    """
    (Unused Untested)
    Used to track the audio's time for the 'now' command.
    """

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
        """
        Reads at what point of the audio it is located.
        """

        return (self.count_20ms * 0.02)  # count_20ms * 20ms


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.allow_cmd = True

        self.is_playing = False
        self.is_paused = False
        self.queue = []
        self.playing = None
        self.started_quit_timeout = False

        self.DISCONNECT_DELAY = 300  # 300s = 5 min

        self.YDL_CFG = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        }

        self.FFMPEG_CFG = {
            'before_options':
            '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }

        self.vc = None

    def _getSrcUrl(self, getOpusSrc=False):
        """
        Gets the current audio's source for playback.

        Can be obtained as an FFmpegOpusAudio type or a string url with the audio.
        """

        if getOpusSrc:
            return self.queue[0][2]
        return self.queue[0][0]['source']

    def getDuration(self, seconds):
        """
        Formats the duration of the audio.
        """

        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        if hour > 0:
            return "%d:%02d:%02d" % (hour, minutes, seconds)
        if minutes > 0:
            return "%02d:%02d" % (minutes, seconds)
        if seconds > 0:
            return "%ds" % (seconds)

    def search_audio(self, query):
        """
        Searches for a query in YouTube using yt_dl.

        The query can be inputted text like a search bar or a specific video URL.
        """

        query = (f"ytsearch:{query}", urlCorrector(query))[
            query.find("http") > -1]
        print("\n-----------QUERY: " + query + "\n")

        with YoutubeDL(self.YDL_CFG) as ydl:
            try:
                ydl.cache.remove()
                info = ydl.extract_info(query, download=False)
                if 'entries' in info.keys():
                    info = info['entries'][0]
            except Exception as error:
                raise Exception(
                    "There was an error trying to find the specified youtube video: " +
                    str(error))
        return {
            'source':
            info['url'],
            'title':
            info['title'],
            'yt_url': (YT_BASE_URL + info['id'],
                       YT_SHORTS_URL + info["id"])[query.find("/shorts/") > -1],
            'length':
            self.getDuration(info['duration']),
        }

    async def _timeout_quit(self, ctx):
        """
        Creates a timer when connected to voicechat

        If it doesn't play anything within the {self.DISCONNECT_DELAY}, it will automatically
        leave the voicechat.
        """

        if self.started_quit_timeout:
            return

        time = 0
        self.started_quit_timeout = True
        while True:
            if not self.vc.is_connected():
                break

            await asyncio.sleep(1)

            time += 1

            if self.vc.is_playing() and not self.vc.is_paused():
                time = 0
            if time == self.DISCONNECT_DELAY:
                await self.vc.disconnect()
                await ctx.send(
                    "Birbia's radio has turned off, but will return once you wish to have more music."
                )
                break

    def queue_next(self):
        """
        Queues another audio for playback.
        """

        if len(self.queue) == 0:
            self.is_playing = False
            self.playing = None
            self.audiotracker = None
            return

        self.is_playing = True

        self.vc.play(self._getSrcUrl(getOpusSrc=True),
                     after=lambda e: self.queue_next())

        self.playing = self.queue.pop(0)

    async def play_audio(self, ctx):
        """
        Plays the next audio from the queue to the voicechat.
        """

        if len(self.queue) == 0:
            self.is_playing = False
            return

        self.is_playing = True

        if self.vc is None or not self.vc.is_connected():
            self.vc = await self.queue[0][1].connect()

            if self.vc is None:
                await ctx.send(
                    "Birbia could not enter your voice chat. This is illegal. We will take action."
                )
                return
        else:
            await self.vc.move_to(self.queue[0][1])

        self.vc.play(self._getSrcUrl(getOpusSrc=True),
                     after=lambda e: self.queue_next())

        self.playing = self.queue.pop(0)

    async def _command_timeout(self):
        """
        A timeout of 2 seconds to wait for each command.
        """

        self.allow_cmd = False
        await asyncio.sleep(2)
        self.allow_cmd = True

    async def _timeout_warn(self, ctx):
        """
        Warns the user if they are still in command timeout.
        """

        await ctx.send(
            "Birbia warns you to wait at least 3 seconds before running the next command."
        )

    @commands.command(
        name="play", help="Play audio through Birbia's most famous radio station.")
    async def play(self, ctx, *args):
        """
        Bot command used to search and play a song/audio/video/short from YouTube.
        """

        params = " ".join(args)

        if params == "" or params == " ":
            await ctx.send(
                "Don't play with Birbia. What is that you want to listen to?")
            return

        vc = ctx.author.voice

        if vc is None:
            await ctx.send(
                "To use Birbia Radio, please connect to a voice channel first.")
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
                        await ctx.send(
                            "Birbia sent out it's fastest eagles, but could not get your audio back. Try again!"
                        )
                    else:
                        opus_src = await discord.FFmpegOpusAudio.from_probe(
                            audio['source'], **self.FFMPEG_CFG)
                        self.queue.append([audio, vc, opus_src])

                        newaudio = discord.Embed(title="Added to radio queue!",
                                                 color=0xff5900)
                        newaudio.add_field(name=f"{audio['title']}",
                                           value=f"{audio['yt_url']} - {audio['length']}")
                        await ctx.send(embed=newaudio)

                        if self.is_playing is False:
                            await self.play_audio(ctx)

                        await self._command_timeout()
                        await self._timeout_quit(ctx)
                except Exception as error:
                    print("\nWHEW! FEW ERRORS: " + str(error))
                    await ctx.send(
                        "Birbia had a tough battle and could not send back your audio. Try ***stopping*** and ***playing*** again the Birbia Station."
                    )
            else:
                await self._timeout_warn(ctx)

    @commands.command(name="pause", help="Pause Birbia's radio station.")
    async def pause(self, ctx):
        """
        Pauses the current audio playing.
        """

        if self.allow_cmd:
            if self.is_playing:
                self.vc.pause()
                self.is_paused = True
                self.is_playing = False
                await ctx.send("Birbia paused the current audio in it's radio station."
                               )
                await self._command_timeout()
            else:
                await ctx.send("Birbia's radio station has nothing to pause!")
        else:
            await self._timeout_warn(ctx)

    @commands.command(name="resume",
                      help="Resume the audio frozen in Birbia's radio station.")
    async def resume(self, ctx):
        """
        Resumes the paused audio.
        """

        if self.allow_cmd:
            if self.is_paused:
                self.vc.resume()
                self.is_paused = False
                self.is_playing = True
                await ctx.send("Birbia has resumed playing on it's radio station!")
                await self._command_timeout()
            else:
                await ctx.send(
                    "Birbia has got nothing to resume in it's radio station.")
        else:
            await self._timeout_warn(ctx)

    @commands.command(
        name="skip",
        help="Skip that one song you don't like from Birbia's radio station.")
    async def skip(self, ctx):
        """
        Skips the current song onto the next in queue.
        """

        if self.allow_cmd:
            if self.vc is not None and self.vc:
                self.vc.stop()
                time.sleep(1)
                await self.play_audio(ctx)
                await ctx.send("Birbia skipped a song. It seems you didn't like it.")
                await self._command_timeout()
        else:
            await self._timeout_warn(ctx)

    @commands.command(
        name="queue",
        aliases=["q"],
        help="Display Birbia's radio station pending play requests.")
    async def queue(self, ctx):
        """
        Displays the queue with the pending songs left for playback.
        """

        if self.allow_cmd:
            q = ""

            for i in range(0, len(self.queue)):
                if i > 15:
                    break
                q += f"{i+1}. [{self.queue[i][0]['title']}]({self.queue[i][0]['yt_url']}) - {self.queue[i][0]['length']}\n"

            if self.queue != []:
                await ctx.send(
                    embed=discord.Embed(title="Birbia Station's Pending Requests",
                                        color=0xff5900,
                                        description=q))
                await self._command_timeout()
            else:
                await ctx.send(
                    "Birbia radio station is currently waiting for new requests. Send one!"
                )
        else:
            await self._timeout_warn(ctx)

    @commands.command(name="now",
                      help="Display the radio's currently playing song.")
    async def now(self, ctx):
        """
        Gets the name and duration of the audio currently playing.
        """

        if self.allow_cmd:
            if self.playing is not None:
                song = f"[{self.playing[0]['title']}]({self.playing[0]['yt_url']}) - {self.playing[0]['length']}"

                await ctx.send(
                    embed=discord.Embed(title="Birbia Station's Currently Playing Song",
                                        color=0xff5900,
                                        description=song))
                await self._command_timeout()
            else:
                await ctx.send(
                    "Birbia's radio isn't playing anything right now. Submit a request now with ***birbia play***!"
                )
                await self._command_timeout()
        else:
            await self._timeout_warn(ctx)

    @commands.command(
        name="clear",
        help="Removes every current request from Birbia's radio station")
    async def clear(self, ctx):
        """
        Clears the queue.
        """

        if self.allow_cmd:
            if self.vc is not None:
                self.queue = []
                await ctx.send("Cleared all requests from Birbia's Radio Station.")
                await self._command_timeout()
            else:
                await ctx.send(
                    "To use Birbia Radio, please connect to a voice channel first.")
        else:
            await self._timeout_warn(ctx)

    @commands.command(name="leave",
                      aliases=["stop"],
                      help="Make Birbia's Radio Station stop for the day.")
    async def leave(self, ctx):
        """
        Stops audio playback and leaves the voicechat.
        """

        if self.allow_cmd:
            self.is_playing = False
            self.is_paused = False
            self.queue = []
            await self.vc.disconnect()
            await ctx.send("Birbia's Radio Station will stop for today sadly.")
            await self._command_timeout()
        else:
            await self._timeout_warn(ctx)
