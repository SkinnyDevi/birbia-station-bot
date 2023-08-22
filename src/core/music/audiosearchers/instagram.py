import requests
import discord
import time
import json
import subprocess
from random import randint
from mutagen.mp3 import MP3
from urllib import parse, request
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
                },
            }
        )

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

            time.sleep(randint(3, 9))
            return self.__online_search(query, shortcode, cache_instance)

    def __invalidate_cache_cookies(self):
        """
        Invalidates the cache if the cached cookies are not valid.
        """

        cache_path = Path("searcher_cache/ig_searcher.json")

        if cache_path.exists():
            cache_path.unlink()

    def __regen_cookies(self):
        """
        Regenerates the page cookies.
        """

        cache_path = Path("searcher_cache")

        if cache_path.exists():
            cache_path = cache_path.joinpath("ig_searcher.json")

            if cache_path.exists():
                BirbiaLogger.info("Retrieving cached cookies")
                with open(cache_path, "r") as cache:
                    return json.load(cache)
            else:
                cache_path = Path("searcher_cache")

        else:
            cache_path.mkdir()

        BirbiaLogger.info("Regenerating cookies")

        page = requests.get("https://sssinstagram.com")
        cookie = page.headers["Set-Cookie"]

        xsrf_tkn = cookie.split("XSRF-TOKEN=")[1].split(";")[0]
        session = cookie.split("sssinstagram_session=")[1].split(";")[0]
        random_n = cookie.split("random_n=")[1].split(";")[0]

        cache_cookies = {
            "random_n": random_n,
            "XSRF-TOKEN": xsrf_tkn,
            "sssinstagram_session": session,
        }

        cache_path = cache_path.joinpath("ig_searcher.json")
        with open(cache_path, "w") as out:
            out.write(json.dumps(cache_cookies))

        return cache_cookies

    def __request_beautify(self, response: requests.Response):
        """
        Returns the necessary information of the post.
        """

        BirbiaLogger.info("Gathering necessary information from video response")

        if "items" not in response.keys():
            raise RuntimeError("No items were returned from the downloader API")

        if len(response["items"]) > 1:
            raise NotImplementedError("Cannot handle IG video carousel")

        entry = response["items"][0]

        video_urls = entry["urls"][0]

        if video_urls["extension"] != "mp4":
            raise InstaPostNotVideoError("The link does not refer to a video post")

        raw_url = video_urls["urlDownloadable"]
        video_url = parse.unquote(raw_url.split("uri=")[1].split("&")[0])
        title: str = entry["meta"]["title"]

        return title[:255], request.urlopen(video_url)

    def __query_requester(self, query: str):
        """
        Sends a query request to the designated service.
        """

        cookies = self.__regen_cookies()
        headers = self.config["headers"].copy()
        headers["x-xsrf-token"] = cookies["XSRF-TOKEN"].replace("%3D", "=")

        json_data = {
            "link": query,
            "token": "",
        }

        def make_req(c: dict, h: dict):
            response = requests.post(
                "https://sssinstagram.com/r",
                cookies=c,
                headers=h,
                json=json_data,
            )

            return response.json()

        try:
            return self.__request_beautify(make_req(cookies, headers)["data"])
        except KeyError:
            self.__invalidate_cache_cookies()
            cookies = self.__regen_cookies()
            headers = self.config["headers"].copy()
            headers["x-xsrf-token"] = cookies["XSRF-TOKEN"].replace("%3D", "=")

            request = make_req(cookies, headers)
            return self.__request_beautify(request["data"])

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
        Searches and downloads a video/reel using `Instaloader` class.
        """

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
