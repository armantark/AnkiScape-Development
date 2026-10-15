import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "maintenance" / "slop_gate_preflight.py"
GATE = (Path.home() / "fleet/config/git/hooks/slop_gate.py").resolve()
EXECUTABLES = tuple(
    Path.home() / ".local/bin" / name
    for name in ("lizard", "complexipy", "radon", "vulture", "pycodestyle")
)


def flat_branches(name: str, count: int) -> str:
    return f"def {name}(value):\n" + "".join(
        f"    if value == {number}:\n        return {number}\n"
        for number in range(count)
    ) + "    return -1\n"


class SlopGatePreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        missing = [] if GATE.is_file() else [str(GATE)]
        missing.extend(
            str(path)
            for path in EXECUTABLES
            if not (path.is_file() and os.access(path, os.X_OK))
        )
        if missing:
            # The remote test host lacks part of the fleet slop-gate toolchain.
            self.skipTest(f"slop-gate prerequisites not installed: {', '.join(missing)}")
        self.repo = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self._git("init", "-q")
        self.source = self.repo / "legacy.py"
        self.source.write_text(flat_branches("legacy", 15), encoding="utf-8")
        self._git("add", "-A")
        self._git(
            "-c", "core.hooksPath=/dev/null", "-c", "user.name=Test",
            "-c", "user.email=test@example.invalid", "commit", "-qm", "baseline",
        )

    def _git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.repo, check=True, capture_output=True, text=True
        ).stdout

    def _run(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(TOOL)], cwd=self.repo, check=False, capture_output=True, text=True
        )

    def test_unchanged_legacy_violation_is_allowed(self):
        self.source.write_text(
            "# Maintenance-only edit.\n" + flat_branches("legacy", 15), encoding="utf-8"
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unstaged_regression_is_refused_and_real_index_is_untouched(self):
        staged = self.repo / "staged.py"
        staged.write_text("value = 1\n", encoding="utf-8")
        self._git("add", "staged.py")
        staged.write_text("value = 2\n", encoding="utf-8")
        (self.repo / "untracked.py").write_text("value = 3\n", encoding="utf-8")
        self.source.write_text(flat_branches("legacy", 16), encoding="utf-8")
        index = Path(self._git("rev-parse", "--path-format=absolute", "--git-path", "index").strip())
        before_status = self._git("status", "--porcelain=v1")  # refreshes the index first
        before_index = index.read_bytes()

        result = self._run()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("legacy.py: legacy 17 (was 16)", result.stdout)
        self.assertEqual(index.read_bytes(), before_index)
        self.assertEqual(self._git("status", "--porcelain=v1"), before_status)


class SlopGatePreflightChildTests(unittest.TestCase):
    def setUp(self):
        self.repo = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.environment = {
            **os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
        }
        self._git("init", "-q")
        source = self.repo / "staged.py"
        source.write_text("value = 1\n", encoding="utf-8")
        self._git("add", "-A")
        source.write_text("value = 2\n", encoding="utf-8")
        (self.repo / "untracked.py").write_text("value = 3\n", encoding="utf-8")
        self.gate = self.repo / ".git" / "hooks" / "slop_gate.py"
        self.index = self.repo / ".git" / "index"

    def _git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.repo, env=self.environment,
            capture_output=True, text=True, check=True,
        ).stdout

    def _run(self, child):
        self.gate.write_text(child, encoding="utf-8")
        before_status = self._git("status", "--porcelain=v1")
        before_index = self.index.read_bytes()

        result = subprocess.run(
            [sys.executable, str(TOOL)], cwd=self.repo, env=self.environment,
            capture_output=True, text=True, check=False,
        )

        self.assertEqual(self.index.read_bytes(), before_index)
        self.assertEqual(self._git("status", "--porcelain=v1"), before_status)
        return result

    def test_silent_child_failure_reports_gate_path_and_preserves_status(self):
        result = self._run("raise SystemExit(37)\n")

        self.assertEqual(result.returncode, 37)
        self.assertEqual(result.stdout, "")
        self.assertEqual(
            result.stderr, f"slop-gate preflight: {self.gate} exited with status 37\n"
        )

    def test_child_failure_preserves_stdout_and_stderr(self):
        result = self._run(
            'import sys\nprint("child stdout")\n'
            'print("child stderr", file=sys.stderr)\nraise SystemExit(23)\n'
        )

        self.assertEqual(result.returncode, 23)
        self.assertEqual(result.stdout, "child stdout\n")
        self.assertEqual(
            result.stderr,
            f"child stderr\nslop-gate preflight: {self.gate} exited with status 23\n",
        )

    def test_silent_child_success_stays_silent(self):
        result = self._run("raise SystemExit(0)\n")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")


class SlopGatePreflightArgumentsTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.git = self.directory / "git"
        self.git.write_text('#!/bin/sh\ntouch "$0.called"\nexit 73\n')
        self.git.chmod(0o755)
        self.marker = self.directory / "git.called"

    def _run(self, argument):
        return subprocess.run(
            [sys.executable, str(TOOL), argument], cwd=self.directory,
            env={**os.environ, "PATH": f"{self.directory}{os.pathsep}{os.environ['PATH']}"},
            capture_output=True, text=True, check=False,
        )

    def test_help_returns_usage_before_any_git_or_gate_operation(self):
        result = self._run("--help")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("usage:", result.stdout)
        self.assertFalse(self.marker.exists())

    def test_unknown_option_is_refused_before_any_git_or_gate_operation(self):
        result = self._run("--unsupported-option")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unrecognized arguments: --unsupported-option", result.stderr)
        self.assertFalse(self.marker.exists())


if __name__ == "__main__":
    unittest.main()
