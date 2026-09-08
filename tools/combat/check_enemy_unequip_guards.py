"""Exercise only enemy-unequip pre-import guards after parent authorization."""

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "tools/combat/compare_enemy_unequip_transaction.py"
EVIDENCE = ROOT / "memory-bank/evidence/combat-unequip-transaction-2026-09-07"
BOOTSTRAP = """import runpy, sys
def audit(event, values):
    if event == 'import' and values[0].split('.')[0] in {'ankiscape', 'pkg_alias', 'tests'}:
        raise RuntimeError('Product import attempted during guard canary.')
sys.addaudithook(audit)
sys.argv = sys.argv[1:]
try:
    runpy.run_path(sys.argv[0], run_name='__main__')
except AssertionError as error:
    print(str(error), file=sys.stderr)
    raise SystemExit(1)
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--inventory-sha256", required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="enemy-unequip-guards-") as directory:
        scratch = Path(directory)
        baseline = EVIDENCE / "baseline-engine.py.gz"
        wrong_baseline = scratch / "wrong-baseline.py.gz"
        wrong_baseline.write_bytes(gzip.compress(b"wrong baseline", mtime=0))
        inventory = EVIDENCE / "source-inventory.json.gz"
        changed = json.loads(gzip.decompress(inventory.read_bytes()))
        changed["logic_pure/logic_pure_combat_engine.py"] = "0" * 64
        altered = scratch / "altered-inventory.json.gz"
        altered.write_bytes(
            gzip.compress(json.dumps(changed, sort_keys=True).encode(), mtime=0)
        )
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
            "--candidate-sha256",
            args.candidate_sha256,
            "--output",
            str(scratch / "result.json"),
        ]
        refused = "Refusing to run with optimizations; the pins are assertions."
        cases = (
            ("correct", (), None, (), None),
            (
                "wrong-baseline",
                ("--baseline", str(wrong_baseline)),
                "Stored baseline hash differs.",
                (),
                None,
            ),
            (
                "wrong-candidate",
                ("--candidate-sha256", "0" * 64),
                "Candidate source hash differs.",
                (),
                None,
            ),
            (
                "wrong-inventory-pin",
                ("--inventory", str(altered)),
                "Inventory hash differs.",
                (),
                None,
            ),
            (
                "wrong-source-inventory",
                ("--inventory", str(altered), "--inventory-sha256", altered_hash),
                "Source inventory differs.",
                (),
                None,
            ),
            ("optimized-flag", (), refused, ("-O",), None),
            ("optimized-env-zero", (), refused, (), "0"),
        )
        rows = []
        for name, extra, expected_error, flags, optimize in cases:
            environment = dict(os.environ)
            environment.pop("PYTHONOPTIMIZE", None)
            if optimize is not None:
                environment["PYTHONOPTIMIZE"] = optimize
            result = subprocess.run(
                [sys.executable, "-B", *flags, "-c", BOOTSTRAP, *arguments, *extra],
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
            )
            observed = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
            if expected_error is None:
                assert result.returncode == 0, observed
                assert result.stdout == result.stderr == "", observed
                assert json.loads(
                    (scratch / "result.json").read_text()
                )["status"] == "PREFLIGHT_PASS", observed
            else:
                assert result.returncode == 1 and result.stdout == "", observed
                assert result.stderr.strip() == expected_error, observed
            rows.append(
                {
                    "case": name,
                    "outcome": expected_error or "PREFLIGHT_PASS",
                    **observed,
                }
            )
    print(
        json.dumps(
            {
                "status": "PASS",
                "cases": rows,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
