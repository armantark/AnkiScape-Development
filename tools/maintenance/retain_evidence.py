"""Retain bounded proof packets and share duplicate immutable evidence on APFS."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from tools.native.session_guard import _copy_file

MAX_FILE_BYTES = 256 * 1024 * 1024
MAX_PACKET_BYTES = 1024 * 1024 * 1024


def _git(repo: Path, *parts: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *parts], text=True).strip()


def _hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _fingerprint(path: Path) -> tuple[int, int, int, int]:
    state = path.stat()
    return state.st_dev, state.st_ino, state.st_size, state.st_mtime_ns


def _contained_file(path: Path, root: Path) -> Path:
    if ".." in path.parts or ".." in root.parts or not path.is_absolute() or not path.is_relative_to(root):
        raise ValueError(f"evidence path escapes root: {path}")
    for parent in (root, *path.relative_to(root).parents):
        candidate = parent if parent.is_absolute() else root / parent
        if candidate.is_symlink():
            raise ValueError(f"evidence path contains a symlink: {candidate}")
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"evidence must be a regular file: {path}")
    return path


def _source_entries(source: Path) -> list[tuple[Path, Path, int]]:
    if source.is_symlink():
        raise ValueError(f"refusing symlinked evidence input: {source}")
    source = source.resolve(strict=True)
    directory = source.is_dir()
    paths = sorted(source.rglob("*")) if directory else [source]
    files = []
    for path in paths:
        if path.is_symlink():
            raise ValueError(f"refusing symlinked evidence input: {path}")
        if not path.is_file():
            continue
        relative = Path(source.name) / path.relative_to(source) if directory else Path(source.name)
        files.append((path, relative, path.stat().st_size))
    return files


def _retention_inputs(sources: list[Path]) -> list[tuple[Path, Path, int]]:
    return [entry for source in sources for entry in _source_entries(source)]


def _check_budget(files: list[tuple[Path, Path, int]], max_file: int, max_packet: int) -> None:
    if len({relative for _, relative, _ in files}) != len(files):
        raise ValueError("evidence names collide")
    if any(size > max_file for _, _, size in files) or sum(size for _, _, size in files) > max_packet:
        raise ValueError("evidence exceeds the 256 MiB file / 1 GiB packet budget")


def _retained_target(destination: Path, relative: Path) -> Path:
    target = destination / relative
    for parent in (target, *target.parents):
        if parent == destination.parent:
            break
        if parent.is_symlink():
            raise ValueError(f"refusing symlinked evidence destination: {parent}")
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _retain_file(path: Path, target: Path, size: int) -> dict:
    before = _fingerprint(path)
    digest = _hash(path)
    if target.exists():
        if _hash(target) != digest:
            raise ValueError(f"refusing to replace distinct evidence: {target}")
    else:
        _copy_file(str(path), str(target))
    if _fingerprint(path) != before or _hash(target) != digest:
        raise RuntimeError(f"evidence changed while retaining: {path}")
    return {"source": str(path), "retained": str(target), "bytes": size, "sha256": digest}


def retain(repo: Path, revision: str, destination: Path, sources: list[Path], *,
           max_file_bytes: int = MAX_FILE_BYTES, max_packet_bytes: int = MAX_PACKET_BYTES) -> dict:
    repo = repo.resolve(strict=True)
    if _git(repo, "rev-parse", "HEAD") != revision or _git(repo, "status", "--porcelain"):
        raise ValueError("evidence source revision is wrong or dirty")
    if destination.is_symlink():
        raise ValueError(f"refusing symlinked evidence destination: {destination}")
    destination = destination.absolute()
    manifest_path = destination / "retention-manifest.json"
    if manifest_path.exists():
        raise FileExistsError(manifest_path)
    files = _retention_inputs(sources)
    _check_budget(files, max_file_bytes, max_packet_bytes)
    rows = [_retain_file(path, _retained_target(destination, relative), size)
            for path, relative, size in files]
    if _git(repo, "rev-parse", "HEAD") != revision or _git(repo, "status", "--porcelain"):
        raise RuntimeError("evidence source revision changed while retaining")
    manifest = {"source_repo": str(repo), "source_head": revision,
                "retained_at": datetime.now(timezone.utc).isoformat(), "files": rows}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return {"source_head": revision, "files_retained": len(rows), "manifest": str(manifest_path)}


def _compaction_pair(row: dict, source_root: Path, packet: Path) -> tuple[Path, Path]:
    source = _contained_file(Path(row["source"]), source_root)
    target = _contained_file(Path(row["retained"]), packet)
    source_state, target_state = _fingerprint(source), _fingerprint(target)
    if source == target or source_state[:2] == target_state[:2]:
        raise ValueError("evidence source and retained copy must be independent")
    if source_state[2] != row["bytes"] or target_state[2] != row["bytes"]:
        raise ValueError(f"evidence size differs from receipt: {target}")
    return source, target


def _share_verified_pair(source: Path, target: Path, digest: str, manifest: Path,
                         receipt_before: tuple[int, ...]) -> None:
    source_before, target_before = _fingerprint(source), _fingerprint(target)
    if _hash(source) != digest or _hash(target) != digest:
        raise ValueError(f"evidence bytes differ from receipt: {target}")
    temporary = target.with_name(f".{target.name}.compact-{uuid.uuid4().hex}")
    try:
        _copy_file(str(source), str(temporary))
        shutil.copystat(target, temporary)
        if (_fingerprint(source) != source_before or _fingerprint(target) != target_before
                or _fingerprint(manifest) != receipt_before):
            raise RuntimeError(f"evidence changed during compaction: {target}")
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def compact(manifest_path: Path, source_root: Path, *, min_bytes: int = 64 * 1024 * 1024,
            apply: bool = False) -> dict:
    source_root = source_root.absolute()
    manifest_path = manifest_path.absolute()
    _contained_file(manifest_path, manifest_path.parent)
    receipt_before = _fingerprint(manifest_path)
    rows = [row for row in json.loads(manifest_path.read_text())["files"] if row["bytes"] >= min_bytes]
    for row in rows:
        source, target = _compaction_pair(row, source_root, manifest_path.parent)
        if apply:
            _share_verified_pair(source, target, row["sha256"], manifest_path, receipt_before)
    return {"manifest": str(manifest_path), "files": len(rows),
            "eligible_bytes": sum(row["bytes"] for row in rows), "applied": apply,
            "hashes_verified": apply}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    keep = commands.add_parser("retain")
    keep.add_argument("repo", type=Path)
    keep.add_argument("revision")
    keep.add_argument("destination", type=Path)
    keep.add_argument("sources", nargs="+", type=Path)
    share = commands.add_parser("compact")
    share.add_argument("manifest", type=Path)
    share.add_argument("source_root", type=Path)
    share.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.command == "retain":
        result = retain(args.repo, args.revision, args.destination, args.sources)
    else:
        if sys.platform != "darwin":
            parser.error("APFS evidence compaction requires Darwin")
        result = compact(args.manifest, args.source_root, apply=args.apply)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
