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

    def test_startup_budget_accepts_under_limit_without_counting_archives(self) -> None:
        root = self._repo()
        for name in ("activeContext", "future-work-kanban", "goal-priority-matrix", "loop-queue", "papercuts"):
            self._track(root, f"memory-bank/{name}.md", "- context\n" * 100)
        self._track(root, "memory-bank/archive/progress-2026-09.md", "history\n" * 4000)
        self._track(root, "memory-bank/progress.md", "progress\n" * 2499)
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/audit_docs.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Documentation audit passed.", result.stdout)

    def test_startup_budget_refuses_at_limit_with_each_file_count(self) -> None:
        root = self._repo()
        counts = {
            "activeContext": 48, "future-work-kanban": 1580, "goal-priority-matrix": 152,
            "loop-queue": 235, "papercuts": 58, "progress": 927,
        }
        for name, count in counts.items():
            self._track(root, f"memory-bank/{name}.md", "- context\n" * count)

        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/audit_docs.py"), "--root", str(root)],
            capture_output=True, text=True,
        )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("3000", result.stdout)
        for name, count in counts.items():
            self.assertIn(f"memory-bank/{name}.md={count}", result.stdout)

    def test_reports_dangling_qualified_test_selectors(self) -> None:
        root = self._repo()
        self._track(
            root,
            "tests/test_example.py",
            "import unittest\n\n"
            "class ExampleTest(unittest.TestCase):\n"
            "    def test_replacement(self):\n"
            "        pass\n",
        )
        self._track(root, "tests/promotion/test_example.py", "def test_promoted():\n    pass\n")
        stale = "tests.test_example.ExampleTest.test_replacement_old"
        missing_module = "tests.promotion.test_missing"
        self._track(
            root,
            "memory-bank/source-audits/example.md",
            "`python3 -m unittest tests.test_example.ExampleTest.test_replacement "
            f"tests.promotion.test_example {stale} {missing_module}`\n",
        )

        report = AUDIT_DOCS.audit_docs(root)

        self.assertEqual(
            [(issue.kind, issue.detail) for issue in report.issues],
            [("dangling_test_selector", stale), ("dangling_test_selector", missing_module)],
        )

    def test_rejects_dated_entries_in_active_context(self) -> None:
        root = self._repo()
        self._track(
            root,
            "memory-bank/activeContext.md",
            "# Active Context\n\n## Current focus — 2026-09-16\n\nok\n\n## Closure — 2026-09-01\n\nold\n",
        )

        report = AUDIT_DOCS.audit_docs(root)

        self.assertEqual([issue.kind for issue in report.issues], ["dated_entry_in_active_context"])
        self.assertEqual(report.issues[0].line, 7)

    def test_rejects_papercut_lines_without_the_bullet(self) -> None:
        root = self._repo()
        self._track(
            root,
            "memory-bank/papercuts.md",
            "# Papercuts\n\n- 2026-09-24T10:00:00-07:00 — ok\n2026-09-24T11:00:00-07:00: bare\n",
        )

        report = AUDIT_DOCS.audit_docs(root)

        self.assertEqual(
            [(issue.kind, issue.line) for issue in report.issues], [("papercut_without_bullet", 4)]
        )

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
