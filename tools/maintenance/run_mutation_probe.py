#!/usr/bin/env python3
"""Run one focused mutation proof and restore the exact source bytes before exit."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.run_logged import read_command_file


@dataclass(frozen=True)
class ProbeFiles:
    backup: Path
    log: Path
    report: Path


@dataclass(frozen=True)
class ProbeOutcome:
    child_returncode: int | None
    timed_out: bool = False
    interrupted_signal: int | None = None


class ProbeInterrupted(Exception):
    def __init__(self, signal_number: int):
        self.signal_number = signal_number
        super().__init__(f"mutation probe interrupted by signal {signal_number}")


def _atomic_write(path: Path, data: bytes, mode: int | None = None) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        if mode is not None:
            temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _write_report(path: Path, record: dict[str, object]) -> None:
    _atomic_write(path, (json.dumps(record, indent=2) + "\n").encode())


def _invalidate_bytecode(source: Path) -> None:
    cache = source.parent / "__pycache__"
    if not cache.is_dir():
        return
    for bytecode in cache.glob(f"{source.stem}.*.pyc"):
        bytecode.unlink()


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def _run_child(command: Sequence[str], worktree: Path, log: Path, timeout: float) -> ProbeOutcome:
    environment = dict(os.environ)
    environment["ANKISCAPE_MUTATION_PROBE_PID"] = str(os.getpid())
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with log.open("wb") as output:
        process = subprocess.Popen(
            command,
            cwd=worktree,
            env=environment,
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            return ProbeOutcome(process.wait(timeout=timeout))
        except subprocess.TimeoutExpired:
            _stop_process(process)
            return ProbeOutcome(None, timed_out=True)
        except ProbeInterrupted as exc:
            _stop_process(process)
            return ProbeOutcome(None, interrupted_signal=exc.signal_number)


def _signal_handler(signal_number: int, _frame: object) -> None:
    raise ProbeInterrupted(signal_number)


def _install_signal_handlers() -> dict[int, object]:
    previous = {}
    for signal_number in (signal.SIGINT, signal.SIGTERM):
        previous[signal_number] = signal.signal(signal_number, _signal_handler)
    return previous


def _restore_signal_handlers(previous: dict[int, object]) -> None:
    for signal_number, handler in previous.items():
        signal.signal(signal_number, handler)


def _probe_files(evidence: Path, source: Path) -> ProbeFiles:
    run_id = f"{source.stem}-{uuid.uuid4().hex[:10]}"
    return ProbeFiles(
        backup=evidence / f"{run_id}.original",
        log=evidence / f"{run_id}.log",
        report=evidence / f"{run_id}.json",
    )


def _validate_paths(
    source: Path, mutant: Path, worktree: Path, evidence: Path,
) -> tuple[bytes, bytes]:
    if not (worktree / ".git").is_file():
        raise ValueError("--worktree must be a linked worktree, not the canonical checkout")
    if not source.is_file() or not source.is_relative_to(worktree):
        raise ValueError("source must be an existing file inside --worktree")
    if not mutant.is_file():
        raise ValueError("mutant must be an existing file")
    if evidence.is_relative_to(worktree):
        raise ValueError("--evidence-dir must be outside the worktree")
    original, mutation = source.read_bytes(), mutant.read_bytes()
    if original == mutation:
        raise ValueError("mutant must differ from the source bytes")
    return original, mutation


def _record(
    source: Path, mutant: Path, worktree: Path, files: ProbeFiles,
    command: Sequence[str], timeout: float,
) -> dict[str, object]:
    return {
        "status": "prepared",
        "source": str(source),
        "mutant": str(mutant),
        "worktree": str(worktree),
        "backup_path": str(files.backup),
        "log_path": str(files.log),
        "command": list(command),
        "timeout_seconds": timeout,
        "child_returncode": None,
        "timed_out": False,
        "interrupted_signal": None,
        "restoration_verified": False,
        "proof_passed": False,
    }


def _execute_probe(
    source: Path, mutation: bytes, original: bytes, mode: int, worktree: Path,
    files: ProbeFiles, command: Sequence[str], timeout: float, record: dict[str, object],
) -> ProbeOutcome:
    previous_handlers = _install_signal_handlers()
    outcome = ProbeOutcome(None)
    try:
        _atomic_write(source, mutation, mode)
        _invalidate_bytecode(source)
        record["status"] = "mutated"
        _write_report(files.report, record)
        outcome = _run_child(command, worktree, files.log, timeout)
    except ProbeInterrupted as exc:
        outcome = ProbeOutcome(None, interrupted_signal=exc.signal_number)
    finally:
        try:
            _atomic_write(source, original, mode)
            _invalidate_bytecode(source)
            record["restoration_verified"] = source.read_bytes() == original
        finally:
            _restore_signal_handlers(previous_handlers)
    return outcome


def _exit_code(outcome: ProbeOutcome, restored: bool) -> int:
    if not restored:
        return 2
    if outcome.interrupted_signal is not None:
        return 128 + outcome.interrupted_signal
    if outcome.timed_out:
        return 124
    if outcome.child_returncode is None:
        return 2
    return int(outcome.child_returncode == 0)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("mutant", type=Path)
    parser.add_argument("--worktree", type=Path, default=ROOT)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--command-file", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=600.0)
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    source = args.source.expanduser().resolve()
    mutant = args.mutant.expanduser().resolve()
    worktree = args.worktree.expanduser().resolve()
    evidence = args.evidence_dir.expanduser().resolve()
    try:
        command = read_command_file(args.command_file.expanduser().resolve())
        original, mutation = _validate_paths(source, mutant, worktree, evidence)
        evidence.mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    files = _probe_files(evidence, source)
    mode = source.stat().st_mode
    files.backup.write_bytes(original)
    with files.backup.open("rb") as backup:
        os.fsync(backup.fileno())
    record = _record(source, mutant, worktree, files, command, args.timeout)
    _write_report(files.report, record)
    try:
        outcome = _execute_probe(
            source, mutation, original, mode, worktree, files, command, args.timeout, record,
        )
    except OSError as exc:
        outcome = ProbeOutcome(None)
        record["error"] = str(exc)
    record.update({
        "child_returncode": outcome.child_returncode,
        "timed_out": outcome.timed_out,
        "interrupted_signal": outcome.interrupted_signal,
    })
    restored = bool(record["restoration_verified"])
    record["proof_passed"] = bool(
        restored
        and outcome.child_returncode not in (None, 0)
        and not outcome.timed_out
        and outcome.interrupted_signal is None
    )
    record["status"] = "restored" if restored else "restoration_failed"
    _write_report(files.report, record)
    print(f"Mutation log: {files.log}")
    print(f"Mutation report: {files.report}")
    print(f"Recovery backup: {files.backup}")
    return _exit_code(outcome, restored)


if __name__ == "__main__":
    raise SystemExit(main())
