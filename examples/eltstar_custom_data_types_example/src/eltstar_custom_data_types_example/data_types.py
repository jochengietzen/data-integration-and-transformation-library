from eltstar.models.data_type import DataType


class DoubleType(DataType):
    identifier: str = "double"


class MissingDataType(DataType):
    identifier: str = "missing"
