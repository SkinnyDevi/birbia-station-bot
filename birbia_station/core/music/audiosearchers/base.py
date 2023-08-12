from abc import ABC, abstractmethod

from ..birbia_queue import BirbiaAudio


class OnlineAudioSearcher(ABC):
    """
    Abstract Audio Searcher that retrieves an audio url from a query on a specified platform.
    """

    def __init__(self, config: dict):
        self._config = config

    @property
    def config(self):
        """
        The searcher's custom config.
        """
        return self._config

    @abstractmethod
    def search(self, query: str) -> BirbiaAudio:
        """
        Searches for a query in the specified platform.
        """
        pass
