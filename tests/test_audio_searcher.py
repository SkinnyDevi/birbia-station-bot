import discord
import time
import pytest
import os

from src.core.music.audiosearchers.youtube import YoutubeSearcher
from src.core.music.audiosearchers.tiktok import TikTokSearcher
from src.core.music.audiosearchers.instagram import InstagramSeacher
from src.core.music.birbia_queue import BirbiaAudio
from src.core.cache import BirbiaCache
from src.core.exceptions import InstaPostNotVideoError, YoutubeAgeRestrictedVideoRequestError

TIKTOK_VIDEO_TEST = "https://vm.tiktok.com/ZNdMNHnYU"
INSTAGRAM_MULTIPLE_TEST = "https://www.instagram.com/p/C5EJ0H7IS2X"
INSTAGRAM_IMAGE_TEST = "https://www.instagram.com/p/C5PMrj-LOMz"
INSTAGRAM_POST_TEST = "https://www.instagram.com/p/CvXwz9mAKmw"
YOUTUBE_VIDEO_TEST = "https://www.youtube.com/watch?v=a_cOaRNqjvQ"


def audio_asserter(audio: BirbiaAudio):
    assert type(audio.source) is str
    assert type(audio.title) is str
    assert type(audio.url) is str
    assert type(audio.length) is int or float
    assert type(audio.audio_id) is str
    assert type(audio.pcm_audio) is None or discord.FFmpegPCMAudio

@pytest.mark.skipif(os.getenv('CI') == 'true', reason="Only run locally.")
def test_youtube_searcher(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = YoutubeSearcher()
    cache = BirbiaCache()
    cache.empty()

    audio_asserter(searcher.search("melissa porno graffiti"))
    audio_asserter(searcher.search("https://www.youtube.com/watch?v=uGGQGoht6ic"))
    audio_asserter(searcher.search("ayyy me cago en la puta yaaaaa"))
    try:
        audio_asserter(searcher.search("dross coñooo"))
    except YoutubeAgeRestrictedVideoRequestError:
        assert True


@pytest.mark.skipif(os.getenv('CI') == 'true', reason="Only run locally.")
def test_youtube_cache_retrieval(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = YoutubeSearcher()
    cache = BirbiaCache()
    cache.empty()

    url = YOUTUBE_VIDEO_TEST
    url_id = url.split("?v=")[1]

    searcher.search(url)  # first search for caching
    recovered = cache.retrieve_audio(url_id)

    assert type(recovered) is BirbiaAudio
    audio_asserter(recovered)


@pytest.mark.skipif(os.getenv('CI') == 'true', reason="Only run locally.")
def test_tiktok_searcher(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = TikTokSearcher()
    cache = BirbiaCache()
    cache.empty()

    url = TIKTOK_VIDEO_TEST
    result = searcher.search(url)

    audio_asserter(result)


@pytest.mark.skipif(os.getenv('CI') == 'true', reason="Only run locally.")
def test_tiktok_cache_retrieval(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = TikTokSearcher()
    cache = BirbiaCache()
    cache.empty()
    time.sleep(10)

    url = TIKTOK_VIDEO_TEST
    url_id = TIKTOK_VIDEO_TEST.split("/")[-1]

    searcher.search(url)  # first search for caching
    recovered = cache.retrieve_audio(url_id)

    assert type(recovered) is BirbiaAudio
    audio_asserter(recovered)


@pytest.mark.skipif(os.getenv('CI') == 'true', reason="Only run locally.")
def test_instagram_searcher(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = InstagramSeacher()
    cache = BirbiaCache()
    cache.empty()
    time.sleep(3)

    url = INSTAGRAM_POST_TEST
    result = searcher.search(url)

    audio_asserter(result)


@pytest.mark.skipif(os.getenv('CI') == 'true', reason="Only run locally.")
def test_instagram_searcher_multiple(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = InstagramSeacher()
    cache = BirbiaCache()
    cache.empty()

    url = INSTAGRAM_MULTIPLE_TEST
    try:
        searcher.search(url)
    except NotImplementedError:
        assert True


@pytest.mark.skipif(os.getenv('CI') == 'true', reason="Only run locally.")
def test_instagram_not_video_error(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = InstagramSeacher()
    cache = BirbiaCache()
    cache.empty()
    time.sleep(3)

    url = INSTAGRAM_IMAGE_TEST

    try:
        searcher.search(url)
    except InstaPostNotVideoError:
        assert True


@pytest.mark.skipif(os.getenv('CI') == 'true', reason="Only run locally.")
def test_instagram_cache_retrieval(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = InstagramSeacher()
    cache = BirbiaCache()
    cache.empty()
    time.sleep(3)

    url = INSTAGRAM_POST_TEST
    url_id = INSTAGRAM_POST_TEST.split("/")[-1]

    searcher.search(url)  # first search for caching
    recovered = cache.retrieve_audio(url_id)

    assert type(recovered) is BirbiaAudio
    audio_asserter(recovered)
