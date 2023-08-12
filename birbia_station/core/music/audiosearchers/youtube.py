from yt_dlp import YoutubeDL

from ...utils.yt_urls import YtUrls
from .base import OnlineAudioSearcher
from ..birbia_queue import BirbiaAudio


class YtAudioSearcher(OnlineAudioSearcher):
    """
    YouTube Audio Searcher that retrieves an audio url from a query or YouTube URL.
    """

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

    def search(self, query: str):
        """
        Searches for a query in YouTube using yt_dl.

        The query can be in inputted text like a search bar or a specific video URL.
        """

        query = (
            YtUrls.url_corrector(query)
            if query.find("http") > -1
            else f"ytsearch:{query}"
        )

        print("\n---------QUERY: " + query)

        with YoutubeDL(self.config) as ydl:
            try:
                ydl.cache.remove()
                info = ydl.extract_info(query, download=False)

                if "entries" in info.keys():
                    info = info["entries"][0]
            except Exception as error:
                # TODO: print to custom logger
                print(
                    "There was an error trying to find the specified youtube video: "
                    + str(error)
                )
                return None

        return BirbiaAudio(
            info["url"],
            info["title"],
            YtUrls.YT_SHORTS_URL + info["id"]
            if query.find("/shorts/") > -1
            else YtUrls.YT_BASE_URL + info["id"],
            info["duration"],
        )