import sys
import pathlib
import pytest

# make project root importable so `from src import ...` works in tests
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.data import DataProgram

@pytest.fixture
def data_factory():
    """Return a factory for DataProgram(initial_balance)"""
    def _make(initial=1000.0):
        return DataProgram(initial)
    return _make
