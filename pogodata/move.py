from typing import Dict, Any, Union

from .custom_types import DefaultEnum, CustomEnum, QueryType
from .misc import match_enum
from .icons import IconManager
from .gameobject import GameObject
from .language import Language
from .type import Type


class Move(GameObject):
    def __init__(self, icon_manager: IconManager, pve_entry, pvp_entry, proto):
        super().__init__(icon_manager, {**pve_entry, **pvp_entry})

        self.proto = CustomEnum(proto)
        self.names: Dict[str, str] = {}
        self.type: Type = Type(self.icon_manager, DefaultEnum(0))

        self.pve = { # TODO move stuff
            "power": 0,
            "energy_gain": 0,
            "duration": 0,
            "window": {
                "start": 0.0,
                "end": 0.0
            }
        }
        self.pvp = {
            "power": 0,
            "energy_gain": 0
        }

        self.query = {
            "move": (QueryType.customenum, self.proto),
            "name": (QueryType.qlist, self.names),
            "type": (QueryType.customenum, self.type.proto),
            "pve_power": (QueryType.qint, self.pve["power"]),
            "pve_energy_gain": (QueryType.qint, self.pve["energy_gain"]),
            "pve_duration": (QueryType.qint, self.pve["duration"]),
            "pve_window_start": (QueryType.qfloat, self.pve["window"]["start"]),
            "pve_window_end": (QueryType.qfloat, self.pve["window"]["end"]),
            "pvp_power": (QueryType.qint, self.pvp["power"]),
            "pvp_energy_gain": (QueryType.qint, self.pvp["energy_gain"])
        }

    def get_base(self) -> Dict[str, Any]:
        return {
            **vars(self.proto),
            "type": self.type.get_base()
        }

    def get_full(self, language: Union[str, Language] = Language.ENGLISH) -> Dict[str, Any]:
        base = self.get_base()
        base.update({
            "name": self.get_name(language),
            "pve": self.pve,
            "pvp": self.pvp
        })
        return base


def _make_move_list(pogodata):
    print("Preparing Moves")
    move_enum = pogodata.get_enum("HoloPokemonMove")
    pattern_pve = r"V\d{4}_MOVE_"
    pattern_pvp = r"^COMBAT_" + pattern_pve

    pvp_moves = {}

    for _, pvp_entry in pogodata.get_gamemaster(pattern_pvp+".*", "combatMove"):
        template = pvp_entry["uniqueId"]
        pvp_moves[template] = pvp_entry

    for _, pve_entry in pogodata.get_gamemaster("^" + pattern_pve + ".*", "moveSettings"):
        template = pve_entry["movementId"]
        pvp_entry = pvp_moves.get(template, {})
        move_proto = match_enum(move_enum, template)

        move = Move(pogodata.icon_manager, pve_entry, pvp_entry, move_proto)
        move.type = pogodata.get_types(type=move.raw.get("type", move.raw.get("pokemonType", 0)))[0]
        move.names = pogodata.language_manager.get_all("move_name_" + str(move.proto.id).zfill(4))
        pogodata.moves.append(move)
