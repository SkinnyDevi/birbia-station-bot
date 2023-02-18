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
    FetchRoot = WebRoot.replace(".net", ".to")

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

    def webscrape_doujin(self, sauce: int):

        pass
