#!/usr/bin/env python3
"""Sync an AnkiScape worktree to the MacBook test mirror and run one lane."""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

HOST = "armans-macbook-pro"
REMOTE_HOME = Path("/Users/armantarkhanian")
REMOTE_ROOT = REMOTE_HOME / "ankiscape-remote-test-host"
REMOTE_REPO = REMOTE_ROOT / "repo"
REMOTE_VENV = REMOTE_ROOT / ".venv-qt"
REMOTE_PLAIN_SITE = REMOTE_ROOT / "plain-site"
REMOTE_GAME_MAIN = REMOTE_ROOT / "sources" / "game-main"
REMOTE_DARKAN = REMOTE_ROOT / "sources" / "darkan-world-server"
SSH = ("ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST)
RSYNC_SSH = "ssh -o BatchMode=yes -o ConnectTimeout=10"
MIN_TESTS = 4_144
MAX_PLAIN_SKIPS = 500
MAX_QT_SKIPS = 10
NETWORK_ATTEMPTS = 3


@dataclass(frozen=True)
class TestSummary:
    ran_line: str
    result_line: str
    tests: int
    skipped: int


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
    max_skips = MAX_PLAIN_SKIPS if lane == "plain" else MAX_QT_SKIPS
    if summary.skipped > max_skips:
        lane_label = "Qt" if lane == "qt" else "plain"
        raise RuntimeError(
            f"remote {lane_label} lane false pass: skipped={summary.skipped}, "
            f"expected at most {max_skips}"
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


def _ssh(remote_command: str, *, label: str) -> str:
    return _run_with_retries((*SSH, remote_command), label=label).stdout


def _sync(local_worktree: Path) -> None:
    _ssh(
        f"mkdir -p {shlex.quote(str(REMOTE_REPO))} "
        f"{shlex.quote(str(REMOTE_ROOT / 'reports'))}",
        label="remote mirror setup",
    )
    command = (
        "rsync",
        "-a",
        "--delete",
        "-e",
        RSYNC_SSH,
        "--exclude=.git",
        "--exclude=__pycache__/",
        "--exclude=.venv-qt/",
        "--exclude=ankiscape_debug.log*",
        f"{local_worktree}/",
        f"{HOST}:{REMOTE_REPO}/",
    )
    _run_with_retries(command, label="worktree sync")


def _remote_lane_command(lane: str) -> str:
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
        )
    return (
        environment
        + f"QT_QPA_PLATFORM=offscreen {shlex.quote(str(REMOTE_VENV / 'bin/python'))} "
        + "-m unittest discover tests"
    )


def _preflight(lane: str) -> None:
    common_checks = (
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
            f"test -x {shlex.quote(str(REMOTE_VENV / 'bin/python'))}",
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
    _ssh(" && ".join((*common_checks, *lane_checks)), label=f"remote {lane} prerequisites")


def _stream_remote_run(lane: str, *, timeout: float, poll_interval: float) -> tuple[int, str]:
    run_id = f"{lane}-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    log_path = REMOTE_ROOT / "reports" / f"{run_id}.log"
    report_path = REMOTE_ROOT / "reports" / f"{run_id}.report"
    temporary_report = REMOTE_ROOT / "reports" / f"{run_id}.report.tmp"
    lane_command = _remote_lane_command(lane)
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
        f"rm -f {shlex.quote(str(log_path))} {shlex.quote(str(report_path))} "
        f"{shlex.quote(str(temporary_report))}; "
        f"nohup /bin/sh -c {shlex.quote(script)} </dev/null "
        f"> {shlex.quote(str(log_path))} 2>&1 &"
    )
    _ssh(launch, label="remote lane launch")

    started = time.monotonic()
    seen = ""
    while True:
        output = _ssh(
            f"cat {shlex.quote(str(log_path))} 2>/dev/null || true",
            label="remote lane log poll",
        )
        if output.startswith(seen):
            addition = output[len(seen) :]
        else:
            addition = output
        if addition:
            print(addition, end="", flush=True)
        seen = output

        report = _ssh(
            f"cat {shlex.quote(str(report_path))} 2>/dev/null || true",
            label="remote lane report poll",
        ).strip()
        if report:
            try:
                returncode = int(report)
            except ValueError as exc:
                raise RuntimeError(f"invalid remote lane report {report!r}") from exc
            final_output = _ssh(
                f"cat {shlex.quote(str(log_path))} 2>/dev/null || true",
                label="remote lane final log read",
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("local_worktree", type=Path)
    parser.add_argument("lane", choices=("plain", "qt"))
    parser.add_argument("--timeout", type=float, default=1800.0)
    parser.add_argument("--poll-interval", type=float, default=5.0)
    args = parser.parse_args(argv)

    local_worktree = args.local_worktree.expanduser().resolve()
    if not (local_worktree / "run_tests.py").is_file():
        parser.error(f"not an AnkiScape worktree: {local_worktree}")
    if args.timeout <= 0 or args.poll_interval <= 0:
        parser.error("--timeout and --poll-interval must be positive")

    try:
        _preflight(args.lane)
        _sync(local_worktree)
        returncode, output = _stream_remote_run(
            args.lane,
            timeout=args.timeout,
            poll_interval=args.poll_interval,
        )
        if returncode != 0:
            raise RuntimeError(f"remote {args.lane} lane failed with exit {returncode}")
        summary = parse_unittest_summary(output)
        validate_test_summary(args.lane, summary)
    except (RuntimeError, TimeoutError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Remote {args.lane} lane summary:")
    print(summary.ran_line)
    print(summary.result_line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
