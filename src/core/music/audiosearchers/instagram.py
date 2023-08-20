import requests
import discord
import time
import subprocess
from random import randint
from bs4 import BeautifulSoup
from mutagen.mp3 import MP3
from urllib import request
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
                    "cf_clearance": "wD3TzRjXEln4J8qmb3KzwESGvHIOaBYlpXNfM1kn.gE-1692484429-0-1-9d92b54d.13fe6093.32c96999-0.2.1692484429",
                    "XSRF-TOKEN": "eyJpdiI6ImRKcU5OR2JQWUg4TEt3VFlya2xjd1E9PSIsInZhbHVlIjoiT0tYci9tZEREZDZlaU9Qc05Gb29QdnJVY1Z0TkFWVmM1dG5xekZyeDBNOHdyT1FRcXZwaDNnQVFUb1NzeFhCTzZibVlkT0xKSFdoSktQNnJkSXhWaHlad0U2UGRiM052UHFZQzF6QWR6eCtBTGdlOStodTk0QmZrNER0dzJLdjMiLCJtYWMiOiI4MTY3ZGZmYjA3YWM3MTYxZjU5MWM5M2U1MzZkNTBjMTBjOTczODg3M2IxNzU2MDM0ZTcwZmM0MDQyMzc5NjIzIiwidGFnIjoiIn0%3D",
                    "indown_session": "eyJpdiI6Ik5WRFRpTWZUWUxDWm9EaWtiTkhma2c9PSIsInZhbHVlIjoib00vYVNtSFBhbHIxWXc0SXRzWS9RckxiQzF4aEcyR1pKNVMvcWJDVCtzMFU2VVV4ck84aXJFd1hsZnFRN2xTcmJKcXpKZC9ZT3JtMkVuQTRoTGxTZG82WVlWbVZsVFl5aHZMbFRvN0JNamZLUyttdFBJSjQwMUF0V0pqaXVGK1QiLCJtYWMiOiI0MDM2YjJjMGJhNjQxZGU1OGQ2NzE0YzlmNTY1YWVmYjdjODcyMGQwN2E0OWU0ODg3ZWE1OWU2ZTNkMjQyYmI5IiwidGFnIjoiIn0%3D",
                },
                "headers": {
                    "authority": "indown.io",
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "accept-language": "en-US,en;q=0.9",
                    "cache-control": "max-age=0",
                    "content-type": "application/x-www-form-urlencoded",
                    "dnt": "1",
                    "origin": "https://indown.io",
                    "referer": "https://indown.io/",
                    "sec-ch-ua": '"Not)A;Brand";v="24", "Chromium";v="116"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"macOS"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "same-origin",
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
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

            time.sleep(randint(3, 7))
            return self.__online_search(query, shortcode, cache_instance)

    def __query_requester(self, query: str):
        """
        Sends a query request to the designated service.
        """

        data = {
            "referer": "https://indown.io",
            "locale": "en",
            "_token": "HFqSKLFpXN4jBU8nSc8S8bLt9BXrgeayaWZ9I5Ln",
            "link": query,
        }

        return requests.post(
            "https://indown.io/download",
            cookies=self.config["cookies"],
            headers=self.config["headers"],
            data=data,
        )

    def __extract_from_html(self, query: str):
        """
        Extracts data from the received HTML.
        """

        response = self.__query_requester(query)
        responseSoup = BeautifulSoup(response.text, "html.parser")

        videoElement = responseSoup.find_all("video", {"class": "img-fluid"})

        if len(videoElement) > 1:
            raise NotImplementedError("Cannot handle IG video carousel")

        if len(videoElement) == 0:
            raise InstaPostNotVideoError(
                "IG URL does not correspond to a video or reel"
            )

        print(videoElement)
        videoElement = videoElement[0]

        videoParent = videoElement.parent.parent
        downloadMp3BtnLink = videoParent.find_all("a")[0]["href"]

        return request.urlopen(downloadMp3BtnLink)

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

        extraction = self.__extract_from_html(query)
        audio_cache = cache_instance.cache_audio(shortcode, extraction, ext="mp4")
        audio_cache = self.__convert_to_mp3(shortcode, audio_cache, cache_instance)
        local_file = MP3(str(audio_cache.absolute()))

        audio = BirbiaAudio(
            str(audio_cache.absolute()),
            f"IG Video - {shortcode}",
            query,
            local_file.info.length,
            shortcode,
            pcm_audio=discord.FFmpegPCMAudio(str(audio_cache.absolute())),
        )

        cache_instance.cache_audio_info(audio)

        return audio
