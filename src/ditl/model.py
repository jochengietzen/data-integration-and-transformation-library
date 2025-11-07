from abc import ABC, abstractmethod
from collections import defaultdict
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    NamedTuple,
    Type,
    TypeVar,
    Optional,
    Union,
)
from pandas import DataFrame
from pydantic import Field, RootModel, model_validator

from ditl.base_model import BaseModel


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
        cls._from_engine_methods[engine_identifier] = (engine_schema_type, from_method)
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
