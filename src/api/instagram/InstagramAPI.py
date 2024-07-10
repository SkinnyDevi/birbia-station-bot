import requests
import json
import time
from bs4 import BeautifulSoup, PageElement
from lxml import etree
from typing import Any
from random import randint


class InstagramAPI:
    def __init__(self):
        self._headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        }
        self.__timed_request = True

    class _Queue:
        def __init__(self):
            self.queue = []

        def enqueue(self, item):
            self.queue.append(item)

        def dequeue(self):
            if len(self.queue) < 1:
                return None
            return self.queue.pop(0)

        def size(self):
            return len(self.queue)

    def set_cookie(self, cookie: str):
        """
        Sets the cookie for the page request.

        To get the correct cookie, open any post in Instagram and open DevTools. Then:
        1. Go to Network tab
        2. Clear any previous requests using the clear button
        3. Refresh the page
        4. Look for the first request and click on it
        5. Go to the Request Headers section
        6. Copy the contents of the Cookie header
        7. Paste it here
        """

        if type(cookie) is not str:
            raise TypeError(f"Cookie is not {type('')}")

        self._headers["Cookie"] = cookie

    def use_timed_request(self, use: bool):
        """
        Adds a delay before each request.
        """

        self.__timed_request = use

    def single_post_video(self, url: str) -> dict[str, Any]:
        """
        Searches for a single Instagram post.

        Accepts reels and video posts with 1 video only.

        :returns: Dictionary with the video information
        """

        if "Cookie" not in self._headers.keys():
            raise ValueError("No cookie set for the request")

        if self.__timed_request:
            time.sleep(randint(1, 4))

        response = requests.get(url, headers=self._headers)
        soup = BeautifulSoup(response.text, "html.parser")

        dom = etree.HTML(str(soup))

        xpath = "//script[contains(text(), '.mp4')]"
        video_urls: list[PageElement] = dom.xpath(xpath)
        if len(video_urls) < 1:
            raise ValueError("No video found in the post")

        vid_element = video_urls[0]
        as_dict: dict = json.loads(vid_element.text)
        versions = self.__gather_video_versions(as_dict)
        first = versions[0]

        return {
            "width": first["width"],
            "height": first["height"],
            "url": first["url"],
        }

    def post_info(self, url: str) -> tuple[str, str]:
        """
        Searches the relevant information for a post.

        :returns: Tuple of title and description
        """

        if self.__timed_request:
            time.sleep(randint(1, 4))

        response = requests.get(url, headers=self._headers)
        soup = BeautifulSoup(response.text, "html.parser")

        dom = etree.HTML(str(soup))

        xpath = "//meta[@property='og:title']"
        meta_tags: list = dom.xpath(xpath)
        if len(meta_tags) < 1:
            raise ValueError("No <meta> tag found for title")
        title = meta_tags[0].attrib["content"]

        xpath = "//meta[@name='description']"
        meta_tags: list = dom.xpath(xpath)
        if len(meta_tags) < 1:
            raise ValueError("No <meta> tag found for description")
        description = meta_tags[0].attrib["content"]

        return title, description

    def __gather_video_versions(self, dict_obj: dict) -> dict:
        if "require" not in dict_obj.keys():
            raise ValueError(
                "No 'require' key found in the object: incorrect <script> tag was found"
            )

        queue = self._Queue()
        queue.enqueue(dict_obj["require"])
        video_versions = None
        while video_versions is None and queue.size() > 0:
            obj = queue.dequeue()

            if type(obj) not in [list, dict]:
                continue

            if type(obj) is list:
                for item in obj:
                    queue.enqueue(item)
                continue

            if type(obj) is dict:
                if "video_versions" in obj.keys():
                    video_versions = obj["video_versions"]
                    continue

                for _, value in obj.items():
                    queue.enqueue(value)
                continue

        if video_versions is None or len(video_versions) < 1:
            raise ValueError("No video versions found")

        return video_versions
