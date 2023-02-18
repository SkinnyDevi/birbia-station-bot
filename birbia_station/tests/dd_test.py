from time import sleep
from random import randint

from ..utils.scraper_bypass import DelayedScraper
from ..cogs.xcog import XCog

dscraper = DelayedScraper()


def test_dd_exists():

    sauce = 442465
    output = dscraper.webscrape_doujin(XCog.WebRoot + str(sauce))
    print("Sauce: ", output)
    assert type(output) is dict


def test_rng_dd_exists():
    sleep(2)

    sauce = randint(1, XCog.MaxSauce)
    output = dscraper.webscrape_doujin(XCog.WebRoot + str(sauce))
    print("RNG: ", output)
    assert type(output) is dict
