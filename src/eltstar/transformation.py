import importlib
import inspect
import pkgutil
from collections.abc import Callable
from importlib.metadata import entry_points
from typing import Any

from ditl.config import (
    EnvironmentConfig,
    EnvironmentConfigType,
    RuntimeConfig,
    RuntimeConfigType,
)
from ditl.exceptions import DuplicateTransformationName, InitiliazationMissingError
from ditl.graph import Lineage
from ditl.logging import logger
from ditl.models.base import BaseModel
from ditl.models.data_frame_wrapper.wrapper import DataFrameWrapper
from ditl.models.table import Table


class InputTableInstruction(BaseModel):
    table: Table
    cast_before_injection: bool = True


class Transformation(BaseModel):
    name: str
    func: Callable
    input_table_models: dict[str, InputTableInstruction]
    output_table_model: Table

    graph_label: str = "default"

    runtime_config: RuntimeConfig | None = None
    environment_config: EnvironmentConfig | None = None

    def execute(self) -> DataFrameWrapper:
        """aigen_start
        Execute this transformation by reading all input tables and calling the wrapped function.
        aigen_end"""
        if self.runtime_config is None:
            raise InitiliazationMissingError("The runtime config was never initialised/loaded!")
        if self.environment_config is None:
            raise InitiliazationMissingError("The runtime config was never initialised/loaded!")
        input_frames: dict[str, DataFrameWrapper] = {}
        for name, table_instruction in self.input_table_models.items():
            table = table_instruction.table
            input_frames[name] = table.read(
                runtime_config=self.runtime_config,
                environment_config=self.environment_config,
            )
            if input_frames[name].engine is None:
                input_frames[name].engine = table.engine
            if input_frames[name].schema is None:
                input_frames[name].schema = table.get_schema(by_name=False)

            if table_instruction.cast_before_injection:
                input_frames[name] = input_frames[name].cast()

        result = self.func(**input_frames)

        # TODO: Add selects for schema + cast? (V1/2)
        #       Probably combination of schema select and input model instruction activation flag
        return DataFrameWrapper.ensure_is_wrapper(data_frame=result)

    def save_output_table(self, result: DataFrameWrapper) -> None:
        """aigen_start
        Write the transformation result to the configured output table.
        aigen_end"""
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
        """aigen_start
        Load the runtime configuration and propagate it to all registered transformations.
        aigen_end"""
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
        """aigen_start
        Load the environment configuration and propagate it to all registered transformations.
        aigen_end"""
        self._environment_config = environment_class_type.load(
            *args, situation_identifier=situation_identifier, **kwargs
        )
        for transformation in self._registered_transformations.values():
            transformation.environment_config = self._environment_config
        return self

    def load_all_transformations(self, module_name: str) -> None:
        """aigen_start
        Discover and import all transformation modules under the given package name.
        aigen_end"""
        transformation_package = importlib.import_module(module_name)
        for loader, sub_module_name, _ in pkgutil.walk_packages(path=transformation_package.__path__):
            spec = loader.find_spec(sub_module_name)
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
        **kwargs: Any,
    ) -> Callable:
        """aigen_start
        Decorator factory that registers a function as a named transformation with its input/output table models.
        aigen_end"""

        def decorator(func: Callable) -> Callable:
            func_name = name_ or func.__name__
            if func_name in self._registered_transformations:
                raise DuplicateTransformationName(f"The function '{func_name}' is already registered.")

            argspec = inspect.getfullargspec(func=func)
            expected_argspec = {}  # TODO: tbd # pylint: disable=unused-variable # noqa # type: ignore (V1)

            # TODO: compare argspec and expected_argspec (V1)

            table_models: dict[str, InputTableInstruction] = {
                name: kwargs[name]
                for name in argspec.args
                if name in kwargs and kwargs[name] is not None and isinstance(kwargs[name], InputTableInstruction)
            } | {
                name: InputTableInstruction(table=kwargs[name])
                for name in argspec.args
                if name in kwargs and kwargs[name] is not None and isinstance(kwargs[name], Table)
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
        """aigen_start
        Build and return the lineage graph from all registered transformations.
        aigen_end"""
        return Lineage().add_transformations(transformations=self._registered_transformations)

    def load_all_plugins(self) -> None:
        """aigen_start
        Discover and load all DITL plugins registered via Python entry points.
        aigen_end"""
        plugin_groups = [
            "ditl.engines",
            "ditl.conversions",
            "ditl.runtime_systems",
        ]
        for group in plugin_groups:
            logger.info("Loading plugin group: %s", group)
            for ep in entry_points(group=group):
                logger.info("Loading entry point: %s", ep)
                ep.load()


manager = TransformationManager()
