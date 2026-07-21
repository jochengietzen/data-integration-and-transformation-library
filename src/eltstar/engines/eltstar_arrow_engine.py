from typing import Any, ClassVar, TypeGuard

import pyarrow as pa

from eltstar.engines.base import ARROW_ENGINE_IDENTIFIER, Engine
from eltstar.exceptions import ProgrammingError
from eltstar.models.base import (
    BinaryType,
    BooleanType,
    DateType,
    DecimalType28,
    FloatType,
    IntegerType,
    StringType,
    TimestampTypeSecondsNTZ,
    TimestampTypeSecondsUTC,
    UUIDType,
)
from eltstar.models.data_frame_wrapper import DataFrameWrapper
from eltstar.models.data_frame_wrapper.wrapper import TypedDataFrameWrapper
from eltstar.models.schema import Schema, SchemaField


def arrow_frame(frame: Any) -> TypeGuard[pa.Table]:
    """Type guard for arrow data frames"""
    return isinstance(frame, pa.Table)


class ArrowEngine(Engine):
    engine_identifier: ClassVar[str] = ARROW_ENGINE_IDENTIFIER
    internal_schema_type: ClassVar[type[pa.Schema]] = pa.Schema

    @classmethod
    def _from_engine_schema(cls, schema: pa.Schema) -> Schema:
        return Schema(
            [
                SchemaField(
                    # Currently the type_ is an instance of the datatype model. Not sure if it should be the class.
                    name=field.name,
                    type_=cls.registered_types[field.type](),
                    nullable=field.nullable,
                )
                for field in schema
            ]
        )

    @classmethod
    def _to_engine_schema(cls, schema: Schema) -> pa.Schema:
        print([schema_field.to_engine_type(engine_identifier=cls.engine_identifier) for schema_field in schema.root])
        return pa.schema(
            fields=[
                pa.field(
                    name=schema_field.name,
                    type=schema_field.to_engine_type(engine_identifier=cls.engine_identifier),
                    nullable=schema_field.nullable,
                )
                for schema_field in schema.root
            ]
        )

    @classmethod
    def cast(cls, schema: Schema, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        data_frame: pa.Table = data_frame_wrapper.data_frame
        return data_frame_wrapper.create_with_new_data(
            data_frame=data_frame.cast(target_schema=cls._to_engine_schema(schema=schema))
        )

    @classmethod
    def dataframe_from_faker_columnar(cls, data: dict[str, list[Any]], schema: Schema) -> DataFrameWrapper:
        return DataFrameWrapper.from_data_frame(
            pa.Table.from_pydict(
                {key: pa.array(values) for key, values in data.items()}, schema=cls._to_engine_schema(schema=schema)
            )
        )

    @classmethod
    def convert_to_arrow(
        cls, schema: Schema, data_frame_wrapper: "DataFrameWrapper"
    ) -> "TypedDataFrameWrapper[ArrowEngine]":
        """Cannot convert arrow to arrow"""
        raise ProgrammingError(
            "A dataframe wrapper for engine Arrow cannot be converted to Arrow. This should not happen!"
        )

    @classmethod
    def convert_from_arrow(
        cls, schema: Schema, data_frame_wrapper: "TypedDataFrameWrapper[ArrowEngine]"
    ) -> "DataFrameWrapper":
        """Cannot convert arrow to arrow"""
        raise ProgrammingError(
            "A dataframe wrapper for engine Arrow cannot be converted to Arrow. This should not happen!"
        )

    @classmethod
    def setup(cls):
        """Setup the arrow engine class"""
        Schema.register_from_engine_schema(
            engine_identifier=cls.engine_identifier,
            engine_schema_type=cls.internal_schema_type,
            from_method=cls._from_engine_schema,
            to_method=cls._to_engine_schema,
        )
        cls.register_data_type(
            data_type=IntegerType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pa.int64(),
            )
        )
        cls.register_data_type(
            data_type=FloatType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pa.float64(),
            )
        )
        cls.register_data_type(
            data_type=StringType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pa.string(),
            )
        )
        cls.register_data_type(
            data_type=BooleanType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pa.bool_(),
            )
        )
        cls.register_data_type(
            data_type=TimestampTypeSecondsNTZ.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pa.timestamp(TimestampTypeSecondsNTZ.unit, TimestampTypeSecondsNTZ.time_zone),
            )
        )
        cls.register_data_type(
            data_type=TimestampTypeSecondsUTC.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pa.timestamp(TimestampTypeSecondsUTC.unit, TimestampTypeSecondsUTC.time_zone),
            )
        )
        cls.register_data_type(
            data_type=DateType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pa.date64(),
            )
        )
        cls.register_data_type(
            data_type=BinaryType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pa.binary(),
            )
        )
        cls.register_data_type(
            data_type=DecimalType28.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pa.decimal256(precision=DecimalType28.precision, scale=DecimalType28.scale),
            )
        )
        cls.register_data_type(
            data_type=UUIDType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pa.uuid(),
            )
        )


ArrowEngine.setup()
