
from typing import Any, Literal, Type
from ditl.model import Column, DataType, Generation, Table, TableExpectation, TablePath, Columns


class StringType(DataType):
    python_type: Type[str] = str


class FooColumn(Column[StringType]):

    foo: Literal["foo"] = "foo"


class MyTablePath(TablePath):
    def full_path(self, *args: Any, **kwargs: dict[str, Any]) -> str:
        return "foo"


class MyTableExpectation(TableExpectation):
    pass


class MyTable(Table[MyTableExpectation, MyTablePath]):
    pass


foo_col = FooColumn(name="foo", data_type=StringType(),
                    generation=Generation())

foo = MyTable(path=MyTablePath(), columns=Columns(
    root={"biz": foo_col}), description="A simple model")
