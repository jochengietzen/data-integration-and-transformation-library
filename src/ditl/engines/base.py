from typing import Any, ClassVar, Type

from ditl.base_model import BaseModel
from ditl.model import DataType


class Engine(BaseModel):
    """"""

    # Defines
    # - Schema
    # - DatenTypen
    # - DataFrame (DataFrameWrapper)
    # - read
    # - write
    engine_identifier: ClassVar[str]
    internal_schema_type: ClassVar[Type[Any]]
    registered_types: ClassVar[dict[Any, DataType]] = {}

    @classmethod
    def register_data_type(cls, data_type: Type[DataType]):
        cls.registered_types[
            data_type._engine_identifier_to_engine_type[data_type.__name__][
                cls.engine_identifier
            ]
        ] = data_type

    @abstractmethod
    def read(cls,  read_type: EngineReadType, *args, **kwargs) -> DataFrameWrapper:
        pass

    # Aktuelle Idee!
    # Wir nutzen doch eine Registrierung für read und write, damit die Nachimplementierung so einfach wie möglich ist.
    # Idee ist, per String key eine methode einzuhängen, die dann aus der Table heraus aufgerufen wird.
    # Read und Write werden dann auf Engine Base Ebene implementiert und geben eine eindeutige Fehlermeldung, wenn diese
    # nicht existiert. Wir können dann beliebig vorimplementieren. Eventuell fliegt dann der EngineReadType wieder raus
    # oder wird zu einem ReadWriteType aber durch string key unwahrscheinlich!
    # Falls diese Änderungen verworfen werden, unbedingt beim Table den Generic für TablePathType und TableExpectationType rausnehmen,
    # das kann durch die TypeVar von pydantic korrekt aufgelöst werden. Also ohne Generic in der Table einfach:
    # expectations: list[TableExpectationType] = Field(default_factory=list)


EngineType = TypeVar("EngineType", bound=Engine)
