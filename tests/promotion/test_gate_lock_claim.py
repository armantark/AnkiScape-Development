import io
import os
import subprocess
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from tests.test_promotion_gate import PromotionRepo
from tools.promotion.lane_execution import _git as run_git
from tools.promotion_gate import (
    FULL_GATE_CHECKS,
    GateError,
    install_hook,
    landing_lock_path_for,
    main_worktree,
    run_gate,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def attempt_main_commit(
    repo: PromotionRepo,
    message: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        (
            "git",
            "-C",
            str(repo.main),
            "commit",
            "--allow-empty",
            "-m",
            message,
        ),
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)},
    )


class GateLockClaimTest(unittest.TestCase):
    def test_main_commit_is_refused_before_canonical_resolution(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            install_hook(repo.main)
            resolving_canonical = threading.Event()
            continue_gate = threading.Event()

            def pause_before_canonical_check(worktree: Path) -> Path:
                resolving_canonical.set()
                if not continue_gate.wait(timeout=5):
                    raise TimeoutError("gate did not resume")
                return main_worktree(worktree)

            with (
                patch(
                    "tools.promotion.lane_execution.main_worktree",
                    side_effect=pause_before_canonical_check,
                ),
                patch(
                    "tools.promotion.lane_execution._run_gate_checks",
                    return_value=(FULL_GATE_CHECKS, ()),
                ),
            ):
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        run_gate,
                        repo.target,
                        plain_only=False,
                        stdout=io.StringIO(),
                    )
                    try:
                        self.assertTrue(resolving_canonical.wait(timeout=5))
                        commit = attempt_main_commit(
                            repo,
                            "immediate main commit",
                        )
                        self.assertEqual(
                            commit.returncode,
                            1,
                            commit.stdout + commit.stderr,
                        )
                        self.assertRegex(
                            commit.stderr,
                            rf"^Commit refused: promotion gate holds "
                            rf"{repo.target_commit} \(PID \d+\) for \d+s\.",
                        )
                    finally:
                        continue_gate.set()
                    future.result(timeout=5)

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_main_commit_is_refused_while_lanes_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            install_hook(repo.main)
            lanes_running = threading.Event()
            continue_gate = threading.Event()

            def pause_lanes(*_args, **_kwargs):
                lanes_running.set()
                if not continue_gate.wait(timeout=5):
                    raise TimeoutError("lanes did not resume")
                return FULL_GATE_CHECKS, ()

            with patch(
                "tools.promotion.lane_execution._run_gate_checks",
                side_effect=pause_lanes,
            ):
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        run_gate,
                        repo.target,
                        plain_only=False,
                        stdout=io.StringIO(),
                    )
                    try:
                        self.assertTrue(lanes_running.wait(timeout=5))
                        commit = attempt_main_commit(
                            repo,
                            "mid-lane main commit",
                        )
                        self.assertEqual(
                            commit.returncode,
                            1,
                            commit.stdout + commit.stderr,
                        )
                        self.assertRegex(
                            commit.stderr,
                            rf"^Commit refused: promotion gate holds "
                            rf"{repo.target_commit} \(PID \d+\) for \d+s\.",
                        )
                    finally:
                        continue_gate.set()
                    future.result(timeout=5)

            self.assertEqual(repo.head(repo.main), repo.main_commit)

    def test_dirty_canonical_refusal_releases_claimed_lock(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = PromotionRepo(Path(temp_dir))
            (repo.main / "state.txt").write_text("dirty\n", encoding="utf-8")
            lock_seen_during_check = []

            def observe_status(worktree: Path, *args: str, **kwargs):
                if args[:2] == ("status", "--porcelain"):
                    lock_seen_during_check.append(
                        landing_lock_path_for(repo.target).exists()
                    )
                return run_git(worktree, *args, **kwargs)

            with (
                patch(
                    "tools.promotion.lane_execution._git",
                    side_effect=observe_status,
                ),
                patch(
                    "tools.promotion.lane_execution._run_gate_checks"
                ) as run_checks,
            ):
                with self.assertRaisesRegex(
                    GateError,
                    "canonical checkout has uncommitted tracked changes",
                ):
                    run_gate(
                        repo.target,
                        plain_only=False,
                        stdout=io.StringIO(),
                    )

            self.assertEqual(lock_seen_during_check, [True])
            self.assertFalse(landing_lock_path_for(repo.target).exists())
            run_checks.assert_not_called()


if __name__ == "__main__":
    unittest.main()
