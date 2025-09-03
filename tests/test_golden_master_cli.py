import sys
import subprocess
import json
import re
from pathlib import Path

TEST_DIR = Path(__file__).parent
ROOT = TEST_DIR.parent

def _build_stdin_from_steps(steps):
    inputs = []
    for s in steps:
        op = s.get("op")
        if op == "total":
            inputs.append("1")
        elif op == "credit":
            inputs.append("2")
            inputs.append(str(s.get("amount")))
        elif op == "debit":
            inputs.append("3")
            inputs.append(str(s.get("amount")))
        else:
            raise ValueError(f"unknown op {op}")
    inputs.append("4")  # exit at the end
    return "\n".join(inputs) + "\n"

def _find_next_line_containing(lines, start_idx, substr):
    for i in range(start_idx, len(lines)):
        if substr in lines[i]:
            return i, lines[i]
    return -1, None

def _extract_first_number(line):
    m = re.search(r"(-?\d+\.\d{2})", line)
    return float(m.group(1)) if m else None

def test_golden_master_cli_matches_json():
    gm_path = TEST_DIR / "golden_master.json"
    assert gm_path.exists(), "golden_master.json not found in tests/"

    gm = json.loads(gm_path.read_text())
    steps = gm.get("steps", [])

    stdin_data = _build_stdin_from_steps(steps)

    cli_path = ROOT / "src" / "cli.py"
    assert cli_path.exists(), f"{cli_path} not found"

    proc = subprocess.run(
        [sys.executable, str(cli_path)],
        input=stdin_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=10,
    )

    out_lines = [ln.rstrip() for ln in proc.stdout.splitlines()]

    # iterate through steps and validate the corresponding output in order
    idx = 0
    for s in steps:
        op = s.get("op")
        if op == "total":
            idx, line = _find_next_line_containing(out_lines, idx, "Current balance")
            assert idx != -1, f"Expected 'Current balance' not found for step {s}"
            num = _extract_first_number(line)
            assert num == pytest_approx(s["expect"]), f"Total mismatch: got {num}, expected {s['expect']}"
            idx += 1
        elif op == "credit":
            # look for credited message or new balance
            idx_msg, _ = _find_next_line_containing(out_lines, idx, "Amount credited")
            idx_balance, line_balance = _find_next_line_containing(out_lines, idx, "New balance")
            # prefer explicit "New balance" line if present
            if idx_balance != -1:
                num = _extract_first_number(line_balance)
                assert num == pytest_approx(s["expect"]), f"Credit mismatch: got {num}, expected {s['expect']}"
                idx = idx_balance + 1
            elif idx_msg != -1:
                # maybe same line contains number
                _, line = _find_next_line_containing(out_lines, idx_msg, "Amount credited")
                num = _extract_first_number(line)
                assert num == pytest_approx(s["expect"]), f"Credit mismatch: got {num}, expected {s['expect']}"
                idx = idx_msg + 1
            else:
                raise AssertionError(f"Credit result not found in output for step {s}")
        elif op == "debit":
            if "expect_error" in s:
                idx_err, _ = _find_next_line_containing(out_lines, idx, s["expect_error"])
                assert idx_err != -1, f"Expected error '{s['expect_error']}' not found for step {s}"
                idx = idx_err + 1
            else:
                idx_msg, _ = _find_next_line_containing(out_lines, idx, "Amount debited")
                idx_balance, line_balance = _find_next_line_containing(out_lines, idx, "New balance")
                if idx_balance != -1:
                    num = _extract_first_number(line_balance)
                    assert num == pytest_approx(s["expect"]), f"Debit mismatch: got {num}, expected {s['expect']}"
                    idx = idx_balance + 1
                elif idx_msg != -1:
                    _, line = _find_next_line_containing(out_lines, idx_msg, "Amount debited")
                    num = _extract_first_number(line)
                    assert num == pytest_approx(s["expect"]), f"Debit mismatch: got {num}, expected {s['expect']}"
                    idx = idx_msg + 1
                else:
                    raise AssertionError(f"Debit result not found in output for step {s}")
        else:
            raise AssertionError(f"Unhandled op {op}")

# small helper to compare floats exactly to two decimals (matching CLI formatting)
def pytest_approx(value):
    # ensure value is a float with two decimals
    return round(float(value), 2)
