#!/usr/bin/env python3
"""Audit tracked Markdown and HTML documentation for mechanical defects."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote


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
    return tuple(path for path in paths if path.exists())


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


def _audit_active_context(path: Path, root: Path, text: str, issues: list[DocIssue]) -> None:
    """Dated entries belong to progress.md; activeContext.md keeps only the head."""
    for line_number, line in enumerate(text.splitlines(), 1):
        if DATED_HEADING_RE.match(line) and not line.startswith("## Current focus"):
            issues.append(DocIssue("dated_entry_in_active_context", _relative(path, root), line_number, line))


PAPERCUTS = Path("memory-bank") / "papercuts.md"


def _audit_papercuts(path: Path, root: Path, text: str, issues: list[DocIssue]) -> None:
    """Every papercut is one `- ` line, so moves and no-loss checks compare lines exactly."""
    for line_number, line in enumerate(text.splitlines(), 1):
        if line and not line.startswith(("#", "- ")):
            issues.append(DocIssue("papercut_without_bullet", _relative(path, root), line_number, line))


def audit_docs(root: Path) -> DocAuditReport:
    issues: list[DocIssue] = []
    markdown_files = 0
    html_files = 0
    test_selectors = _defined_test_selectors(root)
    for path in _tracked_docs(root):
        text = _read_text(path, root, issues)
        if text is None:
            continue
        if path.suffix == ".md":
            markdown_files += 1
            _audit_markdown(path, root, text, issues)
            _audit_test_selectors(path, root, text, test_selectors, issues)
            if path.resolve() == (root / ACTIVE_CONTEXT).resolve():
                _audit_active_context(path, root, text, issues)
            if path.resolve() == (root / PAPERCUTS).resolve():
                _audit_papercuts(path, root, text, issues)
        else:
            html_files += 1
            _audit_html(path, root, text, issues)
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
