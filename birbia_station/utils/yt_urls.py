class YtUrls:
    """
    Utility class for constants and formatting URLs.
    """

    YT_BASE_URL = 'https://www.youtube.com/watch?v='
    YT_SHORTS_URL = "https://www.youtube.com/shorts/"

    def url_corrector(url: str):
        """
        Corrects any URLs passed in to find the correct audio.
        """

        if len(url.split("?v=")) >= 2:
            return YtUrls.YT_BASE_URL + url.split("?v=")[1][:11]
        if len(url.split("/v/")) >= 2:
            return YtUrls.YT_BASE_URL + url.split("/v/")[1][:11]
        if len(url.split("/youtu.be/")) >= 2:
            return YtUrls.YT_BASE_URL + url.split("/youtu.be/")[1][:11]
        if len(url.split("/shorts/")) >= 2:
            return YtUrls.YT_BASE_URL + url.split("/shorts/")[1][:11]

        return False
