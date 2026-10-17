"""Offline Help Center corpus, validation, search, and rendering helpers.

The runtime corpus is Markdown with JSON front matter. JSON is deliberately
used as the structured front-matter subset so the add-on does not gain a YAML
dependency merely to read its bundled help files.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re
from typing import Iterable, Mapping, Sequence

from .search_match import match_rank


HELP_HOME_ID = "home"
HELP_TOPICS_DIR = Path(__file__).resolve().parents[1] / "help_topics"
KNOWN_REGISTRY_BLOCK_IDS = frozenset({"implemented_skills"})

PRIMARY_HELP_TOPIC_BY_TAB_LABEL: Mapping[str, str] = {
    "Skills": "skills",
    "Shop": "shop",
    "Grand Exchange": "grand-exchange",
    "Quests": "quests",
    "Bank": "bank",
    "Equipment": "equipment",
    "Stats": "stats",
    "Challenges": "challenges",
    "Achievements": "achievements",
    "Collections": "collections",
    "Settings": "settings",
}

_STABLE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_HEADING_RE = re.compile(
    r"^(#{1,6})\s+(.+?)(?:\s+\{#([a-z0-9]+(?:-[a-z0-9]+)*)\})?\s*$"
)
_REGISTRY_BLOCK_RE = re.compile(r"^\{\{registry:([a-z0-9_]+)\}\}$")
_HELP_LINK_RE = re.compile(
    r"\[[^\]]+\]\(help:([a-z0-9]+(?:-[a-z0-9]+)*)(?:#([a-z0-9]+(?:-[a-z0-9]+)*))?\)"
)
_INLINE_LINK_RE = re.compile(
    r"\[([^\]]+)\]\((help:[a-z0-9]+(?:-[a-z0-9]+)*(?:#[a-z0-9]+(?:-[a-z0-9]+)*)?)\)"
)


class HelpCorpusError(ValueError):
    """Raised when bundled help content violates the canonical corpus contract."""


@dataclass(frozen=True)
class HelpHeading:
    level: int
    text: str
    anchor: str


@dataclass(frozen=True)
class HelpLink:
    topic_id: str
    anchor: str = ""


@dataclass(frozen=True)
class HelpTopic:
    help_id: str
    title: str
    surface: str
    aliases: tuple[str, ...]
    tags: tuple[str, ...]
    related: tuple[str, ...]
    body_markdown: str
    headings: tuple[HelpHeading, ...]
    links: tuple[HelpLink, ...]
    registry_blocks: tuple[str, ...]
    source_name: str

    @property
    def search_text(self) -> str:
        return " ".join(
            (
                self.title,
                *self.aliases,
                *self.tags,
                *(heading.text for heading in self.headings),
                self.body_markdown,
            )
        ).casefold()


@dataclass(frozen=True)
class HelpRegistryTable:
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


def _string_tuple(value: object, field: str, source_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise HelpCorpusError(f"{source_name}: {field} must be a list of strings")
    return tuple(item.strip() for item in value if item.strip())


def _slugify_heading(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")
    return normalized or "section"


def _headings_from_markdown(body: str) -> tuple[HelpHeading, ...]:
    headings: list[HelpHeading] = []
    seen: dict[str, int] = {}
    for line in body.splitlines():
        match = _HEADING_RE.match(line)
        if match is None:
            continue
        text = match.group(2).strip()
        base = match.group(3) or _slugify_heading(text)
        duplicate_index = seen.get(base, 0)
        seen[base] = duplicate_index + 1
        anchor = base if duplicate_index == 0 else f"{base}-{duplicate_index + 1}"
        headings.append(HelpHeading(len(match.group(1)), text, anchor))
    return tuple(headings)


def parse_help_topic_text(text: str, *, source_name: str = "<memory>") -> HelpTopic:
    """Parse one canonical topic from JSON-front-matter Markdown."""

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise HelpCorpusError(f"{source_name}: topic must begin with ---")
    try:
        closing_index = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration as exc:
        raise HelpCorpusError(f"{source_name}: front matter has no closing ---") from exc

    raw_metadata = "\n".join(lines[1:closing_index]).strip()
    try:
        metadata = json.loads(raw_metadata)
    except json.JSONDecodeError as exc:
        raise HelpCorpusError(f"{source_name}: invalid JSON front matter: {exc.msg}") from exc
    if not isinstance(metadata, dict):
        raise HelpCorpusError(f"{source_name}: front matter must be a JSON object")

    required = ("help_id", "title", "surface", "aliases", "tags", "related")
    missing = [field for field in required if field not in metadata]
    if missing:
        raise HelpCorpusError(f"{source_name}: missing metadata: {', '.join(missing)}")

    help_id = str(metadata["help_id"]).strip()
    title = str(metadata["title"]).strip()
    surface = str(metadata["surface"]).strip()
    if not _STABLE_ID_RE.fullmatch(help_id):
        raise HelpCorpusError(f"{source_name}: invalid help_id {help_id!r}")
    if not title:
        raise HelpCorpusError(f"{source_name}: title cannot be empty")
    if not _STABLE_ID_RE.fullmatch(surface):
        raise HelpCorpusError(f"{source_name}: invalid surface {surface!r}")

    body = "\n".join(lines[closing_index + 1 :]).strip()
    headings = _headings_from_markdown(body)
    links = tuple(HelpLink(topic_id, anchor or "") for topic_id, anchor in _HELP_LINK_RE.findall(body))
    registry_blocks = tuple(
        match.group(1)
        for line in body.splitlines()
        if (match := _REGISTRY_BLOCK_RE.fullmatch(line.strip())) is not None
    )
    return HelpTopic(
        help_id=help_id,
        title=title,
        surface=surface,
        aliases=_string_tuple(metadata["aliases"], "aliases", source_name),
        tags=_string_tuple(metadata["tags"], "tags", source_name),
        related=_string_tuple(metadata["related"], "related", source_name),
        body_markdown=body,
        headings=headings,
        links=links,
        registry_blocks=registry_blocks,
        source_name=source_name,
    )


def validate_help_topics(
    topics: Sequence[HelpTopic],
    *,
    known_registry_blocks: Iterable[str] = KNOWN_REGISTRY_BLOCK_IDS,
) -> tuple[str, ...]:
    """Return every deterministic corpus violation without stopping at the first."""

    issues: list[str] = []
    topic_by_id: dict[str, HelpTopic] = {}
    for topic in topics:
        if topic.help_id in topic_by_id:
            issues.append(
                f"duplicate help_id {topic.help_id!r}: "
                f"{topic_by_id[topic.help_id].source_name}, {topic.source_name}"
            )
        else:
            topic_by_id[topic.help_id] = topic

    if HELP_HOME_ID not in topic_by_id:
        issues.append(f"missing required home topic {HELP_HOME_ID!r}")

    for tab_label, topic_id in PRIMARY_HELP_TOPIC_BY_TAB_LABEL.items():
        topic = topic_by_id.get(topic_id)
        if topic is None:
            issues.append(f"{tab_label}: missing primary topic {topic_id!r}")
        elif topic.surface != topic_id:
            issues.append(
                f"{topic.source_name}: primary topic surface must be {topic_id!r}, "
                f"got {topic.surface!r}"
            )

    valid_blocks = frozenset(known_registry_blocks)
    for topic in topics:
        anchor_names = {heading.anchor for heading in topic.headings}
        for related_id in topic.related:
            if related_id not in topic_by_id:
                issues.append(f"{topic.source_name}: unknown related topic {related_id!r}")
        for link in topic.links:
            linked_topic = topic_by_id.get(link.topic_id)
            if linked_topic is None:
                issues.append(f"{topic.source_name}: unknown help link {link.topic_id!r}")
                continue
            if link.anchor and link.anchor not in {
                heading.anchor for heading in linked_topic.headings
            }:
                issues.append(
                    f"{topic.source_name}: unknown anchor "
                    f"{link.topic_id!r}#{link.anchor}"
                )
        for block_id in topic.registry_blocks:
            if block_id not in valid_blocks:
                issues.append(f"{topic.source_name}: unknown registry block {block_id!r}")
        if len(anchor_names) != len(topic.headings):
            issues.append(f"{topic.source_name}: duplicate heading anchors")
    return tuple(issues)


def load_help_topics(
    directory: Path | str = HELP_TOPICS_DIR,
    *,
    known_registry_blocks: Iterable[str] = KNOWN_REGISTRY_BLOCK_IDS,
) -> tuple[HelpTopic, ...]:
    """Load and fully validate the checked-in offline corpus."""

    topic_dir = Path(directory)
    topics = tuple(
        parse_help_topic_text(path.read_text(encoding="utf-8"), source_name=path.name)
        for path in sorted(topic_dir.glob("*.md"))
    )
    issues = validate_help_topics(topics, known_registry_blocks=known_registry_blocks)
    if issues:
        raise HelpCorpusError("\n".join(issues))
    return topics


def topics_by_id(topics: Iterable[HelpTopic]) -> dict[str, HelpTopic]:
    return {topic.help_id: topic for topic in topics}


def search_help_topics(topics: Iterable[HelpTopic], query: str) -> tuple[HelpTopic, ...]:
    """Return deterministic AND-token matches across canonical topic content."""

    normalized_query = query.strip().casefold()
    candidates = tuple(topics)
    if not normalized_query:
        return tuple(
            sorted(candidates, key=lambda topic: (topic.help_id != HELP_HOME_ID, topic.title.casefold()))
        )
    matches = [topic for topic in candidates
               if match_rank(normalized_query, topic.title, topic.search_text) is not None]

    def _rank(topic: HelpTopic) -> tuple:
        title = topic.title.casefold()
        aliases = tuple(alias.casefold() for alias in topic.aliases)
        exact = int(normalized_query == title or normalized_query in aliases)
        prefix = int(title.startswith(normalized_query) or any(alias.startswith(normalized_query) for alias in aliases))
        alias_match = normalized_query in aliases
        tier = 0 if alias_match else match_rank(normalized_query, topic.title, topic.search_text)
        return (-int(alias_match), tier, -exact, -prefix, title)

    return tuple(sorted(matches, key=_rank))


def split_help_reference(reference: str) -> tuple[str, str]:
    raw = reference.strip()
    if raw.startswith("help:"):
        raw = raw[5:]
    topic_id, separator, anchor = raw.partition("#")
    return topic_id, anchor if separator else ""


def resolve_help_topic(
    topics: Mapping[str, HelpTopic],
    reference: str,
    *,
    developer_mode: bool = False,
) -> tuple[HelpTopic, str]:
    """Resolve a stable topic reference, falling back home outside development."""

    topic_id, anchor = split_help_reference(reference)
    topic = topics.get(topic_id)
    if topic is None:
        if developer_mode:
            raise KeyError(f"Unknown help topic: {topic_id or reference}")
        topic = topics[HELP_HOME_ID]
        anchor = ""
    elif anchor and anchor not in {heading.anchor for heading in topic.headings}:
        if developer_mode:
            raise KeyError(f"Unknown help anchor: {topic_id}#{anchor}")
        anchor = ""
    return topic, anchor


def _render_inline(text: str) -> str:
    """Render the deliberately small inline subset used by bundled topics."""

    rendered: list[str] = []
    cursor = 0
    for link_match in _INLINE_LINK_RE.finditer(text):
        rendered.append(_render_inline_without_links(text[cursor : link_match.start()]))
        rendered.append(
            f'<a href="{escape(link_match.group(2), quote=True)}">'
            f"{_render_inline_without_links(link_match.group(1))}</a>"
        )
        cursor = link_match.end()
    rendered.append(_render_inline_without_links(text[cursor:]))
    return "".join(rendered)


def _render_inline_without_links(text: str) -> str:
    escaped = escape(text)
    code_tokens: list[str] = []

    def _save_code(match: re.Match[str]) -> str:
        code_tokens.append(f"<code>{match.group(1)}</code>")
        return f"\x00CODE{len(code_tokens) - 1}\x00"

    escaped = re.sub(r"`([^`]+)`", _save_code, escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    for index, token in enumerate(code_tokens):
        escaped = escaped.replace(f"\x00CODE{index}\x00", token)
    return escaped


def _render_registry_table(table: HelpRegistryTable) -> str:
    header_html = "".join(f"<th>{escape(value)}</th>" for value in table.headers)
    row_html = "".join(
        "<tr>" + "".join(f"<td>{escape(value)}</td>" for value in row) + "</tr>"
        for row in table.rows
    )
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{row_html}</tbody></table>"


def render_help_topic_html(
    topic: HelpTopic,
    *,
    registry_tables: Mapping[str, HelpRegistryTable] | None = None,
) -> str:
    """Render the safe Markdown subset used by the offline Qt reader."""

    tables = registry_tables or {}
    output: list[str] = []
    paragraph_lines: list[str] = []
    list_kind = ""
    list_items: list[str] = []
    heading_index = 0

    def _flush_paragraph() -> None:
        if paragraph_lines:
            output.append(f"<p>{_render_inline(' '.join(paragraph_lines))}</p>")
            paragraph_lines.clear()

    def _flush_list() -> None:
        nonlocal list_kind
        if list_items:
            output.append(
                f"<{list_kind}>"
                + "".join(f"<li>{_render_inline(item)}</li>" for item in list_items)
                + f"</{list_kind}>"
            )
            list_items.clear()
        list_kind = ""

    for line in topic.body_markdown.splitlines() + [""]:
        stripped = line.strip()
        if not stripped:
            _flush_paragraph()
            _flush_list()
            continue

        heading_match = _HEADING_RE.match(line)
        if heading_match is not None:
            _flush_paragraph()
            _flush_list()
            heading = topic.headings[heading_index]
            heading_index += 1
            output.append(
                f'<h{heading.level} id="{escape(heading.anchor, quote=True)}">'
                f"{_render_inline(heading.text)}</h{heading.level}>"
            )
            continue

        registry_match = _REGISTRY_BLOCK_RE.fullmatch(stripped)
        if registry_match is not None:
            _flush_paragraph()
            _flush_list()
            block_id = registry_match.group(1)
            table = tables.get(block_id)
            if table is not None:
                output.append(_render_registry_table(table))
            else:
                output.append(
                    '<p class="help-unavailable">Live reference data is unavailable.</p>'
                )
            continue

        unordered_match = re.match(r"^[-*]\s+(.+)$", stripped)
        ordered_match = re.match(r"^\d+\.\s+(.+)$", stripped)
        if unordered_match is not None or ordered_match is not None:
            _flush_paragraph()
            new_kind = "ul" if unordered_match is not None else "ol"
            if list_kind and list_kind != new_kind:
                _flush_list()
            list_kind = new_kind
            list_items.append((unordered_match or ordered_match).group(1))
            continue

        _flush_list()
        paragraph_lines.append(stripped)

    return "\n".join(output)
