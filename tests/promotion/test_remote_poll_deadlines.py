import contextlib
import io
import subprocess
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

    def test_wait_reads_complete_log_once_after_report_and_stop(self):
        root = self._worktree()
        log = root / 'lane.log'
        report = root / 'lane.report'
        log.write_text('running\n', encoding='utf-8')
        complete = 'running\nfinished λ\nRan 1 test in 0.1s\n\nOK\n'
        stopped = False
        commands = []
        execute = subprocess.run

        def transport(command, **kwargs):
            commands.append(command[-1])
            if str(log) in command[-1]:
                self.assertTrue(stopped, 'live log must not be reread while polling')
            return execute(command, **kwargs)

        def stop():
            nonlocal stopped
            stopped = True
            log.write_text(complete, encoding='utf-8')
            return 'Stopped'

        with (
            patch.object(run_remote_tests, '_on_test_host', return_value=True),
            patch.object(run_remote_tests.subprocess, 'run', side_effect=transport),
            patch.object(run_remote_tests.time, 'sleep', side_effect=lambda _: report.write_text('0\n')),
            patch.object(run_remote_tests, 'stop_pending_lane', side_effect=stop) as stop_lane,
            contextlib.redirect_stdout(io.StringIO()) as stdout,
        ):
            result = run_remote_tests._wait_for_remote_run(
                'plain', timeout=5, poll_interval=0.01, selectors=('example.',),
                collect_only=False, log_path=log, report_path=report,
                skip_report_path=root / 'skips.json',
            )

        self.assertEqual(result, (0, complete))
        self.assertEqual(stdout.getvalue(), complete)
        self.assertEqual(sum(str(report) in command for command in commands), 2)
        self.assertEqual(sum(str(log) in command for command in commands), 1)
        stop_lane.assert_called_once_with()

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
        clock = [10.0]
        deadlines: list[tuple[str, float | None]] = []

        def ssh(_command: str, *, label: str, deadline=None, **_kwargs) -> str:
            deadlines.append((label, deadline))
            return ""

        def report(_path: str, _deadline: float) -> int:
            clock[0] = 13.1
            return 0

        with (
            patch.object(run_remote_tests, "_ssh", side_effect=ssh),
            patch.object(run_remote_tests, "_completion_report", side_effect=report) as report_poll,
            patch.object(run_remote_tests, "stop_pending_lane", return_value="Stopped") as stop_lane,
            patch.object(run_remote_tests.time, "monotonic", side_effect=lambda: clock[0]),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaisesRegex(TimeoutError, "within 3 seconds"),
        ):
            run_remote_tests._stream_remote_run("plain", timeout=3.0, poll_interval=5.0)

        self.assertEqual(deadlines, [("remote lane launch", None)])
        self.assertEqual(report_poll.call_args.args[1], 13.0)
        stop_lane.assert_called_once_with()

    def test_stalled_report_poll_stops_the_lane(self):
        stall = run_remote_tests.SSHDeadlineExceeded("poll did not finish before its deadline")

        def ssh(_command: str, *, label: str, **_kwargs) -> str:
            if label == "remote lane report poll":
                raise stall
            return ""

        with (
            patch.object(run_remote_tests, "_ssh", side_effect=ssh),
            patch.object(run_remote_tests, "stop_pending_lane", return_value="Stopped") as stop_lane,
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(TimeoutError),
        ):
            run_remote_tests._stream_remote_run("qt", timeout=3.0, poll_interval=5.0)

        stop_lane.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
