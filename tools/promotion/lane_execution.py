"""Bounded promotion lanes, audits, and gate evidence."""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import TextIO

from .contract import (
    FULL_GATE_CHECKS,
    PLAIN_GATE_CHECKS,
    PLAIN_LANE_TIMEOUT,
    QT_LANE_TIMEOUT,
    GateError,
    GateEvidence,
)
from .locking import HeldLock, claim_landing_lock, register_gate
from .promotion_process import kill_process_tree
from .repository import commit_at, evidence_path_for, main_worktree, safe_log_root, _git


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


ResultValidator = Callable[[int, list[str]], bool]


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
    landing_lock = claim_landing_lock(
        worktree,
        operation="running a gate",
        worktree=worktree,
        commit="HEAD (resolving)",
    )
    gate_marker: HeldLock | None = None
    passed_checks: tuple[str, ...] = ()
    failures: tuple[str, ...] = ()
    try:
        worktree = worktree.resolve()
        commit = commit_at(worktree)
        landing_lock.update_target(worktree, commit)
        canonical = main_worktree(worktree)
        canonical_changes = _git(
            canonical, "status", "--porcelain", "--untracked-files=no"
        ).stdout.splitlines()
        if canonical_changes:
            raise GateError(
                "Gate refused: canonical checkout has uncommitted "
                "tracked changes:\n"
                + "\n".join(canonical_changes)
            )
        gate_marker = register_gate(
            worktree,
            commit,
            stderr=stderr,
            coordination=landing_lock,
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
        if gate_marker is not None:
            gate_marker.release()
        landing_lock.release()

    print(log_path, file=stdout)
    if failures:
        raise GateError(f"Gate failed: {', '.join(failures)}. Log: {log_path}")
    return log_path


_PUBLIC_MODULE = f"{__package__.rsplit('.', 1)[0]}.promotion_gate"
_tail_without_progress.__module__ = _PUBLIC_MODULE
_run_bounded.__module__ = _PUBLIC_MODULE
_run_check.__module__ = _PUBLIC_MODULE
_worktree_is_clean.__module__ = _PUBLIC_MODULE
_read_reachability_pins.__module__ = _PUBLIC_MODULE
_read_reachability_report.__module__ = _PUBLIC_MODULE
_reachability_log_lines.__module__ = _PUBLIC_MODULE
_reachability_result_matches_pins.__module__ = _PUBLIC_MODULE
_run_reachability_check.__module__ = _PUBLIC_MODULE
_run_gate_checks.__module__ = _PUBLIC_MODULE
_write_evidence.__module__ = _PUBLIC_MODULE
run_gate.__module__ = _PUBLIC_MODULE
