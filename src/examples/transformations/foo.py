from typing import Any

from ditl.transformation import manager
from examples.models.foo import foo


@manager.register_transformation(output_table_model=foo, foo=foo)
def sample_transformation(foo: Any):
    return foo
