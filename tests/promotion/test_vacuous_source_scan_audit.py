import tempfile
import unittest
from pathlib import Path

from tools.audit_test_quality import audit_test_suite


class VacuousSourceScanAuditTest(unittest.TestCase):
    def _audit(self, source):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test_source_scan.py"
            path.write_text(source, encoding="utf-8")
            return audit_test_suite(Path(temp_dir))

    def test_module_file_scan_requires_a_non_empty_result_assertion(self):
        source = '''
import ast
import unittest
from pathlib import Path
from package import sample_module

class SourceScanTests(unittest.TestCase):
    def test_mappings(self):
        annotation: int
        module = ast.parse(Path(sample_module.__file__).read_text())
        mappings = [
            node for node in module.body
            if isinstance(node, ast.AnnAssign)
        ]
        all_named = all(mapping.target for mapping in mappings)
        self.assertTrue(all_named)
        for mapping in mappings:
            self.assertTrue(mappings)
            self.assertIsNotNone(mapping.target)
'''
        report = self._audit(source)
        issues = [
            issue for issue in report.hard_issues
            if issue.kind == "vacuous_source_scan"
        ]
        self.assertEqual(
            [(issue.line, issue.name) for issue in issues],
            [(10, "SourceScanTests.test_mappings")],
        )

        protected = source.replace(
            "        for mapping in mappings:\n",
            "        self.assertTrue(mappings)\n        for mapping in mappings:\n",
        )
        protected_report = self._audit(protected)
        self.assertFalse(any(
            issue.kind == "vacuous_source_scan"
            for issue in protected_report.hard_issues
        ))

    def test_literal_source_paths_are_detected_and_exact_keys_protect_them(self):
        source = '''
import ast
import unittest
from pathlib import Path

class SourceScanTests(unittest.TestCase):
    def test_path_literal(self):
        module = ast.parse(Path("data/catalog.py").read_text())
        names = {node.name for node in module.body if isinstance(node, ast.ClassDef)}
        for name in names:
            self.assertTrue(name.endswith("Definition"))

    def test_open_literal(self):
        with open("data/catalog.py") as source_file:
            content = source_file.read()
        module = ast.parse(content)
        names = {node.name for node in module.body if isinstance(node, ast.ClassDef)}
        self.assertEqual(names, {"ExpectedDefinition"})
'''
        report = self._audit(source)
        issues = [
            issue.name for issue in report.hard_issues
            if issue.kind == "vacuous_source_scan"
        ]
        self.assertEqual(issues, ["SourceScanTests.test_path_literal"])

    def test_own_file_repository_locator_is_not_a_source_scan(self):
        source = '''
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class RepositoryRootTests(unittest.TestCase):
    def test_root(self):
        module = ast.parse(Path(__file__).read_text())
        classes = [node for node in module.body if isinstance(node, ast.ClassDef)]
        for class_node in classes:
            self.assertTrue(class_node.name.endswith("Tests"))
'''
        report = self._audit(source)

        self.assertFalse(any(
            issue.kind == "vacuous_source_scan"
            for issue in report.hard_issues
        ))


if __name__ == "__main__":
    unittest.main()
