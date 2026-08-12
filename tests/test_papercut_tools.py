import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from run_tests import resolve_selectors, select_tests, selector_suggestions, test_result_exit_code
from tools.run_logged import run_logged
from tools.workflow_manifest_guard import validate_manifest


ROOT = Path(__file__).resolve().parents[1]


class PapercutToolTests(unittest.TestCase):
    def test_focused_runner_selects_discovered_ids_without_guessed_attributes(self):
        class AlphaFixture(unittest.TestCase):
            def test_first_branch(self):
                self.assertTrue(True)

        class BetaFixture(unittest.TestCase):
            def test_second_branch(self):
                self.assertTrue(True)

        alpha = AlphaFixture("test_first_branch")
        beta = BetaFixture("test_second_branch")
        suite = unittest.TestSuite((alpha, beta))

        selected, test_ids = select_tests(suite, ["AlphaFixture.test_first"])

        self.assertEqual(test_ids, [alpha.id()])
        self.assertEqual(selected.countTestCases(), 1)
        self.assertIn(
            "AlphaFixture",
            selector_suggestions("AlphaFixtures", [
                alpha.id(),
                beta.id(),
            ]),
        )

    def test_focused_runner_resolves_one_unambiguous_fuzzy_component(self):
        test_ids = [
            "tests.test_main_menu_widget.MainMenuWidgetTest.test_opens",
            "tests.test_runtime_actions.TestRuntimeActions.test_dispatches",
        ]

        resolved, unresolved = resolve_selectors(["MainMenuWidgetTests"], test_ids)

        self.assertEqual(resolved, ["MainMenuWidgetTest"])
        self.assertEqual(unresolved, [])

    def test_focused_runner_refuses_ambiguous_fuzzy_methods(self):
        test_ids = [
            "tests.test_alpha.AlphaTest.test_alpha_one",
            "tests.test_alpha.AlphaTest.test_alpha_two",
        ]

        resolved, unresolved = resolve_selectors(["test_alpha_onf"], test_ids)

        self.assertEqual(resolved, [])
        self.assertEqual(unresolved, ["test_alpha_onf"])

    def test_repo_search_excludes_giant_generated_tables_and_bounds_results(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "data").mkdir()
            (root / "data" / "shop_data.py").write_text("needle\n", encoding="utf-8")
            (root / "data" / "construction_data.py").write_text("needle\n", encoding="utf-8")
            (root / "data" / "source.py").write_text("needle\nneedle\n", encoding="utf-8")
            command = [
                sys.executable,
                str(ROOT / "tools" / "repo_search.py"),
                "needle",
                "data",
                "--max-results",
                "1",
            ]

            completed = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True)

        self.assertEqual(completed.returncode, 2)
        self.assertIn("data/source.py:1:needle", completed.stdout)
        self.assertNotIn("shop_data.py", completed.stdout)
        self.assertNotIn("construction_data.py", completed.stdout)
        self.assertIn("Search stopped at 1 results", completed.stderr)

    def test_repo_search_names_locates_moved_files_without_shell_globs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "logic").mkdir()
            (root / "logic" / "cadence_kernel.py").write_text("", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "repo_search.py"), "cadence", "logic", "--names"],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "logic/cadence_kernel.py")

    def test_logged_runner_preserves_exit_code_and_complete_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            returncode, log_path, tail = run_logged(
                [sys.executable, "-c", "print('before'); print('failure'); raise SystemExit(7)"],
                label="focused check",
                summary_lines=1,
                log_dir=Path(temp_dir),
            )

            self.assertEqual(returncode, 7)
            self.assertEqual(tail, ["failure"])
            self.assertEqual(log_path.read_text(encoding="utf-8"), "before\nfailure\n")

    def test_workflow_preflight_rejects_recorded_schema_mistakes(self):
        manifest = {
            "cwd": str(ROOT),
            "jobs": [{
                "id": "review",
                "prompt": "Review the packet.",
                "mode": "read-only",
                "budget": {"max_tool_calls": 0},
                "output_schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}},
            }],
        }

        errors = validate_manifest(manifest)

        self.assertEqual(len(errors), 3)
        self.assertTrue(any("mode must be 'read' or 'write'" in error for error in errors))
        self.assertTrue(any("max_tool_calls must be an integer of at least 1" in error for error in errors))
        self.assertTrue(any("additionalProperties to false" in error for error in errors))

    def test_workflow_preflight_checks_conditionally_nested_object_schemas(self):
        manifest = {
            "cwd": str(ROOT),
            "jobs": [{
                "id": "review",
                "prompt": "Review the packet.",
                "output_schema": {
                    "if": {"type": "object", "properties": {}},
                    "then": {"type": "object", "additionalProperties": False},
                },
            }],
        }

        self.assertEqual(
            validate_manifest(manifest),
            ["jobs[0].output_schema.if: object schemas must set additionalProperties to false"],
        )

    def test_workflow_preflight_accepts_a_bounded_read_leaf(self):
        manifest = {
            "cwd": str(ROOT),
            "jobs": [{
                "id": "review",
                "prompt": "Review one frozen packet.",
                "mode": "read",
                "budget": {"max_tool_calls": 1, "max_tool_output_bytes": 12000},
                "output_schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"ok": {"type": "boolean"}},
                },
            }],
        }

        self.assertEqual(validate_manifest(manifest), [])

    def test_equipment_generator_supports_documented_direct_invocation(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "generate_equipment_data.py"), "--help"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("external 2011Scape checkout root", completed.stdout)

    def test_ge_generator_direct_invocation_reaches_its_usage_gate(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "generate_ge_period_data.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stderr.strip(), "usage: generate_ge_period_data.py <output-py>")
        self.assertNotIn("No module named 'pkg_alias'", completed.stderr)

    def test_reachability_summary_is_chain_safe_without_hiding_audit_debt(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "audit_item_reachability.py"), "--summary"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertRegex(
            completed.stdout.strip(),
            r"^\d+ actions; \d+ reachable items; \d+ orphan inputs; \d+ blocked actions$",
        )

    def test_list_truncation_succeeds_with_an_explicit_warning(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "run_tests.py"),
                "PapercutToolTests",
                "--list",
                "--max-results",
                "1",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(len(completed.stdout.splitlines()), 1)
        self.assertIn("Showing the first 1 of", completed.stderr)

    def test_quiet_runner_keeps_the_final_summary_without_test_names(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "run_tests.py"),
                "PapercutToolTests.test_logged_runner_preserves_exit_code_and_complete_log",
                "--quiet",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Ran 1 test", completed.stderr)
        self.assertIn("OK", completed.stderr)
        self.assertNotIn("test_logged_runner_preserves_exit_code", completed.stderr)

    def test_focused_runner_does_not_report_an_all_skipped_lane_as_proof(self):
        result = unittest.TestResult()
        result.testsRun = 1
        result.skipped.append((self, "aqt/PyQt6 not installed (use .venv-qt)"))

        self.assertEqual(test_result_exit_code(result, focused=True), 2)
        self.assertEqual(test_result_exit_code(result, focused=False), 0)

        result.errors.append((self, "cleanup failed"))
        self.assertEqual(test_result_exit_code(result, focused=True), 1)


if __name__ == "__main__":
    unittest.main()
