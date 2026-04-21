import time

from ditl_engine_polars.engine import PolarsEngine
from ditl_polars_example.models.youtube import tech_channels

from ditl.logging import logger
from ditl.testing.faker_manager import FakerManager

faker_manager = FakerManager()
for i in [10, 100, 1000]:
    start = time.time()
    df = faker_manager.generate(table=tech_channels, engine=PolarsEngine(), n_values=i).data_frame
    logger.debug("Generated %d rows in %.4f seconds", i, time.time() - start)

print(df)
