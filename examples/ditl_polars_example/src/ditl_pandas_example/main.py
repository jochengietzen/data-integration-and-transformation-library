from ditl_polars_example.manager import manager
from ditl_rs_dbx_asset_bundle_jobs.runtime_system import DatabricksAssetBundleJobRS

print(manager._registered_transformations.keys())
result = manager._registered_transformations["youtube_channel_overview"].execute()
print(result.data_frame)
manager._registered_transformations["youtube_channel_overview"].save_output_table(result=result)


DatabricksAssetBundleJobRS().generate(lineage=manager.lineage)

# TODO: Build very very minimal example for quick overview of concepts
