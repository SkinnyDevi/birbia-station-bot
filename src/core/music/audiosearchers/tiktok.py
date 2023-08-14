import requests
import discord
from bs4 import BeautifulSoup
from mutagen.mp3 import MP3
from urllib import parse, request

from src.core.music.audiosearchers.base import OnlineAudioSearcher
from src.core.music.birbia_queue import BirbiaAudio
from src.core.logger import BirbiaLogger
from src.core.cache import BirbiaCache
from src.core.exceptions import BirbiaCacheNotFoundError, InvalidBirbiaCacheError


class TikTokSearcher(OnlineAudioSearcher):
    def __init__(self):
        super().__init__(
            {
                "headers": {
                    "authority": "ssstik.io",
                    "accept": "*/*",
                    "accept-language": "en-GB,en;q=0.5",
                    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "hx-current-url": "https://ssstik.io/en",
                    "hx-request": "true",
                    "hx-target": "target",
                    "hx-trigger": "_gcaptcha_pt",
                    "origin": "https://ssstik.io",
                    "referer": "https://ssstik.io/en",
                    "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "sec-gpc": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                },
                "params": {
                    "url": "dl",
                },
            }
        )

    def __extract_video_id(self, video_url: str):
        parsed_uri = parse.urlparse(video_url)

        if "www.tiktok.com" in parsed_uri.hostname:
            return video_url.split("/video/")[1].split("?")[0]

        return video_url.split(".com/")[1][:-1]

    def search(self, query: str) -> BirbiaAudio:
        """
        Downloads and plays the requested TikTok URL from internet or cache.
        """

        BirbiaLogger.info(f"Requesting TikTok query: {query}")

        birbia_cache = BirbiaCache()
        video_id = self.__extract_video_id(query)

        try:
            cache = birbia_cache.retrieve_audio(video_id)
            BirbiaLogger.info(f"Retriving cached TikTok request for id '{video_id}'")
            return cache
        except (BirbiaCacheNotFoundError, InvalidBirbiaCacheError) as error:
            if isinstance(error, InvalidBirbiaCacheError):
                BirbiaLogger.error("Cache found incomplete:", error)
                BirbiaLogger.warn("Invalidating incomplete cache")
                birbia_cache.invalidate(video_id)

            video_id = self.__extract_video_id(query)
            data = {
                "id": query,
                "locale": "en",
                "tt": "dEQ4dnY3",
            }

            response = requests.post(
                "https://ssstik.io/abc",
                params=self.config["params"],
                headers=self.config["headers"],
                data=data,
            )
            responseSoup = BeautifulSoup(response.text, "html.parser")

            videoTitle = responseSoup.find("p", {"class": "maintext"}).decode_contents()

            parentElement = responseSoup.find("a", {"id": "direct_dl_link"}).parent
            downloadMp3BtnLink = parentElement.find_all("a")[2]["href"]
            mp3File = request.urlopen(downloadMp3BtnLink)

            audio_cache = birbia_cache.cache_audio(video_id, mp3File)
            localFile = MP3(str(audio_cache.absolute()))

            audio = BirbiaAudio(
                str(audio_cache.absolute()),
                videoTitle,
                query,
                localFile.info.length,
                video_id,
                pcm_audio=discord.FFmpegPCMAudio(str(audio_cache.absolute())),
            )

            birbia_cache.cache_audio_info(audio)

            return audio