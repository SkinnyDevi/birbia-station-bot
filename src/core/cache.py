import os
import shutil
import json
import discord
import requests
from glob import glob
from pathlib import Path

from src.core.logger import BirbiaLogger
from src.core.exceptions import BirbiaCacheNotFoundError, InvalidBirbiaCacheError
from src.core.music.birbia_queue import BirbiaAudio


class BirbiaCache(object):
    CACHE_DIR = Path("birbiaplayer_cache")
    # fallback
    MAX_CACHE_ENTRIES = 20

    def __init__(self):
        self.MAX_CACHE_ENTRIES = int(os.environ.get("MAX_CACHE_ENTRIES"))

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(BirbiaCache, cls).__new__(cls)

        if not BirbiaCache.CACHE_DIR.exists():
            BirbiaCache.CACHE_DIR.mkdir()

        return cls.instance

    def cache_audio(self, audio_id: str, audio_file_url: str, ext="mp3"):
        """
        Caches a `BirbiaAudio` object and returns the cached file's `Path`.
        """

        self.__cache_limit_reached()

        cache_dir = self.CACHE_DIR.joinpath(audio_id)
        if not cache_dir.exists():
            cache_dir.mkdir()

        audio_file_path = cache_dir.joinpath(f"audio.{ext}")

        self.__cache_online_audio(audio_file_path, audio_file_url)

        BirbiaLogger.info(f"Cached audio file for audio id '{audio_id}'")

        return audio_file_path

    def cache_audio_info(self, audio: BirbiaAudio):
        """
        Caches a `BirbiaAudio` object and returns the cached file's `Path`.
        """

        self.__cache_limit_reached()

        cache_dir = self.CACHE_DIR.joinpath(audio.audio_id)
        if not cache_dir.exists():
            cache_dir.mkdir()

        info_file_path = cache_dir.joinpath("info.json")

        with open(info_file_path, "w") as info_out:
            info_out.write(json.dumps(audio.to_dict()))

        BirbiaLogger.info(f"Cached file info for audio id '{audio.audio_id}'")

        return info_file_path

    def retrieve_audio(self, audio_id: str):
        """
        File name must include extension.

        Returns the file path (if exists) of the desired file name.
        """

        cache_dir = self.CACHE_DIR.joinpath(audio_id)
        if cache_dir.exists():
            response = self.__reconstruct_audio_cache(audio_id, cache_dir)
            if isinstance(response, tuple):
                raise InvalidBirbiaCacheError(
                    f"{response[1]} file from cache '{audio_id}' not found"
                )

            return response

        raise BirbiaCacheNotFoundError(
            f"Audio cache corresponding to id '{audio_id}' not found in cache"
        )

    def empty(self):
        """
        Deletes the current caches.
        """

        BirbiaLogger.warn("Removing cached files...")

        all_caches = glob(str(self.CACHE_DIR.joinpath("*").absolute()))
        for c in all_caches:
            shutil.rmtree(c)

        BirbiaLogger.warn("Removed cached files")

    def invalidate(self, audio_id: str):
        """
        Invalidates the corresponding id's cache.
        """

        cache_dir = self.CACHE_DIR.joinpath(audio_id)
        if not cache_dir.exists():
            raise BirbiaCacheNotFoundError("No cache found to invalidate")

        shutil.rmtree(cache_dir)
        BirbiaLogger.info(f"Invalidated {audio_id} cache")

    def __reconstruct_audio_cache(self, audio_id: str, cache_dir: Path):
        """
        Turns the inputted cache path into a `BirbiaAudio` instance.
        """

        audio_file_path = cache_dir.joinpath("audio.mp3")
        info_file_path = cache_dir.joinpath("info.json")

        if not audio_file_path.exists() or not info_file_path.exists():
            audio_or_info = "Audio" if audio_file_path.exists() else "Info"
            return (None, audio_or_info)

        with open(info_file_path, "r") as info:
            info_file = json.load(info)

        return BirbiaAudio(
            source_url=str(audio_file_path.absolute()),
            title=info_file["title"],
            url=info_file["url"],
            length=info_file["length"],
            audio_id=audio_id,
            pcm_audio=discord.FFmpegPCMAudio(str(audio_file_path.absolute())),
        )

    def __cache_online_audio(self, cache_dir: Path, file_url: str):
        """
        Method for requesting and downloading files from URLs.
        """

        BirbiaLogger.debug(file_url)
        r = requests.get(file_url, allow_redirects=True)

        with open(cache_dir, "wb") as f:
            f.write(r.content)

    def __cache_limit_reached(self):
        """
        Determines if cache limit has been reached.

        If reached, deletes the oldest created cache.
        """
        if len(os.listdir(self.CACHE_DIR)) > self.MAX_CACHE_ENTRIES:
            all_caches = sorted(
                Path("birbiaplayer_cache").iterdir(), key=os.path.getctime, reverse=True
            )

            self.invalidate(all_caches[-1].stem)
