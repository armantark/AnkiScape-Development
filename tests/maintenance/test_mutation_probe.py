import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


TOOL = Path(__file__).resolve().parents[2] / "tools" / "maintenance" / "run_mutation_probe.py"
SEES_MUTANT = "from pathlib import Path; assert Path('target.py').read_text() == \"VALUE = 'mutant'\\n\"; "


class MutationProbeTests(unittest.TestCase):
    def setUp(self):
        self.worktree = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (self.worktree / ".git").write_text("gitdir: /tmp/test-git\n", encoding="utf-8")
        self.tool = self.worktree / "tools" / "maintenance" / TOOL.name
        self.tool.parent.mkdir(parents=True)
        shutil.copy(TOOL, self.tool)
        self.source = self.worktree / "target.py"
        self.original = b"VALUE = 'uncommitted edit'\n"
        self.source.write_bytes(self.original)
        self.mutant = self.worktree / "mutant.py.txt"
        self.mutant.write_bytes(b"VALUE = 'mutant'\n")

    def _probe(self, child: str, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable, str(self.tool), str(self.source), str(self.mutant),
                "--timeout", str(timeout), "--", sys.executable, "-c", SEES_MUTANT + child,
            ],
            text=True, capture_output=True, check=False,
        )

    def test_only_a_red_focused_command_under_the_mutant_is_a_proof(self):
        for child_exit, probe_exit in ((7, 0), (0, 1)):
            with self.subTest(child_exit=child_exit):
                result = self._probe(f"raise SystemExit({child_exit})")

                self.assertEqual(result.returncode, probe_exit, result.stdout + result.stderr)
                self.assertEqual(self.source.read_bytes(), self.original)

    def test_timeout_stops_the_command_restores_the_source_and_is_not_a_proof(self):
        started = time.monotonic()
        result = self._probe("import time; time.sleep(60)", timeout=0.5)

        self.assertLess(time.monotonic() - started, 30)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_termination_mid_run_restores_the_source(self):
        result = self._probe("import os, signal, time; os.kill(os.getppid(), signal.SIGTERM); time.sleep(60)")

        self.assertEqual(result.returncode, 128 + signal.SIGTERM, result.stdout + result.stderr)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_canonical_checkout_is_refused_before_mutation(self):
        (self.worktree / ".git").unlink()
        (self.worktree / ".git").mkdir()

        result = self._probe("raise SystemExit(7)")

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(self.source.read_bytes(), self.original)


if __name__ == "__main__":
    unittest.main()
