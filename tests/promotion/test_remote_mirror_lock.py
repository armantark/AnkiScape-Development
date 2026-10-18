import fcntl
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from tests.test_promotion_gate import PromotionRepo
from tools import run_remote_tests
from tools.promotion_gate import (
    GateError,
    _run_gate_checks,
    active_gate_records,
    claim_landing_lock,
    landing_lock_path_for,
    run_gate,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


REMOTE_RUNNER_WITHOUT_NETWORK = """\
import sys, time
from pathlib import Path
sys.path.insert(0, {project_root!r})
from tools import run_remote_tests as runner
runner.LOCAL_MIRROR_LOCK_PATH = Path({lock_path!r})
runner._preflight = lambda lane: None
runner._sync = lambda worktree: time.sleep({work_seconds!r})
runner._stream_remote_run = lambda lane, **options: (0, "Ran 4506 tests in 1.0s\\n\\nOK\\n")
raise SystemExit(runner.main(sys.argv[1:]))
"""


REMOTE_RUNNER_WITH_LOCAL_HOST = """\
import sys, time
from pathlib import Path
sys.path.insert(0, {project_root!r})
from tools import run_remote_tests as runner
host = Path({host_root!r})
runner.LOCAL_MIRROR_LOCK_PATH = Path({lock_path!r})
runner._on_test_host = lambda: True
runner.REMOTE_ROOT, runner.REMOTE_REPO, runner.REMOTE_VENV = host, host / "ankiscape_fork", host / ".venv-qt"
runner._preflight = lambda lane: time.sleep({work_seconds!r})
runner._sync = lambda worktree: None
runner._remote_lane_command = lambda lane, **options: "sleep 60"
raise SystemExit(runner.main(sys.argv[1:]))
"""


class RemoteMirrorLockTimingTest(unittest.TestCase):
    """The real gate drives the real runner; only the runner's network steps are replaced."""

    def run_plain_gate(
        self,
        *,
        focused_run_seconds: float | None,
        work_seconds: float,
        lock_bound: float = 60.0,
        runner: str = REMOTE_RUNNER_WITHOUT_NETWORK,
        host_root: Path | None = None,
    ) -> tuple[tuple[str, ...], tuple[str, ...], str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            worktree = Path(temp_dir) / "tree"
            (worktree / "tools").mkdir(parents=True)
            (worktree / "run_tests.py").write_text("", encoding="utf-8")
            lock_path = (host_root or Path(temp_dir)) / "mirror.lock"
            (worktree / "tools" / "run_remote_tests.py").write_text(
                runner.format(
                    project_root=str(PROJECT_ROOT),
                    host_root=str(host_root),
                    lock_path=str(lock_path),
                    work_seconds=work_seconds,
                ),
                encoding="utf-8",
            )
            if focused_run_seconds is not None:
                focused_run = lock_path.open("a+", encoding="utf-8")
                self.addCleanup(focused_run.close)
                fcntl.flock(focused_run.fileno(), fcntl.LOCK_EX)
                release = threading.Timer(focused_run_seconds, focused_run.close)
                release.start()
                self.addCleanup(release.cancel)
            log = io.StringIO()
            with (
                patch.object(run_remote_tests, "LOCAL_MIRROR_LOCK_PATH", lock_path),
                patch("tools.promotion.lane_execution.PLAIN_LANE_TIMEOUT", 2.0),
                patch("tools.promotion.lane_execution.REMOTE_MIRROR_LOCK_TIMEOUT", lock_bound),
            ):
                passed, failures = _run_gate_checks(
                    worktree, source_worktree=worktree, plain_only=True, remote_lanes=True, log=log,
                )
        return passed, failures, log.getvalue()

    def test_queue_longer_than_the_lane_limit_does_not_count_against_it(self):
        passed, failures, log = self.run_plain_gate(focused_run_seconds=3.0, work_seconds=0.0)

        self.assertIn("plain lane", passed, log)
        waited = float(re.search(r"held after ([\d.]+) seconds", log).group(1))
        self.assertGreater(waited, 2.0)

    def test_lane_work_over_the_limit_still_times_out(self):
        passed, failures, log = self.run_plain_gate(focused_run_seconds=None, work_seconds=5.0)

        self.assertNotIn("plain lane", passed)
        self.assertIn("plain lane (exit 124)", failures)
        self.assertIn("=== PLAIN LANE ===", log)
        self.assertIn("TIMEOUT: exceeded 2 seconds\nFAILED: exit 124 (TIMEOUT)", log)

    @staticmethod
    def _stop_lane(process: subprocess.Popen) -> None:
        # Reap it: an unwaited kill leaves a zombie and a ResourceWarning that hides
        # real failures in this fixture's output.
        process.kill()
        process.wait(timeout=30)

    def _local_host(self, host_dir: str) -> Path:
        host = Path(host_dir)
        (host / "reports").mkdir()
        (host / "ankiscape_fork").mkdir()
        (host / ".venv-qt" / "bin").mkdir(parents=True)
        (host / ".venv-qt" / "bin" / "python").symlink_to(sys.executable)
        return host

    def test_lane_timeout_stops_the_killed_runner_s_detached_lane(self):
        with tempfile.TemporaryDirectory() as host_dir:
            host = self._local_host(host_dir)
            with patch.object(run_remote_tests, "_on_test_host", return_value=True):
                passed, failures, log = self.run_plain_gate(
                    focused_run_seconds=None, work_seconds=0.0,
                    runner=REMOTE_RUNNER_WITH_LOCAL_HOST, host_root=host,
                )
            (pid_path,) = (host / "reports").glob("*.pid")
            group = int(pid_path.read_text())

        self.assertIn("plain lane (exit 124)", failures)
        self.assertIn(f"FAILED: exit 124 (TIMEOUT)\nStopped remote run {pid_path.stem};", log)
        with self.assertRaises(ProcessLookupError):
            os.killpg(group, 0)

    def test_runner_timed_out_before_launch_leaves_an_earlier_live_lane_running(self):
        with tempfile.TemporaryDirectory() as host_dir:
            host = self._local_host(host_dir)
            pid_path = host / "reports" / "qt-earlier.pid"
            with pid_path.open("w+") as lane_stdin:
                earlier = subprocess.Popen(("sleep", "60"), start_new_session=True, stdin=lane_stdin)
            self.addCleanup(self._stop_lane, earlier)
            pid_path.write_text(f"{earlier.pid}\n")
            record = json.dumps({
                "run_id": "qt-earlier", "log_path": str(host / "reports" / "qt-earlier.log"),
                "report_path": str(host / "reports" / "qt-earlier.report"), "pid_path": str(pid_path),
            })
            pending_path = host / "mirror.pending.json"
            pending_path.write_text(record)
            with patch.object(run_remote_tests, "_on_test_host", return_value=True):
                passed, failures, log = self.run_plain_gate(
                    focused_run_seconds=None, work_seconds=5.0,
                    runner=REMOTE_RUNNER_WITH_LOCAL_HOST, host_root=host,
                )
            self.assertEqual(pending_path.read_text(), record)

        self.assertIn("plain lane (exit 124)", failures)
        self.assertIn("FAILED: exit 124 (TIMEOUT)\nThe timed-out runner left no remote lane of its own", log)
        self.assertIsNone(earlier.poll())

    def test_endless_queue_fails_at_the_lock_bound_without_starting_the_lane(self):
        passed, failures, log = self.run_plain_gate(
            focused_run_seconds=600.0, work_seconds=0.0, lock_bound=1.0,
        )

        self.assertNotIn("plain lane", passed)
        self.assertIn("plain lane (mirror lock wait timed out)", failures)
        self.assertIn("TIMEOUT: waited 1 seconds for ", log)
        self.assertNotIn("=== PLAIN LANE ===", log)


class WaitingGateLockTest(unittest.TestCase):
    def test_waiting_gate_survives_competing_claim_after_1301_seconds(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            lock_path = Path(temp_dir) / "mirror.lock"
            now = datetime.now().astimezone()
            started = now

            with lock_path.open("a+", encoding="utf-8") as mirror:
                fcntl.flock(mirror.fileno(), fcntl.LOCK_EX)

                def contend_after_heartbeat(_seconds):
                    nonlocal now
                    if now == started:
                        now += timedelta(seconds=1301)
                        return
                    active = active_gate_records(repo.target)
                    self.assertEqual([record.commit for record in active], [repo.target_commit])
                    with self.assertRaisesRegex(GateError, "Promotion landing lock held: PID"):
                        claimed = claim_landing_lock(
                            repo.target, operation="landing", worktree=repo.target,
                            commit=repo.target_commit,
                        )
                        claimed.release()
                    mirror.close()

                with (
                    patch.object(run_remote_tests, "LOCAL_MIRROR_LOCK_PATH", lock_path),
                    patch("tools.promotion.locking.datetime", wraps=datetime) as clock,
                    patch("tools.promotion.lane_execution.time.sleep", side_effect=contend_after_heartbeat),
                    patch("tools.promotion.lane_execution._run_check", return_value=0),
                    patch("tools.promotion.lane_execution._run_reachability_check", return_value=0),
                    patch(
                        "tools.promotion.locking.kill_process_tree",
                        side_effect=AssertionError("Healthy waiting gate was killed as stale"),
                    ) as kill,
                ):
                    clock.now.side_effect = lambda: now
                    run_gate(repo.target, plain_only=True, remote_lanes=True, stdout=io.StringIO())
                    kill.assert_not_called()
                self.assertTrue(mirror.closed)
            self.assertFalse(landing_lock_path_for(repo.target).exists())
            self.assertEqual(active_gate_records(repo.target), ())


if __name__ == "__main__":
    unittest.main()
