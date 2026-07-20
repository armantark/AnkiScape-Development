import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_docs", ROOT / "tools" / "audit_docs.py")
assert SPEC and SPEC.loader
AUDIT_DOCS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT_DOCS
SPEC.loader.exec_module(AUDIT_DOCS)


class DocumentationAuditTests(unittest.TestCase):
    def _repo(self) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        return root

    def _track(self, root: Path, relative: str, content: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", "--", relative], cwd=root, check=True)

    def test_accepts_valid_tracked_markdown_and_html(self) -> None:
        root = self._repo()
        self._track(root, "docs/target.md", "# Target\n")
        self._track(root, "README.md", "# Docs\n\n[Target](docs/target.md)\n\n```text\nok\n```\n")
        self._track(root, "report.html", "<!doctype html><html><body>ok</body></html>\n")

        report = AUDIT_DOCS.audit_docs(root)

        self.assertTrue(report.ok, report.issues)
        self.assertEqual((report.markdown_files, report.html_files), (2, 1))

    def test_reports_broken_links_and_unclosed_fences(self) -> None:
        root = self._repo()
        self._track(root, "README.md", "# Docs\n\n[Missing](docs/missing.md)\n\n```text\n")

        report = AUDIT_DOCS.audit_docs(root)

        self.assertEqual({issue.kind for issue in report.issues}, {"broken_local_link", "unclosed_fence"})

    def test_ignores_links_inside_code_fences_and_external_paths(self) -> None:
        root = self._repo()
        self._track(
            root,
            "README.md",
            "# Docs\n\n```markdown\n[Example](missing.md)\n```\n\n"
            "[Outside repo](/private/tmp/evidence.md)\n"
            "[Runtime Help topic](help:skills#choosing-training)\n",
        )

        self.assertTrue(AUDIT_DOCS.audit_docs(root).ok)

    def test_reports_html_nesting_doctype_and_trailing_whitespace(self) -> None:
        root = self._repo()
        self._track(root, "report.html", "<html><body><div>bad</p> \n</body></html>\n")

        report = AUDIT_DOCS.audit_docs(root)

        self.assertEqual(
            {issue.kind for issue in report.issues},
            {"invalid_html_nesting", "missing_doctype", "trailing_whitespace", "unclosed_html_element"},
        )

    def test_reports_missing_local_html_resources(self) -> None:
        root = self._repo()
        self._track(
            root,
            "report.html",
            "<!doctype html><html><body><img src=\"missing.png\"></body></html>\n",
        )

        report = AUDIT_DOCS.audit_docs(root)

        self.assertEqual([(issue.kind, issue.detail) for issue in report.issues], [("broken_html_target", "missing.png")])

    def test_ignores_staged_paths_removed_during_a_move(self) -> None:
        root = self._repo()
        self._track(root, "old.md", "# Old location\n")
        (root / "old.md").unlink()
        (root / "archive").mkdir()
        (root / "archive" / "old.md").write_text("# Archived\n", encoding="utf-8")

        report = AUDIT_DOCS.audit_docs(root)

        self.assertTrue(report.ok, report.issues)
        self.assertEqual(report.markdown_files, 1)


if __name__ == "__main__":
    unittest.main()
