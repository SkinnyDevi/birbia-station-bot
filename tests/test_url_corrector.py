from src.core.music.audiosearchers.youtube import YoutubeSearcher


def test_yt_urls():
    URL_TESTS = [
        "http://www.youtube.com/watch?v=-wtIMTCHWuI",
        "http://www.youtube.com/v/-wtIMTCHWuI?version=3",
        "http://youtu.be/-wtIMTCHWuI",
        "https://youtube.com/shorts/I1I1i1i1I1I?feature=share",
        "https://www.youtube.com/shorts/1ioBJ-3NXx",
    ]

    for t in URL_TESTS:
        assert YoutubeSearcher.url_corrector(t) is not False
