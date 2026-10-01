#!/usr/bin/env python3
"""Append one Markdown record with one blank separator and one terminal newline.

The record is read from standard input. Existing content and meaningful interior
whitespace are preserved; blank lines at the append boundary are normalized.
"""

from __future__ import annotations

import argparse
import fcntl
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Sequence


@contextmanager
def _exclusive(directory: Path) -> Iterator[None]:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        os.close(descriptor)


def _without_trailing_blank_lines(text: str) -> str:
    lines = text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def _without_boundary_blank_lines(text: str) -> str:
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def appended_text(existing: str, record: str) -> str:
    existing = _without_trailing_blank_lines(existing)
    record = _without_boundary_blank_lines(record)
    if not record:
        raise ValueError("record must contain non-blank text")
    return f"{existing}\n\n{record}\n" if existing else f"{record}\n"


def append_record(path: Path, record: str) -> None:
    with _exclusive(path.parent):
        updated = appended_text(path.read_text(encoding="utf-8"), record)
        staged = path.with_name(f".{path.name}.staged")
        try:
            staged.write_text(updated, encoding="utf-8")
            staged.replace(path)
        finally:
            staged.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="existing Markdown ledger to update")
    args = parser.parse_args(argv)
    path = args.path.resolve()
    if path.suffix.lower() != ".md" or not path.is_file():
        parser.error(f"path must be an existing Markdown file: {args.path}")
    try:
        append_record(path, sys.stdin.read())
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Appended one record to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
