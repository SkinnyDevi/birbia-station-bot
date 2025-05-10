import json
from os import environ
from pathlib import Path

from src.core.logger import BirbiaLogger
from src.core.exceptions import LanguageFileNotFoundError


class BirbiaLanguage:
    __instance = None

    def __name_replacer(self, s: str, bot_prefix: str):
        """
        Replaces the entry string with the desired replacer.
        """

        def replace_all(text: str, old: str, new: str):
            """
            Replace all instances of a string in a desired string.
            """

            while old in text:
                text = text.replace(old, new)
            return text

        if "$botname" in s:
            s = replace_all(s, "$botname", bot_prefix.capitalize())

        if "$prefix" in s:
            s = replace_all(s, "$prefix", bot_prefix)

        return s

    def __format_entries(self, data: dict):
        """
        Parses any '$botname' or '$prefix' keywords in the language file
        to the respective entries.
        """

        bot_prefix = self.get_prefix()

        for k, v in data.items():
            # replace any $botname entry
            if type(v) == type(""):
                v = self.__name_replacer(v, bot_prefix)

            if type(v) == type({}):
                # loops command "help" entries and values
                # for dicts with depth of 2
                for dict in v.values():
                    for key, val in dict.items():
                        dict[key] = self.__name_replacer(val, bot_prefix)

            self.__dict__[k] = v

    def change_lang(self, lang: str):
        """
        Change the current language assigned to the bot.
        """

        BirbiaLogger.info(f"Loading bot with languange code '{lang}'")
        self._lang = lang

        lang_path = Path(f"src/lang/{lang}.json")
        if not lang_path.exists():
            raise LanguageFileNotFoundError(
                f"Language file for language code '{lang}' not found"
            )

        with open(lang_path) as lang_file:
            data: dict = json.load(lang_file)
            self.__format_entries(data)

    def __init__(self):
        if BirbiaLanguage.__instance:
            raise RuntimeError("Language instance already exists")

        self._lang = environ.get("LANGUAGE") or "en"
        self.change_lang(self._lang)

        BirbiaLanguage.__instance = self

    @staticmethod
    def instance():
        """
        Generate or grab a Singleton instance for the language module.
        """

        if BirbiaLanguage.__instance:
            return BirbiaLanguage.__instance

        return BirbiaLanguage()

    def __setattr__(self, name, value):
        if name != "_lang":
            raise AttributeError("Language values are read-only")

        super().__setattr__(name, value)

    @staticmethod
    def get_prefix():
        """
        Get the current bot prefix.
        """

        dev_prefix = environ.get("DEV_PREFIX")
        prefix = environ.get("PREFIX")
        is_dev = environ.get("ENV_IS_DEV") == "True"
        return dev_prefix if is_dev else prefix

    @property
    def LANG_CODE(self):
        return self._lang

    def get_cmd_help(self, cmd: str, key: str) -> str:
        return self.help_commands[cmd][key]
