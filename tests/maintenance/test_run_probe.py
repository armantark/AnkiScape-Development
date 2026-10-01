import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "maintenance" / "run_probe.py"


class RunProbeTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.evidence = self.root / "evidence"
        self.commands = self.root / "commands.json"

    def _write_commands(self, commands: list[list[str]]) -> None:
        self.commands.write_text(json.dumps(commands), encoding="utf-8")

    def _run(self, *extra: str, timeout: float = 10.0) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "--commands-file",
                str(self.commands),
                "--worktree",
                str(ROOT),
                "--evidence-dir",
                str(self.evidence),
                "--label",
                "burst_probe",
                *extra,
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )

    def _report(self) -> dict:
        reports = [path for path in self.evidence.glob("*.json") if not path.name.endswith(".pending.json")]
        self.assertEqual(len(reports), 1)
        return json.loads(reports[0].read_text(encoding="utf-8"))

    def test_exact_child_completes_when_its_argument_contains_the_probe_name(self):
        self._write_commands([[
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1])",
            "burst_probe",
        ]])

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self._report()
        self.assertEqual(report["commands"][0]["returncode"], 0)
        self.assertFalse(report["commands"][0]["timed_out"])
        self.assertIn("burst_probe", Path(report["log_path"]).read_text(encoding="utf-8"))

    def test_sequence_preserves_each_exit_status_and_returns_the_first_failure(self):
        self._write_commands([
            [sys.executable, "-c", "print('first')"],
            [sys.executable, "-c", "print('second'); raise SystemExit(7)"],
            [sys.executable, "-c", "print('third')"],
        ])

        result = self._run()

        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        report = self._report()
        self.assertEqual([row["returncode"] for row in report["commands"]], [0, 7, 0])
        self.assertTrue(report["complete"])

    def test_timeout_stops_the_exact_child_and_records_terminal_status(self):
        self._write_commands([[
            sys.executable,
            "-c",
            "import threading; threading.Event().wait(60)",
        ]])

        result = self._run("--timeout", "0.1")

        self.assertEqual(result.returncode, 124, result.stdout + result.stderr)
        report = self._report()
        self.assertEqual(report["commands"][0]["returncode"], 124)
        self.assertTrue(report["commands"][0]["timed_out"])

    def test_detached_launch_returns_before_completion_and_publishes_final_record(self):
        self._write_commands([[
            sys.executable,
            "-c",
            "import threading; print('started'); threading.Event().wait(0.5)",
        ]])

        result = self._run("--detach")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(list(self.evidence.glob("*.json")), list(self.evidence.glob("*.pending.json")))
        deadline = time.monotonic() + 5.0
        reports = []
        while time.monotonic() < deadline and not reports:
            threading.Event().wait(0.02)
            reports = [
                path for path in self.evidence.glob("*.json")
                if not path.name.endswith(".pending.json")
            ]
        self.assertEqual(len(reports), 1)
        report = json.loads(reports[0].read_text(encoding="utf-8"))
        self.assertEqual(report["commands"][0]["returncode"], 0)
        self.assertFalse(list(self.evidence.glob("*.pending.json")))


if __name__ == "__main__":
    unittest.main()
