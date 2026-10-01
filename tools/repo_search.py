#!/usr/bin/env python3
"""Run bounded repository searches without shell globs or giant generated files."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence


DEFAULT_EXCLUDES = (
    "!.git/**",
    "!**/__pycache__/**",
    "!shop_data.py",
    "!construction_data.py",
    "!combat_data.py",
    "!memory-bank/archive/**",
    "!memory-bank/status-updates/**",
    "!memory-bank/source-audits/npc-shop-coverage-ledger-2026-07-06.json",
)


def _existing_paths(paths: Sequence[str]) -> tuple[list[str], list[str]]:
    existing: list[str] = []
    missing: list[str] = []
    for value in paths:
        (existing if Path(value).exists() else missing).append(value)
    return existing, missing


def _rg_base(paths: Sequence[str], include_large: bool) -> list[str]:
    command = ["rg", "--color=never"]
    if not include_large:
        for pattern in DEFAULT_EXCLUDES:
            command.extend(("--glob", pattern))
    return [*command, *paths]


def find_names(
    pattern: str,
    paths: Sequence[str],
    *,
    include_large: bool,
    max_results: int,
) -> tuple[list[str], bool]:
    command = _rg_base(paths, include_large)
    command.insert(2, "--files")
    matcher = re.compile(pattern, re.IGNORECASE)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert process.stdout is not None
    matches: list[str] = []
    truncated = False
    for line in process.stdout:
        path = line.rstrip("\n")
        if not matcher.search(path):
            continue
        if len(matches) >= max_results:
            truncated = True
            process.terminate()
            break
        matches.append(path)
    _, stderr = process.communicate()
    returncode = process.returncode
    if truncated and returncode in (-15, 143):
        returncode = 0
    if returncode not in (0, 1):
        raise RuntimeError(stderr.strip() or f"rg exited {returncode}")
    return matches, truncated


def search_text(
    pattern: str,
    paths: Sequence[str],
    *,
    include_large: bool,
    max_results: int,
    max_columns: int,
) -> tuple[list[str], bool, int]:
    command = _rg_base(paths, include_large)
    command[2:2] = [
        "--line-number",
        "--no-heading",
        "--max-columns",
        str(max_columns),
        pattern,
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert process.stdout is not None
    lines: list[str] = []
    truncated = False
    for line in process.stdout:
        if len(lines) >= max_results:
            truncated = True
            process.terminate()
            break
        lines.append(line.rstrip("\n"))
    _, stderr = process.communicate()
    returncode = process.returncode
    if truncated and returncode in (-15, 143):
        returncode = 0
    if returncode not in (0, 1):
        raise RuntimeError(stderr.strip() or f"rg exited {returncode}")
    return lines, truncated, returncode


def read_line_range(
    path: Path,
    start: int,
    end: int,
    *,
    max_results: int,
    max_columns: int,
) -> tuple[list[str], bool]:
    lines: list[str] = []
    truncated = False
    with path.open(encoding="utf-8") as source:
        for line_number, raw_line in enumerate(source, start=1):
            if line_number < start:
                continue
            if line_number > end:
                break
            if len(lines) >= max_results:
                truncated = True
                break
            text = raw_line.rstrip("\r\n")
            omitted = max(0, len(text) - max_columns)
            preview = text[:max_columns]
            if omitted:
                preview += f" [omitted {omitted} columns]"
            lines.append(f"{path}:{line_number}:{preview}")
    return lines, truncated


def run_line_range(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.pattern is not None or args.paths or args.names or args.include_large:
        parser.error("--line-range cannot be combined with search arguments")
    path_text, start_text, end_text = args.line_range
    try:
        start, end = int(start_text), int(end_text)
    except ValueError:
        parser.error("--line-range START and END must be integers")
    if start < 1 or end < start:
        parser.error("--line-range requires 1 <= START <= END")
    path = Path(path_text)
    if not path.is_file():
        parser.error(f"--line-range file does not exist: {path}")
    lines, truncated = read_line_range(
        path,
        start,
        end,
        max_results=args.max_results,
        max_columns=args.max_columns,
    )
    for line in lines:
        print(line)
    if not truncated:
        return 0
    print(
        f"Line read stopped at {args.max_results} results; narrow the range "
        "or raise --max-results.",
        file=sys.stderr,
    )
    return 2


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pattern", nargs="?", help="regular expression for text or repository-relative paths")
    parser.add_argument("paths", nargs="*", help="existing files or directories; shell globs are unnecessary")
    parser.add_argument("--names", action="store_true", help="search file names instead of file contents")
    parser.add_argument("--include-large", action="store_true", help="include known giant generated/archive files")
    parser.add_argument(
        "--line-range",
        nargs=3,
        metavar=("FILE", "START", "END"),
        help="print a bounded source excerpt; giant lines include an omission marker",
    )
    parser.add_argument("--max-results", type=int, default=200)
    parser.add_argument("--max-columns", type=int, default=500)
    args = parser.parse_args(argv)

    if args.max_results < 1 or args.max_columns < 1:
        parser.error("--max-results and --max-columns must be at least 1")
    if args.line_range:
        return run_line_range(args, parser)
    if args.pattern is None:
        parser.error("pattern is required unless --line-range is used")
    paths = args.paths or ["."]
    existing, missing = _existing_paths(paths)
    if missing:
        print(f"Missing path(s): {', '.join(missing)}", file=sys.stderr)
        print("Use --names from an existing parent directory to locate moved files.", file=sys.stderr)
        return 2

    try:
        if args.names:
            lines, truncated = find_names(
                args.pattern,
                existing,
                include_large=args.include_large,
                max_results=args.max_results,
            )
            returncode = 0 if lines else 1
        else:
            lines, truncated, returncode = search_text(
                args.pattern,
                existing,
                include_large=args.include_large,
                max_results=args.max_results,
                max_columns=args.max_columns,
            )
    except (re.error, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    for line in lines:
        print(line)
    if truncated:
        print(
            f"Search stopped at {args.max_results} results; narrow the paths/pattern "
            "or raise --max-results.",
            file=sys.stderr,
        )
        return 2
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
