import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "memory_bank" / "append_record.py"


class AppendRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.path = self.root / "progress.md"

    def _run(self, record: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(TOOL), str(self.path)],
            input=record,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_repeated_appends_normalize_record_boundaries_and_terminal_newline(self):
        for suffix in ("", "\n", "\n\n\n"):
            with self.subTest(suffix=repr(suffix)):
                self.path.write_text("# Progress" + suffix, encoding="utf-8")
                first = self._run("\n## First\n\nCompleted.\n\n")
                second = self._run("## Second\n\nVerified.\n")
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertEqual(
                    self.path.read_text(encoding="utf-8"),
                    "# Progress\n\n## First\n\nCompleted.\n\n## Second\n\nVerified.\n",
                )

    def test_empty_record_is_refused_without_modifying_the_file(self):
        self.path.write_text("# Progress\n", encoding="utf-8")
        before = self.path.read_bytes()

        result = self._run("\n\n")

        self.assertEqual(result.returncode, 2)
        self.assertIn("record must contain non-blank text", result.stderr)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
