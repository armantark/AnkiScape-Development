"""Freeze an exact commit for a native check without opening Anki."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import sys
import tarfile
import tempfile
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.native.session_guard import copy_addon
from tools.promotion.repository import _git, commit_at
from tools.promotion.snapshot import commit_snapshot
from tools.run_remote_tests import (
    HOST, REMOTE_ROOT, REMOTE_VENV, RSYNC_SSH, _on_test_host, _run_with_retries, _ssh,
)


def _transfer_bundle(output: Path, commit: str, archive_sha256: str) -> None:
    remote = REMOTE_ROOT / "native-input" / commit
    _ssh(f"mkdir -p {shlex.quote(str(remote))}", label="native packet directory", repeat_safe=True)
    destination = f"{remote}/" if _on_test_host() else f"{HOST}:{remote}/"
    _run_with_retries(
        ("rsync", "-a", "-e", RSYNC_SSH, str(output / "source.tar.gz"),
         str(output / "manifest.json"), destination),
        label="native packet transfer",
    )
    program = (
        "import hashlib,json;from pathlib import Path;"
        f"p=Path({str(remote)!r});m=json.loads((p/'manifest.json').read_text());"
        "h=hashlib.sha256((p/'source.tar.gz').read_bytes()).hexdigest();"
        "print(json.dumps({'commit':m['commit'],'archive_sha256':h}))"
    )
    raw = _ssh(
        f"{shlex.quote(str(REMOTE_VENV / 'bin/python'))} -c {shlex.quote(program)}",
        label="native packet hash check", repeat_safe=True,
    )
    received = json.loads(raw)
    if received != {"commit": commit, "archive_sha256": archive_sha256}:
        raise RuntimeError("remote native packet does not match the frozen source")
    (output / "remote-transfer.json").write_text(
        json.dumps({"remote_packet": str(remote), "received": received}, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("worktree", type=Path)
    parser.add_argument("commit")
    parser.add_argument("output", type=Path)
    parser.add_argument("--transfer", action="store_true", help="copy the verified packet to the MacBook")
    args = parser.parse_args()
    worktree = args.worktree.resolve()
    if commit_at(worktree) != args.commit:
        raise RuntimeError("source revision does not match the requested commit")
    if _git(worktree, "status", "--porcelain").stdout:
        raise RuntimeError("source checkout is dirty")
    args.output.mkdir(parents=True)
    archive = args.output / "source.tar.gz"
    with tempfile.TemporaryDirectory(prefix=".source-", dir=args.output) as temporary:
        addon = Path(temporary) / "source"
        with commit_snapshot(worktree, args.commit) as snapshot:
            copy_addon(snapshot, addon)
        files = [
            {"path": path.relative_to(addon).as_posix(),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(addon.rglob("*")) if path.is_file()
        ]
        with tarfile.open(archive, "w:gz") as stream:
            stream.add(addon, arcname="source")
    digest = hashlib.sha256()
    for row in files:
        digest.update(row["path"].encode("utf-8") + b"\0")
        digest.update(bytes.fromhex(row["sha256"]))
    with archive.open("rb") as stream:
        archive_digest = hashlib.file_digest(stream, "sha256").hexdigest()
    manifest = {
        "commit": args.commit,
        "source_sha256": digest.hexdigest(),
        "archive_sha256": archive_digest,
        "files": files,
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    if args.transfer:
        _transfer_bundle(args.output, args.commit, manifest["archive_sha256"])
    print(args.output / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
