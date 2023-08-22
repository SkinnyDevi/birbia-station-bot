from random import randint

from src.core.doujin.scraper import DoujinWebScraper
from src.core.doujin.doujin import DoujinManga

dscraper = DoujinWebScraper()


def asserter(dd: DoujinManga):
    assert type(dd.sauce) is int
    assert type(dd.cover) is str
    assert type(dd.titles) is dict
    assert type(dd.tags) is list
    assert type(dd.pages) is int
    assert type(dd.url) is str


def test_dd_exists():
    sauce = 177013
    output = dscraper.doujin(sauce)
    asserter(output)


def test_rng_dd_exists():
    sauce = randint(1, dscraper.doujin_maxcount() - 5)
    output = dscraper.doujin(sauce)
    asserter(output)


def test_latest_maxcount():
    maxcount = dscraper.doujin_maxcount()
    output = dscraper.doujin(maxcount)
    asserter(output)
