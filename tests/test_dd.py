from random import randint

from src.core.doujin.scraper import DoujinWebScraper
from src.core.doujin.doujin import DoujinManga

dscraper = DoujinWebScraper()


def test_dd_exists():
    sauce = 177013
    output = dscraper.doujin(sauce)
    print("\nSauce: ", output.to_dict())
    assert type(output) is DoujinManga


def test_rng_dd_exists():
    sauce = randint(1, dscraper.doujin_maxcount())
    output = dscraper.doujin(sauce)
    print("\nRNG: ", output.to_dict())
    assert type(output) is DoujinManga


def test_latest_maxcount():
    maxcount = dscraper.doujin_maxcount()
    output = dscraper.doujin(maxcount)
    print("\nMaxCount: ", output.to_dict())
    assert type(output) is DoujinManga
