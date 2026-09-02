import io
import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from tests.test_promotion_gate import PromotionRepo
from tools.promotion import landing_freeze_hook
from tools.promotion.landing_freeze_hook import check
from tools.promotion_gate import (
    LockRecord,
    _write_record,
    claim_landing_lock,
    install_hook,
)
from tools.worktree_guard import audit, landing_freeze_hook_installed


class LandingFreezeHookTest(unittest.TestCase):
    def test_live_lock_refuses_only_canonical_main_and_names_ruling(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            lock = claim_landing_lock(
                repo.main,
                operation="running a gate",
                worktree=repo.target,
                commit=repo.target_commit,
            )
            try:
                stderr = io.StringIO()
                result = check(repo.main, stderr=stderr)
            finally:
                lock.release()
            self.assertEqual(result, 1)
            message = stderr.getvalue()
            self.assertIn(repo.target_commit, message)
            self.assertIn(f"PID {lock.record.pid}", message)
            self.assertIn("memory-bank/pending/", message)

    def test_live_lock_does_not_block_goal_worktree(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            lock = claim_landing_lock(
                repo.main,
                operation="running a gate",
                worktree=repo.target,
                commit=repo.target_commit,
            )
            try:
                with patch.object(landing_freeze_hook, "_git_branch", return_value="goal/slice"):
                    self.assertEqual(check(repo.target, stderr=io.StringIO()), 0)
            finally:
                lock.release()

    def test_dead_pid_lock_allows_main_and_reports_staleness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            lock = claim_landing_lock(
                repo.main,
                operation="running a gate",
                worktree=repo.target,
                commit=repo.target_commit,
            )
            try:
                _write_record(
                    lock.stream,
                    replace(lock.record, pid=99999999, heartbeat_at="2020-01-01T00:00:00+00:00"),
                )
                stderr = io.StringIO()
                self.assertEqual(check(repo.main, stderr=stderr), 0)
            finally:
                lock.release()
            self.assertIn("Landing freeze stale", stderr.getvalue())

    def test_no_lock_leaves_main_untouched(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            stderr = io.StringIO()
            self.assertEqual(check(repo.main, stderr=stderr), 0)
            self.assertEqual(stderr.getvalue(), "")

    def test_audit_requires_hook_only_in_canonical_checkout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            (repo.main / "meta.json").write_text(
                json.dumps({"name": "AnkiScape RuneScape Anki"}), encoding="utf-8"
            )
            missing = subprocess.run(
                ("python3", "tools/worktree_guard.py", "--repo", str(repo.main), "audit"),
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertIn("landing freeze hook missing", missing.stdout)
            linked = io.StringIO()
            with patch("sys.stdout", linked):
                audit(repo.target)
            self.assertNotIn("landing freeze hook missing", linked.getvalue())
            install_hook(repo.main)
            self.assertTrue(landing_freeze_hook_installed(repo.main))
            present = io.StringIO()
            with patch("sys.stdout", present):
                audit(repo.main)
            self.assertNotIn("landing freeze hook missing", present.getvalue())


if __name__ == "__main__":
    unittest.main()
