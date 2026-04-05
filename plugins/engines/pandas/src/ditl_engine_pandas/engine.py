from pathlib import Path
from typing import IO, Any, ClassVar, TypeGuard

import numpy as np
import pandas as pd

from ditl.engines.base import Engine
from ditl.models.base import FloatType, IntegerType, Schema, SchemaField, StringType
from ditl.models.data_frame_wrapper import DataFrameWrapper


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
            schema_field.name: schema_field.type_.to_engine_type(engine_identifier=cls.engine_identifier)
            for schema_field in schema.root
        }

    @classmethod
    def cast(cls, schema: Schema, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        data_frame: pd.DataFrame = data_frame_wrapper.data_frame
        return data_frame_wrapper.create_with_new_data(
            data_frame=data_frame.astype(cls._to_engine_schema(schema=schema))
        )

    @classmethod
    def _read_csv(cls, source: str, *args: Any, **kwargs: Any) -> DataFrameWrapper:
        return DataFrameWrapper(data_frame=pd.read_csv(source, *args, **kwargs))

    @classmethod
    def _write_csv(
        cls,
        *args: Any,
        data_frame: DataFrameWrapper,
        file: str | Path | IO[str] | IO[bytes] | None = None,
        **kwargs: Any,
    ) -> None:
        frame: pd.DataFrame = data_frame.data_frame
        if not pandas_frame(frame):
            raise RuntimeError(
                f"The data_frame Wrapper does not hold a pandas data frame, but {type(data_frame.data_frame)}!"
            )

        frame.to_csv(file, *args, **kwargs)

    @classmethod
    def dataframe_from_faker_columnar(cls, data: dict[str, list[Any]], schema: Schema) -> DataFrameWrapper:

        engine_schema = cls._to_engine_schema(schema=schema)

        if set(engine_schema.keys()) != set(data.keys()):
            raise ValueError(
                f"Incosistent column names - data columns: {list(data.keys())} - schema keys: {list(schema.keys())}"
            )

        return DataFrameWrapper.from_data_frame(
            pd.DataFrame({key: pd.Series(column, engine_schema[key]) for key, column in data.items()})
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

        cls.register_read_method("csv", method=cls._read_csv)
        cls.register_write_method("csv", method=cls._write_csv)


PandasEngine.setup()
