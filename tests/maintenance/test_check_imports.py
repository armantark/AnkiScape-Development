import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "pass14" / "check_imports.py"
GATE = (Path.home() / "fleet/config/git/hooks/slop_gate.py").resolve()


class PlacementPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(GATE.is_file(), f"Missing installed slop gate: {GATE}")
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.repo = self.root / "repo"
        self.repo.mkdir()
        logic = self.repo / "logic"
        logic.mkdir()
        for number in range(39):
            (logic / f"part_{number}.py").write_text("value = 1\n", encoding="utf-8")
        (logic / "oversized.py").write_text("value = 1\n" * 1001, encoding="utf-8")
        (self.repo / "dep.py").write_text("value = 1\n", encoding="utf-8")
        (self.repo / "origin.py").write_text(
            "import dep\nimport logic.oversized\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        environment = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
        }
        subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "baseline"],
            cwd=self.repo,
            check=True,
            env=environment,
        )

    def _run(self, destination: str, name: str = "report.json"):
        output = self.root / name
        completed = subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "--hook",
                str(GATE),
                "--output",
                str(output),
                "--placement",
                destination,
                "--origin",
                "origin.py",
            ],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
        )
        return completed, json.loads(output.read_text(encoding="utf-8"))

    def test_placement_reports_crowding_line_headroom_and_origin_dependencies(self):
        blocked, report = self._run("logic/new_helper.py")
        self.assertEqual(blocked.returncode, 1, blocked.stdout + blocked.stderr)
        self.assertTrue(report["blocked"])
        self.assertEqual(report["directory"], {
            "path": "logic",
            "head_code_files": 40,
            "current_code_files": 40,
            "proposed_code_files": 41,
            "limit": 40,
            "blocked": True,
        })
        self.assertEqual(
            report["origin_inference"]["eligible_dependencies"],
            ["dep.py", "logic/oversized.py", "origin.py"],
        )
        self.assertIn("cohesive subpackage", report["advice"])

        (self.repo / "logic" / "part_0.py").unlink()
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        replacement, replacement_report = self._run(
            "logic/replacement.py", "replacement.json"
        )
        self.assertEqual(
            replacement.returncode, 0, replacement.stdout + replacement.stderr
        )
        self.assertEqual(replacement_report["directory"]["current_code_files"], 39)
        self.assertEqual(replacement_report["directory"]["proposed_code_files"], 40)
        self.assertFalse(replacement_report["directory"]["blocked"])

        nested, nested_report = self._run("logic/helpers/new_helper.py", "nested.json")
        self.assertEqual(nested.returncode, 0, nested.stdout + nested.stderr)
        self.assertFalse(nested_report["directory"]["blocked"])
        self.assertEqual(nested_report["line_budget"]["remaining_growth"], 1000)

        existing, existing_report = self._run("logic/oversized.py", "existing.json")
        self.assertEqual(existing.returncode, 0, existing.stdout + existing.stderr)
        self.assertEqual(existing_report["line_budget"]["head_lines"], 1001)
        self.assertEqual(existing_report["line_budget"]["current_lines"], 1001)
        self.assertEqual(existing_report["line_budget"]["remaining_growth"], 0)
        self.assertIn("no line-growth headroom", existing_report["advice"])


if __name__ == "__main__":
    unittest.main()
