from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Optional
from pandas import DataFrame
from pydantic import Field, RootModel, model_validator

from ditl import base_model
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
    foreign_key: Optional["ForeignKey"] = None


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
    
    @property
    def schema(self) -> Schema:
        pass


class ForeignKey(BaseModel):
    table: "Table"
    columns: list[Column]


TablePathType = TypeVar("TablePathType", bound=TablePath)
TableExpectationType = TypeVar("TableExpectationType", bound=TableExpectation)

class Schema:
    # provides schema for a given instance of Columns
    # Compostition Approach

    @classmethod
    def from_engine_schema(cls, schema: Any) -> "Schema":
        pass
        
    def to_engine_schema(self) -> Any:
        pass

    def __
    # TODO: decide whether we want to use equal and equalish (maybe a @ b, a ~ b, a ^ b) as dunder methods
    # or inplace arithmethic |=

    # -> tendendy: we don't use dunder methods

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

        t

        table_model.write(data_frame_wrapper)




