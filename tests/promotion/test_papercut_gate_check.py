import io
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests import test_promotion_gate as promotion_gate
from tools.promotion.snapshot import commit_snapshot
from tools.promotion_gate import _run_gate_checks


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOL = Path("tools/memory_bank/move_papercuts.py")
PAPERCUTS = Path("memory-bank/papercuts.md")
FIXED = Path("memory-bank/papercuts-fixed-2026-09-28.md")


class PapercutGateCheckTest(unittest.TestCase):
    """A candidate branched from main edits the papercut logs; the gate judges its snapshot."""

    def gate_papercuts(self, edit) -> tuple[tuple[str, ...], tuple[str, ...], str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = promotion_gate.PromotionRepo(Path(temp_dir))
            (repo.main / TOOL.parent).mkdir(parents=True)
            shutil.copy(PROJECT_ROOT / TOOL, repo.main / TOOL)
            (repo.main / PAPERCUTS.parent).mkdir()
            (repo.main / PAPERCUTS).write_text("# Papercuts\n\n- open one\n- open two\n", encoding="utf-8")
            (repo.main / FIXED).write_text("# Papercuts fixed\n\n- fixed earlier\n", encoding="utf-8")
            repo.git(repo.main, "add", "tools", "memory-bank")
            repo.git(repo.main, "commit", "-qm", "papercut logs")
            repo.git(repo.target, "merge", "-q", "--no-edit", "main")
            edit(repo.target)
            repo.git(repo.target, "commit", "-qam", "candidate papercut edit")
            log = io.StringIO()
            # The lanes and other audits have their own tests; here only the papercut check runs.
            with (
                commit_snapshot(repo.target, repo.head(repo.target)) as snapshot,
                patch("tools.promotion.lane_execution._run_check_sequence"),
            ):
                passed, failures = _run_gate_checks(
                    snapshot, source_worktree=repo.target, plain_only=True, log=log,
                )
        return passed, failures, log.getvalue()

    def test_entry_both_open_and_fixed_fails_with_the_tool_message(self):
        def archive_without_closing(tree: Path) -> None:
            with (tree / FIXED).open("a", encoding="utf-8") as stream:
                stream.write("- open one\n")

        passed, failures, log = self.gate_papercuts(archive_without_closing)

        self.assertEqual((passed, failures), ((), ("papercuts (exit 1)",)), log)
        self.assertIn("=== papercuts ===\nopen and fixed: open one\nPapercut logs changed unsafely since ", log)

    def test_lost_entry_fails_with_the_tool_message(self):
        def drop_entry(tree: Path) -> None:
            (tree / PAPERCUTS).write_text("# Papercuts\n\n- open one\n", encoding="utf-8")

        passed, failures, log = self.gate_papercuts(drop_entry)

        self.assertEqual((passed, failures), ((), ("papercuts (exit 1)",)), log)
        self.assertIn("=== papercuts ===\nlost: open two\nPapercut logs changed unsafely since ", log)

    def test_entry_moved_to_a_fixed_log_passes(self):
        def close_entry(tree: Path) -> None:
            (tree / PAPERCUTS).write_text("# Papercuts\n\n- open two\n", encoding="utf-8")
            with (tree / FIXED).open("a", encoding="utf-8") as stream:
                stream.write("- open one\n")

        passed, failures, log = self.gate_papercuts(close_entry)

        self.assertEqual((passed, failures), (("papercuts",), ()), log)
        self.assertIn("=== papercuts ===\nNo papercut line lost since ", log)


if __name__ == "__main__":
    unittest.main()
