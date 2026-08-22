import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_citation_drift", ROOT / "tools" / "audit_citation_drift.py")
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class CitationDriftAuditTests(unittest.TestCase):
    def _repo(self) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        return root

    def _write(self, root: Path, relative: str, content: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _commit(self, root: Path, message: str) -> None:
        env = os.environ.copy()
        env.update({
            "GIT_AUTHOR_NAME": "Citation test",
            "GIT_AUTHOR_EMAIL": "citation-test@example.invalid",
            "GIT_COMMITTER_NAME": "Citation test",
            "GIT_COMMITTER_EMAIL": "citation-test@example.invalid",
        })
        subprocess.run(["git", "add", "--all"], cwd=root, check=True, env=env)
        subprocess.run(["git", "commit", "-q", "-m", message], cwd=root, check=True, env=env)

    def test_detects_moved_and_gone_targets_without_rewriting_citations(self) -> None:
        root = self._repo()
        self._write(root, "src/live.py", "LIVE = True\n")
        self._write(root, "src/moved.py", "MOVED = 'anchor'\n")
        self._write(root, "src/gone.py", "GONE = 'anchor'\n")
        self._write(root, "src/range.py", "before\nRANGE_A = 1\nRANGE_B = 2\nafter\n")
        record = (
            "# Citations\n\n"
            "- `src/live.py:1`\n"
            "- `src/moved.py:1`\n"
            "- `src/gone.py:1`\n"
            "- `src/range.py:2-3`\n"
        )
        self._write(root, "memory-bank/record.md", record)
        self._commit(root, "Record source citations")

        self._write(root, "src/moved.py", "inserted = True\nMOVED = 'anchor'\n")
        (root / "src/gone.py").unlink()
        self._commit(root, "Move and remove cited targets")

        report = AUDIT.audit_citations(root)

        self.assertEqual(report.citations, 4)
        self.assertEqual(report.resolved, 4)
        self.assertEqual(report.stale, 2)
        by_target = {result.target: result for result in report.results}
        self.assertEqual(by_target["src/live.py:1"].status, "ok")
        self.assertEqual(by_target["src/range.py:2-3"].cited_text, ("RANGE_A = 1", "RANGE_B = 2"))
        self.assertEqual(by_target["src/moved.py:1"].status, "moved")
        self.assertEqual(by_target["src/moved.py:1"].real_target, "src/moved.py:2")
        self.assertEqual(by_target["src/gone.py:1"].status, "missing_file")
        self.assertEqual((root / "memory-bank/record.md").read_text(encoding="utf-8"), record)


if __name__ == "__main__":
    unittest.main()
