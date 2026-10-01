#!/usr/bin/env python3
"""Run the installed slop gate on the working tree without touching the real index.

The gate judges staged changes against HEAD, so every working-tree change,
untracked files included, is staged into a disposable copy of the index first.
Run it before approving a review, and after sketching a new module to see the
directory, fan-out, and line-growth refusals before implementing it. The gate's
diagnostics and exit status are returned unchanged.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def git_path(name: str) -> Path:
    return Path(subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-path", name],
        check=True, capture_output=True, text=True,
    ).stdout.strip())


def main() -> int:
    gate = git_path("hooks/slop_gate.py")
    with tempfile.TemporaryDirectory(prefix="slop-gate-preflight-") as temporary:
        index = Path(temporary) / "index"
        shutil.copy2(git_path("index"), index)
        # Match fleet's pre-commit hook, including uv tool executable discovery.
        environment = {
            **os.environ,
            "GIT_INDEX_FILE": str(index),
            "PATH": f"{Path.home() / '.local/bin'}{os.pathsep}{os.environ['PATH']}",
        }
        subprocess.run(["git", "add", "-A"], env=environment, check=True)
        return subprocess.run([sys.executable, str(gate)], env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
