from typing import Any, ClassVar, Protocol, TypeVar

from ditl.base_model import BaseModel


class LoadMethod(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> "Config": ...


class EnvironmentConfig(BaseModel):
    """Information to staging environment: connection, settings"""

    registered_load_methods: ClassVar[dict[str, LoadMethod]] = dict()

    @classmethod
    def register_load_method(cls, situation_identifier: str, method: LoadMethod) -> None:
        cls.registered_load_methods[situation_identifier] = method

    @classmethod
    def load(cls, *args: Any, situation_identifier: str, **kwargs: Any) -> "EnvironmentConfig":
        if situation_identifier not in cls.registered_load_methods:
            raise NotImplementedError(
                f"The configuration {cls.__name__} does not have a load function for "
                f"situation {situation_identifier} implemented."
            )
        return cls.registered_load_methods[situation_identifier](*args, **kwargs)

    env: str


class RuntimeConfig(BaseModel):
    """Possibility to pass runtime specific: storage environments, client Ids"""

    registered_load_methods: ClassVar[dict[str, LoadMethod]] = dict()

    @classmethod
    def register_load_method(cls, situation_identifier: str, method: LoadMethod) -> None:
        cls.registered_load_methods[situation_identifier] = method

    @classmethod
    def load(cls, *args: Any, situation_identifier: str, **kwargs: Any) -> "RuntimeConfig":
        if situation_identifier not in cls.registered_load_methods:
            raise NotImplementedError(
                f"The configuration {cls.__name__} does not have a load function for "
                f"situation {situation_identifier} implemented."
            )
        return cls.registered_load_methods[situation_identifier](*args, **kwargs)


EnvironmentConfigType = TypeVar("EnvironmentConfigType", bound=EnvironmentConfig)
RuntimeConfigType = TypeVar("RuntimeConfigType", bound=RuntimeConfig)
