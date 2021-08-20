from enum import Enum
from typing import List, Dict, Any, Union

from .gameobject import GameObject
from .icons import IconManager, IconSet
from .custom_types import CustomEnum, QueryType
from .type import Type
from .language import Language



class Weather(GameObject):
    def __init__(self, icon_manager: IconManager, proto: Enum):
        super().__init__(icon_manager)

        self.proto: CustomEnum = CustomEnum(proto)
        self.boosts: List[Type] = []
        self.names: Dict[str, str] = {}

    def make_query(self):
        self.query = {
            "weather": (QueryType.customenum, self.proto),
            "name": (QueryType.qlist, self.names),
            "boosts": (QueryType.qlist, [t.proto.id for t in self.boosts])
        }

    def get_base(self) -> Dict[str, Any]:
        return vars(self.proto)

    def get_full(self,
                 language: Union[str, Language] = Language.ENGLISH,
                 iconset: Union[str, int, IconSet] = IconSet.POGO) -> Dict[str, Any]:

        base = self.get_base()
        base.update({
            "name": self.get_name(language),
            "assets": self.icon_manager.weather(self, iconset),
            "boosts": [t.get_base() for t in self.boosts]
        })
        return base


def _make_weather_list(pogodata):
    weather_enum = pogodata.get_enum("WeatherCondition")
    for _, entry in pogodata.get_gamemaster(r"^WEATHER_AFFINITY_.*", "weatherAffinities"):
        template = entry["weatherCondition"]
        proto = weather_enum.match(template)

        weather = Weather(pogodata.icon_manager, proto)
        weather.names = pogodata.language_manager.get_all("weather_" + proto.name)

        for boost_type in entry["pokemonType"]:
            type_ = pogodata.get_types(type=boost_type)[0]
            weather.boosts.append(type_)

        weather.make_query()
        pogodata.weather.append(weather)
