import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class CandidateGateTest(unittest.TestCase):
    def test_candidate_that_changes_gate_code_is_judged_by_its_own_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = Path(temp_dir).resolve()
            shutil.copytree(
                PROJECT_ROOT / "tools",
                candidate / "tools",
                ignore=shutil.ignore_patterns("__pycache__"),
            )
            # The 1fc26752 shape: only the in-process judging code changed.
            with (candidate / "tools" / "promotion" / "lane_execution.py").open(
                "a", encoding="utf-8"
            ) as stream:
                stream.write('\nprint("candidate gate", sys.argv[1:])\nraise SystemExit(0)\n')

            completed = subprocess.run(
                (
                    sys.executable,
                    str(PROJECT_ROOT / "tools" / "promotion_gate.py"),
                    "run",
                    str(candidate),
                    "--remote-lanes",
                ),
                capture_output=True,
                text=True,
                timeout=60,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout,
            f"candidate gate ['run', '{candidate}', '--remote-lanes']\n",
        )
        self.assertEqual(
            completed.stderr,
            "Candidate changes the gate; running "
            f"{candidate / 'tools' / 'promotion_gate.py'}\n",
        )


if __name__ == "__main__":
    unittest.main()
