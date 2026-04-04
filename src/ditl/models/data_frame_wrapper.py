from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar, Union

from ditl.exceptions import ProgrammingError

if TYPE_CHECKING:
    from ditl.engines.base import Engine
    from ditl.models.base import Schema


class DataFrameWrapper:
    # Composition Approach
    # Registration of utilized functions
    # Plugin functionality?

    def __init__(
        self, data_frame: Any, schema: Optional["Schema"] = None, engine: Union["Engine", type["Engine"]] | None = None
    ) -> None:
        self.data_frame = data_frame
        self.schema = schema
        self.engine = engine

    def create_with_new_data(self, data_frame: Any) -> "DataFrameWrapper":
        return DataFrameWrapper(data_frame=data_frame, schema=self.schema, engine=self.engine)

    @classmethod
    def ensure_is_wrapper(
        cls, data_frame: Any, schema: Optional["Schema"] = None, engine: Union["Engine", type["Engine"]] | None = None
    ) -> "DataFrameWrapper":
        if isinstance(data_frame, cls):
            return data_frame
        return cls.from_data_frame(data_frame=data_frame, schema=schema, engine=engine)

    @classmethod
    def from_data_frame(
        cls, data_frame: Any, schema: Optional["Schema"] = None, engine: Union["Engine", type["Engine"]] | None = None
    ) -> "DataFrameWrapper":
        return cls(data_frame=data_frame, schema=schema, engine=engine)

    def write(
        self,
        *args: Any,
        method_identifier: str,
        **kwargs: Any,
    ) -> None:
        if self.engine is None:
            raise ProgrammingError("Writing requires an engine to be set for the DataFrameWrapper!")
        self.engine.write(
            *args,
            method_identifier=method_identifier,
            data_frame=self.cast() if self.schema is not None else self,
            schema=self.schema,
            **kwargs,
        )

    def cast(self) -> "DataFrameWrapper":
        if self.engine is None:
            raise ProgrammingError("Casting requires an engine to be set for the DataFrameWrapper!")
        if self.schema is None:
            raise ProgrammingError("Cannot cast dataframe, due to missing schema in wrapper.")
        return self.engine.cast(schema=self.schema, data_frame_wrapper=self)

    def convert_to(self, target_engine: type["Engine"]) -> "DataFrameWrapper":
        if self.schema is None:
            raise ProgrammingError("Conversion requires a schema to be set for the DataFrameWrapper!")
        if self.engine is None:
            raise ProgrammingError("Conversion requires an engine to be set for the DataFrameWrapper!")
        return self.engine.convert_to_engine(
            schema=self.schema, engine_identifier=target_engine.engine_identifier, data_frame_wrapper=self
        )


DataFrameType = TypeVar("DataFrameType")


class TypedDataFrameWrapper(DataFrameWrapper, Generic[DataFrameType]):
    def __init__(self, data_frame: DataFrameType, schema: Optional["Schema"] = None) -> None:
        super().__init__(data_frame=data_frame, schema=schema)
        self.data_frame: DataFrameType = data_frame
