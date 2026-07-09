from collections.abc import Callable
from typing import Any, ClassVar, Union

from pydantic import RootModel

from eltstar.base_model import BaseModel
from eltstar.models.data_type import DataType


class SchemaField(BaseModel):
    name: str
    type_: DataType
    nullable: bool

    def to_engine_type(self, engine_identifier: str) -> Any:
        """Convenience method for engine type conversion"""
        return self.type_.to_engine_type(engine_identifier)


class SchemaStruct(BaseModel):
    name: str
    fields: list[Union["SchemaStruct", SchemaField]]
    nullable: bool

    def to_engine_type(self, engine_identifier: str) -> Any:
        """not implemented"""
        raise NotImplementedError("No definition for a SchemaStruct to engine type exists!")


class Schema(RootModel[list[SchemaStruct | SchemaField]]):
    _from_engine_methods: ClassVar[dict[str, tuple[type[Any], Callable[[Any], "Schema"]]]] = {}
    _to_engine_methods: ClassVar[dict[str, Callable[["Schema"], Any]]] = {}
    # provides schema for a given instance of Columns
    # Compostition Approach

    @classmethod
    def register_from_engine_schema(
        cls,
        engine_identifier: str,
        engine_schema_type: type[Any],
        from_method: Callable[[Any], "Schema"],
        to_method: Callable[["Schema"], Any],
    ):
        """aigen_start
        Register conversion functions between the engine's native schema format and the eltstar Schema.
        aigen_end"""
        if cls._from_engine_methods is None:
            cls._from_engine_methods = {}
        cls._from_engine_methods[engine_identifier] = (engine_schema_type, from_method)
        cls._to_engine_methods[engine_identifier] = to_method

    @classmethod
    def from_engine_schema(cls, schema: Any) -> "Schema":
        """aigen_start
        Convert an engine-native schema object into a eltstar Schema by dispatching on its type.
        aigen_end"""
        for schema_type, func in cls._from_engine_methods.values():
            if isinstance(schema, schema_type):
                return func(schema=schema)  # type: ignore
        raise RuntimeError(f"Engine for type {type(schema)} not defined!")

    def to_engine_schema(self, engine_identifier: str) -> Any:
        """aigen_start
        Convert this eltstar Schema to the engine-native schema format for the given engine identifier.
        aigen_end"""
        func = self._to_engine_methods.get(engine_identifier, None)
        if func is None:
            raise RuntimeError(f"Engine {engine_identifier} has no to engine schema defined!")
        return func(schema=self)  # type: ignore
