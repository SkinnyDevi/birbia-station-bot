class DoujinManga:
    def __init__(
        self,
        sauce: int,
        cover: str,
        titles: dict[str, str],
        tags: list[str],
        pages: int,
        url: str,
    ):
        self._sauce = sauce
        self._cover = cover
        #
        self._titles = titles
        self._tags = tags
        self._pages = pages
        self._url = url

    @property
    def sauce(self):
        return self._sauce

    @property
    def cover(self):
        return self._cover

    @property
    def titles(self):
        """
        Titles are in the format of {language || original}: title.
        """
        return self._titles

    @property
    def tags(self):
        return self._tags

    @property
    def pages(self):
        """The number of pages."""
        return self._pages

    @property
    def url(self):
        return self._url

    def to_dict(self):
        return {
            "sauce": self._sauce,
            "cover": self._cover,
            "titles": self._titles,
            "tags": self._tags,
            "pages": self._pages,
            "url": self._url,
        }
