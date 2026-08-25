import pandas as pd
from eltstar_engine_pandas.engine import PandasEngine

from eltstar.exceptions import SchemaVerificationError
from eltstar.models.base import IntegerType, StringType
from eltstar.models.column import Column, Columns
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar.models.generation import Generation
from eltstar.models.schema import Schema, SchemaField
from eltstar.testing.faker_type import FakerIDType, FakerStringType
from eltstar_pandas_example.models.youtube import ReadTable, YoutubeTablePath

if __name__ == "__main__":
    tbl = ReadTable(
        path=YoutubeTablePath(
            name="youtube_tech_channels",
            date="20251120",
            time="133753",
        ),
        description="Test table",
        columns=Columns(
            root=dict(
                channel_id=Column(
                    name="channel_id",
                    data_type=IntegerType(),
                    is_primary_key=True,
                    generation=Generation(faker_type=FakerIDType()),
                ),
                channel_name=Column(
                    name="channel_name",
                    data_type=StringType(),
                    generation=Generation(faker_type=FakerStringType()),
                ),
            )
        ),
    )

    print(tbl.columns.get_schema())
    print(PandasEngine._to_engine_schema(tbl.columns.get_schema()))

    data = pd.DataFrame(
        {
            "channel_id": [1, 2, 3],
            "channel_name": ["foo", "biz", "bar"],
        }
    )

    # print(data.printSchema())


    data2 = pd.DataFrame(
        {
            "channel_id": [1, 2, 3],
            "channel_name": ["foo", "biz", "bar"],
            "duplicate_name": ["foo", "biz", "bar"],
        }
    )
    print(data)

    df_w = DataFrameWrapper(data_frame=data, schema=tbl.columns.get_schema(), engine=PandasEngine)

    df_w.verify_schema(raise_on_mismatch=True)

    tbl._verify_schema(data_frame_wrapper=df_w)

    df_w2 = DataFrameWrapper(data_frame=data2, engine=PandasEngine)

    try:
        tbl._verify_schema(data_frame_wrapper=df_w2)
    except SchemaVerificationError:
        pass
    else:
        raise RuntimeError("This should have failed in the test!")

    df_w3 = DataFrameWrapper(
        data_frame=data,
        schema=Schema(
            root=[
                SchemaField(name="channel_id", type_=StringType(), nullable=False),
                SchemaField(name="channel_name", type_=StringType(), nullable=False),
            ]
        ),
        engine=PandasEngine,
    )

    try:
        tbl._verify_schema(data_frame_wrapper=df_w3)
    except SchemaVerificationError:
        pass
    else:
        raise RuntimeError("This should have failed in the test!")

    try:
        DataFrameWrapper(
            data_frame=data2,
            schema=tbl.columns.get_schema(),
            engine=PandasEngine,
            auto_verify_schema_if_given=True,
        )
    except SchemaVerificationError:
        pass
    else:
        raise RuntimeError("This should have failed in the test!")
