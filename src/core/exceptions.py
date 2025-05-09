class UnknownUrlAudioSearcherError(Exception):
    """
    Occurs when a URL does not match any supported searcher
    """


class EmptyQueueError(Exception):
    """
    Occurs when trying to manipulate the `BirbiaQueue`, but it was empty unintentionally.
    """


class VideoContentNotFound(Exception):
    """
    Occurs when no video content is found for downloading as audio.
    """


class QueueAudioValueError(ValueError):
    """
    Occurs when trying to manipulate a `BirbiaAudio` object in the queue, but it was `None`.
    """


class BirbiaCacheNotFoundError(FileNotFoundError):
    """
    Occurs when `BirbiaCache` can't find the specified file name.
    """


class InvalidBirbiaCacheError(FileNotFoundError):
    """
    Occurs when one of the need files in the cache is not present.
    """


class LanguageFileNotFoundError(FileNotFoundError):
    """
    Occurs when trying to load a non-existent language file
    """


class InstaPostNotVideoError(ValueError):
    """
    Occurs when a loaded Instagram post is not a video.
    """

class YoutubeAgeRestrictedVideoRequestError(PermissionError):
    """
    Occurs when an age restricted video is requested, and no account cookies are passed to the searcher.
    """