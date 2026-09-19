import fcntl
import io
import json
import os
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import Mock, patch

from tools import worktree_guard as guard
from tools.promotion import locking


class WorktreeReleaseSafetyTest(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        temporary = self.stack.enter_context(tempfile.TemporaryDirectory())
        self.root = Path(temporary).resolve()
        self.canonical = self.root / "Anki2/addons21/ankiscape_fork"
        self.pooled = guard.pool_root(self.canonical) / "slot/ankiscape_fork"
        self.common = self.root / "git-common"
        self.common.mkdir()
        self.stack.enter_context(patch.object(
            guard, "canonical_and_paths",
            return_value=(self.canonical, (self.canonical, self.pooled)),
        ))
        self.stack.enter_context(patch.object(locking, "git_common_dir", return_value=self.common))
        self.git = self.stack.enter_context(patch.object(guard, "_git", side_effect=self.git_result))
        self.pool = self.stack.enter_context(patch.object(guard, "_treehouse", side_effect=self.pool_result))
        self.stack.enter_context(patch.object(guard, "audit"))
        self.kill = self.stack.enter_context(patch.object(
            locking, "kill_process_tree", side_effect=AssertionError("must never signal"),
        ))
        self.markers = locking.active_gate_dir_for(self.canonical)
        self.markers.mkdir()

    def git_result(self, _repo, *args, **_kwargs):
        return Mock(stdout="frozen-head\n" if args[0] == "rev-parse" else "", returncode=0)

    def lease_row(self):
        return {"path": str(self.pooled), "status": "leased", "lease_id": "lease-1"}

    def pool_result(self, _canonical, *args):
        return Mock(stdout=json.dumps([self.lease_row()]) if args == ("status", "--json") else "")

    def marker_bytes(self, worktree):
        record = locking._new_lock_record("gate", worktree, "frozen-head")
        record = replace(record, started_at="2000-01-01T00:00:00+00:00",
                         heartbeat_at="2000-01-01T00:00:00+00:00")
        return json.dumps(asdict(record)).encode()

    def assert_no_return(self):
        self.pool.assert_not_called()
        self.assertNotIn("checkout", [call.args[1] for call in self.git.call_args_list])
        self.kill.assert_not_called()

    def test_matching_gate_refuses_even_when_old_and_unlocked(self):
        path = self.markers / "gate.json"
        original = self.marker_bytes(self.pooled)
        for held in (False, True):
            with self.subTest(held=held), ExitStack() as streams:
                path.write_bytes(original)
                if held:
                    stream = streams.enter_context(path.open("r+"))
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaisesRegex(RuntimeError, "promotion gate marker.*names"):
                    guard.release_worktree(self.canonical, self.pooled, "lease-1")
                self.assertEqual(path.read_bytes(), original)
                self.assertEqual(json.loads(path.read_bytes())["pid"], os.getpid())
                self.assert_no_return()

    def test_unreadable_markers_refuse_without_rewriting_bytes(self):
        path = self.markers / "gate.json"
        relative = json.loads(self.marker_bytes(self.pooled))
        relative["worktree"] = "relative/path"
        for original in (b"{broken", b"\xff", b"{}", json.dumps(relative).encode()):
            with self.subTest(original=original):
                path.write_bytes(original)
                with self.assertRaisesRegex(RuntimeError, "unreadable promotion gate marker"):
                    guard.release_worktree(self.canonical, self.pooled, "lease-1")
                self.assertEqual(path.read_bytes(), original)
                self.assert_no_return()

    def test_contended_coordination_never_recovers_old_or_unreadable_owner(self):
        held = locking.claim_landing_lock(
            self.canonical, operation="gate", worktree=self.pooled, commit="frozen-head",
        )
        self.addCleanup(held.release)
        for original in (self.marker_bytes(self.pooled), b"{unreadable"):
            with self.subTest(original=original):
                held.stream.seek(0)
                held.stream.truncate()
                held.stream.write(original.decode())
                held.stream.flush()
                with self.assertRaisesRegex(locking.GateError, "stale recovery is disabled"):
                    guard.release_worktree(self.canonical, self.pooled, "lease-1")
                self.assertEqual(held.path.read_bytes(), original)
                self.assert_no_return()

    def test_marker_directory_enumeration_failure_refuses_return(self):
        path = self.markers / "gate.json"
        original = self.marker_bytes(self.pooled)
        path.write_bytes(original)
        with patch.object(Path, "iterdir", side_effect=PermissionError("denied")):
            with self.assertRaisesRegex(RuntimeError, "marker directory is unreadable"):
                guard.release_worktree(self.canonical, self.pooled, "lease-1")
        self.assertEqual(path.read_bytes(), original)
        self.assert_no_return()

    def assert_coordination_held(self):
        with self.assertRaisesRegex(locking.GateError, "stale recovery is disabled"):
            locking.claim_landing_lock(
                self.canonical, operation="contender", worktree=self.pooled,
                commit="other", recover_stale=False,
            )

    def test_unrelated_marker_is_preserved_and_lock_covers_detach_and_return(self):
        path = self.markers / "other.json"
        original = self.marker_bytes(self.root / "other-worktree")
        path.write_bytes(original)
        events = []

        def git_result(repo, *args, **kwargs):
            if args[0] == "checkout":
                self.assert_coordination_held()
                events.append("detach")
            return self.git_result(repo, *args, **kwargs)

        def return_lease(*args):
            self.assert_coordination_held()
            if args[1:] == ("status", "--json"):
                return self.pool_result(*args)
            self.assertEqual(args[1:], ("return", "--force", "--if-lease-id", "lease-1", str(self.pooled)))
            events.append("return")

        self.git.side_effect = git_result
        self.pool.side_effect = return_lease
        guard.release_worktree(self.canonical, self.pooled, "lease-1")
        self.assertEqual(events, ["detach", "return"])
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(locking.landing_lock_path_for(self.canonical).exists())
        self.kill.assert_not_called()

    def test_failed_return_releases_coordination_without_touching_other_marker(self):
        path = self.markers / "other.json"
        original = self.marker_bytes(self.root / "other-worktree")
        path.write_bytes(original)

        def fail_return(*args):
            if args[1:] == ("status", "--json"):
                return self.pool_result(*args)
            raise RuntimeError("pool return failed")

        self.pool.side_effect = fail_return
        with self.assertRaisesRegex(RuntimeError, "pool return failed"):
            guard.release_worktree(self.canonical, self.pooled, "lease-1")
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(locking.landing_lock_path_for(self.canonical).exists())
        self.kill.assert_not_called()

    def test_invalid_lease_refuses_before_detach_or_pool_return(self):
        row = self.lease_row()
        cases = [json.dumps(rows) for rows in (
            [], [row, row], [{**row, "lease_id": "other"}],
            [{**row, "status": "available"}], [{}], {"unexpected": []},
        )]
        cases.append("{invalid")
        for payload in cases:
            with self.subTest(payload=payload):
                self.pool.reset_mock()
                self.git.reset_mock()
                self.pool.side_effect = None
                self.pool.return_value = Mock(stdout=payload)
                with self.assertRaisesRegex(RuntimeError, "refusing return"):
                    guard.release_worktree(self.canonical, self.pooled, "lease-1")
                self.pool.assert_called_once_with(self.canonical, "status", "--json")
                self.assertNotIn("checkout", [call.args[1] for call in self.git.call_args_list])
                self.assertFalse(locking.landing_lock_path_for(self.canonical).exists())
                self.kill.assert_not_called()

    def test_duplicate_branch_refuses_before_pool_allocation(self):
        interpreter = self.canonical / ".venv-qt/bin/python"
        interpreter.parent.mkdir(parents=True)
        interpreter.write_text("")
        self.git.return_value = Mock(stdout=(
            f"worktree {self.canonical}\nbranch refs/heads/main\n\n"
            f"worktree {self.pooled}\nbranch refs/heads/goal/occupied\n\n"
        ))
        self.git.side_effect = None
        for branch in ("goal/occupied", "refs/heads/goal/occupied"):
            with self.subTest(branch=branch), self.assertRaisesRegex(RuntimeError, "already checked out"):
                guard.lease_worktree(self.canonical, branch, "new-owner", "main")
        self.pool.assert_not_called()
        self.assertTrue(all(call.args[1:4] == ("worktree", "list", "--porcelain")
                            for call in self.git.call_args_list))

    def test_qualified_available_branch_checks_out_existing_short_name(self):
        interpreter = self.canonical / ".venv-qt/bin/python"
        interpreter.parent.mkdir(parents=True)
        interpreter.write_text("")
        self.pooled.mkdir(parents=True)

        def git_result(repo, *args, **kwargs):
            if args[0] == "show-ref":
                return Mock(returncode=0 if args[-1] == "refs/heads/goal/available" else 1)
            return self.git_result(repo, *args, **kwargs)

        self.git.side_effect = git_result
        self.pool.side_effect = None
        self.pool.return_value = Mock(stdout=json.dumps(self.lease_row()))
        with redirect_stdout(io.StringIO()) as output:
            guard.lease_worktree(self.canonical, "refs/heads/goal/available", "owner", "main")
        calls = [call.args[1:] for call in self.git.call_args_list]
        self.assertIn(("show-ref", "--verify", "--quiet", "refs/heads/goal/available"), calls)
        self.assertEqual([args for args in calls if args[0] == "checkout"],
                         [("checkout", "goal/available")])
        self.assertEqual(json.loads(output.getvalue())["branch"], "goal/available")

    def test_status_cli_pins_pool_root_and_forwards_json_without_mutation(self):
        # Exercise the real subprocess argv construction, replacing only execution.
        self.stack.close()
        for json_flag in ([], ["--json"]):
            with (
                self.subTest(json_flag=json_flag),
                patch.object(guard, "canonical_and_paths", return_value=(self.canonical, (self.canonical,))),
                patch.object(guard.subprocess, "run", return_value=Mock(returncode=0, stdout="[]\n")) as run,
                redirect_stdout(io.StringIO()) as output,
            ):
                self.assertEqual(guard.main(["--repo", str(self.canonical), "status", *json_flag]), 0)
                self.assertEqual(output.getvalue(), "[]\n")
                run.assert_called_once_with(
                    ("treehouse", "status", *json_flag, "--root", str(guard.pool_root(self.canonical))),
                    text=True, capture_output=True, cwd=str(self.canonical),
                )
