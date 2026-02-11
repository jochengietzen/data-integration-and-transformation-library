from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

if TYPE_CHECKING:
    from ditl.engines.base import Engine


class DataFrameWrapper:
    # Composition Approach
    # Registration of utilized functions
    # Plugin functionality?

    def __init__(self, data_frame: Any) -> None:
        self.data_frame = data_frame

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
        engine.write(*args, method_identifier=method_identifier, data_frame=self, **kwargs)


DataFrameType = TypeVar("DataFrameType")


class TypedDataFrameWrapper(DataFrameWrapper, Generic[DataFrameType]):
    def __init__(self, data_frame: DataFrameType) -> None:
        super().__init__(data_frame)
        self.data_frame: DataFrameType = data_frame
