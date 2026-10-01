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
        self.assertFalse(missing, f"Missing slop-gate prerequisites: {', '.join(missing)}")
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        self.source = self.repo / "legacy.py"
        self.source.write_text(flat_branches("legacy", 15), encoding="utf-8")
        self.base = self._commit("baseline")

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.repo,
            check=True,
            capture_output=True,
            text=True,
        )

    def _commit(self, message: str) -> str:
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        environment = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
        }
        subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", "commit", "-qm", message],
            cwd=self.repo,
            check=True,
            env=environment,
        )
        return self._git("rev-parse", "HEAD").stdout.strip()

    def _run(self, *, base: str | None = None, gate: Path = GATE, env=None):
        command = [
            sys.executable,
            str(TOOL),
            "--root",
            str(self.repo),
            "--slop-gate",
            str(gate),
        ]
        if base is not None:
            command.extend(("--base", base))
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

    def test_unchanged_legacy_violation_is_allowed_against_review_base(self):
        self.source.write_text(
            "# Maintenance-only edit.\n" + flat_branches("legacy", 15),
            encoding="utf-8",
        )
        self._commit("maintenance")

        result = self._run(base=self.base)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_worsened_legacy_violation_is_rejected_on_clean_candidate(self):
        self.source.write_text(flat_branches("legacy", 16), encoding="utf-8")
        self._commit("worsen")

        result = self._run(base=self.base)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("slop-gate: cyclomatic complexity above 15", result.stdout)
        self.assertIn("legacy.py: legacy 17 (was 16)", result.stdout)

    def test_failure_propagates_and_real_index_and_worktree_are_unchanged(self):
        fake_gate = self.root / "fake_gate.py"
        fake_gate.write_text(
            "import subprocess\n"
            "print(subprocess.check_output([\"git\", \"diff\", \"--cached\", "
            "\"--name-only\"], text=True), end=\"\")\n"
            "raise SystemExit(7)\n",
            encoding="utf-8",
        )
        staged = self.repo / "staged.py"
        staged.write_text("value = 1\n", encoding="utf-8")
        self._git("add", "staged.py")
        staged.write_text("value = 2\n", encoding="utf-8")
        (self.repo / "untracked.py").write_text("value = 3\n", encoding="utf-8")
        index = Path(self._git("rev-parse", "--git-path", "index").stdout.strip())
        if not index.is_absolute():
            index = self.repo / index
        before_status = self._git("status", "--porcelain=v1").stdout
        before_index = index.read_bytes()
        temp_root = self.root / "temp"
        temp_root.mkdir()

        result = self._run(gate=fake_gate, env={**os.environ, "TMPDIR": str(temp_root)})

        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["staged.py", "untracked.py"])
        self.assertEqual(index.read_bytes(), before_index)
        self.assertEqual(self._git("status", "--porcelain=v1").stdout, before_status)
        self.assertEqual(list(temp_root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
