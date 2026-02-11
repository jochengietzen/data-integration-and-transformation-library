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
from ditl.models.data_frame_wrapper import DataFrameWrapper
from ditl.models.expectations import RowLevelTableExpectation

TablePathType = TypeVar("TablePathType", bound=TablePath)
TableExpectationType = TypeVar("TableExpectationType", bound=RowLevelTableExpectation)


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
        args_ = self.engine_read_settings.args + list(args)
        method_identifier = self.engine_read_settings.read_type.value
        return self.engine_read_settings.engine.read(
            *args_,
            method_identifier=method_identifier,
            **(self.engine_read_settings.kwargs | kwargs),
        )

    def write(
        self,
        *args: Any,
        runtime_config: RuntimeConfigType,
        environment_config: EnvironmentConfigType,
        data_frame_wrapper: DataFrameWrapper,
        **kwargs: Any,
    ) -> "Table":
        args_ = self.engine_write_settings.args + list(args)
        method_identifier = self.engine_write_settings.write_type.value
        self.engine_write_settings.engine.write(
            *args_,
            method_identifier=method_identifier,
            data_frame=data_frame_wrapper,
            **(self.engine_write_settings.kwargs | kwargs),
        )
        return self

    def _verify_schema(self, data_frame_wrapper: DataFrameWrapper) -> None:
        pass

    def _cast(self, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        pass

    def validate_table_schema(self, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        self._verify_schema(data_frame_wrapper)

        return self._cast(data_frame_wrapper)


class SourceTable(ABC):
    @abstractmethod
    def ingest(self, *args, **kwargs) -> DataFrameWrapper:
        pass

    def __ingest__(self, data_frame_wrapper: DataFrameWrapper, table_model: Table):
        data_frame_wrapper = DataFrameWrapper.ensure_is_wrapper(data_frame=data_frame_wrapper)

        table_model.write(data_frame_wrapper)
