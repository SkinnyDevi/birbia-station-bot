import re
from yt_dlp import YoutubeDL
from urllib.request import urlopen

from src.core.music.audiosearchers.base import OnlineAudioSearcher
from src.core.music.birbia_queue import BirbiaAudio
from src.core.logger import BirbiaLogger
from src.core.cache import BirbiaCache
from src.core.exceptions import BirbiaCacheNotFoundError, InvalidBirbiaCacheError


class YoutubeSearcher(OnlineAudioSearcher):
    """
    YouTube Audio Searcher that retrieves an audio url from a query or YouTube URL.
    """

    YT_BASE_URL = "https://www.youtube.com/watch?v="
    YT_SHORTS_URL = "https://www.youtube.com/shorts/"

    def __init__(self):
        super().__init__(
            {
                "format": "bestaudio/best",
                "extractaudio": True,
                "audioformat": "mp3",
                "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
                "restrictfilenames": True,
                "noplaylist": True,
                "nocheckcertificate": True,
                "ignoreerrors": False,
                "logtostderr": False,
                "quiet": True,
                "no_warnings": True,
                "default_search": "auto",
                "source_address": "0.0.0.0",
            }
        )

    @staticmethod
    def url_corrector(url: str):
        """
        Corrects any URLs passed in to find the correct audio.
        """

        if len(url.split("?v=")) >= 2:
            return YoutubeSearcher.YT_BASE_URL + url.split("?v=")[1][:11]
        if len(url.split("/v/")) >= 2:
            return YoutubeSearcher.YT_BASE_URL + url.split("/v/")[1][:11]
        if len(url.split("/youtu.be/")) >= 2:
            return YoutubeSearcher.YT_BASE_URL + url.split("/youtu.be/")[1][:11]
        if len(url.split("/shorts/")) >= 2:
            return YoutubeSearcher.YT_BASE_URL + url.split("/shorts/")[1][:11]

        return False

    def __extract_video_id(self, url: str):
        """
        Extract YouTube video id from URL.

        Must have previously been passed through `YoutubeSearcher.url_corrector`.
        """

        return url.split("?v=")[1][:11]

    def __format_query(self, query: str):
        """
        Returns the correct format for the query.
        """
        url_matcher = re.search(r"^(http|https):\/\/.*$", query)
        query_is_url = url_matcher is not None
        return (
            YoutubeSearcher.url_corrector(query)
            if query_is_url
            else f"ytsearch:{query}"
        )

    def search(self, query: str):
        """
        Searches for a query in YouTube using yt_dl.

        The query can be in inputted text like a search bar or a specific video URL.
        """

        birbia_cache = BirbiaCache()
        query_is_url = self.__format_query(query)

        BirbiaLogger.info(f"Requesting YouTube query: {query}")
        if not query_is_url:
            # always search first if plain text search
            return self.__online_search(query, birbia_cache, query_is_url)

        # query is a URL, fetch for cache or fetch video
        video_id = self.__extract_video_id(query)
        try:
            cache = birbia_cache.retrieve_audio(video_id)
            BirbiaLogger.info(f"Retriving cached YouTube request for id '{video_id}'")
            return cache
        except (BirbiaCacheNotFoundError, InvalidBirbiaCacheError) as error:
            if isinstance(error, InvalidBirbiaCacheError):
                BirbiaLogger.error("Cache found incomplete:", error)
                BirbiaLogger.warn("Invalidating incomplete cache")
                birbia_cache.invalidate(video_id)

            return self.__online_search(query, birbia_cache, query_is_url)

    def __ytdl_search(self, query: str):
        """
        Performs a youtube search using `YoutubeDL`.
        """

        with YoutubeDL(self.config) as ydl:
            try:
                ydl.cache.remove()
                info = ydl.extract_info(query, download=False)

                if "entries" in info.keys():
                    info = info["entries"][0]
            except Exception as error:
                BirbiaLogger.error(
                    "There was an error trying to find the specified youtube video: ",
                    error.with_traceback(),
                )
                return None

        return info

    def __online_search(self, query: str, cache_instance: BirbiaCache, is_url: bool):
        """
        Searches online in YouTube for a specific URL or query.
        """

        info = self.__ytdl_search(query)

        BirbiaLogger.info("Successfully downloaded audio from query")
        audio = BirbiaAudio(
            source_url=info["url"],
            title=info["title"],
            url=YoutubeSearcher.YT_SHORTS_URL + info["id"]
            if "/shorts/" in query
            else YoutubeSearcher.YT_BASE_URL + info["id"],
            length=info["duration"],
            audio_id=info["id"],
        )

        if is_url:
            audio_file = urlopen(info["url"])
            cache_instance.cache_audio(info["id"], audio_file)
            cache_instance.cache_audio_info(audio)

        return audio
