import unittest
import tempfile
from pathlib import Path

from tools.audit_test_quality import audit_test_suite


ROOT = Path(__file__).resolve().parents[1]


class TestTestQuality(unittest.TestCase):
    def test_audit_includes_nested_promotion_tests(self):
        source = "import unittest\n\nclass NestedTests(unittest.TestCase):\n    def test_nested(self):\n        self.assertTrue(True)\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            nested = Path(temp_dir) / "promotion"
            nested.mkdir()
            (nested / "test_nested.py").write_text(source, encoding="utf-8")
            report = audit_test_suite(Path(temp_dir))

        self.assertEqual(report.test_files, 1)
        self.assertEqual(report.test_methods, 1)

    def test_suite_has_no_mechanically_detectable_slop(self):
        report = audit_test_suite(ROOT / "tests")

        self.assertEqual(report.hard_issues, ())

    def test_audit_detects_dead_assertion_free_and_source_text_tests(self):
        source = '''
import unittest

def test_dead():
    assert True

class BrokenTests(unittest.TestCase):
    def test_no_assertion(self):
        value = 1

    def test_source_text(self):
        with open("module.py") as file_obj:
            content = file_obj.read()
        self.assertIn("handler_name", content)

class LooksLikeTests:
    def test_dead_method(self):
        assert True

class DerivedTests(BrokenTests):
    def test_inherited_case(self):
        self.assertTrue(True)
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test_broken.py"
            path.write_text(source, encoding="utf-8")
            report = audit_test_suite(Path(temp_dir))

        self.assertEqual(
            {issue.kind for issue in report.hard_issues},
            {
                "undiscovered_test_function",
                "undiscovered_test_method",
                "assertion_free_test",
                "source_text_membership_check",
            },
        )

    def test_audit_tracks_read_values_without_combining_unrelated_expressions(self):
        source = '''
import unittest
from pathlib import Path

class SourceTests(unittest.TestCase):
    def test_direct_path_read(self):
        self.assertIn("handler_name", Path("module.py").read_text())

    def test_assigned_path_read(self):
        content = Path("module.py").read_text()
        assert "handler_name" in content

    def test_unrelated_read_is_not_source_membership(self):
        content = Path("module.py").read_text()
        self.assertIn("handler_name", ["handler_name"])
        self.assertTrue(content)
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test_source.py"
            path.write_text(source, encoding="utf-8")
            report = audit_test_suite(Path(temp_dir))

        source_issues = [
            issue for issue in report.hard_issues
            if issue.kind == "source_text_membership_check"
        ]
        self.assertEqual(len(source_issues), 2)

    def test_audit_detects_exact_duplicates_but_only_reports_constant_clones(self):
        source = '''
import unittest

class DuplicateTests(unittest.TestCase):
    def test_first(self):
        self.assertEqual(1, 1)

    def test_second(self):
        self.assertEqual(1, 1)

class ParameterShapeTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual("alpha", "alpha")

    def test_beta(self):
        self.assertEqual("beta", "beta")
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test_duplicates.py"
            path.write_text(source, encoding="utf-8")
            report = audit_test_suite(Path(temp_dir))

        exact = [issue for issue in report.hard_issues if issue.kind == "exact_duplicate_test"]
        self.assertEqual(len(exact), 2)
        self.assertEqual(len(report.structural_clones), 2)

    def test_identical_bodies_in_distinct_fixtures_are_review_candidates_only(self):
        source = '''
import unittest

class FirstFixture(unittest.TestCase):
    def test_contract(self):
        self.assertEqual(self.value, 1)

class SecondFixture(unittest.TestCase):
    def test_contract(self):
        self.assertEqual(self.value, 1)
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test_fixtures.py"
            path.write_text(source, encoding="utf-8")
            report = audit_test_suite(Path(temp_dir))

        self.assertFalse(any(
            issue.kind == "exact_duplicate_test" for issue in report.hard_issues
        ))
        self.assertEqual(len(report.structural_clones), 1)


if __name__ == "__main__":
    unittest.main()
