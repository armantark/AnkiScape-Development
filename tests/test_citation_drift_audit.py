import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "audit_citation_drift.py"
SPEC = importlib.util.spec_from_file_location("audit_citation_drift", SCRIPT)
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

    def test_classifies_every_reported_result_without_rewriting_records(self) -> None:
        root = self._repo()
        self._write(root, "src/live.py", "LIVE = True\n")
        self._write(root, "src/moved.py", "MOVED = 'anchor'\n")
        self._write(root, "src/changed.py", "VALUE = 'before'\n")
        self._write(root, "src/short.py", "first\nSECOND = True\n")
        self._write(root, "src/gone.py", "GONE = 'anchor'\n")
        record = (
            "# Citations\n\n"
            "- `src/live.py:1`\n"
            "- `src/moved.py:1`\n"
            "- `src/changed.py:1`\n"
            "- `src/short.py:2`\n"
            "- `src/gone.py:1`\n"
            "- `vendor/source.java:1`\n"
        )
        self._write(root, "memory-bank/record.md", record)
        self._commit(root, "Record source citations")

        self._write(root, "src/moved.py", "inserted = True\nMOVED = 'anchor'\n")
        self._write(root, "src/changed.py", "VALUE = 'after'\n")
        self._write(root, "src/short.py", "first\n")
        (root / "src/gone.py").unlink()
        self._commit(root, "Change cited targets")

        report = AUDIT.audit_citations(root)

        self.assertEqual(report.citations, 6)
        self.assertEqual(report.resolved, 5)
        self.assertEqual(report.actionable, 3)
        self.assertEqual(report.changed, 1)
        self.assertEqual(report.unpinned_external_issues, 0)
        self.assertEqual(report.unresolved, 1)
        by_target = {result.target: result for result in report.results}
        self.assertEqual(by_target["src/live.py:1"].status, "ok")
        self.assertEqual(by_target["src/moved.py:1"].status, "moved")
        self.assertEqual(by_target["src/moved.py:1"].real_target, "src/moved.py:2")
        self.assertEqual(by_target["src/changed.py:1"].status, "changed")
        self.assertEqual(by_target["src/changed.py:1"].origin_text, ("VALUE = 'before'",))
        self.assertEqual(by_target["src/changed.py:1"].cited_text, ("VALUE = 'after'",))
        self.assertEqual(by_target["src/short.py:2"].status, "missing_lines")
        self.assertEqual(by_target["src/gone.py:1"].status, "missing_file")
        self.assertEqual(by_target["vendor/source.java:1"].status, "unresolved")
        self.assertEqual((root / "memory-bank/record.md").read_text(encoding="utf-8"), record)

    def test_unpinned_external_mismatch_is_not_actionable_drift(self) -> None:
        root = self._repo()
        external = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self._write(external, "vendor.py", "only one line\n")
        self._write(root, "memory-bank/record.md", "`vendor.py:2`\n")
        self._commit(root, "Record unpinned external citation")

        report = AUDIT.audit_citations(
            root,
            external_filesystems=(AUDIT.ExternalRepository("vendor", external),),
        )

        self.assertEqual(report.actionable, 0)
        self.assertEqual(report.unpinned_external_issues, 1)
        self.assertEqual(report.results[0].status, "missing_lines")

    def test_direct_path_list_includes_oxford_and(self) -> None:
        citations = tuple(AUDIT._line_citations(
            "data/hunter_data.py:394, 428, 764, 818, 971, and 1003",
            AUDIT.BARE_CITATION_RE,
        ))

        self.assertEqual(
            citations,
            tuple(("data/hunter_data.py", line, line) for line in (394, 428, 764, 818, 971, 1003)),
        )

    def test_detects_split_path_and_line_list_markers(self) -> None:
        root = self._repo()
        original_lines = (394, 428, 764, 818, 971, 1003)
        moved_lines = (402, 436, 772, 826, 989, 1021)

        def source(marker_lines: tuple[int, ...]) -> str:
            lines = [f"filler {line}" for line in range(1, max(marker_lines) + 1)]
            for index, line in enumerate(marker_lines):
                lines[line - 1] = f"MARKER_{index} = True"
            return "\n".join(lines) + "\n"

        self._write(root, "data/hunter_data.py", source(original_lines))
        record = (
            "The rows are registered in `data/hunter_data.py`. The six known\n"
            "omissions have adjacent markers at lines 394, 428, 764, 818, 971,\n"
            "and 1003.\n"
        )
        self._write(root, "memory-bank/record.md", record)
        self._commit(root, "Record split marker citations")
        self._write(root, "data/hunter_data.py", source(moved_lines))
        self._commit(root, "Move marker lines")

        report = AUDIT.audit_citations(root)

        self.assertEqual(report.citations, 6)
        self.assertEqual(report.actionable, 6)
        by_target = {result.target: result for result in report.results}
        for original, moved in zip(original_lines, moved_lines, strict=True):
            result = by_target[f"data/hunter_data.py:{original}"]
            self.assertEqual(result.status, "moved")
            self.assertEqual(result.real_target, f"data/hunter_data.py:{moved}")

    def test_split_parser_ignores_dotted_identifiers(self) -> None:
        root = self._repo()
        self._write(
            root,
            "memory-bank/record.md",
            "`json.decoder.JSONDecodeError: Extra data: line 1 column 6`\n"
            "`FarmPatch.setInitialLives()` sets lives at lines 377-393.\n"
            "Only `Objs.ANVIL` has a check at lines 14-17.\n",
        )
        self._commit(root, "Record diagnostic prose")

        report = AUDIT.audit_citations(root)

        self.assertEqual(report.citations, 0)

    def test_output_cannot_overwrite_a_source_record(self) -> None:
        root = self._repo()
        self._write(root, "src/live.py", "LIVE = True\n")
        record = "# Citation\n\n`src/live.py:1`\n"
        self._write(root, "memory-bank/record.md", record)
        self._commit(root, "Record source citation")

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(root),
                "--no-default-sources",
                "--output",
                "memory-bank/record.md",
                "--limit",
                "0",
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("--output cannot overwrite citation source record", result.stderr)
        self.assertEqual((root / "memory-bank/record.md").read_text(encoding="utf-8"), record)


if __name__ == "__main__":
    unittest.main()
