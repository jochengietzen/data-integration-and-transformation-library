
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from pydantic import Field, RootModel, ValidationError, model_validator

from ditl.base_model import BaseModel

class TablePath(BaseModel, ABC):
    
    @abstractmethod
    def full_path(self, *args, **kwargs):
        pass

class Generation(BaseModel):
    pass
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


DataTypeType = TypeVar('DataTypeType', bound=DataType)   
class Column(BaseModel, Generic[DataTypeType]):
    name: str = Field(..., pattern=r"^[a-zA-Z0-9-_]+$")
    data_type: DataTypeType
    constraints: list[Constraint] = Field(default_factory=list)
    expectations: list[ColumnExpectation] = Field(default_factory=list)
    generation: Generation
    description: str | None = None
    is_primary_key: bool = False
    foreign_key: "ForeignKey" | None = None



ColumnType = TypeVar('ColumType', bound=Column)   

class Columns(RootModel, Generic[ColumnType]):
    root: dict[str, ColumnType]

    @model_validator(mode="before")
    @classmethod
    def validate_keys(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            raise ValueError("Columns need to be provided as dictionary.")
        for key in value.keys():
            if "," in key:
                raise ValueError(f"Key '{key}' contains commas which are not allowed.")
        return value
        


class ForeignKey(BaseModel, Generic[ColumnType]):
    table: "Table"
    columns: list[ColumnType]



TablePathType = TypeVar('TablePathType', bound=TablePath)
TableExpectationType = TypeVar('TableExpectationType', bound=TableExpectation)

class Table(BaseModel, Generic[ColumnType, TableExpectationType, TablePathType]):
    path: TablePathType
    columns: Columns[ColumnType]
    description: str
    # Assumption: on table-level we only have expectations,
    # there is no equivalent to constraints on column level
    expectations: list[TableExpectationType] = Field(default_factory=list)  
