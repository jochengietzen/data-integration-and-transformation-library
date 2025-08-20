from ditl.transformation import manager
from examples.models import foo
from typing import Any


@manager.register_transformation(foo=foo)
def sample_transformation(foo: Any):
    pass
