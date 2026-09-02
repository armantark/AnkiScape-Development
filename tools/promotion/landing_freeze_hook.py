#!/usr/bin/env python3
"""Refuse canonical-main commits while a promotion gate is making progress."""

from __future__ import annotations

import argparse
import fcntl
import sys
from pathlib import Path

from tools.promotion_gate import (
    LONGEST_LANE_TIMEOUT,
    _read_record_path,
    _record_age,
    landing_lock_path_for,
    main_worktree,
)
from tools.promotion.promotion_process import format_age, kill_process_tree, pid_is_alive


RULING_38 = (
    "During an open window, write ledger sections, papercuts, briefs and "
    "harvests as new untracked files under memory-bank/pending/, then fold "
    "them into their tracked homes in one path-scoped commit after the land."
)


def _git_branch(repo: Path) -> str:
    import subprocess

    result = subprocess.run(
        ("git", "-C", str(repo), "symbolic-ref", "--quiet", "--short", "HEAD"),
        check=False,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _contended_lock_refuses(path: Path, *, stderr) -> bool:
    try:
        record = _read_record_path(path)
    except FileNotFoundError:
        return False
    age = _record_age(record)
    if not pid_is_alive(record.pid) or age > LONGEST_LANE_TIMEOUT:
        print(
            f"Landing freeze stale after {format_age(age)} for {record.commit} "
            f"(PID {record.pid}); allowing commit.",
            file=stderr,
        )
        if pid_is_alive(record.pid):
            kill_process_tree(record.pid)
        return False
    print(
        f"Commit refused: promotion gate holds {record.commit} (PID {record.pid}) "
        f"for {format_age(age)}. {RULING_38}",
        file=stderr,
    )
    return True


def check(repo: Path, *, stderr=sys.stderr) -> int:
    repo = repo.resolve()
    if _git_branch(repo) != "main" or repo != main_worktree(repo):
        return 0
    path = landing_lock_path_for(repo)
    try:
        stream = path.open("r+", encoding="utf-8")
    except FileNotFoundError:
        return 0
    try:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return int(_contended_lock_refuses(path, stderr=stderr))
        record = _read_record_path(path)
        age = _record_age(record)
        if not pid_is_alive(record.pid) or age > LONGEST_LANE_TIMEOUT:
            print(
                f"Landing freeze stale after {format_age(age)} for {record.commit} "
                f"(PID {record.pid}); allowing commit.",
                file=stderr,
            )
        return 0
    finally:
        stream.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    return check(args.repo)


if __name__ == "__main__":
    raise SystemExit(main())
