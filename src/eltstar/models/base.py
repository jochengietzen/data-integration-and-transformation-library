from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    NamedTuple,
    Optional,
    TypeVar,
    Union,
)

from pydantic import Field, RootModel, model_validator

from ditl.base_model import BaseModel
from ditl.config import EnvironmentConfigType, RuntimeConfigType
from ditl.models.expectations import RowLevelColumnExpectation
from ditl.models.generation import Generation

if TYPE_CHECKING:
    from ditl.models.table import Table


class TablePath(BaseModel, ABC):
    @abstractmethod
    def full_path(
        self,
        runtime_config: RuntimeConfigType,
        environment_config: EnvironmentConfigType,
        *args: Any,
        **kwargs: dict[str, Any],
    ) -> str:
        """aigen_start
        Return the fully resolved path string for the table given the runtime and environment configuration.
        aigen_end"""


class Constraint(BaseModel):
    pass


class FromToMethod(NamedTuple):
    from_method: Callable[[Any], "DataType"]
    to_method: Callable[["DataType"], Any]


class DataType(BaseModel):
    _from_and_to_engine_methods: ClassVar[dict[str, dict[str, FromToMethod["DataType"]]]] = defaultdict(dict)
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


class IntegerType(DataType):
    pass


class FloatType(DataType):
    pass


class StringType(DataType):
    pass


#########
DataTypeType = TypeVar("DataTypeType", bound=DataType)  # pylint: disable=invalid-name


class SchemaField(BaseModel):
    name: str
    type_: DataType
    nullable: bool


class SchemaStruct(BaseModel):
    name: str
    fields: list[Union["SchemaStruct", SchemaField]]
    nullable: bool


class Column(BaseModel):
    name: str = Field(..., pattern=r"^[a-zA-Z0-9-_]+$")
    data_type: DataTypeType
    constraints: list[Constraint] = Field(default_factory=list)
    expectations: list[RowLevelColumnExpectation] = Field(default_factory=list)
    generation: Generation | None = None
    description: str | None = None
    is_primary_key: bool = False
    is_nullable: bool = False
    foreign_key: Optional["ForeignKey"] = None


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
        Register conversion functions between the engine's native schema format and the DITL Schema.
        aigen_end"""
        if cls._from_engine_methods is None:
            cls._from_engine_methods = {}
        cls._from_engine_methods[engine_identifier] = (engine_schema_type, from_method)
        cls._to_engine_methods[engine_identifier] = to_method

    @classmethod
    def from_engine_schema(cls, schema: Any) -> "Schema":
        """aigen_start
        Convert an engine-native schema object into a DITL Schema by dispatching on its type.
        aigen_end"""
        for schema_type, func in cls._from_engine_methods.values():
            if isinstance(schema, schema_type):
                return func(schema=schema)
        raise RuntimeError(f"Engine for type {type(schema)} not defined!")

    def to_engine_schema(self, engine_identifier: str) -> Any:
        """aigen_start
        Convert this DITL Schema to the engine-native schema format for the given engine identifier.
        aigen_end"""
        func = self._to_engine_methods.get(engine_identifier, None)
        if func is None:
            raise RuntimeError(f"Engine {engine_identifier} has no to engine schema defined!")
        return func(schema=self)


class Columns(RootModel[dict[str, Column]]):
    @model_validator(mode="before")
    @classmethod
    def validate_keys(cls, value: Any) -> Any:
        """aigen_start
        Validate that column keys are provided as a dictionary and contain no commas.
        aigen_end"""
        if not isinstance(value, dict):
            raise ValueError("Columns need to be provided as dictionary.")
        for key in value.keys():
            if "," in key:
                raise ValueError(f"Key '{key}' contains commas which are not allowed.")
        return value

    def get_schema(self, by_name: bool = False) -> Schema:
        """aigen_start
        Build and return a Schema from the column definitions, using either column keys or names.
        aigen_end"""
        return Schema(
            [
                SchemaField(
                    name=column.name if by_name else key,
                    type_=column.data_type,
                    nullable=column.is_nullable,
                )
                for key, column in self.root.items()
            ]
        )


class ForeignKey(BaseModel):
    table: "Table"
    columns: list[Column]
