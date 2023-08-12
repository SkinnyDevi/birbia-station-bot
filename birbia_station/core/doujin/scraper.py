import requests

from bs4 import BeautifulSoup

from .doujin import DoujinManga


class DoujinWebScraper:
    """
    Scrapes a doujin hub and returns it's data.
    """

    DOUJIN_DATA_ROOT = "https://nhentai.net/api/gallery/"
    WEB_ROOT = "https://www.nhentai.net/g/"
    FETCH_ROOT = "https://nhentai.to"

    def doujin(self, sauce: int):
        """
        Retrieves all doujin information from the sauce.
        """

        request = requests.get(DoujinWebScraper.FETCH_ROOT + "/g/" + str(sauce)).text
        doujin_site = BeautifulSoup(request, "html.parser")

        titles = self.__get_titles(doujin_site)

        return DoujinManga(
            sauce,
            self.__get_dcover(doujin_site),
            {"english": titles[0], "original": titles[1]},
            self.__get_tags(doujin_site),
            self.__get_pages(doujin_site),
            DoujinWebScraper.WEB_ROOT + str(sauce),
        )

    def doujin_maxcount(self) -> int:
        """
        Retrieves the latest doujin ID from the source.
        """

        request = requests.get(DoujinWebScraper.FETCH_ROOT).text
        home_site = BeautifulSoup(request, "html.parser")

        recents = home_site.findAll("div", {"class": "container index-container"})[1]
        recents = BeautifulSoup(str(recents), "html.parser")

        recent_id = recents.find("a", {"class": "cover"})["href"]

        return int(recent_id.replace("g/", "").replace("/", ""))

    def __get_dcover(self, site: BeautifulSoup) -> str:
        """
        Retrieves the doujin cover.
        """

        coverdiv = site.find("div", {"id": "cover"}).children
        atag = list(map(lambda v: v, coverdiv))[1].children
        return list(map(lambda v: v, atag))[1]["src"]

    def __get_titles(self, site: BeautifulSoup) -> list[str]:
        """
        Gets the doujin's titles. Can be either english and/or japanese/chinese (original) title.
        """

        infodiv = site.find("div", {"id": "info"}).children
        titles = list(map(lambda t: t, infodiv))

        return [titles[1].getText(), titles[3].getText()]

    def __get_tags(self, site: BeautifulSoup) -> list[str]:
        """
        Gets the tags attached to the doujin.
        """

        alltags = site.findAll("a", {"class": "tag"})

        tags = []
        for spantag in alltags:
            if "/tag/" in spantag["href"]:
                tags.append(spantag["href"].replace("/tag/", "").replace("/", ""))

        return tags

    def __get_pages(self, site: BeautifulSoup) -> int:
        """
        Retrieves the number of pages the doujin has.
        """

        return int(site.find("a", {"href": "#"}).getText().strip())
