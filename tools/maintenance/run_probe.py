#!/usr/bin/env python3
"""Run exact child commands with durable logs, deadlines, and completion records."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Sequence, TextIO


def _atomic_json(path: Path, value: object) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(value, output, indent=2)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _read_commands(path: Path) -> list[list[str]]:
    try:
        commands = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON commands file: {exc}") from exc
    if not isinstance(commands, list) or not commands:
        raise ValueError("commands file must contain a non-empty list of argument vectors")
    if any(not isinstance(command, list) or not command for command in commands):
        raise ValueError("every command must be a non-empty argument vector")
    if any(not isinstance(argument, str) or not argument for command in commands for argument in command):
        raise ValueError("every command argument must be a non-empty string")
    return commands


def _stop_process(process: subprocess.Popen[object]) -> None:
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def _run_command(
    command: Sequence[str], worktree: Path, timeout: float, log: TextIO,
) -> dict[str, object]:
    print(f"$ {shlex.join(command)}", file=log, flush=True)
    try:
        process = subprocess.Popen(
            command,
            cwd=worktree,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            text=True,
        )
    except OSError as exc:
        print(f"launch failed: {exc}", file=log, flush=True)
        return {"command": list(command), "returncode": 127, "timed_out": False}
    timed_out = False
    try:
        returncode = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        _stop_process(process)
        returncode = 124
    print(f"exit: {returncode}", file=log, flush=True)
    return {
        "command": list(command),
        "returncode": returncode,
        "timed_out": timed_out,
    }


def _worker(spec_path: Path) -> int:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    worktree = Path(spec["worktree"])
    log_path = Path(spec["log_path"])
    report_path = Path(spec["report_path"])
    results = []
    started = time.monotonic()
    try:
        with log_path.open("a", encoding="utf-8") as log:
            for command in spec["commands"]:
                results.append(_run_command(command, worktree, spec["timeout_seconds"], log))
        record = {
            "complete": True,
            "label": spec["label"],
            "worktree": str(worktree),
            "log_path": str(log_path),
            "elapsed_seconds": time.monotonic() - started,
            "commands": results,
        }
        _atomic_json(report_path, record)
    finally:
        spec_path.unlink(missing_ok=True)
    failures = [row["returncode"] for row in results if row["returncode"]]
    return int(failures[0]) if failures else 0


def _safe_label(label: str) -> str:
    safe = "".join(character if character.isalnum() or character in "-_" else "-" for character in label)
    if not safe:
        raise ValueError("--label must contain a letter, number, dash, or underscore")
    return safe


def _launch_spec(
    commands: list[list[str]], worktree: Path, evidence: Path, label: str, timeout: float,
) -> Path:
    run_id = f"{_safe_label(label)}-{uuid.uuid4().hex[:10]}"
    spec_path = evidence / f"{run_id}.pending.json"
    spec = {
        "label": label,
        "worktree": str(worktree),
        "log_path": str(evidence / f"{run_id}.log"),
        "report_path": str(evidence / f"{run_id}.json"),
        "timeout_seconds": timeout,
        "commands": commands,
    }
    _atomic_json(spec_path, spec)
    return spec_path


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commands-file", type=Path)
    parser.add_argument("--worktree", type=Path)
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--label", default="probe")
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--detach", action="store_true")
    parser.add_argument("--worker-spec", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker_spec is not None:
        return args
    if None in (args.commands_file, args.worktree, args.evidence_dir):
        parser.error("--commands-file, --worktree, and --evidence-dir are required")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.worker_spec is not None:
        return _worker(args.worker_spec.resolve())
    worktree = args.worktree.expanduser().resolve()
    evidence = args.evidence_dir.expanduser().resolve()
    try:
        if not worktree.is_dir():
            raise ValueError("--worktree must be an existing directory")
        if evidence.is_relative_to(worktree):
            raise ValueError("--evidence-dir must be outside the worktree")
        commands = _read_commands(args.commands_file.expanduser().resolve())
        evidence.mkdir(parents=True, exist_ok=True)
        spec_path = _launch_spec(commands, worktree, evidence, args.label, args.timeout)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    print(f"Probe log: {spec['log_path']}")
    print(f"Completion record: {spec['report_path']}")
    if not args.detach:
        return _worker(spec_path)
    worker = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--worker-spec", str(spec_path)],
        cwd=worktree,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    print(f"Detached worker pid: {worker.pid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
