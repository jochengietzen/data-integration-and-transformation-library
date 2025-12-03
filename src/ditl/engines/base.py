from collections import defaultdict
from typing import Any, ClassVar, Protocol, Type, TypeVar

from ditl.base_model import BaseModel
from ditl.models.base import DataType
from ditl.models.base import DataFrameWrapper


class ReadMethod(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> DataFrameWrapper: ...


class WriteMethod(Protocol):
    def __call__(
        self, *args: Any, data_frame: DataFrameWrapper, **kwargs: Any
    ) -> None: ...


# TODO: Think about plugin functionality


class Engine(BaseModel):
    """"""

    # Defines
    # - Schema
    # - DatenTypen
    # - DataFrame (DataFrameWrapper)
    # - read
    # - write
    engine_identifier: ClassVar[str]
    internal_schema_type: ClassVar[Type[Any]]
    registered_types: ClassVar[dict[Any, DataType]] = {}
    registered_read_methods: ClassVar[dict[str, dict[str, ReadMethod]]] = defaultdict(
        dict
    )
    registered_write_methods: ClassVar[dict[str, dict[str, WriteMethod]]] = defaultdict(
        dict
    )

    @classmethod
    def register_data_type(cls, data_type: Type[DataType]):
        cls.registered_types[
            data_type._engine_identifier_to_engine_type[data_type.__name__][
                cls.engine_identifier
            ]
        ] = data_type

    @classmethod
    def read(
        cls, *args: Any, method_identifier: str, **kwargs: Any
    ) -> DataFrameWrapper:
        if method_identifier not in cls.registered_read_methods[cls.engine_identifier]:
            raise NotImplementedError(
                f"The read method with name '{method_identifier}' "
                f"is not implemented or registered for engine {cls.engine_identifier}!"
            )
        return cls.registered_read_methods[cls.engine_identifier][method_identifier](
            *args, **kwargs
        )

    @classmethod
    def write(
        cls,
        *args: Any,
        method_identifier: str,
        data_frame: DataFrameWrapper,
        **kwargs: Any,
    ) -> None:
        if method_identifier not in cls.registered_write_methods[cls.engine_identifier]:
            raise NotImplementedError(
                f"The write method with name '{method_identifier}' "
                f"is not implemented or registered for engine {cls.engine_identifier}!"
            )
        cls.registered_write_methods[cls.engine_identifier][method_identifier](
            *args, data_frame=data_frame, **kwargs
        )

    @classmethod
    def register_read_method(cls, method_identifier: str, method: ReadMethod) -> None:
        # TODO: Implement general logger
        # TODO: log warning when overwriting existing function!
        cls.registered_read_methods[cls.engine_identifier][method_identifier] = method

    @classmethod
    def register_write_method(cls, method_identifier: str, method: WriteMethod) -> None:
        # TODO: log warning when overwriting existing function!
        cls.registered_write_methods[cls.engine_identifier][method_identifier] = method


EngineType = TypeVar("EngineType", bound=Engine)
