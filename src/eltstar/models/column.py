from typing import TYPE_CHECKING, Any, Optional, Union

from pydantic import Field, RootModel, model_validator

from eltstar.base_model import BaseModel
from eltstar.models.data_type import DataType, DataTypeType
from eltstar.models.foreign_key import ForeignKey
from eltstar.models.generation import Generation

if TYPE_CHECKING:
    from eltstar.models.schema import Schema


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


class Constraint(BaseModel):
    pass


class Column(BaseModel):
    name: str = Field(..., pattern=r"^[a-zA-Z0-9-_]+$")
    data_type: DataTypeType  # type: ignore # TODO: try to find proper way to handle pydantic and mypy
    constraints: list[Constraint] = Field(default_factory=list)
    # expectations: list[RowLevelColumnExpectation] = Field(default_factory=list)
    generation: Generation | None = None
    description: str | None = None
    is_primary_key: bool = False
    is_nullable: bool = False
    foreign_key: Optional["ForeignKey"] = None


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

    def get_schema(self, by_name: bool = False) -> "Schema":
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
