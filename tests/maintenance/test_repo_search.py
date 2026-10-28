"""CLI proofs for case selection and complete, bounded search output.

Failure modes: mixed-case hits are missed, aggregate output exceeds its budget,
or a clipped result falsely reports a complete successful search.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOL = Path(__file__).resolve().parents[2] / "tools" / "repo_search.py"


class RepoSearchOutputTests(unittest.TestCase):
    def test_case_insensitive_search_is_explicit(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.py"
            source.write_text("MixedCase\n", encoding="utf-8")
            command = [sys.executable, str(TOOL), "mixedcase", str(source)]
            sensitive = subprocess.run(command, capture_output=True, text=True)
            insensitive = subprocess.run([*command, "-i"], capture_output=True, text=True)
        self.assertEqual(sensitive.returncode, 1, sensitive.stderr)
        self.assertEqual(insensitive.returncode, 0, insensitive.stderr)
        self.assertIn("MixedCase", insensitive.stdout)

    def test_aggregate_output_counts_path_prefixes_and_refuses_incomplete_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.py"
            source.write_text("needle\n" * 20, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(TOOL), "needle", str(source), "--max-chars", "200"],
                capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("needle", result.stdout)
        self.assertLessEqual(len(result.stdout), 200)
        self.assertIn("Output stopped at 200 characters", result.stderr)

    def test_line_ranges_obey_the_same_aggregate_output_budget(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.py"
            source.write_text("x" * 100 + "\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(TOOL), "--line-range", str(source), "1", "1", "--max-chars", "20"],
                capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("Output stopped at 20 characters", result.stderr)
