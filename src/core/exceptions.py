class UnknownUrlAudioSearcherError(Exception):
    """
    Occurs when a URL does not match any supported searcher
    """

    pass


class EmptyQueueError(Exception):
    """
    Occurs when trying to manipulate the `BirbiaQueue`, but it was empty unintentionally.
    """

    pass


class VideoContentNotFound(Exception):
    """
    Occurs when no video content is found for downloading as audio.
    """

    pass


class QueueAudioValueError(ValueError):
    """
    Occurs when trying to manipulate a `BirbiaAudio` object in the queue, but it was `None`.
    """

    pass


class BirbiaCacheNotFoundError(FileNotFoundError):
    """
    Occurs when `BirbiaCache` can't find the specified file name.
    """

    pass


class InvalidBirbiaCacheError(FileNotFoundError):
    """
    Occurs when one of the need files in the cache is not present.
    """

    pass


class LanguageFileNotFoundError(FileNotFoundError):
    """
    Occurs when trying to load a non-existent language file
    """

    pass


class InstaPostNotVideoError(ValueError):
    """
    Occurs when a loaded Instagram post is not a video.
    """

    pass
