#!/usr/bin/env python3
"""Run the installed diff-aware slop gate on a disposable candidate index.

The candidate is the current working tree staged in temporary Git metadata. By
default it is compared with HEAD. ``--base`` compares a clean committed review
candidate with an earlier commit without changing the checkout's HEAD, refs,
index, working files, or object database. The gate's diagnostics and exit status
are returned unchanged.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence


def _git(
    root: Path,
    *args: str,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed")
    return result


def _absolute_git_path(root: Path, *args: str) -> Path:
    value = _git(root, "rev-parse", "--path-format=absolute", *args).stdout.strip()
    return Path(value).resolve()


def _candidate_environment(root: Path, temporary: Path, base: str | None) -> dict[str, str]:
    git_dir = temporary / "preflight.git"
    subprocess.run(["git", "init", "--bare", "-q", str(git_dir)], check=True)
    common = _absolute_git_path(root, "--git-common-dir")
    alternates = git_dir / "objects" / "info" / "alternates"
    alternates.parent.mkdir(parents=True, exist_ok=True)
    alternates.write_text(str((common / "objects").resolve()) + "\n", encoding="utf-8")

    base_ref = base or "HEAD"
    base_oid = _git(root, "rev-parse", "--verify", f"{base_ref}^{{commit}}").stdout.strip()
    index = temporary / "index"
    environment = {
        **os.environ,
        "GIT_DIR": str(git_dir),
        "GIT_WORK_TREE": str(root),
        "GIT_INDEX_FILE": str(index),
    }
    _git(root, "update-ref", "refs/heads/preflight", base_oid, environment=environment)
    _git(root, "symbolic-ref", "HEAD", "refs/heads/preflight", environment=environment)

    if base is None:
        real_index = _absolute_git_path(root, "--git-path", "index")
        if real_index.is_file():
            shutil.copy2(real_index, index)
        else:
            _git(root, "read-tree", base_oid, environment=environment)
    else:
        _git(root, "read-tree", base_oid, environment=environment)
    _git(root, "add", "-A", "--", ".", environment=environment)
    return environment


def installed_gate(root: Path) -> Path:
    return _absolute_git_path(root, "--git-path", "hooks/slop_gate.py")


def run_preflight(root: Path, gate: Path, base: str | None = None) -> int:
    with tempfile.TemporaryDirectory(prefix="ankiscape-slop-preflight-") as directory:
        environment = _candidate_environment(root, Path(directory), base)
        environment["PATH"] = str(Path.home() / ".local/bin") + os.pathsep + environment["PATH"]
        return subprocess.run(
            [sys.executable, str(gate)],
            cwd=root,
            env=environment,
            check=False,
        ).returncode


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="candidate repository or worktree")
    parser.add_argument("--base", help="commit used as the slop-gate HEAD baseline (default: HEAD)")
    parser.add_argument("--slop-gate", type=Path, help="gate script (default: installed Git hooks path)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if not (root / ".git").exists():
            raise ValueError(f"root is not a Git checkout: {root}")
        gate = args.slop_gate.resolve() if args.slop_gate else installed_gate(root)
        if not gate.is_file():
            raise ValueError(f"slop gate is not a file: {gate}")
        return run_preflight(root, gate, args.base)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
