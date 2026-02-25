import importlib
import inspect
import pkgutil
from collections.abc import Callable
from typing import Any

from ditl.config import (
    EnvironmentConfig,
    EnvironmentConfigType,
    RuntimeConfig,
    RuntimeConfigType,
)
from ditl.exceptions import DuplicateTransformationName, InitiliazationMissingError
from ditl.graph import Lineage
from ditl.models.base import BaseModel
from ditl.models.data_frame_wrapper import DataFrameWrapper
from ditl.models.table import Table


class Transformation(BaseModel):
    name: str
    func: Callable
    input_table_models: dict[str, Table]
    output_table_model: Table

    graph_label: str = "default"

    runtime_config: RuntimeConfig | None = None
    environment_config: EnvironmentConfig | None = None

    def execute(self) -> DataFrameWrapper:
        if self.runtime_config is None:
            raise InitiliazationMissingError("The runtime config was never initialised/loaded!")
        if self.environment_config is None:
            raise InitiliazationMissingError("The runtime config was never initialised/loaded!")
        input_frames = {}
        for name, table in self.input_table_models.items():
            input_frames[name] = table.read(
                runtime_config=self.runtime_config,
                environment_config=self.environment_config,
            )
            # TODO: Maybe we want to cast the tables before handing them down.
            # If so, we might need to switch from input_table_models str to Table and utilise
            # str to InputTableInstructions instead. Then we could decide on a per TableInstruction
            # basis if we cast or not.

        result = self.func(**input_frames)

        return DataFrameWrapper.ensure_is_wrapper(data_frame=result)

    def save_output_table(self, result: DataFrameWrapper) -> None:
        if self.runtime_config is None:
            raise InitiliazationMissingError("The runtime config was never initialised/loaded!")
        if self.environment_config is None:
            raise InitiliazationMissingError("The runtime config was never initialised/loaded!")
        self.output_table_model.write(
            runtime_config=self.runtime_config,
            environment_config=self.environment_config,
            data_frame_wrapper=result,
        )


class TransformationManager:
    def __init__(
        self,
    ) -> None:
        self._registered_transformations: dict[str, Transformation] = {}

        # initialization stage
        self._runtime_config: RuntimeConfig | None = None
        self._environment_config: EnvironmentConfig | None = None

    def load_runtime_config(
        self,
        *args: Any,
        runtime_class_type: type[RuntimeConfigType],
        situation_identifier: str,
        **kwargs: Any,
    ) -> "TransformationManager":
        self._runtime_config = runtime_class_type.load(*args, situation_identifier=situation_identifier, **kwargs)
        for transformation in self._registered_transformations.values():
            transformation.runtime_config = self._runtime_config
        return self

    def load_environment_config(
        self,
        *args: Any,
        environment_class_type: type[EnvironmentConfigType],
        situation_identifier: str,
        **kwargs: Any,
    ) -> "TransformationManager":
        self._environment_config = environment_class_type.load(
            *args, situation_identifier=situation_identifier, **kwargs
        )
        for transformation in self._registered_transformations.values():
            transformation.environment_config = self._environment_config
        return self

    def load_all_transformations(self, module_name: str) -> None:
        transformation_package = importlib.import_module(module_name)
        for loader, module_name, _ in pkgutil.walk_packages(path=transformation_package.__path__):
            spec = loader.find_spec(module_name)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

    def _check_initialization_state(self) -> None:
        missing_init: list[str] = []
        if self._runtime_config is None:
            missing_init.append("runtime_config")
        if self._environment_config is None:
            missing_init.append("environment_config")

        if missing_init:
            raise InitiliazationMissingError(f"Configurations missing for initialization: {','.join(missing_init)}")

    def register_transformation(
        self,
        output_table_model: Table,
        name_: str | None = None,
        **kwargs: dict[str, Any],
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            func_name = name_ or func.__name__
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

            transformation = Transformation(
                name=func_name,
                func=func,
                input_table_models=table_models,
                output_table_model=output_table_model,
                runtime_config=self._runtime_config,
                environment_config=self._environment_config,
            )

            self._registered_transformations[func_name] = transformation
            return func

        return decorator

    @property
    def lineage(self) -> Lineage:
        return Lineage().add_transformations(transformations=self._registered_transformations)


manager = TransformationManager()
