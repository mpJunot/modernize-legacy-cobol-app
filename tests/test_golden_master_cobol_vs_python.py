import sys
import subprocess
import json
import re
from pathlib import Path

TEST_DIR = Path(__file__).parent
ROOT = TEST_DIR.parent
ARTIFACTS = TEST_DIR / "artifacts"


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
        elif op == "raw":
            inputs.append(str(s.get("value", "")))
        else:
            raise ValueError(f"unknown op {op}")
    inputs.append("4")  # exit at the end
    return "\n".join(inputs) + "\n"


def _extract_numbers(stdout_text):
    # capture all monetary values like 001000.00 or -000010.25
    return [float(m) for m in re.findall(r"-?\d+\.\d{2}", stdout_text)]


def _read_golden():
    gm_path = TEST_DIR / "golden_master.json"
    assert gm_path.exists(), "golden_master.json not found in tests/"
    return json.loads(gm_path.read_text())


def _run_program(cmd, stdin_data):
    return subprocess.run(
        cmd,
        input=stdin_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=15,
        cwd=str(ROOT),
    )


def test_cobol_and_python_outputs_match_and_are_saved(tmp_path):
    gm = _read_golden()
    steps = gm.get("steps", [])
    stdin_data = _build_stdin_from_steps(steps)

    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    py_cli = ROOT / "src" / "cli.py"
    assert py_cli.exists(), f"{py_cli} not found"
    py_proc = _run_program([sys.executable, str(py_cli)], stdin_data)

    cobol_bin = ROOT / "accountsystem"
    assert cobol_bin.exists() and cobol_bin.is_file(), "COBOL binary 'accountsystem' not found at project root"
    cobol_proc = _run_program([str(cobol_bin)], stdin_data)

    py_out_file = ARTIFACTS / "python_output.txt"
    cobol_out_file = ARTIFACTS / "cobol_output.txt"
    py_out_file.write_text(py_proc.stdout)
    cobol_out_file.write_text(cobol_proc.stdout)

    # compare sequences of monetary values
    py_vals = _extract_numbers(py_proc.stdout)
    co_vals = _extract_numbers(cobol_proc.stdout)

    assert py_vals == co_vals, (
        "Mismatch in monetary output sequence between Python and COBOL.\n"
        f"Python values: {py_vals}\n"
        f"COBOL values:  {co_vals}\n"
        f"See artifacts: {py_out_file} and {cobol_out_file}"
    )

    # validate additional expectations if provided
    for s in steps:
        if "expect_error" in s:
            err = s["expect_error"]
            assert err in py_proc.stdout, f"Expected error not in Python output: {err}"
            assert err in cobol_proc.stdout, f"Expected error not in COBOL output: {err}"
        if "expect_contains" in s:
            txt = s["expect_contains"]
            assert txt in py_proc.stdout, f"Expected text not in Python output: {txt}"
            assert txt in cobol_proc.stdout, f"Expected text not in COBOL output: {txt}"
