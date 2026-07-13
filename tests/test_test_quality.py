import unittest
from pathlib import Path

from tools.audit_test_quality import audit_test_suite


ROOT = Path(__file__).resolve().parents[1]


class TestTestQuality(unittest.TestCase):
    def test_suite_has_no_mechanically_detectable_slop(self):
        report = audit_test_suite(ROOT / "tests")

        self.assertEqual(report.hard_issues, ())


if __name__ == "__main__":
    unittest.main()
