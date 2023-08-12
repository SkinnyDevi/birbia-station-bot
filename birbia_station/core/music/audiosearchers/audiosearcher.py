from urllib.parse import urlparse

from .base import OnlineAudioSearcher
from .youtube import YoutubeSearcher
from ...exceptions import UnknownUrlAudioSearcherError


class AudioSearcher(OnlineAudioSearcher):
    def __init__(self):
        super().__init__({})

    def search(self, query: str):
        if "http" not in query:
            yt = YoutubeSearcher()
            return yt.search(query)

        searcher = self.__url_matcher(query)

        return searcher.search(query)

    def __url_matcher(self, url: str) -> OnlineAudioSearcher:
        parsed_uri = urlparse(url)

        match parsed_uri.netloc:
            # case "instagram.com":
            #     pass
            # case "tiktok.com" | "vm.tiktok.com":
            #     pass
            # case "soundcloud.com":
            #     pass
            case "youtube.com" | "www.youtube.com" | "youtu.be":
                return YoutubeSearcher()
            case _:
                raise UnknownUrlAudioSearcherError(
                    f"No audio searcher matched for URL host: {parsed_uri.netloc}"
                )
