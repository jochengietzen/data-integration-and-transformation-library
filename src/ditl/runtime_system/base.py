from abc import abstractmethod

from ditl.graph import Lineage


class BaseRuntimeSystem:
    @abstractmethod
    def generate(self, lineage: Lineage) -> None:
        pass
