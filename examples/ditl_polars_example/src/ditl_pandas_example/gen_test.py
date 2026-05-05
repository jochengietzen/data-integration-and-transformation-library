import time

from ditl_engine_pandas.engine import PandasEngine

from ditl.logging import logger
from ditl.testing.faker_manager import FakerManager
from ditl_pandas_example.models.youtube import tech_channels

faker_manager = FakerManager()
for i in [10, 100, 1000]:
    start = time.time()
    df = faker_manager.generate(table=tech_channels, engine=PandasEngine(), n_values=i).data_frame
    logger.debug("Generated %d rows in %.4f seconds", i, time.time() - start)

print(df)
