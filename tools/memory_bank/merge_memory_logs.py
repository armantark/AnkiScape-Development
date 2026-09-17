"""Move every dated entry of activeContext.md into progress.md.

activeContext.md keeps only its undated durable sections and the one dated
"Current focus" head. progress.md is the single dated log, ordered newest
first. The move is lossless: an entry whose body differs between the two
files keeps both bodies under one heading.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "memory-bank"
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
KEEP_DATED_PREFIX = "## Current focus"
MERGE_NOTE = "*Parallel record from activeContext.md, merged 2026-09-16:*"


def split(text: str) -> tuple[str, list[list[str]]]:
    lines = text.split("\n")
    preamble: list[str] = []
    sections: list[list[str]] = []
    for line in lines:
        if line.startswith("## "):
            sections.append([line])
        elif sections:
            sections[-1].append(line)
        else:
            preamble.append(line)
    return "\n".join(preamble), sections


def norm(section: list[str]) -> str:
    return re.sub(r"\s+", " ", "\n".join(section[1:])).strip()


def date_of(section: list[str]) -> str:
    found = DATE_RE.findall(section[0])
    return found[-1] if found else ""


def body_rstrip(section: list[str]) -> list[str]:
    body = section[1:]
    while body and not body[-1].strip():
        body.pop()
    return body


def drop_exact_repeats(sections: list[list[str]]) -> list[list[str]]:
    seen: set[tuple[str, str]] = set()
    kept = []
    for section in sections:
        key = (section[0], norm(section))
        if key in seen:
            continue
        seen.add(key)
        kept.append(section)
    return kept


def main() -> None:
    active_path = ROOT / "activeContext.md"
    progress_path = ROOT / "progress.md"
    active_pre, active = split(active_path.read_text())
    progress_pre, progress = split(progress_path.read_text())
    active = drop_exact_repeats(active)
    progress = drop_exact_repeats(progress)

    stay: list[list[str]] = []
    moving: list[list[str]] = []
    for section in active:
        if not date_of(section) or section[0].startswith(KEEP_DATED_PREFIX):
            stay.append(section)
        else:
            moving.append(section)

    by_heading = {section[0]: section for section in progress}
    inserts: list[list[str]] = []
    merged = 0
    for section in moving:
        target = by_heading.get(section[0])
        if target is None:
            inserts.append(section)
        elif norm(target) != norm(section):
            target[:] = [*target[:1], *body_rstrip(target), "", MERGE_NOTE, "", *body_rstrip(section), ""]
            merged += 1

    for section in sorted(inserts, key=date_of):
        date = date_of(section)
        index = next((i for i, s in enumerate(progress) if date_of(s) and date_of(s) < date), len(progress))
        progress.insert(index, section)

    progress_path.write_text(progress_pre + "\n" + "\n".join("\n".join(s) for s in progress))
    active_path.write_text(active_pre + "\n" + "\n".join("\n".join(s) for s in stay))
    print(f"moved {len(inserts)} entries, merged {merged} differing bodies, kept {len(stay)} sections in activeContext.md")


if __name__ == "__main__":
    main()
