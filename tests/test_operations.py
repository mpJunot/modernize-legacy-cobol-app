import pytest
from src.operations import create_operations

def test_total_reads_balance(data_factory):
    dp = data_factory(1000.0)
    ops = create_operations(dp)
    assert ops.total() == 1000.00

def test_credit_valid_amount_increases_balance(data_factory):
    dp = data_factory(1000.0)
    ops = create_operations(dp)
    new = ops.credit(100.0)
    assert new == 1100.00
    assert dp.read() == 1100.00

def test_credit_zero_amount_no_change(data_factory):
    dp = data_factory(500.0)
    ops = create_operations(dp)
    new = ops.credit(0)
    assert new == 500.00
    assert dp.read() == 500.00

def test_credit_invalid_negative_or_non_numeric_raises(data_factory):
    dp = data_factory(1000.0)
    ops = create_operations(dp)
    with pytest.raises(ValueError):
        ops.credit(-10)
    with pytest.raises(ValueError):
        ops.credit("not-a-number")

def test_debit_valid_amount_decreases_balance(data_factory):
    dp = data_factory(1000.0)
    ops = create_operations(dp)
    new = ops.debit(50.0)
    assert new == 950.00
    assert dp.read() == 950.00

def test_debit_zero_amount_no_change(data_factory):
    dp = data_factory(300.0)
    ops = create_operations(dp)
    new = ops.debit(0)
    assert new == 300.00
    assert dp.read() == 300.00

def test_debit_overdraft_raises(data_factory):
    dp = data_factory(100.0)
    ops = create_operations(dp)
    with pytest.raises(ValueError):
        ops.debit(200.0)
    assert dp.read() == 100.0  # balance unchanged

def test_debit_invalid_negative_or_non_numeric_raises(data_factory):
    dp = data_factory(200.0)
    ops = create_operations(dp)
    with pytest.raises(ValueError):
        ops.debit(-5)
    with pytest.raises(ValueError):
        ops.debit("xyz")

def test_multiple_sequential_operations_persist_within_run(data_factory):
    dp = data_factory(1000.0)
    ops = create_operations(dp)
    ops.credit(200.0)   # 1200
    ops.debit(50.0)     # 1150
    assert ops.total() == 1150.00
    assert dp.read() == 1150.00
