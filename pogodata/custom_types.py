from enum import Enum
from typing import Union, Any

from .errors import InvalidQueryArgument, NoORANDMixingInQList


class DefaultEnum(Enum):
    UNSET = 0


class CustomEnum:
    def __init__(self, enum: Enum):
        self.id = enum.value
        self.tmpl = enum.name

    def __bool__(self):
        return bool(self.id)

    @classmethod
    def default(cls):
        return cls(DefaultEnum.UNSET)


class QueryType:
    @staticmethod
    def int_(original: int, to_match: int):
        return original == to_match

    @staticmethod
    def string(original: str, to_match: str):
        return original == to_match

    @staticmethod
    def bool_(original: bool, to_match: bool):
        return original == to_match

    @staticmethod
    def float_(original: float, to_match: float):
        return original == to_match

    @staticmethod
    def __qint_or_qfloat(original, to_match, intfloat):
        try:
            return int(original) == to_match
        except ValueError:
            pass

        if original.startswith(">"):
            try:
                return int(original[1:]) < to_match
            except ValueError:
                raise InvalidQueryArgument(original)

        if original.startswith("<"):
            try:
                return int(original[1:]) > to_match
            except ValueError:
                raise InvalidQueryArgument(original)

        raise InvalidQueryArgument(original)

    @staticmethod
    def customenum(original: Union[str, int], to_match: CustomEnum):
        return original == to_match.id or str(original) == to_match.tmpl

    @staticmethod
    def qint(original: Union[str, int], to_match: int):
        QueryType.__qint_or_qfloat(original, to_match, int)

    @staticmethod
    def qfloat(original: Union[str, float], to_match: float):
        QueryType.__qint_or_qfloat(original, to_match, float)

    @staticmethod
    def qlist(original: Any, to_match: list):
        if original.startswith(":"):
            match_complete = True
            original = original[1:].replace("|", ",")
        else:
            match_complete = False

        if "," in original and "|" in original:
            raise NoORANDMixingInQList(original)

        elif "," in original:
            original_list = set(original.split(","))
            if len([o for o in original_list if o in to_match]) >= len(original_list):
                return True

        elif "|" in original:
            original_list = original.split("|")
            if set(original_list) & set(to_match):
                return True

        else:
            return bool(original in to_match)