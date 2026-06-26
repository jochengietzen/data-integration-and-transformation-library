from eltstar.models.column import Columns, Column  # noqa

c = Columns(root={})
print(c.get_schema())
