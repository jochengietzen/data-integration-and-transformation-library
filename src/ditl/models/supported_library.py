import enum
from ditl.base_model import BaseModel
from ditl.excpetions import ProgrammingError


class SupportedLibrary(BaseModel):
    activated: bool = False
    key: str

    required_libraries: list[str] = []
    testing_libraries: list[str] = []


class SupportedLibraries:

    def __init__(self) -> None:
        self.libraries: dict[str, SupportedLibrary] = {}

    def register_library(self, library: SupportedLibrary):
        """
        :param library: Library to register
        :raises ProgrammingError: If the library was already registered
        :return: Void
        """
        if library.key in self.libraries:
            raise ProgrammingError(f"Library {library} is already registered!")
        self.libraries[library.key] = library

    def to_enum(self) -> enum.Enum:
        """
        :return: Enum of supported libraries
        """
        return enum.Enum(
            "SupportedLibrariesEnum",
            {key.upper(): library.key for key, library in self.libraries.items()},
        )

    def __getitem__(self, key: str):
        return self.libraries[key]
