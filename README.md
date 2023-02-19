# Birbia's Radio Station [1.2.8]

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

### Manga [+18]
- Search for the sauces you've always been curious about.
- Use it to get a random manga or find a specific sauce.


## Future Updates and Objectives

### General features
- Language expansion

### Music
- Expand queue commands
	* Jump to number in queue
	* Queue paging
	* Remove certain queue position


## For Developers
If you want to set up the bot yourself, this project uses Poetry as it's package manager. With that in mind, here are some of the commands you can run:
```python
poetry run bot # Starts the bot and goes online
poetry run test # Run any test it can find
```
To start the bot. By default, the bot can run with two tokens:
- A production token
- A beta/testing token

Use the variable ***is_dev*** in *main.py* to switch between these modes.

A docker file exists as a template to host your bot as a docker container locally or in the cloud.

```Dockerfile
FROM python:3.8.15

WORKDIR /birbia-station

ENV POETRY_TOKEN="Production_Token_Here"
ENV POETRY_DEV_TOKEN="Development_Token_Here"

COPY . .

# Install dependencies required through Poetry
RUN pip install poetry
RUN poetry install

# Install ffmpeg executable to the container
# This is necessary to play music through voice chat.
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

CMD [ "poetry", "run", "bot" ]
```

Since bots work using Cogs, every module from this bot has been divided into it's separate cogs. This means that if you wish to disable any section (mangas, music player, etc...), you can simply comment out the respective cog.

Cogs can be found inside *main.py*:
```js
MusicCog(bot) // Music player Cog
UtilityCog(bot) // Utility Cog (purge messages, etc...)
XCog(bot) // Manga Cog
HelpCog(bot) // Hints help commands
```

## Support and Contribution
If you like what I do and find it easy to set up this bot youself, I would love if you'd give the repo a star. Very much appreciated! 

For any inquiries, you cant contact me through [my social links](https://github.com/SkinnyDevi/SkinnyDevi#im-available-in-the-following-social-media).