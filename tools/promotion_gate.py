#!/usr/bin/env python3
"""Run promotion checks under a shared lock and land verified commits safely."""

from __future__ import annotations

import argparse
import errno
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Sequence, TextIO


LOCK_NAME = "ankiscape-promotion-gate.lock"
PROGRESS_LINE = re.compile(r"^[.sEF]+$")


class GateError(RuntimeError):
    """A promotion gate or landing precondition failed."""


@dataclass(frozen=True)
class LockRecord:
    pid: int
    operation: str
    worktree: str
    commit: str
    started_at: str
    token: str

    @classmethod
    def from_json(cls, text: str) -> "LockRecord":
        try:
            payload = json.loads(text)
            return cls(
                pid=int(payload["pid"]),
                operation=str(payload["operation"]),
                worktree=str(payload["worktree"]),
                commit=str(payload["commit"]),
                started_at=str(payload["started_at"]),
                token=str(payload["token"]),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise GateError(f"Promotion lock is unreadable: {exc}") from exc


def _git(
    repo: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ("git", "-C", str(repo), *args),
        check=False,
        text=True,
        capture_output=True,
    )
    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise GateError(detail or f"git {' '.join(args)} failed with exit {completed.returncode}")
    return completed


def commit_at(worktree: Path) -> str:
    return _git(worktree, "rev-parse", "HEAD").stdout.strip()


def git_common_dir(repo: Path) -> Path:
    raw = _git(repo, "rev-parse", "--git-common-dir").stdout.strip()
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (repo / path).resolve()


def lock_path_for(repo: Path) -> Path:
    return git_common_dir(repo) / LOCK_NAME


def process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError as exc:
        return exc.errno != errno.ESRCH
    return True


def _read_lock(lock_path: Path) -> LockRecord | None:
    try:
        return LockRecord.from_json(lock_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise GateError(f"Cannot read promotion lock {lock_path}: {exc}") from exc
    except GateError as exc:
        raise GateError(f"{exc} at {lock_path}; inspect it before proceeding") from exc


def active_lock(lock_path: Path, *, stderr: TextIO = sys.stderr) -> LockRecord | None:
    record = _read_lock(lock_path)
    if record is None:
        return None
    if process_is_alive(record.pid):
        return record

    print(
        "Stale promotion gate lock: "
        f"PID {record.pid} is gone; it recorded {record.operation} for {record.commit} "
        f"in {record.worktree} since {record.started_at}. Removing {lock_path}.",
        file=stderr,
    )
    try:
        lock_path.unlink(missing_ok=True)
    except OSError as exc:
        raise GateError(f"Cannot remove stale promotion lock {lock_path}: {exc}") from exc
    return None


def _new_lock_record(operation: str, worktree: Path, commit: str) -> LockRecord:
    return LockRecord(
        pid=os.getpid(),
        operation=operation,
        worktree=str(worktree.resolve()),
        commit=commit,
        started_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        token=uuid.uuid4().hex,
    )


def _create_lock(lock_path: Path, record: LockRecord) -> None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=lock_path.parent,
            prefix=f".{LOCK_NAME}.",
            delete=False,
        ) as temporary:
            json.dump(asdict(record), temporary, sort_keys=True)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        os.link(temporary_path, lock_path)
    except FileExistsError:
        raise GateError("promotion lock was claimed by another process") from None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def claim_lock(
    repo: Path,
    *,
    operation: str,
    worktree: Path,
    commit: str,
    stderr: TextIO = sys.stderr,
) -> tuple[Path, LockRecord]:
    lock_path = lock_path_for(repo)
    for _ in range(2):
        existing = active_lock(lock_path, stderr=stderr)
        if existing is not None:
            raise GateError(
                f"Promotion lock held by PID {existing.pid}: {existing.operation} for "
                f"{existing.commit} in {existing.worktree} since {existing.started_at}"
            )
        record = _new_lock_record(operation, worktree, commit)
        try:
            _create_lock(lock_path, record)
        except GateError:
            continue
        return lock_path, record
    existing = active_lock(lock_path, stderr=stderr)
    if existing is not None:
        raise GateError(
            f"Promotion lock held by PID {existing.pid}: {existing.operation} for "
            f"{existing.commit} in {existing.worktree} since {existing.started_at}"
        )
    raise GateError(f"Could not claim promotion lock {lock_path}")


def release_lock(lock_path: Path, record: LockRecord) -> None:
    current = _read_lock(lock_path)
    if current is not None and current.token == record.token:
        lock_path.unlink(missing_ok=True)


def _worktree_rows(repo: Path) -> tuple[dict[str, str], ...]:
    result = _git(repo, "worktree", "list", "--porcelain")
    rows: list[dict[str, str]] = []
    row: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if not line:
            if row:
                rows.append(row)
                row = {}
            continue
        key, _, value = line.partition(" ")
        row[key] = value
    if row:
        rows.append(row)
    return tuple(rows)


def main_worktree(repo: Path) -> Path:
    for row in _worktree_rows(repo):
        if row.get("branch") == "refs/heads/main":
            return Path(row["worktree"]).resolve()
    raise GateError("Landing refused: refs/heads/main is not checked out in a worktree")


def safe_log_root(repo: Path) -> Path:
    rows = _worktree_rows(repo)
    if not rows:
        raise GateError("git reported no worktrees")
    canonical = Path(rows[0]["worktree"]).resolve()
    return canonical.parent.parent / "ankiscape_worktrees"


def _tail_without_progress(lines: list[str], count: int) -> list[str]:
    return [line for line in lines if not PROGRESS_LINE.fullmatch(line)][-count:]


def _run_check(
    log: TextIO,
    *,
    heading: str,
    command: Sequence[str],
    worktree: Path,
    selector: Callable[[list[str]], list[str]],
    environment: dict[str, str] | None = None,
    accept_selected_output_on_failure: bool = False,
) -> int:
    print(heading, file=log)
    try:
        completed = subprocess.run(
            command,
            cwd=worktree,
            check=False,
            text=True,
            capture_output=True,
            env={**os.environ, **environment} if environment else None,
        )
        combined = completed.stdout + completed.stderr
        selected = selector(combined.splitlines())
        for line in selected:
            print(line, file=log)
        accepted = completed.returncode == 0 or (
            accept_selected_output_on_failure and bool(selected)
        )
        if not accepted:
            print(f"FAILED: exit {completed.returncode}", file=log)
        log.flush()
        return 0 if accepted else completed.returncode
    except OSError as exc:
        print(f"FAILED: {exc}", file=log)
        log.flush()
        return 127


def _run_gate_checks(worktree: Path, *, plain_only: bool, log: TextIO) -> tuple[str, ...]:
    canonical = main_worktree(worktree)
    checks: list[
        tuple[str, str, Sequence[str], Callable[[list[str]], list[str]], dict[str, str] | None]
    ] = [
        (
            "plain lane",
            "=== PLAIN LANE ===",
            ("/opt/homebrew/bin/python3", "run_tests.py"),
            lambda lines: _tail_without_progress(lines, 20 if plain_only else 30),
            None,
        ),
    ]
    if not plain_only:
        checks.append((
            "Qt lane",
            "=== QT LANE (monolithic) ===",
            (
                str(canonical / ".venv-qt" / "bin" / "python"),
                "-m",
                "unittest",
                "discover",
                "tests",
            ),
            lambda lines: _tail_without_progress(lines, 30),
            {"QT_QPA_PLATFORM": "offscreen"},
        ))
    checks.extend((
        (
            "audit_docs",
            "=== audit_docs ===",
            ("python3", "tools/audit_docs.py"),
            lambda lines: lines[-3:],
            None,
        ),
        (
            "audit_test_quality",
            "=== audit_test_quality ===",
            ("python3", "tools/audit_test_quality.py"),
            lambda lines: lines[:3],
            None,
        ),
        (
            "reachability",
            "=== reachability ===",
            ("python3", "tools/audit_item_reachability.py"),
            lambda lines: [line for line in lines if "actions;" in line][-1:],
            None,
        ),
        (
            "worktree_guard",
            "=== worktree_guard ===",
            ("python3", "tools/worktree_guard.py", "audit"),
            lambda lines: lines[-2:],
            None,
        ),
        (
            "diff check",
            "=== diff check ===",
            ("git", "diff", "--check"),
            lambda lines: lines or ["clean"],
            None,
        ),
    ))

    failures: list[str] = []
    for label, heading, command, selector, environment in checks:
        returncode = _run_check(
            log,
            heading=heading,
            command=command,
            worktree=worktree,
            selector=selector,
            environment=environment,
            accept_selected_output_on_failure=label == "reachability",
        )
        if returncode != 0:
            failures.append(f"{label} (exit {returncode})")
    return tuple(failures)


def run_gate(
    worktree: Path,
    *,
    plain_only: bool,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> Path:
    worktree = worktree.resolve()
    commit = commit_at(worktree)
    lock_path, record = claim_lock(
        worktree,
        operation="gate",
        worktree=worktree,
        commit=commit,
        stderr=stderr,
    )
    failures: tuple[str, ...] = ()
    try:
        prefix = "gateplain" if plain_only else "gate"
        short_commit = _git(worktree, "rev-parse", "--short", "HEAD").stdout.strip()
        log_path = safe_log_root(worktree) / f"{prefix}-{short_commit}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8") as log:
            kind = "plain-lane gate" if plain_only else "gate"
            print(f"=== {kind} for {commit} in {worktree} ===", file=log)
            print(datetime.now().astimezone().ctime(), file=log)
            failures = _run_gate_checks(worktree, plain_only=plain_only, log=log)
            ending_commit = commit_at(worktree)
            if ending_commit != commit:
                failures = (*failures, f"HEAD moved from {commit} to {ending_commit}")
                print(f"FAILED: HEAD moved from {commit} to {ending_commit}", file=log)
            print("=== GATE DONE ===", file=log)
            print(datetime.now().astimezone().ctime(), file=log)
    finally:
        release_lock(lock_path, record)

    print(log_path, file=stdout)
    if failures:
        raise GateError(f"Gate failed: {', '.join(failures)}. Log: {log_path}")
    return log_path


def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    return _git(
        repo,
        "merge-base",
        "--is-ancestor",
        ancestor,
        descendant,
        check=False,
    ).returncode == 0


def land(
    worktree: Path,
    *,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> str:
    worktree = worktree.resolve()
    target_commit = commit_at(worktree)
    lock_path = lock_path_for(worktree)
    existing = active_lock(lock_path, stderr=stderr)
    own_lock: LockRecord | None = None
    same_tree = (
        existing is not None
        and existing.commit == target_commit
        and Path(existing.worktree).resolve() == worktree
    )
    if existing is not None and not same_tree:
        operation = "gate" if existing.operation == "gate" else "landing"
        raise GateError(
            f"Landing refused: running {operation} PID {existing.pid} has held "
            f"{existing.commit} in {existing.worktree} since {existing.started_at}; requested "
            f"{target_commit} in {worktree} is a different tree"
        )
    if existing is not None and existing.operation != "gate":
        raise GateError(
            f"Landing refused: PID {existing.pid} is already landing {existing.commit} "
            f"from {existing.worktree} since {existing.started_at}"
        )
    if existing is None:
        lock_path, own_lock = claim_lock(
            worktree,
            operation="land",
            worktree=worktree,
            commit=target_commit,
            stderr=stderr,
        )

    try:
        main_path = main_worktree(worktree)
        main_commit = _git(main_path, "rev-parse", "refs/heads/main").stdout.strip()
        if not is_ancestor(worktree, main_commit, target_commit):
            raise GateError(
                f"Landing refused: {target_commit} in {worktree} is not a descendant "
                f"of current main {main_commit}"
            )

        merge = _git(
            main_path,
            "merge",
            "--ff-only",
            target_commit,
            check=False,
        )
        if merge.returncode != 0:
            current_main = _git(main_path, "rev-parse", "refs/heads/main").stdout.strip()
            if not is_ancestor(worktree, current_main, target_commit):
                raise GateError(
                    f"Landing refused: {target_commit} is no longer a descendant of current main "
                    f"{current_main}; main moved during landing"
                )
            detail = (merge.stderr or merge.stdout).strip()
            raise GateError(f"Landing failed for {target_commit}: {detail}")
        if merge.stdout:
            print(merge.stdout.rstrip(), file=stdout)
        print(f"Landed {target_commit} from {worktree} onto main in {main_path}", file=stdout)
        return target_commit
    finally:
        if own_lock is not None:
            release_lock(lock_path, own_lock)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="run the promotion gate")
    run_parser.add_argument("worktree", type=Path)
    run_parser.add_argument(
        "--plain-only",
        action="store_true",
        help="skip the offscreen Qt lane for a branch-side promotion check",
    )
    land_parser = subparsers.add_parser("land", help="fast-forward main to a gated worktree")
    land_parser.add_argument("worktree", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.command == "run":
            run_gate(args.worktree, plain_only=args.plain_only)
        else:
            land(args.worktree)
    except (GateError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
