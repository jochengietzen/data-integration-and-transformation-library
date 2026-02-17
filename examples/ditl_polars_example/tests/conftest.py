import pytest

from ditl.engines.base import Engine
from ditl.engines.polars_engine import PolarsEngine
from ditl.testing.faker_manager import FakerManager


@pytest.fixture
def faker_manager() -> FakerManager:
    return FakerManager()


@pytest.fixture
def engine() -> Engine:
    return PolarsEngine()
