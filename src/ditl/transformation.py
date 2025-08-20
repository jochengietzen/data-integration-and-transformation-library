import inspect
from typing import Any, Callable

from ditl.model import BaseModel
from ditl.exceptions import DuplicateTransformationName, InitiliazationMissingError
from ditl.model import Table


class Transformation(BaseModel):
    name: str
    func: Callable
    table_models: dict[str, Table]


class EnvironmentConfig(BaseModel):
    """Information to staging environment: connection, settings"""


class RuntimeConfig(BaseModel):
    """Possibility to pass runtime specific: storage environments, client Ids"""
    # TODO: make environment & runtime configs dynamic typeVars for transformationManager

class TransformationManager:
    def __init__(self) -> None:
        self._registered_transformations: dict[str, Transformation] = {}

        # initialization stage
        self._runtime_config: RuntimeConfig | None = None
        self._environment_config: EnvironmentConfig | None = None

    def _check_initialization_state(self) -> None:
        missing_init: list[str] = []
        if self._runtime_config is None:
            missing_init.append("runtime_config")
        if self._environment_config is None:
            missing_init.append("environment_config")

        if missing_init:
            raise InitiliazationMissingError(
                f"Configurations missing for initialization: {','.join(missing_init)}"
            )

    def register_transformation(self, **kwargs: dict[str, Any]) -> Callable:
        def decorator(func: Callable) -> Callable:

            func_name = kwargs.get("name_", func.__name__)
            if func_name in self._registered_transformations:
                raise DuplicateTransformationName(f"The function '{func_name}' is already registered.")
            
            argspec = inspect.getfullargspec(func=func)
            expected_argspec = {}  # TODO: tbd

            # TODO: compare argspec and expected_argspec

            table_models = {
                name: kwargs.get(name)
                for name in argspec.args
                if name in kwargs and isinstance(kwargs.get(name), Table)
            }

            transformation = Transformation(name=func_name, func=func, table_models=table_models)

            self._registered_transformations[func_name] = transformation
            return func

        return decorator
    
manager = TransformationManager()
