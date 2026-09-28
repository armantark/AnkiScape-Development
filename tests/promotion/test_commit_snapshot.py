import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.test_promotion_gate import PromotionRepo
from tools import run_remote_tests
from tools.promotion.lane_execution import _run_bounded
from tools.promotion.snapshot import commit_snapshot
from tools.promotion_gate import GateError, evidence_path_for, run_gate


PROBE = """\
from pathlib import Path
import sys
value = (Path(sys.argv[1]) / 'state.txt').read_text()
print('consumed: ' + value.strip())
raise SystemExit(0 if value == 'passing\\n' else 1)
"""


class CommitSnapshotTest(unittest.TestCase):
    def run_with_transient_edit(self, repo, *, remote_lanes):
        source = repo.target / "state.txt"
        committed = source.read_text(encoding="utf-8")
        self.checked_roots = []

        def execute(command, **options):
            if command[0] == "git":
                return _run_bounded(command, **options)
            if "worktree_guard.py" in command[1]:
                return subprocess.CompletedProcess(command, 0, "layout checked\n", ""), False
            root = command[2] if "run_remote_tests.py" in command[1] else options["worktree"]
            self.checked_roots.append(Path(root))
            source.write_text("passing\n", encoding="utf-8")
            try:
                return _run_bounded((sys.executable, "-c", PROBE, str(root)), **options)
            finally:
                source.write_text(committed, encoding="utf-8")

        # Replace expensive workloads, retaining real gate dispatch, subprocess reads,
        # source restoration, final Git checks and receipt creation.
        with (
            patch("tools.promotion.lane_execution._run_bounded", side_effect=execute),
            patch("tools.promotion.lane_execution._run_reachability_check", return_value=0),
            patch.object(run_remote_tests, "LOCAL_MIRROR_LOCK_PATH", repo.root / "mirror.lock"),
        ):
            return run_gate(
                repo.target, plain_only=False, remote_lanes=remote_lanes, stdout=io.StringIO(),
            )

    def test_transient_live_edit_cannot_certify_a_failing_commit(self):
        for remote_lanes in (False, True):
            with self.subTest(remote_lanes=remote_lanes), tempfile.TemporaryDirectory() as temp:
                repo = PromotionRepo(Path(temp))
                with self.assertRaisesRegex(GateError, r"plain lane \(exit 1\)"):
                    self.run_with_transient_edit(repo, remote_lanes=remote_lanes)
                self.assertFalse(evidence_path_for(repo.target, repo.target_commit).exists())
                self.assertEqual(repo.git(repo.target, "status", "--porcelain").stdout, "")
                self.assertEqual(repo.head(repo.target), repo.target_commit)
                self.assertEqual(len(set(self.checked_roots)), 1)
                self.assertNotEqual(self.checked_roots[0], repo.target)
                self.assertFalse(self.checked_roots[0].exists())

    def passing_repo(self, root):
        repo = PromotionRepo(root)
        (repo.target / "state.txt").write_text("passing\n", encoding="utf-8")
        repo.git(repo.target, "add", "state.txt")
        repo.git(repo.target, "commit", "-qm", "passing fixture")
        repo.target_commit = repo.head(repo.target)
        return repo

    def test_snapshot_pass_writes_receipt_for_original_commit_and_cleans_up(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = self.passing_repo(Path(temp))
            self.run_with_transient_edit(repo, remote_lanes=True)
            self.assertTrue(evidence_path_for(repo.target, repo.target_commit).exists())
            self.assertEqual(len(set(self.checked_roots)), 1)
            self.assertNotEqual(self.checked_roots[0], repo.target)
            self.assertFalse(self.checked_roots[0].exists())

    def test_original_untracked_file_still_refuses_a_passing_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = self.passing_repo(Path(temp))
            (repo.target / "untracked.txt").write_text("not committed\n", encoding="utf-8")
            with self.assertRaisesRegex(GateError, r"worktree clean \(exit 1\)"):
                self.run_with_transient_edit(repo, remote_lanes=False)
            self.assertFalse(evidence_path_for(repo.target, repo.target_commit).exists())

    def test_snapshot_ignores_staged_and_untracked_edits(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = PromotionRepo(Path(temp))
            (repo.target / "state.txt").write_text("staged edit\n", encoding="utf-8")
            repo.git(repo.target, "add", "state.txt")
            (repo.target / "untracked.txt").write_text("local only\n", encoding="utf-8")
            with commit_snapshot(repo.target, repo.target_commit) as snapshot:
                self.assertEqual((snapshot / "state.txt").read_text(), "promotion\n")
                self.assertFalse((snapshot / "untracked.txt").exists())
                self.assertEqual(repo.head(snapshot), repo.target_commit)
                self.assertEqual((snapshot / ".venv-qt").resolve(), repo.main / ".venv-qt")
            self.assertFalse(snapshot.exists())
            self.assertEqual(
                repo.git(repo.target, "show", ":state.txt").stdout, "staged edit\n",
            )


if __name__ == "__main__":
    unittest.main()
