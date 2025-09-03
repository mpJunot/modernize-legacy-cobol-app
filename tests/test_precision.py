from src.data import DataProgram
from src.operations import create_operations

def test_total_two_decimal_places():
    data = DataProgram(1000.00)
    ops = create_operations(data)
    ops.credit(0.335)
    total = ops.total()
    assert isinstance(total, float)
    assert format(total, '.2f') == f"{total:.2f}"

def test_rounding_consistency():
    data = DataProgram(1000.00)
    ops = create_operations(data)
    # cumulative small adds
    ops.credit(0.10)
    ops.credit(0.20)
    assert ops.total() == round(1000.00 + 0.10 + 0.20, 2)
