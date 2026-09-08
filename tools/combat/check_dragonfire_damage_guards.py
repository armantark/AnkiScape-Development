"""Exercise only pre-import dragonfire comparison guards."""

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
PROBE = ROOT / "tools/combat/compare_dragonfire_damage.py"
EVIDENCE = ROOT / "memory-bank/evidence/combat-dragonfire-damage-2026-09-08"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-engine-sha256", required=True)
    parser.add_argument("--candidate-specials-sha256", required=True)
    parser.add_argument("--inventory-sha256", required=True)
    args = parser.parse_args()
    attempts = []
    rows = []

    def audit(event, values):
        if event == "import" and values[0].split(".")[0] in {
            "ankiscape",
            "pkg_alias",
            "tests",
        }:
            attempts.append(values[0])
            raise RuntimeError("Product import attempted during guard canary.")

    sys.addaudithook(audit)
    with tempfile.TemporaryDirectory(prefix="dragonfire-damage-guards-") as directory:
        scratch = Path(directory)
        baseline = scratch / "baseline.py"
        wrong = scratch / "wrong.py"
        baseline.write_bytes(
            gzip.decompress((EVIDENCE / "baseline-engine.py.gz").read_bytes())
        )
        wrong.write_bytes(b"wrong baseline")
        inventory = EVIDENCE / "source-inventory.json.gz"
        changed = json.loads(gzip.decompress(inventory.read_bytes()))
        changed["logic_pure/logic_pure_combat_engine.py"] = "0" * 64
        altered = scratch / "altered.json.gz"
        altered.write_bytes(gzip.compress(json.dumps(changed).encode(), mtime=0))
        altered_hash = hashlib.sha256(altered.read_bytes()).hexdigest()
        arguments = [
            str(PROBE),
            "--preflight",
            "--baseline",
            str(baseline),
            "--inventory",
            str(inventory),
            "--inventory-sha256",
            args.inventory_sha256,
            "--candidate-engine-sha256",
            args.candidate_engine_sha256,
            "--candidate-specials-sha256",
            args.candidate_specials_sha256,
            "--output",
            str(scratch / "result.json"),
        ]
        cases = [
            ("correct", [], None),
            (
                "wrong-baseline",
                ["--baseline", str(wrong)],
                "Baseline source hash differs.",
            ),
            (
                "wrong-engine",
                ["--candidate-engine-sha256", "0" * 64],
                "Candidate engine source hash differs.",
            ),
            (
                "wrong-specials",
                ["--candidate-specials-sha256", "0" * 64],
                "Candidate specials source hash differs.",
            ),
            (
                "wrong-inventory-pin",
                ["--inventory", str(altered)],
                "Inventory hash differs.",
            ),
            (
                "wrong-source-inventory",
                [
                    "--inventory",
                    str(altered),
                    "--inventory-sha256",
                    altered_hash,
                ],
                "Source inventory differs.",
            ),
        ]
        for name, extra, expected_error in cases:
            stdout = io.StringIO()
            stderr = io.StringIO()
            observed_error = None
            exception_type = None
            with (
                patch.object(sys, "argv", arguments + extra),
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                try:
                    runpy.run_path(str(PROBE), run_name="__main__")
                    report = json.loads((scratch / "result.json").read_text())
                    assert report["status"] == "PREFLIGHT_PASS"
                except BaseException as error:
                    observed_error = str(error)
                    exception_type = type(error).__name__
            row = {
                "case": name,
                "outcome": observed_error or "PREFLIGHT_PASS",
                "observed_error": observed_error,
                "exception_type": exception_type,
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "returncode": None,
                "execution": "in-process",
            }
            rows.append(row)
            assert observed_error == expected_error, {
                "cases": rows,
                "product_import_attempts": attempts,
            }
            assert exception_type == (
                "AssertionError" if expected_error else None
            ), {"cases": rows}
            assert not attempts, {
                "cases": rows,
                "product_import_attempts": attempts,
            }
        bootstrap = """import runpy, sys
def audit(event, values):
    if event == 'import' and values[0].split('.')[0] in {'ankiscape', 'pkg_alias', 'tests'}:
        raise RuntimeError('Product import attempted during optimized canary.')
sys.addaudithook(audit)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
"""
        for name, flags, optimize in (
            ("optimized-flag", ["-O"], None),
            ("optimized-env-zero", [], "0"),
        ):
            environment = dict(os.environ)
            environment.pop("PYTHONOPTIMIZE", None)
            if optimize is not None:
                environment["PYTHONOPTIMIZE"] = optimize
            result = subprocess.run(
                [sys.executable, "-B", *flags, "-c", bootstrap, *arguments],
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
            )
            row = {
                "case": name,
                "outcome": result.stderr.strip(),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution": "subprocess",
            }
            rows.append(row)
            assert result.returncode == 1 and result.stdout == "", {"cases": rows}
            assert result.stderr.strip() == (
                "Refusing to run with optimizations; the pins are assertions."
            ), {"cases": rows}
    assert not any(
        name.split(".")[0] in {"ankiscape", "pkg_alias", "tests"}
        for name in sys.modules
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "cases": rows,
                "product_import_attempts": attempts,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
