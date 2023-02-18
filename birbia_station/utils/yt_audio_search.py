from yt_dlp import YoutubeDL

from .yt_urls import YtUrls


class YtAudioSearcher:
    def __init__(self):
        self.YDL_CFG = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        }

    def getDuration(self, seconds):
        """
        Formats the duration of the audio from seconds to Hours:Minutes:Seconds.
        """

        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        if hour > 0:
            return "%d:%02d:%02d" % (hour, minutes, seconds)
        if minutes > 0:
            return "%02d:%02d" % (minutes, seconds)
        if seconds > 0:
            return "%ds" % (seconds)

    def search_audio(self, query: str):
        """
        Searches for a query in YouTube using yt_dl.

        The query can be inputted text like a search bar or a specific video URL.
        """

        query = YtUrls.urlCorrector(query) if query.find(
            "http") > -1 else f"ytsearch:{query}"

        print("\n---------QUERY: " + query)

        with YoutubeDL(self.YDL_CFG) as ydl:
            try:
                ydl.cache.remove()
                info = ydl.extract_info(query, download=False)
                if 'entries' in info.keys():
                    info = info['entries'][0]
            except Exception as error:
                raise Exception(
                    "There was an error trying to find the specified youtube video: " +
                    str(error))
        return {
            'source':
            info['url'],
            'title':
            info['title'],
            'yt_url': (YtUrls.YT_BASE_URL + info['id'],
                       YtUrls.YT_SHORTS_URL + info["id"])[query.find("/shorts/") > -1],
            'length':
            self.getDuration(info['duration']),
        }
