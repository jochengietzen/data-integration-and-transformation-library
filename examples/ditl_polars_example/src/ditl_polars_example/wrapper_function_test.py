import polars as pl

from ditl.models.base import FloatType, IntegerType, Schema, SchemaField
from ditl.models.data_frame_wrapper import DataFrameWrapper
from ditl.models.data_frame_wrapper.functions.join import JoinArgSpec

DataFrameWrapper.load_all_plugins()
df = pl.DataFrame(
    {
        "id_1": [1, 2, 3],
        "id_2": [4, 5, 6],
        "bar": [6.0, 7.0, 8.0],
    }
)
df_2 = pl.DataFrame(
    {
        "id_1": [0, 2, 5],
        "id_2": [5, 5, 5],
        "bar": [6.0, 7.0, 8.0],
    }
)

schema = Schema(
    root=[
        SchemaField(name="id_1", type_=IntegerType(), nullable=False),
        SchemaField(name="id_2", type_=IntegerType(), nullable=False),
        SchemaField(name="bar", type_=FloatType(), nullable=False),
    ]
)

df_w1 = DataFrameWrapper(data_frame=df, schema=schema)
df_w2 = DataFrameWrapper(data_frame=df_2, schema=schema)

print(
    df_w1.join(
        function_spec=JoinArgSpec(other=df_w2, left_on=["id_1", "id_2"], right_on=["id_1", "id_2"], how="inner"),
    ).data_frame
)
