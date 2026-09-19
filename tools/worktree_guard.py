#!/usr/bin/env python3
"""Keep linked AnkiScape worktrees outside Anki's live add-on directory."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Optional, Sequence

if __package__:
    from .promotion import locking
else:
    from promotion import locking


def worktree_paths(porcelain: str) -> tuple[Path, ...]:
    return tuple(
        Path(line.removeprefix("worktree ")).resolve()
        for line in porcelain.splitlines()
        if line.startswith("worktree ")
    )


def unsafe_registered_worktrees(paths: Sequence[Path], canonical: Path) -> tuple[Path, ...]:
    canonical = canonical.resolve()
    addons_dir = canonical.parent
    resolved_paths = (path.resolve() for path in paths)
    return tuple(
        resolved
        for resolved in resolved_paths
        if resolved.is_relative_to(addons_dir)
        and not resolved.is_relative_to(canonical)
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


def pool_root(canonical: Path) -> Path:
    return safe_worktree_root(canonical) / "pool"


def repo_local_hook_path(repo: Path) -> Path:
    raw_git_dir = Path(_git(repo, "rev-parse", "--git-dir", capture=True).stdout.strip())
    git_dir = raw_git_dir if raw_git_dir.is_absolute() else repo / raw_git_dir
    return git_dir.resolve() / "hooks" / "pre-commit"


def landing_freeze_hook_installed(repo: Path) -> bool:
    path = repo_local_hook_path(repo)
    try:
        return path.is_file() and path.stat().st_mode & 0o111 and "tools.promotion.landing_freeze_hook" in path.read_text(encoding="utf-8")
    except OSError:
        return False


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


def _treehouse(canonical: Path, *args: str) -> subprocess.CompletedProcess[str]:
    # The pool root is always pinned explicitly so neither TREEHOUSE_ROOT nor a
    # config file can steer pooled worktrees outside the audited safe root.
    result = subprocess.run(
        ("treehouse", *args, "--root", str(pool_root(canonical))),
        text=True,
        capture_output=True,
        cwd=str(canonical),
    )
    if result.returncode != 0:
        raise RuntimeError(f"treehouse {args[0]} failed:\n{result.stderr.strip()}")
    return result


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
    if repo.resolve() == canonical and not landing_freeze_hook_installed(repo):
        print(f"WARNING: repo-local landing freeze hook missing: {repo_local_hook_path(repo)}")


def add_worktree(repo: Path, branch: str, name: Optional[str], start_point: str) -> None:
    audit(repo)
    canonical, _ = canonical_and_paths(repo)
    qt_environment = canonical / ".venv-qt"
    qt_interpreter = qt_environment / "bin/python"
    if not qt_interpreter.exists():
        raise RuntimeError(f"Qt test interpreter not found: {qt_interpreter}")
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
    (destination / ".venv-qt").symlink_to(qt_environment, target_is_directory=True)
    audit(repo)
    print(f"Created worktree: {destination}")


def require_branch_available(repo: Path, branch: str) -> None:
    result = _git(repo, "worktree", "list", "--porcelain", capture=True)
    branch_ref = "refs/heads/" + branch.removeprefix("refs/heads/")
    worktree = ""
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            worktree = line.removeprefix("worktree ")
        elif line == f"branch {branch_ref}":
            raise RuntimeError(f"branch {branch_ref} is already checked out in {worktree}")


def pool_status(repo: Path, *, as_json: bool = False) -> None:
    canonical, _ = canonical_and_paths(repo)
    options = ("--json",) if as_json else ()
    result = _treehouse(canonical, "status", *options)
    print(result.stdout, end="")


def lease_worktree(repo: Path, branch: str, holder: Optional[str], start_point: str) -> None:
    audit(repo)
    canonical, _ = canonical_and_paths(repo)
    qt_environment = canonical / ".venv-qt"
    if not (qt_environment / "bin/python").exists():
        raise RuntimeError(f"Qt test interpreter not found: {qt_environment / 'bin/python'}")
    require_branch_available(canonical, branch)
    result = _treehouse(
        canonical,
        "get",
        "--lease",
        "--no-fetch",
        "--json",
        "--lease-holder",
        holder or "worktree_guard",
    )
    try:
        lease = json.loads(result.stdout)
        destination = Path(lease["path"]).resolve()
        lease_id = lease["lease_id"]
    except (ValueError, KeyError):
        raise RuntimeError(
            "treehouse returned an unparseable lease; reconcile with 'treehouse status':\n"
            f"{result.stdout.strip()}"
        ) from None
    try:
        # Never trust the returned path: verify the answer, not just the request.
        if not destination.is_relative_to(pool_root(canonical)):
            raise RuntimeError(f"treehouse leased a worktree outside the pool: {destination}")
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
            _git(destination, "checkout", branch, capture=True)
        else:
            _git(destination, "checkout", "-b", branch, start_point, capture=True)
        link = destination / ".venv-qt"
        if not link.is_symlink():
            link.symlink_to(qt_environment, target_is_directory=True)
        audit(repo)
    except BaseException:
        _treehouse(canonical, "return", "--force", "--if-lease-id", lease_id, str(destination))
        raise
    print(json.dumps({"path": str(destination), "lease_id": lease_id, "branch": branch}))


def require_no_gate_markers(repo: Path, destination: Path) -> None:
    directory = locking.active_gate_dir_for(repo)
    try:
        paths = sorted(directory.iterdir())
    except OSError as exc:
        if isinstance(exc, FileNotFoundError) and not directory.is_symlink():
            return
        raise RuntimeError(f"promotion gate marker directory is unreadable: {directory}: {exc}") from exc
    for path in paths:
        if path.suffix != ".json":
            continue
        try:
            record = locking._read_record_path(path)
            target = Path(record.worktree)
            if not target.is_absolute():
                raise ValueError("worktree path is not absolute")
        except (OSError, ValueError, locking.GateError) as exc:
            raise RuntimeError(f"refusing return: unreadable promotion gate marker {path}: {exc}") from exc
        if target.resolve() == destination:
            raise RuntimeError(
                f"refusing return: promotion gate marker {path} names {destination} "
                f"(PID {record.pid}); preserve it for reconciliation"
            )


def require_clean_worktree(destination: Path) -> None:
    dirty = _git(destination, "status", "--porcelain", capture=True).stdout.strip()
    if dirty:
        raise RuntimeError(
            f"refusing to return a worktree with uncommitted work; commit it first:\n{dirty}"
        )


def require_matching_lease(canonical: Path, destination: Path, lease_id: str) -> None:
    result = _treehouse(canonical, "status", "--json")
    try:
        rows = json.loads(result.stdout)
    except ValueError as exc:
        raise RuntimeError("refusing return: pool status is unreadable") from exc
    if not isinstance(rows, list):
        raise RuntimeError("refusing return: pool status is not a list")
    matches = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("refusing return: pool status has an unreadable worktree row")
        path = Path(row["path"])
        if not path.is_absolute():
            raise RuntimeError("refusing return: pool status worktree path is not absolute")
        if path.resolve() == destination:
            matches.append(row)
    if not lease_id or len(matches) != 1 or matches[0].get("status") != "leased" or matches[0].get("lease_id") != lease_id:
        raise RuntimeError(f"refusing return: pool status does not confirm lease {lease_id} for {destination}")


def release_worktree(repo: Path, path: Path, lease_id: str) -> None:
    canonical, _ = canonical_and_paths(repo)
    destination = path.resolve()
    if not destination.is_relative_to(pool_root(canonical)):
        raise RuntimeError(f"not a pooled worktree: {destination}")
    coordination = locking.claim_landing_lock(
        canonical,
        operation="returning a pooled worktree",
        worktree=destination,
        commit=_git(destination, "rev-parse", "HEAD", capture=True).stdout.strip(),
        recover_stale=False,
    )
    try:
        require_no_gate_markers(canonical, destination)
        require_clean_worktree(destination)
        require_matching_lease(canonical, destination, lease_id)
        # Keep gate registration excluded until the lease has been returned.
        _git(destination, "checkout", "--detach", capture=True)
        _treehouse(canonical, "return", "--force", "--if-lease-id", lease_id, str(destination))
    finally:
        coordination.release()
    audit(repo)
    print(f"Returned pooled worktree: {destination}")


PRESERVED_PREFIX = "refs/preserved/"


def preserved_ref(name: str) -> str:
    # Mapping any other ref through the prefix keeps deletion confined to
    # refs/preserved/ even when a caller passes a full refname.
    return PRESERVED_PREFIX + name.removeprefix(PRESERVED_PREFIX)


def preserved_has_landed(canonical: Path, ref: str) -> bool:
    result = _git(
        canonical, "merge-base", "--is-ancestor", ref, "main", check=False
    )
    return result.returncode == 0


def list_preserved(repo: Path) -> None:
    canonical, _ = canonical_and_paths(repo)
    result = _git(
        canonical,
        "for-each-ref",
        PRESERVED_PREFIX,
        "--format=%(refname) %(objectname:short)",
        capture=True,
    )
    for line in result.stdout.splitlines():
        ref, short_id = line.split(maxsplit=1)
        landed = preserved_has_landed(canonical, ref)
        state = "landed" if landed else "NOT LANDED"
        print(f"{ref} {short_id} {state}")


def delete_preserved(repo: Path, name: str) -> None:
    canonical, _ = canonical_and_paths(repo)
    ref = preserved_ref(name)
    probe = _git(
        canonical, "show-ref", "--verify", "--quiet", ref, check=False
    )
    if probe.returncode != 0:
        raise RuntimeError(f"no preserved ref: {ref}")
    if not preserved_has_landed(canonical, ref):
        raise RuntimeError(
            f"refusing to delete {ref}: its commit is not an ancestor of "
            "main; a preserved ref may be deleted only "
            "after its work has landed"
        )
    _git(canonical, "update-ref", "-d", ref)
    print(f"Deleted preserved ref: {ref}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("audit")
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--json", action="store_true")
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("branch")
    add_parser.add_argument("--name")
    add_parser.add_argument("--start-point", default="main")
    lease_parser = subparsers.add_parser("lease")
    lease_parser.add_argument("branch")
    lease_parser.add_argument("--holder")
    lease_parser.add_argument("--start-point", default="main")
    release_parser = subparsers.add_parser("release")
    release_parser.add_argument("path", type=Path)
    release_parser.add_argument("--lease-id", required=True)
    preserved_parser = subparsers.add_parser("preserved")
    preserved_subparsers = preserved_parser.add_subparsers(
        dest="preserved_command", required=True
    )
    preserved_subparsers.add_parser("list")
    preserved_delete = preserved_subparsers.add_parser("delete")
    preserved_delete.add_argument("name")
    args = parser.parse_args(argv)
    try:
        if args.command == "audit":
            audit(args.repo)
        elif args.command == "status":
            pool_status(args.repo, as_json=args.json)
        elif args.command == "add":
            add_worktree(args.repo, args.branch, args.name, args.start_point)
        elif args.command == "lease":
            lease_worktree(args.repo, args.branch, args.holder, args.start_point)
        elif args.command == "release":
            release_worktree(args.repo, args.path, args.lease_id)
        elif args.command == "preserved" and args.preserved_command == "list":
            list_preserved(args.repo)
        else:
            delete_preserved(args.repo, args.name)
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
