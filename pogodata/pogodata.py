import re
import time

from datetime import datetime
from typing import List, Union, Optional, Dict, Any, Tuple

from enum import Enum
from .misc import httpget, PROTO_URL, GAMEMASTER_URL, INFO_URL
from .pokemon import _make_mon_list, Pokemon
from .type import _make_type_list, Type
#from .event import _make_event_list, Event
#from .item import _make_item_list, Item
#from .grunt import _make_grunt_list, Grunt
#from .raid import _make_raid_list
from .move import _make_move_list, Move
from .weather import _make_weather_list, Weather
#from .quest import _make_quest_list, Quest
from .icons import IconManager
from .language import LanguageManager
from .custom_types import DefaultEnum


class PogoData:
    types: List[Type] = []
    weather: List[Weather] = []
    moves: List[Move] = []
    mons: List[Pokemon] = []

    language_manager = None
    icon_manager = None

    __cached_enums: Dict[str, Dict[str, int]] = {}
    raw_protos: str = ""
    raw_gamemaster: List[Dict] = []

    def __init__(self):
        self.reload()

    def reload(self):
        start = time.time()
        self.language_manager = LanguageManager()
        self.icon_manager = IconManager()

        self.__cached_enums = {}

        print("Downloading latest Protos")
        self.raw_protos = httpget(PROTO_URL).text

        print("Downloading latest GameMaster")
        self.raw_gamemaster = httpget(GAMEMASTER_URL).json()

        _make_type_list(self)
        #_make_item_list(self)
        _make_weather_list(self)
        _make_move_list(self)
        _make_mon_list(self)
        #_make_quest_list(self)
        #_make_raid_list(self)
        #_make_grunt_list(self)
        #_make_event_list(self)

        print(f"It took {round(time.time()-start, 2)}s to reload PogoData")

    @staticmethod
    def __get_object(obj_list: List[Any], **kwargs) -> List[Any]:
        result = []
        for obj in obj_list:
            if obj.compare(**kwargs):
                result.append(obj)
        return result

    def get_mons(self, **kwargs) -> List[Pokemon]:
        result = self.__get_object(self.mons, **kwargs)
        return result

    def get_types(self, **kwargs) -> List[Type]:
        result = self.__get_object(self.types, **kwargs)
        return result

    def get_weather(self, **kwargs) -> List[Weather]:
        result = self.__get_object(self.weather, **kwargs)
        return result

    def get_moves(self, **kwargs) -> List[Move]:
        result = self.__get_object(self.moves, **kwargs)
        return result

    # TODO all get_xxx methods

    def get_enum(self, enum: str, message: Optional[str] = None, remove: Optional[str] = None) -> Enum:
        cache_key = str(message).lower() + ":" + enum.lower()
        cached = self.__cached_enums.get(cache_key)
        if cached:
            final = cached
        else:
            if message is not None:
                protos = re.findall(f"message {message}" + r"[^ß]*?message", self.raw_protos, re.IGNORECASE)
                # sorry

                if len(protos) == 0:
                    return DefaultEnum(0)
                protos = protos[0]
            else:
                protos = self.raw_protos

            proto = re.findall(f"enum {enum} "+r"{[^}]*}", protos, re.IGNORECASE)
            if len(proto) == 0:
                return DefaultEnum(0)

            proto = proto[0].replace("\t", "")

            final = {}
            proto = proto.split("{\n")[1].split("\n}")[0]
            for entry in proto.split("\n"):
                k: str = entry.split(" =")[0]
                v: int = int(entry.split("= ")[1].split(";")[0])
                if remove:
                    k = k.replace(remove, "")
                final[k] = v

            final = Enum(enum, final)
            self.__cached_enums[cache_key] = final

        return final

    def get_gamemaster(self, pattern: str, settings: Optional[str] = None) -> List[Tuple[str, Dict]]:
        result = []
        for entry in self.raw_gamemaster:
            templateid = entry.get("templateId", "")
            if re.search(pattern, templateid):
                data = entry.get("data", {})
                if settings:
                    data = data.get(settings, {})

                result.append((
                    templateid, data
                ))
        return result
