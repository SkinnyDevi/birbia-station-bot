from ..core.music.audiosearchers.youtube import YtAudioSearcher

searcher = YtAudioSearcher()

queries = [
    "melissa porno graffiti",
    "https://www.youtube.com/watch?v=uGGQGoht6ic",
    "dross coñooo",
    "ayyy me cago en la puta yaaaaa",
]


def test_queries():
    for q in queries:
        assert searcher.search(q).source is not None
