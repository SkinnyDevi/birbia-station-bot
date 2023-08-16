import discord

from src.core.music.audiosearchers.youtube import YoutubeSearcher
from src.core.music.audiosearchers.tiktok import TikTokSearcher
from src.core.music.birbia_queue import BirbiaAudio
from src.core.cache import BirbiaCache


def test_youtube_queries(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = YoutubeSearcher()
    cache = BirbiaCache()
    cache.empty()

    queries = [
        "melissa porno graffiti",
        "https://www.youtube.com/watch?v=uGGQGoht6ic",
        "dross coñooo",
        "ayyy me cago en la puta yaaaaa",
    ]

    for q in queries:
        result = searcher.search(q)

        assert type(result.source) is str
        assert type(result.title) is str
        assert type(result.url) is str
        assert type(result.length) is int
        assert type(result.audio_id) is str
        assert type(result.pcm_audio) is None or discord.FFmpegPCMAudio


def test_youtube_recover_from_cache(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = YoutubeSearcher()
    cache = BirbiaCache()
    cache.empty()

    url = "https://www.youtube.com/watch?v=a_cOaRNqjvQ"
    url_id = url.split("?v=")[1]

    searcher.search(url)  # first search for caching
    recovered = cache.retrieve_audio(url_id)

    assert type(recovered) is BirbiaAudio


def test_tiktok_searcher(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = TikTokSearcher()
    cache = BirbiaCache()
    cache.empty()

    url = "https://vm.tiktok.com/ZGJpAqKQs/"
    result = searcher.search(url)

    assert type(result.source) is str
    assert type(result.title) is str
    assert type(result.url) is str
    assert type(result.length) is int or float
    assert type(result.audio_id) is str
    assert type(result.pcm_audio) is None or discord.FFmpegPCMAudio


def test_tiktok_cache_retrieval(monkeypatch):
    monkeypatch.setenv("MAX_CACHE_ENTRIES", "20")

    searcher = TikTokSearcher()
    cache = BirbiaCache()
    cache.empty()

    url = "https://vm.tiktok.com/ZGJpAqKQs/"
    url_id = "ZGJpAqKQs"

    searcher.search(url)  # first search for caching
    recovered = cache.retrieve_audio(url_id)

    assert type(recovered) is BirbiaAudio
