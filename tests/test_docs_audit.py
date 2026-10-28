import hashlib
import importlib.util
import json
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

    def test_startup_budget_accepts_under_limit_without_counting_archives_or_papercuts(self) -> None:
        root = self._repo()
        for name in ("activeContext", "future-work-kanban", "goal-priority-matrix", "loop-queue"):
            self._track(root, f"memory-bank/{name}.md", "- context\n" * 100)
        self._track(root, "memory-bank/papercuts.md", "- papercut\n" * 799)
        self._track(root, "memory-bank/archive/progress-2026-09.md", "history\n" * 4000)
        self._track(root, "memory-bank/progress.md", "progress\n" * 2599)
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/audit_docs.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Documentation audit passed.", result.stdout)

    def test_startup_budget_refuses_at_limit_with_each_file_count(self) -> None:
        root = self._repo()
        counts = {
            "activeContext": 48, "future-work-kanban": 1638, "goal-priority-matrix": 152,
            "loop-queue": 235, "progress": 927,
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

    def test_papercuts_refuse_at_their_own_cap(self) -> None:
        root = self._repo()
        self._track(root, "memory-bank/papercuts.md", "- papercut\n" * 800)

        report = AUDIT_DOCS.audit_docs(root)

        self.assertEqual(
            [(issue.kind, issue.path, issue.detail) for issue in report.issues],
            [("papercuts_line_cap_exceeded", "memory-bank/papercuts.md", "800 papercut lines must stay under 800")],
        )

    def test_rejects_papercut_lines_without_the_bullet(self) -> None:
        root = self._repo()
        self._track(
            root,
            "memory-bank/papercuts.md",
            "# Papercuts\n> Header note.\n\n- 2026-09-24T10:00:00-07:00 — ok\n2026-09-24T11:00:00-07:00: bare\n",
        )

        report = AUDIT_DOCS.audit_docs(root)

        self.assertEqual(
            [(issue.kind, issue.line) for issue in report.issues], [("papercut_without_bullet", 5)]
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

    def test_status_artifacts_use_only_the_publish_preflight(self) -> None:
        root = self._repo()
        self._track(root, "memory-bank/status-updates/plan.html", '<video src="plan.mp4">\n')
        self._track(root, "memory-bank/status-updates/notes.md", "[Missing](missing.md)\n")
        self._track(
            root, "docs/status-updates/report.html",
            '<!doctype html><html><body><img src="missing.png"></body></html>\n',
        )

        report = AUDIT_DOCS.audit_docs(root)

        self.assertEqual(
            {(issue.kind, issue.path) for issue in report.issues},
            {("broken_local_link", "memory-bank/status-updates/notes.md"),
             ("broken_html_target", "docs/status-updates/report.html")},
        )
        self.assertEqual((report.markdown_files, report.html_files), (1, 1))

    def test_ignores_staged_paths_removed_during_a_move(self) -> None:
        root = self._repo()
        self._track(root, "old.md", "# Old location\n")
        (root / "old.md").unlink()
        (root / "archive").mkdir()
        (root / "archive" / "old.md").write_text("# Archived\n", encoding="utf-8")

        report = AUDIT_DOCS.audit_docs(root)

        self.assertTrue(report.ok, report.issues)
        self.assertEqual(report.markdown_files, 1)

    def _capture(self, root: Path, local: str = "sources/capture.html") -> dict:
        package = root / "data/quest/evidence/example"
        path = package / local
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = b'<html><body>original  \r\n<a href="old-relative.html">page</a></body></html>'
        path.write_bytes(raw)
        return {"id": "capture", "local": local, "url": "https://example.org/old",
                "sha256": hashlib.sha256(raw).hexdigest(), "saved_bytes": len(raw)}

    def _index(self, root: Path, records: object) -> Path:
        index = root / "data/quest/evidence/example/source-index.json"
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(json.dumps(records), encoding="utf-8")
        return index

    def test_indexed_raw_captures_preserve_bytes_without_authored_rules(self) -> None:
        root = self._repo()
        html = self._capture(root)
        markdown = self._capture(root, "sources/original.md")
        markdown.update(id="markdown", path="archive/original.md")
        del markdown["url"]
        path = root / "data/quest/evidence/example/sources/original.md"
        raw = b'[Old](missing-page.md)\r\n \t\r\n```unfinished'
        path.write_bytes(raw)
        markdown.update(sha256=hashlib.sha256(raw).hexdigest(), saved_bytes=len(raw))
        self._index(root, [html, markdown, dict(html)])
        originals = {record["local"]: (path.parent.parent / record["local"]).read_bytes()
                     for record in (html, markdown)}

        report = AUDIT_DOCS.audit_docs(root)

        self.assertTrue(report.ok, report.issues)
        for local, expected in originals.items():
            self.assertEqual((path.parent.parent / local).read_bytes(), expected)

    def test_capture_tampering_length_and_missing_files_fail_explicitly(self) -> None:
        for mutation, expected in (("hash", "capture_hash_mismatch"),
                                   ("length", "capture_size_mismatch"),
                                   ("missing", "missing_capture")):
            with self.subTest(mutation=mutation):
                root = self._repo()
                record = self._capture(root)
                self._index(root, [record])
                path = root / "data/quest/evidence/example" / record["local"]
                raw = path.read_bytes()
                if mutation == "hash":
                    path.write_bytes(raw.replace(b"original", b"tampered"))
                elif mutation == "length":
                    path.write_bytes(raw + b"\n")
                else:
                    path.unlink()
                issues = AUDIT_DOCS.audit_docs(root).issues
                self.assertIn(expected, {issue.kind for issue in issues}, issues)
                self.assertTrue(any(issue.path.endswith(record["local"]) for issue in issues))

    def test_capture_registration_rejects_malformed_bindings_and_provenance(self) -> None:
        changes = ({"sha256": "bad"}, {"sha256": None}, {"saved_bytes": -1},
                   {"saved_bytes": True}, {"saved_bytes": "72"}, {"saved_bytes": None},
                   {"url": ""}, {"url": "relative.html"}, {"url": []},
                   {"url": "https://"}, {"url": "https://example.org/has space"},
                   {"url": None, "path": ""}, {"url": None, "path": {}},
                   {"url": None, "path": "\n"}, {"url": None}, {"local": None})
        for change in changes:
            with self.subTest(change=change):
                root = self._repo()
                record = self._capture(root)
                record.update(change)
                if record.get("url") is None:
                    record.pop("url")
                self._index(root, [record])
                issues = AUDIT_DOCS.audit_docs(root).issues
                self.assertIn("invalid_capture_record", {issue.kind for issue in issues}, issues)

    def test_capture_indexes_require_a_list_of_records_and_valid_json(self) -> None:
        for value in ({"local": "sources/capture.html"}, [None], ["capture"], None):
            with self.subTest(value=value):
                root = self._repo()
                self._index(root, value)
                self.assertIn("invalid_capture_index",
                              {issue.kind for issue in AUDIT_DOCS.audit_docs(root).issues})
        root = self._repo()
        self._index(root, []).write_bytes(b"[")
        self.assertIn("invalid_capture_index",
                      {issue.kind for issue in AUDIT_DOCS.audit_docs(root).issues})

    def test_capture_paths_must_be_canonical_and_strictly_under_sources(self) -> None:
        for local in ("evidence.md", "README.md", "sources", "sources/../evidence.md",
                      "../outside.md", "/tmp/outside.md", "sources//capture.html",
                      "sources/./capture.html", "sources\\capture.html",
                      "sources/capture.html/", "sources/\x00capture.html"):
            with self.subTest(local=local):
                root = self._repo()
                record = self._capture(root)
                record["local"] = local
                self._index(root, [record])
                self.assertIn("invalid_capture_record",
                              {issue.kind for issue in AUDIT_DOCS.audit_docs(root).issues})

    def test_capture_symlinks_are_refused_at_each_path_component(self) -> None:
        for component in ("capture.html", "sources", "example", "source-index.json"):
            with self.subTest(component=component):
                root = self._repo()
                record = self._capture(root)
                index = self._index(root, [record])
                package = index.parent
                path = {"capture.html": package / record["local"],
                        "sources": package / "sources", "example": package,
                        "source-index.json": index}[component]
                target = path.with_name(path.name + "-original")
                path.rename(target)
                path.symlink_to(target, target_is_directory=target.is_dir())
                issues = AUDIT_DOCS.audit_docs(root).issues
                self.assertIn("capture_symlink", {issue.kind for issue in issues}, issues)

    def test_conflicting_capture_local_paths_and_ids_are_refused(self) -> None:
        for change in ({"sha256": "0" * 64}, {"saved_bytes": 1},
                       {"url": "https://different.example/old"},
                       {"local": "sources/second.html"}):
            with self.subTest(change=change):
                root = self._repo()
                record = self._capture(root)
                other = dict(record, **change)
                self._index(root, [record, other])
                issues = AUDIT_DOCS.audit_docs(root).issues
                self.assertIn("conflicting_capture_identity", {issue.kind for issue in issues}, issues)

    def test_registry_cannot_exempt_authored_or_unregistered_documentation(self) -> None:
        root = self._repo()
        record = self._capture(root)
        self._index(root, [record])
        for relative in ("data/quest/evidence/example/evidence.md",
                         "data/quest/evidence/example/README.md",
                         "data/quest/evidence/example/sources/unregistered.md",
                         "memory-bank/source-audits/canonical.md", "README.md"):
            self._track(root, relative, "[Broken](missing.md)\n")
        issues = AUDIT_DOCS.audit_docs(root).issues
        self.assertEqual(len(issues), 5, issues)
        self.assertEqual({issue.kind for issue in issues}, {"broken_local_link"})
        # An index outside the exact package boundary never exempts prose.
        (root / "source-index.json").write_text(json.dumps([record]), encoding="utf-8")
        self.assertEqual(AUDIT_DOCS.audit_docs(root).issues, issues)


if __name__ == "__main__":
    unittest.main()
