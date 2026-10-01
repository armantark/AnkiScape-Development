import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "maintenance" / "function_metrics.py"
GATE = (Path.home() / "fleet/config/git/hooks/slop_gate.py").resolve()
EXECUTABLES = tuple(Path.home() / ".local/bin" / name for name in ("lizard", "complexipy", "radon"))


def flat_branches(name, count):
    return f"def {name}(value):\n" + "".join(
        f"    if value == {number}:\n        return {number}\n" for number in range(count)
    ) + "    return -1\n"


def nested_branches(name, count):
    return f"def {name}(value):\n" + "".join(
        "    " * (number + 1) + "if value:\n" for number in range(count)
    ) + "    " * (count + 1) + "return value\n"


def repeated_arithmetic(name, count):
    return f"def {name}(value):\n" + "    value += 1\n" * count + "    return value\n"


class FunctionMetricsTests(unittest.TestCase):
    def setUp(self):
        missing = [] if GATE.is_file() else [str(GATE)]
        missing.extend(str(path) for path in EXECUTABLES if not (path.is_file() and os.access(path, os.X_OK)))
        self.assertFalse(missing, f"Missing function-metrics prerequisites: {', '.join(missing)}. See {ROOT / 'README-tests.md'}.")
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.source_root = self.root / "source"
        self.source_root.mkdir()
        self.source = self.source_root / "fixture.py"
        self.source.write_text(
            "def safe(value):\n    return value + 1\n\n"
            + flat_branches("ccn_high", 15) + "\n"
            + nested_branches("cognitive_high", 6) + "\n"
            + repeated_arithmetic("halstead_high", 162) + "\n"
            + flat_branches("ccn_boundary", 14) + "\n"
            + nested_branches("cognitive_boundary", 5) + "\n"
            + repeated_arithmetic("halstead_boundary", 160), encoding="utf-8",
        )
        self.output = self.root / "named-evidence"

    def _run(self, *names, output=None, source=None, gate=GATE):
        env = dict(os.environ)
        env["PATH"] = os.defpath
        return subprocess.run(
            [sys.executable, str(TOOL), str(source or self.source), *names,
             "--output", str(output or self.output), "--slop-gate", str(gate)],
            cwd=self.source_root, env=env, capture_output=True, text=True,
        )

    def test_safe_selection_ignores_legacy_hotspots_and_leaves_only_named_evidence(self):
        before = {p.relative_to(self.root): p.read_bytes() if p.is_file() else None for p in self.root.rglob("*")}
        result = self._run("safe")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(report["functions"], {
            "safe": {"ccn": 1, "cognitive": 0, "halstead_difficulty": 0.5, "violations": {}},
        })
        self.assertEqual(report["limits"], {"ccn": 15, "cognitive": 15, "halstead_difficulty": 80})
        after = {p.relative_to(self.root): p.read_bytes() if p.is_file() else None for p in self.root.rglob("*")}
        self.assertEqual(after, {**before, self.output.relative_to(self.root): self.output.read_bytes()})

    def test_selected_limit_failures_are_explicit_and_still_write_metrics(self):
        result = self._run("ccn_high", "cognitive_high", "halstead_high")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(self.output.read_text(encoding="utf-8"))
        for name, metric, value, limit in (
            ("ccn_high", "ccn", 16, 15),
            ("cognitive_high", "cognitive", 21, 15),
            ("halstead_high", "halstead_difficulty", 81.0, 80),
        ):
            with self.subTest(name=name):
                self.assertEqual(report["functions"][name]["violations"], {metric: value})
                self.assertIn(f"{name}: {metric} {value:g} > {limit}", result.stderr)

    def test_limits_are_inclusive(self):
        result = self._run("ccn_boundary", "cognitive_boundary", "halstead_boundary")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        functions = json.loads(self.output.read_text(encoding="utf-8"))["functions"]
        self.assertEqual(functions["ccn_boundary"]["ccn"], 15)
        self.assertEqual(functions["cognitive_boundary"]["cognitive"], 15)
        self.assertEqual(functions["halstead_boundary"]["halstead_difficulty"], 80)
        self.assertTrue(all(not row["violations"] for row in functions.values()))

    def test_invalid_selections_do_not_publish_a_partial_report(self):
        for text, name in (
            ("def safe():\n    return 1\n", "missing"),
            ("def broken(:\n", "broken"),
        ):
            with self.subTest(name=name):
                self.source.write_text(text, encoding="utf-8")
                result = self._run(name)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertFalse(self.output.exists())
                self.assertIn("error:", result.stderr)

    def test_nested_selection_names_enclosing_function_before_loading_gate(self):
        self.source.write_text(
            "def outer():\n    def inner():\n        return 1\n    return inner()\n",
            encoding="utf-8",
        )
        result = self._run("inner", gate=self.root / "must-not-load.py")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("outer.inner at line 2", result.stderr)
        self.assertIn("measure enclosing function 'outer'", result.stderr)
        self.assertNotIn("No such file", result.stderr)
        self.assertFalse(self.output.exists())

    def test_duplicate_and_qualified_selections_list_scopes_and_locations(self):
        self.source.write_text(
            "class A:\n    def same(self):\n        return 1\n\n"
            "class B:\n    def same(self):\n        return 2\n",
            encoding="utf-8",
        )
        for name in ("same", "A.same"):
            with self.subTest(name=name):
                result = self._run(name, gate=self.root / "must-not-load.py")
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("A.same at line 2", result.stderr)
                self.assertIn("B.same at line 6", result.stderr)
                self.assertIn("qualified", result.stderr)
                self.assertNotIn("No such file", result.stderr)
                self.assertFalse(self.output.exists())

    def test_in_tree_directory_and_symlink_outputs_are_refused_before_writing(self):
        link = self.root / "evidence-link"
        link.symlink_to(self.source_root, target_is_directory=True)
        for output in (self.source_root / "metrics.json", ROOT / "metrics.json", self.root, link / "metrics.json"):
            with self.subTest(output=output):
                result = self._run("safe", output=output)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("error:", result.stderr)
                if output == self.source_root / "metrics.json":
                    self.assertIn("separate sibling source and evidence directories", result.stderr)
                if not output.is_dir():
                    self.assertFalse(output.exists())

    def test_ordinary_module_is_an_input_error_not_a_limit_violation(self):
        module = self.source_root / "ordinary.py"
        module.write_text("value = 1\n", encoding="utf-8")
        result = self._run("safe", gate=module)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("missing required slop-gate API", result.stderr)
        self.assertFalse(self.output.exists())

    def test_unique_method_names_join_the_gate_instruments(self):
        self.source.write_text(
            "class Example:\n    def choose(self, value):\n        if value:\n            return value + 1\n        return 0\n", encoding="utf-8",
        )
        result = self._run("choose")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(self.output.read_text(encoding="utf-8"))["functions"]["choose"], {
            "ccn": 2, "cognitive": 1, "halstead_difficulty": 0.5, "violations": {},
        })
