"""Bound successful remote reports while preserving protected evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


RUN_ID = re.compile(r"(?:plain|qt)-[0-9]+-[0-9a-f]{8}")
GROUP_FILE = re.compile(r"((?:plain|qt)-[0-9]+-[0-9a-f]{8})(\..*)?")
SUFFIXES = {".log", ".report", ".pid", ".skips.json"}


@dataclass(frozen=True)
class ReportGroup:
    run_id: str
    files: tuple[tuple[Path, tuple[int, ...]], ...]
    modified_ns: int
    size: int


@dataclass(frozen=True)
class RetentionPlan:
    root: Path
    root_identity: tuple[int, ...]
    pins_identity: tuple[int, ...]
    remove: tuple[ReportGroup, ...]
    kept: tuple[str, ...]
    protected: dict[str, str]


def _identity(path: Path) -> tuple[int, ...]:
    value = path.lstat()
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns, value.st_nlink)


def _root_identity(root: Path) -> tuple[int, ...]:
    if (not root.is_absolute() or root != root.resolve(strict=True)
            or root.name != "reports" or root.parent == Path(root.anchor)
            or root == Path.home().resolve() or not root.is_dir()):
        raise ValueError(f"not an isolated reports directory: {root}")
    return _identity(root)


def _read_small(path: Path, limit: int) -> bytes:
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), "rb") as stream:
        contents = stream.read(limit + 1)
    if len(contents) > limit:
        raise ValueError(f"oversized retention record: {path}")
    return contents


def _pins(root: Path) -> tuple[set[str], tuple[int, ...]]:
    path = root / ".retained.json"
    identity = _identity(path)
    if not stat.S_ISREG(identity[2]) or identity[6] != 1:
        raise ValueError(f"retention pins must be an independent regular file: {path}")
    pins = json.loads(_read_small(path, 1024 * 1024))
    if not isinstance(pins, list) or any(
        not isinstance(pin, str) or RUN_ID.fullmatch(pin) is None for pin in pins
    ):
        raise ValueError(f"retention pins must be a list of exact run IDs: {path}")
    if _identity(path) != identity:
        raise RuntimeError(f"retention pins changed while reading: {path}")
    return set(pins), identity


def _open_files(root: Path) -> set[Path]:
    witness = root / ".retained.json"
    # A full FD scan avoids treating unopened sibling reports as failed selectors.
    directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        with os.fdopen(os.open(witness, os.O_RDONLY | os.O_NOFOLLOW), "rb"):
            result = subprocess.run(("/usr/sbin/lsof", "-nP", "-F", "n"),
                                    text=True, capture_output=True, timeout=30)
    finally:
        os.close(directory_fd)
    paths = {Path(line[1:].removesuffix(" (deleted)")).resolve() for line in result.stdout.splitlines()
             if line.startswith("n/")}
    paths = {path for path in paths if path == root or path.parent == root}
    missing = sorted(str(path) for path in {root, witness} - paths)
    if result.returncode != 0 or result.stderr or missing:
        raise RuntimeError(
            f"cannot establish open report files: returncode={result.returncode}; "
            f"missing_witnesses={missing}; stderr={result.stderr!r}"
        )
    return paths


def _completed_group(run_id: str, paths: list[Path]) -> ReportGroup | None:
    suffixes = {path.name[len(run_id):] for path in paths}
    if not suffixes <= SUFFIXES or not {".log", ".report", ".pid"} <= suffixes:
        return None
    files = tuple((path, _identity(path)) for path in sorted(paths))
    if any(not stat.S_ISREG(identity[2]) or identity[6] != 1 for _, identity in files):
        return None
    root = paths[0].parent
    if _read_small(root / f"{run_id}.report", 32) not in {b"0", b"0\n"}:
        return None
    pid = _read_small(root / f"{run_id}.pid", 32).strip()
    if re.fullmatch(rb"[0-9]+", pid) is None or int(pid) <= 1:
        return None
    if any(_identity(path) != identity for path, identity in files):
        return None
    return ReportGroup(run_id, files, max(identity[4] for _, identity in files),
                       sum(identity[3] for _, identity in files))


def _qualify_groups(root: Path, pins: set[str], opened: set[Path]) -> tuple[list[ReportGroup], dict[str, str]]:
    grouped: dict[str, list[Path]] = {}
    for path in root.iterdir():
        match = GROUP_FILE.fullmatch(path.name)
        if match:
            grouped.setdefault(match[1], []).append(path)
    eligible, protected = [], {}
    for run_id, paths in sorted(grouped.items()):
        if run_id in pins or opened.intersection(paths):
            protected[run_id] = "pinned or open"
            continue
        try:
            group = _completed_group(run_id, paths)
        except (OSError, ValueError):
            group = None
        if group is None:
            protected[run_id] = "unresolved, failed, malformed or unknown"
        else:
            eligible.append(group)
    return eligible, protected


def _select_groups(eligible: list[ReportGroup], cutoff_ns: int, max_groups: int,
                   max_bytes: int) -> tuple[tuple[str, ...], tuple[ReportGroup, ...]]:
    kept, remove, retained_bytes = [], [], 0
    for group in sorted(eligible, key=lambda group: (-group.modified_ns, group.run_id)):
        if (group.modified_ns <= cutoff_ns or len(kept) >= max_groups
                or retained_bytes + group.size > max_bytes):
            remove.append(group)
        else:
            kept.append(group.run_id)
            retained_bytes += group.size
    return tuple(kept), tuple(remove)


def plan_retention(root: Path, *, now: float | None = None, max_age_days: int = 7,
                   max_groups: int = 128, max_bytes: int = 64 * 1024 * 1024) -> RetentionPlan:
    root_identity = _root_identity(root)
    pins, pins_identity = _pins(root)
    eligible, protected = _qualify_groups(root, pins, _open_files(root))
    cutoff_ns = int(((time.time() if now is None else now) - max_age_days * 86400) * 1e9)
    kept, remove = _select_groups(eligible, cutoff_ns, max_groups, max_bytes)
    return RetentionPlan(root, root_identity, pins_identity, remove, kept, protected)


def _validate_group_namespace(root: Path, group: ReportGroup) -> None:
    names = {group.run_id + suffix for suffix in SUFFIXES}
    if RUN_ID.fullmatch(group.run_id) is None or any(
        path.parent != root or path.name not in names
        or not stat.S_ISREG(identity[2]) or identity[6] != 1 for path, identity in group.files
    ):
        raise ValueError(f"report group escapes the retention boundary: {group.run_id}")


def _validate_removal_plan(plan: RetentionPlan) -> None:
    if _root_identity(plan.root) != plan.root_identity or _pins(plan.root)[1] != plan.pins_identity:
        raise RuntimeError("reports root or retention pins changed after planning")
    for group in plan.remove:
        _validate_group_namespace(plan.root, group)
    opened = _open_files(plan.root)
    for group in plan.remove:
        if any(path in opened or _identity(path) != identity for path, identity in group.files):
            raise RuntimeError(f"report group changed or opened after planning: {group.run_id}")


def _unlink_group(plan: RetentionPlan, group: ReportGroup, root_identity: tuple[int, ...]) -> tuple[int, ...]:
    if _root_identity(plan.root) != root_identity or _identity(
        plan.root / ".retained.json"
    ) != plan.pins_identity:
        raise RuntimeError("reports root or retention pins changed during cleanup")
    if any(_identity(path) != identity for path, identity in group.files):
        raise RuntimeError(f"report group changed before unlink: {group.run_id}")
    for path, identity in group.files:
        if _identity(path) != identity:
            raise RuntimeError(f"report file changed before unlink: {path}")
        path.unlink()
    return _root_identity(plan.root)


def apply_retention(plan: RetentionPlan) -> None:
    _validate_removal_plan(plan)
    root_identity = plan.root_identity
    for group in plan.remove:
        root_identity = _unlink_group(plan, group, root_identity)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    plan = plan_retention(args.root)
    if args.apply:
        apply_retention(plan)
    print(json.dumps({"root": str(plan.root), "applied": args.apply,
                      "remove_groups": len(plan.remove),
                      "remove_files": sum(len(group.files) for group in plan.remove),
                      "remove_bytes": sum(group.size for group in plan.remove),
                      "kept_groups": len(plan.kept), "protected_groups": len(plan.protected),
                      "protected_reasons": dict(sorted(Counter(plan.protected.values()).items()))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
