import contextlib
import io
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

from tools import run_remote_tests
from tools.native import freeze_source

# The fixture's run_tests.py: one real unittest that fails unless the lane runs in the mirror,
# on the launch snapshot, outside the runner's group and environment, without the mirror lock.
LANE_TEST = """\
import contextlib, os, sys, unittest
from pathlib import Path

class Lane(unittest.TestCase):
    def test_lane_runs_isolated_in_the_mirror(self):
        self.assertEqual(Path.cwd(), Path({mirror!r}))
        self.assertEqual(Path("snapshot.txt").read_text(), "launched\\n")
        self.assertNotIn("ANKISCAPE_RUNNER_ONLY", os.environ)
        self.assertEqual(os.environ["HOME"], {home!r})
        self.assertNotEqual(os.getpgrp(), {runner_group})
        lock = os.stat({lock!r})
        for descriptor in os.listdir("/dev/fd"):
            with contextlib.suppress(OSError):
                self.assertFalse(os.path.samestat(os.fstat(int(descriptor)), lock))
        Path("lane-output.txt").write_text("mirror only\\n")

unittest.main(argv=["run_tests.py"])
"""


class LocalTestHostTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.lock = self.root / "mirror.lock"
        self.enterContext(patch.object(run_remote_tests, "LOCAL_MIRROR_LOCK_PATH", self.lock))

    @contextlib.contextmanager
    def _host(self, *, local: bool) -> Iterator[tuple[Path, Path, Path]]:
        """A disposable source worktree and test host whose PATH `ssh` records every call."""
        source, host, tools = self.root / "source", self.root / "host", self.root / "bin"
        mirror = host / "ankiscape_fork"
        for directory in (
            source / "tools/maintenance", mirror, host / "reports", host / ".venv-qt/bin", tools,
            host / "plain-site/PIL", host / "game-main/data/cfg", host / "darkan/data/npcs/combatdefs",
            host / "darkan/developer-information",
        ):
            directory.mkdir(parents=True)
        (source / "run_tests.py").write_text(LANE_TEST.format(
            mirror=str(mirror), home=os.path.expanduser("~"), runner_group=os.getpgrp(), lock=str(self.lock),
        ))
        (source / "snapshot.txt").write_text("launched\n")
        (source / ".venv-qt").symlink_to("/studio-only/.venv-qt")
        shutil.copy2(Path(run_remote_tests.__file__).parent / "maintenance/report_retention.py",
                     source / "tools/maintenance")
        (mirror / "stale.txt").write_text("previous run\n")
        (host / ".venv-qt/bin/python").symlink_to(sys.executable)
        (host / "reports/.retained.json").write_text("[]\n")
        for fixture in ("plain-site/PIL/__init__.py", "game-main/data/cfg/items.yml",
                        "darkan/developer-information/npcList.txt", "darkan/developer-information/beasts.txt"):
            (host / fixture).write_text("")
        (tools / "ssh").write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$0.calls"\n')
        (tools / "ssh").chmod(0o755)
        with (
            patch.object(run_remote_tests, "_on_test_host", return_value=local),
            patch.object(run_remote_tests, "REMOTE_ROOT", host),
            patch.object(run_remote_tests, "REMOTE_REPO", mirror),
            patch.object(run_remote_tests, "REMOTE_VENV", host / ".venv-qt"),
            patch.object(run_remote_tests, "REMOTE_PLAIN_SITE", host / "plain-site"),
            patch.object(run_remote_tests, "REMOTE_GAME_MAIN", host / "game-main"),
            patch.object(run_remote_tests, "REMOTE_DARKAN", host / "darkan"),
            patch.dict(os.environ, {"PATH": f"{tools}:{os.environ['PATH']}", "ANKISCAPE_RUNNER_ONLY": "leak"}),
        ):
            os.environ.pop(run_remote_tests.INHERITED_MIRROR_LOCK_FD, None)
            yield source, mirror, tools / "ssh.calls"

    def _main(self, source: Path) -> tuple[int, str, str]:
        with (
            contextlib.redirect_stdout(io.StringIO()) as stdout,
            contextlib.redirect_stderr(io.StringIO()) as stderr,
        ):
            returncode = run_remote_tests.main([
                str(source), "plain", "--select", "lane", "--expected-tests", "1",
                "--timeout", "60", "--poll-interval", "0.1",
            ])
        return returncode, stdout.getvalue(), stderr.getvalue()

    def test_runner_on_the_test_host_runs_the_snapshot_locally_without_ssh(self):
        with self._host(local=True) as (source, mirror, ssh_calls):
            preflight = run_remote_tests._preflight

            def edit_after_snapshot(lane):
                (source / "snapshot.txt").write_text("edited while queued\n")
                preflight(lane)

            before = {path: path.read_bytes() for path in source.rglob("*") if path.is_file()}
            with patch.object(run_remote_tests, "_preflight", side_effect=edit_after_snapshot):
                returncode, stdout, stderr = self._main(source)
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertFalse(ssh_calls.exists())
            self.assertIn("Remote focused plain lane summary:\nRan 1 test in ", stdout)
            self.assertEqual((mirror / "snapshot.txt").read_text(), "launched\n")
            self.assertEqual((mirror / "lane-output.txt").read_text(), "mirror only\n")
            self.assertFalse((mirror / "stale.txt").exists())
            self.assertEqual((mirror / ".venv-qt").readlink(), run_remote_tests.REMOTE_VENV)
            after = {path: path.read_bytes() for path in source.rglob("*") if path.is_file()}
            self.assertEqual(after, before | {source / "snapshot.txt": b"edited while queued\n"})
        self.assertFalse(run_remote_tests._pending_path().exists())

    def test_native_packet_transfer_on_test_host_stays_local(self):
        with self._host(local=True) as (source, _mirror, ssh_calls):
            output = source / "packet"
            output.mkdir()
            archive = b"native packet transport fixture"
            (output / "source.tar.gz").write_bytes(archive)
            (output / "manifest.json").write_text(json.dumps({"commit": "local-proof"}))
            digest = hashlib.sha256(archive).hexdigest()
            with (
                patch.object(freeze_source, "REMOTE_ROOT", run_remote_tests.REMOTE_ROOT),
                patch.object(freeze_source, "REMOTE_VENV", run_remote_tests.REMOTE_VENV),
                patch.object(freeze_source, "_on_test_host", return_value=True, create=True),
            ):
                freeze_source._transfer_bundle(output, "local-proof", digest)
            self.assertFalse(ssh_calls.exists())
            received = run_remote_tests.REMOTE_ROOT / "native-input/local-proof"
            self.assertEqual((received / "source.tar.gz").read_bytes(), archive)
            self.assertEqual(
                json.loads((output / "remote-transfer.json").read_text())["received"],
                {"commit": "local-proof", "archive_sha256": digest},
            )

    def test_distant_runner_keeps_ssh_and_never_touches_the_local_mirror(self):
        with (
            self._host(local=False) as (source, mirror, ssh_calls),
            patch.object(run_remote_tests.time, "sleep"),
        ):
            returncode, _stdout, stderr = self._main(source)
            self.assertEqual(returncode, 1)
            self.assertIn("worktree sync failed after 3 attempts", stderr)
            calls = ssh_calls.read_text().splitlines()
            self.assertTrue(all(call.startswith("-o BatchMode=yes -o ConnectTimeout=10 armans-macbook-pro ")
                                for call in calls), calls)
            self.assertEqual([call.split()[5] for call in calls], ["test", "mkdir", *["rsync"] * 3])
            self.assertEqual({path.name for path in mirror.iterdir()}, {"stale.txt"})

    def test_stalled_local_command_cannot_hold_the_mirror_past_its_deadline(self):
        with self._host(local=True) as (_source, _mirror, ssh_calls):
            reports = run_remote_tests.REMOTE_ROOT / "reports"
            # A pipe held open for writing and never written stalls every read until cleanup.
            os.mkfifo(reports / "qt-stalled.pid")
            reader = os.open(reports / "qt-stalled.pid", os.O_RDONLY | os.O_NONBLOCK)
            self.addCleanup(os.close, reader)
            self.addCleanup(os.close, os.open(reports / "qt-stalled.pid", os.O_WRONLY))
            record = json.dumps({"run_id": "qt-stalled"} | {
                f"{field}_path": str(reports / f"qt-stalled.{field}") for field in ("log", "report", "pid")
            })
            for action in (run_remote_tests.stop_pending_lane, run_remote_tests._reconcile_pending_run):
                run_remote_tests._pending_path().write_text(record)
                started = time.monotonic()
                with (
                    patch.object(run_remote_tests, "LANE_STOP_TIMEOUT", 1.0),
                    self.assertRaisesRegex(RuntimeError, "process group read did not finish before its deadline"),
                ):
                    action()
                self.assertLess(time.monotonic() - started, 5.0)
                self.assertEqual(run_remote_tests._pending_path().read_text(), record)
            self.assertFalse(ssh_calls.exists())

    def test_only_a_host_name_that_resolves_to_this_machine_is_local(self):
        self.addCleanup(run_remote_tests._on_test_host.cache_clear)
        for host, local in (
            ("localhost", True), ("127.0.0.1", True),
            ("192.0.2.1", False), ("ankiscape-test-host.invalid", False),
        ):
            with self.subTest(host=host), patch.object(run_remote_tests, "HOST", host):
                run_remote_tests._on_test_host.cache_clear()
                self.assertIs(run_remote_tests._on_test_host(), local)
                # One run never changes transport, even if the name later resolves elsewhere.
                with patch.object(run_remote_tests, "HOST", "192.0.2.1" if local else "localhost"):
                    self.assertIs(run_remote_tests._on_test_host(), local)


if __name__ == "__main__":
    unittest.main()
