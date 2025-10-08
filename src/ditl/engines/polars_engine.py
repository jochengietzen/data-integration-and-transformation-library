from typing import Type, Any
import polars as pl
from ditl.engines.base import Engine
from ditl.model import Schema, SchemaField


class PolarsEngine(Engine):
    engine_identifier: str = "polars"
    internal_schema_type: Type[pl.Schema] = pl.Schema

    @staticmethod
    def _from_engine_schema(cls, schema: Any) -> Schema:
        return Schema(
            [
                # TODO: needs refinement of type_ to reflect a DataType => DataType also needs to work with registration process
                SchemaField(name=key, type_=value, nullable=True)
                for key, value in schema.to_python().items()
            ]
        )

    def setup(self):
        Schema.register_from_engine_schema(
            engine=self,
            engine_schema_type=self.internal_schema_type,
            func=self._from_engine_schema,
        )


PolarsEngine().setup()

if __name__ == "__main__":
    df = pl.DataFrame(
        {
            "foo": [1, 2, 3],
            "bar": [6.0, 7.0, 8.0],
            "ham": ["a", "b", "c"],
        }
    )

    print(df)
    print(df.schema)
    print(df.schema.to_python())
    print(dir(df.schema))
    print(isinstance(df.schema, PolarsEngine().internal_schema_type))

    print(Schema.from_engine_schema(df.schema))
