# Birbia's Radio Station [3.0.2]

![Birbia worker](https://thumbs.gfycat.com/RapidGlamorousGoldenretriever-size_restricted.gif)

From the all well known radio of Birbia's nation, we are now introducing Birbia's Radio Station in Discord!

This project grew from having the most popular discord music bots being taken down by YouTube.

So in short, ***I decided to make my own***.


## Name origin
For those who don't know or don't follow bird content, the term **'Birbia'** is a name that was given to the land where all birds come from and live. Try searching up some funny memes and you'll see how fun it is. 

The term itself derives from the funny way of saying 'bird' as 'birb', therefore 'Birbia'.

## Features

### Music
- Search for videos from YouTube as it were YouTube's search bar, or link a YouTube video to play it in a voice chat!
- Have control of what you listen to: ***play, pause, resume and skip*** audios and videos.
- Custom queue manager to list all future videos to play.

- Supported audio request platforms:
	- YouTube (URL and plain text search)
	- TikTok videos (URL search only)
	- Instagram videos (URL search only (Videos, Reels), videos in carousel not yet supported)

All of the above support caching! 
This means that if you frequently use URLs for audio requests, using the same URLs after the first use will provide you with your request exponentially quicker!

### Manga [+18]
- Search for the sauces you've always been curious about.
- Use it to get a random manga or find a specific sauce.

### Languages
Currently supported languages:
- English (en)
- Spanish (es)

To contribute to language translations, please reference the existing language files
and submit a pull request with your new language file. Pull requests run through a language key test
to test if the language file has all the needed translations and are up-to-date.


## Future Updates and Objectives

### General features
- ~~Language expansion~~ (2.2.0)

### Music
- Expand queue commands
	* Jump to number in queue
	* Queue pagination
	* Remove certain audio in X position of the queue

- Ability to load and play playlists
- ~~Caching system~~ (2.1.0)

- Multiple query platforms (now easier to implement with v2.0.0)
  * ~~Implement Instagram downloaders~~ (3.0.0)
  * ~~Implement TikTok downloaders~~ (2.1.0)
  * Implement Soundcloud downloaders
  * Implement Spotify downloaders


## For Developers
If you want to set up the bot yourself, this project as of v2.1.1 now uses venv (previously used poetry).
To setup the environment:
```zsh
py -m venv .venv # create an env
pip install --upgrade pip # update pip
pip install -r requirements.txt # install dependencies
```
To start the bot. By default, the bot can run with two tokens:
- A production token
- A beta/testing token

A custom `.env.example` file has been provided for you to play around with the settings:
```py
ENV_IS_DEV=True
BOT_TOKEN="Production_token_here"
BOT_DEV_TOKEN="Developer_token_here"
# Default delay = 300s = 5 min
DISCONNECT_DELAY=600
# Timeout in seconds
CMD_TIMEOUT=2
# default max entriers are 20
MAX_CACHE_ENTRIES=20
# If none, defaults to english
LANGUAGE=en
```

As of v2.1.0, a `docker-compose` has been provided to make the setup process of a docker container much more simpler.

As mentioned previously, rename your `.env.example` file to `.env` before executing the docker compose command.
```yml
version: '3.1'

services:
  bot:
    restart: unless-stopped
    env_file:
      - .env
    image: felixmv/birbia-station:latest

```

The Dockerfile of the discord bot provided.
```Dockerfile
FROM python:3.10.6

WORKDIR /birbia-station

# Default ENV values.
# Won't work if no env file is specified in docker-compose
ENV ENV_IS_DEV=False
ENV BOT_TOKEN="Production_token_here"
ENV BOT_DEV_TOKEN="Developer_token_here"
ENV DISCONNECT_DELAY=600
ENV CMD_TIMEOUT=2
ENV MAX_CACHE_ENTRIES=20
ENV LANGUAGE=en

COPY . .

RUN pip install poetry
RUN poetry install

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

```

Since bots work using Cogs, every module from this bot has been divided into it's separate cogs. This means that if you wish to disable any section (mangas, music player, etc...), you can simply comment out the respective cog.

Cogs can be found inside *main.py*:
```js
MusicCog(bot) // Music player Cog
UtilityCog(bot) // Utility Cog (purge messages, etc...)
XCog(bot) // Manga Cog
HelpCog(bot) // Hints help commands
```

## Changelog

### [3.0.2]
* Added a cookie regeneration system for when cookies expire for the `InstagramSearcher`
* Fixed a bug that threw and error when passing URLs containing '/reel/'

### [3.0.1]
* Changed Instagram downloader provider to a more reliable one
* New provider successfully passes all tests in all cases

### [3.0.0]
- Added **Instagram audio/url searcher** implementation:
	- Supports Videos and Reels URLs
	- Warns when a photo post is passed
	- Currently doesn't support video carrousels

### [2.2.0]
- Added language support!
- Added `LANGUAGE` configuration to `.env`
- Supported languages:
	- English (en)
	- Spanish (es)

To contribute to language translations, please reference the existing language files
and submit a pull request with your new language file. Pull requests run through a language key test
to test if the language file has all the needed translations and are up-to-date.

### [2.1.2]
* Added a new method of caching YouTube urls:
	- Before, caching was made with the given URL, and downloading using `urllib.request.urlopen`. Now, caching is made by directly downloading using the `YouTubeDL` class

### [2.1.1]
* Reworked testing for consistency
* General code refactorization
* Fixed a bug for `YoutubeSearcher` which errored when searching in plain text or URLs

### [2.1.0]
- Added a caching system for reusing local audios instead of requesting every time.
- Added **TikTok audio/url searcher** implementation
- Added `MAX_CACHE_ENTRIES` configuration to `.env`
- Implemented caching for TikTok and YouTube URLs
- Reworked the docker building process:
	- Added custom environment variables to the image (previously hardcoded)
	- Added a docker compose file for ease of use

### [2.0.0]
- Reworked the entire music cog for better maintanance and readability
- Added a general `AudioSearcher` class for a common class of platform audio searchers
- Added a logger
- Added custom exceptions
- Added new configurations to `.env`
* Fixes the error from 1.2.11 where the FFmpeg instance didn't work

## Support and Contribution
If you like what I do and find it easy to set up this bot youself, I would love if you'd give the repo a star. Very much appreciated! 

For any inquiries, you cant contact me through [my social links](https://github.com/SkinnyDevi/SkinnyDevi#im-available-in-the-following-social-media).
