import requests
import discord
import time
import subprocess
from random import randint
from mutagen.mp3 import MP3
from bs4 import BeautifulSoup, ResultSet, PageElement
from pathlib import Path

from src.core.music.audiosearchers.base import OnlineAudioSearcher
from src.core.music.birbia_queue import BirbiaAudio
from src.core.exceptions import (
    InstaPostNotVideoError,
    BirbiaCacheNotFoundError,
    InvalidBirbiaCacheError,
)
from src.api.instagram.InstagramAPI import InstagramAPI
from src.core.cache import BirbiaCache
from src.core.logger import BirbiaLogger


class InstagramSeacher(OnlineAudioSearcher):
    def __init__(self):
        super().__init__(
            {
                "headers": {
                    "Accept": "*/*",
                    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            }
        )

        self.__ig_api = InstagramAPI()

    def __shortcode_extractor(self, url: str):
        """
        Extracts the Instagram short code from a given url.
        """

        splitter = "/reel/" if "/reel/" in url else "/p/"
        return url.split(splitter)[1][:11]

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

            time.sleep(randint(1, 4))
            return self.__online_search(query, shortcode, cache_instance)

    def __create_payload(self, post_url: str) -> str:
        """
        Creates the payload for the Instagram query.
        """

        payload = {
            "k_token": "b97a2deb55a25b2501d9928f9e565ab55f453dcf6ea87d4690bb595f27ba7533",
            "t": "media",
            "lang": "en",
            "k_exp": 3000000000,
            "q": post_url,
        }

        return "&".join([f"{k}={v}" for k, v in payload.items()])

    def __get_post_info(self, query: str):
        """
        Retrieves the post information.
        """

        self.__ig_api.use_timed_request(False)
        post_info = self.__ig_api.post_info(query)

        return post_info[1][:255]

    def __query_requester(self, query: str, shortcode: str) -> tuple[str, str]:
        """
        Sends a query request to the designated service.
        """

        REQ_URL = "https://v3.saveinsta.app/api/ajaxSearch"

        req_payload = self.__create_payload(query)
        response = requests.post(
            REQ_URL, data=req_payload, headers=self.config["headers"]
        )
        parsed = response.json()
        if "data" not in parsed.keys():
            raise ValueError("No data found in the response")

        soup = BeautifulSoup(parsed["data"], "html.parser")
        list_tags: ResultSet[PageElement] = soup.find_all("li")
        if len(list_tags) < 1:
            raise ValueError("No download link found")

        if len(list_tags) > 1:
            BirbiaLogger.warn("Multiple download links found (Multiple Post)")
            raise NotImplementedError("Multiple download links found (Multiple Post)")

        download_link: str = None
        for tag in list_tags:
            videoIcon = tag.find_all("i", {"class": "icon icon-dlvideo"})
            is_video = len(videoIcon) > 0

            if is_video:
                link: ResultSet[PageElement] = tag.find_all("a")
                download_link = link[1]["href"]
                break
            else:
                raise InstaPostNotVideoError(f"Post '{shortcode}' is not a video")

        post_info = self.__get_post_info(query)

        return post_info, download_link

    def __convert_to_mp3(self, shortcode: str, mp4_path: Path, cache: BirbiaCache):
        """
        Converts the MP4 downloaded file to MP3 using FFmpeg.
        """

        new_path = cache.CACHE_DIR.joinpath(shortcode).joinpath("audio.mp3")

        mp3abs = str(new_path.absolute())
        mp4abs = str(mp4_path.absolute())

        subprocess.run(
            f'ffmpeg -i "{mp4abs}" "{mp3abs}"',
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
        Searches and downloads a video/reel.
        """

        extraction = self.__query_requester(query, shortcode)
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
