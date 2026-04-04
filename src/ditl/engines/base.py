from abc import abstractmethod
from collections import defaultdict
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple, Protocol, TypeVar

from ditl.base_model import BaseModel
from ditl.models.base import DataType, Schema

if TYPE_CHECKING:
    from ditl.models.data_frame_wrapper import DataFrameWrapper


class ReadMethod(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> "DataFrameWrapper": ...


class WriteMethod(Protocol):
    def __call__(self, *args: Any, data_frame: "DataFrameWrapper", **kwargs: Any) -> None: ...


class ConversionMethod(Protocol):
    def __call__(
        self, *args: Any, data_frame: "DataFrameWrapper", schema: Schema, **kwargs: Any
    ) -> "DataFrameWrapper": ...


class ConversionEngineTuple(NamedTuple):
    source_engine_identifier: str
    target_engine_identifier: str


class Engine(BaseModel):
    """"""

    # Defines
    # - Schema
    # - DatenTypen
    # - DataFrame (DataFrameWrapper)
    # - read
    # - write
    engine_identifier: ClassVar[str]
    internal_schema_type: ClassVar[type[Any]]
    registered_types: ClassVar[dict[Any, type[DataType]]] = {}
    registered_read_methods: ClassVar[dict[str, dict[str, ReadMethod]]] = defaultdict(dict)
    registered_write_methods: ClassVar[dict[str, dict[str, WriteMethod]]] = defaultdict(dict)
    # TODO: Switch other registragtion variables to use the named tuple, as well
    registered_conversion_methods: ClassVar[dict[ConversionEngineTuple, ConversionMethod]] = dict()

    @classmethod
    def register_data_type(cls, data_type: type[DataType]):
        cls.registered_types[data_type._engine_identifier_to_engine_type[data_type.__name__][cls.engine_identifier]] = (
            data_type
        )

    @classmethod
    def read(cls, *args: Any, method_identifier: str, **kwargs: Any) -> "DataFrameWrapper":
        if method_identifier not in cls.registered_read_methods[cls.engine_identifier]:
            raise NotImplementedError(
                f"The read method with name '{method_identifier}' "
                f"is not implemented or registered for engine {cls.engine_identifier}!"
            )
        return cls.registered_read_methods[cls.engine_identifier][method_identifier](*args, **kwargs)

    @classmethod
    def write(
        cls,
        *args: Any,
        method_identifier: str,
        data_frame: "DataFrameWrapper",
        **kwargs: Any,
    ) -> None:
        if method_identifier not in cls.registered_write_methods[cls.engine_identifier]:
            raise NotImplementedError(
                f"The write method with name '{method_identifier}' "
                f"is not implemented or registered for engine {cls.engine_identifier}!"
            )
        cls.registered_write_methods[cls.engine_identifier][method_identifier](*args, data_frame=data_frame, **kwargs)

    @classmethod
    def register_read_method(cls, method_identifier: str, method: ReadMethod) -> None:
        # TODO: Implement general logger
        # TODO: log warning when overwriting existing function!
        cls.registered_read_methods[cls.engine_identifier][method_identifier] = method

    @classmethod
    def register_write_method(cls, method_identifier: str, method: WriteMethod) -> None:
        # TODO: log warning when overwriting existing function!
        cls.registered_write_methods[cls.engine_identifier][method_identifier] = method

    @classmethod
    @abstractmethod
    def _from_engine_schema(cls, schema: Any) -> Schema:
        pass

    @classmethod
    @abstractmethod
    def _to_engine_schema(cls, schema: Schema) -> Any:
        pass

    @classmethod
    @abstractmethod
    def cast(cls, schema: Schema, data_frame_wrapper: "DataFrameWrapper") -> "DataFrameWrapper":
        pass

    @classmethod
    @abstractmethod
    def dataframe_from_faker_columnar(cls, data: dict[str, list[Any]], schema: Schema) -> "DataFrameWrapper":
        pass

    @classmethod
    def register_conversion_to_engine(cls, target_engine_identifier: str, func: ConversionMethod):
        cls.registered_conversion_methods[
            ConversionEngineTuple(
                source_engine_identifier=cls.engine_identifier, target_engine_identifier=target_engine_identifier
            )
        ] = func
        # TODO: Warning, if tuple already exists and code differs!

    @classmethod
    def convert_to_engine(
        cls, schema: Schema, engine_identifier: str, data_frame_wrapper: "DataFrameWrapper"
    ) -> "DataFrameWrapper":
        conversion_tuple = ConversionEngineTuple(cls.engine_identifier, engine_identifier)
        func = cls.registered_conversion_methods.get(conversion_tuple)
        if func is None:
            raise NotImplementedError(
                f"The engine {conversion_tuple.source_engine_identifier} "
                f"has no implementation for the conversion into the engine "
                f"{conversion_tuple.target_engine_identifier}. "
                f"Please make sure, to register a conversion function, "
                f"using the engine's `register_conversion_to_engine` function."
            )
        return func(data_frame=data_frame_wrapper, schema=schema)

    # TODO: Add check whether the engine_read_settings and engine_write_settings have
    # engines, that actually have implemented the transfer from one to the other.
    # Only read => write direction seems to be required for now.
    # TODO: Prompt Primer -> Prompt Erzeugung für Claude etc.
    # TODO: provide standard functionalities like merge, upsert for engines


EngineType = TypeVar("EngineType", bound=Engine)
