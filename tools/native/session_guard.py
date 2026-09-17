#!/usr/bin/env python3
"""Own isolated Anki launches and check that the owner's collection is unchanged."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Sequence


RECEIPT = "native-session-receipt.json"
ANKI = Path("/Applications/Anki.app/Contents/MacOS/anki")


def owner_collection() -> Path:
    return Path.home() / "Library/Application Support/Anki2/User 1/collection.anki2"


def measure(collection: Path) -> dict:
    try:
        stream = collection.open("rb")
    except FileNotFoundError:
        return {"exists": False}
    with stream:
        before = os.fstat(stream.fileno())
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
        after = os.fstat(stream.fileno())
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError(f"collection changed while measuring: {collection}")
    return {"exists": True, "sha256": digest.hexdigest(),
            "size": after.st_size, "mtime_ns": after.st_mtime_ns}


def require_anki_stopped() -> None:
    result = subprocess.run(
        ("/usr/bin/pgrep", "-ix", "anki"), text=True, capture_output=True,
    )
    if result.returncode == 0:
        raise RuntimeError(
            f"Anki is already running (PIDs: {result.stdout.split()}); "
            "quit Anki before preparing or launching an isolated session"
        )
    if result.returncode != 1:
        raise RuntimeError(f"cannot check whether Anki is running: {result.stderr.strip()}")


def copy_addon(repo: Path, destination: Path) -> None:
    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored = set(shutil.ignore_patterns(
            ".*", "__pycache__", "user_files", "tmp", "memory-bank",
        )(directory, names))
        for name in set(names) - ignored:
            if (Path(directory) / name).is_symlink():
                raise RuntimeError(f"refusing add-on symlink: {Path(directory) / name}")
        return ignored

    shutil.copytree(repo, destination, ignore=ignore)


def prepare(repo: Path) -> Path:
    require_anki_stopped()
    repo = repo.resolve()
    if not (repo / "__init__.py").is_file():
        raise RuntimeError(f"not an add-on repository: {repo}")
    collection = owner_collection()
    baseline = measure(collection)
    base = Path(tempfile.mkdtemp(prefix="ankiscape-native-")).resolve()
    copy_addon(repo, base / "addons21" / "ankiscape_fork")
    receipt = {"base": str(base), "repo": str(repo),
               "collection": str(collection), "baseline": baseline}
    (base / RECEIPT).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    command = (sys.executable, str(Path(__file__).resolve()), "launch", str(base))
    print(json.dumps({"path": str(base), "launch_command": shlex.join(command),
                      "anki_command": shlex.join((str(ANKI), "-b", str(base)))}))
    return base


def read_receipt(base: Path) -> dict:
    base = base.resolve()
    if not (base / RECEIPT).is_file():
        raise RuntimeError(f"not a prepared session (missing {RECEIPT}): {base}")
    receipt = json.loads((base / RECEIPT).read_text(encoding="utf-8"))
    if not isinstance(receipt, dict):
        raise ValueError(f"invalid session receipt: {base}")
    if (receipt.get("base") != str(base)
            or receipt.get("collection") != str(owner_collection())
            or not base.is_relative_to(Path(tempfile.gettempdir()).resolve())
            or not base.name.startswith("ankiscape-native-")):
        raise ValueError(f"receipt does not match an isolated session: {base}")
    baseline = receipt.get("baseline")
    if not isinstance(baseline, dict) or not isinstance(baseline.get("exists"), bool):
        raise ValueError(f"invalid collection baseline: {base}")
    expected = {"exists", "sha256", "size", "mtime_ns"} if baseline["exists"] else {"exists"}
    if set(baseline) != expected:
        raise ValueError(f"incomplete collection baseline: {base}")
    return receipt


def launch(base: Path) -> int:
    base = base.resolve()
    read_receipt(base)
    require_anki_stopped()
    if not (base / "addons21/ankiscape_fork/__init__.py").is_file():
        raise RuntimeError(f"prepared add-on is missing: {base}")
    return subprocess.run((str(ANKI), "-b", str(base)), check=False).returncode


def verify(base: Path) -> int:
    receipt = read_receipt(base)
    before = receipt["baseline"]
    after = measure(owner_collection())
    changes = {key: {"before": before.get(key), "after": after.get(key)}
               for key in sorted(before.keys() | after.keys())
               if before.get(key) != after.get(key)}
    print(json.dumps({"path": str(base.resolve()), "collection": receipt["collection"],
                      "unchanged": not changes, "changes": changes}))
    return 1 if changes else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare")
    for command in ("launch", "verify"):
        subparsers.add_parser(command).add_argument("base", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            prepare(args.repo)
        elif args.command == "launch":
            return launch(args.base)
        else:
            return verify(args.base)
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
