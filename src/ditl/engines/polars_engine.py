from pathlib import Path
from typing import IO, ClassVar, Type, Any, TypeGuard
import polars as pl
from ditl.engines.base import Engine
from ditl.models.base import FloatType, IntegerType, StringType
from ditl.models.base import DataFrameWrapper, Schema, SchemaField


def polars_frame(frame: Any) -> TypeGuard[pl.DataFrame]:
    return isinstance(frame, pl.DataFrame)


class PolarsEngine(Engine):
    engine_identifier: ClassVar[str] = "polars"
    internal_schema_type: ClassVar[Type[pl.Schema]] = pl.Schema

    @classmethod
    def _from_engine_schema(cls, schema: Any) -> Schema:
        print(schema)
        print([(key, value) for key, value in schema.items()])
        return Schema(
            [
                SchemaField(
                    # Currently the type_ is an instance of the datatype model. Not sure if it should be the class instead
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
            {
                schema_field.name: schema_field.type_.to_engine_type(
                    engine_identifier=cls.engine_identifier
                )
                for schema_field in schema.root
            }
        )

    @classmethod
    def _read_csv(cls, source: str, *args: Any, **kwargs: Any) -> DataFrameWrapper:
        return DataFrameWrapper(data_frame=pl.read_csv(source, *args, **kwargs))

    @classmethod
    def _write_csv(
        cls,
        *args: Any,
        data_frame: DataFrameWrapper,
        file: str | Path | IO[str] | IO[bytes] | None = None,
        **kwargs: Any,
    ) -> None:
        frame: pl.DataFrame = data_frame.data_frame
        if not polars_frame(frame):
            raise RuntimeError(
                f"The data_frame Wrapper does not hold a polars data frame, but {type(data_frame.data_frame)}!"
            )

        return frame.write_csv(file, *args, **kwargs)

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

        cls.register_read_method("csv", method=cls._read_csv)
        cls.register_write_method("csv", method=cls._write_csv)


PolarsEngine.setup()

if __name__ == "__main__":
    df = pl.DataFrame(
        {
            "foo": [1, 2, 3],
            "bar": [6.0, 7.0, 8.0],
            "ham": ["a", "b", "c"],
        }
    )

    # print(df)
    print(df.schema)
    # print(df.schema.to_python())
    # print(dir(df.schema))
    # print(isinstance(df.schema, PolarsEngine().internal_schema_type))
    schema = Schema.from_engine_schema(df.schema)
    print(schema)
    print(schema.to_engine_schema(engine_identifier=PolarsEngine.engine_identifier))

    df: pl.DataFrame = PolarsEngine.read(
        method_identifier="csv",
        source="/workspace/data/testfile.csv",
    ).data_frame
    print(Schema.from_engine_schema(df.schema))
    print(df)
    df = df.with_columns((df["foo"] + df["bar"]).alias("test"))
    PolarsEngine.write(
        method_identifier="csv",
        data_frame=DataFrameWrapper.ensure_is_wrapper(df),
        file="/workspace/data/output.csv",
    )
    DataFrameWrapper.ensure_is_wrapper(df).write(
        engine=PolarsEngine,
        method_identifier="csv",
        file="/workspace/data/output_2.csv",
    )
