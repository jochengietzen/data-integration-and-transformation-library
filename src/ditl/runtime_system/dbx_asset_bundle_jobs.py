from ditl.graph import Lineage
from ditl.runtime_system.base import BaseRuntimeSystem


class DatabricksAssetBundleJobRS(BaseRuntimeSystem):
    def generate(self, lineage: Lineage) -> None:
        return super().generate(lineage)
