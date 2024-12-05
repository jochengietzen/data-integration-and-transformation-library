from typing import Any, Callable, Optional
from ditl.excpetions import ProgrammingError
from ditl.models.supported_library import SupportedLibrary


class DitlDataType:
    name: str
    description: Optional[str] = None

    cast_lookup: dict[str, Callable] = {}

    @classmethod
    def register_cast(
        cls, library: SupportedLibrary, cast_function: Callable[[Any], Any]
    ):
        cls.cast_lookup[library.key] = cast_function

    @classmethod
    def cast(cls, value: Any, target_library: SupportedLibrary) -> Any:
        if target_library.key not in cls.cast_lookup:
            raise ProgrammingError(
                f"Couldn't cast the data type {str(cls.__class__.__name__)} into target library {target_library.key}, "
                f"since there is no cast function registered for this. Please provide a cast function like "
                f"'{str(cls.__class__.__name__)}.register_cast(library=SupportedLibrary, "
                f"cast_function=lambda x: int(x))'"
            )
        return cls.cast_lookup[target_library.key](value)


sup = SupportedLibrary(key="cst")


class IntegerDataType(DitlDataType):
    name = "integer"
    description = "Integer"


IntegerDataType.register_cast(sup, lambda x: int(x))

if __name__ == "__main__":
    print(IntegerDataType().cast("4", target_library=sup))
