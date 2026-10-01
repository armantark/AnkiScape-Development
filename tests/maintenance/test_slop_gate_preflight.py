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


if __name__ == "__main__":
    unittest.main()
