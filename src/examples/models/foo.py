from typing import Any, Type
from ditl.model import (
    Column,
    DataType,
    Generation,
    Table,
    TableExpectation,
    TablePath,
    Columns,
)


class StringType(DataType):
    python_type: Type[str] = str


class IntegerType(DataType):
    python_type: Type[int] = int


class MyTablePath(TablePath):
    def full_path(self, *args: Any, **kwargs: dict[str, Any]) -> str:
        return "foo"


class MyTableExpectation(TableExpectation):
    pass


class MyTable(Table[MyTableExpectation, MyTablePath]):
    pass


foo_col = Column[StringType](
    name="foo", data_type=StringType(), generation=Generation()
)

foo = MyTable(
    path=MyTablePath(),
    columns=Columns(
        root={
            "biz": foo_col,
            "baz": Column[IntegerType](
                name="baz", data_type=IntegerType(), generation=Generation()
            ),
        }
    ),
    description="A simple model",
)


if __name__ == "__main__":
    print(foo.columns.get_schema())
