"""Freeze an exact commit for a native check without opening Anki."""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path

from tools.promotion.repository import _git, commit_at
from tools.promotion.snapshot import commit_snapshot

from .session_guard import copy_addon, source_digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("worktree", type=Path)
    parser.add_argument("commit")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    worktree = args.worktree.resolve()
    if commit_at(worktree) != args.commit:
        raise RuntimeError("source revision does not match the requested commit")
    if _git(worktree, "status", "--porcelain").stdout:
        raise RuntimeError("source checkout is dirty")
    args.output.mkdir(parents=True)
    addon = args.output / "source"
    with commit_snapshot(worktree, args.commit) as snapshot:
        copy_addon(snapshot, addon)
    files = [
        {"path": path.relative_to(addon).as_posix(),
         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in sorted(addon.rglob("*")) if path.is_file()
    ]
    archive = args.output / "source.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        stream.add(addon, arcname="source")
    manifest = {
        "commit": args.commit,
        "source_sha256": source_digest(addon),
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "files": files,
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    print(args.output / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
