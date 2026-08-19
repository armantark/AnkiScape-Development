import contextlib
import io
import unittest
from unittest.mock import patch

from tools import run_remote_tests


class RemoteTestHostTests(unittest.TestCase):
    def test_summary_parser_accepts_complete_unittest_output(self):
        summary = run_remote_tests.parse_unittest_summary(
            "progress\nRan 4144 tests in 125.215s\n\nOK (skipped=499)\n"
        )

        self.assertEqual(summary.tests, 4144)
        self.assertEqual(summary.skipped, 499)
        self.assertEqual(summary.ran_line, "Ran 4144 tests in 125.215s")
        self.assertEqual(summary.result_line, "OK (skipped=499)")

    def test_summary_parser_rejects_truncated_and_zero_test_output(self):
        for output, message in (
            ("progress only", "complete unittest success summary"),
            ("Ran 0 tests in 0.000s\n\nOK\n", "reported zero tests"),
        ):
            with self.subTest(output=output):
                with self.assertRaisesRegex(ValueError, message):
                    run_remote_tests.parse_unittest_summary(output)

    def test_lane_guard_rejects_partial_discovery_and_inflated_skips(self):
        cases = (
            ("plain", 4143, 499, "ran 4143 tests"),
            ("plain", 4144, 501, "plain lane false pass"),
            ("qt", 4144, 499, "Qt lane false pass"),
        )
        for lane, tests, skipped, message in cases:
            with self.subTest(lane=lane, tests=tests, skipped=skipped):
                summary = run_remote_tests.TestSummary("Ran", "OK", tests, skipped)
                with self.assertRaisesRegex(RuntimeError, message):
                    run_remote_tests.validate_test_summary(lane, summary)

    def test_lane_guard_accepts_recorded_plain_and_qt_baselines(self):
        for lane, skipped in (("plain", 499), ("qt", 3)):
            with self.subTest(lane=lane):
                summary = run_remote_tests.TestSummary("Ran", "OK", 4144, skipped)
                self.assertIsNone(run_remote_tests.validate_test_summary(lane, summary))

    def test_stream_reloads_log_after_completion_report_appears(self):
        complete = "....\nRan 4144 tests in 295.116s\n\nOK (skipped=3)\n"
        with patch.object(
            run_remote_tests,
            "_ssh",
            side_effect=("", "....", "0\n", complete),
        ), contextlib.redirect_stdout(io.StringIO()):
            returncode, output = run_remote_tests._stream_remote_run(
                "qt", timeout=1.0, poll_interval=0.01
            )

        self.assertEqual(returncode, 0)
        self.assertEqual(output, complete)
        self.assertEqual(run_remote_tests.parse_unittest_summary(output).tests, 4144)


if __name__ == "__main__":
    unittest.main()
