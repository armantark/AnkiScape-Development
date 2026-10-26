import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from tools import run_remote_tests
from tools.promotion.promotion_process import open_locked_file
from tools.promotion_gate import (
    FULL_GATE_CHECKS,
    PLAIN_GATE_CHECKS,
    GateError,
    GateEvidence,
    LockRecord,
    _run_gate_checks,
    _run_reachability_check,
    _run_check,
    _worktree_is_clean,
    active_gate_dir_for,
    active_gate_records,
    evidence_path_for,
    landing_lock_path_for,
    claim_landing_lock,
    land,
    main as promotion_main,
    register_gate,
    run_gate,
)
from tools.reachability.pins import read_reachability_pins


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_ACTION_FIELDS = ("action_count", "reachable_item_count")


def copy_reachability_tree(destination: Path) -> Path:
    shutil.copytree(
        PROJECT_ROOT,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )
    return destination.resolve()


def copy_running_gate(worktree: Path) -> Path:
    """Give a candidate the running gate's code, so the gate judges it in-process."""
    shutil.copytree(
        PROJECT_ROOT / "tools",
        worktree / "tools",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    return worktree.resolve()


def run_reachability_check(worktree: Path) -> tuple[int, str]:
    log = io.StringIO()
    returncode = _run_reachability_check(log, worktree)
    return returncode, log.getvalue()


def reachability_summary(pins: dict[str, int]) -> str:
    return (
        f"{pins['action_count']} actions; {pins['reachable_item_count']} reachable items; "
        f"{pins['orphan_input_count']} orphan inputs; "
        f"{pins['unresolved_action_count']} blocked actions"
    )


def pinned_summary(worktree: Path) -> str:
    return reachability_summary(read_reachability_pins(worktree))


def synthetic_reachability_tree(
    destination: Path,
    *,
    update_pins: bool,
) -> tuple[Path, str]:
    worktree = copy_reachability_tree(destination)
    action_path = worktree / "data" / "thieving_data.py"
    with action_path.open("a", encoding="utf-8") as stream:
        stream.write(
            '\nTHIEVING_TARGETS["promotion_gate_synthetic"] = {\n'
            '    "guaranteed": {"Promotion gate synthetic item": 1},\n'
            '}\n'
        )

    pins = read_reachability_pins(worktree)
    expected_pins = dict(pins)
    for field in SYNTHETIC_ACTION_FIELDS:
        expected_pins[field] += 1
    if update_pins:
        pin_path = worktree / "tests" / "reachability/test_report_baseline.py"
        source = pin_path.read_text(encoding="utf-8")
        for field in SYNTHETIC_ACTION_FIELDS:
            old = f'self.assertEqual(report["{field}"], {pins[field]})'
            new = f'self.assertEqual(report["{field}"], {expected_pins[field]})'
            if source.count(old) != 1:
                raise AssertionError(f"Expected one synthetic pin target: {old}")
            source = source.replace(old, new, 1)
        pin_path.write_text(source, encoding="utf-8")
    return worktree, reachability_summary(expected_pins)


class PromotionRepo:
    def __init__(self, root: Path, *, descendant: bool = True):
        self.root = root.resolve()
        self.main = self.root / "addons21" / "ankiscape_fork"
        self.target = self.root / "ankiscape_worktrees" / "promotion"
        self.main.mkdir(parents=True)
        self.git(self.main, "init", "-q", "-b", "main")
        (self.main / "state.txt").write_text("main\n", encoding="utf-8")
        self.git(self.main, "add", "state.txt")
        self.git(self.main, "commit", "-q", "-m", "main")
        self.main_commit = self.head(self.main)

        if descendant:
            self.git(self.main, "branch", "promotion")
            self.git(self.main, "worktree", "add", "-q", str(self.target), "promotion")
            (self.target / "state.txt").write_text("promotion\n", encoding="utf-8")
            self.git(self.target, "add", "state.txt")
            self.git(self.target, "commit", "-q", "-m", "promotion")
        else:
            tree = self.git(self.main, "mktree", input_text="").stdout.strip()
            unrelated = self.git(
                self.main,
                "commit-tree",
                tree,
                input_text="unrelated\n",
            ).stdout.strip()
            self.git(self.main, "branch", "promotion", unrelated)
            self.git(self.main, "worktree", "add", "-q", str(self.target), "promotion")
        self.target_commit = self.head(self.target)

    @staticmethod
    def git(
        repo: Path,
        *args: str,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ("git", "-C", str(repo), *args),
            check=True,
            capture_output=True,
            text=True,
            input=input_text,
        )

    def head(self, repo: Path) -> str:
        return self.git(repo, "rev-parse", "HEAD").stdout.strip()

    def add_target(self, name: str) -> tuple[Path, str]:
        target = self.root / "ankiscape_worktrees" / name
        self.git(self.main, "worktree", "add", "-q", "-b", name, str(target), "main")
        (target / f"{name}.txt").write_text(f"{name}\n", encoding="utf-8")
        self.git(target, "add", f"{name}.txt")
        self.git(target, "commit", "-q", "-m", name)
        return target.resolve(), self.head(target)

    def write_unlocked_gate_marker(
        self,
        *,
        pid: int,
        commit: str,
        worktree: Path,
    ) -> Path:
        directory = active_gate_dir_for(self.main)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "unlocked-stale.json"
        record = LockRecord(
            pid=pid,
            operation="gate",
            worktree=str(worktree.resolve()),
            commit=commit,
            started_at="2026-08-22T05:00:00-07:00",
            token="unlocked-stale",
        )
        path.write_text(json.dumps(asdict(record)) + "\n", encoding="utf-8")
        return path


def pass_gate(
    repo: PromotionRepo,
    *,
    plain_only: bool = False,
    remote_lanes: bool = False,
) -> Path:
    checks = PLAIN_GATE_CHECKS if plain_only else FULL_GATE_CHECKS
    with patch("tools.promotion.lane_execution._run_gate_checks", return_value=(checks, ())):
        run_gate(
            repo.target,
            plain_only=plain_only,
            remote_lanes=remote_lanes,
            stdout=io.StringIO(),
        )
    return evidence_path_for(repo.target, repo.target_commit)


if __name__ == "__main__":
    unittest.main()
