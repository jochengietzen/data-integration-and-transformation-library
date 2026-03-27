import pandas as pd
from ditl_engine_pandas.engine import PandasEngine

from ditl.models.base import FloatType, IntegerType, Schema, SchemaField
from ditl.models.data_frame_wrapper import DataFrameWrapper

df = pd.DataFrame(
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
df_2 = PandasEngine.cast(schema=schema, data_frame_wrapper=DataFrameWrapper(data_frame=df))
print(df_2.data_frame.dtypes)

print(df_w.data_frame)
df_w = df_w.cast(engine=PandasEngine)
print(df_w.data_frame)
