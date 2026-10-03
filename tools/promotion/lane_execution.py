"""Bounded promotion lanes, audits, and gate evidence."""

from __future__ import annotations

import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Callable, Iterator, Sequence
from concurrent.futures import Future
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import TextIO

from .contract import (
    FULL_GATE_CHECKS,
    PLAIN_GATE_CHECKS,
    PLAIN_LANE_TIMEOUT,
    QT_LANE_TIMEOUT,
    REMOTE_MIRROR_LOCK_TIMEOUT,
    GateError,
    GateEvidence,
)
from .locking import HeldLock, claim_landing_lock, register_gate
from .promotion_process import kill_process_tree
from .repository import commit_at, evidence_path_for, main_worktree, safe_log_root, _git
from .snapshot import commit_snapshot

if __package__ == "promotion":  # direct execution from tools/
    from reachability.pins import REACHABILITY_PIN_FIELDS, read_reachability_pins
else:
    from ..reachability.pins import REACHABILITY_PIN_FIELDS, read_reachability_pins

if __package__ == "tools.promotion":
    from .. import run_remote_tests
else:  # direct execution from tools/
    import run_remote_tests


PROGRESS_LINE = re.compile(r"^[.sEF]+$")


ResultValidator = Callable[[int, list[str]], bool]


GateCheck = tuple[
    str,
    str,
    Sequence[str],
    Callable[[list[str]], list[str]],
    dict[str, str] | None,
    ResultValidator | None,
    float | None,
]


def _tail_without_progress(lines: list[str], count: int | None = None) -> list[str]:
    filtered = [line for line in lines if not PROGRESS_LINE.fullmatch(line)]
    return filtered[-count:] if count is not None else filtered


def _run_bounded(
    command: Sequence[str],
    *,
    worktree: Path,
    environment: dict[str, str] | None,
    timeout: float | None,
    pass_fds: Sequence[int] = (),
) -> tuple[subprocess.CompletedProcess[str], bool]:
    options = dict(
        cwd=worktree,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, **environment} if environment else None,
        pass_fds=pass_fds,
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
    pass_fds: Sequence[int] = (),
) -> int:
    print(heading, file=log)
    try:
        completed, timed_out = _run_bounded(
            command,
            worktree=worktree,
            environment=environment,
            timeout=timeout,
            pass_fds=pass_fds,
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
    return (
        returncode == 0
        and report is not None
        and all(
            type(report.get(field)) is int and report[field] == pins[field]
            for field in REACHABILITY_PIN_FIELDS
        )
    )


def _run_reachability_check(log: TextIO, worktree: Path) -> int:
    try:
        pins = read_reachability_pins(worktree)
    except ValueError as exc:
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


def _run_papercut_check(log: TextIO, worktree: Path) -> int:
    # The snapshot clones the source repository, so origin/main is the main a landing
    # must descend from. Its merge base with the gated commit is that main for any tree
    # that can land, and for one that has not merged main yet it keeps main's later
    # papercuts from reading as this tree's losses.
    base = _git(worktree, "merge-base", "HEAD", "refs/remotes/origin/main", check=False)
    if base.returncode != 0:
        print("=== papercuts ===", file=log)
        print(f"FAILED: no merge base with main: {base.stderr.strip()}", file=log)
        log.flush()
        return 1
    return _run_check(
        log,
        heading="=== papercuts ===",
        command=("python3", "tools/memory_bank/move_papercuts.py", "check", base.stdout.strip()),
        worktree=worktree,
        selector=lambda lines: lines,
    )


def _wait_for_remote_mirror(lock: TextIO, started: float, heartbeat: Callable[[], None]) -> bool:
    if time.monotonic() - started >= REMOTE_MIRROR_LOCK_TIMEOUT:
        return False
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except BlockingIOError:
        pass

    completed: Future[None] = Future()
    descriptor = os.dup(lock.fileno())

    def acquire() -> None:
        try:
            # The duplicate shares the gate's lock description. If the gate times out
            # and closes its copy, a late acquisition releases when this copy closes.
            with os.fdopen(descriptor) as pending:
                fcntl.flock(pending.fileno(), fcntl.LOCK_EX)
        except OSError as exc:
            completed.set_exception(exc)
        else:
            completed.set_result(None)

    threading.Thread(target=acquire, daemon=True).start()
    while not completed.done():
        remaining = REMOTE_MIRROR_LOCK_TIMEOUT - (time.monotonic() - started)
        if remaining <= 0:
            return False
        heartbeat()
        time.sleep(min(1.0, remaining))
    completed.result()
    return time.monotonic() - started < REMOTE_MIRROR_LOCK_TIMEOUT


@contextmanager
def _hold_remote_mirror(log: TextIO, heartbeat: Callable[[], None]) -> Iterator[int | None]:
    """Hold the test-mirror lock across both remote lanes, or yield None at its bound.

    Focused runs share this lock. Taking it before the lanes keeps their queue out of the
    fixed lane limits, which then bound only each lane's own sync and execution.

    Production callers are promotion_gate.py run (run_gate -> _run_gate_checks)
    and maintenance/verify_remote_mirror_priority.py main. Both are one-shot
    processes that exit on timeout failure; promotion_gate.py land never calls
    this function. The daemon worker and its duplicate may stay blocked until
    that exit or the holder releases. Tests that keep a caller alive release
    their holders and verify late acquisitions do not leak.
    """
    lock_path = run_remote_tests.LOCAL_MIRROR_LOCK_PATH
    print("=== remote mirror lock ===", file=log)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with (
        lock_path.open("a+", encoding="utf-8") as lock,
        lock_path.with_suffix(".turnstile").open("a+") as turnstile,
    ):
        started = time.monotonic()
        admitted = False
        while True:
            try:
                fcntl.lockf(turnstile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                admitted = True
                break
            except BlockingIOError:
                remaining = REMOTE_MIRROR_LOCK_TIMEOUT - (time.monotonic() - started)
                if remaining <= 0:
                    break
                heartbeat()
                time.sleep(min(1.0, remaining))
        if not admitted or not _wait_for_remote_mirror(lock, started, heartbeat):
            # Close before yielding: the caller may keep running after the timeout.
            lock.close()
            turnstile.close()
            print(
                f"TIMEOUT: waited {REMOTE_MIRROR_LOCK_TIMEOUT:g} seconds for {lock_path}",
                file=log,
            )
            log.flush()
            yield None
            return
        turnstile.close()
        print(f"held after {time.monotonic() - started:.1f} seconds", file=log)
        log.flush()
        yield lock.fileno()


def _pending_remote_record() -> str | None:
    pending_path = run_remote_tests._pending_path()
    return pending_path.read_text(encoding="utf-8") if pending_path.exists() else None


def _stop_timed_out_remote_lane(log: TextIO, earlier_record: str | None) -> None:
    """Stop the lane of a runner killed at its limit while the gate still holds the mirror.

    The killed runner cannot stop its detached MacBook lane itself, and an orphan left
    running would block every later sync. Under the held lock only that runner can have
    written a record that differs from the one present before it started; an unchanged
    record belongs to an earlier run whose lane this gate must not stop.
    """
    try:
        if _pending_remote_record() in (None, earlier_record):
            print("The timed-out runner left no remote lane of its own; nothing stopped", file=log)
        else:
            print(run_remote_tests.stop_pending_lane(), file=log)
    except (OSError, RuntimeError) as exc:
        print(f"FAILED: timed-out remote lane not stopped: {exc}", file=log)
    log.flush()


def _run_check_sequence(
    log: TextIO,
    worktree: Path,
    checks: Sequence[GateCheck],
    *,
    heartbeat: Callable[[], None],
    passed: list[str],
    failures: list[str],
    mirror_lock: int | None = None,
) -> None:
    for label, heading, command, selector, environment, validator, timeout in checks:
        heartbeat()
        earlier_record = None
        if mirror_lock is not None:
            environment = {run_remote_tests.INHERITED_MIRROR_LOCK_FD: str(mirror_lock)}
            earlier_record = _pending_remote_record()
        returncode = _run_check(
            log,
            heading=heading,
            command=command,
            worktree=worktree,
            selector=selector,
            environment=environment,
            validator=validator,
            timeout=timeout,
            pass_fds=() if mirror_lock is None else (mirror_lock,),
        )
        if mirror_lock is not None and returncode == 124:
            _stop_timed_out_remote_lane(log, earlier_record)
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


def _run_gate_checks(
    worktree: Path,
    *,
    plain_only: bool,
    remote_lanes: bool = False,
    source_worktree: Path,
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
        canonical = main_worktree(source_worktree)
        plain_command = ("/opt/homebrew/bin/python3", "run_tests.py")
        qt_command = (
            str(canonical / ".venv-qt" / "bin" / "python"),
            "run_tests.py",
        )
        qt_environment = {"QT_QPA_PLATFORM": "offscreen"}
    lane_checks: list[GateCheck] = [
        (
            "plain lane",
            "=== PLAIN LANE ===",
            plain_command,
            _tail_without_progress,
            None,
            None,
            PLAIN_LANE_TIMEOUT,
        ),
    ]
    if not plain_only:
        lane_checks.append((
            "Qt lane",
            "=== QT LANE (monolithic) ===",
            qt_command,
            _tail_without_progress,
            qt_environment,
            None,
            QT_LANE_TIMEOUT,
        ))
    audit_checks: tuple[GateCheck, ...] = (
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
            ("python3", "tools/worktree_guard.py", "--repo", str(source_worktree), "audit"),
            lambda lines: lines[-2:],
            None,
            None,
            None,
        ),
        (
            "worktree clean",
            "=== worktree clean ===",
            ("git", "-C", str(source_worktree), "status", "--porcelain", "--untracked-files=all"),
            lambda lines: lines or ["clean"],
            None,
            _worktree_is_clean,
            None,
        ),
        (
            "diff check",
            "=== diff check ===",
            ("git", "-C", str(source_worktree), "diff", "--check"),
            lambda lines: lines or ["clean"],
            None,
            None,
            None,
        ),
    )

    passed: list[str] = []
    failures: list[str] = []
    run = partial(
        _run_check_sequence, log, worktree, heartbeat=heartbeat, passed=passed, failures=failures,
    )
    if remote_lanes:
        with _hold_remote_mirror(log, heartbeat) as mirror_lock:
            if mirror_lock is None:
                failures.extend(f"{check[0]} (mirror lock wait timed out)" for check in lane_checks)
            else:
                run(lane_checks, mirror_lock=mirror_lock)
    else:
        run(lane_checks)
    run(audit_checks)
    returncode = _run_papercut_check(log, worktree)
    if returncode == 0:
        passed.append("papercuts")
    else:
        failures.append(f"papercuts (exit {returncode})")
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

        def heartbeat() -> None:
            landing_lock.refresh()
            gate_marker.refresh()

        prefix = "gateplain" if plain_only else "gate"
        short_commit = _git(worktree, "rev-parse", "--short", "HEAD").stdout.strip()
        log_path = safe_log_root(worktree) / f"{prefix}-{short_commit}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8") as log:
            kind = "plain-lane gate" if plain_only else "gate"
            print(f"=== {kind} for {commit} in {worktree} ===", file=log)
            print(datetime.now().astimezone().ctime(), file=log)
            with commit_snapshot(worktree, commit) as snapshot:
                passed_checks, failures = _run_gate_checks(
                    snapshot,
                    source_worktree=worktree,
                    plain_only=plain_only,
                    remote_lanes=remote_lanes,
                    log=log,
                    heartbeat=heartbeat,
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
_read_reachability_report.__module__ = _PUBLIC_MODULE
_reachability_log_lines.__module__ = _PUBLIC_MODULE
_reachability_result_matches_pins.__module__ = _PUBLIC_MODULE
_run_reachability_check.__module__ = _PUBLIC_MODULE
_run_gate_checks.__module__ = _PUBLIC_MODULE
_write_evidence.__module__ = _PUBLIC_MODULE
run_gate.__module__ = _PUBLIC_MODULE
