import re
from urllib.parse import urlparse

from src.core.music.audiosearchers.base import OnlineAudioSearcher
from src.core.music.audiosearchers.youtube import YoutubeSearcher
from src.core.music.audiosearchers.tiktok import TikTokSearcher
from src.core.music.audiosearchers.instagram import InstagramSeacher

from src.core.exceptions import UnknownUrlAudioSearcherError


class AudioSearcher(OnlineAudioSearcher):
    """
    This is the main class used to find any audio on the supported platforms.
    """

    def __init__(self):
        super().__init__({})

    def search(self, query: str):
        is_url = re.search(r"^(http|https):\/\/.*$", query)
        if is_url is None:
            yt = YoutubeSearcher()
            return yt.search(query)

        searcher = self.__url_matcher(query)

        return searcher.search(query)

    def __url_matcher(self, url: str) -> OnlineAudioSearcher:
        """
        Match and return the correct `OnlineAudioSearcher`.
        """

        parsed_uri = urlparse(url)

        match parsed_uri.netloc:
            case "www.instagram.com":
                return InstagramSeacher()
            case "www.tiktok.com" | "vm.tiktok.com":
                return TikTokSearcher()
            # case "soundcloud.com":
            #     pass
            case "youtube.com" | "www.youtube.com" | "youtu.be":
                return YoutubeSearcher()
            case _:
                raise UnknownUrlAudioSearcherError(
                    f"No audio searcher matched for URL host: {parsed_uri.netloc}"
                )
