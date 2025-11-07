from typing import Any, ClassVar, Type

from ditl.base_model import BaseModel
from ditl.model import DataType


class Engine(BaseModel):
    """"""

    # Defines
    # - Schema
    # - DatenTypen
    # - DataFrame (DataFrameWrapper)
    # - read
    # - write
    engine_identifier: ClassVar[str]
    internal_schema_type: ClassVar[Type[Any]]
    registered_types: ClassVar[dict[Any, DataType]] = {}

    @classmethod
    def register_data_type(cls, data_type: Type[DataType]):
        cls.registered_types[
            data_type._engine_identifier_to_engine_type[data_type.__name__][
                cls.engine_identifier
            ]
        ] = data_type
