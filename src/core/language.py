import json
from os import environ
from pathlib import Path

from src.core.logger import BirbiaLogger
from src.core.exceptions import LanguageFileNotFoundError


class BirbiaLanguage:
    __instance = None

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

            for k, v in data.items():
                self.__dict__[k] = v

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

    @property
    def LANG_CODE(self):
        return self._lang

    def get_cmd_help(self, cmd: str, key: str) -> str:
        return self.help_commands[cmd][key]
