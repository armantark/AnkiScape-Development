#!/usr/bin/env python3
"""Run one focused mutation proof and restore the exact source bytes before exit.

Separate mutate, test, and restore commands once left a red-proof mutant in a
worktree whose progress notes already reported the fix green, so this tool makes
restoration part of the proof result: it exits 0 only when the focused command
fails under the mutant and the source is verified back to its pre-probe bytes.
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]


def _exit_on_signal(signal_number: int, _frame: object) -> None:
    raise SystemExit(128 + signal_number)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("mutant", type=Path)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("command", nargs="+", help="focused test command, after --")
    args = parser.parse_args(argv)
    source = args.source.resolve()
    if not (ROOT / ".git").is_file():
        parser.error("run mutation proofs from a linked worktree, not the canonical checkout")
    if not source.is_file() or not source.is_relative_to(ROOT):
        parser.error(f"source must be an existing file inside {ROOT}")

    original = source.read_bytes()
    mutation = args.mutant.read_bytes()
    with tempfile.NamedTemporaryFile(prefix=f"{source.name}.", suffix=".original", delete=False) as backup:
        backup.write(original)
    print(f"Recovery backup for {source}: {backup.name}", flush=True)

    previous_handler = signal.signal(signal.SIGTERM, _exit_on_signal)
    red = False
    try:
        source.write_bytes(mutation)
        # A mutant .pyc written in the same second as the restore could outlive it.
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            completed = subprocess.run(args.command, cwd=ROOT, env=environment, timeout=args.timeout, check=False)
            red = completed.returncode != 0
        except subprocess.TimeoutExpired:
            print(f"focused command exceeded {args.timeout:g} seconds", file=sys.stderr)
    finally:
        source.write_bytes(original)
        signal.signal(signal.SIGTERM, previous_handler)

    if source.read_bytes() != original:
        print(f"error: restoration failed; recover {source} from {backup.name}", file=sys.stderr)
        return 2
    Path(backup.name).unlink()
    print(f"Mutation proof: {'red' if red else 'NOT red'}; {source} restored")
    return 0 if red else 1


if __name__ == "__main__":
    raise SystemExit(main())
