from ditl.graph import Lineage
from ditl.runtime_system.base import BaseRuntimeSystem


class DatabricksAssetBundleJobRS(BaseRuntimeSystem):
    def generate(self, lineage: Lineage, source_table_type: type | None = None) -> None:
        print([t.path.name for t in lineage.iter_source_tables(source_table_type=source_table_type)])
        print([t.path.name for t in lineage.iter_sink_tables()])
        print([(t.name, t.depends_on_transformations) for t in lineage.iter_transformations()])
        # TODO: Write the actual asset bundle files
