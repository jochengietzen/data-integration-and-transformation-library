from ditl.base_model import BaseModel
from ditl.models.column import BaseColumn


class BaseSchema(BaseModel):
    columns: list[BaseColumn]
