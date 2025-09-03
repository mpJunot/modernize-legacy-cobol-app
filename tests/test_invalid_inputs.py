import math
import pytest
from src.data import DataProgram
from src.operations import create_operations

@pytest.fixture
def ops():
    data = DataProgram(1000.00)
    return create_operations(data)

def test_credit_negative_raises(ops):
    with pytest.raises(ValueError) as exc:
        ops.credit(-10)
    assert 'Invalid amount' in str(exc.value)

def test_debit_negative_raises(ops):
    with pytest.raises(ValueError) as exc:
        ops.debit(-5)
    assert 'Invalid amount' in str(exc.value)

def test_credit_nan_raises(ops):
    with pytest.raises(ValueError) as exc:
        ops.credit(math.nan)
    assert 'Invalid amount' in str(exc.value)

def test_debit_nan_raises(ops):
    with pytest.raises(ValueError) as exc:
        ops.debit(math.nan)
    assert 'Invalid amount' in str(exc.value)

def test_credit_non_numeric_raises(ops):
    with pytest.raises(ValueError):
        ops.credit("not-a-number")

def test_debit_non_numeric_raises(ops):
    with pytest.raises(ValueError):
        ops.debit("xyz")
