#!/usr/bin/env python3
"""Keep linked AnkiScape worktrees outside Anki's live add-on directory.

Concurrent exclude setup is atomic on POSIX and best-effort elsewhere.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence

try:
    import fcntl
except ImportError:  # Non-POSIX fallback is advisory and may append duplicates.
    fcntl = None


OWNER_FILE = ".ankiscape-worktree-owner"


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


def caller_owner(explicit: Optional[str] = None) -> str:
    owner = explicit or os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not owner:
        raise ValueError("owner is required outside a Claude Code session; pass --owner")
    return owner


def owner_path(worktree: Path) -> Path:
    return worktree / OWNER_FILE


def read_owner(worktree: Path) -> Optional[str]:
    path = owner_path(worktree)
    if not path.is_file():
        return None
    owner = path.read_text(encoding="utf-8").strip()
    return owner or None


def claim_owner(
    worktree: Path,
    owner: str,
    *,
    take_over: bool = False,
) -> Optional[str]:
    path = owner_path(worktree)
    try:
        with path.open("x", encoding="utf-8") as owner_file:
            owner_file.write(f"{owner}\n")
        return None
    except FileExistsError:
        previous = read_owner(worktree)
        if previous == owner:
            return previous
        if not take_over:
            raise RuntimeError(
                f"worktree is owned by {previous!r}; pass --take-over to replace it"
            )
        path.write_text(f"{owner}\n", encoding="utf-8")
        return previous


def claimable_worktree(paths: Sequence[Path], canonical: Path, repo: Path) -> Path:
    current = repo.resolve()
    if current == canonical.resolve():
        raise ValueError("the canonical checkout cannot be claimed")
    if current not in {path.resolve() for path in paths}:
        raise ValueError("claim target is not a registered linked worktree")
    return current


def ownership_mismatch(
    paths: Sequence[Path],
    canonical: Path,
    repo: Path,
    owner: str,
) -> Optional[tuple[Path, Optional[str]]]:
    current = repo.resolve()
    if current == canonical.resolve() or current not in {path.resolve() for path in paths}:
        return None
    recorded = read_owner(current)
    if recorded == owner:
        return None
    return current, recorded


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


def ensure_owner_ignored(repo: Path) -> None:
    result = _git(repo, "rev-parse", "--git-common-dir", capture=True)
    common_dir = Path(result.stdout.strip())
    if not common_dir.is_absolute():
        common_dir = repo.resolve() / common_dir
    exclude = common_dir.resolve() / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    with exclude.open("a+", encoding="utf-8") as exclude_file:
        if fcntl is None:
            print(
                "warning: owner ignore setup is not concurrency-safe without POSIX fcntl",
                file=sys.stderr,
            )
        else:
            fcntl.flock(exclude_file, fcntl.LOCK_EX)
        exclude_file.seek(0)
        existing = exclude_file.read()
        if OWNER_FILE in {line.strip() for line in existing.splitlines()}:
            return
        # Append preserves other writers' entries; duplicate inert patterns are tolerated.
        if existing and not existing.endswith("\n"):
            exclude_file.write("\n")
        exclude_file.write(f"{OWNER_FILE}\n")


def audit(repo: Path, owner: Optional[str] = None) -> None:
    canonical, paths = canonical_and_paths(repo)
    unsafe = unsafe_registered_worktrees(paths, canonical)
    duplicates = duplicate_enabled_addons(canonical.parent, canonical)
    problems = tuple(dict.fromkeys((*unsafe, *duplicates)))
    if problems:
        joined = "\n".join(f"- {path}" for path in problems)
        raise RuntimeError(f"Anki would load linked/duplicate AnkiScape checkouts:\n{joined}")
    if owner is not None:
        mismatch = ownership_mismatch(paths, canonical, repo, owner)
        if mismatch:
            path, recorded = mismatch
            if recorded is None:
                raise RuntimeError(
                    "Linked worktree is unclaimed:\n"
                    f"- {path}\n"
                    "Run `python3 tools/worktree_guard.py claim` from that worktree first."
                )
            raise RuntimeError(
                "Linked worktrees are owned by another session:\n"
                f"- {path}: owned by {recorded!r}, caller is {owner!r}"
            )
    print(f"Worktree layout safe: {canonical}")
    print(f"Linked worktree root: {safe_worktree_root(canonical)}")


def add_worktree(
    repo: Path,
    branch: str,
    name: Optional[str],
    start_point: str,
    owner: str,
) -> None:
    audit(repo, owner)
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
    claim_owner(destination, owner)
    audit(destination, owner)
    print(f"Created worktree: {destination}")
    print(f"Owner: {owner}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--owner", help="session identity; defaults to CLAUDE_CODE_SESSION_ID")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("audit")
    claim_parser = subparsers.add_parser("claim")
    claim_parser.add_argument("--take-over", action="store_true")
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("branch")
    add_parser.add_argument("--name")
    add_parser.add_argument("--start-point", default="main")
    args = parser.parse_args(argv)
    try:
        if args.command == "audit":
            audit(args.repo, args.owner or os.environ.get("CLAUDE_CODE_SESSION_ID"))
        else:
            owner = caller_owner(args.owner)
            ensure_owner_ignored(args.repo)
            if args.command == "claim":
                canonical, paths = canonical_and_paths(args.repo)
                worktree = claimable_worktree(paths, canonical, args.repo)
                previous = claim_owner(worktree, owner, take_over=args.take_over)
                if previous is not None and previous != owner:
                    print(f"Took over worktree from: {previous}")
                print(f"Worktree owner: {owner}")
            else:
                add_worktree(args.repo, args.branch, args.name, args.start_point, owner)
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
