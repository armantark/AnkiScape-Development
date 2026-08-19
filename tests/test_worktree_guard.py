import json
import tempfile
import unittest
from pathlib import Path

from tools.worktree_guard import (
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

    def test_worktree_name_cannot_escape_safe_root(self):
        for name in ("", ".", "..", "../unsafe", "/tmp/unsafe", "nested/unsafe"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_worktree_name(name)
        self.assertEqual(validate_worktree_name("feature-name"), "feature-name")


if __name__ == "__main__":
    unittest.main()
