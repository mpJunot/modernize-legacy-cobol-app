import sys
import subprocess
from pathlib import Path

TEST_DIR = Path(__file__).parent
ROOT = TEST_DIR.parent


def _run(cmd, stdin):
    return subprocess.run(
        cmd,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=20,
        cwd=str(ROOT),
    )

# Extract numbers from the output
def _numbers(s):
    import re
    return [float(x) for x in re.findall(r"-?\d+\.\d{2}", s)]


def test_menu_empty_input_then_valid_sequence():
    # Empty line as first menu input should yield an invalid choice, then continue
    stdin = "\n1\n4\n"
    py = _run([sys.executable, str(ROOT / "src" / "cli.py")], stdin)
    assert "Invalid choice" in py.stdout
    assert "Current balance" in py.stdout
    assert "Exiting the program. Goodbye!" in py.stdout


def test_long_sequence_cobol_vs_python_consistency():
    steps = []
    steps.extend(["2\n10\n"] * 100)
    steps.extend(["3\n5\n"] * 100)
    stdin = "".join(steps) + "4\n"

    py = _run([sys.executable, str(ROOT / "src" / "cli.py")], stdin)
    co = _run([str(ROOT / "accountsystem")], stdin)

    py_vals = _numbers(py.stdout)
    co_vals = _numbers(co.stdout)
    assert py_vals == co_vals, (
        "Mismatch in long-sequence monetary outputs between Python and COBOL"
    )
