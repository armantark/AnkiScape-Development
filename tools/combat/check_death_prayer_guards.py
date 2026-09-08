"""Check death-prayer comparison refusals without importing product code."""

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
EVIDENCE = ROOT / "memory-bank/evidence/combat-death-prayer-2026-09-08"
PROBE = ROOT / "tools/combat/compare_death_prayer.py"


def preflight_cases(arguments, altered, altered_pin):
    rows = []
    for label, overrides, expected in (
        ("correct", [], None),
        ("wrong-inventory-pin", ["--inventory-sha256", "0" * 64], "Inventory hash differs"),
        ("wrong-source", ["--inventory", str(altered), "--inventory-sha256", altered_pin], "Source differs"),
    ):
        error = None
        with patch.object(sys, "argv", arguments + overrides):
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    runpy.run_path(str(PROBE), run_name="__main__")
            except ValueError as exc:
                error = str(exc)
        passed = error is None if expected is None else expected in (error or "")
        rows.append({"case": label, "pass": passed, "error": error})
    return rows


def optimization_cases(arguments):
    rows = []
    for label, flag, value in (("optimize-flag", "-O", None), ("optimize-env", None, "0")):
        environment = dict(os.environ)
        environment.pop("PYTHONOPTIMIZE", None)
        if value is not None:
            environment["PYTHONOPTIMIZE"] = value
        command = [sys.executable] + ([flag] if flag else []) + arguments
        result = subprocess.run(command, env=environment, capture_output=True, text=True)
        rows.append({
            "case": label,
            "pass": result.returncode != 0 and "Optimized interpreter refused" in result.stderr,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-sha256", required=True)
    args = parser.parse_args()
    attempts = []
    rows = []

    def audit(event, values):
        if event == "import" and values[0].split(".")[0] in {"ankiscape", "pkg_alias", "tests"}:
            attempts.append(values[0])
            raise RuntimeError("Product import attempted during guard canary.")

    sys.addaudithook(audit)
    with tempfile.TemporaryDirectory(prefix="death-prayer-guards-") as directory:
        scratch = Path(directory)
        inventory = EVIDENCE / "source-inventory.json.gz"
        changed = json.loads(gzip.decompress(inventory.read_bytes()))
        changed["logic_pure/logic_pure_combat_engine.py"] = "0" * 64
        altered = scratch / "altered.json.gz"
        altered.write_bytes(gzip.compress(json.dumps(changed).encode(), mtime=0))
        altered_pin = hashlib.sha256(altered.read_bytes()).hexdigest()
        arguments = [
            str(PROBE), "--preflight", "--inventory", str(inventory),
            "--inventory-sha256", args.inventory_sha256,
            "--output", str(scratch / "result.json"),
        ]
        rows.extend(preflight_cases(arguments, altered, altered_pin))
        rows.extend(optimization_cases(arguments))
    report = {"cases": rows, "product_import_attempts": attempts}
    print(json.dumps(report, indent=2))
    if attempts or not all(row["pass"] for row in rows):
        raise SystemExit("Death-prayer source guard failed.")


if __name__ == "__main__":
    main()
