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
    DoujinDataRoot = "https://nhentai.net/api/gallery/"
    WebRoot = 'https://www.nhentai.net/g/'
    FetchRoot = "https://nhentai.to/g/"

    def __init__(self, useDriver=False):
        if (useDriver):
            chromeOpts = uc.ChromeOptions()
            chromeOpts.headless = True

            if os.environ.get("POETRY_IS_DOCKER") == "True":
                chromeOpts.binary_location = "/usr/local/bin/chromedriver"

            self.driver = uc.Chrome(options=chromeOpts)

    def scrapedriver_dcover(self, url: str):
        self.driver.get(url)

        print("Getting cover...")
        results_container = WebDriverWait(self.driver, timeout=randint(5, 8)).until(
            EC.presence_of_element_located((By.ID, 'cover'))
        )

        self.driver._web_element_cls = uc.UCWebElement

        results_container = self.driver.find_element(By.ID, "cover")
        cover_atag: uc.WebElement = results_container.children()[0]
        return cover_atag.children('img')[0].get_attribute('src')

    def scrapedriver_ddata(self, sauce: int):
        self.driver.get(self.DoujinDataRoot + str(sauce))

        print("Getting data...")
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

    def scrapedriver_doujin(self, url: str):
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

    def __get_dcover(self, site: BeautifulSoup) -> str:
        coverdiv = site.find(
            'div', {'id': 'cover'}).children
        atag = list(map(lambda v: v, coverdiv))[1].children
        return list(map(lambda v: v, atag))[1]['src']

    def __get_titles(self, site: BeautifulSoup) -> list[str]:
        infodiv = site.find('div', {'id': 'info'}).children
        titles = list(map(lambda t: t, infodiv))

        return [titles[1].getText(), titles[3].getText()]

    def __get_tags(self, site: BeautifulSoup) -> list[str]:
        alltags = site.findAll('a', {'class': 'tag'})

        tags = []
        for spantag in alltags:
            if "/tag/" in spantag['href']:
                tags.append(spantag['href'].replace(
                    "/tag/", "").replace("/", ""))

        return tags

    def __get_pages(self, site: BeautifulSoup) -> int:
        return int(site.find('a', {'href': '#'}).getText().strip())

    def webscrape_doujin(self, sauce: int):
        request = requests.get(self.FetchRoot + str(sauce)).text
        doujinSite = BeautifulSoup(request, "html.parser")

        titles = self.__get_titles(doujinSite)

        return {
            'sauce': sauce,
            'cover': self.__get_dcover(doujinSite),
            'titles': {
                'english': titles[0],
                'original': titles[1]
            },
            'tags': self.__get_tags(doujinSite),
            'pages': self.__get_pages(doujinSite),
            'url': self.WebRoot + str(sauce)
        }
