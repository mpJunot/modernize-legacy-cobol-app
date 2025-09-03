import os
import json
import subprocess
import tempfile
import pytest
from src.data import DataProgram
from src.operations import create_operations

GOLDEN_PATH = os.path.join(os.path.dirname(__file__), "golden_master.json")

def replay_python(golden):
    data = DataProgram(golden["initial"])
    ops = create_operations(data)
    results = []
    for step in golden["steps"]:
        op = step["op"]
        try:
            if op == "total":
                v = ops.total()
                results.append({"ok": round(v, 2)})
            elif op == "credit":
                v = ops.credit(step["amount"])
                results.append({"ok": round(v, 2)})
            elif op == "debit":
                v = ops.debit(step["amount"])
                results.append({"ok": round(v, 2)})
            else:
                results.append({"error": f"unknown op {op}"})
        except Exception as e:
            results.append({"error": str(e)})
    return results

def replay_cobol_via_runner(golden, runner_cmd):
    # The runner is expected to accept one argument: path to a JSON file (same schema as golden_master.json),
    # and to print to stdout a JSON array of step results matching replay_python format:
    #   [ {"ok": 1000.0}, {"ok": 1100.0}, {"error": "Insufficient funds"}, ... ]
    # This allows comparing Python vs COBOL outputs.
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
        json.dump(golden, tmp)
        tmp_path = tmp.name
    try:
        proc = subprocess.run([runner_cmd, tmp_path], capture_output=True, text=True, timeout=10)
        if proc.returncode != 0:
            raise RuntimeError(f"COBOL runner failed: {proc.stderr.strip()}")
        return json.loads(proc.stdout)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

@pytest.mark.parametrize("backend", ["python", "cobol"])
def test_golden_master(backend):
    with open(GOLDEN_PATH, "r") as f:
        golden = json.load(f)

    py_results = replay_python(golden)
    # validate python matches golden expectations first
    for step, exp, res in zip(golden["steps"], golden["steps"], py_results):
        if "expect" in step:
            assert "ok" in res, f"expected ok but got error: {res}"
            assert res["ok"] == pytest.approx(step["expect"], rel=1e-9)
        elif "expect_error" in step:
            assert "error" in res
            assert step["expect_error"] in res["error"]

    if backend == "python":
        return

    runner_cmd = os.environ.get("COBOL_RUNNER")
    if not runner_cmd:
        pytest.skip("COBOL_RUNNER not set; skipping COBOL golden master run")

    cobol_results = replay_cobol_via_runner(golden, runner_cmd)

    # compare sequences element-wise: either equal ok values or matching error substrings
    assert len(cobol_results) == len(py_results)
    for idx, (py_r, cob_r, step) in enumerate(zip(py_results, cobol_results, golden["steps"])):
        if "ok" in py_r:
            assert "ok" in cob_r, f"step {idx} expected ok, got {cob_r}"
            assert cob_r["ok"] == pytest.approx(py_r["ok"], rel=1e-9)
        else:
            # compare error messages by substring to avoid brittle text differences
            assert "error" in cob_r, f"step {idx} expected error, got {cob_r}"
            if "expect_error" in step:
                assert step["expect_error"] in cob_r["error"]
