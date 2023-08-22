import os
from pathlib import Path, PosixPath
from urllib.request import urlopen

from src.core.cache import BirbiaCache
from src.core.music.birbia_queue import BirbiaAudio


def init_cache():
    cache = BirbiaCache()
    cache.empty()
    return cache


def cache_example():
    url = "https://github.com/SkinnyDevi/birbia-station-bot/raw/master/src/audios/vc_disconnect.mp3"

    audio = BirbiaAudio(
        "None",
        "Test Cache Example",
        url,
        99999,
        "ZGJpans2c",
    )

    return audio, url


def test_audio_cache(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    cache = init_cache()
    example = cache_example()

    save_path = cache.cache_audio(example[0].audio_id, example[1])

    assert type(save_path) is Path or PosixPath
    assert save_path.exists()


def test_info_cache(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    cache = init_cache()
    example = cache_example()

    save_path = cache.cache_audio_info(example[0])

    assert type(save_path) is Path or PosixPath
    assert save_path.exists()


def test_cache_retrieval(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    cache = init_cache()
    example = cache_example()

    cache.cache_audio(example[0].audio_id, example[1])
    cache.cache_audio_info(example[0])

    retrieved = cache.retrieve_audio(example[0].audio_id)

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
