from ditl.transformation import manager
from ditl_pandas_example.config import MyEnvironmentConfig, MyRuntimeConfig

manager.load_all_plugins()

manager.load_runtime_config(runtime_class_type=MyRuntimeConfig, situation_identifier="local")
manager.load_environment_config(
    environment_class_type=MyEnvironmentConfig,
    situation_identifier="local",
    path="/workspace/data/tst/config.yaml",
)


manager.load_all_transformations("ditl_pandas_example.transformations")
