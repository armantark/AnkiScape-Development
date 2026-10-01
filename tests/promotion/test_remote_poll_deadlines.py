import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import run_remote_tests


class RemotePollDeadlineTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        lock_patch = patch.object(
            run_remote_tests,
            "LOCAL_MIRROR_LOCK_PATH",
            Path(temporary.name) / "mirror.lock",
        )
        lock_patch.start()
        self.addCleanup(lock_patch.stop)

    def _worktree(self) -> Path:
        worktree = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (worktree / "run_tests.py").write_text("launch\n", encoding="utf-8")
        return worktree

    def test_remote_collect_only_reports_host_inventory_without_execution_summary(self):
        inventory = "Matching tests: 760\n"
        with (
            patch.object(run_remote_tests, "_preflight"),
            patch.object(run_remote_tests, "_sync"),
            patch.object(
                run_remote_tests,
                "_stream_remote_run",
                return_value=(0, inventory),
            ) as run,
            contextlib.redirect_stdout(io.StringIO()) as stdout,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            result = run_remote_tests.main([
                str(self._worktree()),
                "plain",
                "--collect-only",
                "--select",
                "test_combat_logic",
            ])

        self.assertEqual(result, 0)
        self.assertEqual(run.call_args.kwargs["selectors"], ["test_combat_logic"])
        self.assertTrue(run.call_args.kwargs["collect_only"])
        self.assertIn(
            "Remote plain inventory summary:\nMatching tests: 760",
            stdout.getvalue(),
        )
        self.assertNotIn("lane summary", stdout.getvalue())

    def test_completion_after_execution_deadline_times_out_instead_of_passing(self):
        deadlines: list[tuple[str, float | None]] = []

        def ssh(_command: str, *, label: str, deadline=None, **_kwargs) -> str:
            deadlines.append((label, deadline))
            return ""

        def stop() -> str:
            run_remote_tests._pending_path().unlink()
            return "Stopped late lane"

        with (
            patch.object(run_remote_tests, "_ssh", side_effect=ssh),
            patch.object(run_remote_tests, "_completion_report", return_value=0) as report,
            patch.object(run_remote_tests, "stop_pending_lane", side_effect=stop) as stop_lane,
            patch.object(run_remote_tests.time, "monotonic", side_effect=(10.0, 10.0, 13.1)),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaisesRegex(TimeoutError, "within 3 seconds"),
        ):
            run_remote_tests._stream_remote_run("plain", timeout=3.0, poll_interval=5.0)

        self.assertEqual(
            deadlines,
            [("remote lane launch", None), ("remote lane log poll", 13.0)],
        )
        self.assertEqual(report.call_args.args[1], 13.0)
        stop_lane.assert_called_once_with()
        self.assertFalse(run_remote_tests._pending_path().exists())

    def test_execution_polling_uses_one_deadline_and_caps_sleep_to_time_left(self):
        sleeps: list[float] = []
        monotonic = iter((20.0, 20.0, 20.2, 22.7, 23.0))

        def ssh(_command: str, *, label: str, deadline=None, **_kwargs) -> str:
            if label != "remote lane launch":
                self.assertEqual(deadline, 23.0)
            return ""

        def stop() -> str:
            run_remote_tests._pending_path().unlink()
            return "Stopped timed lane"

        with (
            patch.object(run_remote_tests, "_ssh", side_effect=ssh),
            patch.object(run_remote_tests, "_completion_report", return_value=None) as report,
            patch.object(run_remote_tests, "stop_pending_lane", side_effect=stop),
            patch.object(
                run_remote_tests.time,
                "monotonic",
                side_effect=lambda: next(monotonic),
            ),
            patch.object(run_remote_tests.time, "sleep", side_effect=sleeps.append),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(TimeoutError),
        ):
            run_remote_tests._stream_remote_run("qt", timeout=3.0, poll_interval=5.0)

        self.assertEqual(report.call_args.args[1], 23.0)
        self.assertEqual(len(sleeps), 1)
        self.assertAlmostEqual(sleeps[0], 0.3)


if __name__ == "__main__":
    unittest.main()
