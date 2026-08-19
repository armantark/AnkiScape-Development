#!/usr/bin/env python3
"""Keep linked AnkiScape worktrees outside Anki's live add-on directory."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Optional, Sequence


def worktree_paths(porcelain: str) -> tuple[Path, ...]:
    return tuple(
        Path(line.removeprefix("worktree ")).resolve()
        for line in porcelain.splitlines()
        if line.startswith("worktree ")
    )


def unsafe_registered_worktrees(paths: Sequence[Path], canonical: Path) -> tuple[Path, ...]:
    addons_dir = canonical.resolve().parent
    return tuple(
        path.resolve()
        for path in paths
        if path.resolve() != canonical.resolve() and path.resolve().is_relative_to(addons_dir)
    )


def duplicate_enabled_addons(addons_dir: Path, canonical: Path) -> tuple[Path, ...]:
    canonical_meta = json.loads((canonical / "meta.json").read_text(encoding="utf-8"))
    canonical_name = canonical_meta.get("name")
    duplicates = []
    for child in addons_dir.iterdir():
        if child.resolve() == canonical.resolve() or not (child / "__init__.py").is_file():
            continue
        meta_path = child / "meta.json"
        if not meta_path.is_file():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if meta.get("name") == canonical_name and not meta.get("disabled", False):
            duplicates.append(child.resolve())
    return tuple(duplicates)


def safe_worktree_root(canonical: Path) -> Path:
    return canonical.resolve().parent.parent / "ankiscape_worktrees"


def validate_worktree_name(name: str) -> str:
    if not name or name in {".", ".."} or Path(name).name != name:
        raise ValueError("worktree name must be one path component")
    return name


def _git(
    canonical: Path,
    *args: str,
    capture: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", "-C", str(canonical), *args),
        check=check,
        text=True,
        capture_output=capture,
    )


def canonical_and_paths(repo: Path) -> tuple[Path, tuple[Path, ...]]:
    result = _git(repo, "worktree", "list", "--porcelain", capture=True)
    paths = worktree_paths(result.stdout)
    if not paths:
        raise RuntimeError("git reported no worktrees")
    return paths[0], paths


def audit(repo: Path) -> None:
    canonical, paths = canonical_and_paths(repo)
    unsafe = unsafe_registered_worktrees(paths, canonical)
    duplicates = duplicate_enabled_addons(canonical.parent, canonical)
    problems = tuple(dict.fromkeys((*unsafe, *duplicates)))
    if problems:
        joined = "\n".join(f"- {path}" for path in problems)
        raise RuntimeError(f"Anki would load linked/duplicate AnkiScape checkouts:\n{joined}")
    print(f"Worktree layout safe: {canonical}")
    print(f"Linked worktree root: {safe_worktree_root(canonical)}")


def add_worktree(repo: Path, branch: str, name: Optional[str], start_point: str) -> None:
    audit(repo)
    canonical, _ = canonical_and_paths(repo)
    leaf = validate_worktree_name(name or branch.replace("/", "-"))
    destination = safe_worktree_root(canonical) / leaf
    destination.parent.mkdir(parents=True, exist_ok=True)
    exists = (
        _git(
            canonical,
            "show-ref",
            "--verify",
            "--quiet",
            f"refs/heads/{branch}",
            check=False,
        ).returncode
        == 0
    )
    if exists:
        _git(canonical, "worktree", "add", str(destination), branch)
    else:
        _git(canonical, "worktree", "add", "-b", branch, str(destination), start_point)
    audit(repo)
    print(f"Created worktree: {destination}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("audit")
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("branch")
    add_parser.add_argument("--name")
    add_parser.add_argument("--start-point", default="main")
    args = parser.parse_args(argv)
    try:
        if args.command == "audit":
            audit(args.repo)
        else:
            add_worktree(args.repo, args.branch, args.name, args.start_point)
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
