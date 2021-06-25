import re

from enum import Enum
from typing import Dict, Union, Optional

from .misc import httpget, match_enum

LOCALE_URL = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/{}.txt"
REMOTE_LOCALE_URL = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20Remote/{}.txt"


class Language(Enum):
    ENGLISH = "English"
    BRAZILIANPORTUGUESE = "BrazilianPortuguese"
    CHINESETRADITIONAL = "ChineseTraditional"
    FRENCH = "French"
    GERMAN = "German"
    ITALIAN = "Italian"
    JAPANESE = "Japanese"
    KOREAN = "Korean"
    RUSSIAN = "Russian"
    SPANISH = "Spanish"
    THAI = "Thai"

    # Aliases
    BRAZILIAN = "BrazilianPortuguese"
    PORTUGUESE = "BrazilianPortuguese"
    PTBR = "BrazilianPortuguese"
    CHINESE = "ChineseTraditional"
    ZH = "ChineseTraditional"
    CH = "ChineseTraditional"
    EN = "English"
    DE = "German"
    IT = "Italian"
    JA = "Japanese"
    JP = "Japanese"
    KO = "Korean"
    ES = "Spanish"
    TH = "Thai"


class LanguageManager:
    def __init__(self):
        self.languages: Dict[str, Dict[str, str]] = {}
        for lang in Language:
            self.languages[lang.value] = self.download_locale(lang)
            #break #TODO remove after testing

    @staticmethod
    def download_locale(language: Language):
        print(f"LanguageManager: Downloading language files for {language.value}")
        result = {}

        for url in [LOCALE_URL, REMOTE_LOCALE_URL]:
            raw = httpget(url.format(language.value)).text
            keys = re.findall(r"(?<=RESOURCE ID: ).*", raw)
            values = re.findall(r"(?<=TEXT: ).*", raw)

            final_locale = {keys[i].strip("\r"): values[i].strip("\r") for i in range(len(keys))}
            result = {**result, **final_locale}
        return result

    def get(self, key: str, language: Union[Language, str] = Language.ENGLISH) -> Optional[str]:
        try:
            language = match_enum(Language, language)
        except ValueError:
            language = Language.ENGLISH
        return self.languages[language.value].get(key)

    def get_all(self, key: str) -> Dict[str, Optional[str]]:
        result = dict()
        for lang in Language:
            result[lang.value] = (self.get(key, language=lang))
            #break #TODO remove after testing
        return result
