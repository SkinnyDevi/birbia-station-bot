import discord
import time

from src.core.music.audiosearchers.youtube import YoutubeSearcher
from src.core.music.audiosearchers.tiktok import TikTokSearcher
from src.core.music.audiosearchers.instagram import InstagramSeacher
from src.core.music.birbia_queue import BirbiaAudio
from src.core.cache import BirbiaCache
from src.core.exceptions import InstaPostNotVideoError


def audio_asserter(audio: BirbiaAudio):
    assert type(audio.source) is str
    assert type(audio.title) is str
    assert type(audio.url) is str
    assert type(audio.length) is int or float
    assert type(audio.audio_id) is str
    assert type(audio.pcm_audio) is None or discord.FFmpegPCMAudio


def test_youtube_searcher(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = YoutubeSearcher()
    cache = BirbiaCache()
    cache.empty()

    audio_asserter(searcher.search("melissa porno graffiti"))
    audio_asserter(searcher.search("https://www.youtube.com/watch?v=uGGQGoht6ic"))
    audio_asserter(searcher.search("dross coñooo"))
    audio_asserter(searcher.search("ayyy me cago en la puta yaaaaa"))


def test_youtube_cache_retrieval(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = YoutubeSearcher()
    cache = BirbiaCache()
    cache.empty()

    url = "https://www.youtube.com/watch?v=a_cOaRNqjvQ"
    url_id = url.split("?v=")[1]

    searcher.search(url)  # first search for caching
    recovered = cache.retrieve_audio(url_id)

    assert type(recovered) is BirbiaAudio
    audio_asserter(recovered)


def test_tiktok_searcher(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = TikTokSearcher()
    cache = BirbiaCache()
    cache.empty()

    url = "https://vm.tiktok.com/ZGJpAqKQs/"
    result = searcher.search(url)

    audio_asserter(result)


def test_tiktok_cache_retrieval(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = TikTokSearcher()
    cache = BirbiaCache()
    cache.empty()
    time.sleep(10)

    url = "https://vm.tiktok.com/ZGJpAqKQs/"
    url_id = "ZGJpAqKQs"

    searcher.search(url)  # first search for caching
    recovered = cache.retrieve_audio(url_id)

    assert type(recovered) is BirbiaAudio
    audio_asserter(recovered)


def test_instagram_searcher(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = InstagramSeacher()
    cache = BirbiaCache()
    cache.empty()

    url = "https://www.instagram.com/p/CvXwz9mAKmw/"
    result = searcher.search(url)

    audio_asserter(result)


def test_instagram_searcher_multiple(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = InstagramSeacher()
    cache = BirbiaCache()
    cache.empty()

    url = "https://www.instagram.com/p/CwGK5D8SJeY/"
    try:
        searcher.search(url)
    except NotImplementedError:
        assert True


def test_instagram_not_video_error(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = InstagramSeacher()
    cache = BirbiaCache()
    cache.empty()

    url = "https://www.instagram.com/p/Cqx4gHJMrdj"

    try:
        searcher.search(url)
    except InstaPostNotVideoError:
        assert True


def test_instagram_cache_retrieval(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = InstagramSeacher()
    cache = BirbiaCache()
    cache.empty()
    time.sleep(3)

    url = "https://www.instagram.com/p/CvXwz9mAKmw/"
    url_id = "CvXwz9mAKmw"

    searcher.search(url)  # first search for caching
    recovered = cache.retrieve_audio(url_id)

    assert type(recovered) is BirbiaAudio
    audio_asserter(recovered)
