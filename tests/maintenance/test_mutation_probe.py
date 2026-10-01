import json
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "maintenance" / "run_mutation_probe.py"


class MutationProbeTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.worktree = self.root / "worktree"
        self.worktree.mkdir()
        (self.worktree / ".git").write_text("gitdir: /tmp/test-git\n", encoding="utf-8")
        self.source = self.worktree / "target.py"
        self.original = b"VALUE = 'original dirty bytes'\n"
        self.source.write_bytes(self.original)
        self.mutant = self.root / "mutant.py"
        self.mutant.write_bytes(b"VALUE = 'mutant'\n")
        self.evidence = self.root / "evidence"
        self.command_file = self.root / "command.json"

    def _write_command(self, source: str) -> None:
        self.command_file.write_text(
            json.dumps([sys.executable, "-c", source, str(self.source)]),
            encoding="utf-8",
        )

    def _run(self, timeout: float = 5.0) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(TOOL),
                str(self.source),
                str(self.mutant),
                "--worktree",
                str(self.worktree),
                "--evidence-dir",
                str(self.evidence),
                "--command-file",
                str(self.command_file),
                "--timeout",
                str(timeout),
            ],
            cwd=self.worktree,
            text=True,
            capture_output=True,
            check=False,
        )

    def _report(self) -> dict:
        reports = list(self.evidence.glob("*.json"))
        self.assertEqual(len(reports), 1)
        return json.loads(reports[0].read_text(encoding="utf-8"))

    def test_failing_focused_command_restores_preexisting_bytes_and_records_red_proof(self):
        bytecode = self.worktree / "__pycache__" / "target.cpython-314.pyc"
        bytecode.parent.mkdir()
        bytecode.write_bytes(b"stale")
        self._write_command(
            "from pathlib import Path; import sys; "
            "assert Path(sys.argv[1]).read_text() == \"VALUE = 'mutant'\\n\"; "
            "raise SystemExit(7)"
        )

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertFalse(bytecode.exists())
        report = self._report()
        self.assertEqual(report["child_returncode"], 7)
        self.assertTrue(report["proof_passed"])
        self.assertTrue(report["restoration_verified"])
        self.assertEqual(Path(report["backup_path"]).read_bytes(), self.original)

    def test_timeout_restores_source_and_cannot_report_a_successful_proof(self):
        self._write_command(
            "from pathlib import Path; import sys, threading; "
            "assert Path(sys.argv[1]).read_text() == \"VALUE = 'mutant'\\n\"; "
            "threading.Event().wait(60)"
        )

        result = self._run(timeout=0.1)

        self.assertEqual(result.returncode, 124, result.stdout + result.stderr)
        self.assertEqual(self.source.read_bytes(), self.original)
        report = self._report()
        self.assertTrue(report["timed_out"])
        self.assertFalse(report["proof_passed"])
        self.assertTrue(report["restoration_verified"])

    def test_handled_termination_restores_source_and_preserves_backup(self):
        self._write_command(
            "from pathlib import Path; import os, signal, sys, threading; "
            "assert Path(sys.argv[1]).read_text() == \"VALUE = 'mutant'\\n\"; "
            "os.kill(int(os.environ['ANKISCAPE_MUTATION_PROBE_PID']), signal.SIGTERM); "
            "threading.Event().wait(60)"
        )

        result = self._run()

        self.assertEqual(result.returncode, 128 + signal.SIGTERM, result.stdout + result.stderr)
        self.assertEqual(self.source.read_bytes(), self.original)
        report = self._report()
        self.assertEqual(report["interrupted_signal"], signal.SIGTERM)
        self.assertFalse(report["proof_passed"])
        self.assertTrue(report["restoration_verified"])
        self.assertEqual(Path(report["backup_path"]).read_bytes(), self.original)


if __name__ == "__main__":
    unittest.main()
