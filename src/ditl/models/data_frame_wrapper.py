from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar, Union

from ditl.exceptions import ProgrammingError

if TYPE_CHECKING:
    from ditl.engines.base import Engine
    from ditl.models.base import Schema


class DataFrameWrapper:
    # Composition Approach
    # Registration of utilized functions
    # Plugin functionality?

    def __init__(self, data_frame: Any, schema: Optional["Schema"] = None) -> None:
        self.data_frame = data_frame
        self.schema = schema

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
        engine: Union["Engine", type["Engine"]],  # fmt: skip
        **kwargs: Any,
    ) -> None:
        engine.write(
            *args,
            method_identifier=method_identifier,
            data_frame=self.cast(engine=engine) if self.schema is not None else self,
            schema=self.schema,
            **kwargs,
        )

    def cast(self, engine: Union["Engine", type["Engine"]]) -> "DataFrameWrapper":
        if self.schema is None:
            raise ProgrammingError("Cannot cast dataframe, due to missing schema in wrapper.")
        return engine.cast(schema=self.schema, data_frame_wrapper=self)


DataFrameType = TypeVar("DataFrameType")


class TypedDataFrameWrapper(DataFrameWrapper, Generic[DataFrameType]):
    def __init__(self, data_frame: DataFrameType) -> None:
        super().__init__(data_frame)
        self.data_frame: DataFrameType = data_frame
