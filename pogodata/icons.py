import re
from enum import Enum
from typing import Tuple, Dict, Union

from .misc import match_enum, get_repo_content


class IconSet(Enum):
    POGO = 0
    POGO_OPTIMIZED = 1
    POGO_OUTLINE = 2
    #COPYRIGHTSAFE = 10
    #THEARTIFICIAL = 11
    HOME = 20
    HOME_OUTLINE = 21
    SHUFFLE = 30
    SUGMIORI_OPTIMIZED = 40
    DERP_AFD = 50
    DERP_FLORK = 51
    #PIXEL_GEN3 = 60


class IconType(Enum):
    PMSF = 0
    UICONS = 1
    POKEMINERS = 2


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
    IconSet.SUGMIORI_OPTIMIZED: {
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

        if self.type == IconType.PMSF:
            match = re.match(r"https:\/\/raw\.githubusercontent\.com\/([^\/]*)\/([^\/]*)\/([^\/]*).*", self.url)
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
        iconset = match_enum(IconSet, iconset)
        return self.iconsets[iconset]

    def pokemon(self,
                mon,
                gender: int = 0,
                iconset: Union[str, int, IconSet] = IconSet.POGO) -> Tuple[str, str]:
        iconset = self.get_iconset(iconset)

        if iconset.type == IconType.POKEMINERS:
            return mon.assets[gender], iconset.url + "Images/Pokemon/" + mon.assets[gender] + ".png"
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
                        if icon in iconset.icons:
                            return icon, iconset.url + icon + ".png"
            default = "pokemon_icon_000_00"
            return default, iconset.url + default + ".png"
    
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
                "name": montype.type.tmpl,
                "url": iconset.url + "Images/Types/" + montype.type.tmpl + ".png"
            }
    
    def weather(self, weather, is_day=True):
        if self.type == IconType.POKEMINERS:
            westr = weather.template.lower()
            if weather.id == 1 and is_day:
                westr = "sunny"
            elif weather.id == 2:
                westr = "rain"
            elif weather.id == 3:
                westr = "partlycloudy_"
                if is_day:
                    westr += "day"
                else:
                    westr += "night"
            elif weather.id == 4:
                westr = "cloudy"
            
            return self.url + f"Images/Weather/weatherIcon_small_{westr}.png"

    def grunt(self, grunt):
        if self.type == IconType.PMSF:
            return self.url + "grunt/" + str(grunt.id) + ".png"
