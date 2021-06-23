import re

from enum import Enum
from math import floor
from typing import List, Dict, Any, Union

from .misc import CP_MULTIPLIERS, match_enum, get_repo_content, INGAME_ICONS, ICON_SHA
from .custom_types import CustomEnum, QueryType
from .icons import IconSet, IconManager
from .gameobject import GameObject, BaseGameObject
from .language import Language
from .move import Move
from .type import Type


GENERATION_MAXES = [151, 251, 386, 493, 649, 721, 809, 898]


class Generation(Enum):
    UNSET = 0
    KANTO = 1
    JOHTO = 2
    HOENN = 3
    SINNOH = 4
    UNOVA = 5
    KALOS = 6
    ALOLA = 7
    GALAR = 8


class PokemonType(Enum):
    UNSET = 0
    BASE = 1
    FORM = 2
    TEMP_EVOLUTION = 3
    COSTUME = 4


class Pokemon(GameObject):
    def __init__(self, icon_manager: IconManager, gamemaster_entry: dict):
        super().__init__(icon_manager, gamemaster_entry)

        self.names: Dict[str, str] = {}
        self.shiny: int = 0  # TODO shiny
        self.pokemon_type: PokemonType = PokemonType.BASE
        self.proto: CustomEnum = CustomEnum.default()
        self.form: CustomEnum = CustomEnum.default()
        self.costume: CustomEnum = CustomEnum.default()
        self.temp_evolution: CustomEnum = CustomEnum.default()
        self.rarity: CustomEnum = CustomEnum.default()

        gen: Generation = Generation.UNSET
        if self.proto.id > GENERATION_MAXES[-1]:
            gen = Generation.UNSET
        else:
            for gen_max in GENERATION_MAXES:
                if self.proto.id > gen_max:
                    gen = Generation(gen_max)
                    break
        self.generation: CustomEnum = CustomEnum(gen)

        self.moves: List[Move] = []
        self.elite_moves: List[Move] = []
        self.types: List[Type] = []
        self.evolutions: List[Evolution] = []
        self.temp_evolutions: List[TempEvolution] = []
        self.base_stats: List[int] = []
        self.assets: List[Dict[str, Union[str, int]]] = []
        self.info: Dict[str, Any] = {}

        self.male_ratio: float = 0
        self.female_ratio: float = 0
        self.genderless_ratio: float = 0

        self._has_female_asset: bool = False
        self._asset_suffix: str = ""
        self._asset_value: str = ""
        self.assets: List[str] = []

        self.id: int = 0
        self.make_internal_id()
        self.make_info()
        self.make_stats()
        self.make_query()

    def __repr__(self):
        return f"<Pokemon {self.id}:{self.proto.tmpl}:{self.form.tmpl}:{self.temp_evolution.tmpl}:{self.costume.tmpl}>"

    def get_base(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "shiny": 0,
            "pokemon_type": self.pokemon_type.name.lower(),
            "generation": vars(self.generation),
            "pokemon": vars(self.proto),
            "form": vars(self.form),
            "costume": vars(self.costume),
            "temp_evolution": vars(self.temp_evolution),
        }

    def get_full(self,
                 language: Union[str, Language] = Language.ENGLISH,
                 iconset: Union[str, int, IconSet] = IconSet.POGO) -> Dict[str, Any]:

        assets = []
        for gender, _ in enumerate(self.assets):
            wanted_assets = self.icon_manager.pokemon(self, gender, iconset)
            for icon_name, icon_url, is_shiny in wanted_assets:
                assets.append({
                    "name": icon_name,
                    "url": icon_url,
                    "shiny": is_shiny,
                    "female": bool(gender)
                })

        base = self.get_base()

        base.update({
            "name": self.get_name(language),
            "moves": [m.get_base() for m in self.moves],
            "elite_moves": [m.get_base() for m in self.elite_moves],
            "types": [t.get_base() for t in self.types],
            "evolutions": [evo.get_base() for evo in self.evolutions],
            "temp_evolutions": [evo.get_base() for evo in self.temp_evolutions],
            "base_stats": self.base_stats,
            "assets": assets,
            "info": self.info
        })
        return base

    @staticmethod
    def id_part(part: CustomEnum):
        if part.id > 0:
            return str(part.id)
        else:
            return ""

    def make_internal_id(self):
        if self.proto.id == 0:
            self.id = 0
        else:
            self.id = int(self.id_part(self.proto) + self.id_part(self.form) + self.id_part(self.costume)
                          + self.id_part(self.temp_evolution))

    def calculate_cp(self, level, ivs):
        multiplier = CP_MULTIPLIERS.get(level, 0.5)
        attack = self.base_stats[0] + ivs[0]
        defense = self.base_stats[1] + ivs[1]
        stamina = self.base_stats[2] + ivs[2]
        return floor((attack * defense**0.5 * stamina**0.5 * multiplier**2) / 10)

    def get_gender_asset(self, gender: int = 0):
        asset = "pokemon_icon_"
        if self._asset_suffix:
            asset += self._asset_suffix
        else:
            asset += str(self.proto.id).zfill(3) + "_"
            if self._asset_value:
                asset += self._asset_value
            else:
                asset += "0" + str(gender)
                if self.costume:
                    asset += "_" + str(self.costume.id).zfill(2)
        return asset

    def make_assets(self):
        self.assets = []
        self.assets.append(self.get_gender_asset())
        if self._has_female_asset:
            self.assets.append(self.get_gender_asset(1))

    def make_stats(self):
        stats = self.raw.get("stats")
        if not stats:
            self.base_stats = []
            return
        self.base_stats = [stats["baseAttack"], stats["baseDefense"], stats["baseStamina"]]

    def make_info(self):
        raw_encounter: dict = self.raw.get("encounter", {})

        self.info["rarity"]: str = self.rarity.tmpl.lower()

        self.info["bonus_stardust"]: int = raw_encounter.get("bonusStardustCaptureReward", 0)
        self.info["bonus_candy"]: int = raw_encounter.get("bonusCandyCaptureReward", 0)
        self.info["bonus_xl"]: int = raw_encounter.get("bonusXlCandyCaptureReward", 0)

        self.info["deployable"]: bool = self.raw.get("isDeployable", False)
        self.info["tradable"]: bool = self.raw.get("isTradable", False)
        self.info["transferable"]: bool = self.raw.get("isTransferable", False)

        self.info["buddy_distance"]: float = self.raw.get("kmBuddyDistance", 0)
        self.info["height"]: float = self.raw.get("heightStdDev", 0)
        self.info["weight"]: float = self.raw.get("weightStdDev", 0)

        self.info["gender_ratio"] = {
            "male": self.male_ratio,
            "female": self.female_ratio,
            "genderless": self.genderless_ratio
        }

        raw_third_move: dict = self.raw.get("thirdMove", {})
        third_move = self.info["third_move"] = dict()
        third_move["candy"]: int = raw_third_move.get("stardustToUnlock", 0)
        third_move["stardust"]: int = raw_third_move.get("candyToUnlock", 0)

        encounter = self.info["encounter"] = dict()
        encounter["base_capture_rate"]: float = encounter.get("baseCaptureRate", 0)
        encounter["flee_rate"]: float = encounter.get("baseFleeRate", 0)

        attack = encounter["attack"] = dict()
        attack["duration"]: float = raw_encounter.get("attackTimerS", 0)
        attack["probability"]: float = raw_encounter.get("attackProbability", 0)

        dodge = encounter["dodge"] = dict()
        dodge["duration"]: float = raw_encounter.get("dodgeDurationS", 0)
        dodge["probability"]: float = raw_encounter.get("dodgeProbability", 0)
        dodge["distance"]: float = raw_encounter.get("dodgeDistance", 0)

    def make_query(self):
        self.query = {
            "id": (QueryType.int_, self.id),
            "pokemon": (QueryType.customenum, self.proto),
            "name": (QueryType.qlist, self.names),
            "shiny": (QueryType.qint, self.shiny),
            "generation": (QueryType.customenum, self.generation),
            "form": (QueryType.customenum, self.form),
            "costume": (QueryType.customenum, self.costume),
            "temp_evolution": (QueryType.customenum, self.temp_evolution),
            "assets": (QueryType.qlist, self.assets),
            "rarity": (QueryType.customenum, self.rarity),
            "bonus_stardust": (QueryType.qint, self.info["bonus_stardust"]),
            "bonus_candy": (QueryType.qint, self.info["bonus_candy"]),
            "bonus_xl": (QueryType.qint, self.info["bonus_xl"]),
            "deployable": (QueryType.bool_, self.info["deployable"]),
            "tradable": (QueryType.bool_, self.info["tradable"]),
            "transferable": (QueryType.bool_, self.info["transferable"]),
            "buddy_distance": (QueryType.qfloat, self.info["buddy_distance"]),
            "weight": (QueryType.qfloat, self.info["weight"]),
            "height": (QueryType.qfloat, self.info["height"]),
            "male_ratio": (QueryType.qfloat, self.male_ratio),
            "female_ratio": (QueryType.qfloat, self.female_ratio),
            "genderless_ratio": (QueryType.qfloat, self.genderless_ratio),
            "base_capture_rate": (QueryType.qfloat, self.info["encounter"]["base_capture_rate"]),
            "flee_rate": (QueryType.qfloat, self.info["encounter"]["flee_rate"])
        }


class _BaseEvolution(BaseGameObject):
    def __init__(self, pokemon: Pokemon):
        super().__init__()
        self.into: Pokemon = pokemon

    def get_base(self):
        base = vars(self).copy()
        base.pop("into")
        base["into"] = self.into.get_base()
        return base


class Evolution(_BaseEvolution):
    def __init__(self, pokemon: Pokemon, candy: int = 0, quest: Any = None):
        super().__init__(pokemon)
        self.candy: int = candy
        self.quest: Any = quest


class TempEvolution(_BaseEvolution):
    def __init__(self, pokemon: Pokemon, energy_initial: int = 0, energy_subsequent: int = 0):
        super().__init__(pokemon)
        self.energy_initial: int = energy_initial
        self.energy_subsequent: int = energy_subsequent


def __typing(pogodata, mon: Pokemon, type1ref: str, type2ref: str):
    # makes Pokemon types
    typings = [mon.raw.get(type1ref), mon.raw.get(type2ref)]
    for typing in typings:
        if typing:
            mon.types.append(pogodata.get_types(type=typing)[0])


def __append_evolution(pogodata, mon: Pokemon, to_append: list):
    # adds evolutions to Pokemon.evolutions
    evolutions = mon.raw.get("evolutionBranch", [])
    for evo_raw in evolutions:
        if "temporaryEvolution" in evo_raw:
            continue
        form: str = evo_raw.get("form")
        candy: int = evo_raw.get("candyCost", 0)
        # TODO evolution quests
        if not form:
            evo = pogodata.get_mons(pokemon=evo_raw["evolution"])[0]
        else:
            evo = pogodata.get_mons(form=form)[0]
        to_append.append(Evolution(evo, candy))
        __append_evolution(pogodata, evo, to_append)


def __handle_match(icon):
    icon = icon.replace(".png", "")
    icon = icon.replace("Images/Pokemon/", "")
    icon = icon.replace("_01", "_00", 1)

    return icon


def _make_mon_list(pogodata):
    forms = pogodata.get_enum("Form")
    megas = pogodata.get_enum("HoloTemporaryEvolutionId")
    mon_ids = pogodata.get_enum("HoloPokemonId")
    costumes = pogodata.get_enum("Costume")
    rarities = pogodata.get_enum("HoloPokemonClass", remove="POKEMON_CLASS_")

    # Getting spawn ratios
    print("Getting female/male ratios")
    gender_ratios = {}
    for templateid, entry in pogodata.get_gamemaster(r"^SPAWN_V\d{4}_POKEMON_.*", "genderSettings"):
        gender_ratios[templateid.strip("SPAWN_")] = entry.get("gender", {})

    # Creating a base mon list based on GM entries
    print("Pokemon: Preparing Base Pokemon")
    pattern = r"^V\d{4}_POKEMON_"
    for templateid, entry in pogodata.get_gamemaster(pattern+".*", "pokemonSettings"):
        template = entry.get("form", entry.get("pokemonId"))

        if not template:
            continue

        mon = Pokemon(pogodata.icon_manager, entry)
        mon.proto = CustomEnum(match_enum(mon_ids, entry.get("pokemonId", 0)))
        mon.form = CustomEnum(match_enum(forms, entry.get("form", 0)))
        mon.costume = CustomEnum(costumes(0))
        mon.temp_evolution = CustomEnum(megas(0))
        raw_rarity = entry.get("rarity", 0).strip("POKEMON_RARITY")
        mon.rarity = CustomEnum(match_enum(rarities, raw_rarity))

        gender_settings = gender_ratios.get(templateid, {})
        mon.male_ratio = gender_settings.get("malePercent")
        mon.female_ratio = gender_settings.get("femalePercent")

        locale_key = "pokemon_name_" + str(mon.proto.id).zfill(4)
        mon.names = pogodata.language_manager.get_all(locale_key)

        mon.moves += [pogodata.get_moves(move=t)[0] for t in mon.raw.get("quickMoves", [])]
        mon.moves += [pogodata.get_moves(move=t)[0] for t in mon.raw.get("cinematicMoves", [])]
        
        mon.elite_moves = [pogodata.get_moves(move=t)[0] for t in mon.raw.get("eliteQuickMove", [])]
        mon.elite_moves = [pogodata.get_moves(move=t)[0] for t in mon.raw.get("eliteCinematicMove", [])]

        mon.make_assets()
        mon.make_internal_id()
        __typing(pogodata, mon, "type", "type2")

        mon.make_query()

        pogodata.mons.append(mon)

        # Handling Temp (Mega) Evolutions
        for temp_evo in mon.raw.get("tempEvoOverrides", []):
            evo: Pokemon = mon.copy()
            evo.pokemon_type = PokemonType.TEMP_EVOLUTION

            temp_evolution_template = temp_evo.get("tempEvoId")
            evo.temp_evolution = CustomEnum(match_enum(megas, temp_evolution_template))

            evo.raw = temp_evo
            evo.names = pogodata.language_manager.get_all(locale_key + "_" + str(evo.temp_evolution.id).zfill(4))

            evo.types = []
            __typing(pogodata, evo, "typeOverride1", "typeOverride2")

            evo.make_stats()
            evo.make_info()
            evo.make_internal_id()
            evo.make_assets()
            evo.make_query()

            pogodata.mons.append(evo)

            evo_branch = mon.raw.get("evolutionBranch", [])
            energy_initial = 0
            energy_subsequent = 0
            for possible_evo in evo_branch:
                if possible_evo.get("temporaryEvolution") == evo.temp_evolution.tmpl:
                    energy_initial: int = possible_evo.get("temporaryEvolutionEnergyCost", 0)
                    energy_subsequent: int = possible_evo.get("temporaryEvolutionEnergyCostSubsequent", 0)
                    break
            mon.temp_evolutions.append(TempEvolution(evo, energy_initial, energy_subsequent))

    # Going through GM Forms and adding missing Forms (Unown, Spinda) and making in-game assets
    print("Pokemon: Adding missing forms")
    for template, formsettings in pogodata.get_gamemaster(r"^FORMS_V\d{4}_POKEMON_.*", "formSettings"):
        form_list = formsettings.get("forms", [])
        for form in form_list:
            formname = form.get("form")
            if formname:
                mon = pogodata.get_mons(form=form.get("form"))
            if not formname or not mon:
                mon = pogodata.get_mons(pokemon=formsettings["pokemon"])[0]
                mon = mon.copy()
                mon.pokemon_type = PokemonType.FORM
                mon.form = CustomEnum(match_enum(forms, form.get("form", 0)))
                mon.make_query()
                pogodata.mons.append(mon)
            else:
                mon = mon[0]

            asset_value = form.get("assetBundleValue")
            asset_suffix = form.get("assetBundleSuffix")
            if asset_value or asset_suffix:
                mon.asset_value = asset_value
                mon.asset_suffix = asset_suffix

            mon.make_assets()
            mon.make_info()
            mon.make_stats()
            mon.make_internal_id()
            mon.make_query()

    # Temp Evolution assets
    print("Pokemon: Re-doing Temp Evolutions for proper assets")
    evo_gm = pogodata.get_gamemaster(
        r"^TEMPORARY_EVOLUTION_V\d{4}_POKEMON_.*",
        "temporaryEvolutionSettings"
    )
    for base_template, evos in evo_gm:
        base_template = evos.get("pokemonId", "")
        evos = evos.get("temporaryEvolutions", [])
        for temp_evo_raw in evos:
            mons = pogodata.get_mons(
                pokemon=base_template,
                temp_evolution=temp_evo_raw["temporaryEvolutionId"]
            )
            for mon in mons:
                mon.asset_value = temp_evo_raw["assetBundleValue"]
                mon.make_assets()
                mon.make_query()

    # Making Pokemon.evolutions attributes
    print("Pokemon: Appending evolutions")
    for mon in pogodata.mons:
        evos = []
        __append_evolution(pogodata, mon, evos)
        mon.evolutions = evos

    # Costumes
    print("Pokemon: Checking costumes & female assets")
    icons = get_repo_content(INGAME_ICONS, ICON_SHA)
    base_regex = r"Images/Pokemon/pokemon_icon{}.png"

    for icon in icons:
        gender_match = re.match(base_regex.format(r"_\d{3}_01(?!(_\d*)_?shiny).*"), icon)
        if gender_match:
            og_asset = __handle_match(icon)

            mons: List[Pokemon] = pogodata.get_mons(assets=og_asset)

            for mon in mons:
                mon._has_female_asset = True
                mon.make_assets()

    for icon in icons:
        costume_match = re.match(base_regex.format(r"(_\d*){3}(?!\d*_?shiny)"), icon)

        if costume_match:
            icon = __handle_match(icon)

            costume = re.findall(r"_\d*$", icon)[0]
            og_asset = re.sub(costume + "$", "", icon)
            costume = int(costume.strip("_"))

            mon = pogodata.get_mons(assets=og_asset)[0]

            copy: Pokemon = mon.copy()
            copy.costume = CustomEnum(costumes(costume))
            copy.pokemon_type = PokemonType.COSTUME
            copy.make_assets()
            copy.make_internal_id()
            copy.make_query()
            pogodata.mons.append(copy)

    # sort final list by mon, form, temp evo, costume
    pogodata.mons = sorted(pogodata.mons,
                           key=lambda m: (m.proto.id, m.form.id, m.temp_evolution.id, m.costume.id))
