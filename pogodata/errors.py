from .language import Language


class PogoDataException(Exception):
    """Base exception for PogoData Errors.
    """


class QueryException(Exception):
    """Base exception for Query Errors.
    """


class InvalidQueryArgument(QueryException):
    def __init__(self, argument):
        message = f"Invalid query argument: `{argument}`"
        super().__init__(message)


class NoORANDMixingInQList(QueryException):
    def __init__(self, argument):
        message = f"Cannot mix and match | and , in qlists. Argument: `{argument}`"
        super().__init__(message)


class UnknownLanguage(QueryException):
    def __init__(self, language):
        langs = ", ".join([l_.name.lower() for l_ in Language])
        message = f"Unknown language `{language}`. Please use one of the following: {langs}"
        super().__init__(message)
