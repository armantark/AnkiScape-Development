#!/usr/bin/env python3
"""Run promotion checks and land only the exact commit that passed them."""

from __future__ import annotations

import argparse
import ast
import fcntl
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
from typing import Callable, IO, Sequence, TextIO

try:
    from tools.promotion.promotion_process import format_age, kill_process_tree, pid_is_alive
except ModuleNotFoundError:  # direct execution from tools/
    from promotion.promotion_process import format_age, kill_process_tree, pid_is_alive


LAND_LOCK_NAME = "ankiscape-promotion-land.lock"
ACTIVE_GATE_DIR_NAME = "ankiscape-promotion-gates"
EVIDENCE_DIR_NAME = "ankiscape-promotion-evidence"
PROGRESS_LINE = re.compile(r"^[.sEF]+$")
REACHABILITY_PIN_FIELDS = (
    "action_count",
    "reachable_item_count",
    "orphan_input_count",
    "root_orphan_count",
    "cascade_orphan_count",
    "unresolved_action_count",
    "seed_item_count",
)
REACHABILITY_PIN_METHOD = "test_report_matches_player_finishable_quest_baseline"
PLAIN_GATE_CHECKS = (
    "plain lane",
    "audit_docs",
    "audit_test_quality",
    "reachability",
    "worktree_guard",
    "worktree clean",
    "diff check",
)
FULL_GATE_CHECKS = ("plain lane", "Qt lane", *PLAIN_GATE_CHECKS[1:])
PLAIN_LANE_TIMEOUT = 1000.0
QT_LANE_TIMEOUT = 1300.0
LONGEST_LANE_TIMEOUT = max(PLAIN_LANE_TIMEOUT, QT_LANE_TIMEOUT)


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
    heartbeat_at: str = ""

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
                heartbeat_at=str(payload.get("heartbeat_at", payload["started_at"])),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise GateError(f"Promotion lock is unreadable: {exc}") from exc


@dataclass(frozen=True)
class GateEvidence:
    schema_version: int
    commit: str
    worktree: str
    plain_only: bool
    remote_lanes: bool
    passed_checks: tuple[str, ...]
    completed_at: str

    @classmethod
    def from_json(cls, text: str) -> "GateEvidence":
        try:
            payload = json.loads(text)
            passed_checks = payload["passed_checks"]
            if not isinstance(passed_checks, list) or not all(
                isinstance(label, str) for label in passed_checks
            ):
                raise TypeError("passed_checks must be a list of strings")
            plain_only = payload["plain_only"]
            if not isinstance(plain_only, bool):
                raise TypeError("plain_only must be a boolean")
            remote_lanes = payload.get("remote_lanes", False)
            if not isinstance(remote_lanes, bool):
                raise TypeError("remote_lanes must be a boolean")
            return cls(
                schema_version=int(payload["schema_version"]),
                commit=str(payload["commit"]),
                worktree=str(payload["worktree"]),
                plain_only=plain_only,
                remote_lanes=remote_lanes,
                passed_checks=tuple(passed_checks),
                completed_at=str(payload["completed_at"]),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise GateError(f"Promotion evidence is unreadable: {exc}") from exc


@dataclass
class HeldLock:
    path: Path
    stream: IO[str]
    unlink_on_release: bool
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

    def release(self) -> None:
        if self.stream.closed:
            return
        if self.unlink_on_release:
            self.path.unlink(missing_ok=True)
        self.stream.close()


ResultValidator = Callable[[int, list[str]], bool]


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


def landing_lock_path_for(repo: Path) -> Path:
    return git_common_dir(repo) / LAND_LOCK_NAME


def active_gate_dir_for(repo: Path) -> Path:
    return git_common_dir(repo) / ACTIVE_GATE_DIR_NAME


def evidence_path_for(repo: Path, commit: str) -> Path:
    return git_common_dir(repo) / EVIDENCE_DIR_NAME / f"{commit}.json"


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
) -> HeldLock:
    path = landing_lock_path_for(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = path.open("a+", encoding="utf-8")
    try:
        flags = fcntl.LOCK_EX if wait else fcntl.LOCK_EX | fcntl.LOCK_NB
        fcntl.flock(stream.fileno(), flags)
    except BlockingIOError:
        stream.close()
        try:
            existing = _read_record_path(path)
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
    return HeldLock(path, stream, unlink_on_release=False, record=record)


def claim_gate_marker(worktree: Path, commit: str) -> HeldLock:
    directory = active_gate_dir_for(worktree)
    directory.mkdir(parents=True, exist_ok=True)
    record = _new_lock_record("gate", worktree, commit)
    path = directory / f"{record.token}.json"
    stream = path.open("x+", encoding="utf-8")
    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    _write_record(stream, record)
    return HeldLock(path, stream, unlink_on_release=True, record=record)


def _invalidate_evidence(repo: Path, commit: str) -> None:
    evidence_path_for(repo, commit).unlink(missing_ok=True)


def register_gate(
    worktree: Path,
    commit: str,
    *,
    stderr: TextIO = sys.stderr,
) -> HeldLock:
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
        coordination.release()


def install_hook(repo: Path) -> Path:
    repo = repo.resolve()
    raw_git_dir = Path(_git(repo, "rev-parse", "--git-dir").stdout.strip())
    git_dir = (raw_git_dir if raw_git_dir.is_absolute() else repo / raw_git_dir).resolve()
    hook_path = git_dir / "hooks" / "pre-commit"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    source = """#!/bin/sh
exec python3 -m tools.promotion.landing_freeze_hook \"$@\"
"""
    hook_path.write_text(source, encoding="utf-8")
    hook_path.chmod(0o755)
    return hook_path


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


def _run_bounded(
    command: Sequence[str],
    *,
    worktree: Path,
    environment: dict[str, str] | None,
    timeout: float | None,
) -> tuple[subprocess.CompletedProcess[str], bool]:
    options = dict(
        cwd=worktree,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, **environment} if environment else None,
    )
    try:
        process = subprocess.Popen(command, **options, start_new_session=True)
    except PermissionError:
        process = subprocess.Popen(command, **options)
    try:
        stdout_text, stderr_text = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        kill_process_tree(process.pid, process_group=True)
        stdout_text, stderr_text = process.communicate()
        stdout_text = stdout_text or exc.stdout or ""
        stderr_text = stderr_text or exc.stderr or ""
        return subprocess.CompletedProcess(command, 124, stdout_text, stderr_text), True
    return subprocess.CompletedProcess(command, process.returncode, stdout_text, stderr_text), False


def _run_check(
    log: TextIO,
    *,
    heading: str,
    command: Sequence[str],
    worktree: Path,
    selector: Callable[[list[str]], list[str]],
    environment: dict[str, str] | None = None,
    validator: ResultValidator | None = None,
    parse_stdout_only: bool = False,
    timeout: float | None = None,
) -> int:
    print(heading, file=log)
    try:
        completed, timed_out = _run_bounded(
            command,
            worktree=worktree,
            environment=environment,
            timeout=timeout,
        )
        stderr_lines = completed.stderr.splitlines()
        lines = (
            completed.stdout.splitlines()
            if parse_stdout_only
            else (completed.stdout + completed.stderr).splitlines()
        )
        selected = selector(lines)
        for line in selected:
            print(line, file=log)
        if parse_stdout_only:
            for line in stderr_lines:
                print(line, file=log)
        if timed_out:
            print(f"TIMEOUT: exceeded {timeout:g} seconds", file=log)
            print("FAILED: exit 124 (TIMEOUT)", file=log)
            log.flush()
            return 124
        accepted = (
            validator(completed.returncode, lines)
            if validator is not None
            else completed.returncode == 0
        )
        if not accepted:
            print(f"FAILED: exit {completed.returncode}", file=log)
        log.flush()
        return 0 if accepted else completed.returncode or 1
    except OSError as exc:
        print(f"FAILED: {exc}", file=log)
        log.flush()
        return 127


def _worktree_is_clean(returncode: int, lines: list[str]) -> bool:
    return returncode == 0 and not lines


def _read_reachability_pins(worktree: Path) -> dict[str, int]:
    path = worktree / "tests" / "test_item_reachability_audit.py"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        raise GateError(f"Cannot read reachability pins from {path}: {exc}") from exc

    methods = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == REACHABILITY_PIN_METHOD
    ]
    if len(methods) != 1:
        raise GateError(
            f"Expected one {REACHABILITY_PIN_METHOD} method in {path}; found {len(methods)}"
        )

    pins: dict[str, int] = {}
    for node in ast.walk(methods[0]):
        if (
            not isinstance(node, ast.Call)
            or not isinstance(node.func, ast.Attribute)
            or node.func.attr != "assertEqual"
            or len(node.args) < 2
        ):
            continue
        actual, expected = node.args[:2]
        if (
            not isinstance(actual, ast.Subscript)
            or not isinstance(actual.value, ast.Name)
            or actual.value.id != "report"
            or not isinstance(actual.slice, ast.Constant)
            or actual.slice.value not in REACHABILITY_PIN_FIELDS
            or not isinstance(expected, ast.Constant)
            or type(expected.value) is not int
        ):
            continue
        field = str(actual.slice.value)
        if field in pins:
            raise GateError(f"Reachability pin {field!r} appears more than once in {path}")
        pins[field] = expected.value

    missing = [field for field in REACHABILITY_PIN_FIELDS if field not in pins]
    if missing:
        raise GateError(f"Reachability pins missing from {path}: {', '.join(missing)}")
    return pins


def _read_reachability_report(lines: list[str]) -> dict[str, object] | None:
    try:
        report = json.loads("\n".join(lines))
    except (TypeError, json.JSONDecodeError):
        return None
    return report if isinstance(report, dict) else None


def _reachability_log_lines(lines: list[str]) -> list[str]:
    report = _read_reachability_report(lines)
    if report is None:
        return _tail_without_progress(lines, 5)
    summary_fields = (
        "action_count",
        "reachable_item_count",
        "orphan_input_count",
        "unresolved_action_count",
    )
    if any(type(report.get(field)) is not int for field in summary_fields):
        return _tail_without_progress(lines, 5)
    return [
        f"{report['action_count']} actions; {report['reachable_item_count']} reachable items; "
        f"{report['orphan_input_count']} orphan inputs; "
        f"{report['unresolved_action_count']} blocked actions"
    ]


def _reachability_result_matches_pins(
    returncode: int,
    lines: list[str],
    pins: dict[str, int],
) -> bool:
    report = _read_reachability_report(lines)
    expected_returncode = 1 if pins["orphan_input_count"] else 0
    return (
        returncode == expected_returncode
        and report is not None
        and all(
            type(report.get(field)) is int and report[field] == pins[field]
            for field in REACHABILITY_PIN_FIELDS
        )
    )


def _run_reachability_check(log: TextIO, worktree: Path) -> int:
    try:
        pins = _read_reachability_pins(worktree)
    except GateError as exc:
        print("=== reachability ===", file=log)
        print(f"FAILED: {exc}", file=log)
        log.flush()
        return 1
    return _run_check(
        log,
        heading="=== reachability ===",
        command=("python3", "tools/audit_item_reachability.py", "--json"),
        worktree=worktree,
        selector=_reachability_log_lines,
        validator=lambda returncode, lines: _reachability_result_matches_pins(
            returncode,
            lines,
            pins,
        ),
        parse_stdout_only=True,
    )


def _run_gate_checks(
    worktree: Path,
    *,
    plain_only: bool,
    remote_lanes: bool = False,
    log: TextIO,
    heartbeat: Callable[[], None] = lambda: None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if remote_lanes:
        remote_runner = (
            "/opt/homebrew/bin/python3",
            "tools/run_remote_tests.py",
            str(worktree.resolve()),
        )
        plain_command = (*remote_runner, "plain")
        qt_command = (*remote_runner, "qt")
        qt_environment = None
    else:
        canonical = main_worktree(worktree)
        plain_command = ("/opt/homebrew/bin/python3", "run_tests.py")
        qt_command = (
            str(canonical / ".venv-qt" / "bin" / "python"),
            "run_tests.py",
        )
        qt_environment = {"QT_QPA_PLATFORM": "offscreen"}
    checks: list[
        tuple[
            str,
            str,
            Sequence[str],
            Callable[[list[str]], list[str]],
            dict[str, str] | None,
            ResultValidator | None,
            float | None,
        ]
    ] = [
        (
            "plain lane",
            "=== PLAIN LANE ===",
            plain_command,
            lambda lines: _tail_without_progress(lines, 20 if plain_only else 30),
            None,
            None,
            PLAIN_LANE_TIMEOUT,
        ),
    ]
    if not plain_only:
        checks.append((
            "Qt lane",
            "=== QT LANE (monolithic) ===",
            qt_command,
            lambda lines: _tail_without_progress(lines, 30),
            qt_environment,
            None,
            QT_LANE_TIMEOUT,
        ))
    checks.extend((
        (
            "audit_docs",
            "=== audit_docs ===",
            ("python3", "tools/audit_docs.py"),
            lambda lines: lines[-3:],
            None,
            None,
            None,
        ),
        (
            "audit_test_quality",
            "=== audit_test_quality ===",
            ("python3", "tools/audit_test_quality.py"),
            lambda lines: lines[:3],
            None,
            None,
            None,
        ),
        (
            "worktree_guard",
            "=== worktree_guard ===",
            ("python3", "tools/worktree_guard.py", "audit"),
            lambda lines: lines[-2:],
            None,
            None,
            None,
        ),
        (
            "worktree clean",
            "=== worktree clean ===",
            ("git", "status", "--porcelain", "--untracked-files=all"),
            lambda lines: lines or ["clean"],
            None,
            _worktree_is_clean,
            None,
        ),
        (
            "diff check",
            "=== diff check ===",
            ("git", "diff", "--check"),
            lambda lines: lines or ["clean"],
            None,
            None,
            None,
        ),
    ))

    passed: list[str] = []
    failures: list[str] = []
    for label, heading, command, selector, environment, validator, timeout in checks:
        heartbeat()
        returncode = _run_check(
            log,
            heading=heading,
            command=command,
            worktree=worktree,
            selector=selector,
            environment=environment,
            validator=validator,
            timeout=timeout,
        )
        if returncode == 0:
            passed.append(label)
        else:
            failures.append(f"{label} (exit {returncode})")
        if label == "audit_test_quality":
            returncode = _run_reachability_check(log, worktree)
            if returncode == 0:
                passed.append("reachability")
            else:
                failures.append(f"reachability (exit {returncode})")
    return tuple(passed), tuple(failures)


def _write_evidence(
    worktree: Path,
    *,
    commit: str,
    plain_only: bool,
    remote_lanes: bool,
    passed_checks: tuple[str, ...],
) -> Path:
    evidence = GateEvidence(
        schema_version=1,
        commit=commit,
        worktree=str(worktree.resolve()),
        plain_only=plain_only,
        remote_lanes=remote_lanes,
        passed_checks=passed_checks,
        completed_at=datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    path = evidence_path_for(worktree, commit)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{commit}.",
            delete=False,
        ) as temporary:
            json.dump(asdict(evidence), temporary, sort_keys=True)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
        return path
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def run_gate(
    worktree: Path,
    *,
    plain_only: bool,
    remote_lanes: bool = False,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> Path:
    worktree = worktree.resolve()
    commit = commit_at(worktree)
    gate_marker = register_gate(worktree, commit, stderr=stderr)
    landing_lock: HeldLock | None = None
    passed_checks: tuple[str, ...] = ()
    failures: tuple[str, ...] = ()
    try:
        landing_lock = claim_landing_lock(
            worktree,
            operation="running a gate",
            worktree=worktree,
            commit=commit,
        )
        prefix = "gateplain" if plain_only else "gate"
        short_commit = _git(worktree, "rev-parse", "--short", "HEAD").stdout.strip()
        log_path = safe_log_root(worktree) / f"{prefix}-{short_commit}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8") as log:
            kind = "plain-lane gate" if plain_only else "gate"
            print(f"=== {kind} for {commit} in {worktree} ===", file=log)
            print(datetime.now().astimezone().ctime(), file=log)
            passed_checks, failures = _run_gate_checks(
                worktree,
                plain_only=plain_only,
                remote_lanes=remote_lanes,
                log=log,
                heartbeat=gate_marker.refresh,
            )
            ending_commit = commit_at(worktree)
            if ending_commit != commit:
                failures = (*failures, f"HEAD moved from {commit} to {ending_commit}")
                print(f"FAILED: HEAD moved from {commit} to {ending_commit}", file=log)
            print("=== GATE DONE ===", file=log)
            print(datetime.now().astimezone().ctime(), file=log)
        if not failures:
            expected_checks = PLAIN_GATE_CHECKS if plain_only else FULL_GATE_CHECKS
            if passed_checks != expected_checks:
                raise GateError(
                    f"Gate result is incomplete: passed {passed_checks}; expected {expected_checks}"
                )
            _write_evidence(
                worktree,
                commit=commit,
                plain_only=plain_only,
                remote_lanes=remote_lanes,
                passed_checks=passed_checks,
            )
    finally:
        gate_marker.release()
        if landing_lock is not None:
            landing_lock.release()

    print(log_path, file=stdout)
    if failures:
        raise GateError(f"Gate failed: {', '.join(failures)}. Log: {log_path}")
    return log_path


def _load_landing_evidence(worktree: Path, commit: str) -> GateEvidence:
    path = evidence_path_for(worktree, commit)
    try:
        evidence = GateEvidence.from_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise GateError(
            f"Landing refused: no passed full-gate evidence for exact commit {commit} at {path}"
        ) from None
    except OSError as exc:
        raise GateError(f"Landing refused: cannot read gate evidence {path}: {exc}") from exc
    except GateError as exc:
        raise GateError(f"Landing refused: {exc} at {path}") from exc

    if evidence.schema_version != 1:
        raise GateError(
            f"Landing refused: unsupported gate evidence schema {evidence.schema_version} at {path}"
        )
    if evidence.commit != commit:
        raise GateError(
            f"Landing refused: gate evidence at {path} names {evidence.commit}, not {commit}"
        )
    if evidence.plain_only or evidence.passed_checks != FULL_GATE_CHECKS:
        raise GateError(
            f"Landing refused: evidence for {commit} did not pass every full-gate check; "
            f"recorded {evidence.passed_checks}"
        )
    return evidence


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
    landing_lock = claim_landing_lock(
        worktree,
        operation="landing",
        worktree=worktree,
        commit=target_commit,
    )
    try:
        active_gates = active_gate_records(worktree, stderr=stderr)
        for gate in active_gates:
            if gate.commit != target_commit:
                raise GateError(
                    f"Landing refused: running gate PID {gate.pid} has held {gate.commit} in "
                    f"{gate.worktree} since {gate.started_at}; requested {target_commit} in "
                    f"{worktree} is a different tree"
                )
        if active_gates:
            gate = active_gates[0]
            raise GateError(
                f"Landing refused: gate PID {gate.pid} is still running for exact commit "
                f"{target_commit} in {gate.worktree} since {gate.started_at}"
            )

        _load_landing_evidence(worktree, target_commit)
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
        landing_lock.release()


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
    run_parser.add_argument(
        "--remote-lanes",
        action="store_true",
        help="run the plain and Qt lanes through the MacBook remote test host",
    )
    subparsers.add_parser("install-hook", help="install the repo-local landing freeze hook")
    land_parser = subparsers.add_parser("land", help="fast-forward main to a gated worktree")
    land_parser.add_argument("worktree", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.command == "run":
            run_gate(
                args.worktree,
                plain_only=args.plain_only,
                remote_lanes=args.remote_lanes,
            )
        elif args.command == "land":
            land(args.worktree)
        else:
            print(install_hook(Path.cwd()))
    except (GateError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
