#!/usr/bin/env python3
"""Move closed papercut lines verbatim into a dated papercuts-fixed file, and prove no line was lost.

`move PLAN` reads a JSON plan:

    {"destination": "memory-bank/papercuts-fixed-YYYY-MM-DD.md",
     "sections": [{"heading": "...", "disposition": "fixed",
                   "evidence": "commit ...", "lines": ["- 2026-..."]}]}

Each line is an entry of `memory-bank/papercuts.md`, copied exactly. Naming
entries by text rather than line number means a plan written before another
move finished still moves the entries it names, or refuses if they are gone.
Each section is appended to the destination as `## heading`, the note, then
its lines in their order in `papercuts.md`. Nothing is
written unless the result passes the same proof as `check`, and both files
are staged in full before either is replaced, so a failed write loses nothing.
Moves run one at a time: a second move waits until the first has finished.

`append TIMESTAMP INCIDENT` constructs and appends one required `- ` bullet while
holding the same lock as moves. Multiline values are refused before any write.

`check BASE` proves that every line the papercut logs held at git revision
BASE is still in one of them, and that no open papercut is also recorded as
fixed.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import subprocess
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator, Sequence


PAPERCUTS = "memory-bank/papercuts.md"
FIXED_RE = re.compile(r"memory-bank/papercuts-fixed-(\d{4}-\d{2}-\d{2})\.md")


def _lines(texts: Iterable[str]) -> Counter[str]:
    # Older fixed files hold entries without the `- ` bullet; stripping it on
    # both sides keeps that historical form from reading as a lost line.
    return Counter(
        line.removeprefix("- ") for text in texts for line in text.splitlines() if line.strip()
    )


def _fixed_paths(root: Path) -> list[Path]:
    return sorted((root / "memory-bank").glob("papercuts-fixed-*.md"))


@contextmanager
def _exclusive(directory: Path) -> Iterator[None]:
    # The lock sits on the directory because replacing a log swaps its inode, so a
    # lock on the log itself would not stop the next move from reading stale text.
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        os.close(descriptor)


def _replace(texts: dict[Path, str]) -> None:
    staged = {path: path.with_name(f".{path.name}.staged") for path in texts}
    try:
        for path, text in texts.items():
            staged[path].write_text(text, encoding="utf-8")
        for path in texts:
            staged[path].replace(path)
    finally:
        for path in staged.values():
            path.unlink(missing_ok=True)


def problems(before: Sequence[str], open_log: str, fixed_logs: Sequence[str]) -> list[str]:
    lost = _lines(before) - _lines([open_log, *fixed_logs])
    # Only entries count as open: a category heading may repeat in a fixed log.
    entries = {line.removeprefix("- ") for line in open_log.splitlines() if line.startswith("- ")}
    both = entries & _lines(fixed_logs).keys()
    return [f"lost: {line}" for line in sorted(lost.elements())] + [
        f"open and fixed: {line}" for line in sorted(both)
    ]


def _choose(source: Sequence[str], entry: str, chosen: set[int]) -> int:
    for number, line in enumerate(source):
        if number not in chosen and line.rstrip("\n") == entry and entry.startswith("- "):
            chosen.add(number)
            return number
    raise SystemExit(f"not an open entry of {PAPERCUTS}, or chosen twice: {entry}")


def _closure_note(section: dict) -> str:
    disposition = section.get("disposition")
    if disposition not in {"fixed", "duplicate"}:
        raise SystemExit("each move section requires disposition 'fixed' or 'duplicate'")
    evidence = section.get("evidence")
    if not isinstance(evidence, str) or not evidence.strip():
        raise SystemExit(f"{disposition} disposition requires non-empty evidence")
    parts = [f"Disposition: {disposition}.", f"Evidence: {evidence.strip()}"]
    note = section.get("note", "")
    if note:
        if not isinstance(note, str):
            raise SystemExit("section note must be text")
        parts.append(note.strip())
    return "\n\n".join(parts)


def append(root: Path, timestamp: str, incident: str) -> bool:
    if not timestamp.strip() or not incident.strip() or any(
        character in timestamp or character in incident for character in "\r\n"
    ):
        raise SystemExit("timestamp and incident must each be non-empty single-line text")
    entry = f"- {timestamp.strip()} — {incident.strip()}"
    source_path = root / PAPERCUTS
    with _exclusive(root / "memory-bank"):
        source_text = source_path.read_text(encoding="utf-8")
        if entry in source_text.splitlines():
            return False
        archived = _lines(path.read_text(encoding="utf-8") for path in _fixed_paths(root))
        if entry.removeprefix("- ") in archived:
            raise SystemExit("entry is already archived as fixed; it cannot be reopened")
        updated = source_text.rstrip("\n") + "\n" + entry + "\n"
        _replace({source_path: updated})
    return True


def move(root: Path, plan: dict) -> tuple[int, list[str]]:
    match = FIXED_RE.fullmatch(plan["destination"])
    if not match:
        raise SystemExit(f"destination must be memory-bank/papercuts-fixed-YYYY-MM-DD.md: {plan['destination']}")
    sections = plan.get("sections", [])
    closure_notes = [_closure_note(section) for section in sections]
    source_path, destination = root / PAPERCUTS, root / plan["destination"]
    with _exclusive(root / "memory-bank"):
        source_text = source_path.read_text(encoding="utf-8")
        source = source_text.splitlines(keepends=True)
        fixed_before = (
            destination.read_text(encoding="utf-8")
            if destination.exists()
            else f"# Papercuts fixed — {match.group(1)}\n"
        )
        chosen: set[int] = set()
        fixed_after = fixed_before
        for section, closure_note in zip(sections, closure_notes):
            numbers = [_choose(source, entry, chosen) for entry in section["lines"]]
            fixed_after += f"\n## {section['heading']}\n\n{closure_note}\n\n" + "".join(
                source[number] for number in sorted(numbers)
            )
        remaining = "".join(line for number, line in enumerate(source) if number not in chosen)
        others = [path.read_text(encoding="utf-8") for path in _fixed_paths(root) if path != destination]
        errors = problems([source_text, fixed_before], remaining, [*others, fixed_after])
        if not errors:
            # The archive lands first: if the second replace fails, lines are duplicated, never lost.
            _replace({destination: fixed_after, source_path: remaining})
    return len(chosen), errors


def check(root: Path, base: str) -> list[str]:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=root, check=True, capture_output=True, text=True
        ).stdout

    names = git("ls-tree", "--name-only", base, "memory-bank/").splitlines()
    before = [git("show", f"{base}:{name}") for name in names if name == PAPERCUTS or FIXED_RE.fullmatch(name)]
    return problems(
        before,
        (root / PAPERCUTS).read_text(encoding="utf-8"),
        [path.read_text(encoding="utf-8") for path in _fixed_paths(root)],
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("move").add_argument("plan", type=Path)
    append_parser = commands.add_parser("append")
    append_parser.add_argument("timestamp")
    append_parser.add_argument("incident")
    commands.add_parser("check").add_argument("base")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "move":
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        count, errors = move(root, plan)
        success = f"Moved {count} papercut lines into {plan['destination']}; no line lost."
        failure = "Nothing was written."
    elif args.command == "append":
        added = append(root, args.timestamp, args.incident)
        errors = []
        success = "Appended one papercut entry." if added else "Papercut entry already open; nothing changed."
        failure = "Nothing was written."
    else:
        errors = check(root, args.base)
        success = f"No papercut line lost since {args.base}; no open papercut is also fixed."
        failure = f"Papercut logs changed unsafely since {args.base}."
    for error in errors:
        print(error)
    print(failure if errors else success)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
