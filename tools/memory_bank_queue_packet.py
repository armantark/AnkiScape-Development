#!/usr/bin/env python3
"""Build a line-numbered Memory Bank queue packet without reading it into a prompt.

The packet is capped at 32 KiB by default, measured as encoded UTF-8 including
its omission report. Intrinsic source limits keep each section focused. Every
source omitted by the byte cap or truncated by an intrinsic limit is named in
the final report. If that report cannot fit, the command exits with an error
instead of producing a silently incomplete packet.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


DEFAULT_MAX_BYTES = 32 * 1024
MIN_MAX_BYTES = 1024
TOP_SECTION_LIMIT = 2
SECTION_LINE_LIMIT = 24
QUEUE_ENTRY_LIMIT = 8
ENTRY_CONTEXT_LIMIT = 3
LABEL_LIMIT = 6
BACKLOG_ITEM_LIMIT = 12
PAPERCUT_LIMIT = 8

_REQUIRED_FILES = (
    "activeContext.md",
    "progress.md",
    "future-work-kanban.md",
    "design-thread-queue.md",
    "gpt-deferred-queue.md",
    "loop-queue.md",
    "gap-backlog.json",
    "papercuts.md",
)
_CLOSED_BACKLOG_STATUSES = frozenset({
    "implemented",
    "implemented_verified",
    "merged",
    "rejected_out_of_period",
    "rejected_product_scope",
    "verified",
})
_CHECKBOX_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+\[([ xX])\]\s+")
_LABEL_RE = re.compile(
    r"^\s*(?:[-*+]\s+)?(?:\*\*)?"
    r"(?:Status|Labels?|Blockers?|Blocks|Class|Classification)(?:\*\*)?\s*:",
    re.IGNORECASE,
)
_PAPERCUT_RE = re.compile(r"^(?:- )?(\d{4}-\d{2}-\d{2})(?=T|\s|:|$)")
_BACKLOG_FIELDS = frozenset({"id", "skill", "title", "status", "note"})


class PacketError(ValueError):
    """Raised when a packet cannot be built truthfully."""


@dataclass(frozen=True)
class SourceBlock:
    source: str
    lines: tuple[str, ...]
    truncations: tuple[str, ...] = ()


def _read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise PacketError(f"cannot read {path}: {exc}") from exc


def _source_name(root_number: int, filename: str) -> str:
    return f"root[{root_number}]/memory-bank/{filename}"


def _referenced(source: str, lines: Sequence[str], indexes: Sequence[int]) -> tuple[str, ...]:
    return tuple(
        f"{source}:{index + 1}: {lines[index]}"
        for index in indexes
        if lines[index].strip()
    )


def _top_sections(path: Path, source: str) -> SourceBlock:
    lines = _read_lines(path)
    starts = [index for index, line in enumerate(lines) if line.startswith("## ")]
    if not starts:
        raise PacketError(f"{path} has no top-level '##' sections")

    selected: list[int] = []
    truncations: list[str] = []
    for position, start in enumerate(starts[:TOP_SECTION_LIMIT]):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        bounded_end = min(end, start + SECTION_LINE_LIMIT)
        selected.extend(range(start, bounded_end))
        if bounded_end < end:
            truncations.append(
                f"section at line {start + 1} kept {SECTION_LINE_LIMIT} of {end - start} lines"
            )
    if len(starts) > TOP_SECTION_LIMIT:
        truncations.append(
            f"kept first {TOP_SECTION_LIMIT} of {len(starts)} top-level sections"
        )
    return SourceBlock(source, _referenced(source, lines, selected), tuple(truncations))


def _context_indexes(
    lines: Sequence[str],
    start: int,
    entry_re: re.Pattern[str] = _CHECKBOX_RE,
) -> tuple[list[int], bool]:
    indexes = [start]
    cursor = start + 1
    while cursor < len(lines) and len(indexes) <= ENTRY_CONTEXT_LIMIT:
        line = lines[cursor]
        if not line.strip() or line.startswith("#") or entry_re.match(line):
            break
        indexes.append(cursor)
        cursor += 1
    truncated = (
        cursor < len(lines)
        and len(indexes) > ENTRY_CONTEXT_LIMIT
        and bool(lines[cursor].strip())
        and not lines[cursor].startswith("#")
        and not entry_re.match(lines[cursor])
    )
    return indexes, truncated


def _queue_state(path: Path, source: str) -> SourceBlock:
    lines = _read_lines(path)
    unchecked = [
        index for index, line in enumerate(lines)
        if (match := _CHECKBOX_RE.match(line)) and match.group(1) == " "
    ]
    labels = [index for index, line in enumerate(lines) if _LABEL_RE.match(line)]

    selected: set[int] = set()
    truncations: list[str] = []
    for index in unchecked[:QUEUE_ENTRY_LIMIT]:
        context, truncated = _context_indexes(lines, index)
        selected.update(context)
        if truncated:
            truncations.append(
                f"unchecked entry at line {index + 1} kept {ENTRY_CONTEXT_LIMIT} context lines"
            )
    if len(unchecked) > QUEUE_ENTRY_LIMIT:
        truncations.append(
            f"kept first {QUEUE_ENTRY_LIMIT} of {len(unchecked)} unchecked entries"
        )

    chosen_labels = labels[:LABEL_LIMIT]
    if len(labels) > LABEL_LIMIT:
        truncations.append(f"kept first {LABEL_LIMIT} of {len(labels)} blocker/class labels")
    for index in chosen_labels:
        context, truncated = _context_indexes(lines, index)
        selected.update(context)
        if truncated:
            truncations.append(
                f"label at line {index + 1} kept {ENTRY_CONTEXT_LIMIT} context lines"
            )

    if not selected:
        truncations.append(
            "no unchecked entries or blocker/class labels matched the queue packet vocabulary"
        )
    indexes = sorted(selected)
    return SourceBlock(source, _referenced(source, lines, indexes), tuple(truncations))


def _skip_json_whitespace(text: str, cursor: int, end: int) -> int:
    while cursor < end and text[cursor].isspace():
        cursor += 1
    return cursor


def _json_object_members(
    text: str,
    start: int,
    end: int,
) -> list[tuple[str, int, int, int]]:
    if start >= end or text[start] != "{" or text[end - 1] != "}":
        raise PacketError("cannot locate structural JSON object boundaries")

    decoder = json.JSONDecoder()
    members: list[tuple[str, int, int, int]] = []
    cursor = start + 1
    while True:
        cursor = _skip_json_whitespace(text, cursor, end)
        if cursor == end - 1:
            return members
        if members:
            if text[cursor] != ",":
                raise PacketError("cannot locate structural JSON object boundaries")
            cursor = _skip_json_whitespace(text, cursor + 1, end)

        key_start = cursor
        key, key_end = decoder.raw_decode(text, cursor)
        if not isinstance(key, str):
            raise PacketError("cannot locate structural JSON object fields")
        cursor = _skip_json_whitespace(text, key_end, end)
        if cursor >= end or text[cursor] != ":":
            raise PacketError("cannot locate structural JSON object fields")
        value_start = _skip_json_whitespace(text, cursor + 1, end)
        _, value_end = decoder.raw_decode(text, value_start)
        if value_end > end - 1:
            raise PacketError("cannot locate structural JSON object fields")
        members.append((key, key_start, value_start, value_end))
        cursor = value_end


def _validated_backlog_items(
    path: Path,
    lines: Sequence[str],
) -> tuple[list[dict[str, object]], list[tuple[int, dict[str, object]]]]:
    try:
        data = json.loads("\n".join(lines))
    except json.JSONDecodeError as exc:
        raise PacketError(f"invalid JSON in {path}: {exc}") from exc
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise PacketError(f"{path} must contain an 'items' list")

    active: list[tuple[int, dict[str, object]]] = []
    validated: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for item_index, item in enumerate(items):
        if not isinstance(item, dict):
            raise PacketError(f"{path} contains a non-object backlog item")
        values = (item.get("id"), item.get("status"))
        for value in values:
            if not isinstance(value, str) or not value:
                raise PacketError(
                    f"{path} backlog items require non-empty string 'id' and 'status'"
                )
        item_id, status = (str(value) for value in values)
        if item_id in seen_ids:
            raise PacketError(f"{path} contains duplicate backlog id {item_id!r}")
        seen_ids.add(item_id)
        validated.append(item)
        if status not in _CLOSED_BACKLOG_STATUSES:
            active.append((item_index, item))
    return validated, active


def _backlog_item_spans(text: str, item_count: int, path: Path) -> list[tuple[int, int]]:
    decoder = json.JSONDecoder()
    root_start = _skip_json_whitespace(text, 0, len(text))
    _, root_end = decoder.raw_decode(text, root_start)
    items_members = [
        (value_start, value_end)
        for key, _, value_start, value_end in _json_object_members(text, root_start, root_end)
        if key == "items"
    ]
    if len(items_members) != 1:
        raise PacketError(f"cannot locate one structural 'items' list in {path}")
    items_start, items_end = items_members[0]
    if text[items_start] != "[" or text[items_end - 1] != "]":
        raise PacketError(f"cannot locate structural backlog item boundaries in {path}")

    spans: list[tuple[int, int]] = []
    cursor = items_start + 1
    for _ in range(item_count):
        cursor = _skip_json_whitespace(text, cursor, items_end)
        if spans:
            if text[cursor] != ",":
                raise PacketError(f"cannot locate structural backlog item boundaries in {path}")
            cursor = _skip_json_whitespace(text, cursor + 1, items_end)
        _, item_end = decoder.raw_decode(text, cursor)
        spans.append((cursor, item_end))
        cursor = item_end
    if _skip_json_whitespace(text, cursor, items_end) != items_end - 1:
        raise PacketError(f"cannot locate structural boundaries for every backlog item in {path}")
    return spans


def _active_backlog_line_indexes(
    text: str,
    spans: Sequence[tuple[int, int]],
    active: Sequence[tuple[int, dict[str, object]]],
) -> list[int]:
    selected: list[int] = []
    for item_index, item in active[:BACKLOG_ITEM_LIMIT]:
        item_id = str(item["id"])
        field_lines: dict[str, int] = {}
        for field, key_start, _, _ in _json_object_members(text, *spans[item_index]):
            if field not in _BACKLOG_FIELDS:
                continue
            if field in field_lines:
                raise PacketError(
                    f"cannot locate unambiguous line references for backlog id {item_id!r}: "
                    f"duplicate {field!r} field"
                )
            field_lines[field] = text.count("\n", 0, key_start)
        missing_fields = sorted(
            field for field in _BACKLOG_FIELDS if field in item and field not in field_lines
        )
        if missing_fields:
            raise PacketError(
                f"cannot locate line references for backlog id {item_id!r} fields: "
                f"{', '.join(missing_fields)}"
            )
        selected.extend(field_lines.values())
    return selected


def _backlog_state(path: Path, source: str) -> SourceBlock:
    lines = _read_lines(path)
    items, active = _validated_backlog_items(path, lines)
    text = "\n".join(lines)
    spans = _backlog_item_spans(text, len(items), path)
    selected = _active_backlog_line_indexes(text, spans, active)

    truncations: list[str] = []
    if not active:
        truncations.append("no non-closed backlog items matched the queue packet vocabulary")
    if len(active) > BACKLOG_ITEM_LIMIT:
        truncations.append(
            f"kept first {BACKLOG_ITEM_LIMIT} of {len(active)} non-closed status rows"
        )
    return SourceBlock(source, _referenced(source, lines, sorted(set(selected))), tuple(truncations))


def _papercuts(path: Path, source: str) -> SourceBlock:
    lines = _read_lines(path)
    starts = [
        (match.group(1), index) for index, line in enumerate(lines)
        if (match := _PAPERCUT_RE.match(line))
    ]
    starts.sort(reverse=True)
    selected: list[int] = []
    truncations: list[str] = []
    for _date, index in starts[:PAPERCUT_LIMIT]:
        context, truncated = _context_indexes(lines, index, _PAPERCUT_RE)
        selected.extend(context)
        if truncated:
            truncations.append(
                f"papercut at line {index + 1} kept {ENTRY_CONTEXT_LIMIT} context lines"
            )
    if not starts:
        truncations.append("no dated papercut entries matched the queue packet vocabulary")
    if len(starts) > PAPERCUT_LIMIT:
        truncations.append(f"kept newest {PAPERCUT_LIMIT} of {len(starts)} dated papercuts")
    return SourceBlock(source, _referenced(source, lines, selected), tuple(truncations))


def _validated_roots(roots: Sequence[Path]) -> tuple[Path, ...]:
    if not roots:
        raise PacketError("at least one repository or worktree root is required")
    resolved: list[Path] = []
    for root in roots:
        try:
            candidate = root.expanduser().resolve(strict=True)
        except OSError as exc:
            raise PacketError(f"invalid root {root}: {exc}") from exc
        if not candidate.is_dir():
            raise PacketError(f"root is not a directory: {candidate}")
        memory_bank = candidate / "memory-bank"
        if not memory_bank.is_dir():
            raise PacketError(f"root has no memory-bank directory: {candidate}")
        missing = [name for name in _REQUIRED_FILES if not (memory_bank / name).is_file()]
        if missing:
            raise PacketError(f"{candidate} is missing required Memory Bank files: {', '.join(missing)}")
        if candidate in resolved:
            raise PacketError(f"duplicate root: {candidate}")
        resolved.append(candidate)
    return tuple(resolved)


def _render(
    roots: Sequence[Path],
    blocks: Sequence[SourceBlock],
    reports: dict[str, list[str]],
    max_bytes: int,
) -> str:
    output = [
        "# Memory Bank queue packet",
        "",
        f"Byte cap: {max_bytes} UTF-8 bytes, including this report.",
        "",
        "## Operator search guidance",
        (
            "- Discover filenames with `python3 tools/repo_search.py PATTERN ROOT --names` "
            "or `rg --files ROOT` before targeted reads, and search contents with the same "
            "tool instead of raw grep or shell globs; its --help covers generated catalogs."
        ),
        "",
        "Roots:",
    ]
    output.extend(f"- root[{index}]: {root}" for index, root in enumerate(roots, 1))
    for block in blocks:
        output.extend(("", f"## {block.source}", *block.lines))
    output.extend(("", "## Omissions and truncations"))
    if reports:
        for source in sorted(reports):
            output.append(f"- {source} — {'; '.join(reports[source])}")
    else:
        output.append("- none")
    return "\n".join(output) + "\n"


def build_packet(roots: Sequence[Path], *, max_bytes: int = DEFAULT_MAX_BYTES) -> str:
    """Return a deterministic packet whose UTF-8 size does not exceed max_bytes."""
    if max_bytes < MIN_MAX_BYTES:
        raise PacketError(f"max_bytes must be at least {MIN_MAX_BYTES}")
    validated = _validated_roots(roots)

    blocks: list[SourceBlock] = []
    for root_number, root in enumerate(validated, 1):
        memory_bank = root / "memory-bank"
        blocks.append(_top_sections(
            memory_bank / "activeContext.md",
            _source_name(root_number, "activeContext.md"),
        ))
        blocks.append(_top_sections(
            memory_bank / "progress.md",
            _source_name(root_number, "progress.md"),
        ))
        blocks.append(_queue_state(
            memory_bank / "future-work-kanban.md",
            _source_name(root_number, "future-work-kanban.md"),
        ))
        blocks.append(_backlog_state(
            memory_bank / "gap-backlog.json",
            _source_name(root_number, "gap-backlog.json"),
        ))
        for path in sorted(memory_bank.glob("*-queue.md"), key=lambda candidate: candidate.name):
            blocks.append(_queue_state(path, _source_name(root_number, path.name)))
        blocks.append(_papercuts(
            memory_bank / "papercuts.md",
            _source_name(root_number, "papercuts.md"),
        ))

    included = [block for block in blocks if block.lines]
    omitted_by_cap: set[str] = set()
    while True:
        reports = {
            block.source: list(block.truncations)
            for block in blocks
            if block.truncations and block.source not in omitted_by_cap
        }
        for source in omitted_by_cap:
            reports[source] = [f"omitted because the {max_bytes}-byte cap was reached"]
        packet = _render(validated, included, reports, max_bytes)
        if len(packet.encode("utf-8")) <= max_bytes:
            return packet
        if not included:
            required = len(packet.encode("utf-8"))
            raise PacketError(
                f"max_bytes={max_bytes} cannot fit the packet header and omission report "
                f"({required} bytes required)"
            )
        removed = included.pop()
        omitted_by_cap.add(removed.source)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="+",
        type=Path,
        help="repository or guarded-worktree roots containing memory-bank/",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=DEFAULT_MAX_BYTES,
        help=f"maximum UTF-8 packet size (default: {DEFAULT_MAX_BYTES}; minimum: {MIN_MAX_BYTES})",
    )
    args = parser.parse_args(argv)
    try:
        packet = build_packet(args.roots, max_bytes=args.max_bytes)
    except PacketError as exc:
        parser.exit(2, f"error: {exc}\n")
    print(packet, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
