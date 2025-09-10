from ditl.transformation import manager
from examples.models.foo import foo
from typing import Any


@manager.register_transformation(output_table_model=foo, foo=foo)
def sample_transformation(foo: Any):
    return foo
