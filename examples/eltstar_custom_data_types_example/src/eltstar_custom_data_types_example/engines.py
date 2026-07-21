import polars as pl
import pyarrow as pa
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.engines.eltstar_arrow_engine import ArrowEngine
from eltstar_custom_data_types_example.data_types import DoubleType, MissingDataType

ArrowEngine.register_data_type(
    data_type=DoubleType.register_from_and_to_methods(
        engine_identifier=ArrowEngine.engine_identifier,
        engine_type=pa.float64(),
    )
)
ArrowEngine.register_data_type(
    data_type=MissingDataType.register_from_and_to_methods(
        engine_identifier=ArrowEngine.engine_identifier,
        engine_type=pa.float64(),
    )
)
PolarsEngine.register_data_type(
    data_type=DoubleType.register_from_and_to_methods(
        engine_identifier=PolarsEngine.engine_identifier,
        engine_type=pl.Float64,
    )
)
