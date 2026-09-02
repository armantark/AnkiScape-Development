"""Git and worktree paths used by promotion operations."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .contract import EVIDENCE_DIR_NAME, GateError


def _git(
    repo: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ("git", "-C", str(repo), *args),
        check=False,
        text=True,
        capture_output=True,
    )
    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise GateError(detail or f"git {' '.join(args)} failed with exit {completed.returncode}")
    return completed


def commit_at(worktree: Path) -> str:
    return _git(worktree, "rev-parse", "HEAD").stdout.strip()


def git_common_dir(repo: Path) -> Path:
    raw = _git(repo, "rev-parse", "--git-common-dir").stdout.strip()
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (repo / path).resolve()


def evidence_path_for(repo: Path, commit: str) -> Path:
    return git_common_dir(repo) / EVIDENCE_DIR_NAME / f"{commit}.json"


def _worktree_rows(repo: Path) -> tuple[dict[str, str], ...]:
    result = _git(repo, "worktree", "list", "--porcelain")
    rows: list[dict[str, str]] = []
    row: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if not line:
            if row:
                rows.append(row)
                row = {}
            continue
        key, _, value = line.partition(" ")
        row[key] = value
    if row:
        rows.append(row)
    return tuple(rows)


def main_worktree(repo: Path) -> Path:
    for row in _worktree_rows(repo):
        if row.get("branch") == "refs/heads/main":
            return Path(row["worktree"]).resolve()
    raise GateError("Landing refused: refs/heads/main is not checked out in a worktree")


def safe_log_root(repo: Path) -> Path:
    rows = _worktree_rows(repo)
    if not rows:
        raise GateError("git reported no worktrees")
    canonical = Path(rows[0]["worktree"]).resolve()
    return canonical.parent.parent / "ankiscape_worktrees"


_PUBLIC_MODULE = f"{__package__.rsplit('.', 1)[0]}.promotion_gate"
_git.__module__ = _PUBLIC_MODULE
commit_at.__module__ = _PUBLIC_MODULE
git_common_dir.__module__ = _PUBLIC_MODULE
evidence_path_for.__module__ = _PUBLIC_MODULE
_worktree_rows.__module__ = _PUBLIC_MODULE
main_worktree.__module__ = _PUBLIC_MODULE
safe_log_root.__module__ = _PUBLIC_MODULE
