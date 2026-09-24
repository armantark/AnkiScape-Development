import contextlib
import io
import json
import shutil
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import run_remote_tests


class RemoteTestHostTests(unittest.TestCase):
    def test_focused_arguments_refuse_incomplete_or_empty_selection_before_network(self):
        root = str(Path(__file__).resolve().parents[1])
        cases = (
            ["--select", "test_remote_test_host"],
            ["--expected-tests", "1"],
            ["--select", "test_remote_test_host", "--expected-tests", "0"],
            ["--select", "", "--expected-tests", "1"],
        )
        for arguments in cases:
            with (
                self.subTest(arguments=arguments),
                patch.object(run_remote_tests, "_preflight") as preflight,
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit) as result,
            ):
                run_remote_tests.main([root, "plain", *arguments])
            self.assertEqual(result.exception.code, 2)
            preflight.assert_not_called()

    def test_focused_run_requires_exact_count_and_zero_skips_without_lowering_full_floor(self):
        root = str(Path(__file__).resolve().parents[1])
        cases = (
            ("Ran 1 test in 0.1s\n\nOK\n", 0),
            ("Ran 2 tests in 0.1s\n\nOK\n", 1),
            ("Ran 1 test in 0.1s\n\nOK (skipped=1)\n", 1),
            ("Ran 1 test in 0.1s\n", 1),
        )
        for output, expected in cases:
            with (
                self.subTest(output=output),
                patch.object(run_remote_tests, "_preflight"),
                patch.object(run_remote_tests, "_sync"),
                patch.object(run_remote_tests, "_stream_remote_run", return_value=(0, output)) as run,
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                result = run_remote_tests.main([
                    root, "plain", "--select", "test_remote_test_host", "--expected-tests", "1",
                ])
            self.assertEqual(result, expected)
            self.assertEqual(run.call_args.kwargs["selectors"], ["test_remote_test_host"])
        summary = run_remote_tests.parse_unittest_summary(cases[0][0])
        with self.assertRaisesRegex(RuntimeError, "expected at least 4506"):
            run_remote_tests.validate_test_summary("plain", summary)

    def test_focused_commands_quote_selectors_and_preserve_full_lane_commands(self):
        selectors = ("tests/test_remote_test_host.py", "name with 'quotes'; $(false)")
        for lane in ("plain", "qt"):
            with self.subTest(lane=lane):
                focused = shlex.split(run_remote_tests._remote_lane_command(lane, selectors=selectors))
                self.assertEqual(focused[-5:], ["run_tests.py", "--quiet", "--", *selectors])
                full = run_remote_tests._remote_lane_command(lane)
                self.assertNotIn("--quiet", full)
                if lane == "qt":
                    self.assertTrue(full.endswith("-m unittest discover tests"))
                else:
                    self.assertTrue(full.endswith("run_tests.py"))

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        lock_patch = patch.object(
            run_remote_tests, "LOCAL_MIRROR_LOCK_PATH", Path(temporary.name) / "mirror.lock"
        )
        lock_patch.start()
        self.addCleanup(lock_patch.stop)

    def test_ssh_does_not_replay_remote_failures_or_arbitrary_commands(self):
        for returncode, repeat_safe in ((1, False), (2, True), (255, False)):
            with self.subTest(returncode=returncode, repeat_safe=repeat_safe):
                result = subprocess.CompletedProcess((), returncode, "test stdout", "test stderr")
                with (
                    patch.object(run_remote_tests.subprocess, "run", return_value=result) as execute,
                    patch.object(run_remote_tests.time, "sleep") as sleep,
                    self.assertRaises(run_remote_tests.SSHCommandError) as failure,
                ):
                    run_remote_tests._ssh("test-command", label="test lane", repeat_safe=repeat_safe)
                self.assertEqual(execute.call_count, 1)
                sleep.assert_not_called()
                self.assertEqual(failure.exception.returncode, returncode)
                self.assertIn("test stdout", str(failure.exception))
                self.assertIn("test stderr", str(failure.exception))

    def test_repeat_safe_ssh_retries_only_255_with_existing_bound(self):
        failed = subprocess.CompletedProcess((), 255, "", "connection lost")
        success = subprocess.CompletedProcess((), 0, "report", "")
        for results, expected_attempts in (((failed, success), 2), ((failed,) * 3, 3)):
            with (
                self.subTest(expected_attempts=expected_attempts),
                patch.object(run_remote_tests.subprocess, "run", side_effect=results) as execute,
                patch.object(run_remote_tests.time, "sleep") as sleep,
            ):
                if results[-1].returncode:
                    with self.assertRaises(run_remote_tests.SSHCommandError):
                        run_remote_tests._ssh("cat report", label="report", repeat_safe=True)
                else:
                    self.assertEqual(
                        run_remote_tests._ssh("cat report", label="report", repeat_safe=True), "report"
                    )
                self.assertEqual(execute.call_count, expected_attempts)
                self.assertEqual(sleep.call_count, expected_attempts - 1)

    def test_disconnected_launch_reconciles_same_run_and_preserves_failure(self):
        commands = []

        def execute(command, **_kwargs):
            remote = command[-1]
            commands.append(remote)
            if remote.startswith("nohup "):
                self.assertTrue(run_remote_tests._pending_path().is_file())
                return subprocess.CompletedProcess(command, 255, "", "connection lost after launch")
            return subprocess.CompletedProcess(command, 0, "2\n" if ".report " in remote else "test failed\n", "")

        with (
            patch.object(run_remote_tests.subprocess, "run", side_effect=execute),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            returncode, output = run_remote_tests._stream_remote_run("qt", timeout=1, poll_interval=0.01)
        self.assertEqual(returncode, 2)
        self.assertEqual(output, "test failed\n")
        self.assertEqual(stdout.getvalue(), "test failed\n")
        self.assertEqual(sum(command.startswith("nohup ") for command in commands), 1)
        self.assertFalse(any("rm -f" in command for command in commands))
        self.assertFalse(run_remote_tests._pending_path().exists())
        report_command = next(command for command in commands if ".report " in command)
        self.assertIn(report_command.split()[1], commands[0])

    def test_interrupted_run_keeps_exact_identity_until_completion_in_both_lanes(self):
        for lane in ("plain", "qt"):
            with self.subTest(lane=lane):
                launches = []
                report = [""]

                def execute(command, **_kwargs):
                    remote = command[-1]
                    if remote.startswith("nohup "):
                        launches.append(remote)
                        return subprocess.CompletedProcess(command, 255, "", "connection lost")
                    return subprocess.CompletedProcess(command, 0, report[0], "")

                with (
                    patch.object(run_remote_tests.subprocess, "run", side_effect=execute),
                    patch.object(run_remote_tests.time, "monotonic", side_effect=(0, 2)),
                    contextlib.redirect_stderr(io.StringIO()),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    with self.assertRaises(TimeoutError):
                        run_remote_tests._stream_remote_run(lane, timeout=1, poll_interval=0.01)
                    original = run_remote_tests._pending_path().read_bytes()
                    pending = json.loads(original)
                    with self.assertRaisesRegex(RuntimeError, "sync blocked"):
                        run_remote_tests._reconcile_pending_run()
                    self.assertEqual(run_remote_tests._pending_path().read_bytes(), original)
                    self.assertEqual(len(launches), 1)
                    self.assertIn(pending["report_path"], launches[0])
                    report[0] = "23\n"
                    run_remote_tests._reconcile_pending_run()
                    self.assertFalse(run_remote_tests._pending_path().exists())
                    self.assertEqual(len(launches), 1)

    def test_unresolved_run_blocks_next_sync_after_launch_poll_or_timeout_failure(self):
        worktree = Path(__file__).resolve().parents[1]
        for failure_at in ("launch", "poll", "timeout"):
            with self.subTest(failure_at=failure_at), tempfile.TemporaryDirectory() as temp_dir:
                launches = []

                def execute(command, **_kwargs):
                    remote = command[-1]
                    if remote.startswith("nohup "):
                        launches.append(remote)
                        code = 2 if failure_at == "launch" else 255
                        return subprocess.CompletedProcess(command, code, "launch output", "launch error")
                    if ".log " in remote and failure_at == "poll":
                        return subprocess.CompletedProcess(command, 255, "", "poll disconnected")
                    return subprocess.CompletedProcess(command, 0, "", "")

                with (
                    patch.object(run_remote_tests, "LOCAL_MIRROR_LOCK_PATH", Path(temp_dir) / "mirror.lock"),
                    patch.object(run_remote_tests, "_preflight"),
                    patch.object(run_remote_tests, "_run_with_retries") as rsync,
                    patch.object(run_remote_tests.subprocess, "run", side_effect=execute) as subprocess_run,
                    patch.object(run_remote_tests.time, "sleep"),
                    patch.object(run_remote_tests.time, "monotonic", side_effect=(0, 2)),
                    contextlib.redirect_stdout(io.StringIO()),
                    contextlib.redirect_stderr(io.StringIO()) as stderr,
                ):
                    args = [str(worktree), "qt", "--timeout", "1"]
                    self.assertEqual(run_remote_tests.main(args), 1)
                    mutations = [
                        call.args[0][-1] for call in subprocess_run.call_args_list
                        if not call.args[0][-1].startswith("cat ")
                    ]
                    self.assertEqual(len(mutations), 3)
                    self.assertTrue(mutations[0].startswith("mkdir "))
                    self.assertTrue(mutations[1].startswith("ln "))
                    self.assertTrue(mutations[2].startswith("nohup "))
                    pending_path = run_remote_tests._pending_path()
                    original = pending_path.read_bytes()
                    pending = json.loads(original)
                    self.assertEqual(run_remote_tests.main(args), 1)
                    with self.assertRaises(RuntimeError) as failure:
                        run_remote_tests._sync(worktree)
                    self.assertEqual(pending_path.read_bytes(), original)
                    self.assertEqual(rsync.call_count, 1)
                    self.assertEqual(len(launches), 1)
                    self.assertEqual(mutations, [
                        call.args[0][-1] for call in subprocess_run.call_args_list
                        if not call.args[0][-1].startswith("cat ")
                    ])
                    self.assertIn(str(pending_path), str(failure.exception))
                    self.assertIn(pending["run_id"], str(failure.exception))
                    self.assertIn(pending["log_path"], str(failure.exception))
                    self.assertIn(pending["report_path"], str(failure.exception))
                    self.assertIn(pending["run_id"], stderr.getvalue())
                    self.assertIn(pending["log_path"], stderr.getvalue())
                    self.assertIn(pending["report_path"], stderr.getvalue())
                    self.assertIn("Read-only inspection:", stderr.getvalue())
                    self.assertIn(pending["report_path"], subprocess_run.call_args.args[0][-1])

    def test_pending_run_only_releases_mirror_after_valid_completion(self):
        pending_path = run_remote_tests._pending_path()
        pending = {
            "run_id": "qt-prior", "log_path": "/reports/qt-prior.log",
            "report_path": "/reports/qt-prior.report",
        }
        with (
            patch.object(run_remote_tests.subprocess, "run") as execute,
            patch.object(run_remote_tests, "_run_with_retries") as rsync,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            malformed = [json.dumps(value) for value in (
                None, [], {}, pending | {"run_id": ""},
                pending | {"log_path": 17}, pending | {"report_path": " "},
            )] + ["{"]
            for record in malformed:
                with self.subTest(record=record):
                    pending_path.write_text(record)
                    with self.assertRaises(RuntimeError) as failure:
                        run_remote_tests._sync(Path("/source"))
                    self.assertIn(str(pending_path), str(failure.exception))
                    self.assertEqual(pending_path.read_text(), record)
                    execute.assert_not_called()
                    rsync.assert_not_called()
            pending_path.write_text(json.dumps(pending))
            for report in ("", "partial", "256"):
                execute.return_value = subprocess.CompletedProcess((), 0, report, "")
                with self.assertRaises(RuntimeError):
                    run_remote_tests._sync(Path("/source"))
                self.assertTrue(pending_path.is_file())
                rsync.assert_not_called()
                self.assertTrue(all(
                    call.args[0][-1].startswith("cat ") for call in execute.call_args_list
                ))
            execute.return_value = subprocess.CompletedProcess((), 0, "1\n", "")
            run_remote_tests._sync(Path("/source"))
            rsync.assert_called_once()
            self.assertTrue(execute.call_args_list[-2].args[0][-1].startswith("mkdir "))
            self.assertTrue(execute.call_args_list[-1].args[0][-1].startswith("ln "))
        self.assertFalse(pending_path.exists())

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

            def local_ssh(command, *, label, repeat_safe=False):
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
