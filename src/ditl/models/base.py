from enum import Enum
from typing import Any, Callable, ClassVar, Generic, Type

from pydantic import Field, RootModel, model_validator

from ditl.base_model import BaseModel

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import (
    NamedTuple,
    TypeVar,
    Optional,
    Union,
)

from typing import TYPE_CHECKING


from ditl.config import EnvironmentConfigType, RuntimeConfigType
from ditl.models.generation import Generation

if TYPE_CHECKING:
    from ditl.models.table import Table
    from ditl.engines.base import Engine


class TablePath(BaseModel, ABC):
    @abstractmethod
    def full_path(
        self,
        runtime_config: RuntimeConfigType,
        environment_config: EnvironmentConfigType,
        *args: Any,
        **kwargs: dict[str, Any],
    ) -> str:
        pass


class Expectation(BaseModel):
    pass


class ColumnExpectation(Expectation):
    pass


class TableExpectation(Expectation):
    pass


class Constraint(BaseModel):
    pass


class FromToMethod(NamedTuple):
    from_method: Callable[[Any], "DataType"]
    to_method: Callable[["DataType"], Any]


class DataType(BaseModel):
    _from_and_to_engine_methods: ClassVar[
        dict[str, dict[str, FromToMethod["DataType"]]]
    ] = defaultdict(dict)
    _engine_type_to_engine_identifier: ClassVar[dict[str, dict[Any, str]]] = (
        defaultdict(dict)
    )
    _engine_identifier_to_engine_type: ClassVar[dict[str, dict[str, Any]]] = (
        defaultdict(dict)
    )

    @classmethod
    def register_from_and_to_methods(
        cls,
        engine_identifier: str,
        engine_type: Any,
        from_method: Callable[[Any], "DataType"],
        to_method: Callable[["DataType"], Any],
    ) -> Type["DataType"]:
        cls._from_and_to_engine_methods[cls.__name__][engine_identifier] = FromToMethod(
            from_method=from_method, to_method=to_method
        )
        cls._engine_type_to_engine_identifier[cls.__name__][engine_type] = (
            engine_identifier
        )
        cls._engine_identifier_to_engine_type[cls.__name__][engine_identifier] = (
            engine_type
        )
        return cls

    @classmethod
    def to_engine_type(cls, engine_identifier: str) -> Any:
        type_ = cls._engine_identifier_to_engine_type[cls.__name__].get(
            engine_identifier, None
        )
        if type_ is None:
            raise RuntimeError(
                f"The data type {cls.__name__} has no engine {engine_identifier} registered"
            )
        return type_


class IntegerType(DataType):
    pass


class FloatType(DataType):
    pass


class StringType(DataType):
    pass


#########
DataTypeType = TypeVar("DataTypeType", bound=DataType)


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
    expectations: list[ColumnExpectation] = Field(default_factory=list)
    generation: Generation | None = None
    description: str | None = None
    is_primary_key: bool = False
    is_nullable: bool = False
    foreign_key: Optional["ForeignKey"] = None


class Schema(RootModel[list[Union[SchemaStruct, SchemaField]]]):
    _from_engine_methods: ClassVar[
        dict[str, tuple[Type[Any], Callable[[Any, Any], "Schema"]]]
    ] = {}
    _to_engine_methods: ClassVar[
        dict[str, tuple[Type[Any], Callable[["Schema"], Any]]]
    ] = {}
    # provides schema for a given instance of Columns
    # Compostition Approach

    @classmethod
    def register_from_engine_schema(
        cls,
        engine_identifier: str,
        engine_schema_type: Type[Any],
        from_method: Callable[[Any, Any], "Schema"],
        to_method: Callable[["Schema"], Any],
    ):
        if cls._from_engine_methods is None:
            cls._from_engine_methods = {}
        cls._from_engine_methods[engine_identifier] = (
            engine_schema_type, from_method)
        cls._to_engine_methods[engine_identifier] = to_method

    @classmethod
    def from_engine_schema(cls, schema: Any) -> "Schema":
        for schema_type, func in cls._from_engine_methods.values():
            if isinstance(schema, schema_type):
                return func(schema=schema)
        raise RuntimeError(f"Engine for type {type(schema)} not defined!")

    def to_engine_schema(self, engine_identifier: str) -> Any:
        func = self._to_engine_methods.get(engine_identifier, None)
        if func is None:
            raise RuntimeError(
                f"Engine {engine_identifier} has no to engine schema defined!"
            )
        return func(schema=self)


# TODO: Try to make it work with complex types (Array, Map, Variant)


class Columns(RootModel[dict[str, Column]]):
    @model_validator(mode="before")
    @classmethod
    def validate_keys(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            raise ValueError("Columns need to be provided as dictionary.")
        for key in value.keys():
            if "," in key:
                raise ValueError(
                    f"Key '{key}' contains commas which are not allowed.")
        return value

    def get_schema(self, by_name: bool = False) -> Schema:
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


class EngineFileType(Enum):
    CSV = "csv"
    JSON = "json"
    DELTA = "delta"
    PARQUET = "parquet"


TablePathType = TypeVar("TablePathType", bound=TablePath)
TableExpectationType = TypeVar("TableExpectationType", bound=TableExpectation)


class DataFrameWrapper:
    # Composition Approach
    # Registration of utilized functions
    # Plugin functionality?

    def __init__(self, data_frame: Any) -> None:
        self.data_frame = data_frame

    @classmethod
    def ensure_is_wrapper(cls, data_frame: Any) -> "DataFrameWrapper":
        if isinstance(data_frame, cls):
            return data_frame
        return cls.from_data_frame(data_frame)

    @classmethod
    def from_data_frame(cls, data_frame: Any) -> "DataFrameWrapper":
        return cls(data_frame=data_frame)

    def write(
        self,
        *args: Any,
        method_identifier: str,
        engine: "Engine" | Type["Engine"],
        **kwargs: Any,
    ) -> None:
        engine.write(
            *args, method_identifier=method_identifier, data_frame=self, **kwargs
        )


DataFrameType = TypeVar("DataFrameType")


class TypedDataFrameWrapper(DataFrameWrapper, Generic[DataFrameType]):
    def __init__(self, data_frame: DataFrameType) -> None:
        super().__init__(data_frame)
        self.data_frame: DataFrameType = data_frame
