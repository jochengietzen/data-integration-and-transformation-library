import inspect
from re import S
from turtle import st
from typing import Any, Callable
from ditl.exceptions import InitiliazationMissingError
from ditl.model import Table


class Transformation:
    pass


class EnvironmentConfig:
    pass


class RuntimeConfig:
    pass


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

    def register_transformation(self, name_: str, **kwargs: dict[str, Any]) -> Callable:
        def decorator(func: Callable) -> Callable:
            argspec = inspect.getfullargspec(func=func)
            expected_argspec = {}  # TODO: tbd

            # TODO: compare argspec and expected_argspec

            table_models = {
                name: kwargs.get(name)
                for name in argspec.args
                if name in kwargs and isinstance(kwargs.get(name), Table)
            }

            # TODO: 

            self._registered_transformations[name_] = transformation
            return func

        return decorator
