import json
import multiprocessing
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.worktree_guard import (
    claim_owner,
    claimable_worktree,
    duplicate_enabled_addons,
    ensure_owner_ignored,
    owner_path,
    ownership_mismatch,
    read_owner,
    safe_worktree_root,
    unsafe_registered_worktrees,
    validate_worktree_name,
    worktree_paths,
)


def _claim_repeatedly(worktree: str, owner: str, rounds: int, barrier, results) -> None:
    path = Path(worktree)
    for _ in range(rounds):
        barrier.wait()
        try:
            claim_owner(path, owner)
        except RuntimeError:
            results.put(False)
        else:
            results.put(True)
        barrier.wait()


class WorktreeGuardTest(unittest.TestCase):
    def test_porcelain_paths_preserve_spaces(self):
        paths = worktree_paths("worktree /tmp/Anki Main\nHEAD abc\n\nworktree /tmp/feature tree\n")
        self.assertEqual(
            paths,
            (Path("/tmp/Anki Main").resolve(), Path("/tmp/feature tree").resolve()),
        )

    def test_only_linked_worktrees_inside_addons21_are_unsafe(self):
        canonical = Path("/tmp/Anki2/addons21/ankiscape_fork")
        paths = (
            canonical,
            Path("/tmp/Anki2/addons21/feature"),
            Path("/tmp/Anki2/ankiscape_worktrees/feature"),
        )
        self.assertEqual(
            unsafe_registered_worktrees(paths, canonical),
            (Path("/tmp/Anki2/addons21/feature").resolve(),),
        )
        self.assertEqual(
            safe_worktree_root(canonical),
            Path("/tmp/Anki2/ankiscape_worktrees").resolve(),
        )

    def test_duplicate_enabled_package_is_rejected_even_when_not_a_worktree(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            addons = Path(temp_dir) / "addons21"
            canonical = addons / "ankiscape_fork"
            duplicate = addons / "ankiscape_copy"
            for path, disabled in ((canonical, False), (duplicate, False)):
                path.mkdir(parents=True)
                (path / "__init__.py").write_text("", encoding="utf-8")
                (path / "meta.json").write_text(
                    json.dumps({"name": "AnkiScape RuneScape Anki", "disabled": disabled}),
                    encoding="utf-8",
                )
            self.assertEqual(duplicate_enabled_addons(addons, canonical), (duplicate.resolve(),))

    def test_owned_worktree_seen_by_a_different_owner_is_flagged(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            canonical = root / "addons21" / "ankiscape_fork"
            worktree = root / "ankiscape_worktrees" / "feature"
            canonical.mkdir(parents=True)
            worktree.mkdir(parents=True)
            claim_owner(worktree, "session-a")

            mismatch = ownership_mismatch(
                (canonical, worktree),
                canonical,
                worktree,
                "session-b",
            )

        self.assertEqual(mismatch, (worktree.resolve(), "session-a"))

    def test_unowned_worktree_remains_usable_and_owner_can_be_taken_over(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            worktree = Path(temp_dir)
            self.assertIsNone(read_owner(worktree))
            self.assertIsNone(claim_owner(worktree, "session-a"))
            with self.assertRaisesRegex(RuntimeError, "pass --take-over"):
                claim_owner(worktree, "session-b")
            self.assertEqual(
                claim_owner(worktree, "session-b", take_over=True),
                "session-a",
            )
            self.assertEqual(read_owner(worktree), "session-b")

    def test_simultaneous_claims_have_exactly_one_winner(self):
        rounds = 100
        context = multiprocessing.get_context("spawn")
        barrier = context.Barrier(3)
        results = context.Queue()
        with tempfile.TemporaryDirectory() as temp_dir:
            worktree = Path(temp_dir)
            processes = [
                context.Process(
                    target=_claim_repeatedly,
                    args=(temp_dir, owner, rounds, barrier, results),
                )
                for owner in ("session-a", "session-b")
            ]
            for process in processes:
                process.start()
            for iteration in range(rounds):
                path = owner_path(worktree)
                if path.exists():
                    path.unlink()
                barrier.wait()
                outcomes = [results.get(timeout=10), results.get(timeout=10)]
                barrier.wait()
                with self.subTest(iteration=iteration):
                    self.assertEqual(sum(outcomes), 1)
            for process in processes:
                process.join(timeout=10)
                self.assertEqual(process.exitcode, 0)

    def test_claim_target_must_be_a_registered_linked_worktree(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            canonical = root / "addons21" / "ankiscape_fork"
            worktree = root / "ankiscape_worktrees" / "feature"
            unknown = root / "ankiscape_worktrees" / "typo"
            paths = (canonical, worktree)
            for path in (*paths, unknown):
                path.mkdir(parents=True)

            self.assertEqual(claimable_worktree(paths, canonical, worktree), worktree.resolve())
            with self.assertRaisesRegex(ValueError, "canonical checkout cannot be claimed"):
                claimable_worktree(paths, canonical, canonical)
            with self.assertRaisesRegex(ValueError, "not a registered linked worktree"):
                claimable_worktree(paths, canonical, unknown)

    def test_owner_marker_is_ignored_across_branches_through_common_exclude(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            canonical = root / "canonical"
            worktree = root / "old-branch"
            subprocess.run(("git", "init", "-q", str(canonical)), check=True)
            (canonical / "tracked.txt").write_text("baseline\n", encoding="utf-8")
            subprocess.run(("git", "-C", str(canonical), "add", "tracked.txt"), check=True)
            subprocess.run(
                (
                    "git",
                    "-C",
                    str(canonical),
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "-qm",
                    "baseline",
                ),
                check=True,
            )
            subprocess.run(
                ("git", "-C", str(canonical), "worktree", "add", "-qb", "old", str(worktree)),
                check=True,
            )

            ensure_owner_ignored(worktree)
            ensure_owner_ignored(worktree)
            claim_owner(worktree, "session-a")
            status = subprocess.run(
                ("git", "-C", str(worktree), "status", "--short"),
                check=True,
                capture_output=True,
                text=True,
            )
            common_dir = subprocess.run(
                ("git", "-C", str(worktree), "rev-parse", "--git-common-dir"),
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            exclude = Path(common_dir)
            if not exclude.is_absolute():
                exclude = worktree / exclude
            entries = (exclude.resolve() / "info" / "exclude").read_text(encoding="utf-8").splitlines()

        self.assertEqual(status.stdout, "")
        self.assertIn(".ankiscape-worktree-owner", entries)

    def test_worktree_name_cannot_escape_safe_root(self):
        for name in ("", ".", "..", "../unsafe", "/tmp/unsafe", "nested/unsafe"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_worktree_name(name)
        self.assertEqual(validate_worktree_name("feature-name"), "feature-name")


if __name__ == "__main__":
    unittest.main()
