import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.promotion_gate import (
    GateError,
    LockRecord,
    _create_lock,
    land,
    lock_path_for,
    run_gate,
)


class PromotionRepo:
    def __init__(self, root: Path, *, descendant: bool = True):
        root = root.resolve()
        self.main = root / "addons21" / "ankiscape_fork"
        self.target = root / "ankiscape_worktrees" / "promotion"
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
    def git(repo: Path, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ("git", "-C", str(repo), *args),
            check=True,
            capture_output=True,
            text=True,
            input=input_text,
        )

    def head(self, repo: Path) -> str:
        return self.git(repo, "rev-parse", "HEAD").stdout.strip()

    def write_lock(self, *, pid: int, commit: str, worktree: Path) -> Path:
        path = lock_path_for(self.main)
        _create_lock(
            path,
            LockRecord(
                pid=pid,
                operation="gate",
                worktree=str(worktree),
                commit=commit,
                started_at="2026-08-22T05:00:00-07:00",
                token="test-token",
            ),
        )
        return path


class PromotionGateTest(unittest.TestCase):
    def test_lock_for_another_tree_refuses_landing_and_names_the_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            repo.write_lock(pid=os.getpid(), commit=repo.main_commit, worktree=repo.main)

            with self.assertRaisesRegex(
                GateError,
                rf"^Landing refused: running gate PID {os.getpid()} has held {repo.main_commit} "
                rf"in {repo.main} since 2026-08-22T05:00:00-07:00; requested "
                rf"{repo.target_commit} in {repo.target} is a different tree$",
            ):
                land(repo.target)

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_stale_lock_is_reported_removed_and_does_not_block_landing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            lock_path = repo.write_lock(pid=2_147_483_647, commit=repo.main_commit, worktree=repo.main)
            stderr = io.StringIO()

            landed = land(repo.target, stdout=io.StringIO(), stderr=stderr)

            self.assertEqual(landed, repo.target_commit)
            self.assertEqual(repo.head(repo.main), repo.target_commit)
            self.assertFalse(lock_path.exists())
            self.assertEqual(
                stderr.getvalue(),
                "Stale promotion gate lock: PID 2147483647 is gone; it recorded gate for "
                f"{repo.main_commit} in {repo.main} since 2026-08-22T05:00:00-07:00. "
                f"Removing {lock_path}.\n",
            )

    def test_non_descendant_tree_is_refused_before_git_merge(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir), descendant=False)

            with self.assertRaisesRegex(
                GateError,
                rf"^Landing refused: {repo.target_commit} in {repo.target} is not a descendant "
                rf"of current main {repo.main_commit}$",
            ):
                land(repo.target)

            self.assertEqual(repo.head(repo.main), repo.main_commit)
            self.assertFalse(lock_path_for(repo.main).exists())

    def test_clean_descendant_fast_forwards_main_and_releases_lock(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            stdout = io.StringIO()

            landed = land(repo.target, stdout=stdout)

            self.assertEqual(landed, repo.target_commit)
            self.assertEqual(repo.head(repo.main), repo.target_commit)
            self.assertIn(f"Landed {repo.target_commit}", stdout.getvalue())
            self.assertFalse(lock_path_for(repo.main).exists())

    def test_failed_gate_releases_its_lock(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            with patch("tools.promotion_gate._run_gate_checks", side_effect=GateError("check failed")):
                with self.assertRaisesRegex(GateError, "^check failed$"):
                    run_gate(repo.target, plain_only=True, stdout=io.StringIO())

            self.assertFalse(lock_path_for(repo.main).exists())


if __name__ == "__main__":
    unittest.main()
