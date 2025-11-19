from abc import ABC, abstractmethod
from ditl.base_model import BaseModel
from ditl.engines.base import EngineType
from ditl.models.base import DataFrameWrapper, TableExpectationType, TablePathType
from ditl.models.base import Columns


from pydantic import Field


from typing import Type

from ditl.models.base import EngineReadType


class Table(BaseModel):
    path: TablePathType
    columns: Columns
    description: str
    engine: Type[EngineType]
    # Assumption: on table-level we only have expectations,
    # there is no equivalent to constraints on column level
    # Possibliy we do not need the generic type.
    expectations: list[TableExpectationType] = Field(default_factory=list)

    def read(self, read_type: EngineReadType, *args, **kwargs) -> DataFrameWrapper:
        return self.engine.read(*args, read_type=read_type, **kwargs)

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
