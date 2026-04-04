from typing import Any

import polars as pl
from ditl_engine_pandas.engine import PandasEngine
from ditl_engine_polars.engine import PolarsEngine

from ditl.models.base import Schema
from ditl.models.data_frame_wrapper import DataFrameWrapper


def _pandas_to_polars(*args: Any, data_frame: "DataFrameWrapper", schema: Schema, **kwargs: Any) -> DataFrameWrapper:
    return DataFrameWrapper(
        data_frame=pl.from_pandas(
            data=data_frame.data_frame, schema_overrides=PolarsEngine._to_engine_schema(schema=schema)
        ),
        schema=schema,
    )


def _polars_to_pandas(*args: Any, data_frame: "DataFrameWrapper", schema: Schema, **kwargs: Any):
    return PandasEngine.cast(
        schema=schema,
        data_frame_wrapper=DataFrameWrapper(
            data_frame=data_frame.data_frame.to_pandas(),
            schema=schema,
        ),
    )


PandasEngine.register_conversion_to_engine(
    target_engine_identifier=PolarsEngine.engine_identifier, func=_pandas_to_polars
)

PolarsEngine.register_conversion_to_engine(
    target_engine_identifier=PandasEngine.engine_identifier, func=_polars_to_pandas
)

print("Loaded conversion plugin for pandas with polars")
