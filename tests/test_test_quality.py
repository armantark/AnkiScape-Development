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
                "vacuous_source_scan",
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

    def test_audit_resolves_local_imported_test_case_bases_without_whitelisting(self):
        harness = '''
import unittest

class ImportedCase(unittest.TestCase):
    pass

class OrdinaryBase:
    pass

class TestCase:
    pass
'''
        cyclic = '''
class Left(Right):
    pass

class Right(Left):
    pass
'''
        relative = '''
from .harness import ImportedCase as RelativeCase

class RelativeTests(RelativeCase):
    def test_relative(self):
        self.assertTrue(True)
'''
        aliases = '''
import harness as support
from package import harness as package_support
from unittest import TestCase as Case

class AliasTests(support.ImportedCase):
    def test_alias(self):
        self.assertTrue(True)

class PackageAliasTests(package_support.ImportedCase):
    def test_package_alias(self):
        self.assertTrue(True)

class StdlibAliasTests(Case):
    def test_stdlib_alias(self):
        self.assertTrue(True)
'''
        unknown = '''
from harness import OrdinaryBase as UnknownBase
from harness import TestCase as ShadowedTestCase
from cyclic import Left
from package import unittest as shadowed_unittest
from unavailable_harness import MissingBase
from unittest import TestCase as ReboundCase
import unittest as rebound_unittest

class ReboundCase:
    pass

rebound_unittest = object()

class OrdinaryImportTests(UnknownBase):
    def test_ordinary_import(self):
        self.assertTrue(True)

class MissingImportTests(MissingBase):
    def test_missing_import(self):
        self.assertTrue(True)

class ShadowedImportTests(ShadowedTestCase):
    def test_shadowed_import(self):
        self.assertTrue(True)

class CyclicImportTests(Left):
    def test_cyclic_import(self):
        self.assertTrue(True)

class ShadowedModuleTests(shadowed_unittest.TestCase):
    def test_shadowed_module(self):
        self.assertTrue(True)

class ReboundClassTests(ReboundCase):
    def test_rebound_class(self):
        self.assertTrue(True)

class ReboundModuleTests(rebound_unittest.TestCase):
    def test_rebound_module(self):
        self.assertTrue(True)
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package = root / "package"
            package.mkdir()
            (root / "harness.py").write_text(harness, encoding="utf-8")
            (root / "cyclic.py").write_text(cyclic, encoding="utf-8")
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "harness.py").write_text(harness, encoding="utf-8")
            (package / "unittest.py").write_text("class TestCase:\n    pass\n", encoding="utf-8")
            (package / "test_relative.py").write_text(relative, encoding="utf-8")
            (root / "test_aliases.py").write_text(aliases, encoding="utf-8")
            (root / "test_unknown.py").write_text(unknown, encoding="utf-8")
            report = audit_test_suite(root)

        undiscovered = {
            issue.name
            for issue in report.hard_issues
            if issue.kind == "undiscovered_test_method"
        }
        self.assertEqual(
            undiscovered,
            {
                "OrdinaryImportTests.test_ordinary_import",
                "MissingImportTests.test_missing_import",
                "ShadowedImportTests.test_shadowed_import",
                "CyclicImportTests.test_cyclic_import",
                "ShadowedModuleTests.test_shadowed_module",
                "ReboundClassTests.test_rebound_class",
                "ReboundModuleTests.test_rebound_module",
            },
        )
        self.assertEqual(report.test_methods, 4)

    def test_audit_uses_package_relative_and_dotted_import_bindings(self):
        ordinary = "class ImportedCase:\n    pass\n"
        test_case = "import unittest\nclass ImportedCase(unittest.TestCase):\n    pass\n"
        package_export = "from .harness import ImportedCase\nclass ExportedCase(ImportedCase):\n    pass\n"
        cases = (
            ("relative genuine", test_case, ordinary, package_export,
             "from tests.package import ExportedCase", "ExportedCase", 1),
            ("relative ordinary", ordinary, test_case, package_export,
             "from tests.package import ExportedCase", "ExportedCase", 0),
            ("dotted genuine", test_case, ordinary, ordinary,
             "import package.harness", "package.harness.ImportedCase", 1),
            ("dotted root ordinary", test_case, ordinary, ordinary,
             "import package.harness", "package.ImportedCase", 0),
            ("dotted alias", test_case, ordinary, ordinary,
             "import package.harness as support", "support.ImportedCase", 1),
        )
        for label, harness, root_harness, package_init, imports, base, count in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                (root / "package").mkdir()
                sources = {
                    "harness.py": root_harness,
                    "package/harness.py": harness,
                    "package/__init__.py": package_init,
                    "test_consumer.py": (
                        f"{imports}\nclass ConsumerTests({base}):\n"
                        "    def test_consumer(self):\n        self.assertTrue(True)\n"
                    ),
                }
                for name, source in sources.items():
                    (root / name).write_text(source, encoding="utf-8")
                report = audit_test_suite(root)

                self.assertEqual(report.test_methods, count)
                self.assertEqual(
                    [issue.kind for issue in report.hard_issues],
                    [] if count else ["undiscovered_test_method"],
                )

    def test_audit_does_not_parse_unrelated_fixture_sources(self):
        source = (
            "import unittest\nimport invalid_syntax\n"
            "class ConsumerTests(unittest.TestCase):\n"
            "    def test_consumer(self):\n        self.assertTrue(True)\n"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "test_consumer.py").write_text(source, encoding="utf-8")
            (root / "invalid_syntax.py").write_text("def broken(", encoding="utf-8")
            (root / "invalid_encoding.py").write_bytes(bytes([255]))
            report = audit_test_suite(root)

        self.assertEqual(report.test_methods, 1)
        self.assertEqual(report.hard_issues, ())

    def test_audit_resolves_stdlib_paths_and_rejects_dynamic_or_rebound_bases(self):
        cases = (
            ("stdlib dotted", "import unittest.case", "unittest.case.TestCase", 1),
            ("stdlib module alias", "import unittest.case as cases", "cases.TestCase", 1),
            ("stdlib class alias", "from unittest.case import TestCase as Base", "Base", 1),
            ("stdlib reexport", "from unittest import case", "case.TestCase", 1),
            ("undefined", "", "Unknown", 0),
            ("dynamic", "import unittest", "factory()", 0),
            ("local rebound", "import unittest\nclass Base(unittest.TestCase):\n    pass\nBase = object()", "Base", 0),
            ("conditional rebound", "from unittest import TestCase as Base\nif flag:\n    Base = object()", "Base", 0),
            ("function rebound", "from unittest import TestCase as Base\ndef Base():\n    pass", "Base", 0),
            ("star rebound", "from unittest import TestCase as Base\nfrom external import *", "Base", 0),
        )
        for label, imports, base, count in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                (root / "test_consumer.py").write_text(
                    f"{imports}\nclass ConsumerTests({base}):\n"
                    "    def test_consumer(self):\n        self.assertTrue(True)\n",
                    encoding="utf-8",
                )
                report = audit_test_suite(root)

                self.assertEqual(report.test_methods, count)
                self.assertEqual(len(report.hard_issues), 1 - count)

    def test_audit_does_not_confuse_local_unittest_with_the_stdlib(self):
        source = (
            "import unittest\nclass ConsumerTests(unittest.TestCase):\n"
            "    def test_consumer(self):\n        self.assertTrue(True)\n"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "unittest.py").write_text("class TestCase:\n    pass\n", encoding="utf-8")
            (root / "test_consumer.py").write_text(source, encoding="utf-8")
            report = audit_test_suite(root)

        self.assertEqual(report.test_methods, 0)
        self.assertEqual(
            [(issue.kind, issue.name) for issue in report.hard_issues],
            [("undiscovered_test_method", "ConsumerTests.test_consumer")],
        )

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
