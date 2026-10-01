import json
import tempfile
import unittest
from pathlib import Path

from tools.maintenance.probe_progress import ProbeProgress


class ProbeProgressTests(unittest.TestCase):
    def test_case_records_flush_start_and_completion_with_advancing_counts(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        progress_path = root / "progress.jsonl"

        with ProbeProgress(progress_path) as progress:
            with progress.case("generated", case_index=0, replay_seed=8128):
                pass
            records = [json.loads(line) for line in progress_path.read_text().splitlines()]

        self.assertEqual([record["event"] for record in records], ["start", "complete"])
        self.assertEqual([record["completed_cases"] for record in records], [0, 1])
        self.assertEqual({record["phase"] for record in records}, {"generated"})
        self.assertEqual({record["case_index"] for record in records}, {0})
        self.assertEqual({record["replay_seed"] for record in records}, {8128})
        self.assertTrue(all(record["elapsed_seconds"] >= 0 for record in records))

    def test_interrupted_case_leaves_an_unmatched_start_record(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        progress_path = root / "progress.jsonl"

        with self.assertRaisesRegex(RuntimeError, "interrupted"):
            with ProbeProgress(progress_path) as progress:
                with progress.case("baseline", case_index=0):
                    pass
                with progress.case("generated", case_index=43857, replay_seed=99):
                    raise RuntimeError("interrupted")

        records = [json.loads(line) for line in progress_path.read_text().splitlines()]
        self.assertEqual(
            [(record["event"], record["case_index"]) for record in records],
            [("start", 0), ("complete", 0), ("start", 43857)],
        )
        self.assertEqual(records[-1]["completed_cases"], 1)
        self.assertEqual(records[-1]["replay_seed"], 99)


if __name__ == "__main__":
    unittest.main()
