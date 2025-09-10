class ProgrammingError(Exception):
    """
    This exception indicates, that the library was used in an uninteded or incorrect way.
    """


class InitiliazationMissingError(Exception):
    """Indicates an invalid initilization state"""


class DuplicateTransformationName(Exception):
    """Indicates a duplicated transformation name in the context of the tansformation manager"""
