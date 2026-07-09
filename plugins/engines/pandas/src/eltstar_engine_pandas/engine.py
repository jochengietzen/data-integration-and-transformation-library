from typing import Any, ClassVar, TypeGuard

import numpy as np
import pandas as pd
import pyarrow as pa

from eltstar.engines.base import Engine
from eltstar.engines.eltstar_arrow_engine import ArrowEngine
from eltstar.models.base import FloatType, IntegerType, StringType
from eltstar.models.data_frame_wrapper import DataFrameWrapper, TypedDataFrameWrapper
from eltstar.models.schema import Schema, SchemaField


def pandas_frame(frame: Any) -> TypeGuard[pd.DataFrame]:
    return isinstance(frame, pd.DataFrame)


class PandasEngine(Engine):
    engine_identifier: ClassVar[str] = "pandas"
    internal_schema_type: ClassVar[type[dict[Any, Any]]] = dict

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
    def _to_engine_schema(cls, schema: Schema) -> dict[Any, Any]:
        return {
            schema_field.name: schema_field.type_.to_engine_type(engine_identifier=cls.engine_identifier)()
            for schema_field in schema.root
        }

    @classmethod
    def cast(cls, schema: Schema, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        data_frame: pd.DataFrame = data_frame_wrapper.data_frame
        return data_frame_wrapper.create_with_new_data(
            data_frame=data_frame.astype(cls._to_engine_schema(schema=schema))
        )

    @classmethod
    def dataframe_from_faker_columnar(cls, data: dict[str, list[Any]], schema: Schema) -> DataFrameWrapper:

        engine_schema = cls._to_engine_schema(schema=schema)

        if set(engine_schema.keys()) != set(data.keys()):
            raise ValueError(
                f"Incosistent column names - data columns: {list(data.keys())} - schema keys: {list(schema.keys())}"
            )

        return DataFrameWrapper.from_data_frame(
            pd.DataFrame({key: pd.Series(data=column, dtype=engine_schema[key]) for key, column in data.items()})
        )

    @classmethod
    def convert_to_arrow(
        cls, schema: Schema, data_frame_wrapper: DataFrameWrapper
    ) -> TypedDataFrameWrapper[ArrowEngine]:
        """Converts the engine specific dataframe wrapper to an arrow object"""
        data_frame: pd.DataFrame = data_frame_wrapper.data_frame
        return DataFrameWrapper(
            data_frame=pa.Table.from_pandas(data_frame, schema=ArrowEngine._to_engine_schema(schema)),
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
            data_frame=data_frame.to_pandas(),
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
                engine_type=np.int64,
                from_method=lambda x: IntegerType(),
                to_method=lambda x: np.int64(),
            )
        )
        cls.register_data_type(
            data_type=FloatType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=np.float64,
                from_method=lambda x: FloatType(),
                to_method=lambda x: np.float64(),
            )
        )
        cls.register_data_type(
            data_type=StringType.register_from_and_to_methods(
                engine_identifier=cls.engine_identifier,
                engine_type=pd.StringDtype,
                from_method=lambda x: StringType(),
                to_method=lambda x: pd.StringDtype(),
            )
        )


PandasEngine.setup()
