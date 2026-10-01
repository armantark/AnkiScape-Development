import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("audit_docs_rotation", ROOT / "tools" / "audit_docs.py")
assert SPEC and SPEC.loader
AUDIT_DOCS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT_DOCS
SPEC.loader.exec_module(AUDIT_DOCS)

TRIAGE = "## 2026-09-23 — Papercut triage finished\n\nMoved 56 lines; the no-loss check passed.\n\n"
GATE = "## 2026-09-24 — Gate lanes skip the mirror queue\n\nBoth lanes passed.\n\n"
PARALLEL = "## 2026-09-23 — Papercut triage finished\n\nThe parallel record from the second seat.\n\n"


class ProgressRotationAuditTests(unittest.TestCase):
    def test_reports_a_section_the_rotation_copied_twice_but_not_a_parallel_record(self) -> None:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        archive = root / "memory-bank" / "archive" / "progress-2026-09.md"
        archive.parent.mkdir(parents=True)
        # A same-heading entry with a different body is a kept parallel record, not a repeat.
        archive.write_text("# Progress, September 2026\n\n" + TRIAGE + GATE + PARALLEL + TRIAGE + GATE, encoding="utf-8")
        subprocess.run(["git", "add", "--all"], cwd=root, check=True)

        report = AUDIT_DOCS.audit_docs(root)

        repeats = [(issue.kind, issue.line, issue.detail) for issue in report.issues]
        self.assertEqual(repeats, [
            ("repeated_progress_section", 15, "## 2026-09-23 — Papercut triage finished repeats line 3"),
            ("repeated_progress_section", 19, "## 2026-09-24 — Gate lanes skip the mirror queue repeats line 7"),
        ])


if __name__ == "__main__":
    unittest.main()
