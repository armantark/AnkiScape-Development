"""Promotion lock ownership, heartbeat, and stale-lock recovery."""

from __future__ import annotations

import fcntl
import json
import os
import sys
import uuid
from dataclasses import asdict, dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import IO, TextIO

from .contract import (
    ACTIVE_GATE_DIR_NAME,
    LAND_LOCK_NAME,
    LONGEST_LANE_TIMEOUT,
    GateError,
    LockRecord,
)
from .promotion_process import format_age, kill_process_tree, open_locked_file
from .repository import evidence_path_for, git_common_dir


@dataclass
class HeldLock:
    path: Path
    stream: IO[str]
    record: LockRecord

    def refresh(self) -> None:
        if self.stream.closed:
            return
        self.record = LockRecord(
            **{
                **asdict(self.record),
                "heartbeat_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            }
        )
        _write_record(self.stream, self.record)

    def update_target(self, worktree: Path, commit: str) -> None:
        self.record = replace(
            self.record,
            worktree=str(worktree.resolve()),
            commit=commit,
        )
        _write_record(self.stream, self.record)

    def release(self) -> None:
        if self.stream.closed:
            return
        self.path.unlink(missing_ok=True)
        self.stream.close()


def landing_lock_path_for(repo: Path) -> Path:
    return git_common_dir(repo) / LAND_LOCK_NAME


def active_gate_dir_for(repo: Path) -> Path:
    return git_common_dir(repo) / ACTIVE_GATE_DIR_NAME


def _new_lock_record(operation: str, worktree: Path, commit: str) -> LockRecord:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    return LockRecord(
        pid=os.getpid(),
        operation=operation,
        worktree=str(worktree.resolve()),
        commit=commit,
        started_at=now,
        token=uuid.uuid4().hex,
        heartbeat_at=now,
    )


def _write_record(stream: IO[str], record: LockRecord) -> None:
    stream.seek(0)
    stream.truncate()
    json.dump(asdict(record), stream, sort_keys=True)
    stream.write("\n")
    stream.flush()
    os.fsync(stream.fileno())


def _read_record_path(path: Path) -> LockRecord:
    try:
        return LockRecord.from_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except OSError as exc:
        raise GateError(f"Cannot read promotion lock {path}: {exc}") from exc
    except GateError as exc:
        raise GateError(f"{exc} at {path}; inspect it before proceeding") from exc


def _record_age(record: LockRecord) -> float:
    try:
        heartbeat = datetime.fromisoformat(record.heartbeat_at or record.started_at)
    except ValueError:
        return float("inf")
    return max(0.0, (datetime.now().astimezone() - heartbeat).total_seconds())


def _reclaim_stale_lock(path: Path, record: LockRecord) -> None:
    kill_process_tree(record.pid)


def claim_landing_lock(
    repo: Path,
    *,
    operation: str,
    worktree: Path,
    commit: str,
    wait: bool = False,
    recover_stale: bool = True,
) -> HeldLock:
    path = landing_lock_path_for(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        stream = open_locked_file(path, wait=wait)
    except BlockingIOError:
        if not recover_stale:
            raise GateError("Promotion landing lock held; stale recovery is disabled") from None
        try:
            existing = _read_record_path(path)
        except FileNotFoundError:
            return claim_landing_lock(repo, operation=operation, worktree=worktree, commit=commit, wait=wait)
        except GateError as exc:
            raise GateError(f"Promotion landing lock held: {exc}") from None
        age = _record_age(existing)
        if age > LONGEST_LANE_TIMEOUT:
            _reclaim_stale_lock(path, existing)
            return claim_landing_lock(
                repo,
                operation=operation,
                worktree=worktree,
                commit=commit,
                wait=wait,
            )
        detail = (
            f"PID {existing.pid} is {existing.operation} for {existing.commit} in "
            f"{existing.worktree} since {existing.started_at}; "
            f"held for {format_age(_record_age(existing))}"
        )
        raise GateError(f"Promotion landing lock held: {detail}") from None
    record = _new_lock_record(operation, worktree, commit)
    _write_record(stream, record)
    return HeldLock(path, stream, record=record)


def claim_gate_marker(worktree: Path, commit: str) -> HeldLock:
    directory = active_gate_dir_for(worktree)
    directory.mkdir(parents=True, exist_ok=True)
    record = _new_lock_record("gate", worktree, commit)
    path = directory / f"{record.token}.json"
    stream = path.open("x+", encoding="utf-8")
    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    _write_record(stream, record)
    return HeldLock(path, stream, record=record)


def _invalidate_evidence(repo: Path, commit: str) -> None:
    evidence_path_for(repo, commit).unlink(missing_ok=True)


def register_gate(
    worktree: Path,
    commit: str,
    *,
    stderr: TextIO = sys.stderr,
    coordination: HeldLock | None = None,
) -> HeldLock:
    owns_coordination = coordination is None
    if coordination is None:
        coordination = claim_landing_lock(
            worktree,
            operation="registering a gate",
            worktree=worktree,
            commit=commit,
            wait=True,
        )
    try:
        for active in active_gate_records(worktree, stderr=stderr):
            if active.commit == commit:
                raise GateError(
                    f"Gate already running for exact commit {commit}: PID {active.pid} in "
                    f"{active.worktree} since {active.started_at}"
                )
        _invalidate_evidence(worktree, commit)
        return claim_gate_marker(worktree, commit)
    finally:
        if owns_coordination:
            coordination.release()


def active_gate_records(
    repo: Path,
    *,
    stderr: TextIO = sys.stderr,
) -> tuple[LockRecord, ...]:
    directory = active_gate_dir_for(repo)
    if not directory.exists():
        return ()
    active: list[LockRecord] = []
    for path in sorted(directory.glob("*.json")):
        try:
            stream = path.open("r+", encoding="utf-8")
        except FileNotFoundError:
            continue
        try:
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                stream.seek(0)
                try:
                    record = LockRecord.from_json(stream.read())
                except GateError as exc:
                    raise GateError(
                        f"{exc} at active gate marker {path}; inspect it before proceeding"
                    ) from exc
                age = _record_age(record)
                if age > LONGEST_LANE_TIMEOUT:
                    print(
                        f"Stale promotion gate marker: {record.commit} PID {record.pid} "
                        f"held for {format_age(age)}. Killing its process tree.",
                        file=stderr,
                    )
                    _reclaim_stale_lock(path, record)
                    path.unlink(missing_ok=True)
                else:
                    active.append(record)
                continue

            stream.seek(0)
            try:
                stale = LockRecord.from_json(stream.read())
                detail = (
                    f"it recorded {stale.operation} PID {stale.pid} for {stale.commit} "
                    f"in {stale.worktree} since {stale.started_at}"
                )
            except GateError:
                detail = "its record is unreadable"
            print(f"Stale promotion gate marker: {detail}. Removing {path}.", file=stderr)
            path.unlink(missing_ok=True)
        finally:
            stream.close()
    return tuple(active)


_PUBLIC_MODULE = f"{__package__.rsplit('.', 1)[0]}.promotion_gate"
HeldLock.__module__ = _PUBLIC_MODULE
landing_lock_path_for.__module__ = _PUBLIC_MODULE
active_gate_dir_for.__module__ = _PUBLIC_MODULE
_new_lock_record.__module__ = _PUBLIC_MODULE
_write_record.__module__ = _PUBLIC_MODULE
_read_record_path.__module__ = _PUBLIC_MODULE
_record_age.__module__ = _PUBLIC_MODULE
_reclaim_stale_lock.__module__ = _PUBLIC_MODULE
claim_landing_lock.__module__ = _PUBLIC_MODULE
claim_gate_marker.__module__ = _PUBLIC_MODULE
_invalidate_evidence.__module__ = _PUBLIC_MODULE
register_gate.__module__ = _PUBLIC_MODULE
active_gate_records.__module__ = _PUBLIC_MODULE
