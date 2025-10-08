from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Type,
    TypeVar,
    Optional,
    Union,
    overload,
)
from pandas import DataFrame
from pydantic import Field, RootModel, model_validator

from ditl import base_model
from ditl.base_model import BaseModel
from ditl.engines.base import Engine


class TablePath(BaseModel, ABC):
    @abstractmethod
    def full_path(self, *args: Any, **kwargs: dict[str, Any]) -> str:
        pass


class Generation(BaseModel):
    """Generation of dummy/fake data (Faker etc.)"""


class Expectation(BaseModel):
    pass


class ColumnExpectation(Expectation):
    pass


class TableExpectation(Expectation):
    pass


class Constraint(BaseModel):
    pass


class DataType(BaseModel):
    pass


DataTypeType = TypeVar("DataTypeType", bound=DataType)


class Column(BaseModel, Generic[DataTypeType]):
    name: str = Field(..., pattern=r"^[a-zA-Z0-9-_]+$")
    data_type: DataTypeType
    constraints: list[Constraint] = Field(default_factory=list)
    expectations: list[ColumnExpectation] = Field(default_factory=list)
    generation: Generation
    description: str | None = None
    is_primary_key: bool = False
    is_nullable: bool = False
    foreign_key: Optional["ForeignKey"] = None


# TODO: Try to make it work with complex types (Array, Map, Variant)
class SchemaField(BaseModel):
    name: str
    type_: DataType
    nullable: bool


class SchemaStruct(BaseModel):
    name: str
    fields: list[Union["SchemaStruct", SchemaField]]
    nullable: bool


class Schema(RootModel[list[Union[SchemaStruct, SchemaField]]]):
    _from_engine_methods: ClassVar[
        dict[str, tuple[Type[Any], Callable[[Any, Any], "Schema"]]]
    ] = {}
    # provides schema for a given instance of Columns
    # Compostition Approach

    @classmethod
    def register_from_engine_schema(
        cls,
        engine: Engine,
        engine_schema_type: Type[Any],
        func: Callable[[Any, Any], "Schema"],
    ):
        cls._from_engine_methods[engine.engine_identifier] = (engine_schema_type, func)

    @classmethod
    def from_engine_schema(cls, schema: Any) -> "Schema":
        for schema_type, func in cls._from_engine_methods.values():
            if isinstance(schema, schema_type):
                return func(cls=cls, schema=schema)
        raise RuntimeError(f"Engine for type {type(schema)} not defined!")

    def to_engine_schema(self) -> Any:
        pass

    # def __
    # TODO: decide whether we want to use equal and equalish (maybe a @ b, a ~ b, a ^ b) as dunder methods
    # or inplace arithmethic |=

    # -> tendendy: we don't use dunder methods


class Columns(RootModel[dict[str, Column[Any]]]):
    @model_validator(mode="before")
    @classmethod
    def validate_keys(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            raise ValueError("Columns need to be provided as dictionary.")
        for key in value.keys():
            if "," in key:
                raise ValueError(f"Key '{key}' contains commas which are not allowed.")
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
        if isinstance(data_frame, DataFrameWrapper):
            return data_frame
        return cls.from_data_frame(data_frame)

    @classmethod
    def from_data_frame(cls, data_frame: Any) -> "DataFrameWrapper":
        return cls(data_frame=data_frame)


class Table(BaseModel, Generic[TableExpectationType, TablePathType]):
    path: TablePathType
    columns: Columns
    description: str
    # Assumption: on table-level we only have expectations,
    # there is no equivalent to constraints on column level
    expectations: list[TableExpectationType] = Field(default_factory=list)

    def read(self, *args, **kwargs) -> DataFrame:
        return DataFrame({"biz": "a.b.c".split(".")})

    def _verify_schema(self, data_frame_wrapper: DataFrameWrapper) -> None:
        pass

    def _cast(self, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        pass

    def validate(self, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        self._verify_schema(data_frame_wrapper)

        return self._cast(data_frame_wrapper)


class SourceTable(ABC):
    @abstractmethod
    def ingest(self, *args, **kwargs) -> DataFrameWrapper:
        pass

    def __ingest__(self, data_frame_wrapper: DataFrameWrapper, table_model: Table):
        data_frame_wrapper = DataFrameWrapper.ensure_is_wrapper(data_frame_wrapper)

        table_model.write(data_frame_wrapper)
