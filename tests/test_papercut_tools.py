import io
import itertools
import json
import os
import shutil
import struct
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
DEFINITION_JAVA = Path(os.environ.get("JAVA_BIN", "/opt/homebrew/opt/openjdk@25/bin/java"))
DEFINITION_JAVAC = Path(os.environ.get("JAVAC_BIN", "/opt/homebrew/opt/openjdk@25/bin/javac"))
DEFINITION_GRADLE_CACHE = Path(os.environ.get("GRADLE_CACHE", Path.home() / ".gradle/caches/modules-2/files-2.1"))


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

    def test_focused_runner_matches_whole_dotted_names_before_fragments(self):
        modules = (
            "tests.test_achievement_diaries",
            "tests.test_achievement_diaries_ui",
            "tests.test_achievement_diaries_integration",
            "tests.promotion.test_gate_lock_claim",
        )
        suite = unittest.TestSuite(
            type("Case", (unittest.TestCase,), {"__module__": module, "test_it": lambda self: None})("test_it")
            for module in modules
        )
        test_ids = [test.id() for test in suite]
        expected_by_selector = {
            "test_achievement_diaries": ["tests.test_achievement_diaries.Case.test_it"],
            "tests.test_achievement_diaries": ["tests.test_achievement_diaries.Case.test_it"],
            "test_achievement_diaries.": ["tests.test_achievement_diaries.Case.test_it"],
            "tests.promotion.test_gate_lock_claim": ["tests.promotion.test_gate_lock_claim.Case.test_it"],
            "promotion.test_gate_lock_claim": ["tests.promotion.test_gate_lock_claim.Case.test_it"],
            "diaries_ui": ["tests.test_achievement_diaries_ui.Case.test_it"],
        }
        for selector, expected in expected_by_selector.items():
            with self.subTest(selector=selector):
                resolved, unresolved = resolve_selectors([selector], test_ids)
                _selected, selected_ids = select_tests(suite, resolved)

                self.assertEqual(unresolved, [])
                self.assertEqual(selected_ids, expected)

    def test_runner_refuses_a_test_id_discovered_twice(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = Path(temp_dir) / "duplicate-fixture"
            tests_dir = checkout / "tests"
            tests_dir.mkdir(parents=True)
            shutil.copy2(ROOT / "run_tests.py", checkout / "run_tests.py")
            shutil.copy2(ROOT / "tests/__init__.py", tests_dir / "__init__.py")
            (tests_dir / "test_base.py").write_text(
                "import unittest\n"
                "\n"
                "\n"
                "class BaseCase(unittest.TestCase):\n"
                "    def test_runs(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            (tests_dir / "test_reuse.py").write_text("from tests.test_base import BaseCase\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(checkout / "run_tests.py")],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertIn("Discovered 1 unittest IDs more than once:", completed.stderr)
        self.assertIn("  tests.test_base.BaseCase.test_runs", completed.stderr)
        self.assertNotIn("Ran ", completed.stderr)

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

    def test_repo_search_previews_long_generated_rows_with_bounded_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data = root / "data"
            data.mkdir()
            (data / "shop_data.py").write_text(
                "wilderness " + "catalog-value " * 200 + "\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "repo_search.py"),
                    "wilderness",
                    "data/shop_data.py",
                    "--include-large",
                    "--max-columns",
                    "80",
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("wilderness", completed.stdout)
        self.assertLess(len(completed.stdout), 300)

    def test_repo_search_treats_flag_prefixed_pattern_as_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tool = root / "tools" / "run_remote_tests.py"
            tool.parent.mkdir()
            tool.write_text("parser.add_argument('--select')\n", encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "repo_search.py"),
                    "--",
                    "--select|select.*startswith|test_name",
                    "tools/run_remote_tests.py",
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("parser.add_argument('--select')", completed.stdout)
        self.assertNotIn("unrecognized flag", completed.stderr)

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

    def test_repo_search_line_range_bounds_giant_source_lines(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "generated.py"
            source.write_text("first\n" + "x" * 1000 + "\nthird\nfourth\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "repo_search.py"),
                    "--line-range",
                    "generated.py",
                    "2",
                    "4",
                    "--max-columns",
                    "10",
                    "--max-results",
                    "2",
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(
            completed.stdout.splitlines(),
            [
                "generated.py:2:xxxxxxxxxx [omitted 990 columns]",
                "generated.py:3:third",
            ],
        )
        self.assertIn("stopped at 2 results", completed.stderr)

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

    def test_list_ends_with_the_matching_test_count_even_when_cut(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = Path(temp_dir) / "count-fixture"
            tests_dir = checkout / "tests"
            tests_dir.mkdir(parents=True)
            shutil.copy2(ROOT / "run_tests.py", checkout / "run_tests.py")
            shutil.copy2(ROOT / "tests/__init__.py", tests_dir / "__init__.py")
            (tests_dir / "test_count_probe.py").write_text(
                "import unittest\n"
                "\n"
                "\n"
                "class CountProbe(unittest.TestCase):\n"
                "    def test_a(self):\n"
                "        self.assertTrue(True)\n"
                "\n"
                "    @unittest.skip('skipped tests still count')\n"
                "    def test_b(self):\n"
                "        self.assertTrue(True)\n"
                "\n"
                "    def test_c(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )

            def list_output(*extra):
                # Merged streams prove the count line lands after the IDs even when stdout is a pipe.
                return subprocess.run(
                    [sys.executable, str(checkout / "run_tests.py"), "CountProbe", "--list", *extra],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )

            complete = list_output()
            cut = list_output("--max-results", "2")

        ids = [f"tests.test_count_probe.CountProbe.test_{name}" for name in "abc"]
        self.assertEqual(complete.returncode, 0, complete.stdout)
        self.assertEqual(complete.stdout.splitlines(), [*ids, "Matching tests: 3"])
        self.assertEqual(cut.returncode, 2, cut.stdout)
        self.assertEqual(
            cut.stdout.splitlines(),
            [
                *ids[:2],
                "Matching tests: 3. Refusing to print the last 1; narrow the selector "
                "or pass --max-results 3.",
            ],
        )

    def test_count_inventory_ignores_id_cap_and_counts_overlapping_selectors_once(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = Path(temp_dir)
            tests_dir = checkout / "tests"
            tests_dir.mkdir()
            shutil.copy2(ROOT / "run_tests.py", checkout / "run_tests.py")
            shutil.copy2(ROOT / "tests/__init__.py", tests_dir / "__init__.py")
            (tests_dir / "test_inventory.py").write_text(
                "import unittest\n"
                "class Inventory(unittest.TestCase):\n"
                "    def must_not_run(self):\n"
                "        raise AssertionError('inventory executed a test')\n"
                "for index in range(201):\n"
                "    setattr(Inventory, f'test_{index:03}', Inventory.must_not_run)\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(checkout / "run_tests.py"), "--count", "Inventory", "test_000"],
                check=False, capture_output=True, text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "Matching tests: 201\n")
        self.assertIn("Runtime skips: unknown until tests run", completed.stderr)
        self.assertNotIn("Ran ", completed.stderr)

    def test_count_inventory_reports_class_and_method_skips_without_predicting_runtime(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = Path(temp_dir)
            tests_dir = checkout / "tests"
            tests_dir.mkdir()
            shutil.copy2(ROOT / "run_tests.py", checkout / "run_tests.py")
            shutil.copy2(ROOT / "tests/__init__.py", tests_dir / "__init__.py")
            (tests_dir / "test_inventory.py").write_text(
                "import unittest\n"
                "@unittest.skip('aqt/PyQt6 not installed (use .venv-qt)')\n"
                "class QtOnly(unittest.TestCase):\n"
                "    @unittest.skip('method reason overridden by class')\n"
                "    def test_widget(self):\n"
                "        raise AssertionError('inventory executed a test')\n"
                "class Plain(unittest.TestCase):\n"
                "    @unittest.skip('platform guard')\n"
                "    def test_platform(self):\n"
                "        raise AssertionError('inventory executed a test')\n"
                "    def test_runtime(self):\n"
                "        self.skipTest('scenario ended before the forfeit could be tested')\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(checkout / "run_tests.py"), "--count"],
                check=False, capture_output=True, text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "Matching tests: 3\n")
        self.assertEqual(completed.stderr.splitlines(), [
            "Static skip: tests.test_inventory.Plain.test_platform: platform guard",
            "Static skip: tests.test_inventory.QtOnly.test_widget: aqt/PyQt6 not installed (use .venv-qt)",
            "Runtime skips: unknown until tests run; metadata applies to this interpreter only.",
        ])

    def test_optional_report_write_and_serialization_faults_leave_the_result_authoritative(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = Path(temp_dir)
            tests_dir = checkout / "tests"
            tests_dir.mkdir()
            shutil.copy2(ROOT / "run_tests.py", checkout / "run_tests.py")
            shutil.copy2(ROOT / "tests/__init__.py", tests_dir / "__init__.py")
            for serialization_fault in (False, True):
                with self.subTest(serialization_fault=serialization_fault):
                    source = "import unittest\nclass Probe(unittest.TestCase):\n    def test_active(self):\n        pass\n"
                    if serialization_fault:
                        source += "from unittest.mock import patch\npatch('json.dump', side_effect=TypeError('serialization probe')).start()\n"
                    (tests_dir / "test_probe.py").write_text(source, encoding="utf-8")
                    destination = checkout / "report.json" if serialization_fault else checkout / "missing" / "report.json"
                    completed = subprocess.run(
                        [sys.executable, str(checkout / "run_tests.py"), "--quiet"],
                        env={**os.environ, "ANKISCAPE_TEST_SKIP_REPORT": str(destination)},
                        check=False, capture_output=True, text=True,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    self.assertEqual(completed.stdout, "")
                    self.assertIn("OK", completed.stderr)
                    self.assertIn("warning: skipped-test report could not be written:", completed.stderr)
                    self.assertNotIn("Traceback", completed.stderr)

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

    def test_synthetic_cache_fixture_skips_only_without_its_optional_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = str(Path(directory) / "absent")
            count = len(unittest.defaultTestLoader.getTestCaseNames(OpenRs2DefinitionArgumentTests))
            for field in ("JAVA_BIN", "JAVAC_BIN", "GRADLE_CACHE"):
                with self.subTest(field=field):
                    result = subprocess.run(
                        [sys.executable, "-m", "unittest", "tests.test_papercut_tools.OpenRs2DefinitionArgumentTests"],
                        cwd=ROOT, env={**os.environ, field: missing},
                        check=False, capture_output=True, text=True, timeout=30,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn(f"OK (skipped={count})", result.stderr)
                    self.assertNotIn("ERROR", result.stderr)


@unittest.skipUnless(
    DEFINITION_JAVA.is_file() and DEFINITION_JAVAC.is_file()
    and (DEFINITION_GRADLE_CACHE / "rs.darkan/core/2.0.5").is_dir(),
    "Java 25 and Darkan core 2.0.5 required for the synthetic disk cache",
)
class OpenRs2DefinitionArgumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.cache = cls.root / "cache"
        cls.cache.mkdir()
        cls.java = str(DEFINITION_JAVA)
        cls.javac = str(DEFINITION_JAVAC)
        cls.classpath = ":".join(str(path) for path in DEFINITION_GRADLE_CACHE.rglob("*.jar"))
        cls.classes = cls.root / "classes"
        subprocess.run(
            [cls.javac, "--release", "25", "-cp", cls.classpath, "-d", str(cls.classes),
             str(ROOT / "tools/OpenRs2CacheDefinitionSearch.java")],
            check=True, capture_output=True, text=True, timeout=30,
        )
        data = bytearray(520)

        def archive(index, archive_id, payload):
            container = b"\0" + struct.pack(">I", len(payload)) + payload
            sector = len(data) // 520
            # Tiny uncompressed fixture archives fit within one 512-byte sector payload.
            data.extend(struct.pack(">HH", archive_id, 0) + b"\0\0\0" + bytes([index])
                        + container + bytes(512 - len(container)))
            path = cls.cache / f"main_file_cache.idx{index}"
            entries = bytearray(path.read_bytes() if path.exists() else b"")
            entries.extend(bytes(max(0, (archive_id + 1) * 6 - len(entries))))
            entries[archive_id * 6:archive_id * 6 + 6] = (
                len(container).to_bytes(3, "big") + sector.to_bytes(3, "big")
            )
            path.write_bytes(entries)

        # Index 10 holds "huffman", whose 31-based archive-name hash is 1258058669.
        for index, files, name_hash in ((10, (0,), 1258058669), (16, (1, 2), None), (18, (1, 2), None)):
            reference = bytes([5, int(name_hash is not None)]) + struct.pack(">HH", 1, 0)
            if name_hash is not None:
                reference += struct.pack(">I", name_hash)
            reference += struct.pack(">IIH", 0, 0, len(files))
            reference += struct.pack(">" + "H" * len(files), files[0], *[b - a for a, b in zip(files, files[1:])])
            if name_hash is not None:
                reference += bytes(4 * len(files))
            archive(255, index, reference)
        # Huffman maps all 256 byte values with eight-bit codes, a complete prefix code.
        archive(10, 0, bytes([8]) * 256)
        for index, kind in ((16, "object"), (18, "npc")):
            definitions = [
                b"\2" + f"{kind} canary {number}".encode() + b"\0"
                + (bytes([95, 0, 40 + number]) if kind == "npc" else b"") + b"\0"
                for number in (1, 2)
            ]
            archive(index, 0, b"".join(definitions)
                    + struct.pack(">ii", len(definitions[0]), len(definitions[1]) - len(definitions[0])) + b"\1")
        (cls.cache / "main_file_cache.dat2").write_bytes(data)

    def _run(self, *arguments, direct=False, unavailable=False, cache=None):
        cache = self.cache if cache is None else cache
        # Unavailable removes toolchain and cache for the wrapper, but only the cache for direct Java.
        if unavailable:
            cache = self.root / "unopened"
        command = (
            [self.java, "--class-path", f"{self.classes}:{self.classpath}", "OpenRs2CacheDefinitionSearch"]
            if direct else [str(ROOT / "tools/query_openrs2_cache_definitions.sh")]
        )
        env = {**os.environ, "TMPDIR": str(self.root)}
        if unavailable and not direct:
            env.update(JAVA_BIN=str(self.root / "missing-java"), JAVAC_BIN=str(self.root / "missing-javac"),
                       GRADLE_CACHE=str(self.root / "missing-gradle"))
        return subprocess.run([*command, str(cache), *arguments], cwd=ROOT, env=env,
                              check=False, capture_output=True, text=True, timeout=30)

    def test_invalid_id_operands_fail_before_runtime_cache_or_partial_output(self):
        for direct in (False, True):
            for unavailable in (False, True):
                for mode in ("--id", "--params", "--combat-levels"):
                    for operands in ((), ("--id", "2"), ("1", "--id", "2"), ("1", "bad"),
                                     ("1", ""), ("1.5",), ("-1",), ("2147483648",)):
                        with self.subTest(direct=direct, unavailable=unavailable, mode=mode, operands=operands):
                            result = self._run("npc", mode, *operands, direct=direct, unavailable=unavailable)
                            self.assertEqual(result.returncode, 2, result.stderr)
                            self.assertEqual(result.stdout, "")
                            self.assertIn("usage:", result.stderr)
                            self.assertNotIn("Exception", result.stderr)
                            self.assertNotIn("\tat ", result.stderr)

    def test_valid_multi_id_modes_read_both_synthetic_definitions(self):
        cases = (("npc", "--id"), ("npc", "--params"), ("npc", "--combat-levels"),
                 ("object", "--id"), ("object", "--params"))
        for direct, (kind, mode) in itertools.product((False, True), cases):
            with self.subTest(direct=direct, kind=kind, mode=mode):
                result = self._run(kind, mode, "+0001", "2", direct=direct)
                self.assertEqual(result.returncode, 0, result.stderr)
                suffixes = {
                    "--combat-levels": ("41", "42"), "--params": ("{}", "{}"),
                }.get(mode, ("[null, null, null, null, null]",) * 2)
                self.assertEqual(result.stdout, "".join(
                    f"{number}\t{kind} canary {number}\t{suffix}\n"
                    for number, suffix in zip((1, 2), suffixes)
                ))
                self.assertEqual(result.stderr, "")

    def test_invalid_kind_and_object_combat_mode_fail_before_cache_open(self):
        for direct in (False, True):
            for arguments in (("item", "--id", "1"), ("object", "--combat-levels", "1")):
                with self.subTest(direct=direct, arguments=arguments):
                    result = self._run(*arguments, direct=direct, unavailable=True)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn("usage:", result.stderr)

    def test_name_search_and_wrapper_cleanup_keep_working(self):
        result = self._run("object", "canary")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([row.split("\t")[:2] for row in result.stdout.splitlines()],
                         [["1", "object canary 1"], ["2", "object canary 2"]])
        self.assertEqual(list(self.root.glob("ankiscape-openrs2-defs.*")), [])

    def test_name_search_reports_the_missing_cache_index(self):
        for direct, (index, kind, name), truncate in itertools.product(
            (False, True), ((16, "object", "OBJECTS"), (18, "npc", "NPCS")), (False, True)
        ):
            with self.subTest(direct=direct, kind=kind, truncate=truncate), tempfile.TemporaryDirectory(dir=self.root) as directory:
                cache = Path(directory)
                shutil.copytree(self.cache, cache, dirs_exist_ok=True)
                table = bytearray((cache / "main_file_cache.idx255").read_bytes())
                if truncate:
                    del table[index * 6:]
                else:
                    table[index * 6:index * 6 + 6] = bytes(6)
                (cache / "main_file_cache.idx255").write_bytes(table)
                result = self._run(kind, "canary", direct=direct, cache=cache)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, f"cache is missing the {name} index\n")

    def test_java_failure_preserves_wrapper_exit_status_and_cleans_owned_temp_files(self):
        with tempfile.TemporaryDirectory(dir=self.root) as directory:
            cache = Path(directory)
            shutil.copytree(self.cache, cache, dirs_exist_ok=True)
            (cache / "main_file_cache.dat2").write_bytes(b"")
            direct = self._run("npc", "canary", direct=True, cache=cache)
            result = self._run("npc", "canary", cache=cache)
            self.assertNotEqual(direct.returncode, 0, direct.stderr)
            self.assertEqual(result.returncode, direct.returncode, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertIn("com.rs.cache.Store", result.stderr)
            self.assertEqual(list(self.root.glob("ankiscape-openrs2-defs.*")), [])


if __name__ == "__main__":
    unittest.main()
