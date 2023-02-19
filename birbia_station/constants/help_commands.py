"""
Command list and help descriptions.
"""

GENERAL_CMDS = {
    "help": "Displayes all of Birbia's available actions.",
    "music": "Play music through your voice chats!",
    "doujin": "Search available doujins from our sources."
}

MUSIC_CMDS = {
    "play": "Play audio through Birbia's most famous radio station.",
    "pause": "Pause Birbia's radio station.",
    "resume": "Resume the audio frozen in Birbia's radio station.",
    "skip": "Skip that one song you don't like from Birbia's radio station.",
    "queue [q]": "Display Birbia's radio station pending play requests.",
    "clear": "Removes every current request from Birbia's radio station.",
    "leave [stop]": "Make Birbia's Radio Station stop for the day.",
    "now": "Display the radio's currently playing song."
}

DOUJIN_CMDS = {
    "doujin": "Displays a random doujin from our sources.",
    "arguments": "-s",
    "-s": "Specifies a sauce to look for within our sources."
}
