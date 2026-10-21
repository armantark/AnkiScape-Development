import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from tools import run_remote_tests
from tools.promotion.promotion_process import open_locked_file
from tools.promotion_gate import (
    FULL_GATE_CHECKS,
    PLAIN_GATE_CHECKS,
    GateError,
    GateEvidence,
    LockRecord,
    _run_gate_checks,
    _run_reachability_check,
    _run_check,
    _worktree_is_clean,
    active_gate_dir_for,
    active_gate_records,
    evidence_path_for,
    landing_lock_path_for,
    claim_landing_lock,
    land,
    main as promotion_main,
    register_gate,
    run_gate,
)
from tools.reachability.pins import read_reachability_pins


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_ACTION_FIELDS = ("action_count", "reachable_item_count")


def copy_reachability_tree(destination: Path) -> Path:
    shutil.copytree(
        PROJECT_ROOT,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )
    return destination.resolve()


def copy_running_gate(worktree: Path) -> Path:
    """Give a candidate the running gate's code, so the gate judges it in-process."""
    shutil.copytree(
        PROJECT_ROOT / "tools",
        worktree / "tools",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    return worktree.resolve()


def run_reachability_check(worktree: Path) -> tuple[int, str]:
    log = io.StringIO()
    returncode = _run_reachability_check(log, worktree)
    return returncode, log.getvalue()


def reachability_summary(pins: dict[str, int]) -> str:
    return (
        f"{pins['action_count']} actions; {pins['reachable_item_count']} reachable items; "
        f"{pins['orphan_input_count']} orphan inputs; "
        f"{pins['unresolved_action_count']} blocked actions"
    )


def pinned_summary(worktree: Path) -> str:
    return reachability_summary(read_reachability_pins(worktree))


def synthetic_reachability_tree(
    destination: Path,
    *,
    update_pins: bool,
) -> tuple[Path, str]:
    worktree = copy_reachability_tree(destination)
    action_path = worktree / "data" / "thieving_data.py"
    with action_path.open("a", encoding="utf-8") as stream:
        stream.write(
            '\nTHIEVING_TARGETS["promotion_gate_synthetic"] = {\n'
            '    "guaranteed": {"Promotion gate synthetic item": 1},\n'
            '}\n'
        )

    pins = read_reachability_pins(worktree)
    expected_pins = dict(pins)
    for field in SYNTHETIC_ACTION_FIELDS:
        expected_pins[field] += 1
    if update_pins:
        pin_path = worktree / "tests" / "test_item_reachability_audit.py"
        source = pin_path.read_text(encoding="utf-8")
        for field in SYNTHETIC_ACTION_FIELDS:
            old = f'self.assertEqual(report["{field}"], {pins[field]})'
            new = f'self.assertEqual(report["{field}"], {expected_pins[field]})'
            if source.count(old) != 1:
                raise AssertionError(f"Expected one synthetic pin target: {old}")
            source = source.replace(old, new, 1)
        pin_path.write_text(source, encoding="utf-8")
    return worktree, reachability_summary(expected_pins)


class PromotionRepo:
    def __init__(self, root: Path, *, descendant: bool = True):
        self.root = root.resolve()
        self.main = self.root / "addons21" / "ankiscape_fork"
        self.target = self.root / "ankiscape_worktrees" / "promotion"
        self.main.mkdir(parents=True)
        self.git(self.main, "init", "-q", "-b", "main")
        (self.main / "state.txt").write_text("main\n", encoding="utf-8")
        self.git(self.main, "add", "state.txt")
        self.git(self.main, "commit", "-q", "-m", "main")
        self.main_commit = self.head(self.main)

        if descendant:
            self.git(self.main, "branch", "promotion")
            self.git(self.main, "worktree", "add", "-q", str(self.target), "promotion")
            (self.target / "state.txt").write_text("promotion\n", encoding="utf-8")
            self.git(self.target, "add", "state.txt")
            self.git(self.target, "commit", "-q", "-m", "promotion")
        else:
            tree = self.git(self.main, "mktree", input_text="").stdout.strip()
            unrelated = self.git(
                self.main,
                "commit-tree",
                tree,
                input_text="unrelated\n",
            ).stdout.strip()
            self.git(self.main, "branch", "promotion", unrelated)
            self.git(self.main, "worktree", "add", "-q", str(self.target), "promotion")
        self.target_commit = self.head(self.target)

    @staticmethod
    def git(
        repo: Path,
        *args: str,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ("git", "-C", str(repo), *args),
            check=True,
            capture_output=True,
            text=True,
            input=input_text,
        )

    def head(self, repo: Path) -> str:
        return self.git(repo, "rev-parse", "HEAD").stdout.strip()

    def add_target(self, name: str) -> tuple[Path, str]:
        target = self.root / "ankiscape_worktrees" / name
        self.git(self.main, "worktree", "add", "-q", "-b", name, str(target), "main")
        (target / f"{name}.txt").write_text(f"{name}\n", encoding="utf-8")
        self.git(target, "add", f"{name}.txt")
        self.git(target, "commit", "-q", "-m", name)
        return target.resolve(), self.head(target)

    def write_unlocked_gate_marker(
        self,
        *,
        pid: int,
        commit: str,
        worktree: Path,
    ) -> Path:
        directory = active_gate_dir_for(self.main)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "unlocked-stale.json"
        record = LockRecord(
            pid=pid,
            operation="gate",
            worktree=str(worktree.resolve()),
            commit=commit,
            started_at="2026-08-22T05:00:00-07:00",
            token="unlocked-stale",
        )
        path.write_text(json.dumps(asdict(record)) + "\n", encoding="utf-8")
        return path


def pass_gate(
    repo: PromotionRepo,
    *,
    plain_only: bool = False,
    remote_lanes: bool = False,
) -> Path:
    checks = PLAIN_GATE_CHECKS if plain_only else FULL_GATE_CHECKS
    with patch("tools.promotion.lane_execution._run_gate_checks", return_value=(checks, ())):
        run_gate(
            repo.target,
            plain_only=plain_only,
            remote_lanes=remote_lanes,
            stdout=io.StringIO(),
        )
    return evidence_path_for(repo.target, repo.target_commit)


class PromotionGateTest(unittest.TestCase):
    def test_hung_lane_times_out_kills_children_and_records_refusal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            child_pid_path = Path(temp_dir) / "child.pid"
            command = (
                sys.executable,
                "-c",
                (
                    "import pathlib, subprocess, sys, time; "
                    "child=subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)']); "
                    f"pathlib.Path({str(child_pid_path)!r}).write_text(str(child.pid)); "
                    "child.wait()"
                ),
            )
            log = io.StringIO()

            returncode = _run_check(
                log,
                heading="=== hanging lane ===",
                command=command,
                worktree=PROJECT_ROOT,
                selector=lambda lines: lines,
                timeout=2.0,
            )

            self.assertEqual(returncode, 124)
            self.assertIn("TIMEOUT: exceeded 2 seconds", log.getvalue())
            child_pid = int(child_pid_path.read_text(encoding="utf-8"))
            self.assertNotEqual(
                subprocess.run(("ps", "-p", str(child_pid)), check=False).returncode,
                0,
            )

    def test_locked_file_closes_stream_when_path_stat_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "landing.lock"
            stream = path.open("a+", encoding="utf-8")
            with (
                patch.object(Path, "open", return_value=stream),
                patch.object(Path, "stat", side_effect=PermissionError("denied")),
            ):
                with self.assertRaisesRegex(PermissionError, "denied"):
                    open_locked_file(path, wait=False)
            self.assertTrue(stream.closed)

    def test_landing_lock_retries_when_contended_record_disappears(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            held = claim_landing_lock(
                repo.target,
                operation="landing",
                worktree=repo.target,
                commit=repo.target_commit,
            )

            def remove_record(_path: Path) -> LockRecord:
                held.release()
                raise FileNotFoundError

            with patch("tools.promotion.locking._read_record_path", side_effect=remove_record):
                acquired = claim_landing_lock(
                    repo.target,
                    operation="landing",
                    worktree=repo.target,
                    commit=repo.target_commit,
                )
            acquired.release()
            self.assertFalse(landing_lock_path_for(repo.target).exists())

    def test_landing_lock_refusal_includes_its_age(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            lock = claim_landing_lock(
                repo.target,
                operation="landing",
                worktree=repo.target,
                commit=repo.target_commit,
            )
            try:
                with self.assertRaisesRegex(GateError, r"held for \d+s"):
                    claim_landing_lock(
                        repo.target,
                        operation="landing",
                        worktree=repo.target,
                        commit=repo.target_commit,
                    )
            finally:
                lock.release()

    def test_stale_live_landing_lock_is_reclaimed_after_tree_kill(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            path = landing_lock_path_for(repo.target)
            script = (
                "import fcntl, json, os, sys, time; "
                "path=sys.argv[1]; stream=open(path, 'a+', encoding='utf-8'); "
                "fcntl.flock(stream.fileno(), fcntl.LOCK_EX); stream.seek(0); "
                "payload=json.load(stream); payload['pid']=os.getpid(); "
                "stream.seek(0); stream.truncate(); json.dump(payload, stream); stream.flush(); "
                "time.sleep(30)"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(
                    {
                        "pid": 0,
                        "operation": "running a gate",
                        "worktree": str(repo.target),
                        "commit": repo.target_commit,
                        "started_at": "2020-01-01T00:00:00+00:00",
                        "heartbeat_at": "2020-01-01T00:00:00+00:00",
                        "token": "stale",
                    }
                ),
                encoding="utf-8",
            )
            holder = subprocess.Popen((sys.executable, "-c", script, str(path)))
            try:
                deadline = time.monotonic() + 5
                published = False
                while holder.poll() is None and not published:
                    if time.monotonic() >= deadline:
                        self.fail("lock holder did not publish its pid")
                    try:
                        published = json.loads(path.read_text(encoding="utf-8"))["pid"] != 0
                    except (OSError, json.JSONDecodeError):
                        pass
                    time.sleep(0.01)
                self.assertTrue(published)
                acquired = claim_landing_lock(
                    repo.target,
                    operation="landing",
                    worktree=repo.target,
                    commit=repo.target_commit,
                )
                acquired.release()
                holder.wait(timeout=5)
                self.assertIsNotNone(holder.returncode)
            finally:
                if holder.poll() is None:
                    holder.kill()
                    holder.wait(timeout=5)

    def test_landing_without_a_passed_gate_is_refused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            evidence_path = evidence_path_for(repo.target, repo.target_commit)

            with self.assertRaisesRegex(
                GateError,
                rf"^Landing refused: no passed full-gate evidence for exact commit "
                rf"{repo.target_commit} at {evidence_path}$",
            ):
                land(repo.target)

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_failed_landing_releases_its_lock(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))

            with self.assertRaises(GateError):
                land(repo.target)

            self.assertFalse(landing_lock_path_for(repo.target).exists())

    def test_plain_only_gate_records_checks_but_does_not_authorize_landing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            evidence_path = pass_gate(repo, plain_only=True)
            payload = json.loads(evidence_path.read_text(encoding="utf-8"))

            self.assertEqual(payload["commit"], repo.target_commit)
            self.assertEqual(tuple(payload["passed_checks"]), PLAIN_GATE_CHECKS)
            self.assertIs(payload["remote_lanes"], False)
            with self.assertRaisesRegex(
                GateError,
                rf"^Landing refused: evidence for {repo.target_commit} did not pass every "
                rf"full-gate check; recorded {re.escape(str(PLAIN_GATE_CHECKS))}$",
            ):
                land(repo.target)

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_remote_gate_evidence_records_lane_origin(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            evidence_path = pass_gate(repo, remote_lanes=True)

            payload = json.loads(evidence_path.read_text(encoding="utf-8"))

            self.assertIs(payload["remote_lanes"], True)
            self.assertEqual(tuple(payload["passed_checks"]), FULL_GATE_CHECKS)

    def test_evidence_parser_defaults_old_records_to_local_lanes(self):
        payload = {
            "schema_version": 1,
            "commit": "abc123",
            "worktree": "/scratch/promotion",
            "plain_only": False,
            "passed_checks": list(FULL_GATE_CHECKS),
            "completed_at": "2026-08-27T17:00:00-07:00",
        }

        evidence = GateEvidence.from_json(json.dumps(payload))

        self.assertFalse(evidence.remote_lanes)
        payload["remote_lanes"] = "false"
        with self.assertRaisesRegex(GateError, "remote_lanes must be a boolean"):
            GateEvidence.from_json(json.dumps(payload))

    def test_running_gate_for_same_commit_cannot_land_early(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            marker = register_gate(repo.target, repo.target_commit)
            try:
                with self.assertRaisesRegex(
                    GateError,
                    rf"^Landing refused: gate PID {os.getpid()} is still running for exact "
                    rf"commit {repo.target_commit} in {repo.target} since ",
                ):
                    land(repo.target)
            finally:
                marker.release()

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_duplicate_gate_for_exact_commit_is_refused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            first = register_gate(repo.target, repo.target_commit)
            try:
                with self.assertRaisesRegex(
                    GateError,
                    rf"^Gate already running for exact commit {repo.target_commit}: PID "
                    rf"{os.getpid()} in {repo.target} since ",
                ):
                    register_gate(repo.target, repo.target_commit)
            finally:
                first.release()

    def test_gate_registration_waits_for_landing_coordination(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            landing_lock = claim_landing_lock(
                repo.target,
                operation="landing",
                worktree=repo.target,
                commit=repo.target_commit,
            )
            result = {}

            def register() -> None:
                try:
                    result["marker"] = register_gate(repo.target, repo.target_commit)
                except Exception as exc:  # pragma: no cover - asserted through result
                    result["error"] = exc

            thread = threading.Thread(target=register)
            thread.start()
            try:
                thread.join(timeout=0.1)
                self.assertTrue(thread.is_alive())
            finally:
                landing_lock.release()
                thread.join(timeout=5)

            self.assertFalse(thread.is_alive())
            self.assertNotIn("error", result)
            result["marker"].release()

    def test_second_landing_is_refused_while_landing_lock_is_held(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            landing_lock = claim_landing_lock(
                repo.target,
                operation="landing",
                worktree=repo.target,
                commit=repo.target_commit,
            )
            try:
                with self.assertRaisesRegex(
                    GateError,
                    rf"^Promotion landing lock held: PID {os.getpid()} is landing for "
                    rf"{repo.target_commit} in {repo.target} since ",
                ):
                    land(repo.target)
            finally:
                landing_lock.release()

    def test_independent_worktrees_can_register_gates_concurrently(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            other_target, other_commit = repo.add_target("promotion-b")
            first = register_gate(repo.target, repo.target_commit)
            second = None
            try:
                second = register_gate(other_target, other_commit)
                active = active_gate_records(repo.main, stderr=io.StringIO())
                self.assertEqual(
                    {record.commit for record in active},
                    {repo.target_commit, other_commit},
                )
            finally:
                if second is not None:
                    second.release()
                first.release()

    def test_gate_for_another_tree_refuses_landing_and_names_the_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            pass_gate(repo)
            marker = register_gate(repo.main, repo.main_commit)
            try:
                with self.assertRaisesRegex(
                    GateError,
                    rf"^Landing refused: running gate PID {os.getpid()} has held "
                    rf"{repo.main_commit} in {repo.main} since .*; requested "
                    rf"{repo.target_commit} in {repo.target} is a different tree$",
                ):
                    land(repo.target)
            finally:
                marker.release()

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_unlocked_marker_with_live_unrelated_pid_is_stale(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            pass_gate(repo)
            sleeper = subprocess.Popen(
                (sys.executable, "-c", "import time; time.sleep(30)"),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            try:
                marker_path = repo.write_unlocked_gate_marker(
                    pid=sleeper.pid,
                    commit=repo.main_commit,
                    worktree=repo.main,
                )
                stderr = io.StringIO()

                landed = land(repo.target, stdout=io.StringIO(), stderr=stderr)

                self.assertEqual(landed, repo.target_commit)
                self.assertEqual(repo.head(repo.main), repo.target_commit)
                self.assertFalse(marker_path.exists())
                self.assertIsNone(sleeper.poll())
                self.assertIn(
                    f"Stale promotion gate marker: it recorded gate PID {sleeper.pid}",
                    stderr.getvalue(),
                )
            finally:
                sleeper.terminate()
                sleeper.wait(timeout=5)

    def test_non_descendant_tree_is_refused_before_git_merge(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir), descendant=False)
            pass_gate(repo)

            with self.assertRaisesRegex(
                GateError,
                rf"^Landing refused: {repo.target_commit} in {repo.target} is not a descendant "
                rf"of current main {repo.main_commit}$",
            ):
                land(repo.target)

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_passed_full_gate_fast_forwards_main(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            evidence_path = pass_gate(repo)
            payload = json.loads(evidence_path.read_text(encoding="utf-8"))
            stdout = io.StringIO()

            landed = land(repo.target, stdout=stdout)

            self.assertEqual(payload["commit"], repo.target_commit)
            self.assertEqual(tuple(payload["passed_checks"]), FULL_GATE_CHECKS)
            self.assertFalse(payload["plain_only"])
            self.assertIs(payload["remote_lanes"], False)
            self.assertEqual(landed, repo.target_commit)
            self.assertEqual(repo.head(repo.main), repo.target_commit)
            self.assertFalse(landing_lock_path_for(repo.target).exists())
            self.assertIn(f"Landed {repo.target_commit}", stdout.getvalue())

    def test_failed_rerun_removes_prior_landable_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            evidence_path = pass_gate(repo)
            self.assertTrue(evidence_path.exists())

            with patch(
                "tools.promotion.lane_execution._run_gate_checks",
                return_value=(("plain lane",), ("audit_docs (exit 1)",)),
            ):
                with self.assertRaisesRegex(
                    GateError,
                    r"^Gate failed: audit_docs \(exit 1\)\. Log: ",
                ):
                    run_gate(repo.target, plain_only=False, stdout=io.StringIO())

            self.assertFalse(evidence_path.exists())
            self.assertEqual(active_gate_records(repo.main, stderr=io.StringIO()), ())
            with self.assertRaisesRegex(GateError, "no passed full-gate evidence"):
                land(repo.target)

    def test_remote_lanes_flag_reaches_run_gate(self):
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch("tools.promotion.cli.run_gate") as gate,
        ):
            worktree = copy_running_gate(Path(temp_dir))
            result = promotion_main(["run", str(worktree), "--remote-lanes"])

        self.assertEqual(result, 0)
        gate.assert_called_once_with(
            worktree,
            plain_only=False,
            remote_lanes=True,
        )

    def test_dirty_canonical_checkout_refuses_gate_before_any_lane(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            copy_running_gate(repo.target)
            (repo.main / "state.txt").write_text("dirty\n", encoding="utf-8")
            stderr = io.StringIO()

            with (
                patch(
                    "tools.promotion.lane_execution._run_check"
                ) as run_check,
                patch("sys.stderr", stderr),
            ):
                with self.assertRaisesRegex(SystemExit, r"^2$"):
                    promotion_main(["run", str(repo.target)])

            self.assertEqual(
                stderr.getvalue(),
                "error: Gate refused: canonical checkout has uncommitted "
                "tracked changes:\n M state.txt\n",
            )
            run_check.assert_not_called()

    def test_untracked_canonical_file_does_not_refuse_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            pending = repo.main / "memory-bank" / "pending"
            pending.mkdir(parents=True)
            (pending / "note.md").write_text("untracked\n", encoding="utf-8")

            with (
                patch(
                    "tools.promotion.lane_execution._run_check",
                    return_value=0,
                ),
                patch(
                    "tools.promotion.lane_execution._run_reachability_check",
                    return_value=0,
                ),
            ):
                log_path = run_gate(
                    repo.target,
                    plain_only=False,
                    stdout=io.StringIO(),
                )

            self.assertTrue(log_path.exists())

    def test_default_gate_uses_local_lane_commands(self):
        canonical = Path("/canonical/ankiscape_fork")
        with (
            patch("tools.promotion.lane_execution.main_worktree", return_value=canonical),
            patch("tools.promotion.lane_execution._run_check", return_value=0) as run_check,
            patch("tools.promotion.lane_execution._run_reachability_check", return_value=0),
            patch("tools.promotion.lane_execution._run_papercut_check", return_value=0),
        ):
            passed, failures = _run_gate_checks(
                Path("/scratch/promotion"),
                source_worktree=Path("/scratch/promotion"),
                plain_only=False,
                log=io.StringIO(),
            )

        lane_calls = {
            call.kwargs["heading"]: call
            for call in run_check.call_args_list
            if call.kwargs["heading"]
            in ("=== PLAIN LANE ===", "=== QT LANE (monolithic) ===")
        }
        self.assertEqual(
            lane_calls["=== PLAIN LANE ==="].kwargs["command"],
            ("/opt/homebrew/bin/python3", "run_tests.py", "--processes", "8"),
        )
        self.assertIsNone(lane_calls["=== PLAIN LANE ==="].kwargs["environment"])
        self.assertEqual(
            lane_calls["=== QT LANE (monolithic) ==="].kwargs["command"],
            (str(canonical / ".venv-qt" / "bin" / "python"), "run_tests.py", "--processes", "8"),
        )
        self.assertEqual(
            lane_calls["=== QT LANE (monolithic) ==="].kwargs["environment"],
            {"QT_QPA_PLATFORM": "offscreen"},
        )
        self.assertEqual(passed, FULL_GATE_CHECKS)
        self.assertEqual(failures, ())

    def test_remote_gate_uses_exact_serial_runner_commands(self):
        worktree = Path("/scratch/promotion")
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch.object(run_remote_tests, "LOCAL_MIRROR_LOCK_PATH", Path(temp_dir) / "mirror.lock"),
            patch("tools.promotion.lane_execution.main_worktree") as main_worktree,
            patch("tools.promotion.lane_execution._run_check", return_value=0) as run_check,
            patch("tools.promotion.lane_execution._run_reachability_check", return_value=0),
            patch("tools.promotion.lane_execution._run_papercut_check", return_value=0),
        ):
            passed, failures = _run_gate_checks(
                worktree,
                source_worktree=worktree,
                plain_only=False,
                remote_lanes=True,
                log=io.StringIO(),
            )

        lane_calls = [
            call
            for call in run_check.call_args_list
            if call.kwargs["heading"]
            in ("=== PLAIN LANE ===", "=== QT LANE (monolithic) ===")
        ]
        diagnostics = ["FAIL: first regression", *(f"detail {index}" for index in range(60)),
                       "ERROR: last regression", "FAILED (failures=1, errors=1)"]
        for call in lane_calls:
            self.assertEqual(call.kwargs["selector"]([".sEF", *diagnostics]), diagnostics)
        self.assertEqual(
            [call.kwargs["command"] for call in lane_calls],
            [
                (
                    "/opt/homebrew/bin/python3",
                    "tools/run_remote_tests.py",
                    str(worktree.resolve()),
                    "plain",
                ),
                (
                    "/opt/homebrew/bin/python3",
                    "tools/run_remote_tests.py",
                    str(worktree.resolve()),
                    "qt",
                ),
            ],
        )
        mirror_lock = lane_calls[0].kwargs["pass_fds"]
        self.assertEqual(len(mirror_lock), 1)
        self.assertEqual(
            [(call.kwargs["environment"], call.kwargs["pass_fds"]) for call in lane_calls],
            [({run_remote_tests.INHERITED_MIRROR_LOCK_FD: str(mirror_lock[0])}, mirror_lock)] * 2,
        )
        main_worktree.assert_not_called()
        self.assertEqual(passed, FULL_GATE_CHECKS)
        self.assertEqual(failures, ())

    def test_remote_plain_only_gate_omits_qt_runner(self):
        worktree = Path("/scratch/promotion")
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch.object(run_remote_tests, "LOCAL_MIRROR_LOCK_PATH", Path(temp_dir) / "mirror.lock"),
            patch("tools.promotion.lane_execution.main_worktree") as main_worktree,
            patch("tools.promotion.lane_execution._run_check", return_value=0) as run_check,
            patch("tools.promotion.lane_execution._run_reachability_check", return_value=0),
            patch("tools.promotion.lane_execution._run_papercut_check", return_value=0),
        ):
            passed, failures = _run_gate_checks(
                worktree,
                source_worktree=worktree,
                plain_only=True,
                remote_lanes=True,
                log=io.StringIO(),
            )

        lane_calls = [
            call
            for call in run_check.call_args_list
            if call.kwargs["heading"]
            in ("=== PLAIN LANE ===", "=== QT LANE (monolithic) ===")
        ]
        self.assertEqual(len(lane_calls), 1)
        self.assertEqual(
            lane_calls[0].kwargs["command"],
            (
                "/opt/homebrew/bin/python3",
                "tools/run_remote_tests.py",
                str(worktree.resolve()),
                "plain",
            ),
        )
        self.assertEqual(
            lane_calls[0].kwargs["environment"],
            {run_remote_tests.INHERITED_MIRROR_LOCK_FD: str(lane_calls[0].kwargs["pass_fds"][0])},
        )
        main_worktree.assert_not_called()
        self.assertEqual(passed, PLAIN_GATE_CHECKS)
        self.assertEqual(failures, ())

    def test_dirty_worktree_fails_clean_commit_check(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            (repo.target / "untracked.txt").write_text("not in the commit\n", encoding="utf-8")
            log = io.StringIO()

            returncode = _run_check(
                log,
                heading="=== worktree clean ===",
                command=("git", "status", "--porcelain", "--untracked-files=all"),
                worktree=repo.target,
                selector=lambda lines: lines or ["clean"],
                validator=_worktree_is_clean,
            )

            self.assertEqual(returncode, 1)
            self.assertIn("?? untracked.txt", log.getvalue())
            self.assertTrue(log.getvalue().endswith("FAILED: exit 0\n"))

    def test_reachability_tree_matching_its_own_pins_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            worktree = copy_reachability_tree(Path(temp_dir))
            self.assertFalse((worktree / ".git").exists())

            returncode, log = run_reachability_check(worktree)

            self.assertEqual(returncode, 0)
            self.assertEqual(log, f"=== reachability ===\n{pinned_summary(worktree)}\n")

    def test_reachability_content_addition_with_updated_pins_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            worktree, expected_summary = synthetic_reachability_tree(
                Path(temp_dir),
                update_pins=True,
            )

            returncode, log = run_reachability_check(worktree)

            self.assertEqual(returncode, 0)
            self.assertEqual(log, f"=== reachability ===\n{expected_summary}\n")

    def test_reachability_content_addition_without_updated_pins_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            worktree, expected_summary = synthetic_reachability_tree(
                Path(temp_dir),
                update_pins=False,
            )

            returncode, log = run_reachability_check(worktree)

            self.assertEqual(returncode, 1)
            self.assertEqual(
                log,
                f"=== reachability ===\n{expected_summary}\nFAILED: exit 0\n",
            )

    def test_reachability_warning_on_stderr_does_not_corrupt_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            worktree = copy_reachability_tree(Path(temp_dir))
            audit_path = worktree / "tools" / "audit_item_reachability.py"
            source = audit_path.read_text(encoding="utf-8")
            source = source.replace(
                "import sys\n",
                "import sys\n\nprint('DeprecationWarning: something', file=sys.stderr)\n",
                1,
            )
            audit_path.write_text(source, encoding="utf-8")

            returncode, log = run_reachability_check(worktree)

            self.assertEqual(returncode, 0)
            self.assertEqual(
                log,
                f"=== reachability ===\n{pinned_summary(worktree)}\n"
                "DeprecationWarning: something\n",
            )

    def test_promotion_docs_explain_tree_owned_reachability_pins(self):
        # Assert the contract, not exact sentences: an editor who rephrases
        # these passages must not redden the gate, but deleting the
        # explanation must still fail.
        patterns = (
            PROJECT_ROOT / "memory-bank" / "systemPatterns.md"
        ).read_text(encoding="utf-8").lower()
        chronology = (
            PROJECT_ROOT / "memory-bank" / "source-audits"
            / "systempatterns-chronology-2026-09-16.md"
        ).read_text(encoding="utf-8").lower()
        # Papercut triage moves addressed records verbatim into dated
        # papercuts-fixed-*.md files, so the record may live in any of them.
        memory_bank = PROJECT_ROOT / "memory-bank"
        papercuts = "\n\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in (
                memory_bank / "papercuts.md",
                *sorted(memory_bank.glob("papercuts-fixed-*.md")),
            )
        )

        pattern_paragraphs = [
            p for p in patterns.split("\n\n") if "reachabilit" in p
        ]
        self.assertTrue(
            any("pin" in p and "gated tree" in p for p in pattern_paragraphs),
            "systemPatterns.md must explain that reachability pins come "
            "from the gated tree",
        )
        self.assertIn(
            "supersedes",
            chronology,
            "the systemPatterns chronology must identify the superseded papercut",
        )
        self.assertIn(
            "2026-08-22 05:52",
            chronology,
            "the systemPatterns chronology must identify the superseded papercut by date",
        )
        superseded_paragraphs = [
            p for p in papercuts.split("\n\n") if "superseded" in p
        ]
        self.assertTrue(
            any("pin" in p and "gated tree" in p for p in superseded_paragraphs),
            "the 2026-08-22 05:52 papercut must record its superseding rule",
        )

    def test_reachability_audit_crashing_after_summary_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            worktree = copy_reachability_tree(Path(temp_dir))
            summary = pinned_summary(worktree)
            (worktree / "tools" / "audit_item_reachability.py").write_text(
                f"print({summary!r})\nraise RuntimeError('audit crashed')\n",
                encoding="utf-8",
            )

            returncode, log = run_reachability_check(worktree)

            self.assertEqual(returncode, 1)
            self.assertIn(summary, log)
            self.assertIn("RuntimeError: audit crashed", log)
            self.assertTrue(log.endswith("FAILED: exit 1\n"))

    def test_reachability_audit_failing_after_a_matching_report_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            worktree = Path(temp_dir).resolve()
            (worktree / "tests").mkdir()
            (worktree / "tools").mkdir()
            shutil.copy2(
                PROJECT_ROOT / "tests" / "test_item_reachability_audit.py",
                worktree / "tests" / "test_item_reachability_audit.py",
            )
            pins = read_reachability_pins(worktree)
            (worktree / "tools" / "audit_item_reachability.py").write_text(
                f"import json\nprint(json.dumps({pins!r}))\nraise SystemExit(1)\n",
                encoding="utf-8",
            )

            returncode, log = run_reachability_check(worktree)

            self.assertEqual(returncode, 1)
            self.assertEqual(
                log,
                f"=== reachability ===\n{reachability_summary(pins)}\nFAILED: exit 1\n",
            )

    def test_reachability_audit_without_summary_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            worktree = copy_reachability_tree(Path(temp_dir))
            (worktree / "tools" / "audit_item_reachability.py").write_text(
                "raise SystemExit(1)\n",
                encoding="utf-8",
            )

            returncode, log = run_reachability_check(worktree)

            self.assertEqual(returncode, 1)
            self.assertEqual(log, "=== reachability ===\nFAILED: exit 1\n")


if __name__ == "__main__":
    unittest.main()
