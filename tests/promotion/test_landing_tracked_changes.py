import io
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.test_promotion_gate import PromotionRepo, pass_gate
from tools.promotion_gate import FULL_GATE_CHECKS, GateError, _git, land, run_gate


class LandingTrackedChangesTest(unittest.TestCase):
    def test_landing_onto_tracked_canonical_changes_is_refused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            target, target_commit = repo.add_target("candidate")
            with patch(
                "tools.promotion.lane_execution._run_gate_checks",
                return_value=(FULL_GATE_CHECKS, ()),
            ):
                run_gate(target, plain_only=False, stdout=io.StringIO())
            (repo.main / "state.txt").write_text("untested\n", encoding="utf-8")
            (repo.main / "untracked.md").write_text("orchestrator note\n", encoding="utf-8")

            with self.assertRaisesRegex(
                GateError,
                r"^Landing refused: canonical checkout has uncommitted tracked changes:\n"
                r" M state\.txt$",
            ):
                land(target)

            self.assertEqual(repo.head(repo.main), repo.main_commit)
            (repo.main / "state.txt").write_text("main\n", encoding="utf-8")
            self.assertEqual(land(target, stdout=io.StringIO()), target_commit)
            self.assertEqual(repo.head(repo.main), target_commit)

    def test_tracked_change_made_during_the_merge_fails_the_landing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            pass_gate(repo)

            def merge_then_edit(path: Path, *args: str, **kwargs):
                result = _git(path, *args, **kwargs)
                if args[0] == "merge":
                    (repo.main / "state.txt").write_text("edited\n", encoding="utf-8")
                return result

            with patch("tools.promotion.landing._git", side_effect=merge_then_edit):
                with self.assertRaisesRegex(
                    GateError,
                    rf"^Landing of {repo.target_commit} moved main, but canonical checkout "
                    rf"{re.escape(str(repo.main))} gained uncommitted tracked changes "
                    r"during the merge:\n M state\.txt$",
                ):
                    land(repo.target, stdout=io.StringIO())

            self.assertEqual(repo.head(repo.main), repo.target_commit)


if __name__ == "__main__":
    unittest.main()
