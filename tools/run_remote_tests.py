#!/usr/bin/env python3
"""Sync an AnkiScape worktree to the MacBook test mirror and run one lane.

Preparation snapshots the worktree and checks prerequisites; sync includes pending-run reconciliation and mirror
setup; execution includes launch, polling and final log retrieval. Lock wait is untimed,
except that a promotion gate holds the lock itself and hands it to its lane runs. The
pending JSON is transient coordination state: retain the announced exact-run log and
report paths, and never infer success or relaunch solely because that record disappeared.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, NoReturn, Sequence

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
MAX_PROOF_FILE_BYTES = 256 * 1024 * 1024
LANE_GROUP_LEADER = (
    "import os, resource, sys; "
    "resource.setrlimit(resource.RLIMIT_FSIZE, (int(sys.argv[2]), int(sys.argv[2]))); "
    "os.setpgid(0, 0); os.execv('/bin/sh', ('/bin/sh', '-c', sys.argv[1]))"
)
# A lane owns its process group, every process with the lane's pid file (its stdin) or log
# (its stdout and stderr) open for writing as a standard stream, and all their descendants.
# Only lane work inherits those descriptors, so a test subprocess that started its own
# session and outlived its parent still counts, while a reader of either file does not.
# The leader never lets go of its streams, so a process at the leader's pid that holds
# neither file reused that pid after the leader exited, and its group is not the lane's.
# A subprocess that leaves the group, replaces all three streams and outlives its parent
# cannot be seen: macOS shows no other process's environment to mark it with.
# The probe holds both files itself, so lsof exits 0 only when its scan found them and must
# list the probe; any failed scan fails the check instead of reading as a stopped lane.
# lsof lives in /usr/sbin, outside the lanes' PATH.
LANE_PROCESSES = """\
exec 8<"$log_path" 9<"$pid_path" || exit 1
lane_processes() {
  holders=$(/usr/sbin/lsof -w -F pfa -- "$pid_path" "$log_path") || return 1
  table=$(ps -A -o pid= -o ppid= -o pgid=) || return 1
  printf '%s\\n%s\\n' "$table" "$holders" | awk -v group="$group" -v probe="$$" '
    NF == 3 { parent[$1] = $2; if ($3 == group) grouped[$1] = 1 }
    /^p/ { holder = substr($0, 2); listed[holder] = 1 }
    /^f/ { descriptor = substr($0, 2) }
    /^a[wu]/ && descriptor ~ /^[012]$/ { owned[holder] = 1 }
    END {
      if (!(probe in listed)) exit 1
      if (!(group in parent) || (group in owned)) for (p in grouped) owned[p] = 1
      do {
        grown = 0
        for (p in parent) if (!(p in owned) && (parent[p] in owned)) { owned[p] = 1; grown = 1 }
      } while (grown)
      for (p in owned) print p
    }'
}
"""
# xargs splits the pid list the same way whichever login shell runs the script.
LANE_STOP = LANE_PROCESSES + """\
for signal in TERM TERM TERM TERM TERM TERM TERM TERM TERM TERM KILL KILL KILL; do
  processes=$(lane_processes) || exit 1
  [ -z "$processes" ] && exit 0
  echo "$processes" | xargs kill -"$signal" 2>/dev/null
  sleep 1
done
processes=$(lane_processes) || exit 1
[ -z "$processes" ]
"""
LANE_LIVENESS = LANE_PROCESSES + """\
processes=$(lane_processes) || exit 1
[ -n "$processes" ] || echo stopped
"""
LANE_STOP_TIMEOUT = 90.0


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


def parse_count_inventory(output: str) -> int:
    matches = re.findall(r"^Matching tests: (\d+)$", output, re.MULTILINE)
    if not matches:
        raise ValueError("remote inventory did not emit 'Matching tests: N'")
    return int(matches[-1])


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


class SSHDeadlineExceeded(RuntimeError):
    pass


def _ssh(
    remote_command: str, *, label: str, repeat_safe: bool = False, deadline: float | None = None,
) -> str:
    for attempt in range(1, NETWORK_ATTEMPTS + 1):
        try:
            result = subprocess.run(
                (*SSH, remote_command), text=True, capture_output=True, check=False,
                timeout=None if deadline is None else max(deadline - time.monotonic(), 0.0),
            )
        except subprocess.TimeoutExpired as exc:
            raise SSHDeadlineExceeded(f"{label} did not finish before its deadline") from exc
        if result.returncode == 0:
            return result.stdout
        # SSH 255 can also follow remote execution: only repeat safe operations.
        if not repeat_safe or result.returncode != 255 or attempt == NETWORK_ATTEMPTS:
            raise SSHCommandError(label, result)
        time.sleep(attempt)
    raise AssertionError("unreachable SSH retry state")


def _pending_path() -> Path:
    return LOCAL_MIRROR_LOCK_PATH.with_suffix(".pending.json")


def _run_identity(pending: dict[str, str]) -> str:
    return (
        f"run: {pending['run_id']}; log: {pending['log_path']}; "
        f"report: {pending['report_path']}"
    )


def _completion_report(report_path: str, deadline: float | None = None) -> int | None:
    report = _ssh(
        f"cat {shlex.quote(report_path)} 2>/dev/null || true",
        label="remote lane report poll",
        repeat_safe=True,
        deadline=deadline,
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


def _read_pending() -> dict[str, str] | None:
    pending_path = _pending_path()
    if not pending_path.exists():
        return None
    try:
        pending = json.loads(pending_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid pending run record; sync blocked: {pending_path}") from exc
    # A record written before lanes recorded their process group has no pid_path.
    if not isinstance(pending, dict) or any(
        not isinstance(pending.get(field), str) or not pending[field].strip()
        for field in {"run_id", "log_path", "report_path"} | (pending.keys() & {"pid_path"})
    ):
        raise RuntimeError(f"invalid pending run record; sync blocked: {pending_path}")
    return pending


def _lane_process_group(pending: dict[str, str], deadline: float | None = None) -> int | None:
    if "pid_path" not in pending:
        return None
    recorded = _ssh(
        f"cat {shlex.quote(pending['pid_path'])} 2>/dev/null || true",
        label="remote lane process group read",
        repeat_safe=True,
        deadline=deadline,
    ).strip()
    # Group 1 is launchd's, whose descendants are every process on the MacBook; 0 is none.
    if not re.fullmatch(r"[0-9]+", recorded) or int(recorded) <= 1:
        return None
    return int(recorded)


def _lane_script(pending: dict[str, str], group: int, action: str) -> str:
    paths = " ".join(f"{field}={shlex.quote(pending[field])}" for field in ("pid_path", "log_path"))
    return f"group={group} {paths}\n{action}"


def _lane_confirmed_stopped(pending: dict[str, str], deadline: float) -> bool:
    group = _lane_process_group(pending, deadline)
    return group is not None and _ssh(
        _lane_script(pending, group, LANE_LIVENESS),
        label="remote lane liveness check",
        repeat_safe=True,
        deadline=deadline,
    ).strip() == "stopped"


def stop_pending_lane() -> str:
    """Stop every process of the pending lane, confirm they are gone, then clear its record.

    Only the mirror-lock holder that launched the pending lane may call this. A later run
    never stops another run's lane; it refuses to sync until that lane finishes or dies.
    The whole stop has a deadline, so a stalled host cannot keep the mirror lock held;
    an unconfirmed stop keeps the record, which keeps later syncs blocked.
    """
    deadline = time.monotonic() + LANE_STOP_TIMEOUT
    pending = _read_pending()
    if pending is None:
        return "No pending remote lane to stop"
    group = _lane_process_group(pending, deadline)
    if group is None:
        raise RuntimeError(
            f"remote run {pending['run_id']} recorded no process group; "
            f"cannot confirm it stopped: {pending.get('pid_path')}"
        )
    _ssh(
        _lane_script(pending, group, LANE_STOP),
        label=f"remote run {pending['run_id']} stop",
        repeat_safe=True,
        deadline=deadline,
    )
    _pending_path().unlink()
    return f"Stopped remote run {pending['run_id']}; log: {pending['log_path']}"


def _reconcile_pending_run() -> None:
    pending = _read_pending()
    if pending is None:
        return
    pending_path = _pending_path()
    try:
        # A lane writes its report before its processes exit, and a detached helper can
        # outlive it, so only a confirmed stop frees the mirror. A record without a process
        # group predates that check and can only be judged by its report. The check holds
        # the mirror lock, so a stalled host must not hold it past the deadline.
        deadline = time.monotonic() + LANE_STOP_TIMEOUT
        stopped = _lane_confirmed_stopped(pending, deadline)
        returncode = _completion_report(pending["report_path"], deadline)
        if not stopped and (returncode is None or "pid_path" in pending):
            raise RuntimeError("previous remote lane is not confirmed stopped; sync blocked")
    except RuntimeError as exc:
        raise RuntimeError(
            f"{exc}; pending record: {pending_path}; {_run_identity(pending)}"
        ) from exc
    if returncode is None:
        print(
            f"Previous remote run {pending['run_id']} stopped without a completion report; "
            f"cleared its record; log: {pending['log_path']}", file=sys.stderr,
        )
    else:
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
        f"{shlex.quote(str(REMOTE_REPO / '.venv-qt'))} && "
        f"cd {shlex.quote(str(REMOTE_REPO))} && "
        f"{shlex.quote(str(REMOTE_VENV / 'bin/python'))} -m tools.maintenance.report_retention "
        f"{shlex.quote(str(REMOTE_ROOT / 'reports'))} --apply",
        label="remote interpreter and report retention",
        repeat_safe=True,
    )


def _remote_lane_command(
    lane: str, *, selectors: Sequence[str] = (), collect_only: bool = False,
) -> str:
    environment = (
        "PATH=/opt/homebrew/bin:/usr/bin:/bin "
        f"ANKISCAPE_GAME_MAIN={shlex.quote(str(REMOTE_GAME_MAIN))} "
        f"ANKISCAPE_DARKAN_WORLD_SERVER={shlex.quote(str(REMOTE_DARKAN))} "
    )
    arguments = ["run_tests.py"]
    if collect_only:
        arguments.extend(("--count", "--", *selectors))
    elif selectors:
        arguments.extend(("--quiet", "--", *selectors))
    run_tests = shlex.join(arguments)
    if lane == "plain":
        return (
            environment
            + f"PYTHONPATH={shlex.quote(str(REMOTE_PLAIN_SITE))} "
            + "/opt/homebrew/bin/python3 "
            + run_tests
        )
    return (
        environment
        + f"QT_QPA_PLATFORM=offscreen {shlex.quote(str(REMOTE_VENV / 'bin/python'))} "
        + run_tests
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


def _lane_command_with_skip_report(
    lane: str, selectors: Sequence[str], report_path: Path, *, collect_only: bool,
) -> str:
    command = _remote_lane_command(lane, selectors=selectors, collect_only=collect_only)
    if selectors and not collect_only:
        return f"ANKISCAPE_TEST_SKIP_REPORT={shlex.quote(str(report_path))} " + command
    return command


def _read_skip_report(report_path: Path) -> list[list[str]]:
    output = _ssh(
        f"cat {shlex.quote(str(report_path))} 2>/dev/null || true",
        label="remote skipped-test report", repeat_safe=True,
    )
    records = json.loads(output)
    if not isinstance(records, list):
        raise ValueError("skipped-test report must be a list")
    for record in records:
        if not isinstance(record, list) or len(record) != 2:
            raise ValueError("skipped-test report entries must be ID/reason pairs")
        if not all(isinstance(value, str) for value in record):
            raise ValueError("skipped-test report IDs and reasons must be strings")
    return records


def _print_skipped_tests(
    report_path: Path, selectors: Sequence[str], returncode: int, output: str,
) -> None:
    if not selectors:
        return
    if returncode == 0:
        try:
            summary = parse_unittest_summary(output)
        except ValueError:
            # Main owns incomplete-summary refusals; no skip outcome is known here.
            return
        if not summary.skipped:
            return
    try:
        for test_id, reason in _read_skip_report(report_path):
            print(f"Skipped test: {test_id}: {reason}", file=sys.stderr)
    except Exception as exc:
        # An optional report cannot overrule the exit code or focused-summary gate.
        print(f"warning: skipped-test diagnostics unavailable: {exc}", file=sys.stderr)


def _raise_lane_timeout(
    lane: str, timeout: float, report_path: Path, cause: BaseException | None = None,
) -> NoReturn:
    message = (
        f"remote {lane} lane did not finish within {timeout:g} seconds; "
        f"report path: {report_path}"
    )
    print(f"{message}; stopping it", file=sys.stderr)
    print(stop_pending_lane(), file=sys.stderr)
    raise TimeoutError(message) from cause


def _stream_remote_run(
    lane: str, *, timeout: float, poll_interval: float, selectors: Sequence[str] = (),
    collect_only: bool = False,
) -> tuple[int, str]:
    run_id = f"{lane}-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    log_path = REMOTE_ROOT / "reports" / f"{run_id}.log"
    report_path = REMOTE_ROOT / "reports" / f"{run_id}.report"
    temporary_report = REMOTE_ROOT / "reports" / f"{run_id}.report.tmp"
    pid_path = REMOTE_ROOT / "reports" / f"{run_id}.pid"
    skip_report_path = REMOTE_ROOT / "reports" / f"{run_id}.skips.json"
    lane_command = _lane_command_with_skip_report(
        lane, selectors, skip_report_path, collect_only=collect_only,
    )
    script = "\n".join(
        (
            f"printf '%s\\n' \"$$\" > {shlex.quote(str(pid_path))}",
            f"cd {shlex.quote(str(REMOTE_REPO))}",
            "exit_code=$?",
            f'if [ "$exit_code" -eq 0 ]; then {lane_command}; exit_code=$?; fi',
            f"printf '%s\\n' \"$exit_code\" > {shlex.quote(str(temporary_report))}",
            f"mv {shlex.quote(str(temporary_report))} {shlex.quote(str(report_path))}",
        )
    )
    # Its own process group, and the pid file as stdin, let a timeout find and stop the
    # whole lane, test subprocesses in their own sessions included. `<>` creates the pid
    # file before the lane writes its group into it.
    launch = (
        f"nohup {shlex.quote(str(REMOTE_VENV / 'bin/python'))} -c {shlex.quote(LANE_GROUP_LEADER)} "
        f"{shlex.quote(script)} {MAX_PROOF_FILE_BYTES} "
        f"<> {shlex.quote(str(pid_path))} > {shlex.quote(str(log_path))} 2>&1 &"
    )
    pending = {
        "run_id": run_id, "log_path": str(log_path), "report_path": str(report_path),
        "pid_path": str(pid_path),
    }
    with _pending_path().open("x", encoding="utf-8") as pending_file:
        json.dump(pending, pending_file)
        pending_file.flush()
        os.fsync(pending_file.fileno())
    print(f"Remote {_run_identity(pending)}", file=sys.stderr)
    try:
        _ssh(launch, label="remote lane launch")
    except SSHCommandError as exc:
        if exc.returncode != 255:
            raise
        print(f"{exc}; reconciling the same run without relaunch", file=sys.stderr)

    return _wait_for_remote_run(
        lane,
        timeout=timeout,
        poll_interval=poll_interval,
        selectors=selectors,
        collect_only=collect_only,
        log_path=log_path,
        report_path=report_path,
        skip_report_path=skip_report_path,
    )


def _print_log_addition(seen: str, output: str) -> str:
    addition = output[len(seen) :] if output.startswith(seen) else output
    if addition:
        print(addition, end="", flush=True)
    return output


def _poll_remote_run(
    log_path: Path, report_path: Path, seen: str, deadline: float,
) -> tuple[str, int | None]:
    output = _ssh(
        f"cat {shlex.quote(str(log_path))} 2>/dev/null || true",
        label="remote lane log poll", repeat_safe=True, deadline=deadline,
    )
    seen = _print_log_addition(seen, output)
    return seen, _completion_report(str(report_path), deadline)


def _finish_remote_run(
    log_path: Path, skip_report_path: Path, seen: str, selectors: Sequence[str],
    returncode: int, collect_only: bool,
) -> tuple[int, str]:
    # The report precedes the lane's exit, and a detached helper can outlive it.
    stop_pending_lane()
    final_output = _ssh(
        f"cat {shlex.quote(str(log_path))} 2>/dev/null || true",
        label="remote lane final log read", repeat_safe=True,
        deadline=time.monotonic() + LANE_STOP_TIMEOUT,
    )
    _print_log_addition(seen, final_output)
    if not collect_only:
        _print_skipped_tests(skip_report_path, selectors, returncode, final_output)
    return returncode, final_output


def _wait_for_remote_run(
    lane: str, *, timeout: float, poll_interval: float, selectors: Sequence[str],
    collect_only: bool, log_path: Path, report_path: Path, skip_report_path: Path,
) -> tuple[int, str]:
    deadline = time.monotonic() + timeout
    seen = ""
    while True:
        try:
            seen, returncode = _poll_remote_run(log_path, report_path, seen, deadline)
        except SSHDeadlineExceeded as exc:
            _raise_lane_timeout(lane, timeout, report_path, exc)
        remaining = deadline - time.monotonic()
        # A report that lands after the deadline is still a timeout, not a pass.
        if remaining <= 0:
            _raise_lane_timeout(lane, timeout, report_path)
        if returncode is not None:
            return _finish_remote_run(
                log_path, skip_report_path, seen, selectors, returncode, collect_only,
            )
        time.sleep(min(poll_interval, remaining))


def _wait_for_turnstile() -> None:
    """Pass mirror admission after a waiting gate releases it.

    Never wait for the mirror or for an earlier runner while holding this: runners would
    then starve the gate here instead.
    """
    with LOCAL_MIRROR_LOCK_PATH.with_suffix(".turnstile").open("a+") as turnstile:
        try:
            fcntl.lockf(turnstile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(
                f"Remote mirror busy; waiting without a deadline for turnstile {turnstile.name}. "
                "--timeout starts after launch; run this command as a background task.",
                file=sys.stderr,
            )
            fcntl.lockf(turnstile.fileno(), fcntl.LOCK_EX)


@contextmanager
def _mirror_queue_place() -> Iterator[None]:
    """Register before gate admission and retain every earlier normal's priority.

    The file length allocates monotonically increasing tickets under byte zero's lock.
    Each runner locks its own ticket before publication, then every earlier ticket as
    one range. Later runners cannot pass a paused predecessor; death releases all owned
    ranges without deleting coordination state or reusing a live ticket.
    """
    with LOCAL_MIRROR_LOCK_PATH.with_suffix(".queue").open("a+") as queue:
        descriptor = queue.fileno()
        try:
            fcntl.lockf(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB, 1, 0)
        except BlockingIOError:
            fcntl.lockf(descriptor, fcntl.LOCK_EX, 1, 0)
        place = os.fstat(descriptor).st_size + 1
        fcntl.lockf(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB, 1, place)
        os.ftruncate(descriptor, place)
        fcntl.lockf(descriptor, fcntl.LOCK_UN, 1, 0)
        if place > 1:
            try:
                fcntl.lockf(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB, place - 1, 1)
            except BlockingIOError:
                print(
                    f"Remote mirror busy; waiting without a deadline for queue {queue.name}. "
                    "--timeout starts after launch; run this command as a background task.",
                    file=sys.stderr,
                )
                fcntl.lockf(descriptor, fcntl.LOCK_EX, place - 1, 1)
        yield


@contextmanager
def _hold_mirror_lock() -> Iterator[None]:
    """Hold the test mirror for one run, or reuse the lock a promotion gate handed down.

    Normal runners retain registration order across gate waits. A waiting gate blocks
    admission, and only the normal queue head competes for the mirror itself.
    """
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
    with (
        _mirror_queue_place(),
        LOCAL_MIRROR_LOCK_PATH.open("a+", encoding="utf-8") as mirror_lock,
    ):
        _wait_for_turnstile()
        try:
            fcntl.flock(
                mirror_lock.fileno(),
                fcntl.LOCK_EX | fcntl.LOCK_NB,
            )
        except BlockingIOError:
            print(
                f"Remote mirror busy; waiting without a deadline for {LOCAL_MIRROR_LOCK_PATH}. "
                "--timeout starts after launch; run this command as a background task.",
                file=sys.stderr,
            )
            fcntl.flock(mirror_lock.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(mirror_lock.fileno(), fcntl.LOCK_UN)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "The mirror-lock wait is untimed; --timeout covers lane execution only. Launch "
            "the runner as a background task. The run tests the snapshot taken at launch, "
            "so rerun after any later intended edit."
        ),
    )
    parser.add_argument("local_worktree", type=Path)
    parser.add_argument("lane", choices=("plain", "qt"))
    parser.add_argument("--timeout", type=float, default=1800.0)
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument(
        "--select", action="append", default=[],
        help="Focused test selector; repeat for each selection.",
    )
    parser.add_argument(
        "--collect-only", action="store_true",
        help=(
            "discover the selected tests on the synchronized remote lane without running them; "
            "prints the authoritative 'Matching tests: N' for a later --expected-tests run"
        ),
    )
    parser.add_argument(
        "--expected-tests", type=int,
        help=(
            "Exact focused test count; no skipped tests are accepted. Take it from a remote "
            "--collect-only run with the same selectors and unchanged tree."
        ),
    )
    args = parser.parse_args(argv)

    args.local_worktree = args.local_worktree.expanduser().resolve()
    if not (args.local_worktree / "run_tests.py").is_file():
        parser.error(f"not an AnkiScape worktree: {args.local_worktree}")
    if args.timeout <= 0 or args.poll_interval <= 0:
        parser.error("--timeout and --poll-interval must be positive")
    if args.collect_only:
        if not args.select or args.expected_tests is not None:
            parser.error("--collect-only requires --select and cannot use --expected-tests")
    elif bool(args.select) != (args.expected_tests is not None):
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


def _validated_summary_lines(
    args: argparse.Namespace, returncode: int, output: str,
) -> tuple[str, ...]:
    if returncode == 128 + signal.SIGXFSZ:
        raise RuntimeError(
            f"remote {args.lane} lane exceeded its per-file storage limit "
            f"of {MAX_PROOF_FILE_BYTES} bytes (SIGXFSZ)"
        )
    if returncode != 0:
        raise RuntimeError(f"remote {args.lane} lane failed with exit {returncode}")
    if args.collect_only:
        count = parse_count_inventory(output)
        return f"Remote {args.lane} inventory summary:", f"Matching tests: {count}"
    summary = parse_unittest_summary(output)
    if args.select:
        _validate_focused_summary(summary, args.expected_tests)
    else:
        validate_test_summary(args.lane, summary)
    scope = "focused " if args.select else ""
    return f"Remote {scope}{args.lane} lane summary:", summary.ran_line, summary.result_line


def main(argv: Sequence[str] | None = None) -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from tools.native.session_guard import _copy_file

    args = _parse_args(argv)
    local_worktree = args.local_worktree
    timings: dict[str, PhaseTiming] = {}

    print(
        "Remote verification uses the snapshot taken now; later edits require a new run.",
        file=sys.stderr,
    )
    try:
        with tempfile.TemporaryDirectory(prefix="ankiscape-remote-sync-") as temporary:
            snapshot = Path(temporary) / "source"
            with _measure_phase(timings, "Remote preparation"):
                # The mirror lock wait is untimed; syncing the live tree after it would test
                # whatever the author stashed or edited while the run queued.
                shutil.copytree(
                    local_worktree, snapshot, symlinks=True, copy_function=_copy_file,
                    ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv-qt", "ankiscape_debug.log*"),
                )
                _preflight(args.lane)
            with _hold_mirror_lock():
                with _measure_phase(timings, "Sync"):
                    _sync(snapshot)
                with _measure_phase(timings, "Test execution"):
                    returncode, output = _stream_remote_run(
                        args.lane,
                        timeout=args.timeout,
                        poll_interval=args.poll_interval,
                        selectors=args.select,
                        collect_only=args.collect_only,
                    )
        summary_lines = _validated_summary_lines(args, returncode, output)
    except (OSError, RuntimeError, TimeoutError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        pending_path = _pending_path()
        if pending_path.exists():
            print(f"Unresolved remote run blocks sync; pending record: {pending_path}", file=sys.stderr)
            try:
                pending = json.loads(pending_path.read_text(encoding="utf-8"))
                print(_run_identity(pending), file=sys.stderr)
                read_command = " ".join(
                    shlex.quote(pending[field])
                    for field in ("pid_path", "report_path", "log_path") if field in pending
                )
                print(f"Read-only inspection: {shlex.join((*SSH, f'cat {read_command}'))}", file=sys.stderr)
            except (OSError, ValueError, KeyError, TypeError):
                print("Pending record is unreadable; preserve it for driver reconciliation of the exact run.", file=sys.stderr)
            print(
                "A later run clears this record once the lane's processes are confirmed gone; until "
                "then sync stays blocked. If the run recorded no process group, the driver must "
                "confirm no active worker or in-flight launch before manually clearing the pending "
                "record.",
                file=sys.stderr,
            )
        return 1
    else:
        print("\n".join(summary_lines))
        return 0
    finally:
        _print_phase_timings(timings)


if __name__ == "__main__":
    raise SystemExit(main())
