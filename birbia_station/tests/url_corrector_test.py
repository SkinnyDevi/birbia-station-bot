from ..utils.yt_urls import YtUrls


def test_urls():
    URL_TESTS = [
        "http://www.youtube.com/watch?v=-wtIMTCHWuI",
        "http://www.youtube.com/v/-wtIMTCHWuI?version=3",
        "http://youtu.be/-wtIMTCHWuI",
        "https://youtube.com/shorts/I1I1i1i1I1I?feature=share",
        "https://www.youtube.com/shorts/1ioBJ-3NXx"
    ]

    for t in URL_TESTS:
        assert YtUrls.urlCorrector(t) is not False
