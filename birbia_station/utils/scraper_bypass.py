import os
import json
from random import randint

import undetected_chromedriver as uc
import selenium.webdriver.support.expected_conditions as EC

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import By

import requests
from bs4 import BeautifulSoup


class DelayedScraper:
    """
    Scrapes a doujin hub and returns it's data.
    """

    DoujinDataRoot = "https://nhentai.net/api/gallery/"
    WebRoot = 'https://www.nhentai.net/g/'
    FetchRoot = "https://nhentai.to"

    def __init__(self, useDriver=False):
        if (useDriver):
            chromeOpts = uc.ChromeOptions()
            chromeOpts.headless = True

            if os.environ.get("POETRY_IS_DOCKER") == "True":
                chromeOpts.binary_location = "/usr/local/bin/chromedriver"

            self.driver = uc.Chrome(options=chromeOpts)

    def scrapedriver_dcover(self, url: str) -> str:
        """
        Uses UC driver to load the page and get the cover image.
        """

        self.driver.get(url)

        results_container = WebDriverWait(self.driver, timeout=randint(5, 8)).until(
            EC.presence_of_element_located((By.ID, 'cover'))
        )

        self.driver._web_element_cls = uc.UCWebElement

        results_container = self.driver.find_element(By.ID, "cover")
        cover_atag: uc.WebElement = results_container.children()[0]
        return cover_atag.children('img')[0].get_attribute('src')

    def scrapedriver_ddata(self, sauce: int) -> dict:
        """
        Uses UC driver to load the api segment and get the corresponding data.
        """

        self.driver.get(self.DoujinDataRoot + str(sauce))

        results_container = WebDriverWait(self.driver, timeout=randint(5, 8)).until(
            EC.presence_of_element_located((By.TAG_NAME, 'pre'))
        )

        self.driver._web_element_cls = uc.UCWebElement

        results_container = self.driver.find_element(By.TAG_NAME, "pre").text
        ddata = json.loads(results_container)
        titles = ddata['title']

        return {
            'sauce': int(ddata['id']),
            'titles': {
                'english': titles['english'],
                'original': titles['japanese']
            },
            'tags': ddata['tags'],
            'pages': int(ddata['num_pages'])
        }

    def scrapedriver_doujin(self, url: str) -> dict:
        """
        Uses UC driver to load a doujin from the official web, bypassing CloudFlare.
        """

        sauce = int(url.split("/")[-1])
        cover_url = self.webscrape_dcover(url)
        doujin_data = self.webscrape_ddata(sauce)

        doujin_data['url'] = url
        doujin_data['cover'] = cover_url

        tags = []
        for t in doujin_data['tags']:
            tags.append(t['name'])

        doujin_data['tags'] = tags

        return doujin_data

    def _get_dcover(self, site: BeautifulSoup) -> str:
        """
        Retrieves the doujin cover.
        """

        coverdiv = site.find(
            'div', {'id': 'cover'}).children
        atag = list(map(lambda v: v, coverdiv))[1].children
        return list(map(lambda v: v, atag))[1]['src']

    def _get_titles(self, site: BeautifulSoup) -> list[str]:
        """
        Gets the doujin's titles. Can be either english and/or japanese/chinese (original) title.
        """

        infodiv = site.find('div', {'id': 'info'}).children
        titles = list(map(lambda t: t, infodiv))

        return [titles[1].getText(), titles[3].getText()]

    def _get_tags(self, site: BeautifulSoup) -> list[str]:
        """
        Gets the tags attached to the doujin.
        """

        alltags = site.findAll('a', {'class': 'tag'})

        tags = []
        for spantag in alltags:
            if "/tag/" in spantag['href']:
                tags.append(spantag['href'].replace(
                    "/tag/", "").replace("/", ""))

        return tags

    def _get_pages(self, site: BeautifulSoup) -> int:
        """
        Retrieves the number of pages the doujin has.
        """

        return int(site.find('a', {'href': '#'}).getText().strip())

    def webscrape_doujin(self, sauce: int) -> dict:
        """
        Retrieves all doujin information from the sauce.
        """

        request = requests.get(self.FetchRoot + "/g/" + str(sauce)).text
        doujinSite = BeautifulSoup(request, "html.parser")

        titles = self._get_titles(doujinSite)

        return {
            'sauce': sauce,
            'cover': self._get_dcover(doujinSite),
            'titles': {
                'english': titles[0],
                'original': titles[1]
            },
            'tags': self._get_tags(doujinSite),
            'pages': self._get_pages(doujinSite),
            'url': self.WebRoot + str(sauce)
        }

    def webscrape_doujin_maxcount(self) -> int:
        """
        Retrieves the latest doujin ID from the source.
        """

        request = requests.get(self.FetchRoot).text
        homeSite = BeautifulSoup(request, "html.parser")

        recents = homeSite.findAll(
            'div', {'class': 'container index-container'})[1]
        recents = BeautifulSoup(str(recents), "html.parser")

        recentId = recents.find('a', {'class': 'cover'})['href']

        return int(recentId.replace("g/", "").replace("/", ""))
