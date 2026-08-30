import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tools.worktree_guard import (
    add_worktree,
    duplicate_enabled_addons,
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

    def test_worktree_name_cannot_escape_safe_root(self):
        for name in ("", ".", "..", "../unsafe", "/tmp/unsafe", "nested/unsafe"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_worktree_name(name)
        self.assertEqual(validate_worktree_name("feature-name"), "feature-name")


if __name__ == "__main__":
    unittest.main()
