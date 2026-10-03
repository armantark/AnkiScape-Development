"""Repeat the mirror-lock focused proof five times, then run the full plain lane."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from tools import run_remote_tests as runner
from tools.promotion.lane_execution import _hold_remote_mirror


SELECTORS = (
    "test_remote_mirror_priority", "test_remote_mirror_lock", "test_remote_test_host",
    "test_promotion_gate.", "test_memory_bank_queue_packet.",
)


def record_run(evidence: Path, name: str, command: list[str], **options) -> str:
    log_path = evidence / f"review-{name}.log"
    checkpoint = evidence / f"review-{name}.json"
    record = {
        "command": command, "log": str(log_path), "status": "pending",
        "revision": subprocess.check_output(("git", "rev-parse", "HEAD"), text=True).strip(),
        "dirty_tree": subprocess.check_output(("git", "status", "--porcelain"), text=True),
    }
    checkpoint.write_text(json.dumps(record, indent=2) + "\n")
    print(f"Starting {name}: {log_path}", flush=True)
    with log_path.open("w") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, **options)
    output = log_path.read_text()
    record.update(status=result.returncode, output=output)
    checkpoint.write_text(json.dumps(record, indent=2) + "\n")
    if result.returncode:
        print(output, flush=True)
        raise SystemExit(result.returncode)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    os.chdir(root)
    args.evidence = args.evidence.resolve()
    args.evidence.mkdir(parents=True, exist_ok=True)
    inventory = record_run(
        args.evidence, "local-count", [sys.executable, "run_tests.py", "--count", *SELECTORS],
    )
    expected = runner.parse_count_inventory(inventory)
    command = [sys.executable, "tools/run_remote_tests.py", str(root), "plain"]
    selection = [argument for selector in SELECTORS for argument in ("--select", selector)]
    with (args.evidence / "review-mirror.log").open("w") as log:
        with _hold_remote_mirror(log, lambda: log.flush()) as descriptor:
            if descriptor is None:
                return 1
            options = {
                "env": {**os.environ, runner.INHERITED_MIRROR_LOCK_FD: str(descriptor)},
                "pass_fds": (descriptor,),
            }
            inventory = record_run(
                args.evidence, "remote-count", [*command, *selection, "--collect-only"], **options,
            )
            if runner.parse_count_inventory(inventory) != expected:
                raise RuntimeError("local and remote focused inventories differ")
            focused = [*command, *selection, "--expected-tests", str(expected)]
            for attempt in range(1, 6):
                output = record_run(args.evidence, f"focused-{attempt}", focused, **options)
                summary = runner.parse_unittest_summary(output)
                print(f"Focused {attempt}:\n{summary.ran_line}\n{summary.result_line}", flush=True)
            output = record_run(args.evidence, "full-plain", command, **options)
            summary = runner.parse_unittest_summary(output)
            print(f"Full plain:\n{summary.ran_line}\n{summary.result_line}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
