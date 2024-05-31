from ditl.base_model import BaseModel
from ditl.models.schema import BaseSchema


class BaseTable(BaseModel):
    table_schema: BaseSchema
