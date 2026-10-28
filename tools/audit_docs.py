#!/usr/bin/env python3
"""Audit tracked Markdown and HTML documentation for mechanical defects."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


MARKDOWN_LINK_RE = re.compile(r"(?<![\w])!?\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+['\"][^'\"]*['\"])?\)")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
QUALIFIED_TEST_SELECTOR_RE = re.compile(
    r"(?<![\w.])(tests(?:\.[A-Za-z_]\w*)+\.test_[A-Za-z_]\w*)(?![\w.])"
)


@dataclass(frozen=True)
class DocIssue:
    kind: str
    path: str
    line: int
    detail: str


@dataclass(frozen=True)
class DocAuditReport:
    markdown_files: int
    html_files: int
    issues: tuple[DocIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


VOID_ELEMENTS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
})
OPTIONAL_END_ELEMENTS = frozenset({
    "dd", "dt", "li", "optgroup", "option", "p", "rp", "rt", "tbody",
    "td", "tfoot", "th", "thead", "tr",
})


class _DocumentParser(HTMLParser):
    """Check lexical validity and explicit non-optional element nesting."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, int]] = []
        self.errors: list[tuple[int, str]] = []
        self.local_targets: list[tuple[int, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name.lower() in {"href", "src"} and value:
                self.local_targets.append((self.getpos()[0], value))
        tag = tag.lower()
        if tag not in VOID_ELEMENTS:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        for name, value in attrs:
            if name.lower() in {"href", "src"} and value:
                self.local_targets.append((self.getpos()[0], value))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in VOID_ELEMENTS:
            return
        while self.stack and self.stack[-1][0] in OPTIONAL_END_ELEMENTS and self.stack[-1][0] != tag:
            self.stack.pop()
        if not self.stack:
            if tag not in OPTIONAL_END_ELEMENTS:
                self.errors.append((self.getpos()[0], f"unexpected closing </{tag}>"))
            return
        expected, _ = self.stack[-1]
        if expected != tag:
            self.errors.append((self.getpos()[0], f"closing </{tag}> does not match open <{expected}>"))
            return
        self.stack.pop()


def _tracked_docs(root: Path) -> tuple[Path, ...]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.md", "*.html"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    paths = (root / item.decode() for item in result.stdout.split(b"\0") if item)
    # The publisher owns status-page checks; their ignored videos are absent from Git snapshots.
    status_artifacts = root / "memory-bank" / "status-updates"
    return tuple(
        path for path in paths if path.exists()
        and not (path.suffix == ".html" and path.is_relative_to(status_artifacts))
    )


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _read_text(path: Path, root: Path, issues: list[DocIssue]) -> str | None:
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        issues.append(DocIssue("invalid_utf8", _relative(path, root), 1, str(exc)))
        return None
    if raw and not raw.endswith(b"\n"):
        issues.append(DocIssue("missing_final_newline", _relative(path, root), text.count("\n") + 1, "file must end with a newline"))
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip() and line:
            issues.append(DocIssue("whitespace_only_line", _relative(path, root), line_number, "blank line contains whitespace"))
        if path.suffix == ".html" and line.rstrip(" \t") != line:
            issues.append(DocIssue("trailing_whitespace", _relative(path, root), line_number, "HTML line has trailing whitespace"))
    return text


def _defined_test_selectors(root: Path) -> frozenset[str]:
    selectors: set[str] = set()
    tests_root = root / "tests"
    if not tests_root.exists():
        return frozenset()
    for path in tests_root.rglob("test*.py"):
        module = ".".join(path.relative_to(root).with_suffix("").parts)
        selectors.add(module)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                selectors.add(f"{module}.{node.name}")
            elif isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test"):
                        selectors.add(f"{module}.{node.name}.{child.name}")
    return frozenset(selectors)


def _audit_test_selectors(
    path: Path, root: Path, text: str, selectors: frozenset[str], issues: list[DocIssue]
) -> None:
    if path.relative_to(root).parts[:2] != ("memory-bank", "source-audits"):
        return
    for line_number, line in enumerate(text.splitlines(), 1):
        for match in QUALIFIED_TEST_SELECTOR_RE.finditer(line):
            selector = match.group(1)
            if selector not in selectors:
                issues.append(DocIssue("dangling_test_selector", _relative(path, root), line_number, selector))


def _audit_markdown(path: Path, root: Path, text: str, issues: list[DocIssue]) -> None:
    fence: str | None = None
    visible_lines: list[str] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        match = FENCE_RE.match(line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            visible_lines.append("")
            continue
        visible_lines.append("") if fence else visible_lines.append(line)
    if fence is not None:
        issues.append(DocIssue("unclosed_fence", _relative(path, root), len(visible_lines), f"unclosed {fence[0]} fence"))

    for line_number, line in enumerate(visible_lines, 1):
        for match in MARKDOWN_LINK_RE.finditer(line):
            target = match.group(1).strip("<>")
            if not target or target.startswith(
                ("#", "http://", "https://", "mailto:", "data:", "help:", "/")
            ):
                continue
            target_path = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not target_path:
                continue
            resolved = (path.parent / target_path).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                continue
            if not resolved.exists():
                issues.append(DocIssue("broken_local_link", _relative(path, root), line_number, target))


def _audit_html(path: Path, root: Path, text: str, issues: list[DocIssue]) -> None:
    if not text.lstrip().lower().startswith("<!doctype html>"):
        issues.append(DocIssue("missing_doctype", _relative(path, root), 1, "standalone HTML must declare <!doctype html>"))
    parser = _DocumentParser()
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:  # HTMLParser reports malformed declarations as exceptions.
        line, _ = parser.getpos()
        issues.append(DocIssue("invalid_html", _relative(path, root), line, str(exc)))
        return
    for line, detail in parser.errors:
        issues.append(DocIssue("invalid_html_nesting", _relative(path, root), line, detail))
    for tag, line in parser.stack:
        if tag not in OPTIONAL_END_ELEMENTS:
            issues.append(DocIssue("unclosed_html_element", _relative(path, root), line, f"unclosed <{tag}>"))
    for line, target in parser.local_targets:
        if target.startswith(("#", "http://", "https://", "mailto:", "data:", "javascript:", "/")):
            continue
        target_path = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not target_path:
            continue
        resolved = (path.parent / target_path).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        if not resolved.exists():
            issues.append(DocIssue("broken_html_target", _relative(path, root), line, target))


ACTIVE_CONTEXT = Path("memory-bank") / "activeContext.md"
DATED_HEADING_RE = re.compile(r"^## .*\d{4}-\d{2}-\d{2}")
STARTUP_LINE_BUDGET = 3000
STARTUP_FILES = tuple(f"memory-bank/{name}.md" for name in (
    "activeContext", "progress", "future-work-kanban",
    "goal-priority-matrix", "loop-queue",
))
PAPERCUTS = Path("memory-bank") / "papercuts.md"
# Papercuts grow by one line per incident; a cap of their own keeps them from
# competing with progress for the shared startup budget (owner, 2026-10-27).
PAPERCUTS_LINE_CAP = 800


def _line_count(path: Path) -> int:
    return path.read_bytes().count(b"\n") if path.exists() else 0


def _audit_startup_budget(root: Path, issues: list[DocIssue]) -> None:
    counts = {relative: _line_count(root / relative) for relative in STARTUP_FILES}
    total = sum(counts.values())
    if total >= STARTUP_LINE_BUDGET:
        detail = f"{total} startup lines must stay under {STARTUP_LINE_BUDGET}: "
        detail += ", ".join(f"{path}={count}" for path, count in counts.items())
        issues.append(DocIssue("startup_line_budget_exceeded", ACTIVE_CONTEXT.as_posix(), 1, detail))
    papercuts = _line_count(root / PAPERCUTS)
    if papercuts >= PAPERCUTS_LINE_CAP:
        detail = f"{papercuts} papercut lines must stay under {PAPERCUTS_LINE_CAP}"
        issues.append(DocIssue("papercuts_line_cap_exceeded", PAPERCUTS.as_posix(), 1, detail))


def _audit_active_context(path: Path, root: Path, text: str, issues: list[DocIssue]) -> None:
    """Dated entries belong to progress.md; activeContext.md keeps only the head."""
    for line_number, line in enumerate(text.splitlines(), 1):
        if DATED_HEADING_RE.match(line) and not line.startswith("## Current focus"):
            issues.append(DocIssue("dated_entry_in_active_context", _relative(path, root), line_number, line))


def _audit_papercuts(path: Path, root: Path, text: str, issues: list[DocIssue]) -> None:
    """Every papercut is one `- ` line, so moves and no-loss checks compare lines exactly."""
    for line_number, line in enumerate(text.splitlines(), 1):
        if line and not line.startswith(("#", "> ", "- ")):
            issues.append(DocIssue("papercut_without_bullet", _relative(path, root), line_number, line))


PROGRESS_LOG_RE = re.compile(r"memory-bank/(?:progress|archive/progress-[\w-]+)\.md")
SECTION_HEADING_RE = re.compile(r"^## .*$", re.M)


def _audit_repeated_sections(path: Path, root: Path, text: str, issues: list[DocIssue]) -> None:
    """A monthly rotation that copies a block twice leaves `## ` sections repeated word for word."""
    headings = list(SECTION_HEADING_RE.finditer(text))
    first_line: dict[str, int] = {}
    for heading, following in zip(headings, [*headings[1:], None]):
        section = text[heading.start():following.start() if following else len(text)].strip()
        line = text.count("\n", 0, heading.start()) + 1
        if section in first_line:
            detail = f"{heading.group()} repeats line {first_line[section]}"
            issues.append(DocIssue("repeated_progress_section", _relative(path, root), line, detail))
        first_line.setdefault(section, line)


def _capture_has_symlink(path: Path, root: Path) -> bool:
    return any(parent.is_symlink() for parent in (path, *path.parents) if parent != root
               and parent.is_relative_to(root))


def _valid_capture_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        parsed.port  # Validate a supplied port as well as the host.
        return (parsed.scheme in {"http", "https"} and bool(parsed.hostname)
                and not any(char.isspace() for char in value))
    except ValueError:
        return False


def _valid_capture_provenance(record: dict) -> bool:
    values = [record[key] for key in ("url", "path") if key in record]
    for value in values:
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            return False
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            return False
    return bool(values) and ("url" not in record or _valid_capture_url(record["url"]))


def _valid_capture_record(record: dict) -> bool:
    local = record.get("local")
    if not isinstance(local, str) or "\\" in local or "\x00" in local:
        return False
    parts = PurePosixPath(local).parts
    if (len(parts) < 2 or parts[0] != "sources" or ".." in parts
            or PurePosixPath(local).as_posix() != local):
        return False
    digest = record.get("sha256")
    size = record.get("saved_bytes")
    return (isinstance(digest, str) and re.fullmatch(r"[0-9a-fA-F]{64}", digest) is not None
            and type(size) is int and size >= 0 and _valid_capture_provenance(record))


def _capture_records(index: Path, root: Path, issues: list[DocIssue]) -> list[dict]:
    if _capture_has_symlink(index, root):
        issues.append(DocIssue("capture_symlink", _relative(index, root), 1,
                               "source index path must not contain symlinks"))
        return []
    try:
        records = json.loads(index.read_bytes())
        if not isinstance(records, list) or not all(isinstance(row, dict) for row in records):
            raise ValueError("source index must be a list of records")
    except (OSError, ValueError) as exc:
        issues.append(DocIssue("invalid_capture_index", _relative(index, root), 1, str(exc)))
        return []
    return records


def _capture_bytes_match(path: Path, record: dict, root: Path, issues: list[DocIssue]) -> bool:
    relative = _relative(path, root)
    if _capture_has_symlink(path, root):
        issues.append(DocIssue("capture_symlink", relative, 1,
                               "capture path must not contain symlinks"))
        return False
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        issues.append(DocIssue("missing_capture", relative, 1, "indexed capture is missing"))
        return False
    except OSError as exc:
        issues.append(DocIssue("unreadable_capture", relative, 1, str(exc)))
        return False
    matches = True
    if len(raw) != record["saved_bytes"]:
        issues.append(DocIssue("capture_size_mismatch", relative, 1,
                               f"expected {record['saved_bytes']} bytes, found {len(raw)}"))
        matches = False
    if hashlib.sha256(raw).hexdigest() != record["sha256"].lower():
        issues.append(DocIssue("capture_hash_mismatch", relative, 1,
                               "saved bytes do not match indexed sha256"))
        matches = False
    return matches


def _register_capture(
    index: Path, root: Path, record: dict, number: int,
    identities: dict[tuple[str, str], dict], issues: list[DocIssue],
) -> bool:
    if not _valid_capture_record(record):
        issues.append(DocIssue("invalid_capture_record", _relative(index, root), 1,
                               f"record {number}: canonical sources/ path, sha256, "
                               "saved_bytes and url or path provenance required"))
        return False
    keys = [("local", record["local"])]
    if "id" in record:
        if not isinstance(record["id"], str) or not record["id"].strip():
            issues.append(DocIssue("invalid_capture_record", _relative(index, root), 1,
                                   f"record {number}: id must be a nonempty string"))
            return False
        keys.append(("id", record["id"]))
    identity = dict(record, sha256=record["sha256"].lower())
    if any(key in identities and identities[key] != identity for key in keys):
        issues.append(DocIssue("conflicting_capture_identity", _relative(index, root), 1,
                               f"record {number}: conflicting local path or id"))
        return False
    for key in keys:
        identities[key] = identity
    return True


def _indexed_captures(root: Path, issues: list[DocIssue]) -> set[Path]:
    captures: set[Path] = set()
    for index in sorted((root / "data/quest/evidence").glob("*/source-index.json")):
        identities: dict[tuple[str, str], dict] = {}
        for number, record in enumerate(_capture_records(index, root, issues), 1):
            if not _register_capture(index, root, record, number, identities, issues):
                continue
            path = index.parent / record["local"]
            if _capture_bytes_match(path, record, root, issues):
                captures.add(path)
    return captures


def _audit_markdown_document(
    path: Path, root: Path, text: str, selectors: frozenset[str], issues: list[DocIssue]
) -> None:
    _audit_markdown(path, root, text, issues)
    _audit_test_selectors(path, root, text, selectors, issues)
    if path.resolve() == (root / ACTIVE_CONTEXT).resolve():
        _audit_active_context(path, root, text, issues)
    if path.resolve() == (root / PAPERCUTS).resolve():
        _audit_papercuts(path, root, text, issues)
    if PROGRESS_LOG_RE.fullmatch(_relative(path, root)):
        _audit_repeated_sections(path, root, text, issues)


def audit_docs(root: Path) -> DocAuditReport:
    issues: list[DocIssue] = []
    markdown_files = 0
    html_files = 0
    test_selectors = _defined_test_selectors(root)
    captures = _indexed_captures(root, issues)
    for path in _tracked_docs(root):
        if path in captures:
            continue
        text = _read_text(path, root, issues)
        if text is None:
            continue
        if path.suffix == ".md":
            markdown_files += 1
            _audit_markdown_document(path, root, text, test_selectors, issues)
        else:
            html_files += 1
            _audit_html(path, root, text, issues)
    _audit_startup_budget(root, issues)
    return DocAuditReport(markdown_files, html_files, tuple(issues))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit_docs(args.root.resolve())
    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"Audited {report.markdown_files} Markdown and {report.html_files} HTML files.")
        for issue in report.issues:
            print(f"{issue.path}:{issue.line}: {issue.kind}: {issue.detail}")
        print("Documentation audit passed." if report.ok else f"Documentation audit found {len(report.issues)} issue(s).")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
