import requests

from bs4 import BeautifulSoup

from src.core.logger import BirbiaLogger 
from src.core.doujin.doujin import DoujinManga

class DoujinWebScraper:
    """
    Scrapes a doujin hub and returns it's data.
    """
    
    BASE_URL = "https://nhentai.net"
    USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/300.0.598994205 Mobile/15E148 Safari/604"
    
    def doujin(self, sauce: int) -> DoujinManga:
        """
        Retrieves all doujin information from the sauce.
        """

        parsed_site = self.__html_requester(sauce)
        titles = self.__get_titles(parsed_site)
        
        return DoujinManga(
            sauce,
            self.__get_cover(parsed_site),
            {"english": titles[0], "original": titles[1]},
            self.__get_artist(parsed_site),
            self.__get_tags(parsed_site),
            self.__get_pages(parsed_site),
            f"{DoujinWebScraper.BASE_URL}/g/{sauce}",
        )
        
    def doujin_maxcount(self) -> int:
        """
        Retrieves the latest doujin ID from the source.
        """
        
        parsed_site = self.__recents_requester()
        recents_container = parsed_site.select("#content .container:nth-child(3)")
        
        if len(recents_container) < 1:
            BirbiaLogger.error("Could not get recents container.")
            return -1
        
        recent_alink = recents_container[0].select_one(".cover")
        
        if not recent_alink:
            BirbiaLogger.error("Could not find latest doujin.")
            return -1
        
        return int(recent_alink["href"][3:-1])
    
    def __html_requester(self, sauce: int) -> BeautifulSoup:
        """
        Gets and parses de HTML for the manga.
        """
        
        request = requests.get(f"{DoujinWebScraper.BASE_URL}/g/{sauce}", headers={"User-Agent":DoujinWebScraper.USER_AGENT}).text
        return BeautifulSoup(request, "html.parser")
    
    def __recents_requester(self) -> BeautifulSoup:
        """
        Gets and parses the base url's home page.
        """
        
        request = requests.get(f"{DoujinWebScraper.BASE_URL}", headers={"User-Agent":DoujinWebScraper.USER_AGENT}).text
        return BeautifulSoup(request, "html.parser")
    
    def __get_id_from_html(self, doujin_site: BeautifulSoup) -> int:
        """
        Gets the manga id from the doujin HTML.
        """
        
        span = doujin_site.select_one("#gallery_id")
        
        if span:
            return int(span.contents[1])
        
        BirbiaLogger.error("Could not find sauce from html site.")
        return -1
    
    def __get_titles(self, doujin_site: BeautifulSoup) -> list[str]:
        """
        Gets the doujin's titles. Can be either english and/or japanese/chinese (original) title.
        """
        
        title_elements = doujin_site.select("#info .title span.pretty")
        return list(map(lambda t: t.contents[0], title_elements))
    
    def __get_cover(self, doujin_site: BeautifulSoup) -> str | None:
        """
        Retrieves the doujin cover.
        """
        
        cover_src: dict = doujin_site.select_one("#cover img")
        
        if cover_src:
            return cover_src["data-src"]
    
        sauce_id = self.__get_id_from_html(doujin_site)
        BirbiaLogger.error("Could not find doujin image for:", sauce_id)
        return None
    
    def __get_artist(self, doujin_site: BeautifulSoup) -> str:
        """
        Gets the artist attached to the doujin.
        """
        
        tags = doujin_site.select(".tag-container")
        
        if len(tags) < 1:
            BirbiaLogger.error("No tag container found for:", self.__get_id_from_html(doujin_site))
            return []
        
        artist_tag = tags[3].select_one(".tag .name")
        if artist_tag:
            return artist_tag.contents[0].getText()
        
        BirbiaLogger.warn("Could not find manga artist name for:", self.__get_id_from_html(doujin_site))
        return "unknown"
    
    def __get_pages(self, doujin_site: BeautifulSoup) -> int:
        """
        Retrieves the number of pages the doujin has.
        """
        
        return len(doujin_site.select("#thumbnail-container .thumb-container"))    
    
    def __get_tags(self, doujin_site: BeautifulSoup) -> list[str]:
        """
        Gets the tags attached to the doujin.
        """
        
        tags = doujin_site.select(".tag-container")
        
        if len(tags) < 1:
            BirbiaLogger.warn("No tag container found for:", self.__get_id_from_html(doujin_site))
            return []
        
        category_tags = tags[2].select(".tag .name")
        if len(category_tags) < 1:
            return []
        
        return list(map(lambda t: t.contents[0], category_tags))