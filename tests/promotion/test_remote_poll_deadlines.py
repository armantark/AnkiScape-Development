import contextlib
import io
import json
import os
import subprocess
import tempfile
import time
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
        report_polls = [0]
        run_transport = run_remote_tests._run_transport_attempt

        def transport(command, *, timeout=None):
            remote = command[-1]
            commands.append(remote)
            if str(log) in remote:
                self.assertTrue(stopped, 'live log must not be reread while polling')
            if str(report) in remote:
                # The first poll finds no report, as before the lane's exit lands.
                report_polls[0] += 1
                if report_polls[0] == 2:
                    report.write_text('0\n', encoding='utf-8')
            return run_transport(command, timeout=timeout)

        def stop():
            nonlocal stopped
            stopped = True
            log.write_text(complete, encoding='utf-8')
            return 'Stopped'

        with (
            patch.object(run_remote_tests, '_on_test_host', return_value=True),
            patch.object(run_remote_tests, '_run_transport_attempt', side_effect=transport),
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

    def test_report_poll_exit_before_sigterm_still_stops_the_lane(self):
        root = self._worktree()
        receipt = run_remote_tests._pending_path()
        receipt.write_text(json.dumps({"run_id": "owned-fixture"}))
        lane = subprocess.Popen(("/bin/sleep", "6"), start_new_session=True)
        polls = []
        cleanup = run_remote_tests._stop_process_group

        def after_report_exit(process):
            polls.append(process)
            self.assertNotEqual(process.pid, os.getpgrp())
            # Let the real report read exit after its timeout, without a wait or reap.
            for _ in range(100):
                row = subprocess.run(
                    ("/bin/ps", "-p", str(process.pid), "-o", "stat="),
                    capture_output=True, text=True, check=True,
                ).stdout.strip()
                if row.startswith("Z"):
                    break
                time.sleep(0.01)
            self.assertTrue(row.startswith("Z"), row)
            return cleanup(process)

        def stop_owned_lane():
            lane.terminate()
            lane.wait(timeout=2)
            receipt.unlink()
            return "Stopped owned fixture"

        try:
            with (
                patch.object(run_remote_tests, "_on_test_host", return_value=True),
                patch.object(run_remote_tests, "_stop_process_group", side_effect=after_report_exit),
                patch.object(run_remote_tests, "stop_pending_lane", side_effect=stop_owned_lane) as stop,
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(TimeoutError) as raised,
            ):
                run_remote_tests._wait_for_remote_run(
                    "plain", timeout=0.000001, poll_interval=0.01, selectors=(),
                    collect_only=False, log_path=root / "lane.log", report_path=root / "lane.report",
                    skip_report_path=root / "skips.json",
                )
            self.assertIsInstance(raised.exception.__cause__, run_remote_tests.SSHDeadlineExceeded)
            stop.assert_called_once_with()
            self.assertIsNotNone(lane.poll())
            self.assertFalse(receipt.exists())
        finally:
            if lane.poll() is None:
                lane.terminate()
            lane.wait(timeout=2)
            for process in polls:
                process.communicate(timeout=2)

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
