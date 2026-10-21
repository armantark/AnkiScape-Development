"""Parallel runner results must remain usable by gate and triage consumers."""

import io
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from run_tests import ParallelSuite, merge_worker_report, worker_report


class ParallelResultTests(unittest.TestCase):
    def test_incomplete_worker_report_fails_the_combined_run(self):
        report = worker_report(unittest.TextTestRunner(stream=io.StringIO()).run(unittest.TestSuite()))
        with tempfile.TemporaryDirectory() as directory:
            prefix = str(Path(directory) / "worker")
            Path(prefix + ".json").write_text(json.dumps(report), encoding="utf-8")
            output = io.StringIO()
            process = Mock()
            process.wait.return_value = 0
            process.poll.return_value = 0
            result = unittest.TextTestRunner(stream=output).run(
                lambda combined: ParallelSuite.collect_worker(
                    combined, process, prefix, ["tests.probe.Case.test_missing"], io.StringIO(), float("inf"),
                )
            )
        self.assertFalse(result.wasSuccessful())
        self.assertIn("worker ran 0 tests; assigned 1", output.getvalue())
        self.assertIn("FAILED (errors=1)", output.getvalue())

    def test_worker_failure_reaches_combined_report_with_rerunnable_id(self):
        class FailureProbe(unittest.TestCase):
            def test_failure(self):
                self.fail("parallel failure traceback survives")

        FailureProbe.__qualname__ = "FailureProbe"
        probe = FailureProbe("test_failure")
        worker = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.TestSuite([probe]))
        output = io.StringIO()
        combined = unittest.TextTestRunner(stream=output).run(
            lambda result: merge_worker_report(result, worker_report(worker), 1)
        )
        matches = re.findall(r"^(?:FAIL|ERROR): \S+ \(([\w.]+)\)", output.getvalue(), re.MULTILINE)
        self.assertIn(f"FAIL: {probe}", output.getvalue())
        self.assertIn("parallel failure traceback survives", output.getvalue())
        self.assertEqual(combined.testsRun, 1)
        self.assertFalse(combined.wasSuccessful())
        self.assertEqual(matches, [probe.id()])
