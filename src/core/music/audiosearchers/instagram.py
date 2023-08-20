import requests
import discord
import time
import subprocess
from random import randint
from mutagen.mp3 import MP3
from urllib.request import urlopen
from pathlib import Path

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
                    "random_n": "eyJpdiI6InBuelFsQ0VHOE9Feks3bDRkTVNDeWc9PSIsInZhbHVlIjoiV3VoMy9adUdOSEVwTm56VktoM3pXK2h0NFIxQW5wN3VwWGpCK0NIbm5VSDgvUE1lMEs2dVZaVy8zSWQ4L015biIsIm1hYyI6IjcxMDFhNGZjYjFjYWE4N2JhYjM2NWJlYWZjNTBmNDBjN2NmMzViYmVlNWVkMTM2ZjI0Mzc4NzZjYjhmM2EyODUiLCJ0YWciOiIifQ%3D%3D",
                    "XSRF-TOKEN": "eyJpdiI6Ik9DbGRQZEpHZXFvTFVGNGszS1lQSkE9PSIsInZhbHVlIjoiTCtKWTVhNmFraDJUVjhMTGw5eDNnb2dLQmFTb3NpaXJoWGE5c1RLSlpEVDAxejY2NFJmaEpCTFNJWmFsYjhpWVV1a3dGRUROMHNpZmIxNElCaSt6ZUZEY2NnMG13RnVDdmtjK2pqdHZ6VkJYNUFCQ28wNld0d2djeUxxS3JOZkMiLCJtYWMiOiJkM2ZiMTdkY2NlZTZiMDkzYjIxMzJhYWZlMmQzNmRjZTZjNjIzNDAzYzI5ZmQzNjljY2RlNjU0NjVmZDc2MWRjIiwidGFnIjoiIn0%3D",
                    "sssinstagram_session": "eyJpdiI6Im9pK1JGNTBPbjR5UmNLb2tYVTZLN1E9PSIsInZhbHVlIjoiTkZ1bWsvN200ZDcxQnJoOFBZR3k0QXJJNGdvSjFoLzR2UjFSNTdOZktZbTFoY2FpbUZwTHpMMEhhZ1Jld2IxSlkvdlhzTXFhUEpYTUI5cW1wd2lHYjlKY3dzOERKamR0NzdhR1ZMdENGQzh0M1kxV1pxdlVrckE3UUxNYmZuQTAiLCJtYWMiOiIyMjNmMjY2Mzk1NjI0YzM3OWRlOGRhMzFhODc3Y2U5NjUxYjZjMzVkMjUzM2JkMmYyY2FhMjcyZjJmZjEyYjQ5IiwidGFnIjoiIn0%3D",
                },
                "headers": {
                    "authority": "sssinstagram.com",
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "en-US,en;q=0.9",
                    "content-type": "application/json;charset=UTF-8",
                    "dnt": "1",
                    "origin": "https://sssinstagram.com",
                    "sec-ch-ua": '"Not)A;Brand";v="24", "Chromium";v="116"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"macOS"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                    "x-requested-with": "XMLHttpRequest",
                    "x-xsrf-token": "eyJpdiI6Ik9DbGRQZEpHZXFvTFVGNGszS1lQSkE9PSIsInZhbHVlIjoiTCtKWTVhNmFraDJUVjhMTGw5eDNnb2dLQmFTb3NpaXJoWGE5c1RLSlpEVDAxejY2NFJmaEpCTFNJWmFsYjhpWVV1a3dGRUROMHNpZmIxNElCaSt6ZUZEY2NnMG13RnVDdmtjK2pqdHZ6VkJYNUFCQ28wNld0d2djeUxxS3JOZkMiLCJtYWMiOiJkM2ZiMTdkY2NlZTZiMDkzYjIxMzJhYWZlMmQzNmRjZTZjNjIzNDAzYzI5ZmQzNjljY2RlNjU0NjVmZDc2MWRjIiwidGFnIjoiIn0=",
                },
            }
        )

    def __shortcode_extractor(self, url: str):
        """
        Extracts the Instagram short code from a given url.
        """

        return url.split("/p/")[1][:11]

    def search(self, query: str) -> BirbiaAudio:
        cache_instance = BirbiaCache()

        BirbiaLogger.info(f"Requesting Instagram query: {query}")
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

            time.sleep(randint(3, 9))
            return self.__online_search(query, shortcode, cache_instance)

    def __request_beautify(self, request: requests.Response):
        response: dict = request.json()["data"]

        if "items" not in response.keys():
            raise RuntimeError("No items were returned from the downloader API")

        if len(response["items"]) > 1:
            raise NotImplementedError("Cannot handle IG video carousel")

        entry = response["items"][0]

        video_urls = entry["urls"][0]

        if video_urls["extension"] != "mp4":
            raise InstaPostNotVideoError("The link does not refer to a video post")

        video_url = video_urls["urlDownloadable"]
        title: str = entry["meta"]["title"]

        return title[:255], urlopen(video_url)

    def __query_requester(self, query: str):
        """
        Sends a query request to the designated service.
        """

        json_data = {
            "link": query,
            "token": "",
        }

        response = requests.post(
            "https://sssinstagram.com/r",
            cookies=self.config["cookies"],
            headers=self.config["headers"],
            json=json_data,
        )

        return self.__request_beautify(response)

    def __convert_to_mp3(self, shortcode: str, mp4_path: Path, cache: BirbiaCache):
        new_path = cache.CACHE_DIR.joinpath(shortcode).joinpath("audio.mp3")

        mp3abs = str(new_path.absolute())
        mp4abs = str(mp4_path.absolute())

        subprocess.run(
            f"ffmpeg -i {mp4abs} {mp3abs}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        BirbiaLogger.info("Converted post to MP3")
        mp4_path.unlink()

        return new_path

    def __online_search(
        self, query: str, shortcode: str, cache_instance: BirbiaCache
    ) -> BirbiaAudio:
        """
        Searches and downloads a video/reel using `Instaloader` class.
        """

        # extraction = self.__extract_from_html(query)
        extraction = self.__query_requester(query)
        audio_cache = cache_instance.cache_audio(shortcode, extraction[1], ext="mp4")
        audio_cache = self.__convert_to_mp3(shortcode, audio_cache, cache_instance)
        local_file = MP3(str(audio_cache.absolute()))

        audio = BirbiaAudio(
            str(audio_cache.absolute()),
            extraction[0],
            query,
            local_file.info.length,
            shortcode,
            pcm_audio=discord.FFmpegPCMAudio(str(audio_cache.absolute())),
        )

        cache_instance.cache_audio_info(audio)

        return audio
