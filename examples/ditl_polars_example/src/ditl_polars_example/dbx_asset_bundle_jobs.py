from ditl.graph import Lineage
from ditl.runtime_system.base import BaseRuntimeSystem
from ditl_polars_example.manager import manager
from ditl_polars_example.models.youtube import ReadTable


class DatabricksAssetBundleJobRS(BaseRuntimeSystem):
    def generate(self, lineage: Lineage) -> None:
        print([t.path.name for t in lineage.iter_source_tables(source_table_type=ReadTable)])
        print([t.path.name for t in lineage.iter_sink_tables()])
        print([(t.name, t.depends_on_transformations) for t in lineage.iter_transformations()])
        # TODO: Write the actual asset bundle files


DatabricksAssetBundleJobRS().generate(lineage=manager.lineage)
