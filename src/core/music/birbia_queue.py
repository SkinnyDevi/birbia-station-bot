import discord

from src.core.logger import BirbiaLogger
from src.core.exceptions import *


class BirbiaAudio:
    """
    An audio object used to handle music in queues.
    """

    FFMPEG_CFG = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    def __init__(
        self,
        source_url: str,
        title: str,
        url: str,
        length: int,
        audio_id: str,
        pcm_audio: discord.FFmpegPCMAudio = None,
    ):
        self._source_url = source_url
        self._title = title
        self._audio_id = audio_id
        self._url = url
        self._length = length
        self._pcm_audio = (
            pcm_audio
            if pcm_audio is not None
            else discord.FFmpegPCMAudio(self._source_url, **BirbiaAudio.FFMPEG_CFG)
        )
        self.__requester_vc: discord.VoiceChannel | None = None

    @property
    def source(self):
        """
        The audio's source URL.
        """
        return self._source_url

    @property
    def title(self):
        """
        The audio's title.
        """
        return self._title

    @property
    def url(self):
        """
        The audio's original URL from which it was requested.
        """
        return self._url

    @property
    def length(self):
        """
        The audio's length in seconds.
        """
        return self._length

    @property
    def audio_id(self):
        """
        The audio's specific platform ID.

        Used for cache identification mostly.
        """
        return self._audio_id

    @property
    def pcm_audio(self):
        """
        The audio's FFmpegPCMAudio instance for VoiceClient playing.
        """
        return self._pcm_audio

    @pcm_audio.setter
    def pcm_audio(self, val: discord.FFmpegPCMAudio):
        self._pcm_audio = val

    def set_requester_vc(self, vc: discord.VoiceChannel):
        """
        Saves the requester's voice channel to the audio object.
        """

        self.__requester_vc = vc

    def get_requester_vc(self):
        """
        Returns the attached voice channel.
        """

        return self.__requester_vc

    def get_duration(self):
        """
        Formats the duration of the audio from seconds to `Hours:Minutes:Seconds`.
        """

        seconds = self._length

        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        if hour > 0:
            return "%d:%02d:%02d" % (hour, minutes, seconds)
        elif minutes > 0:
            return "%02d:%02d" % (minutes, seconds)

        return "%ds" % (seconds)

    def regenerate(self):
        """
        Regenerates the PCMAudio. Mainly used for looping.
        """

        if "https" in self._source_url:
            self._pcm_audio = discord.FFmpegPCMAudio(
                self._source_url, **BirbiaAudio.FFMPEG_CFG
            )
        else:
            self._pcm_audio = discord.FFmpegPCMAudio(self._source_url)

        return self

    def to_dict(self):
        """
        Returns the essential information as a `dict`.
        """
        return {
            "title": self._title,
            "length": self._length,
            "id": self._audio_id,
            "url": self._url,
        }


class BirbiaQueue:
    """
    Birbia's radio queue to manage incoming `BirbiaAudio` audio objects.
    """

    def __init__(self):
        self.__queue: list[BirbiaAudio] = []
        self.__now: BirbiaAudio | None = None
        self.__history: list[BirbiaAudio] = []

    def get_queue(self):
        """
        Returns a copy of the current queue.
        """

        return self.__queue.copy()

    def get_history(self):
        """
        Returns a copy of the current play history.
        """

        return self.__history.copy()

    def queue_length(self):
        """
        Returns the length of the current queue.
        """

        return len(self.__queue)

    def next(self):
        """
        Plays the next in line `BirbiaAudio` object.
        """

        if len(self.__queue) == 0:
            raise EmptyQueueError("There are no more audios left in the queue.")

        if self.__now is not None:
            self.__history.insert(0, self.__now)

        self.__now = self.__queue.pop(0)

        return self.__now

    def up_next(self) -> BirbiaAudio:
        """
        Returns the next (if any) song/audio to play in queue.
        """

        return self.__queue[0] if len(self.__queue) > 0 else None

    def add_to_queue(self, audio: BirbiaAudio):
        """
        Adds a song/audio to the queue.
        """

        if audio is None:
            raise QueueAudioValueError(f"Cannot append {type(None)} to queue.")

        self.__queue.append(audio)
        BirbiaLogger.info(f"Appended audio '{audio.title}' to queue")

    def now_to_history(self):
        """
        Sends the current song/audio playing to the queue's history, leaving the `now` property empty.
        """

        self.__history.insert(0, self.__now)
        self.__now = None

    def now(self):
        """
        Returns the current audio playing in queue.
        """

        return self.__now

    def jump_to_pos(self, position: int):
        """
        Make the passed position the next audio to queue in after the current audio.
        """

        if position <= 0 or position > len(self.__queue):
            return None

        jumped_audio = self.__queue.pop(position - 1)
        self.__queue.insert(0, jumped_audio)

        return True

    def is_queue_empty(self):
        """
        Tests if the queue is empty.
        """

        return len(self.__queue) <= 0

    def reset(self):
        """
        Resets the history and queue back to being empty.
        """

        self.empty_history()
        self.empty_queue()
        BirbiaLogger.warn("Queue and History were reset")

    def empty_queue(self):
        """
        Empties the current queue.
        """

        self.__queue.clear()
        BirbiaLogger.info("Queue was emptied")

    def empty_history(self):
        """
        Empties the current queue's history.
        """

        self.__history.clear()
        BirbiaLogger.info("History was emptied")
