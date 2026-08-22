import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from tools.promotion_gate import (
    FULL_GATE_CHECKS,
    PLAIN_GATE_CHECKS,
    REACHABILITY_BASELINE_SUMMARY,
    GateError,
    LockRecord,
    _reachability_result_is_pinned,
    _run_check,
    _worktree_is_clean,
    active_gate_dir_for,
    active_gate_records,
    evidence_path_for,
    claim_landing_lock,
    land,
    register_gate,
    run_gate,
)


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


def pass_gate(repo: PromotionRepo, *, plain_only: bool = False) -> Path:
    checks = PLAIN_GATE_CHECKS if plain_only else FULL_GATE_CHECKS
    with patch("tools.promotion_gate._run_gate_checks", return_value=(checks, ())):
        run_gate(repo.target, plain_only=plain_only, stdout=io.StringIO())
    return evidence_path_for(repo.target, repo.target_commit)


class PromotionGateTest(unittest.TestCase):
    def test_landing_without_a_passed_gate_is_refused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            evidence_path = evidence_path_for(repo.target, repo.target_commit)

            with self.assertRaisesRegex(
                GateError,
                rf"^Landing refused: no passed full-gate evidence for exact commit "
                rf"{repo.target_commit} at {evidence_path}$",
            ):
                land(repo.target)

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_plain_only_gate_records_checks_but_does_not_authorize_landing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            evidence_path = pass_gate(repo, plain_only=True)
            payload = json.loads(evidence_path.read_text(encoding="utf-8"))

            self.assertEqual(payload["commit"], repo.target_commit)
            self.assertEqual(tuple(payload["passed_checks"]), PLAIN_GATE_CHECKS)
            with self.assertRaisesRegex(
                GateError,
                rf"^Landing refused: evidence for {repo.target_commit} did not pass every "
                rf"full-gate check; recorded {re.escape(str(PLAIN_GATE_CHECKS))}$",
            ):
                land(repo.target)

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_running_gate_for_same_commit_cannot_land_early(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            marker = register_gate(repo.target, repo.target_commit)
            try:
                with self.assertRaisesRegex(
                    GateError,
                    rf"^Landing refused: gate PID {os.getpid()} is still running for exact "
                    rf"commit {repo.target_commit} in {repo.target} since ",
                ):
                    land(repo.target)
            finally:
                marker.release()

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_duplicate_gate_for_exact_commit_is_refused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            first = register_gate(repo.target, repo.target_commit)
            try:
                with self.assertRaisesRegex(
                    GateError,
                    rf"^Gate already running for exact commit {repo.target_commit}: PID "
                    rf"{os.getpid()} in {repo.target} since ",
                ):
                    register_gate(repo.target, repo.target_commit)
            finally:
                first.release()

    def test_gate_registration_waits_for_landing_coordination(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            landing_lock = claim_landing_lock(
                repo.target,
                operation="landing",
                worktree=repo.target,
                commit=repo.target_commit,
            )
            result = {}

            def register() -> None:
                try:
                    result["marker"] = register_gate(repo.target, repo.target_commit)
                except Exception as exc:  # pragma: no cover - asserted through result
                    result["error"] = exc

            thread = threading.Thread(target=register)
            thread.start()
            try:
                thread.join(timeout=0.1)
                self.assertTrue(thread.is_alive())
            finally:
                landing_lock.release()
                thread.join(timeout=5)

            self.assertFalse(thread.is_alive())
            self.assertNotIn("error", result)
            result["marker"].release()

    def test_second_landing_is_refused_while_landing_lock_is_held(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            landing_lock = claim_landing_lock(
                repo.target,
                operation="landing",
                worktree=repo.target,
                commit=repo.target_commit,
            )
            try:
                with self.assertRaisesRegex(
                    GateError,
                    rf"^Promotion landing lock held: PID {os.getpid()} is landing for "
                    rf"{repo.target_commit} in {repo.target} since ",
                ):
                    land(repo.target)
            finally:
                landing_lock.release()

    def test_independent_worktrees_can_register_gates_concurrently(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            other_target, other_commit = repo.add_target("promotion-b")
            first = register_gate(repo.target, repo.target_commit)
            second = None
            try:
                second = register_gate(other_target, other_commit)
                active = active_gate_records(repo.main, stderr=io.StringIO())
                self.assertEqual(
                    {record.commit for record in active},
                    {repo.target_commit, other_commit},
                )
            finally:
                if second is not None:
                    second.release()
                first.release()

    def test_gate_for_another_tree_refuses_landing_and_names_the_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            pass_gate(repo)
            marker = register_gate(repo.main, repo.main_commit)
            try:
                with self.assertRaisesRegex(
                    GateError,
                    rf"^Landing refused: running gate PID {os.getpid()} has held "
                    rf"{repo.main_commit} in {repo.main} since .*; requested "
                    rf"{repo.target_commit} in {repo.target} is a different tree$",
                ):
                    land(repo.target)
            finally:
                marker.release()

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_unlocked_marker_with_live_unrelated_pid_is_stale(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            pass_gate(repo)
            sleeper = subprocess.Popen(
                (sys.executable, "-c", "import time; time.sleep(30)"),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            try:
                marker_path = repo.write_unlocked_gate_marker(
                    pid=sleeper.pid,
                    commit=repo.main_commit,
                    worktree=repo.main,
                )
                stderr = io.StringIO()

                landed = land(repo.target, stdout=io.StringIO(), stderr=stderr)

                self.assertEqual(landed, repo.target_commit)
                self.assertEqual(repo.head(repo.main), repo.target_commit)
                self.assertFalse(marker_path.exists())
                self.assertIsNone(sleeper.poll())
                self.assertIn(
                    f"Stale promotion gate marker: it recorded gate PID {sleeper.pid}",
                    stderr.getvalue(),
                )
            finally:
                sleeper.terminate()
                sleeper.wait(timeout=5)

    def test_non_descendant_tree_is_refused_before_git_merge(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir), descendant=False)
            pass_gate(repo)

            with self.assertRaisesRegex(
                GateError,
                rf"^Landing refused: {repo.target_commit} in {repo.target} is not a descendant "
                rf"of current main {repo.main_commit}$",
            ):
                land(repo.target)

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_passed_full_gate_fast_forwards_main(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            evidence_path = pass_gate(repo)
            payload = json.loads(evidence_path.read_text(encoding="utf-8"))
            stdout = io.StringIO()

            landed = land(repo.target, stdout=stdout)

            self.assertEqual(payload["commit"], repo.target_commit)
            self.assertEqual(tuple(payload["passed_checks"]), FULL_GATE_CHECKS)
            self.assertFalse(payload["plain_only"])
            self.assertEqual(landed, repo.target_commit)
            self.assertEqual(repo.head(repo.main), repo.target_commit)
            self.assertIn(f"Landed {repo.target_commit}", stdout.getvalue())

    def test_failed_rerun_removes_prior_landable_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            evidence_path = pass_gate(repo)
            self.assertTrue(evidence_path.exists())

            with patch(
                "tools.promotion_gate._run_gate_checks",
                return_value=(("plain lane",), ("audit_docs (exit 1)",)),
            ):
                with self.assertRaisesRegex(
                    GateError,
                    r"^Gate failed: audit_docs \(exit 1\)\. Log: ",
                ):
                    run_gate(repo.target, plain_only=False, stdout=io.StringIO())

            self.assertFalse(evidence_path.exists())
            self.assertEqual(active_gate_records(repo.main, stderr=io.StringIO()), ())
            with self.assertRaisesRegex(GateError, "no passed full-gate evidence"):
                land(repo.target)

    def test_dirty_worktree_fails_clean_commit_check(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            (repo.target / "untracked.txt").write_text("not in the commit\n", encoding="utf-8")
            log = io.StringIO()

            returncode = _run_check(
                log,
                heading="=== worktree clean ===",
                command=("git", "status", "--porcelain", "--untracked-files=all"),
                worktree=repo.target,
                selector=lambda lines: lines or ["clean"],
                validator=_worktree_is_clean,
            )

            self.assertEqual(returncode, 1)
            self.assertIn("?? untracked.txt", log.getvalue())
            self.assertTrue(log.getvalue().endswith("FAILED: exit 0\n"))

    def test_reachability_accepts_only_the_exact_pinned_exit_one(self):
        log = io.StringIO()

        returncode = _run_check(
            log,
            heading="=== reachability ===",
            command=(
                sys.executable,
                "-c",
                f"print({REACHABILITY_BASELINE_SUMMARY!r}); raise SystemExit(1)",
            ),
            worktree=Path.cwd(),
            selector=lambda lines: [
                line for line in lines if line == REACHABILITY_BASELINE_SUMMARY
            ][-1:],
            validator=_reachability_result_is_pinned,
        )

        self.assertEqual(returncode, 0)
        self.assertEqual(
            log.getvalue(),
            f"=== reachability ===\n{REACHABILITY_BASELINE_SUMMARY}\n",
        )

    def test_reachability_rejects_a_crash_after_the_pinned_summary(self):
        log = io.StringIO()

        returncode = _run_check(
            log,
            heading="=== reachability ===",
            command=(
                sys.executable,
                "-c",
                f"print({REACHABILITY_BASELINE_SUMMARY!r}); raise RuntimeError('audit crashed')",
            ),
            worktree=Path.cwd(),
            selector=lambda lines: [
                line for line in lines if line == REACHABILITY_BASELINE_SUMMARY
            ][-1:],
            validator=_reachability_result_is_pinned,
        )

        self.assertEqual(returncode, 1)
        self.assertEqual(
            log.getvalue(),
            f"=== reachability ===\n{REACHABILITY_BASELINE_SUMMARY}\nFAILED: exit 1\n",
        )

    def test_reachability_rejects_different_or_missing_summary(self):
        cases = (
            "0 actions; 0 reachable items; 999 orphan inputs; 999 blocked actions",
            "audit produced no summary",
        )
        for output in cases:
            with self.subTest(output=output):
                log = io.StringIO()
                returncode = _run_check(
                    log,
                    heading="=== reachability ===",
                    command=(
                        sys.executable,
                        "-c",
                        f"print({output!r}); raise SystemExit(1)",
                    ),
                    worktree=Path.cwd(),
                    selector=lambda lines: [
                line for line in lines if line == REACHABILITY_BASELINE_SUMMARY
            ][-1:],
                    validator=_reachability_result_is_pinned,
                )
                self.assertEqual(returncode, 1)
                self.assertTrue(log.getvalue().endswith("FAILED: exit 1\n"))


if __name__ == "__main__":
    unittest.main()
