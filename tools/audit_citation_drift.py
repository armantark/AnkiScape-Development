#!/usr/bin/env python3
"""Find Memory Bank line citations whose targets have moved or changed."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^#{1,6}\s")
INLINE_CODE_RE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
INLINE_CITATION_RE = re.compile(
    r"(?<![\w./-])"
    r"(?P<path>/(?:[^`:\n]+/)*[^`/:\n]+\.[A-Za-z0-9]+|"
    r"(?:[A-Za-z0-9_@.+-]+/)*[A-Za-z0-9_@.+-]+\.[A-Za-z][A-Za-z0-9]*)"
    r":(?P<start>\d+)(?:-(?P<end>\d+))?"
)
BARE_CITATION_RE = re.compile(
    r"(?<![\w./:-])"
    r"(?P<path>/?(?:[A-Za-z0-9_@.+-]+/)*[A-Za-z0-9_@.+-]+\.[A-Za-z][A-Za-z0-9]*)"
    r":(?P<start>\d+)(?:-(?P<end>\d+))?"
)
CONTINUATION_RE = re.compile(r"\s*,\s*(?P<start>\d+)(?:-(?P<end>\d+))?")
SHA_RE = re.compile(r"(?<![0-9a-f])(?=[0-9a-f]{7,40}(?![0-9a-f]))(?=[0-9a-f]*[a-f])([0-9a-f]{7,40})", re.I)
BLAME_HEADER_RE = re.compile(r"^([0-9a-f]{40}) \d+ \d+(?: \d+)?$")
STALE_STATUSES = frozenset({"changed", "missing_file", "missing_lines", "moved"})
_PATH_INDEXES: dict[int, tuple[set[str], dict[str, tuple[str, ...]]]] = {}


@dataclass(frozen=True)
class Citation:
    record_path: str
    record_line: int
    target_path: str
    start_line: int
    end_line: int
    target: str
    origin_commit: str | None
    commit_candidates: tuple[str, ...]
    context: str


@dataclass(frozen=True)
class CitationResult:
    record_path: str
    record_line: int
    target: str
    status: str
    source: str | None
    origin_commit: str | None
    origin_target: str | None
    origin_text: tuple[str, ...]
    cited_target: str | None
    cited_text: tuple[str, ...]
    real_target: str | None
    real_text: tuple[str, ...]
    detail: str

    @property
    def stale(self) -> bool:
        return self.status in STALE_STATUSES

    @property
    def resolved(self) -> bool:
        return self.status not in {"ambiguous", "unresolved"}


@dataclass(frozen=True)
class CitationAuditReport:
    markdown_files: int
    citations: int
    resolved: int
    repository_local: int
    pinned_external: int
    unpinned_external: int
    stale: int
    unresolved: int
    results: tuple[CitationResult, ...]

    @property
    def ok(self) -> bool:
        return self.stale == 0 and self.unresolved == 0


@dataclass(frozen=True)
class ExternalRepository:
    name: str
    path: Path


class GitRepository:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self._trees: dict[str, tuple[str, ...]] = {}
        self._files: dict[tuple[str, str], tuple[str, ...] | None] = {}
        self._commits: dict[str, str | None] = {}

    def _run(self, *args: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            ["git", "-C", str(self.root), *args],
            check=False,
            capture_output=True,
        )

    def resolve_commit(self, commit: str) -> str | None:
        if commit not in self._commits:
            result = self._run("rev-parse", "--verify", f"{commit}^{{commit}}")
            self._commits[commit] = result.stdout.decode().strip() if result.returncode == 0 else None
        return self._commits[commit]

    def tree_paths(self, commit: str) -> tuple[str, ...]:
        resolved = self.resolve_commit(commit)
        if resolved is None:
            return ()
        if resolved not in self._trees:
            result = self._run("ls-tree", "-r", "--name-only", "-z", resolved)
            self._trees[resolved] = tuple(
                item.decode("utf-8", errors="replace")
                for item in result.stdout.split(b"\0")
                if item
            ) if result.returncode == 0 else ()
        return self._trees[resolved]

    def file_lines(self, commit: str, path: str) -> tuple[str, ...] | None:
        resolved = self.resolve_commit(commit)
        if resolved is None:
            return None
        key = (resolved, path)
        if key not in self._files:
            result = self._run("show", f"{resolved}:{path}")
            self._files[key] = (
                tuple(result.stdout.decode("utf-8", errors="replace").splitlines())
                if result.returncode == 0
                else None
            )
        return self._files[key]

    def blame_commits(self, path: str, line_count: int) -> tuple[str | None, ...]:
        result = self._run("blame", "--line-porcelain", "HEAD", "--", path)
        if result.returncode != 0:
            return (None,) * line_count
        commits: list[str | None] = []
        current: str | None = None
        for raw_line in result.stdout.decode("utf-8", errors="replace").splitlines():
            match = BLAME_HEADER_RE.match(raw_line)
            if match:
                current = None if set(match.group(1)) == {"0"} else match.group(1)
            elif raw_line.startswith("\t"):
                commits.append(current)
        if len(commits) < line_count:
            commits.extend([None] * (line_count - len(commits)))
        return tuple(commits[:line_count])


class WorkingTree:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        result = subprocess.run(
            ["git", "-C", str(self.root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            check=True,
            capture_output=True,
        )
        self.paths = tuple(
            item.decode("utf-8", errors="replace")
            for item in result.stdout.split(b"\0")
            if item and (self.root / item.decode("utf-8", errors="replace")).is_file()
        )
        self.top_levels = frozenset(Path(path).parts[0] for path in self.paths if Path(path).parts)
        self._lines: dict[str, tuple[str, ...] | None] = {}

    def file_lines(self, path: str) -> tuple[str, ...] | None:
        if path not in self._lines:
            try:
                self._lines[path] = tuple((self.root / path).read_text(encoding="utf-8").splitlines())
            except (OSError, UnicodeDecodeError):
                self._lines[path] = None
        return self._lines[path]


class FilesystemTree:
    def __init__(self, name: str, root: Path) -> None:
        self.name = name
        self.root = root.resolve()
        self._paths: tuple[str, ...] | None = None
        self._lines: dict[str, tuple[str, ...] | None] = {}

    @property
    def paths(self) -> tuple[str, ...]:
        if self._paths is None:
            self._paths = tuple(
                path.relative_to(self.root).as_posix()
                for path in self.root.rglob("*")
                if path.is_file() and ".git" not in path.parts
            )
        return self._paths

    def file_lines(self, path: str) -> tuple[str, ...] | None:
        if path not in self._lines:
            try:
                self._lines[path] = tuple((self.root / path).read_text(encoding="utf-8").splitlines())
            except (OSError, UnicodeDecodeError):
                self._lines[path] = None
        return self._lines[path]


def _tracked_markdown(root: Path, memory_bank: Path) -> tuple[Path, ...]:
    result = subprocess.run(
        [
            "git", "-C", str(root), "ls-files", "-z", "--cached", "--others",
            "--exclude-standard", "--", memory_bank.relative_to(root).as_posix(),
        ],
        check=True,
        capture_output=True,
    )
    return tuple(
        root / item.decode("utf-8", errors="replace")
        for item in result.stdout.split(b"\0")
        if item and item.decode("utf-8", errors="replace").endswith(".md")
        and (root / item.decode("utf-8", errors="replace")).is_file()
    )


def _line_citations(text: str, regex: re.Pattern[str]) -> Iterable[tuple[str, int, int]]:
    for match in regex.finditer(text):
        path = match.group("path").strip()
        start = int(match.group("start"))
        end = int(match.group("end") or start)
        if "..." in Path(path).parts:
            continue
        yield path, start, end
        cursor = match.end()
        while continuation := CONTINUATION_RE.match(text, cursor):
            continuation_start = int(continuation.group("start"))
            continuation_end = int(continuation.group("end") or continuation_start)
            yield path, continuation_start, continuation_end
            cursor = continuation.end()


def _commit_candidates(lines: Sequence[str], line_index: int) -> tuple[str, ...]:
    candidates: list[str] = []
    for index in range(line_index, max(-1, line_index - 120), -1):
        for commit in reversed(SHA_RE.findall(lines[index])):
            if commit not in candidates:
                candidates.append(commit)
    return tuple(candidates)


def _source_context(lines: Sequence[str], line_index: int) -> str:
    start = line_index
    while start > 0 and not HEADING_RE.match(lines[start]):
        start -= 1
    current = lines[line_index].lower()
    section = "\n".join(lines[start:line_index]).lower()
    return f"{current}\n{section}"


def _parse_citations(root: Path, memory_bank: Path, git: GitRepository) -> tuple[int, tuple[Citation, ...]]:
    citations: list[Citation] = []
    markdown_paths = _tracked_markdown(root, memory_bank)
    for path in markdown_paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        pending: list[tuple[int, str, int, int, str, tuple[str, ...], str]] = []
        fence: str | None = None
        for line_index, line in enumerate(lines):
            fence_match = FENCE_RE.match(line)
            if fence_match:
                marker = fence_match.group(1)
                if fence is None:
                    fence = marker
                elif marker[0] == fence[0] and len(marker) >= len(fence):
                    fence = None
                continue
            if fence:
                continue
            spans = tuple(INLINE_CODE_RE.finditer(line))
            found: set[tuple[str, int, int]] = set()
            for span in spans:
                for candidate in _line_citations(span.group(1), INLINE_CITATION_RE):
                    found.add(candidate)
            bare_line = list(line)
            for span in spans:
                bare_line[span.start():span.end()] = " " * (span.end() - span.start())
            for candidate in _line_citations("".join(bare_line), BARE_CITATION_RE):
                found.add(candidate)
            if not found:
                continue
            commits = _commit_candidates(lines, line_index)
            context = f"{_source_context(lines, line_index)}\nrecord:{path.name.lower()}"
            for target_path, start_line, end_line in sorted(found):
                target = f"{target_path}:{start_line}" + (f"-{end_line}" if end_line != start_line else "")
                pending.append((line_index, target_path, start_line, end_line, target, commits, context))
        if not pending:
            continue
        record_path = path.relative_to(root).as_posix()
        blame = git.blame_commits(record_path, len(lines))
        for line_index, target_path, start_line, end_line, target, commits, context in pending:
            citations.append(Citation(
                record_path=record_path,
                record_line=line_index + 1,
                target_path=target_path,
                start_line=start_line,
                end_line=end_line,
                target=target,
                origin_commit=blame[line_index] if line_index < len(blame) else None,
                commit_candidates=commits,
                context=context,
            ))
    return len(markdown_paths), tuple(citations)

def _repo_relative_path(path: str, root: Path) -> str | None:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        return path.lstrip("./")
    try:
        return candidate.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        pass
    parts = candidate.parts
    if "ankiscape_fork" in parts:
        index = parts.index("ankiscape_fork")
        return Path(*parts[index + 1:]).as_posix()
    if "ankiscape_worktrees" in parts:
        index = parts.index("ankiscape_worktrees")
        if len(parts) > index + 2:
            return Path(*parts[index + 2:]).as_posix()
    return None


def _path_index(paths: Sequence[str]) -> tuple[set[str], dict[str, tuple[str, ...]]]:
    key = id(paths)
    if key not in _PATH_INDEXES:
        by_name: dict[str, list[str]] = {}
        for path in paths:
            by_name.setdefault(Path(path).name, []).append(path)
        _PATH_INDEXES[key] = (set(paths), {name: tuple(values) for name, values in by_name.items()})
    return _PATH_INDEXES[key]


def _matching_paths(paths: Sequence[str], citation_path: str, root: Path, *, memory_bank: bool) -> tuple[str, ...]:
    relative = _repo_relative_path(citation_path, root)
    if relative is None:
        return ()
    relatives = [relative]
    if memory_bank and relative.startswith("AS/ankiscape/"):
        as_path = relative.removeprefix("AS/ankiscape/")
        relatives.extend((as_path, Path(as_path).name))
    path_set, by_name = _path_index(paths)
    candidates: list[str] = []
    for item in relatives:
        for candidate in (item, f"memory-bank/{item}" if memory_bank and not item.startswith("memory-bank/") else None):
            if candidate and candidate in path_set and candidate not in candidates:
                candidates.append(candidate)
    if candidates:
        return tuple(candidates)
    matches: list[str] = []
    for item in relatives:
        suffix = item.lstrip("/")
        for candidate in by_name.get(Path(suffix).name, ()):
            if (candidate == suffix or candidate.endswith(f"/{suffix}")) and candidate not in matches:
                matches.append(candidate)
    return tuple(matches)


def _external_matching_paths(
    paths: Sequence[str], citation_path: str, root: Path, source_name: str
) -> tuple[str, ...]:
    matches = _matching_paths(paths, citation_path, root, memory_bank=False)
    if matches:
        return matches
    relative = citation_path.lstrip("./")
    if source_name.startswith("darkan"):
        parts = relative.split("/")
        if parts[-1].startswith("D-"):
            parts[-1] = parts[-1][2:]
            matches = _matching_paths(paths, "/".join(parts), root, memory_bank=False)
            if matches:
                return matches
    aliases = (
        source_name,
        "game-main" if source_name == "game-main" else "",
        "GM" if source_name == "game-main" else "",
        "DK" if source_name.startswith("darkan") else "",
    )
    for alias in aliases:
        prefix = f"{alias}/"
        if alias and relative.startswith(prefix):
            matches = _matching_paths(paths, relative[len(prefix):], root, memory_bank=False)
            if matches:
                return matches
    return ()


def _preferred_external_sources(context: str) -> tuple[str, ...]:
    def labels(text: str) -> tuple[str, ...]:
        preferred: list[str] = []
        if "darkan-client" in text or "darkan client" in text:
            preferred.append("darkan-client")
        if "darkan-cache" in text or "darkan cache" in text:
            preferred.append("darkan-cache")
        if "darkan" in text or "[dk" in text:
            for source in ("darkan-world-server", "darkan-client", "darkan-cache"):
                if source not in preferred:
                    preferred.append(source)
        if "game-main" in text or "2011scape" in text or "[gm" in text:
            preferred.append("game-main")
        return tuple(preferred)

    current_line = context.split("\n", 1)[0]
    return labels(current_line) or labels(context)


def _best_basename_match(paths: Sequence[str], citation_path: str, context: str) -> str | None:
    name = Path(citation_path).name
    if name.startswith("D-"):
        name = name[2:]
    _, by_name = _path_index(paths)
    matches = by_name.get(name, ())
    if len(matches) == 1:
        return matches[0]
    if not matches:
        return None
    context_tokens = set(re.findall(r"[a-z0-9]+", context.lower()))
    ignored = {"src", "main", "java", "kotlin", "game", "content"}
    scores = []
    for match in matches:
        path_tokens = set(re.findall(r"[a-z0-9]+", match.lower())) - ignored
        scores.append((len(path_tokens & context_tokens), match))
    best = max(score for score, _ in scores)
    winners = [match for score, match in scores if score == best]
    return winners[0] if best > 0 and len(winners) == 1 else None


def _slice(lines: tuple[str, ...] | None, start: int, end: int) -> tuple[str, ...] | None:
    if lines is None or start < 1 or end < start or end > len(lines):
        return None
    return lines[start - 1:end]


def _target(path: str, start: int, end: int) -> str:
    return f"{path}:{start}" + (f"-{end}" if end != start else "")


def _find_block(
    paths: Sequence[str],
    line_reader,
    block: tuple[str, ...],
    preferred_path: str,
) -> tuple[tuple[str, int, int], ...]:
    if not block:
        return ()
    _, by_name = _path_index(paths)
    ordered = by_name.get(Path(preferred_path).name, ())
    matches: list[tuple[str, int, int]] = []
    width = len(block)
    for path in ordered:
        lines = line_reader(path)
        if lines is None or len(lines) < width:
            continue
        for index in range(len(lines) - width + 1):
            if lines[index:index + width] == block:
                matches.append((path, index + 1, index + width))
                if len(matches) > 8:
                    return tuple(matches)
    return tuple(matches)


def _resolve_local(
    citation: Citation,
    root: Path,
    git: GitRepository,
    working: WorkingTree,
) -> CitationResult | None:
    origin_lines: tuple[str, ...] | None = None
    origin_block: tuple[str, ...] | None = None
    origin_path: str | None = None
    if citation.origin_commit:
        tree_paths = git.tree_paths(citation.origin_commit)
        origin_paths = _matching_paths(tree_paths, citation.target_path, root, memory_bank=True)
        if len(origin_paths) == 1:
            origin_path = origin_paths[0]
            origin_lines = git.file_lines(citation.origin_commit, origin_path)
            origin_block = _slice(origin_lines, citation.start_line, citation.end_line)

    current_paths = _matching_paths(working.paths, citation.target_path, root, memory_bank=True)
    if origin_path and origin_path in working.paths:
        current_paths = (origin_path,)
    if origin_path is None and len(current_paths) != 1:
        relative = _repo_relative_path(citation.target_path, root)
        first = Path(relative).parts[0] if relative and Path(relative).parts else ""
        looks_local = bool(
            relative
            and (
                first in working.top_levels
                or relative.startswith(("source-audits/", "handoffs/"))
                or Path(relative).suffix == ".md"
            )
        )
        if not looks_local:
            return None
        return CitationResult(
            citation.record_path, citation.record_line, citation.target, "missing_file",
            "repository", citation.origin_commit, None, (), None, (), None, (),
            "No current or introducing-commit repository file matches this citation.",
        )
    current_path = current_paths[0] if len(current_paths) == 1 else origin_path
    current_lines = working.file_lines(current_path) if current_path else None
    current_block = _slice(current_lines, citation.start_line, citation.end_line)

    if origin_path is None:
        status = "ok" if current_block is not None else "missing_lines"
        return CitationResult(
            citation.record_path, citation.record_line, citation.target, status,
            "repository", citation.origin_commit, None, (),
            _target(current_path, citation.start_line, citation.end_line), current_block or (),
            None, (),
            "The current repository target exists, but the citation's introducing commit has no matching target."
            if status == "ok" else "The cited line interval is outside the current file.",
        )

    origin_target = _target(origin_path, citation.start_line, citation.end_line)
    if origin_block is None:
        status = "missing_lines" if origin_lines is not None else "missing_file"
        return CitationResult(
            citation.record_path, citation.record_line, citation.target, status,
            "repository", citation.origin_commit, origin_target, (),
            _target(current_path, citation.start_line, citation.end_line) if current_path else None,
            current_block or (), None, (),
            "The citation did not point to an existing line interval when its record line was introduced.",
        )

    if current_path is not None and current_block == origin_block:
        target = _target(current_path, citation.start_line, citation.end_line)
        return CitationResult(
            citation.record_path, citation.record_line, citation.target, "ok",
            "repository", citation.origin_commit, origin_target, origin_block,
            target, current_block, target, current_block,
            "The cited text is unchanged from the record line's introducing commit.",
        )

    matches = _find_block(working.paths, working.file_lines, origin_block, origin_path)
    if len(matches) == 1:
        path, start, end = matches[0]
        real_target = _target(path, start, end)
        return CitationResult(
            citation.record_path, citation.record_line, citation.target, "moved",
            "repository", citation.origin_commit, origin_target, origin_block,
            _target(current_path, citation.start_line, citation.end_line) if current_path else None,
            current_block or (), real_target, origin_block,
            f"The original target text now appears at {real_target}.",
        )

    if current_path is None or current_lines is None:
        status = "missing_file"
        detail = "The file that existed when the citation was introduced is gone from the current tree."
    elif current_block is None:
        status = "missing_lines"
        detail = "The cited line interval is outside the current file."
    else:
        status = "changed"
        detail = "The cited lines no longer contain the text present when the citation was introduced."
        if len(matches) > 1:
            detail += f" The original text has {len(matches)} possible current locations."
    return CitationResult(
        citation.record_path, citation.record_line, citation.target, status,
        "repository", citation.origin_commit, origin_target, origin_block,
        _target(current_path, citation.start_line, citation.end_line) if current_path else None,
        current_block or (), None, (), detail,
    )


def _resolve_external(
    citation: Citation,
    repositories: Sequence[tuple[ExternalRepository, GitRepository]],
    filesystems: Sequence[FilesystemTree],
) -> CitationResult | None:
    commit_sources: set[str] = set()
    for commit in citation.commit_candidates:
        for spec, repository in repositories:
            resolved_commit = repository.resolve_commit(commit)
            if resolved_commit is None:
                continue
            commit_sources.add(spec.name)
            tree_paths = repository.tree_paths(resolved_commit)
            paths = _external_matching_paths(tree_paths, citation.target_path, repository.root, spec.name)
            used_basename_fallback = False
            if len(paths) != 1:
                fallback = _best_basename_match(tree_paths, citation.target_path, citation.context)
                if fallback is None:
                    continue
                paths = (fallback,)
                used_basename_fallback = True
            path = paths[0]
            lines = repository.file_lines(resolved_commit, path)
            block = _slice(lines, citation.start_line, citation.end_line)
            target = f"{spec.name}@{resolved_commit[:12]}:{_target(path, citation.start_line, citation.end_line)}"
            moved = used_basename_fallback and "/" in citation.target_path
            status = "missing_lines" if block is None else ("moved" if moved else "ok")
            return CitationResult(
                citation.record_path, citation.record_line, citation.target, status,
                f"external:{spec.name}", citation.origin_commit, citation.target, (),
                None if moved else target, block or (), target if block is not None else None, block or (),
                f"The named external path now resolves by filename at {target}."
                if moved else (
                    "Resolved against the named external commit."
                    if block is not None else "The cited line interval is outside the pinned external file."
                ),
            )

    absolute = Path(citation.target_path).expanduser()
    if absolute.is_absolute() and absolute.is_file():
        try:
            lines = tuple(absolute.read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeDecodeError):
            lines = ()
        block = _slice(lines, citation.start_line, citation.end_line)
        status = "ok" if block is not None else "missing_lines"
        target = _target(absolute.as_posix(), citation.start_line, citation.end_line)
        return CitationResult(
            citation.record_path, citation.record_line, citation.target, status,
            "external-tree:absolute", citation.origin_commit, target, block or (),
            target, block or (), target if block is not None else None, block or (),
            "Resolved against the current external file; the record names no usable commit."
            if block is not None else "The cited line interval is outside the current external file.",
        )

    if citation.target_path.startswith("GM/"):
        preferred = ("game-main",)
    elif citation.target_path.startswith("DK/") or Path(citation.target_path).name.startswith("D-"):
        preferred = ("darkan-world-server", "darkan-client", "darkan-cache")
    else:
        preferred = _preferred_external_sources(citation.context)
    candidate_trees = [tree for tree in filesystems if not preferred or tree.name in preferred]
    filesystem_matches: list[tuple[FilesystemTree, str, bool]] = []
    for tree in candidate_trees:
        paths = _external_matching_paths(tree.paths, citation.target_path, tree.root, tree.name)
        if len(paths) == 1:
            filesystem_matches.append((tree, paths[0], False))
    if not filesystem_matches:
        for tree in candidate_trees:
            fallback = _best_basename_match(tree.paths, citation.target_path, citation.context)
            if fallback is not None:
                filesystem_matches.append((tree, fallback, True))
    if len(filesystem_matches) == 1:
        tree, path, used_basename_fallback = filesystem_matches[0]
        lines = tree.file_lines(path)
        block = _slice(lines, citation.start_line, citation.end_line)
        target = f"{tree.name}:{_target(path, citation.start_line, citation.end_line)}"
        moved = used_basename_fallback and "/" in citation.target_path
        status = "missing_lines" if block is None else ("moved" if moved else "ok")
        return CitationResult(
            citation.record_path, citation.record_line, citation.target, status,
            f"external-tree:{tree.name}", citation.origin_commit, citation.target, (),
            None if moved else target, block or (), target if block is not None else None, block or (),
            f"The external path now resolves by filename at {target}."
            if moved else (
                "Resolved against the current external tree; the record names no usable commit."
                if block is not None else "The cited line interval is outside the current external file."
            ),
        )
    if len(filesystem_matches) > 1:
        return CitationResult(
            citation.record_path, citation.record_line, citation.target, "ambiguous",
            None, citation.origin_commit, None, (), None, (), None, (),
            "The citation matches more than one unpinned external source tree.",
        )
    if commit_sources:
        if len(commit_sources) == 1:
            source_name = next(iter(commit_sources))
            return CitationResult(
                citation.record_path, citation.record_line, citation.target, "missing_file",
                f"external:{source_name}", citation.origin_commit, citation.target, (),
                None, (), None, (),
                f"The cited file does not exist at the available named {source_name} commit.",
            )
    explicit_source = None
    if citation.target_path.startswith("GM/"):
        explicit_source = "game-main"
    elif citation.target_path.startswith("DK/") or Path(citation.target_path).name.startswith("D-"):
        explicit_source = "darkan-world-server"
    if explicit_source:
        return CitationResult(
            citation.record_path, citation.record_line, citation.target, "missing_file",
            f"external-tree:{explicit_source}", citation.origin_commit, citation.target, (),
            None, (), None, (),
            f"The explicitly named {explicit_source} path does not exist in the available source tree.",
        )
    return None

def audit_citations(
    root: Path,
    *,
    memory_bank: Path | None = None,
    external_repositories: Sequence[ExternalRepository] = (),
    external_filesystems: Sequence[ExternalRepository] = (),
) -> CitationAuditReport:
    root = root.resolve()
    memory_bank = (memory_bank or root / "memory-bank").resolve()
    git = GitRepository(root)
    working = WorkingTree(root)
    markdown_files, citations = _parse_citations(root, memory_bank, git)
    repositories = tuple((spec, GitRepository(spec.path)) for spec in external_repositories if spec.path.exists())
    filesystems = tuple(FilesystemTree(spec.name, spec.path) for spec in external_filesystems if spec.path.exists())
    results: list[CitationResult] = []
    for citation in citations:
        result = _resolve_local(citation, root, git, working)
        if result is None:
            result = _resolve_external(citation, repositories, filesystems)
        if result is None:
            result = CitationResult(
                citation.record_path, citation.record_line, citation.target, "unresolved",
                None, citation.origin_commit, None, (), None, (), None, (),
                "No repository-local target or pinned external source matches this citation.",
            )
        results.append(result)
    result_tuple = tuple(results)
    resolved = sum(result.resolved for result in result_tuple)
    repository_local = sum(result.source == "repository" for result in result_tuple)
    pinned_external = sum(bool(result.source and result.source.startswith("external:")) for result in result_tuple)
    unpinned_external = sum(bool(result.source and result.source.startswith("external-tree:")) for result in result_tuple)
    stale = sum(result.stale for result in result_tuple)
    unresolved = len(result_tuple) - resolved
    return CitationAuditReport(
        markdown_files=markdown_files,
        citations=len(citations),
        resolved=resolved,
        repository_local=repository_local,
        pinned_external=pinned_external,
        unpinned_external=unpinned_external,
        stale=stale,
        unresolved=unresolved,
        results=result_tuple,
    )


def _default_sources() -> tuple[tuple[ExternalRepository, ...], tuple[ExternalRepository, ...]]:
    darkan_root = Path(os.environ.get(
        "ANKISCAPE_DARKAN_WORLD_SERVER",
        "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server",
    ))
    repositories = (
        ExternalRepository("darkan-world-server", darkan_root),
        ExternalRepository(
            "darkan-client",
            Path(os.environ.get(
                "ANKISCAPE_DARKAN_CLIENT",
                "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-client",
            )),
        ),
        ExternalRepository(
            "darkan-cache",
            Path(os.environ.get(
                "ANKISCAPE_DARKAN_CACHE",
                "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-cache",
            )),
        ),
    )
    filesystems = repositories + (
        ExternalRepository(
            "game-main",
            Path(os.environ.get("ANKISCAPE_GAME_MAIN", "/Users/ArmanTarkhanian1/Downloads/game-main")),
        ),
        ExternalRepository(
            "addons21",
            Path(os.environ.get(
                "ANKISCAPE_ADDONS21",
                "/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21",
            )),
        ),
    )
    return repositories, filesystems


def _source_spec(value: str) -> ExternalRepository:
    if "=" not in value:
        raise argparse.ArgumentTypeError("source must be NAME=PATH")
    name, path = value.split("=", 1)
    if not name or not path:
        raise argparse.ArgumentTypeError("source must be NAME=PATH")
    return ExternalRepository(name, Path(path).expanduser())


def _text(lines: tuple[str, ...]) -> str:
    return "\\n".join(lines) if lines else "<missing>"


def _print_result(result: CitationResult) -> None:
    print(f"{result.record_path}:{result.record_line}: {result.status}: `{result.target}`")
    print(f"  {result.detail}")
    if result.origin_target:
        print(f"  origin {result.origin_target}: {_text(result.origin_text)}")
    if result.cited_target:
        print(f"  cited {result.cited_target}: {_text(result.cited_text)}")
    if result.real_target and result.real_target != result.cited_target:
        print(f"  real {result.real_target}: {_text(result.real_text)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--memory-bank", type=Path)
    parser.add_argument("--external-repo", action="append", default=[], type=_source_spec, metavar="NAME=PATH")
    parser.add_argument("--external-tree", action="append", default=[], type=_source_spec, metavar="NAME=PATH")
    parser.add_argument("--no-default-sources", action="store_true")
    parser.add_argument("--all", action="store_true", help="print resolved citations as well as issues")
    parser.add_argument("--limit", type=int, help="limit the number of citation records printed")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    default_repositories, default_filesystems = _default_sources()
    repositories = tuple(args.external_repo) if args.no_default_sources else default_repositories + tuple(args.external_repo)
    filesystems = tuple(args.external_tree) if args.no_default_sources else default_filesystems + tuple(args.external_tree)
    root = args.root.resolve()
    memory_bank = args.memory_bank
    if memory_bank is not None and not memory_bank.is_absolute():
        memory_bank = root / memory_bank
    report = audit_citations(
        root,
        memory_bank=memory_bank,
        external_repositories=repositories,
        external_filesystems=filesystems,
    )
    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"Scanned {report.markdown_files} Markdown files and found {report.citations} citations.")
        print(
            f"Resolved {report.resolved} citations "
            f"({report.repository_local} repository-local, {report.pinned_external} pinned external, "
            f"{report.unpinned_external} current external)."
        )
        print(f"Found {report.stale} stale and {report.unresolved} unresolved citations.")
        displayed = report.results if args.all else tuple(
            result for result in report.results if result.stale or not result.resolved
        )
        if args.limit is not None:
            displayed = displayed[:args.limit]
        for result in displayed:
            _print_result(result)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
