from typing import Union, Dict, List, Any, Tuple
from enum import Enum

from .icons import IconManager, IconSet
from .custom_types import CustomEnum, QueryType
from .gameobject import GameObject
from .language import Language


# typeid: #(effective_against, weak_against, resists, resisted_by)
EFFECTIVENESSES = {
    0: (
        [], [], [], []
    ),
    1: (
        [], [6, 9], [8], [8]
    ),
    2: (
        [1, 15, 6, 17, 9], [4, 3, 14, 7, 18], [], []
    ),
    3: (
        [12, 2, 7], [13, 6, 9], [5], []
    ),
    4: (
        [12, 18], [4, 5, 6, 8], [], [9]
    ),
    5: (
        [10, 13, 4, 6, 9], [12, 7], [13], [3]
    ),
    6: (
        [10, 15, 3, 7], [2, 5, 9], [], []
    ),
    7: (
        [12, 14, 17], [10, 2, 4, 8, 9, 18], [], [17]
    ),
    8: (
        [8, 14], [17], [1, 2], [1]
    ),
    9: (
        [15, 6, 18], [10, 11, 13, 9], [4], []
    ),
    10: (
        [12, 15, 7, 9], [10, 11, 6, 16], [], []
    ),
    11: (
        [10, 5, 6], [11, 12, 16], [], []
    ),
    12: (
        [11, 5, 6], [10, 12, 4, 3, 3, 7, 9, 18], [], []
    ),
    13: (
        [11, 3], [12, 13, 16], [], [5]
    ),
    14: (
        [2, 4], [9, 14], [], []
    ),
    15: (
        [12, 5, 3, 16], [9, 10, 11, 15], [], []
    ),
    16: (
        [16], [9], [], [18]
    ),
    17: (
        [8, 14], [2, 17, 18], [7], []
    ),
    18: (
        [2, 16, 17], [11, 4, 9], [16], []
    )
}


class _BaseType(GameObject):
    def __init_(self, icon_manager: IconManager, proto: Enum):
        super().__init__(icon_manager)

        self.proto: CustomEnum = CustomEnum(proto)

    def get_base(self) -> Dict[str, Any]:
        return vars(self.proto)


class Type(_BaseType):
    def __init__(self, icon_manager: IconManager, proto: Enum):
        super().__init__(icon_manager)
        self.proto: CustomEnum = CustomEnum(proto)
        self.names: Dict[str, str] = {}

        self.effective_against: List[_BaseType] = []
        self.weak_against: List[_BaseType] = []
        self.resists: List[_BaseType] = []
        self.resisted_by: List[_BaseType] = []

        self.make_query()

    def make_query(self):
        self.query = {
            "type": (QueryType.customenum, self.proto),
            "name": (QueryType.qlist, self.names),
            "effective_against": (QueryType.qlist, self.effective_against),
            "weak_against": (QueryType.qlist, self.weak_against),
            "resists": (QueryType.qlist, self.resists),
            "resisted_by": (QueryType.qlist, self.resisted_by)
        }

    def get_full(self,
                 language: Union[str, Language] = Language.ENGLISH,
                 iconset: Union[str, int, IconSet] = IconSet.POGO) -> Dict[str, Any]:

        base = self.get_base()
        base.update({
            "name": self.get_name(language),
            "asset": self.icon_manager.montype(self, iconset),
            "effective_against": [t.get_base() for t in self.effective_against],
            "weak_against": [t.get_base() for t in self.weak_against],
            "resists": [t.get_base() for t in self.resists],
            "resisted_by": [t.get_base() for t in self.resisted_by]
        })
        return base


def _make_type_list(pogodata):
    print("Preparing Pokemon Types")
    type_proto = pogodata.get_enum("HoloPokemonType")
    base_types = {}

    for proto in type_proto:
        montype = Type(pogodata.icon_manager, proto)
        montype.names = pogodata.language_manager.get_all(proto.name)

        pogodata.types.append(montype)
        base_types[proto.value] = _BaseType(pogodata.icon_manager, proto)

    for montype in pogodata.types:
        effectiveness = EFFECTIVENESSES.get(montype.proto.id, ([], [], [], []))

        def __get_type_ids(index):
            return [base_types[id_] for id_ in effectiveness[index]]

        montype.effective_against += __get_type_ids(0)
        montype.weak_against += __get_type_ids(1)
        montype.resists += __get_type_ids(2)
        montype.resisted_by += __get_type_ids(3)

        montype.make_query()
