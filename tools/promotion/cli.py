"""Run promotion checks and land only the exact commit that passed them."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from .contract import GateError
from .landing import land
from .lane_execution import run_gate
from .repository import _git


def install_hook(repo: Path) -> Path:
    repo = repo.resolve()
    raw_git_dir = Path(_git(repo, "rev-parse", "--git-dir").stdout.strip())
    git_dir = (raw_git_dir if raw_git_dir.is_absolute() else repo / raw_git_dir).resolve()
    hook_path = git_dir / "hooks" / "pre-commit"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    source = """#!/bin/sh
exec python3 -m tools.promotion.landing_freeze_hook \"$@\"
"""
    hook_path.write_text(source, encoding="utf-8")
    hook_path.chmod(0o755)
    return hook_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="run the promotion gate")
    run_parser.add_argument("worktree", type=Path)
    run_parser.add_argument(
        "--plain-only",
        action="store_true",
        help="skip the offscreen Qt lane for a branch-side promotion check",
    )
    run_parser.add_argument(
        "--remote-lanes",
        action="store_true",
        help="run the plain and Qt lanes through the MacBook remote test host",
    )
    subparsers.add_parser("install-hook", help="install the repo-local landing freeze hook")
    land_parser = subparsers.add_parser("land", help="fast-forward main to a gated worktree")
    land_parser.add_argument("worktree", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.command == "run":
            run_gate(
                args.worktree,
                plain_only=args.plain_only,
                remote_lanes=args.remote_lanes,
            )
        elif args.command == "land":
            land(args.worktree)
        else:
            print(install_hook(Path.cwd()))
    except (GateError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


_PUBLIC_MODULE = f"{__package__.rsplit('.', 1)[0]}.promotion_gate"
install_hook.__module__ = _PUBLIC_MODULE
main.__module__ = _PUBLIC_MODULE
