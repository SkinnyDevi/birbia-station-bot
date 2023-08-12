import discord


class BirbiaAudio:
    FFMPEG_CFG = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    def __init__(self, source_url: str, title: str, url: str, length: int):
        self._source_url = source_url
        self._title = title
        self._url = url
        self._length = length
        self._pcm_audio = discord.FFmpegPCMAudio(source_url, **BirbiaAudio.FFMPEG_CFG)
        self.__requester_vc: discord.VoiceChannel = None

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
    def pcm_audio(self):
        """
        The audio's FFmpegPCMAudio instance for VoiceClient playing.
        """
        return self._pcm_audio

    def set_requester_vc(self, vc: discord.VoiceChannel):
        self.__requester_vc = vc

    def get_requester_vc(self):
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
        if minutes > 0:
            return "%02d:%02d" % (minutes, seconds)

        return "%ds" % (seconds)


class BirbiaQueue:
    def __init__(self):
        self.__queue: list[BirbiaAudio] = []
        self.__now: BirbiaAudio | None = None
        self.__history: list[BirbiaAudio] = []

    def get_queue(self):
        return self.__queue.copy()

    def get_history(self):
        return self.__history.copy()

    def queue_length(self):
        return len(self.__queue)

    def next(self):
        if len(self.__queue) == 0:
            raise Exception("There are no more audios left in the queue.")

        if self.__now is not None:
            self.__history.insert(0, self.__now)

        self.__now = self.__queue.pop(0)

        return self.__now

    def up_next(self) -> BirbiaAudio:
        if len(self.__queue) > 0:
            return self.__queue[0]

        return None

    def add_to_queue(self, audio: BirbiaAudio):
        if audio is None:
            raise Exception(f"Cannot append {type(None)} to queue.")

        self.__queue.append(audio)

    def now(self):
        return self.__now

    def is_queue_empty(self):
        return len(self.__queue) <= 0

    def reset(self):
        self.empty_history()
        self.empty_queue()

    def empty_queue(self):
        self.__queue.clear()

    def empty_history(self):
        self.__history.clear()
