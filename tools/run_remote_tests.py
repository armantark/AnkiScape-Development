#!/usr/bin/env python3
"""Sync an AnkiScape worktree to the MacBook test mirror and run one lane.

Preparation snapshots the worktree and checks prerequisites; sync includes pending-run reconciliation and mirror
setup; execution includes launch, polling and final log retrieval. Lock wait is untimed,
except that a promotion gate holds the lock itself and hands it to its lane runs.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence

HOST = "armans-macbook-pro"
REMOTE_HOME = Path("/Users/armantarkhanian")
REMOTE_ROOT = REMOTE_HOME / "ankiscape-remote-test-host"
REMOTE_REPO = REMOTE_ROOT / "ankiscape_fork"
REMOTE_VENV = REMOTE_ROOT / ".venv-qt"
REMOTE_PLAIN_SITE = REMOTE_ROOT / "plain-site"
REMOTE_GAME_MAIN = REMOTE_ROOT / "sources" / "game-main"
REMOTE_DARKAN = REMOTE_ROOT / "sources" / "darkan-world-server"
SSH = ("ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST)
RSYNC_SSH = "ssh -o BatchMode=yes -o ConnectTimeout=10"
LOCAL_MIRROR_LOCK_PATH = (
    Path.home() / "Library" / "Caches" / "ankiscape-remote-test-host.lock"
)
INHERITED_MIRROR_LOCK_FD = "ANKISCAPE_INHERITED_MIRROR_LOCK_FD"
MIN_TESTS = 4_506
MIN_PLAIN_ACTIVE_TESTS = 3_994
MIN_QT_ACTIVE_TESTS = 4_503
NETWORK_ATTEMPTS = 3
PHASE_NAMES = ("Remote preparation", "Sync", "Test execution")


@dataclass(frozen=True)
class TestSummary:
    ran_line: str
    result_line: str
    tests: int
    skipped: int


@dataclass(frozen=True)
class PhaseTiming:
    elapsed_seconds: float
    finished: bool


@contextmanager
def _measure_phase(timings: dict[str, PhaseTiming], phase: str) -> Iterator[None]:
    started = time.perf_counter()
    finished = False
    try:
        yield
        finished = True
    finally:
        timings[phase] = PhaseTiming(time.perf_counter() - started, finished)


def _print_phase_timings(timings: dict[str, PhaseTiming]) -> None:
    print("Remote phase timings:")
    for phase in PHASE_NAMES:
        timing = timings.get(phase)
        if timing is None:
            print(f"{phase}: not started")
            continue
        state = "finished" if timing.finished else "incomplete"
        print(f"{phase}: {timing.elapsed_seconds:.3f}s ({state})")


def parse_unittest_summary(output: str) -> TestSummary:
    ran_matches = list(re.finditer(r"^Ran (\d+) tests? in .+$", output, re.MULTILINE))
    result_matches = list(re.finditer(r"^OK(?: \(skipped=(\d+)\))?$", output, re.MULTILINE))
    if not ran_matches or not result_matches:
        raise ValueError("remote lane did not emit a complete unittest success summary")
    ran_match = ran_matches[-1]
    result_match = result_matches[-1]
    tests = int(ran_match.group(1))
    skipped = int(result_match.group(1) or 0)
    if tests == 0:
        raise ValueError("remote lane reported zero tests")
    return TestSummary(ran_match.group(0), result_match.group(0), tests, skipped)


def validate_test_summary(lane: str, summary: TestSummary) -> None:
    if summary.tests < MIN_TESTS:
        raise RuntimeError(
            f"remote {lane} lane false pass: ran {summary.tests} tests, "
            f"expected at least {MIN_TESTS}"
        )
    minimum_active = (
        MIN_PLAIN_ACTIVE_TESTS if lane == "plain" else MIN_QT_ACTIVE_TESTS
    )
    active_tests = summary.tests - summary.skipped
    if active_tests < minimum_active:
        raise RuntimeError(
            f"remote {lane} lane false pass: active={active_tests} "
            f"(tests={summary.tests}, skipped={summary.skipped}), "
            f"expected at least {minimum_active} active tests"
        )


def _run_with_retries(command: Sequence[str], *, label: str) -> subprocess.CompletedProcess[str]:
    last: subprocess.CompletedProcess[str] | None = None
    for attempt in range(1, NETWORK_ATTEMPTS + 1):
        last = subprocess.run(command, text=True, capture_output=True, check=False)
        if last.returncode == 0:
            return last
        if attempt < NETWORK_ATTEMPTS:
            time.sleep(attempt)
    assert last is not None
    detail = last.stderr.strip() or last.stdout.strip() or "no output"
    raise RuntimeError(f"{label} failed after {NETWORK_ATTEMPTS} attempts: {detail}")


class SSHCommandError(RuntimeError):
    def __init__(self, label: str, result: subprocess.CompletedProcess[str]):
        self.returncode = result.returncode
        super().__init__(
            f"{label} failed with exit {result.returncode}; "
            f"stdout: {result.stdout!r}; stderr: {result.stderr!r}"
        )


def _ssh(remote_command: str, *, label: str, repeat_safe: bool = False) -> str:
    for attempt in range(1, NETWORK_ATTEMPTS + 1):
        result = subprocess.run(
            (*SSH, remote_command), text=True, capture_output=True, check=False
        )
        if result.returncode == 0:
            return result.stdout
        # SSH 255 can also follow remote execution: only repeat safe operations.
        if not repeat_safe or result.returncode != 255 or attempt == NETWORK_ATTEMPTS:
            raise SSHCommandError(label, result)
        time.sleep(attempt)
    raise AssertionError("unreachable SSH retry state")


def _pending_path() -> Path:
    return LOCAL_MIRROR_LOCK_PATH.with_suffix(".pending.json")


def _completion_report(report_path: str) -> int | None:
    report = _ssh(
        f"cat {shlex.quote(report_path)} 2>/dev/null || true",
        label="remote lane report poll",
        repeat_safe=True,
    ).strip()
    if not report:
        return None
    try:
        returncode = int(report)
    except ValueError as exc:
        raise RuntimeError(f"invalid remote lane report {report!r}: {report_path}") from exc
    if not 0 <= returncode <= 255:
        raise RuntimeError(f"invalid remote lane report {report!r}: {report_path}")
    return returncode


def _reconcile_pending_run() -> None:
    pending_path = _pending_path()
    if pending_path.exists():
        try:
            pending = json.loads(pending_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid pending run record; sync blocked: {pending_path}") from exc
        if not isinstance(pending, dict) or any(
            not isinstance(pending.get(field), str) or not pending[field].strip()
            for field in ("run_id", "log_path", "report_path")
        ):
            raise RuntimeError(f"invalid pending run record; sync blocked: {pending_path}")
        try:
            returncode = _completion_report(pending["report_path"])
            if returncode is None:
                raise RuntimeError("previous remote lane has no completion report; sync blocked")
        except RuntimeError as exc:
            raise RuntimeError(
                f"{exc}; pending record: {pending_path}; run: {pending['run_id']}; "
                f"log: {pending['log_path']}; report: {pending['report_path']}"
            ) from exc
        print(
            f"Previous remote run {pending['run_id']} completed with exit {returncode}; "
            f"log: {pending['log_path']}", file=sys.stderr,
        )
        pending_path.unlink()


def _rsync_command(local_worktree: Path, destination: str) -> tuple[str, ...]:
    return (
        "rsync",
        "-a",
        "--delete",
        "--delete-excluded",
        "-e",
        RSYNC_SSH,
        "--exclude=.git",
        "--exclude=__pycache__/",
        "--exclude=.venv-qt",
        "--exclude=ankiscape_debug.log*",
        f"{local_worktree}/",
        destination,
    )


def _sync(local_worktree: Path) -> None:
    _reconcile_pending_run()
    _ssh(
        f"mkdir -p {shlex.quote(str(REMOTE_REPO))} "
        f"{shlex.quote(str(REMOTE_ROOT / 'reports'))}",
        label="remote mirror setup",
        repeat_safe=True,
    )
    command = _rsync_command(local_worktree, f"{HOST}:{REMOTE_REPO}/")
    _run_with_retries(command, label="worktree sync")
    _ssh(
        f"ln -sfn {shlex.quote(str(REMOTE_VENV))} "
        f"{shlex.quote(str(REMOTE_REPO / '.venv-qt'))}",
        label="remote Qt interpreter link",
        repeat_safe=True,
    )


def _remote_lane_command(lane: str, *, selectors: Sequence[str] = ()) -> str:
    environment = (
        "PATH=/opt/homebrew/bin:/usr/bin:/bin "
        f"ANKISCAPE_GAME_MAIN={shlex.quote(str(REMOTE_GAME_MAIN))} "
        f"ANKISCAPE_DARKAN_WORLD_SERVER={shlex.quote(str(REMOTE_DARKAN))} "
    )
    if lane == "plain":
        return (
            environment
            + f"PYTHONPATH={shlex.quote(str(REMOTE_PLAIN_SITE))} "
            + "/opt/homebrew/bin/python3 run_tests.py"
            + (" --quiet -- " + shlex.join(selectors) if selectors else "")
        )
    return (
        environment
        + f"QT_QPA_PLATFORM=offscreen {shlex.quote(str(REMOTE_VENV / 'bin/python'))} "
        + ("run_tests.py --quiet -- " + shlex.join(selectors) if selectors else "-m unittest discover tests")
    )


def _preflight(lane: str) -> None:
    common_checks = (
        f"test -x {shlex.quote(str(REMOTE_VENV / 'bin/python'))}",
        f"test -f {shlex.quote(str(REMOTE_GAME_MAIN / 'data/cfg/items.yml'))}",
        f"test -f {shlex.quote(str(REMOTE_DARKAN / 'developer-information/npcList.txt'))}",
        f"test -f {shlex.quote(str(REMOTE_DARKAN / 'developer-information/beasts.txt'))}",
        f"test -d {shlex.quote(str(REMOTE_DARKAN / 'data/npcs/combatdefs'))}",
        "PATH=/opt/homebrew/bin:/usr/bin:/bin command -v rg >/dev/null",
    )
    if lane == "plain":
        lane_checks = (
            f"PYTHONPATH={shlex.quote(str(REMOTE_PLAIN_SITE))} "
            "/opt/homebrew/bin/python3 -c 'import PIL'",
        )
    else:
        cache_root = REMOTE_HOME / "Library/Caches/codex/2012scape-openrs2/extracted"
        lane_checks = (
            f"{shlex.quote(str(REMOTE_VENV / 'bin/python'))} -c 'import anki, aqt, PyQt6'",
            "test -x /opt/homebrew/opt/openjdk@25/bin/java",
            "test -x /opt/homebrew/opt/openjdk@25/bin/javac",
            f"test -d {shlex.quote(str(REMOTE_HOME / '.gradle/caches/modules-2/files-2.1/rs.darkan/core/2.0.5'))}",
            *(
                f"test -f {shlex.quote(str(cache_root / revision / 'cache/main_file_cache.dat2'))}"
                for revision in (
                    "652-2011-06-08",
                    "727-2012-07-24",
                    "741-2012-11-04",
                    "742-2012-11-07",
                )
            ),
        )
    _ssh(
        " && ".join((*common_checks, *lane_checks)),
        label=f"remote {lane} prerequisites",
        repeat_safe=True,
    )


def _stream_remote_run(
    lane: str, *, timeout: float, poll_interval: float, selectors: Sequence[str] = (),
) -> tuple[int, str]:
    run_id = f"{lane}-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    log_path = REMOTE_ROOT / "reports" / f"{run_id}.log"
    report_path = REMOTE_ROOT / "reports" / f"{run_id}.report"
    temporary_report = REMOTE_ROOT / "reports" / f"{run_id}.report.tmp"
    lane_command = _remote_lane_command(lane, selectors=selectors)
    script = "\n".join(
        (
            f"cd {shlex.quote(str(REMOTE_REPO))}",
            "exit_code=$?",
            f'if [ "$exit_code" -eq 0 ]; then {lane_command}; exit_code=$?; fi',
            f"printf '%s\\n' \"$exit_code\" > {shlex.quote(str(temporary_report))}",
            f"mv {shlex.quote(str(temporary_report))} {shlex.quote(str(report_path))}",
        )
    )
    launch = (
        f"nohup /bin/sh -c {shlex.quote(script)} </dev/null "
        f"> {shlex.quote(str(log_path))} 2>&1 &"
    )
    pending = {"run_id": run_id, "log_path": str(log_path), "report_path": str(report_path)}
    with _pending_path().open("x", encoding="utf-8") as pending_file:
        json.dump(pending, pending_file)
        pending_file.flush()
        os.fsync(pending_file.fileno())
    try:
        _ssh(launch, label="remote lane launch")
    except SSHCommandError as exc:
        if exc.returncode != 255:
            raise
        print(f"{exc}; reconciling the same run without relaunch", file=sys.stderr)

    started = time.monotonic()
    seen = ""
    while True:
        output = _ssh(
            f"cat {shlex.quote(str(log_path))} 2>/dev/null || true",
            label="remote lane log poll",
            repeat_safe=True,
        )
        if output.startswith(seen):
            addition = output[len(seen) :]
        else:
            addition = output
        if addition:
            print(addition, end="", flush=True)
        seen = output

        returncode = _completion_report(str(report_path))
        if returncode is not None:
            _pending_path().unlink()
            final_output = _ssh(
                f"cat {shlex.quote(str(log_path))} 2>/dev/null || true",
                label="remote lane final log read",
                repeat_safe=True,
            )
            if final_output.startswith(seen):
                addition = final_output[len(seen) :]
            else:
                addition = final_output
            if addition:
                print(addition, end="", flush=True)
            return returncode, final_output
        if time.monotonic() - started >= timeout:
            raise TimeoutError(
                f"remote {lane} lane did not finish within {timeout:g} seconds; "
                f"report path: {report_path}"
            )
        time.sleep(poll_interval)


@contextmanager
def _hold_mirror_lock() -> Iterator[None]:
    inherited = os.environ.get(INHERITED_MIRROR_LOCK_FD)
    if inherited is not None:
        descriptor = int(inherited)
        try:
            if not os.path.samestat(os.fstat(descriptor), LOCAL_MIRROR_LOCK_PATH.stat()):
                raise OSError("descriptor names a different file")
            # Succeeds only on the description the parent gate already locked, so the
            # variable cannot jump the queue; unlocking here would release the gate's hold.
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise RuntimeError(
                f"inherited descriptor {descriptor} does not hold {LOCAL_MIRROR_LOCK_PATH}"
            ) from exc
        yield
        return
    LOCAL_MIRROR_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCAL_MIRROR_LOCK_PATH.open("a+", encoding="utf-8") as mirror_lock:
        try:
            fcntl.flock(
                mirror_lock.fileno(),
                fcntl.LOCK_EX | fcntl.LOCK_NB,
            )
        except BlockingIOError:
            print(
                f"Remote mirror busy; waiting for {LOCAL_MIRROR_LOCK_PATH}",
                file=sys.stderr,
            )
            fcntl.flock(mirror_lock.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(mirror_lock.fileno(), fcntl.LOCK_UN)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("local_worktree", type=Path)
    parser.add_argument("lane", choices=("plain", "qt"))
    parser.add_argument("--timeout", type=float, default=1800.0)
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument(
        "--select", action="append", default=[],
        help="Focused test selector; repeat for each selection.",
    )
    parser.add_argument(
        "--expected-tests", type=int,
        help="Exact focused test count; no skipped tests are accepted.",
    )
    args = parser.parse_args(argv)

    args.local_worktree = args.local_worktree.expanduser().resolve()
    if not (args.local_worktree / "run_tests.py").is_file():
        parser.error(f"not an AnkiScape worktree: {args.local_worktree}")
    if args.timeout <= 0 or args.poll_interval <= 0:
        parser.error("--timeout and --poll-interval must be positive")
    if bool(args.select) != (args.expected_tests is not None):
        parser.error("--select and --expected-tests must be supplied together")
    if args.expected_tests is not None and args.expected_tests <= 0:
        parser.error("--expected-tests must be positive")
    if any(not selector.strip() for selector in args.select):
        parser.error("--select must not be empty")
    return args


def _validate_focused_summary(summary: TestSummary, expected_tests: int) -> None:
    if summary.tests != expected_tests or summary.skipped:
        raise RuntimeError(
            f"remote focused lane false pass: tests={summary.tests}, "
            f"skipped={summary.skipped}; expected exactly {expected_tests} tests and no skips"
        )


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    local_worktree = args.local_worktree
    timings: dict[str, PhaseTiming] = {}

    try:
        with tempfile.TemporaryDirectory(prefix="ankiscape-remote-sync-") as snapshot:
            with _measure_phase(timings, "Remote preparation"):
                # The mirror lock wait is untimed; syncing the live tree after it would test
                # whatever the author stashed or edited while the run queued.
                _run_with_retries(
                    _rsync_command(local_worktree, f"{snapshot}/"), label="worktree snapshot"
                )
                _preflight(args.lane)
            with _hold_mirror_lock():
                with _measure_phase(timings, "Sync"):
                    _sync(Path(snapshot))
                with _measure_phase(timings, "Test execution"):
                    returncode, output = _stream_remote_run(
                        args.lane,
                        timeout=args.timeout,
                        poll_interval=args.poll_interval,
                        selectors=args.select,
                    )
        if returncode != 0:
            raise RuntimeError(f"remote {args.lane} lane failed with exit {returncode}")
        summary = parse_unittest_summary(output)
        if args.select:
            _validate_focused_summary(summary, args.expected_tests)
        else:
            validate_test_summary(args.lane, summary)
    except (OSError, RuntimeError, TimeoutError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        pending_path = _pending_path()
        if pending_path.exists():
            print(f"Unresolved remote run blocks sync; pending record: {pending_path}", file=sys.stderr)
            try:
                pending = json.loads(pending_path.read_text(encoding="utf-8"))
                print(
                    f"Run: {pending['run_id']}; log: {pending['log_path']}; "
                    f"report: {pending['report_path']}", file=sys.stderr,
                )
                read_command = f"cat {shlex.quote(pending['report_path'])} {shlex.quote(pending['log_path'])}"
                print(f"Read-only inspection: {shlex.join((*SSH, read_command))}", file=sys.stderr)
            except (OSError, ValueError, KeyError, TypeError):
                print("Pending record is unreadable; preserve it for driver reconciliation of the exact run.", file=sys.stderr)
            print(
                "Rerun the test runner to reconcile completion before sync. "
                "If completion cannot be read, the driver must reconcile this exact run and confirm "
                "no active worker or in-flight launch before manually clearing the pending record.",
                file=sys.stderr,
            )
        return 1
    else:
        scope = "focused " if args.select else ""
        print(f"Remote {scope}{args.lane} lane summary:")
        print(summary.ran_line)
        print(summary.result_line)
        return 0
    finally:
        _print_phase_timings(timings)


if __name__ == "__main__":
    raise SystemExit(main())
