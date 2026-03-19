import polars as pl
from ditl_engine_polars.engine import PolarsEngine

from ditl.models.base import FloatType, IntegerType, Schema, SchemaField
from ditl.models.data_frame_wrapper import DataFrameWrapper

df = pl.DataFrame(
    {
        "foo": [1, 2, 3],
        "bar": [6.0, 7.0, 8.0],
    }
)

schema = Schema(
    root=[
        SchemaField(name="bar", type_=IntegerType(), nullable=False),
        SchemaField(name="foo", type_=FloatType(), nullable=False),
    ]
)

df_w = DataFrameWrapper(data_frame=df, schema=schema)

print(df)
df_2 = PolarsEngine.cast(schema=schema, data_frame_wrapper=DataFrameWrapper(data_frame=df))
print(df_2.data_frame)

print(df_w.data_frame)
df_w = df_w.cast(engine=PolarsEngine)
print(df_w.data_frame)
