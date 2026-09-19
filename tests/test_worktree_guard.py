import io
import json
import shlex
import sys
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from tools.native import session_guard as native
from tools.worktree_guard import (
    add_worktree,
    delete_preserved,
    duplicate_enabled_addons,
    lease_worktree,
    list_preserved,
    pool_root,
    release_worktree,
    safe_worktree_root,
    unsafe_registered_worktrees,
    validate_worktree_name,
    worktree_paths,
)


class WorktreeGuardTest(unittest.TestCase):
    def test_porcelain_paths_preserve_spaces(self):
        paths = worktree_paths("worktree /tmp/Anki Main\nHEAD abc\n\nworktree /tmp/feature tree\n")
        self.assertEqual(
            paths,
            (Path("/tmp/Anki Main").resolve(), Path("/tmp/feature tree").resolve()),
        )

    def test_only_canonical_descendants_are_exempt_inside_addons21(self):
        canonical = Path("/tmp/Anki2/addons21/ankiscape_fork")
        sibling = Path("/tmp/Anki2/addons21/feature")
        other_addon_nested = Path("/tmp/Anki2/addons21/other_addon/feature")
        paths = (
            canonical,
            canonical / "test-harness/worktree",
            sibling,
            other_addon_nested,
            Path("/tmp/Anki2/ankiscape_worktrees/feature"),
        )
        self.assertEqual(
            unsafe_registered_worktrees(paths, canonical),
            (sibling.resolve(), other_addon_nested.resolve()),
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

    def test_add_fails_before_worktree_creation_without_qt_interpreter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            canonical = (Path(temp_dir) / "Anki2/addons21/ankiscape_fork").resolve()
            canonical.mkdir(parents=True)
            qt_interpreter = canonical / ".venv-qt/bin/python"
            worktree_root = safe_worktree_root(canonical)
            with (
                patch("tools.worktree_guard.audit"),
                patch(
                    "tools.worktree_guard.canonical_and_paths",
                    return_value=(canonical, (canonical,)),
                ),
                patch("tools.worktree_guard._git") as git,
            ):
                with self.assertRaises(RuntimeError) as context:
                    add_worktree(canonical, "feature", None, "main")

            self.assertEqual(
                str(context.exception),
                f"Qt test interpreter not found: {qt_interpreter}",
            )
            git.assert_not_called()
            self.assertFalse(worktree_root.exists())

    def test_add_creates_absolute_qt_environment_symlink(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            canonical = (Path(temp_dir) / "Anki2/addons21/ankiscape_fork").resolve()
            qt_environment = canonical / ".venv-qt"
            qt_interpreter = qt_environment / "bin/python"
            qt_interpreter.parent.mkdir(parents=True)
            qt_interpreter.write_text("", encoding="utf-8")
            destination = safe_worktree_root(canonical) / "feature"

            def fake_git(_canonical, *args, **_kwargs):
                if args[:2] == ("worktree", "add"):
                    destination.mkdir(parents=True)
                return Mock(returncode=1)

            with (
                patch("tools.worktree_guard.audit"),
                patch(
                    "tools.worktree_guard.canonical_and_paths",
                    return_value=(canonical, (canonical,)),
                ),
                patch("tools.worktree_guard._git", side_effect=fake_git),
            ):
                add_worktree(canonical, "feature", None, "main")

            link = destination / ".venv-qt"
            self.assertTrue(link.is_symlink())
            self.assertTrue(link.readlink().is_absolute())
            self.assertEqual(link.readlink(), qt_environment)

    def test_release_refuses_uncommitted_work(self):
        canonical = Path("/tmp/Anki2/addons21/ankiscape_fork")
        pooled = pool_root(canonical) / ".treehouse/ankiscape_fork-1/1/ankiscape_fork"
        with (
            patch("tools.worktree_guard.locking.claim_landing_lock"),
            patch("tools.worktree_guard.require_no_gate_markers"),
            patch(
                "tools.worktree_guard.canonical_and_paths",
                return_value=(canonical, (canonical,)),
            ),
            patch(
                "tools.worktree_guard._git",
                return_value=Mock(stdout=" M core/storage_pure.py\n"),
            ) as git,
            patch("tools.worktree_guard._treehouse") as treehouse,
        ):
            with self.assertRaises(RuntimeError) as context:
                release_worktree(canonical, pooled, "lease-1")
        self.assertIn("uncommitted work", str(context.exception))
        treehouse.assert_not_called()
        # Only the revision and status probes ran; there was no detach.
        self.assertEqual(git.call_count, 2)
        self.assertEqual(git.call_args.args[1], "status")

    def test_release_rejects_path_outside_pool(self):
        canonical = Path("/tmp/Anki2/addons21/ankiscape_fork")
        outside = safe_worktree_root(canonical) / "feature-2026-08-31"
        with (
            patch(
                "tools.worktree_guard.canonical_and_paths",
                return_value=(canonical, (canonical,)),
            ),
            patch("tools.worktree_guard._git") as git,
            patch("tools.worktree_guard._treehouse") as treehouse,
        ):
            with self.assertRaises(RuntimeError) as context:
                release_worktree(canonical, outside, "lease-1")
        self.assertIn("not a pooled worktree", str(context.exception))
        git.assert_not_called()
        treehouse.assert_not_called()

    def test_release_detaches_before_returning_with_the_lease_id(self):
        canonical = Path("/tmp/Anki2/addons21/ankiscape_fork")
        pooled = pool_root(canonical) / ".treehouse/ankiscape_fork-1/1/ankiscape_fork"
        events = []

        def fake_git(_path, *args, **_kwargs):
            events.append(("git", args[0]))
            return Mock(stdout="")

        def fake_treehouse(_canonical, *args):
            events.append(("treehouse", args))
            if args == ("status", "--json"):
                return Mock(stdout=json.dumps([{
                    "path": str(pooled), "status": "leased", "lease_id": "lease-1",
                }]))
            return Mock(stdout="")

        with (
            patch("tools.worktree_guard.locking.claim_landing_lock"),
            patch("tools.worktree_guard.require_no_gate_markers"),
            patch("tools.worktree_guard.audit"),
            patch(
                "tools.worktree_guard.canonical_and_paths",
                return_value=(canonical, (canonical,)),
            ),
            patch("tools.worktree_guard._git", side_effect=fake_git),
            patch("tools.worktree_guard._treehouse", side_effect=fake_treehouse),
        ):
            release_worktree(canonical, pooled, "lease-1")

        self.assertEqual(
            events,
            [
                ("git", "rev-parse"),
                ("git", "status"),
                ("treehouse", ("status", "--json")),
                ("git", "checkout"),
                (
                    "treehouse",
                    ("return", "--force", "--if-lease-id", "lease-1", str(pooled)),
                ),
            ],
        )

    def test_lease_returns_a_lease_pointing_outside_the_pool(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            canonical = (Path(temp_dir) / "Anki2/addons21/ankiscape_fork").resolve()
            qt_interpreter = canonical / ".venv-qt/bin/python"
            qt_interpreter.parent.mkdir(parents=True)
            qt_interpreter.write_text("", encoding="utf-8")
            escaped = canonical.parent / "escaped_worktree"
            lease = {"path": str(escaped), "lease_id": "lease-1"}
            with (
                patch("tools.worktree_guard.audit"),
                patch(
                    "tools.worktree_guard.canonical_and_paths",
                    return_value=(canonical, (canonical,)),
                ),
                patch("tools.worktree_guard._git", return_value=Mock(stdout="")) as git,
                patch(
                    "tools.worktree_guard._treehouse",
                    return_value=Mock(stdout=json.dumps(lease)),
                ) as treehouse,
            ):
                with self.assertRaises(RuntimeError) as context:
                    lease_worktree(canonical, "goal/feature", None, "main")

            self.assertIn("outside the pool", str(context.exception))
            git.assert_called_once_with(canonical, "worktree", "list", "--porcelain", capture=True)
            self.assertEqual(
                treehouse.call_args_list[-1].args[1:],
                ("return", "--force", "--if-lease-id", "lease-1", str(escaped)),
            )

    def test_lease_returns_lease_when_branch_checkout_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            canonical = (Path(temp_dir) / "Anki2/addons21/ankiscape_fork").resolve()
            qt_interpreter = canonical / ".venv-qt/bin/python"
            qt_interpreter.parent.mkdir(parents=True)
            qt_interpreter.write_text("", encoding="utf-8")
            pooled = pool_root(canonical) / ".treehouse/ankiscape_fork-1/1/ankiscape_fork"
            lease = {"path": str(pooled), "lease_id": "lease-1"}

            def fake_git(_path, *args, **_kwargs):
                if args[0] == "worktree":
                    return Mock(stdout="")
                if args[0] == "show-ref":
                    return Mock(returncode=1)
                raise subprocess.CalledProcessError(1, ("git", *args))

            with (
                patch("tools.worktree_guard.audit"),
                patch(
                    "tools.worktree_guard.canonical_and_paths",
                    return_value=(canonical, (canonical,)),
                ),
                patch("tools.worktree_guard._git", side_effect=fake_git),
                patch(
                    "tools.worktree_guard._treehouse",
                    return_value=Mock(stdout=json.dumps(lease)),
                ) as treehouse,
            ):
                with self.assertRaises(subprocess.CalledProcessError):
                    lease_worktree(canonical, "goal/feature", None, "main")

            self.assertEqual(
                treehouse.call_args_list[-1].args[1:],
                ("return", "--force", "--if-lease-id", "lease-1", str(pooled)),
            )

    def test_worktree_name_cannot_escape_safe_root(self):
        for name in ("", ".", "..", "../unsafe", "/tmp/unsafe", "nested/unsafe"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_worktree_name(name)
        self.assertEqual(validate_worktree_name("feature-name"), "feature-name")


class PreservedRefTest(unittest.TestCase):
    """Real git repo so the merge-base ancestry check is exercised for real."""

    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.canonical = Path(self._temporary.name) / "ankiscape_fork"
        self.canonical.mkdir()
        self.git = lambda *args, **kwargs: subprocess.run(
            ("git", "-C", str(self.canonical), *args),
            check=kwargs.get("check", True),
            capture_output=True,
            text=True,
        )
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Worktree Guard Tests")

    def _commit(self, message: str) -> str:
        self.git("commit", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def test_delete_refuses_work_that_has_not_landed(self):
        self._commit("landed work on main")
        self.git("checkout", "-q", "--detach", "main")
        unlanded = self._commit("rework in progress, waiting on a ruling")
        ref = "refs/preserved/preserved-test/rework-2026-09-02"
        self.git("update-ref", ref, unlanded)
        self.git("checkout", "-q", "main")

        name = "preserved-test/rework-2026-09-02"
        with self.assertRaises(RuntimeError) as context:
            delete_preserved(self.canonical, name)

        self.assertIn(ref, str(context.exception))
        self.assertIn("not an ancestor of main", str(context.exception))
        live_ref = self.git("show-ref", "--verify", ref).stdout.split()
        self.assertEqual(live_ref[0], unlanded)

    def test_delete_removes_ref_once_its_commit_is_on_main(self):
        landed = self._commit("preserved work later merged to main")
        ref = "refs/preserved/preserved-test/landed-2026-09-02"
        self.git("update-ref", ref, landed)

        delete_preserved(self.canonical, "preserved-test/landed-2026-09-02")

        probe = self.git("show-ref", "--verify", "--quiet", ref, check=False)
        self.assertNotEqual(probe.returncode, 0)

    def test_list_reports_each_refs_landing_state(self):
        landed = self._commit("landed work on main")
        self.git("checkout", "-q", "--detach", "main")
        unlanded = self._commit("rework in progress, waiting on a ruling")
        self.git("update-ref", "refs/preserved/preserved-test/landed", landed)
        self.git(
            "update-ref", "refs/preserved/preserved-test/rework", unlanded
        )
        self.git("checkout", "-q", "main")

        with redirect_stdout(io.StringIO()) as output:
            list_preserved(self.canonical)

        rows = [
            (ref, state)
            for ref, _, state in (
                line.split(maxsplit=2)
                for line in output.getvalue().splitlines()
            )
        ]
        self.assertEqual(
            rows,
            [
                ("refs/preserved/preserved-test/landed", "landed"),
                ("refs/preserved/preserved-test/rework", "NOT LANDED"),
            ],
        )
        # The listing also carries each ref's short object id.
        self.assertIn(landed[:7], output.getvalue())
        self.assertIn(unlanded[:7], output.getvalue())


class NativeSessionGuardTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "__init__.py").write_text("ADDON = True\n", encoding="utf-8")
        self.collection = self.root / "owner/collection.anki2"
        self.collection.parent.mkdir()
        self.collection.write_bytes(b"original collection")
        self.enterContext(patch.object(native, "owner_collection", return_value=self.collection))
        self.process = self.enterContext(patch.object(
            native.subprocess, "run", return_value=Mock(returncode=1, stdout="", stderr=""),
        ))
        self.enterContext(patch.object(native.tempfile, "tempdir", str(self.root)))

    def prepare_session(self):
        with redirect_stdout(io.StringIO()) as output:
            base = native.prepare(self.repo)
        return base, json.loads(output.getvalue())

    def test_prepare_copies_addon_and_records_collection_without_modifying_it(self):
        before = native.measure(self.collection)
        base, output = self.prepare_session()
        copied = base / "addons21/ankiscape_fork/__init__.py"
        self.assertEqual(copied.read_bytes(), b"ADDON = True\n")
        self.assertFalse(copied.is_symlink())
        receipt = json.loads((base / native.RECEIPT).read_text())
        self.assertEqual(receipt["baseline"], before)
        self.assertEqual(native.measure(self.collection), before)
        self.assertEqual(output["path"], str(base))
        self.assertIn(" -b ", output["anki_command"])
        self.assertIn(" launch ", output["launch_command"])
        self.assertEqual(shlex.split(output["launch_command"]), [
            sys.executable, str(Path(native.__file__).resolve()), "launch", str(base),
        ])
        with patch.object(native, "prepare") as prepare:
            self.assertEqual(native.main(["prepare"]), 0)
        prepare.assert_called_once_with(Path(__file__).resolve().parents[1])

    def test_prepare_refuses_running_anki_before_creating_a_session(self):
        self.process.return_value = Mock(returncode=0, stdout="123\n", stderr="")
        before = native.measure(self.collection)
        with self.assertRaisesRegex(RuntimeError, "Anki is already running"):
            native.prepare(self.repo)
        self.assertEqual(list(self.root.glob("ankiscape-native-*")), [])
        self.assertEqual(native.measure(self.collection), before)
        self.process.assert_called_once_with(
            ("/usr/bin/pgrep", "-ix", "anki"), text=True, capture_output=True,
        )

    def test_verify_detects_modified_collection_and_preserves_evidence(self):
        base, _ = self.prepare_session()
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(native.main(["verify", str(base)]), 0)
        self.assertTrue(json.loads(output.getvalue())["unchanged"])
        self.collection.write_bytes(b"modified collection with more data")
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(native.main(["verify", str(base)]), 1)
        report = json.loads(output.getvalue())
        self.assertFalse(report["unchanged"])
        self.assertIn("sha256", report["changes"])
        self.assertIn("size", report["changes"])
        self.assertTrue((base / native.RECEIPT).is_file())
        self.assertTrue((base / "addons21/ankiscape_fork/__init__.py").is_file())

    def test_verify_handles_absence_and_detects_creation_and_removal(self):
        self.collection.unlink()
        base, _ = self.prepare_session()
        with redirect_stdout(io.StringIO()):
            self.assertEqual(native.verify(base), 0)
            self.collection.write_bytes(b"new collection")
            self.assertEqual(native.verify(base), 1)
        present, _ = self.prepare_session()
        self.collection.unlink()
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(native.verify(present), 1)
        self.assertEqual(json.loads(output.getvalue())["changes"]["exists"],
                         {"before": True, "after": False})

    def test_launch_refuses_unprepared_or_relocated_receipt(self):
        with self.assertRaisesRegex(RuntimeError, "missing native-session-receipt.json"):
            native.launch(self.root)
        self.process.assert_not_called()
        base, _ = self.prepare_session()
        moved = base.rename(base.with_name("ankiscape-native-moved"))
        self.process.reset_mock()
        with self.assertRaisesRegex(ValueError, "receipt does not match"):
            native.launch(moved)
        self.process.assert_not_called()

    def test_launch_rechecks_running_anki_and_always_passes_base(self):
        base, _ = self.prepare_session()
        self.process.reset_mock()
        self.process.return_value = Mock(returncode=0, stdout="123\n", stderr="")
        with self.assertRaisesRegex(RuntimeError, "Anki is already running"):
            native.launch(base)
        self.assertEqual(self.process.call_count, 1)
        self.process.side_effect = [Mock(returncode=1), Mock(returncode=7)]
        self.assertEqual(native.launch(base), 7)
        self.process.assert_called_with((str(native.ANKI), "-b", str(base)), check=False)

    def test_process_probe_failure_is_not_treated_as_anki_stopped(self):
        self.process.return_value = Mock(returncode=2, stderr="probe denied")
        with self.assertRaisesRegex(RuntimeError, "cannot check.*probe denied"):
            native.prepare(self.repo)
        self.assertEqual(list(self.root.glob("ankiscape-native-*")), [])


if __name__ == "__main__":
    unittest.main()
