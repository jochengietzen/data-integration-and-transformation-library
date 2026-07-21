from abc import abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, TypeVar

from eltstar.base_model import BaseModel
from eltstar.exceptions import ProgrammingError
from eltstar.models.data_type import DataType
from eltstar.models.schema import Schema

if TYPE_CHECKING:
    from eltstar.engines.eltstar_arrow_engine import ArrowEngine
    from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper, TypedDataFrameWrapper

ARROW_ENGINE_IDENTIFIER = "arrow"


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
    # TODO: Switch other registragtion variables to use the named tuple, as well (V3?)
    # registered_conversion_methods: ClassVar[dict[ConversionEngineTuple, ConversionMethod]] = {}

    @classmethod
    def register_data_type(cls, data_type: type[DataType]):
        """aigen_start
        Register a DataType by mapping its engine-native type to the DataType class for this engine.
        aigen_end"""
        cls.registered_types[data_type._engine_identifier_to_engine_type[data_type.__name__][cls.engine_identifier]] = (  # pylint: disable=protected-access
            data_type
        )

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
        if data_frame_wrapper.engine.engine_identifier == target_engine.engine_identifier:
            return data_frame_wrapper
        source_engine = data_frame_wrapper.engine
        if source_engine is None:
            raise ProgrammingError("Can only convert dataframes that are engine aware!")
        if source_engine.engine_identifier == ARROW_ENGINE_IDENTIFIER:
            arrow_wrapper = data_frame_wrapper
        else:
            arrow_wrapper = source_engine.convert_to_arrow(schema=schema, data_frame_wrapper=data_frame_wrapper)
        if target_engine.engine_identifier == ARROW_ENGINE_IDENTIFIER:
            return arrow_wrapper
        return target_engine.convert_from_arrow(schema=schema, data_frame_wrapper=arrow_wrapper)


EngineType = TypeVar("EngineType", bound=Engine)  # pylint: disable=invalid-name
