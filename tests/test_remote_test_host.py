import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import run_remote_tests


class RemoteTestHostTests(unittest.TestCase):
    def test_summary_parser_accepts_complete_unittest_output(self):
        summary = run_remote_tests.parse_unittest_summary(
            "progress\nRan 4507 tests in 247.142s\n\nOK (skipped=513)\n"
        )

        self.assertEqual(summary.tests, 4507)
        self.assertEqual(summary.skipped, 513)
        self.assertEqual(summary.ran_line, "Ran 4507 tests in 247.142s")
        self.assertEqual(summary.result_line, "OK (skipped=513)")

    def test_summary_parser_rejects_truncated_and_zero_test_output(self):
        for output, message in (
            ("Ran 4506 tests in 247.142s\n", "complete unittest success summary"),
            ("Ran 0 tests in 0.000s\n\nOK\n", "reported zero tests"),
        ):
            with self.subTest(output=output):
                with self.assertRaisesRegex(ValueError, message):
                    run_remote_tests.parse_unittest_summary(output)

    def test_lane_guard_rejects_partial_discovery_and_lost_active_coverage(self):
        cases = (
            ("plain", 4505, 511, "ran 4505 tests"),
            ("plain", 4506, 513, "active=3993"),
            ("qt", 4506, 4, "active=4502"),
        )
        for lane, tests, skipped, message in cases:
            with self.subTest(lane=lane, tests=tests, skipped=skipped):
                summary = run_remote_tests.parse_unittest_summary(
                    f"Ran {tests} tests in 1.000s\n\nOK (skipped={skipped})\n"
                )
                with self.assertRaisesRegex(RuntimeError, message):
                    run_remote_tests.validate_test_summary(lane, summary)

    def test_lane_guard_accepts_current_discovery_and_active_floors(self):
        for lane, skipped in (("plain", 512), ("qt", 3)):
            with self.subTest(lane=lane):
                summary = run_remote_tests.parse_unittest_summary(
                    f"Ran 4506 tests in 1.000s\n\nOK (skipped={skipped})\n"
                )
                self.assertIsNone(run_remote_tests.validate_test_summary(lane, summary))

    def test_lane_guard_accepts_more_qt_only_skips_when_plain_coverage_holds(self):
        summary = run_remote_tests.parse_unittest_summary(
            "Ran 4507 tests in 247.142s\n\nOK (skipped=513)\n"
        )

        self.assertIsNone(run_remote_tests.validate_test_summary("plain", summary))

    def test_rsync_excludes_local_worktree_links_from_fresh_and_stale_mirrors(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            source.mkdir()
            (source / "tracked.txt").write_text("tracked\n", encoding="utf-8")
            (source / ".git").write_text(
                "gitdir: /studio-only/.git/worktrees/fixture\n",
                encoding="utf-8",
            )
            (source / ".venv-qt").symlink_to(
                "/studio-only/.venv-qt",
                target_is_directory=True,
            )

            for stale in (False, True):
                with self.subTest(stale=stale):
                    destination = root / f"mirror-{stale}"
                    destination.mkdir()
                    if stale:
                        (destination / ".venv-qt").symlink_to(
                            "/previous-studio/.venv-qt",
                            target_is_directory=True,
                        )

                    subprocess.run(
                        run_remote_tests._rsync_command(
                            source,
                            f"{destination}/",
                        ),
                        check=True,
                        text=True,
                        capture_output=True,
                    )

                    self.assertEqual(
                        (destination / "tracked.txt").read_text(encoding="utf-8"),
                        "tracked\n",
                    )
                    self.assertFalse((destination / ".git").exists())
                    self.assertFalse((destination / ".venv-qt").is_symlink())

    def test_sync_recreates_only_the_remote_interpreter_link_and_preserves_old_mirror(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            source.mkdir()
            (source / "tracked.txt").write_text("tracked\n", encoding="utf-8")
            (source / ".venv-qt").symlink_to("/studio-only/.venv-qt")
            host_root = root / "remote host"
            mirror = host_root / run_remote_tests.REMOTE_REPO.name
            old_mirror = host_root / "repo"
            old_mirror.mkdir(parents=True)
            (old_mirror / "keep.txt").write_text("old mirror\n", encoding="utf-8")
            reports = host_root / "reports"
            reports.mkdir()
            (reports / "keep.log").write_text("old report\n", encoding="utf-8")
            venv = host_root / ".venv-qt"
            (venv / "bin").mkdir(parents=True)
            (venv / "bin" / "python").symlink_to(sys.executable)

            def local_ssh(command, *, label):
                return subprocess.run(
                    ("/bin/sh", "-c", command),
                    check=True, text=True, capture_output=True,
                ).stdout

            def local_rsync(command, *, label):
                local_command = (*command[:-1], command[-1].removeprefix(f"{run_remote_tests.HOST}:"))
                return subprocess.run(
                    local_command, check=True, text=True, capture_output=True,
                )

            with (
                patch.object(run_remote_tests, "REMOTE_ROOT", host_root),
                patch.object(run_remote_tests, "REMOTE_REPO", mirror),
                patch.object(run_remote_tests, "REMOTE_VENV", venv),
                patch.object(run_remote_tests, "_ssh", side_effect=local_ssh) as ssh,
                patch.object(run_remote_tests, "_run_with_retries", side_effect=local_rsync),
            ):
                for _ in range(2):
                    run_remote_tests._sync(source)
                    run_remote_tests._ssh(*ssh.call_args.args, **ssh.call_args.kwargs)
                    self.assertEqual(mirror.name, "ankiscape_fork")
                    self.assertEqual((mirror / ".venv-qt").readlink(), venv)
                    self.assertFalse((venv / ".venv-qt").is_symlink())
                    self.assertEqual((mirror / "tracked.txt").read_text(), "tracked\n")
                    executed = subprocess.run(
                        (str(mirror / ".venv-qt/bin/python"), "-c", "print('interpreter available')"),
                        check=True, text=True, capture_output=True,
                    )
                    self.assertEqual(executed.stdout, "interpreter available\n")
                    self.assertEqual((old_mirror / "keep.txt").read_text(), "old mirror\n")
                    self.assertEqual((reports / "keep.log").read_text(), "old report\n")

    def test_remote_mirror_lock_path_is_absolute_and_shared_across_imports(self):
        source = Path(run_remote_tests.__file__)
        probe = (
            "import json, os, runpy, sys\n"
            "path = runpy.run_path(sys.argv[1])['LOCAL_MIRROR_LOCK_PATH']\n"
            "print(json.dumps({\n"
            "    'pid': os.getpid(),\n"
            "    'absolute': path.is_absolute(),\n"
            "    'resolved': str(path.resolve()),\n"
            "}))\n"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            results = []
            for name in ("first", "second"):
                root = Path(temp_dir) / name
                root.mkdir()
                copy = Path(shutil.copy2(source, root / source.name))
                completed = subprocess.run(
                    (sys.executable, "-c", probe, str(copy)),
                    cwd=root,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                results.append(json.loads(completed.stdout))

        self.assertNotEqual(results[0]["pid"], results[1]["pid"])
        self.assertTrue(all(result["absolute"] for result in results))
        self.assertEqual(results[0]["resolved"], results[1]["resolved"])

    def test_remote_mirror_lock_reports_wait_before_blocking(self):
        worktree = Path(__file__).resolve().parents[1]
        complete = "Ran 4506 tests in 251.835s\n\nOK (skipped=512)\n"
        operations = []

        def flock(_descriptor: int, operation: int) -> None:
            operations.append(operation)
            if len(operations) == 1:
                raise BlockingIOError

        with tempfile.TemporaryDirectory() as temp_dir:
            lock_path = Path(temp_dir) / "mirror.lock"
            stderr = io.StringIO()
            with (
                patch.object(run_remote_tests, "_preflight"),
                patch.object(run_remote_tests, "LOCAL_MIRROR_LOCK_PATH", lock_path),
                patch.object(run_remote_tests.fcntl, "flock", side_effect=flock),
                patch.object(run_remote_tests, "_sync"),
                patch.object(
                    run_remote_tests,
                    "_stream_remote_run",
                    return_value=(0, complete),
                ),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(stderr),
            ):
                result = run_remote_tests.main([str(worktree), "plain"])

        self.assertEqual(result, 0)
        self.assertEqual(
            operations,
            [
                run_remote_tests.fcntl.LOCK_EX | run_remote_tests.fcntl.LOCK_NB,
                run_remote_tests.fcntl.LOCK_EX,
                run_remote_tests.fcntl.LOCK_UN,
            ],
        )
        self.assertEqual(
            stderr.getvalue(),
            f"Remote mirror busy; waiting for {lock_path}\n",
        )

    def test_remote_mirror_lock_wraps_sync_and_run_on_every_exit(self):
        worktree = Path(__file__).resolve().parents[1]
        complete = "Ran 4506 tests in 251.835s\n\nOK (skipped=512)\n"
        for failure_at in (None, "sync", "run"):
            with (
                self.subTest(failure_at=failure_at),
                tempfile.TemporaryDirectory() as temp_dir,
            ):
                events: list[object] = []

                def record_lock(_descriptor: int, operation: int) -> None:
                    events.append(operation)

                def sync(local_worktree: Path) -> None:
                    events.append("sync")
                    self.assertEqual(local_worktree, worktree)
                    if failure_at == "sync":
                        raise RuntimeError("remote sync failed")

                def run(*_args: object, **_kwargs: object) -> tuple[int, str]:
                    events.append("run")
                    if failure_at == "run":
                        raise RuntimeError("remote lane failed")
                    return 0, complete

                with (
                    patch.object(run_remote_tests, "_preflight"),
                    patch.object(
                        run_remote_tests,
                        "LOCAL_MIRROR_LOCK_PATH",
                        Path(temp_dir) / "mirror.lock",
                    ),
                    patch.object(
                        run_remote_tests.fcntl,
                        "flock",
                        side_effect=record_lock,
                    ),
                    patch.object(run_remote_tests, "_sync", side_effect=sync),
                    patch.object(run_remote_tests, "_stream_remote_run", side_effect=run),
                    contextlib.redirect_stdout(io.StringIO()),
                    contextlib.redirect_stderr(io.StringIO()),
                ):
                    result = run_remote_tests.main([str(worktree), "plain"])

                self.assertEqual(result, 0 if failure_at is None else 1)
                self.assertTrue((Path(temp_dir) / "mirror.lock").is_file())
                self.assertEqual(
                    events,
                    [
                        run_remote_tests.fcntl.LOCK_EX
                        | run_remote_tests.fcntl.LOCK_NB,
                        "sync",
                        *([] if failure_at == "sync" else ["run"]),
                        run_remote_tests.fcntl.LOCK_UN,
                    ],
                )

    def test_stream_reloads_log_after_completion_report_appears(self):
        complete = "....\nRan 4506 tests in 444.064s\n\nOK (skipped=3)\n"
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
        self.assertEqual(run_remote_tests.parse_unittest_summary(output).tests, 4506)


if __name__ == "__main__":
    unittest.main()
