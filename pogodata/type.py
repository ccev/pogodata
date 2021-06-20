from typing import Union, Dict, List, Any
from enum import Enum

from .icons import IconManager, IconSet
from .custom_types import CustomEnum, QueryType
from .gameobject import GameObject
from .language import Language


class Type(GameObject):
    def __init__(self, icon_manager: IconManager, proto: Enum):
        super().__init__(icon_manager)

        self.proto: CustomEnum = CustomEnum(proto)
        self.names: Dict[str, str] = {}

        self.effective_against: List[Type] = []
        self.weak_against: List[Type] = []
        self.resists: List[Type] = []
        self.resisted_by: List[Type] = []

        self.query = {
            "type": (QueryType.customenum, self.proto),
            "name": (QueryType.qlist, self.names),
            "effective_against": (QueryType.qlist, self.effective_against),
            "weak_against": (QueryType.qlist, self.weak_against),
            "resists": (QueryType.qlist, self.resists),
            "resisted_by": (QueryType.qlist, self.resisted_by)
        }

    def get_base(self) -> Dict[str, Any]:
        return vars(self.proto)

    def get_full(self,
                 language: Union[str, Language] = Language.ENGLISH,
                 iconset: Union[str, int, IconSet] = IconSet.POGO) -> Dict[str, Any]:

        base = self.get_base()
        base.update({
            "name": self.get_name(language),
            "asset": self.icon_manager.montype(self, iconset),
            "effective_against": [t.get_base for t in self.effective_against],
            "weak_against": [t.get_base for t in self.weak_against],
            "resists": [t.get_base for t in self.resists],
            "resisted_by": [t.get_base for t in self.resisted_by]
        })
        return base


def _make_type_list(pogodata):
    print("Preparing Pokemon Types")
    type_proto = pogodata.get_enum("HoloPokemonType")

    for proto in type_proto:
        montype = Type(pogodata.icon_manager, proto)
        montype.names = pogodata.language_manager.get_all(proto.name)

        pogodata.types.append(montype)
