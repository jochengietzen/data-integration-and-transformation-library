from typing import TYPE_CHECKING

from eltstar.base_model import BaseModel

if TYPE_CHECKING:
    from eltstar.models.column import Column
    from eltstar.models.table import Table


class ForeignKey(BaseModel):
    table: "Table"
    columns: list["Column"]
