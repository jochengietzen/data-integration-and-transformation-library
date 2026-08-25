from typing import TypeVar

from eltstar.base_model import BaseModel


class DataType(BaseModel):
    identifier: str

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, DataType):
            return False
        return self.identifier == value.identifier

    def __hash__(self) -> int:
        return hash(self.identifier)


DataTypeType = TypeVar("DataTypeType", bound=DataType)  # pylint: disable=invalid-name
