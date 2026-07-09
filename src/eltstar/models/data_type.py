from collections import defaultdict
from collections.abc import Callable
from typing import Any, ClassVar, NamedTuple, TypeVar

from eltstar.base_model import BaseModel


class FromToMethod(NamedTuple):
    from_method: Callable[[Any], "DataType"]
    to_method: Callable[["DataType"], Any]


class DataType(BaseModel):
    _from_and_to_engine_methods: ClassVar[dict[str, dict[str, FromToMethod]]] = defaultdict(dict)
    _engine_type_to_engine_identifier: ClassVar[dict[str, dict[Any, str]]] = defaultdict(dict)
    _engine_identifier_to_engine_type: ClassVar[dict[str, dict[str, Any]]] = defaultdict(dict)

    @classmethod
    def register_from_and_to_methods(
        cls,
        engine_identifier: str,
        engine_type: Any,
        from_method: Callable[[Any], "DataType"],
        to_method: Callable[["DataType"], Any],
    ) -> type["DataType"]:
        """aigen_start
        Register bidirectional conversion methods between this DataType and an engine-native type.
        aigen_end"""
        cls._from_and_to_engine_methods[cls.__name__][engine_identifier] = FromToMethod(
            from_method=from_method, to_method=to_method
        )
        cls._engine_type_to_engine_identifier[cls.__name__][engine_type] = engine_identifier
        cls._engine_identifier_to_engine_type[cls.__name__][engine_identifier] = engine_type
        return cls

    @classmethod
    def to_engine_type(cls, engine_identifier: str) -> Any:
        """aigen_start
        Return the engine-native type corresponding to this DataType for the given engine identifier.
        aigen_end"""
        type_ = cls._engine_identifier_to_engine_type[cls.__name__].get(engine_identifier, None)
        if type_ is None:
            raise RuntimeError(f"The data type {cls.__name__} has no engine {engine_identifier} registered")
        return type_


DataTypeType = TypeVar("DataTypeType", bound=DataType)  # pylint: disable=invalid-name
