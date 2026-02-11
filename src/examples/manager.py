from ditl.transformation import manager
from examples.config.youtube import MyEnvironmentConfig, MyRuntimeConfig

manager.load_runtime_config(runtime_class_type=MyRuntimeConfig, situation_identifier="local")
manager.load_environment_config(
    environment_class_type=MyEnvironmentConfig,
    situation_identifier="local",
    path="/workspace/data/tst/config.yaml",
)


manager.load_all_transformations("examples.transformations")
print(manager._registered_transformations)
result = manager._registered_transformations["youtube_channel_overview"].execute()
print(result.data_frame)
manager._registered_transformations["youtube_channel_overview"].save_output_table(result=result)

# TODO: Next step: Work on fake data generation
# TODO: Discuss if name should be part of path or table itself
