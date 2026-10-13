import contextlib
import errno
import io
import json
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests import test_remote_test_host
from tools import run_remote_tests


class RemoteStorageTests(unittest.TestCase):
    _worktree = test_remote_test_host.RemoteTestHostTests._worktree

    def test_direct_runner_reaches_preflight_from_an_unrelated_working_directory(self):
        worktree = self._worktree()
        root = self._worktree()
        binary = root / "bin"
        binary.mkdir()
        ssh = binary / "ssh"
        ssh.write_text("#!/bin/sh\necho TEST_PREFLIGHT_REFUSAL >&2\nexit 7\n")
        ssh.chmod(0o755)
        canary_env = dict(os.environ)
        canary_env.pop("PYTHONPATH", None)
        canary_env["PATH"] = str(binary) + ":/usr/bin:/bin"
        completed = subprocess.run(
            (sys.executable, run_remote_tests.__file__, str(worktree), "plain",
             "--select", "tests.", "--collect-only"),
            cwd=root, env=canary_env, text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("TEST_PREFLIGHT_REFUSAL", completed.stderr)
        self.assertNotIn("ModuleNotFoundError", completed.stderr)
        self.assertEqual((worktree / "run_tests.py").read_text(), "launch\n")

    def test_report_retention_runs_only_after_pending_reconciliation_and_source_sync(self):
        events = []
        with patch.object(run_remote_tests, "_reconcile_pending_run", side_effect=lambda: events.append("pending")), \
                patch.object(run_remote_tests, "_run_with_retries", side_effect=lambda *args, **kwargs: events.append("sync")), \
                patch.object(run_remote_tests, "_ssh", side_effect=lambda *args, **kwargs: events.append(kwargs["label"])) as ssh:
            run_remote_tests._sync(Path("/disposable/source"))
        self.assertEqual(events, ["pending", "remote mirror setup", "sync",
                                  "remote interpreter and report retention"])
        command = ssh.call_args.args[0]
        self.assertTrue(command.startswith("ln "))
        self.assertIn(f"cd {shlex.quote(str(run_remote_tests.REMOTE_REPO))} &&", command)
        self.assertIn(f"{shlex.quote(str(run_remote_tests.REMOTE_VENV / 'bin/python'))} -m tools.maintenance.report_retention", command)
        self.assertTrue(command.endswith(f"{shlex.quote(str(run_remote_tests.REMOTE_ROOT / 'reports'))} --apply"))
        self.assertTrue(ssh.call_args.kwargs["repeat_safe"])
        with patch.object(run_remote_tests, "_reconcile_pending_run", side_effect=RuntimeError("pending")), \
                patch.object(run_remote_tests, "_ssh") as ssh:
            with self.assertRaisesRegex(RuntimeError, "pending"):
                run_remote_tests._sync(Path("/disposable/source"))
        ssh.assert_not_called()

    def test_lane_file_limit_stops_oversize_descendant_and_preserves_parent_and_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            owner = root / "owner-sentinel"
            owner.write_bytes(b"owner unchanged")
            proof = root / "proof.bin"
            log = root / "lane.log"
            child = "\n".join((
                "import json,os,signal,sys",
                "if sys.argv[2] == 'signal': signal.signal(signal.SIGXFSZ,signal.SIG_DFL)",
                "fd=os.open(sys.argv[1],os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)",
                "try:",
                "    os.write(fd,b'x'*2048);os.write(fd,b'x')",
                "except OSError as error:",
                "    print(json.dumps({'errno':error.errno}),flush=True)",
                "    raise",
            ))
            for mode in ("signal", "python"):
                with self.subTest(mode=mode):
                    script = shlex.join((sys.executable, "-c", child, str(proof), mode))
                    with log.open("wb") as output:
                        completed = subprocess.run(
                            (sys.executable, "-c", run_remote_tests.LANE_GROUP_LEADER, script, "1024"),
                            stdout=output, stderr=subprocess.STDOUT, check=False,
                        )
                    self.assertEqual(completed.returncode, -signal.SIGXFSZ if mode == "signal" else 1)
                    self.assertLessEqual(proof.stat().st_size, 1024)
                    if mode == "python":
                        with log.open() as stream:
                            self.assertEqual(json.loads(stream.readline()), {"errno": errno.EFBIG})
                    self.assertEqual(owner.read_bytes(), b"owner unchanged")

    def test_only_sigxfsz_exit_is_labeled_as_the_storage_limit(self):
        arguments = run_remote_tests._parse_args([str(self._worktree()), "plain"])
        with self.assertRaisesRegex(RuntimeError, "per-file storage limit.*SIGXFSZ"):
            run_remote_tests._validated_summary_lines(arguments, 128 + signal.SIGXFSZ, "")
        with self.assertRaisesRegex(RuntimeError, "failed with exit 1") as failure:
            run_remote_tests._validated_summary_lines(arguments, 1, "")
        self.assertNotIn("storage limit", str(failure.exception))

    def test_launch_snapshot_keeps_independent_files_and_rsync_exclusions(self):
        worktree = self._worktree()
        (worktree / "state.py").write_text("launch\n")
        for name in (".git", ".venv-qt", "__pycache__"):
            (worktree / name).mkdir()
            (worktree / name / "ignored").write_text("exclude\n")
        (worktree / "ankiscape_debug.log").write_text("exclude\n")

        def sync(snapshot):
            self.assertEqual({p.name for p in snapshot.iterdir()}, {"run_tests.py", "state.py"})
            (snapshot / "state.py").write_text("private mutation\n")
            self.assertEqual((worktree / "state.py").read_text(), "launch\n")

        with (patch.object(run_remote_tests, "LOCAL_MIRROR_LOCK_PATH", self._worktree() / "lock"),
              patch.object(run_remote_tests, "_preflight"),
              patch.object(run_remote_tests, "_sync", side_effect=sync),
              patch.object(run_remote_tests, "_stream_remote_run", return_value=(0, "Ran 1 test in 0.1s\n\nOK\n")),
              contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO())):
            self.assertEqual(run_remote_tests.main([str(worktree), "plain", "--select", "x.",
                                                   "--expected-tests", "1"]), 0)

