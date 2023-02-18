from time import sleep
from random import randint

from ..utils.scraper_bypass import DelayedScraper
from ..cogs.xcog import XCog

dscraper = DelayedScraper()


def test_dd_exists():
    sauce = 177013
    output = dscraper.webscrape_doujin(sauce)
    print("Sauce: ", output)
    assert type(output) is dict


def test_rng_dd_exists():
    sauce = randint(1, XCog.MaxSauce)
    output = dscraper.webscrape_doujin(sauce)
    print("RNG: ", output)
    assert type(output) is dict


dscraper = DelayedScraper(useDriver=True)


def notest_dd_driver_exists():
    sauce = 442465
    output = dscraper.scrapedriver_doujin(DelayedScraper.WebRoot + str(sauce))
    print("Sauce: ", output)
    assert type(output) is dict


def notest_rng_dd_driver_exists():
    sleep(2)

    sauce = randint(1, XCog.MaxSauce)
    output = dscraper.scrapedriver_doujin(DelayedScraper.WebRoot + str(sauce))
    print("RNG: ", output)
    assert type(output) is dict
