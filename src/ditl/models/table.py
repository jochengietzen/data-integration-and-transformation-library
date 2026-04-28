from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import Field

from ditl.base_model import BaseModel
from ditl.config import (
    EnvironmentConfigType,
    RuntimeConfigType,
)
from ditl.engines.base import EngineType
from ditl.models.base import Columns, EngineFileType, TablePath
from ditl.models.data_frame_wrapper.wrapper import DataFrameWrapper
from ditl.models.expectations import RowLevelTableExpectation

TablePathType = TypeVar("TablePathType", bound=TablePath)  # pylint: disable=invalid-name
TableExpectationType = TypeVar("TableExpectationType", bound=RowLevelTableExpectation)  # pylint: disable=invalid-name


class EngineReadSettings(BaseModel):
    engine: type[EngineType]
    read_type: EngineFileType
    args: list[Any] = Field(default_factory=list)
    kwargs: dict[str, Any] = Field(default_factory=dict)


class EngineWriteSettings(BaseModel):
    engine: type[EngineType]
    write_type: EngineFileType
    args: list[Any] = Field(default_factory=list)
    kwargs: dict[str, Any] = Field(default_factory=dict)


class Table(BaseModel):
    path: TablePathType
    columns: Columns
    description: str
    engine_read_settings: EngineReadSettings
    engine_write_settings: EngineWriteSettings
    # Assumption: on table-level we only have expectations,
    # there is no equivalent to constraints on column level
    # Possibliy we do not need the generic type.
    expectations: list[TableExpectationType] = Field(default_factory=list)

    def read(
        self,
        *args: Any,
        runtime_config: RuntimeConfigType,
        environment_config: EnvironmentConfigType,
        **kwargs: Any,
    ) -> DataFrameWrapper:
        """aigen_start
        Read data from the configured source path and return it as a DataFrameWrapper.
        aigen_end"""
        args_ = self.engine_read_settings.args + list(args)
        method_identifier = self.engine_read_settings.read_type.value
        dfw = self.engine_read_settings.engine.read(
            *args_,
            method_identifier=method_identifier,
            **(self.engine_read_settings.kwargs | kwargs),
        )
        dfw.schema = self.columns.get_schema()
        return dfw

    def write(
        self,
        *args: Any,
        runtime_config: RuntimeConfigType,
        environment_config: EnvironmentConfigType,
        data_frame_wrapper: DataFrameWrapper,
        **kwargs: Any,
    ) -> "Table":
        """aigen_start
        Write the given DataFrameWrapper to the configured output path and return self.
        aigen_end"""
        args_ = self.engine_write_settings.args + list(args)
        method_identifier = self.engine_write_settings.write_type.value
        self.engine_write_settings.engine.write(
            *args_,
            method_identifier=method_identifier,
            data_frame=data_frame_wrapper,
            **(self.engine_write_settings.kwargs | kwargs),
        )
        return self

    # TODO: Add verify_schema functionality for a full table

    def _verify_schema(self, data_frame_wrapper: DataFrameWrapper) -> None:
        pass

    def cast(self, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        """Convenience function to cast the dataframe into the actual table"""
        dfw = DataFrameWrapper(
            data_frame=data_frame_wrapper.data_frame,
            schema=self.columns.get_schema(by_name=False),
            engine=data_frame_wrapper.engine,
        )
        return dfw.cast()

    def validate_table_schema(self, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        """aigen_start
        Verify the schema and cast the given DataFrameWrapper according to this table's schema.
        aigen_end"""
        self._verify_schema(data_frame_wrapper)

        return self.cast(data_frame_wrapper)


class SourceTable(ABC):
    @abstractmethod
    def ingest(self, *args, **kwargs) -> DataFrameWrapper:
        """aigen_start
        Ingest data from a source and return it as a DataFrameWrapper.
        aigen_end"""

    def __ingest__(self, data_frame_wrapper: DataFrameWrapper, table_model: Table):
        data_frame_wrapper = DataFrameWrapper.ensure_is_wrapper(data_frame=data_frame_wrapper)

        table_model.write(data_frame_wrapper)
