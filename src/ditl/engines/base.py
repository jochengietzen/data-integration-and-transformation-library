from abc import abstractmethod
from collections import defaultdict
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, TypeVar

from ditl.base_model import BaseModel
from ditl.exceptions import ProgrammingError
from ditl.models.base import DataType, Schema

if TYPE_CHECKING:
    from ditl.models.data_frame_wrapper.wrapper import DataFrameWrapper


class ReadMethod(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> "DataFrameWrapper": ...


class WriteMethod(Protocol):
    def __call__(self, *args: Any, data_frame: "DataFrameWrapper", **kwargs: Any) -> None: ...


# class ConversionMethod(Protocol):
#     def __call__(
#         self, *args: Any, data_frame: "DataFrameWrapper", schema: Schema, **kwargs: Any
#     ) -> "DataFrameWrapper": ...


# class ConversionEngineTuple(NamedTuple):
#     source_engine_identifier: str
#     target_engine_identifier: str


class Engine(BaseModel):
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
    # registered_conversion_methods: ClassVar[dict[ConversionEngineTuple, ConversionMethod]] = {}

    @classmethod
    def register_data_type(cls, data_type: type[DataType]):
        """aigen_start
        Register a DataType by mapping its engine-native type to the DataType class for this engine.
        aigen_end"""
        cls.registered_types[data_type._engine_identifier_to_engine_type[data_type.__name__][cls.engine_identifier]] = (
            data_type
        )

    @classmethod
    def read(cls, *args: Any, method_identifier: str, **kwargs: Any) -> "DataFrameWrapper":
        """aigen_start
        Dispatch a read call to the registered method identified by method_identifier.
        aigen_end"""
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
        """aigen_start
        Dispatch a write call to the registered method identified by method_identifier.
        aigen_end"""
        if method_identifier not in cls.registered_write_methods[cls.engine_identifier]:
            raise NotImplementedError(
                f"The write method with name '{method_identifier}' "
                f"is not implemented or registered for engine {cls.engine_identifier}!"
            )
        cls.registered_write_methods[cls.engine_identifier][method_identifier](*args, data_frame=data_frame, **kwargs)

    @classmethod
    def register_read_method(cls, method_identifier: str, method: ReadMethod) -> None:
        """aigen_start
        Register a read method under the given identifier for this engine.
        aigen_end"""
        # TODO: Implement general logger
        # TODO: log warning when overwriting existing function!
        cls.registered_read_methods[cls.engine_identifier][method_identifier] = method

    @classmethod
    def register_write_method(cls, method_identifier: str, method: WriteMethod) -> None:
        """aigen_start
        Register a write method under the given identifier for this engine.
        aigen_end"""
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
        """aigen_start
        Cast the dataframe in the wrapper to the types defined by the given schema.
        aigen_end"""

    @classmethod
    @abstractmethod
    def dataframe_from_faker_columnar(cls, data: dict[str, list[Any]], schema: Schema) -> "DataFrameWrapper":
        """aigen_start
        Build a DataFrameWrapper from a columnar dict of fake data with the given schema.
        aigen_end"""

    @classmethod
    @abstractmethod
    def convert_to_arrow(
        cls, schema: Schema, data_frame_wrapper: "DataFrameWrapper"
    ) -> "TypedDataFrameWrapper[ArrowEngine]":
        """Converts the engine specific dataframe wrapper to an arrow object"""

    @classmethod
    @abstractmethod
    def convert_from_arrow(
        cls, schema: Schema, data_frame_wrapper: "TypedDataFrameWrapper[ArrowEngine]"
    ) -> "DataFrameWrapper":
        """Converts the engine specific dataframe wrapper from an arrow dataframe wrapper"""

    @classmethod
    def convert_to_engine(
        cls, schema: Schema, target_engine: type["Engine"], data_frame_wrapper: "DataFrameWrapper"
    ) -> "DataFrameWrapper":
        """aigen_start
        Convert the given DataFrameWrapper to a different engine using a registered conversion function.
        aigen_end"""
        source_engine = data_frame_wrapper.engine
        if source_engine is None:
            raise ProgrammingError("Can only convert dataframes that are engine aware!")
        arrow_wrapper = source_engine.convert_to_arrow(schema=schema, data_frame_wrapper=data_frame_wrapper)
        return target_engine.convert_from_arrow(schema=schema, data_frame_wrapper=arrow_wrapper)

    # TODO: Add check whether the engine_read_settings and engine_write_settings have
    # engines, that actually have implemented the transfer from one to the other.
    # Only read => write direction seems to be required for now.
    # TODO: Prompt Primer -> Prompt Erzeugung für Claude etc.
    # TODO: provide standard functionalities like merge, upsert for engines


EngineType = TypeVar("EngineType", bound=Engine)  # pylint: disable=invalid-name
