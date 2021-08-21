from __future__ import annotations
import re
from enum import Enum
from typing import Tuple, Dict, Union, List, TYPE_CHECKING, Optional

from .misc import get_repo_content, EnumMatcher

if TYPE_CHECKING:
    from .pokemon import Pokemon


class IconSet(EnumMatcher):
    POGO = 0
    POGO_OPTIMIZED = 1
    POGO_OUTLINE = 2
    #COPYRIGHTSAFE = 10
    #THEARTIFICIAL = 11
    HOME = 20
    HOME_OUTLINE = 21
    SHUFFLE = 30
    SUGIMORI_OPTIMIZED = 40
    DERP_AFD = 50
    DERP_FLORK = 51
    #PIXEL_GEN3 = 60


class IconType(Enum):
    PMSF = 0
    UICONS = 1
    POKEMINERS = 2


class Icon:
    name: str
    url: str

    def __init__(self, url, name):
        self.name = name
        self.url = url


class PokemonIcon(Icon):
    female: bool
    shiny: bool

    def __init__(self, url: str, name: str, female: bool, shiny: bool):
        super().__init__(url, name)
        self.female = female
        self.shiny = shiny


class IconGenerator:
    @staticmethod
    def pokemon(iconset: IconSetManager, pokemon: Pokemon):
        pass


class PokeMinersGenerator(IconGenerator):
    @staticmethod
    def pokemon(iconset: IconSetManager, pokemon: Pokemon):
        forms = []
        costumes = []

        if pokemon.pokemon_type.value == 3:
            forms.append(".f" + pokemon.temp_evolution.tmpl.replace("TEMP_EVOLUTION_", ""))
        else:
            form = pokemon.form.tmpl.replace(pokemon.proto.tmpl, "").strip("_")
            if form not in ["NORMAL", "SHADOW", "PURIFIED", ""]:
                forms.append(".f" + form)
        forms.append("")

        costume = pokemon.costume.tmpl
        if pokemon.costume.id > 0 and costume:
            costumes.append(".c" + costume)
        costumes.append("")

        name_template = "pm" + str(pokemon.proto.id) + "{}.icon"
        url_template = iconset.url + "Images/Pokemon/Addressable%20Assets/{}.png"

        found = False
        name = ""
        if pokemon.proto.id == 888:
            print(forms)
            print(costumes)
        for form in forms:
            if found:
                break
            for costume in costumes:
                name = name_template.format(form + costume)
                if name + ".png" in iconset.icons:
                    found = True
                    break

        if found:
            icon = PokemonIcon(url_template.format(name), name, False, False)
            icons = [icon]
            gender_name = name.replace(".icon", ".g2.icon")
            if gender_name + ".png" in iconset.icons:
                gender_icon = PokemonIcon(url_template.format(gender_name), gender_name, True, False)
                icons.append(gender_icon)

            for icon in icons.copy():
                shiny_name = icon.name.replace(".icon", ".s.icon")
                if shiny_name + ".png" in iconset.icons:
                    shiny_icon = PokemonIcon(url_template.format(shiny_name), shiny_name, icon.female, True)
                    icons.append(shiny_icon)

        else:
            icons = []
            asset = "pokemon_icon_"
            for shiny in ["", "_shiny"]:
                for gender in [0, 1]:
                    if pokemon._asset_suffix:
                        asset += pokemon._asset_suffix
                    else:
                        asset += str(pokemon.proto.id).zfill(3) + "_"
                        if pokemon._asset_value:
                            asset += str(pokemon._asset_value)
                        else:
                            asset += "0" + str(gender)
                            if pokemon.costume:
                                asset += "_" + str(pokemon.costume.id).zfill(2)
                    asset += shiny
                    if asset + ".png" in iconset.icons:
                        icon = PokemonIcon(iconset.url + "Images/Pokemon/" + asset + ".png", asset, bool(gender), bool(shiny))
                        icons.append(icon)

        return [vars(i) for i in icons]


ICON_DETAILS = {
    IconSet.POGO: {
        "url": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/",
        "type": IconType.POKEMINERS
    },
    IconSet.POGO_OPTIMIZED: {
        "url": "https://raw.githubusercontent.com/whitewillem/PogoAssets/resized/no_border/",
        "type": IconType.PMSF
    },
    IconSet.POGO_OUTLINE: {
        "url": "https://raw.githubusercontent.com/whitewillem/PogoAssets/resized/icons_large/",
        "type": IconType.PMSF
    },
    IconSet.HOME: {
        "url": "https://raw.githubusercontent.com/nileplumb/PkmnHomeIcons/master/pmsf/",
        "type": IconType.PMSF
    },
    IconSet.HOME_OUTLINE: {
        "url": "https://raw.githubusercontent.com/nileplumb/PkmnHomeIcons/master/pmsf_OS_128/",
        "type": IconType.PMSF
    },
    IconSet.SHUFFLE: {
        "url": "https://raw.githubusercontent.com/nileplumb/PkmnShuffleMap/master/PMSF_icons_large/",
        "type": IconType.PMSF
    },
    IconSet.SUGIMORI_OPTIMIZED: {
        "url": "https://raw.githubusercontent.com/xxleevo/monicons/master/classic/",
        "type": IconType.PMSF
    },
    IconSet.DERP_AFD: {
        "url": "https://raw.githubusercontent.com/ccev/pogoafd/master/sprites/",
        "type": IconType.PMSF
    },
    IconSet.DERP_FLORK: {
        "url": "https://raw.githubusercontent.com/xxleevo/monicons/master/derpy/",
        "type": IconType.PMSF
    }
}


class IconSetManager:
    def __init__(self, iconset: IconSet):
        self.iconset = iconset
        self.details = ICON_DETAILS[self.iconset]
        self.url = self.details["url"]
        self.type = self.details["type"]

        match = re.match(r"https://raw\.githubusercontent\.com/([^/]*)/([^/]*)/([^/]*).*", self.url)
        user, repo, branch = match.groups()

        base_api = f"https://api.github.com/repos/{user}/{repo}/"
        sha_url = base_api + f"branches/{branch}"
        files_url = base_api + "git/trees/{sha}?recursive=true"
        icons = get_repo_content(files_url, sha_url)
        self.icons = [re.sub(r"[^\/]*\/", "", i) for i in icons]


class IconManager:
    def __init__(self):
        self.iconsets: Dict[IconSet, IconSetManager] = {}
        for iconset in IconSet:
            print(f"IconManager: Preparing iconset {iconset.name}")
            self.iconsets[iconset] = IconSetManager(iconset)
            break # TODO remove after testing

    def get_iconset(self, iconset: Union[str, int, IconSet] = IconSet.POGO):
        iconset = IconSet.match(iconset)
        return self.iconsets[iconset]

    def pokemon(self,
                mon,
                gender: int = 0,
                iconset: Union[str, int, IconSet] = IconSet.POGO):
        """
        Returns a list containg tuples: (icon name, icon url, is_shiny?)
        """
        iconset = self.get_iconset(iconset)
        result = []

        if iconset.type == IconType.POKEMINERS:
            return PokeMinersGenerator.pokemon(iconset, mon)
        elif iconset.type == IconType.PMSF:
            for monid in (mon.proto.id, 0):
                for form in (mon.form.id, 0):
                    for costm in (mon.costume.id, 0):
                        if form == 0:
                            formstr = "_00"
                        else:
                            formstr = "_" + str(form)

                        if costm > 0:
                            costr = "_" + str(costm)
                        else:
                            costr = ""

                        icon = "pokemon_icon_" + str(monid).zfill(3) + formstr + costr
                        if icon + ".png" in iconset.icons:
                            return [(icon, iconset.url + icon + ".png", False)]
            default = "pokemon_icon_000_00"
            return [(default, iconset.url + default + ".png", False)]
    
    def item(self, item, amount=1):
        if self.type == IconType.POKEMINERS:
            url = ICON_DETAILS[IconSet.POGO_OPTIMIZED]["url"]
        elif self.type == IconType.PMSF:
            url = self.url
        return url + "rewards/reward_" + str(item.id) + "_" + str(amount) + ".png"

    def montype(self, montype, iconset: Union[str, int, IconSet] = IconSet.POGO) -> Dict[str, str]:
        iconset = self.get_iconset(iconset)
        if iconset.type == IconType.POKEMINERS:
            return {
                "name": montype.proto.tmpl.lower(),
                "url": iconset.url + "Images/Types/" + montype.proto.tmpl.lower() + ".png"
            }
    
    def weather(self, weather, iconset: Union[str, int, IconSet] = IconSet.POGO):
        iconset = self.get_iconset(iconset)

        if iconset.type == IconType.POKEMINERS:
            icons = []

            for is_day in [True, False]:
                westr = weather.proto.tmpl.lower()
                if weather.proto.id == 1 and is_day:
                    westr = "sunny"
                elif weather.proto.id == 2:
                    westr = "rain"
                elif weather.proto.id == 3:
                    westr = "partlycloudy_"
                    if is_day:
                        westr += "day"
                    else:
                        westr += "night"
                elif weather.proto.id == 4:
                    westr = "cloudy"

                if weather.proto.id not in [1, 3]:
                    is_day = None

                name = f"weatherIcon_small_{westr}"

                icon = {
                    "name": name,
                    "url": iconset.url + f"Images/Weather/{name}.png",
                    "day": is_day
                }
                icons.append(icon)
            return icons

    def grunt(self, grunt):
        if self.type == IconType.PMSF:
            return self.url + "grunt/" + str(grunt.id) + ".png"
