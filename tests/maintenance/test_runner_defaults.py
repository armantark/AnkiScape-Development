"""A bare `python3 run_tests.py` picks the interpreter and worker count a local run needs."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROBE = """\
import json, os, sys, unittest


class RunnerProbe(unittest.TestCase):
    def test_records_its_process(self):
        with open(os.environ["RUNNER_PROBE_RECORD"], "w", encoding="utf-8") as record:
            json.dump({
                "prefix": os.path.realpath(sys.prefix),
                "worker": "--worker-input" in sys.argv,
                "platform": os.environ.get("QT_QPA_PLATFORM"),
            }, record)
"""


class RunnerDefaultTests(unittest.TestCase):
    def setUp(self):
        self.checkout = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (self.checkout / "tests").mkdir()
        shutil.copy2(ROOT / "run_tests.py", self.checkout / "run_tests.py")
        shutil.copy2(ROOT / "tests/__init__.py", self.checkout / "tests/__init__.py")
        (self.checkout / "tests/test_runner_probe.py").write_text(PROBE, encoding="utf-8")

    def run_runner(self, *arguments: str, **environment: str) -> subprocess.CompletedProcess[str]:
        # The calling lane's own interpreter choice must not leak into the fixture run.
        inherited = {
            key: value for key, value in os.environ.items()
            if key not in ("ANKISCAPE_PLAIN_LANE", "QT_QPA_PLATFORM")
        }
        return subprocess.run(
            [sys.executable, str(self.checkout / "run_tests.py"), *arguments],
            env={**inherited, "RUNNER_PROBE_RECORD": str(self.checkout / "record.json"), **environment},
            capture_output=True, text=True, timeout=120,
        )

    def probe(self, *arguments: str, **environment: str) -> dict:
        completed = self.run_runner(*arguments, **environment)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads((self.checkout / "record.json").read_text(encoding="utf-8"))

    def test_full_run_fans_out_to_workers_unless_one_process_is_asked_for(self):
        self.assertTrue(self.probe()["worker"])
        self.assertFalse(self.probe("--processes", "1")["worker"])
        self.assertFalse(self.probe("RunnerProbe")["worker"])

    def test_run_moves_to_the_checkout_qt_interpreter_unless_the_plain_lane_keeps_its_own(self):
        qt_environment = self.checkout / ".venv-qt"
        venv.create(qt_environment, symlinks=True)

        moved = self.probe("--processes", "1")
        self.assertEqual(moved["prefix"], os.path.realpath(qt_environment))
        self.assertEqual(moved["platform"], "offscreen")

        kept = self.probe("--processes", "1", ANKISCAPE_PLAIN_LANE="1")
        self.assertEqual(kept["prefix"], os.path.realpath(sys.prefix))
        self.assertIsNone(kept["platform"])

        refused = self.run_runner("NoSuchProbe")
        self.assertEqual(refused.returncode, 2, refused.stderr)
        self.assertIn("No unambiguous unittest ID matched: NoSuchProbe", refused.stderr)


if __name__ == "__main__":
    unittest.main()
