from copy import deepcopy
from enum import Enum
from typing import Dict, Tuple, Callable, Any, Optional, Union

from .icons import IconManager
from .errors import UnknownLanguage
from .language import Language
from .custom_types import CustomEnum


class _CopyableClass:
    def copy(self):
        return deepcopy(self)


class BaseGameObject(_CopyableClass):
    def __bool__(self):
        return True

    def __repr__(self):
        return f"<{type(self).__name__}>"

    def get_base(self):
        return {}

    def get_full(self):
        return self.get_base()


class GameObject(BaseGameObject):
    def __init__(self,
                 icon_manager: Optional[IconManager] = None,
                 gamemaster_entry: Optional[Dict] = None):

        if icon_manager:
            self.icon_manager = icon_manager

        if gamemaster_entry:
            self.raw = gamemaster_entry
        else:
            self.raw = {}

        self.id: int = 0
        self.proto: CustomEnum = CustomEnum.default()
        self.names: Dict[str, str] = {}
        self.query: Dict[str, Tuple[Callable, Any]] = {}

    def __bool__(self):
        return bool(self.proto.id)

    def __repr__(self):
        return f"<{type(self).__name__} {self.proto.id}:{self.proto.tmpl}>"

    def get_name(self, language: Union[str, Language, None], var: Optional[dict] = None) -> str:
        try:
            if not language:
                language = Language.ENGLISH
            language = Language.match(language)
        except ValueError:
            raise UnknownLanguage(language)

        if not var:
            var = self.names
        return var.get(str(language.value), var[Language.ENGLISH.value])

    def compare(self, **kwargs) -> bool:
        if "id" in kwargs:
            if int(kwargs["id"]) == self.id:
                return True
            return False

        for key, value in kwargs.items():
            to_compare = self.query.get(key)

            if not to_compare:
                continue

            if not to_compare[0](value, to_compare[1]):
                return False

        return True
