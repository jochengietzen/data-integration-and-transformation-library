from typing import Any

from ditl.models.base import (
    Column,
    Columns,
    DataType,
    TablePath,
)
from ditl.models.expectations import TableExpectation
from ditl.models.generation import Generation
from ditl.models.table import Table


class StringType(DataType):
    python_type: type[str] = str


class IntegerType(DataType):
    python_type: type[int] = int


class MyTablePath(TablePath):
    def full_path(self, *args: Any, **kwargs: dict[str, Any]) -> str:
        return "foo"


class MyTableExpectation(TableExpectation):
    pass


class MyTable(Table):
    pass


foo_col = Column[StringType](name="foo", data_type=StringType(), generation=Generation())

foo = MyTable(
    path=MyTablePath(),
    columns=Columns(
        root={
            "biz": foo_col,
            "baz": Column[IntegerType](name="baz", data_type=IntegerType(), generation=Generation()),
        }
    ),
    description="A simple model",
)


if __name__ == "__main__":
    print(foo.columns.get_schema())
