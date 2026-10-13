import contextlib
import io
import resource
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

    def test_report_retention_runs_only_after_pending_reconciliation_and_source_sync(self):
        events = []
        with patch.object(run_remote_tests, "_reconcile_pending_run", side_effect=lambda: events.append("pending")), \
                patch.object(run_remote_tests, "_run_with_retries", side_effect=lambda *args, **kwargs: events.append("sync")), \
                patch.object(run_remote_tests, "_ssh", side_effect=lambda *args, **kwargs: events.append(kwargs["label"])) as ssh:
            run_remote_tests._sync(Path("/disposable/source"))
        self.assertEqual(events, ["pending", "remote mirror setup", "sync", "remote Qt interpreter link",
                                  "remote report retention"])
        command = ssh.call_args.args[0]
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
        before = resource.getrlimit(resource.RLIMIT_FSIZE)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            owner = root / "owner-sentinel"
            owner.write_bytes(b"owner unchanged")
            proof = root / "proof.bin"
            log = root / "lane.log"
            child = ("import os,signal,sys;signal.signal(signal.SIGXFSZ,signal.SIG_DFL);"
                     "print('storage-limit canary',flush=True);"
                     "fd=os.open(sys.argv[1],os.O_WRONLY|os.O_CREAT,0o600);"
                     "os.write(fd,b'x'*2048);os.write(fd,b'x')")
            script = shlex.join((sys.executable, "-c", child, str(proof)))
            with patch.object(run_remote_tests, "MAX_PROOF_FILE_BYTES", 1024), log.open("wb") as output:
                completed = subprocess.run((sys.executable, "-c", run_remote_tests.LANE_GROUP_LEADER,
                                            script, str(run_remote_tests.MAX_PROOF_FILE_BYTES)),
                                           stdout=output, stderr=subprocess.STDOUT, check=False)
            self.assertNotEqual(completed.returncode, 0)
            self.assertLessEqual(proof.stat().st_size, 1024)
            self.assertIn("storage-limit canary", log.read_text())
            self.assertEqual(owner.read_bytes(), b"owner unchanged")
        self.assertEqual(resource.getrlimit(resource.RLIMIT_FSIZE), before)

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

