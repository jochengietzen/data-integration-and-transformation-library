import time

from ditl_engine_polars.engine import PolarsEngine

from ditl.testing.faker_manager import FakerManager
from ditl_polars_example.models.youtube import tech_channels

faker_manager = FakerManager()
for i in [10, 100, 1000]:
    start = time.time()
    df = faker_manager.generate(table=tech_channels, engine=PolarsEngine(), n_values=i).data_frame
    print(i, "in", time.time() - start, "seconds")

print(df)
