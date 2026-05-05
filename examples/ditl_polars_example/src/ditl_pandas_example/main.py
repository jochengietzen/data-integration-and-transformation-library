from ditl_rs_dbx_asset_bundle_jobs.runtime_system import DatabricksAssetBundleJobRS

from ditl.logging import logger
from ditl_pandas_example.manager import manager

logger.debug("Registered transformations: %s", manager._registered_transformations.keys())
result = manager._registered_transformations["youtube_channel_overview"].execute()
print(result.data_frame)
manager._registered_transformations["youtube_channel_overview"].save_output_table(result=result)


DatabricksAssetBundleJobRS().generate(lineage=manager.lineage)

# TODO: Build very very minimal example for quick overview of concepts
