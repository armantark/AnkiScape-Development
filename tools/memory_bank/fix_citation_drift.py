#!/usr/bin/env python3
"""Repoint Memory Bank line citations whose cited text moved, from an audit report.

`tools/audit_citation_drift.py` finds drift but never rewrites a citation. This
tool reads its gzip JSON report and rewrites only what history proves:

- A `moved` row gets the line numbers (and, when the written path no longer
  names the file, the path) where the audit found the cited text.
- A `missing_lines` or `missing_file` row is traced to the commit that first
  wrote its citation token into the record. If the lines cited at that commit
  appear exactly once in the current tree, the row is repointed there.
  Otherwise the code is gone, and the citation is pinned to that commit as
  `<sha>:path:line`, which the audit treats as a fixed historical citation.

Every other row is printed as `unfixed` for a person to rewrite: its target
never existed, is ambiguous, or is written in a form this tool does not edit.
Without `--apply` nothing is written.

The audit resolves a repository citation against the commit that `git blame`
assigns to the record line, so an edited line is checked against the tree of
the commit that edits it. Run the audit again after committing the result.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import subprocess
from dataclasses import dataclass
from functools import cache
from pathlib import Path


STRUCTURAL = frozenset({"moved", "missing_lines", "missing_file"})
NUMBER = r"\d+(?:[-–]\d+)?"


@dataclass(frozen=True)
class Fix:
    record_path: str
    record_line: int
    path: str
    start: int
    end: int
    new_path: str
    new_start: int
    new_end: int
    how: str


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True, errors="replace"
    ).stdout


def _split_target(target: str) -> tuple[str, int, int]:
    path, _, numbers = target.rpartition(":")
    start, _, end = numbers.partition("-")
    return path, int(start), int(end or start)


def _names(written: str, actual: str) -> bool:
    """Whether a path as written in a record (relative, partial or absolute) still names actual."""
    written = written.lstrip("./")
    return actual == written or actual.endswith(f"/{written}") or written.endswith(f"/{actual}")


class Tree:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.paths = tuple(_git(root, "ls-files").splitlines())
        self._first_lines: dict[str, list[tuple[str, int]]] | None = None

    @cache
    def lines(self, path: str) -> tuple[str, ...] | None:
        try:
            return tuple((self.root / path).read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeDecodeError):
            return None

    def find(self, block: tuple[str, ...]) -> list[tuple[str, int, int]]:
        if self._first_lines is None:
            self._first_lines = {}
            for path in self.paths:
                for index, line in enumerate(self.lines(path) or ()):
                    self._first_lines.setdefault(line, []).append((path, index))
        matches = []
        for path, index in self._first_lines.get(block[0], ()):
            if self.lines(path)[index:index + len(block)] == block:
                matches.append((path, index + 1, index + len(block)))
        return matches


@cache
def _tree_paths(root: Path, commit: str) -> tuple[str, ...]:
    return tuple(_git(root, "ls-tree", "-r", "--name-only", commit).splitlines())


def _token(line: str, path: str, start: int, end: int) -> re.Match[str] | None:
    """Find the number item for start-end in the citation list that follows path."""
    item = str(start) if start == end else f"{start}[-–]{end}"
    for occurrence in re.finditer(re.escape(path), line):
        if occurrence.start() and re.match(r"[\w./-]", line[occurrence.start() - 1]):
            continue
        tail = re.match(rf"(?::|`?\s+lines?\s+)((?:{NUMBER}(?:\s*,\s*(?:and\s+)?|\s+and\s+))*){item}(?![\d–-])",
                        line[occurrence.end():])
        if tail:
            return re.compile(rf"{item}(?![\d–-])").search(line, occurrence.end() + tail.start(1) + len(tail.group(1)))
    return None


def _origin(root: Path, row: dict, line: str) -> tuple[str, str, tuple[str, ...]] | None:
    """The commit that first wrote this citation into the record, the cited file's path then, and the cited lines."""
    path, start, end = _split_target(row["target"])
    match = _token(line, path, start, end)
    citation = line[line.rfind(path, 0, match.start()):match.end()]
    commits = _git(root, "log", "--reverse", "--format=%H", "-S", citation, "--", row["record_path"]).split()
    if not commits:
        return None
    candidates = [p for p in _tree_paths(root, commits[0]) if _names(path, p)]
    if len(candidates) != 1:
        return None
    lines = _git(root, "show", f"{commits[0]}:{candidates[0]}").splitlines()
    return (commits[0], candidates[0], tuple(lines[start - 1:end])) if 1 <= start <= end <= len(lines) else None


def _edits(line: str, fix: Fix) -> list[tuple[int, int, str]]:
    match = _token(line, fix.path, fix.start, fix.end)
    numbers = str(fix.new_start) if fix.new_start == fix.new_end else f"{fix.new_start}-{fix.new_end}"
    edits = [(match.start(), match.end(), numbers)]
    if not _names(fix.path, fix.new_path):
        at = line.rfind(fix.path, 0, match.start())
        edits.append((at, at + len(fix.path), fix.new_path))
    return edits


def _repoint(root: Path, tree: Tree, row: dict) -> Fix | None:
    line = tree.lines(row["record_path"])[row["record_line"] - 1]
    path, start, end = _split_target(row["target"])
    if row["source"] != "repository" or _token(line, path, start, end) is None:
        return None
    if row["status"] == "moved":
        return Fix(row["record_path"], row["record_line"], path, start, end, *_split_target(row["real_target"]), "moved")
    origin = _origin(root, row, line)
    if origin is None:
        return None
    commit, origin_path, block = origin
    # A short one-line block such as `material.xp,` can be unique by chance.
    matches = tree.find(block) if len("".join(block).replace(" ", "")) >= 20 else []
    if len(matches) == 1 and matches[0][0] != row["record_path"]:
        return Fix(row["record_path"], row["record_line"], path, start, end, *matches[0], "traced")
    return Fix(row["record_path"], row["record_line"], path, start, end, f"{commit[:8]}:{origin_path}", start, end, "pinned")


def _consistent(report: dict, tree: Tree, candidates: list[tuple[dict, Fix]]) -> list[bool]:
    """One path written before a list such as `a.py:10,20` changes only if the whole list moved to one file."""
    items: dict[tuple[str, int, str], int] = {}
    for row in report["results"]:
        key = (row["record_path"], row["record_line"], _split_target(row["target"])[0])
        items[key] = items.get(key, 0) + 1
    spans: dict[tuple[str, int, int, int], list[str]] = {}
    edits = [_edits(tree.lines(fix.record_path)[fix.record_line - 1], fix) for _, fix in candidates]
    for (_, fix), fix_edits in zip(candidates, edits):
        for begin, finish, text in fix_edits:
            spans.setdefault((fix.record_path, fix.record_line, begin, finish), []).append(text)
    verdicts = []
    for (_, fix), fix_edits in zip(candidates, edits):
        numbers, *path = (spans[(fix.record_path, fix.record_line, begin, finish)] for begin, finish, _ in fix_edits)
        whole_list = not path or (
            len(set(path[0])) == 1 and len(path[0]) == items[(fix.record_path, fix.record_line, fix.path)]
        )
        verdicts.append(whole_list and len(set(numbers)) == 1)
    return verdicts


def _editable(row: dict) -> bool:
    """An actionable audit row: structural drift measured against history."""
    authoritative = row["source"] == "repository" or row["source"].startswith("external:")
    return row["status"] in STRUCTURAL and authoritative


def plan(root: Path, report: dict, skip: frozenset[str]) -> tuple[list[Fix], list[dict]]:
    tree = Tree(root)
    rows = [row for row in report["results"] if _editable(row) and row["record_path"] not in skip]
    repointed = [(row, _repoint(root, tree, row)) for row in rows]
    candidates = [(row, fix) for row, fix in repointed if fix is not None]
    verdicts = _consistent(report, tree, candidates)
    fixes = [fix for (_, fix), ok in zip(candidates, verdicts) if ok]
    unfixed = [row for row, fix in repointed if fix is None]
    unfixed += [row for (row, _), ok in zip(candidates, verdicts) if not ok]
    return fixes, unfixed


def apply(root: Path, fixes: list[Fix]) -> None:
    for record_path in sorted({fix.record_path for fix in fixes}):
        file = root / record_path
        lines = file.read_text(encoding="utf-8").split("\n")
        by_line: dict[int, set[tuple[int, int, str]]] = {}
        for fix in fixes:
            if fix.record_path == record_path:
                by_line.setdefault(fix.record_line, set()).update(_edits(lines[fix.record_line - 1], fix))
        for number, edits in by_line.items():
            line = lines[number - 1]
            for begin, finish, text in sorted(edits, reverse=True):
                line = line[:begin] + text + line[finish:]
            lines[number - 1] = line
        file.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--report", type=Path, help="default: ROOT/memory-bank/citation-drift-results.json.gz")
    parser.add_argument("--skip", action="append", default=[], metavar="RECORD",
                        help="leave this record untouched, e.g. a live document to rewrite by hand")
    parser.add_argument("--apply", action="store_true", help="rewrite the records; default is a dry run")
    args = parser.parse_args()
    root = args.root.resolve()
    report = json.loads(gzip.decompress((args.report or root / "memory-bank/citation-drift-results.json.gz").read_bytes()))
    fixes, unfixed = plan(root, report, frozenset(args.skip))
    for fix in fixes:
        print(f"{fix.how}: {fix.record_path}:{fix.record_line}: {fix.path}:{fix.start}-{fix.end} -> "
              f"{fix.new_path}:{fix.new_start}-{fix.new_end}")
    for row in unfixed:
        print(f"unfixed {row['status']}: {row['record_path']}:{row['record_line']}: {row['target']}")
    counts = ", ".join(f"{sum(f.how == how for f in fixes)} {how}" for how in ("moved", "traced", "pinned"))
    print(f"{len(fixes)} fixable ({counts}), {len(unfixed)} unfixed.")
    if args.apply:
        apply(root, fixes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
