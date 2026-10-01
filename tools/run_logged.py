#!/usr/bin/env python3
"""Run one command quietly, preserve its exit code, and retain a complete log."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
import tempfile
from collections import deque
from pathlib import Path
from typing import Sequence


def run_logged(
    command: Sequence[str],
    *,
    label: str,
    summary_lines: int,
    log_dir: Path | None = None,
) -> tuple[int, Path, list[str]]:
    directory = log_dir or Path(tempfile.gettempdir()) / "ankiscape-check-logs"
    directory.mkdir(parents=True, exist_ok=True)
    safe_label = "".join(character if character.isalnum() or character in "-_" else "-" for character in label)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=f"{safe_label or 'check'}-",
        suffix=".log",
        dir=directory,
        delete=False,
    ) as log:
        log_path = Path(log.name)
        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)

    with log_path.open(encoding="utf-8", errors="replace") as log:
        tail = list(deque((line.rstrip("\n") for line in log), maxlen=summary_lines))
    return completed.returncode, log_path, tail


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="check")
    parser.add_argument("--summary-lines", type=int, default=12)
    parser.add_argument("--log-dir", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)

    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command is required after --")
    if args.summary_lines < 1:
        parser.error("--summary-lines must be at least 1")

    returncode, log_path, tail = run_logged(
        command,
        label=args.label,
        summary_lines=args.summary_lines,
        log_dir=args.log_dir,
    )
    outcome = "PASS" if returncode == 0 else f"FAIL (exit {returncode})"
    print(f"{args.label}: {outcome}")
    for line in tail:
        print(line)
    print(f"Full log: {log_path}")
    if returncode != 0:
        print(f"Command: {shlex.join(command)}", file=sys.stderr)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
