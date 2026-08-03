# from eltstar.models.expectations import RowLevelColumnExpectation


from eltstar.models.data_type import DataType


class IntegerType(DataType):
    identifier: str = "integer"


class FloatType(DataType):
    identifier: str = "float"


class StringType(DataType):
    identifier: str = "string"


class BooleanType(DataType):
    identifier: str = "boolean"


class TimestampTypeBase(DataType):
    unit: str
    time_zone: str | None


class TimestampTypeSecondsNTZ(TimestampTypeBase):
    identifier: str = "timestamp_ntz_ns"
    unit: str = "ns"
    time_zone: str | None = None


class TimestampTypeSecondsUTC(TimestampTypeBase):
    identifier: str = "timestamp_utc_ns"
    unit: str = "ns"
    time_zone: str = "UTC"


class DateType(DataType):
    identifier: str = "date"


class BinaryType(DataType):
    identifier: str = "binary"
    length: int = -1


class DecimalType28(DataType):
    identifier: str = "decimal_28"
    precision: int = 28
    scale: int = 0


class UUIDType(DataType):
    identifier: str = "uuid"
