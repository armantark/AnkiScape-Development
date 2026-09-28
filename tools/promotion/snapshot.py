"""Private commit trees for promotion checks, independent of checkout writes."""

from __future__ import annotations

import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .repository import _git, main_worktree


@contextmanager
def commit_snapshot(worktree: Path, commit: str) -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix="ankiscape-promotion-") as temporary:
        root = Path(temporary).resolve()
        snapshot = root / "tree"
        _git(worktree, "clone", "--shared", "--no-checkout", "--quiet", str(worktree), str(snapshot))
        _git(snapshot, "checkout", "--quiet", "--detach", commit)
        (snapshot / ".venv-qt").symlink_to(main_worktree(worktree) / ".venv-qt", target_is_directory=True)
        yield snapshot
