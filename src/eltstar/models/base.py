# from eltstar.models.expectations import RowLevelColumnExpectation

from typing import ClassVar

from eltstar.models.data_type import DataType


class IntegerType(DataType):
    pass


class FloatType(DataType):
    pass


class StringType(DataType):
    pass


class BooleanType(DataType):
    pass


class TimestampTypeBase(DataType):
    unit: ClassVar[str]
    time_zone: ClassVar[str | None]


class TimestampTypeSecondsNTZ(TimestampTypeBase):
    unit: ClassVar[str] = "ns"
    time_zone: ClassVar[str | None] = None


class TimestampTypeSecondsUTC(TimestampTypeBase):
    unit: ClassVar[str] = "ns"
    time_zone: ClassVar[str] = "UTC"


class DateType(DataType):
    pass


class BinaryType(DataType):
    length: ClassVar[int] = -1


class DecimalType28(DataType):
    precision: ClassVar[int] = 28
    scale: ClassVar[int] = 0


class UUIDType(DataType):
    pass
