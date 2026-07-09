from typing import Any, ClassVar, TypeGuard

import polars as pl

from eltstar.engines.base import Engine
from eltstar.engines.eltstar_arrow_engine import ArrowEngine
from eltstar.models.schema import Schema, SchemaField
from eltstar.models.base import FloatType, IntegerType,StringType
from eltstar.models.data_frame_wrapper import DataFrameWrapper, TypedDataFrameWrapper
from eltstar.utils import columnar_dictionary_to_records


def polars_frame(frame: Any) -> TypeGuard[pl.DataFrame]:
    return isinstance(frame, pl.DataFrame)


class PolarsEngine(Engine):
    engine_identifier: ClassVar[str] = "polars"
    internal_schema_type: ClassVar[type[pl.Schema]] = pl.Schema

    @classmethod
    def _from_engine_schema(cls, schema: Any) -> Schema:
        return Schema(
            [
                SchemaField(
                    # Currently the type_ is an instance of the datatype model. Not sure if it should be the class.
                    name=key,
                    type_=cls.registered_types[value](),
                    nullable=True,
                )
                for key, value in schema.items()
            ]
        )

    @classmethod
    def _to_engine_schema(cls, schema: Schema) -> pl.Schema:
        return pl.Schema(
            schema={
                schema_field.name: schema_field.type_.to_engine_type(engine_identifier=cls.engine_identifier)
                for schema_field in schema.root
            }
        )

    @classmethod
    def cast(cls, schema: Schema, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        data_frame: pl.DataFrame = data_frame_wrapper.data_frame
        return data_frame_wrapper.create_with_new_data(data_frame=data_frame.cast(cls._to_engine_schema(schema=schema)))

    @classmethod
    def dataframe_from_faker_columnar(cls, data: dict[str, list[Any]], schema: Schema) -> DataFrameWrapper:
        records = columnar_dictionary_to_records(values=data)
        return DataFrameWrapper.from_data_frame(
            pl.from_records(data=records, schema=cls._to_engine_schema(schema=schema))
        )

    @classmethod
    def convert_to_arrow(
        cls, schema: Schema, data_frame_wrapper: DataFrameWrapper
    ) -> TypedDataFrameWrapper[ArrowEngine]:
        """Converts the engine specific dataframe wrapper to an arrow object"""
        data_frame: pl.DataFrame = data_frame_wrapper.data_frame
        return DataFrameWrapper(
            data_frame=data_frame.to_arrow(),
            schema=schema,
            engine=ArrowEngine,
        )

    @classmethod
    def convert_from_arrow(
        cls, schema: Schema, data_frame_wrapper: TypedDataFrameWrapper[ArrowEngine]
    ) -> DataFrameWrapper:
        """Converts the engine specific dataframe wrapper to an arrow object"""
        data_frame: pa.Table = data_frame_wrapper.data_frame
        return DataFrameWrapper(
            data_frame=pl.from_arrow(data=data_frame, schema=cls._to_engine_schema(schema=schema)),
            schema=schema,
            engine=cls,
        )

    @classmethod
    def setup(cls):
        Schema.register_from_engine_schema(
            engine_identifier=cls.engine_identifier,
            engine_schema_type=cls.internal_schema_type,
            from_method=cls._from_engine_schema,
            to_method=cls._to_engine_schema,
        )
        cls.register_data_type(
            data_type=IntegerType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pl.Int64,
                from_method=lambda x: IntegerType(),
                to_method=lambda x: pl.Int64(),
            )
        )
        cls.register_data_type(
            data_type=FloatType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pl.Float64,
                from_method=lambda x: FloatType(),
                to_method=lambda x: pl.Float64(),
            )
        )
        cls.register_data_type(
            data_type=StringType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pl.String,
                from_method=lambda x: StringType(),
                to_method=lambda x: pl.String(),
            )
        )


PolarsEngine.setup()
