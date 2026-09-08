"""Exercise only pre-import comparison guards after parent authorization."""

import argparse
import contextlib
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "tools/combat/compare_player_attack_rolls.py"
EVIDENCE = ROOT / "memory-bank/evidence/combat-player-attack-rolls-2026-09-07"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--inventory-sha256", required=True)
    args = parser.parse_args()
    attempts, rows = [], []

    def audit(event, values):
        if event == "import" and values[0].split(".")[0] in {"ankiscape", "pkg_alias", "tests"}:
            attempts.append(values[0])
            raise RuntimeError("Product import attempted during guard canary.")

    sys.addaudithook(audit)
    with tempfile.TemporaryDirectory(prefix="player-roll-guards-") as directory:
        scratch = Path(directory)
        baseline, wrong = scratch / "baseline.py", scratch / "wrong.py"
        baseline.write_bytes(gzip.decompress((EVIDENCE / "baseline-engine.py.gz").read_bytes()))
        wrong.write_bytes(b"wrong baseline")
        inventory = EVIDENCE / "source-inventory.json.gz"
        changed = json.loads(gzip.decompress(inventory.read_bytes()))
        changed["logic_pure/logic_pure_combat_engine.py"] = "0" * 64
        altered = scratch / "altered.json.gz"
        altered.write_bytes(gzip.compress(json.dumps(changed).encode(), mtime=0))
        altered_hash = hashlib.sha256(altered.read_bytes()).hexdigest()
        arguments = [str(PROBE), "--preflight", "--baseline", str(baseline), "--inventory", str(inventory), "--inventory-sha256", args.inventory_sha256, "--candidate-sha256", args.candidate_sha256, "--output", str(scratch / "result.json")]
        cases = [
            ("correct", [], None),
            ("wrong-baseline", ["--baseline", str(wrong)], "Baseline source hash differs."),
            ("wrong-candidate", ["--candidate-sha256", "0" * 64], "Candidate source hash differs."),
            ("wrong-inventory-pin", ["--inventory", str(altered)], "Inventory hash differs."),
            ("wrong-source-inventory", ["--inventory", str(altered), "--inventory-sha256", altered_hash], "Source inventory differs."),
        ]
        for name, extra, expected_error in cases:
            stdout, stderr = io.StringIO(), io.StringIO()
            with patch.object(sys, "argv", arguments + extra), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                try:
                    runpy.run_path(str(PROBE), run_name="__main__")
                except AssertionError as error:
                    assert expected_error is not None and str(error) == expected_error
                else:
                    assert expected_error is None
                    assert json.loads((scratch / "result.json").read_text())["status"] == "PREFLIGHT_PASS"
            assert not attempts
            rows.append({"case": name, "outcome": expected_error or "PREFLIGHT_PASS", "stdout": stdout.getvalue(), "stderr": stderr.getvalue()})
        bootstrap = """import runpy, sys
def audit(event, values):
    if event == 'import' and values[0].split('.')[0] in {'ankiscape', 'pkg_alias', 'tests'}:
        raise RuntimeError('Product import attempted during optimized canary.')
sys.addaudithook(audit)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
"""
        for name, flags, optimize in (("optimized-flag", ["-O"], None), ("optimized-env-zero", [], "0")):
            environment = dict(os.environ)
            environment.pop("PYTHONOPTIMIZE", None)
            if optimize is not None:
                environment["PYTHONOPTIMIZE"] = optimize
            result = subprocess.run([sys.executable, "-B", *flags, "-c", bootstrap, *arguments], env=environment, capture_output=True, text=True, timeout=30)
            assert result.returncode == 1 and result.stdout == ""
            assert result.stderr.strip() == "Refusing to run with optimizations; the pins are assertions."
            rows.append({"case": name, "outcome": result.stderr.strip()})
    assert not any(name.split(".")[0] in {"ankiscape", "pkg_alias", "tests"} for name in sys.modules)
    print(json.dumps({"status": "PASS", "cases": rows, "product_import_attempts": attempts}, indent=2))


if __name__ == "__main__":
    main()
