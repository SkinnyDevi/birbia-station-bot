from ..core.music.audiosearchers.youtube import YoutubeSearcher


def test_youtube_queries():
    searcher = YoutubeSearcher()

    queries = [
        "melissa porno graffiti",
        "https://www.youtube.com/watch?v=uGGQGoht6ic",
        "dross coñooo",
        "ayyy me cago en la puta yaaaaa",
    ]

    for q in queries:
        assert searcher.search(q).source is not None
