import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from run_tests import resolve_selectors, select_tests, selector_suggestions, test_result_exit_code
from tools.run_logged import run_logged
from tools.workflow_manifest_guard import validate_manifest


ROOT = Path(__file__).resolve().parents[1]


class PapercutToolTests(unittest.TestCase):
    def test_runner_anchors_process_cwd_to_its_checkout_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            checkout = temp_root / "Anki2" / "ankiscape_worktrees" / "cwd-fixture"
            tests_dir = checkout / "tests"
            unrelated_cwd = temp_root / "unrelated"
            tests_dir.mkdir(parents=True)
            unrelated_cwd.mkdir()
            shutil.copy2(ROOT / "run_tests.py", checkout / "run_tests.py")
            shutil.copy2(ROOT / "tests/__init__.py", tests_dir / "__init__.py")
            (tests_dir / "test_cwd_probe.py").write_text(
                "import unittest\n"
                "from pathlib import Path\n"
                "\n"
                "\n"
                "class RunnerCwdProbe(unittest.TestCase):\n"
                "    def test_process_cwd_is_fixture_checkout_root(self):\n"
                "        self.assertEqual(Path.cwd(), Path(__file__).resolve().parents[1])\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [sys.executable, str((checkout / "run_tests.py").resolve())],
                cwd=unrelated_cwd,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Ran 1 test", completed.stderr)

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

    def test_focused_runner_refuses_a_fuzzy_module_substitution(self):
        test_ids = [
            "tests.test_main_menu_widget.MainMenuWidgetTest.test_opens",
            "tests.test_runtime_actions.TestRuntimeActions.test_dispatches",
        ]

        resolved, unresolved = resolve_selectors(["MainMenuWidgetTests"], test_ids)

        self.assertEqual(resolved, [])
        self.assertEqual(unresolved, ["MainMenuWidgetTests"])

    def test_focused_runner_refuses_ambiguous_fuzzy_methods(self):
        test_ids = [
            "tests.test_alpha.AlphaTest.test_alpha_one",
            "tests.test_alpha.AlphaTest.test_alpha_two",
        ]

        resolved, unresolved = resolve_selectors(["test_alpha_onf"], test_ids)

        self.assertEqual(resolved, [])
        self.assertEqual(unresolved, ["test_alpha_onf"])

    def test_focused_runner_resolves_a_test_file_path_to_only_its_module(self):
        class CombatTest(unittest.TestCase):
            __module__ = "test_combat"

            def test_routes(self):
                self.assertTrue(True)

        class CombatLogicTest(unittest.TestCase):
            __module__ = "test_combat_logic"

            def test_dispatches(self):
                self.assertTrue(True)

        suite = unittest.TestSuite((CombatTest("test_routes"), CombatLogicTest("test_dispatches")))
        test_ids = [test.id() for test in suite]

        resolved, unresolved = resolve_selectors(["tests/test_combat.py"], test_ids)
        selected, selected_ids = select_tests(suite, resolved)

        self.assertEqual(resolved, ["test_combat."])
        self.assertEqual(unresolved, [])
        self.assertEqual(selected_ids, ["test_combat.PapercutToolTests.test_focused_runner_resolves_a_test_file_path_to_only_its_module.<locals>.CombatTest.test_routes"])
        self.assertEqual(selected.countTestCases(), 1)

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

    def test_repo_search_include_large_reaches_shop_catalogs(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "repo_search.py"),
                "shop_data",
                "data",
                "--names",
                "--include-large",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("data/shop_data.py", completed.stdout.splitlines())

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

    def test_reachability_report_modes_exit_zero_with_or_without_orphans(self):
        from tools import audit_item_reachability

        for orphan_input_count in (0, 2):
            report = {
                "action_count": 17,
                "reachable_item_count": 23,
                "orphan_input_count": orphan_input_count,
                "unresolved_action_count": 5,
                "orphan_inputs": [],
                "root_orphan_leverage": [],
            }
            results = {}
            for args in ((), ("--summary",), ("--json",), ("--json", "--summary"), ("--rank-roots", "1")):
                output = io.StringIO()
                with (
                    patch.object(sys, "argv", ["audit_item_reachability.py", *args]),
                    patch.object(
                        audit_item_reachability,
                        "build_reachability_report",
                        return_value=report,
                    ),
                    redirect_stdout(output),
                ):
                    results[args] = (audit_item_reachability.main(), output.getvalue())

            self.assertEqual(
                results[("--summary",)][1].strip(),
                f"17 actions; 23 reachable items; {orphan_input_count} orphan inputs; 5 blocked actions",
            )
            self.assertEqual({returncode for returncode, _output in results.values()}, {0})

    def test_reachability_check_without_counts_compares_the_tree_pins(self):
        from tools import audit_item_reachability

        report = audit_item_reachability.build_reachability_report()
        pin_source = (ROOT / "tests" / "test_item_reachability_audit.py").read_text(encoding="utf-8")
        blocked = report["unresolved_action_count"]
        pin = f'self.assertEqual(report["unresolved_action_count"], {blocked})'
        self.assertEqual(pin_source.count(pin), 1)

        def run_check(root):
            errors = io.StringIO()
            with (
                patch.object(sys, "argv", ["audit_item_reachability.py", "--check", "--summary"]),
                patch.object(audit_item_reachability, "ROOT", root),
                patch.object(
                    audit_item_reachability,
                    "build_reachability_report",
                    return_value=report,
                ),
                redirect_stdout(io.StringIO()),
                redirect_stderr(errors),
            ):
                return audit_item_reachability.main(), errors.getvalue()

        self.assertEqual(run_check(ROOT), (0, ""))

        with tempfile.TemporaryDirectory() as temp_dir:
            stale_root = Path(temp_dir)
            (stale_root / "tests").mkdir()
            (stale_root / "tests" / "test_item_reachability_audit.py").write_text(
                pin_source.replace(pin, f'self.assertEqual(report["unresolved_action_count"], {blocked + 1})'),
                encoding="utf-8",
            )

            self.assertEqual(
                run_check(stale_root),
                (1, f"unresolved_action_count: expected {blocked + 1}, observed {blocked}\n"),
            )

    def test_reachability_check_mode_requires_and_compares_all_explicit_counts(self):
        from tools import audit_item_reachability

        report = {
            "action_count": 17,
            "reachable_item_count": 23,
            "orphan_input_count": 2,
            "unresolved_action_count": 5,
            "orphan_inputs": [],
            "root_orphan_leverage": [],
        }

        def run_main(*args):
            output = io.StringIO()
            errors = io.StringIO()
            with (
                patch.object(sys, "argv", ["audit_item_reachability.py", *args]),
                patch.object(
                    audit_item_reachability,
                    "build_reachability_report",
                    return_value=report,
                ),
                redirect_stdout(output),
                redirect_stderr(errors),
            ):
                returncode = audit_item_reachability.main()
            return returncode, output.getvalue(), errors.getvalue()

        matching_args = (
            "--json",
            "--check",
            "--actions",
            "17",
            "--reachable-items",
            "23",
            "--orphan-inputs",
            "2",
            "--blocked-actions",
            "5",
        )
        returncode, output, errors = run_main(*matching_args)

        self.assertEqual(returncode, 0)
        self.assertEqual(json.loads(output), report)
        self.assertEqual(errors, "")

        mismatching_args = (
            "--json",
            "--check",
            "--actions",
            "16",
            "--reachable-items",
            "24",
            "--orphan-inputs",
            "1",
            "--blocked-actions",
            "6",
        )
        returncode, output, errors = run_main(*mismatching_args)

        self.assertEqual(returncode, 1)
        self.assertEqual(json.loads(output), report)
        self.assertEqual(
            errors.splitlines(),
            [
                "action_count: expected 16, observed 17",
                "reachable_item_count: expected 24, observed 23",
                "orphan_input_count: expected 1, observed 2",
                "unresolved_action_count: expected 6, observed 5",
            ],
        )

        for option, field, expected, observed in (
            ("--actions", "action_count", 16, 17),
            ("--reachable-items", "reachable_item_count", 24, 23),
            ("--orphan-inputs", "orphan_input_count", 1, 2),
            ("--blocked-actions", "unresolved_action_count", 6, 5),
        ):
            single_mismatch_args = list(matching_args)
            pin_index = single_mismatch_args.index(option) + 1
            single_mismatch_args[pin_index] = str(expected)
            with self.subTest(field=field):
                returncode, output, errors = run_main(*single_mismatch_args)
                self.assertEqual(returncode, 1)
                self.assertEqual(json.loads(output), report)
                self.assertEqual(
                    errors,
                    f"{field}: expected {expected}, observed {observed}\n",
                )

        errors = io.StringIO()
        with (
            patch.object(
                sys,
                "argv",
                ["audit_item_reachability.py", "--check", "--actions", "17"],
            ),
            redirect_stderr(errors),
            self.assertRaises(SystemExit) as raised,
        ):
            audit_item_reachability.main()

        self.assertEqual(raised.exception.code, 2)
        self.assertIn(
            "--check with explicit counts requires --reachable-items, --orphan-inputs, --blocked-actions",
            errors.getvalue(),
        )

    def test_list_truncation_refuses_to_look_complete(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "run_tests.py"),
                "tests/test_papercut_tools.py",
                "--list",
                "--max-results",
                "1",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(len(completed.stdout.splitlines()), 1)
        self.assertIn("Refusing to print", completed.stderr)

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
