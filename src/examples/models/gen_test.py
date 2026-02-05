import time
from ditl.engines.polars_engine import PolarsEngine
from ditl.testing.faker_manager import FakerManager
from examples.models.youtube import tech_channels


faker_manager = FakerManager()
for i in [10, 100, 1000, 10000, 100000, 1000000]:
    start = time.time()
    df = faker_manager.generate(
        table=tech_channels, engine=PolarsEngine(), n_values=i
    ).data_frame
    print(i, "in", time.time() - start, "seconds")

print(df)
