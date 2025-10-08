from typing import Any, Type
from ditl.base_model import BaseModel


class Engine(BaseModel):
    """"""

    # Defines
    # - Schema
    # - DatenTypen
    # - DataFrame
    # - read
    # - write
    engine_identifier: str
    internal_schema_type: Type[Any]
