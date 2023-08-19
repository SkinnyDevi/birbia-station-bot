import requests
import discord
from bs4 import BeautifulSoup
from mutagen.mp3 import MP3
from urllib import parse, request

from src.core.music.audiosearchers.base import OnlineAudioSearcher
from src.core.music.birbia_queue import BirbiaAudio
from src.core.exceptions import (
    InstaPostNotVideoError,
    BirbiaCacheNotFoundError,
    InvalidBirbiaCacheError,
)
from src.core.cache import BirbiaCache
from src.core.logger import BirbiaLogger


class InstagramSeacher(OnlineAudioSearcher):
    def __init__(self):
        super().__init__(
            {
                "cookies": {
                    "__cf_bm": "phLKXs1jpx4neQINeZxUSLEfPtM5QzSj2GJRr.RGZ2Y-1692402385-0-AWk24nRAdedHlzCAy5L+kYFmlDOjkuxtycn4Kuq5sJAn8eRaR5xM44DZmGcgCGPd4dGJJTaqdjnRFYvLZWaxv1s=",
                    "_cfuvid": "CJWbmppkGc.62vPm4eXjTU2Wva_74ei4v.kt4XddRkE-1692402385892-0-604800000",
                    "PHPSESSID": "bk5rnv4bore8ijfh79rbg9thvc",
                },
                "headers": {
                    "authority": "snapinsta.app",
                    "accept": "*/*",
                    "accept-language": "en-US,en;q=0.9",
                    "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryKMrY7ha1fX4B5SJW",
                    "dnt": "1",
                    "origin": "https://snapinsta.app",
                    "referer": "https://snapinsta.app/",
                    "sec-ch-ua": '"Not)A;Brand";v="24", "Chromium";v="116"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"macOS"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                },
            }
        )

    def __shortcode_extractor(self, url: str):
        """
        Extracts the Instagram short code from a given url.
        """

        return url.split("/p/")[1][:-1]

    def search(self, query: str) -> BirbiaAudio:
        cache_instance = BirbiaCache()

        shortcode = self.__shortcode_extractor(query)

        try:
            cache = cache_instance.retrieve_audio(shortcode)
            BirbiaLogger.info(
                f"Retrieving cached Instagram request for id '{shortcode}'"
            )
            return cache
        except (BirbiaCacheNotFoundError, InvalidBirbiaCacheError) as error:
            if isinstance(error, InvalidBirbiaCacheError):
                BirbiaLogger.error("Cache found incomplete:", error)
                BirbiaLogger.warn("Invalidating incomplete cache")
                cache_instance.invalidate(shortcode)

            return self.__online_search(query, shortcode, cache_instance)

    # def __query_requester(self, query: str):
    #     """
    #     Sends a query request to the designated service.
    #     """

    #     data = f'------WebKitFormBoundaryKMrY7ha1fX4B5SJW\r\nContent-Disposition: form-data; name="url"\r\n\r\n{query}\r\n------WebKitFormBoundaryKMrY7ha1fX4B5SJW\r\nContent-Disposition: form-data; name="action"\r\n\r\npost\r\n------WebKitFormBoundaryKMrY7ha1fX4B5SJW\r\nContent-Disposition: form-data; name="lang"\r\n\r\n\r\n------WebKitFormBoundaryKMrY7ha1fX4B5SJW--\r\n'

    #     return requests.post(
    #         "https://snapinsta.app/action2.php",
    #         cookies=self.config["cookies"],
    #         headers=self.config["headers"],
    #         data=data,
    #     )

    # def __extract_from_html(self, query: str):
    #     """
    #     Extracts data from the received HTML.
    #     """

    #     response = self.__query_requester(query)
    #     responseSoup = BeautifulSoup(response.text, "html.parser")

    #     parentElement = responseSoup.find("div", {"class": "download-bottom"})
    #     downloadMp3BtnLink = parentElement.find("a")

    #     return responseSoup.find(
    #         "p", {"class": "maintext"}
    #     ).decode_contents(), request.urlopen(downloadMp3BtnLink)

    def __online_search(
        self, query: str, shortcode: str, cache_instance: BirbiaCache
    ) -> BirbiaAudio:
        """
        Searches and downloads a video/reel using `Instaloader` class.
        """

        # post = Post.from_shortcode(self.__instaloader.context, shortcode)

        # if not post.is_video:
        #     raise InstaPostNotVideoError(f"Instagram post '{shortcode}' is not a post")

        # file_request = urlopen(post.video_url)
        # audio_cache = cache_instance.cache_audio(shortcode, file_request)

        # audio = BirbiaAudio(
        #     source_url=str(audio_cache.absolute()),
        #     title=post.caption[:255],
        #     url=query,
        #     length=0 if post.video_duration is None else post.video_duration,
        #     audio_id=shortcode,
        #     pcm_audio=discord.FFmpegPCMAudio(str(audio_cache.absolute())),
        # )
        # cache_instance.cache_audio_info(audio)

        # return audio
