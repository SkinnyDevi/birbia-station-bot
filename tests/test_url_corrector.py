from birbia_station.core.music.audiosearchers.youtube import YtUrls


def test_yt_urls():
    URL_TESTS = [
        "http://www.youtube.com/watch?v=-wtIMTCHWuI",
        "http://www.youtube.com/v/-wtIMTCHWuI?version=3",
        "http://youtu.be/-wtIMTCHWuI",
        "https://youtube.com/shorts/I1I1i1i1I1I?feature=share",
        "https://www.youtube.com/shorts/1ioBJ-3NXx",
    ]

    for t in URL_TESTS:
        assert YtUrls.url_corrector(t) is not False
