import os
from pathlib import Path, PosixPath
from yt_dlp import YoutubeDL
from urllib.request import urlopen

from src.core.cache import BirbiaCache
from src.core.music.birbia_queue import BirbiaAudio


def init_cache():
    cache = BirbiaCache()
    cache.empty()
    return cache


def youtube_example():
    url = "https://www.youtube.com/watch?v=a_cOaRNqjvQ"

    config = {
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

    with YoutubeDL(config) as ydl:
        ydl.cache.remove()
        info = ydl.extract_info(url, download=False)

        if "entries" in info.keys():
            info = info["entries"][0]

    return BirbiaAudio(
        source_url=info["url"],
        title=info["title"],
        url=url,
        length=info["duration"],
        audio_id=info["id"],
    )


def test_audio_cache(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    cache = init_cache()
    example = youtube_example()

    audio_file = urlopen(example.source)
    save_path = cache.cache_audio(example.audio_id, audio_file)

    assert type(save_path) is Path or PosixPath
    assert save_path.exists()


def test_info_cache(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    cache = init_cache()
    example = youtube_example()

    save_path = cache.cache_audio_info(example)

    assert type(save_path) is Path or PosixPath
    assert save_path.exists()


def test_cache_retrieval(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    cache = init_cache()
    example = youtube_example()

    audio_file = urlopen(example.source)
    cache.cache_audio(example.audio_id, audio_file)
    cache.cache_audio_info(example)

    retrieved = cache.retrieve_audio(example.audio_id)

    assert type(retrieved) is BirbiaAudio


def test_cache_empty(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    cache = BirbiaCache()

    for i in range(10):
        n_dir = cache.CACHE_DIR.joinpath(f"cache{i}")
        n_dir.mkdir()

    cache.empty()

    assert len(os.listdir(cache.CACHE_DIR)) == 0


def test_cache_invalidation(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    cache = init_cache()

    test_cache = cache.CACHE_DIR.joinpath("test_example_id")
    test_cache.mkdir()

    cache.invalidate("test_example_id")

    assert not test_cache.exists()


def test_cache_empty(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    cache = BirbiaCache()

    for i in range(10):
        n_dir = cache.CACHE_DIR.joinpath(f"cache{i}")
        n_dir.mkdir()

    cache.empty()

    assert len(os.listdir(cache.CACHE_DIR)) == 0
