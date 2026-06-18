#!/usr/bin/env python3
"""Build the pre-EOC quest catalog from source-backed RuneScape Wiki pages.

The runtime imports the generated Python catalog. This script is intentionally
repeatable: network responses are cached under tools/.cache so the broad quest
tree can be audited and refreshed without re-scraping every page.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import pprint
import re
import time
import urllib.parse
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "tools" / ".cache" / "pre_eoc_quest_catalog"
OUTPUT_PATH = ROOT / "quest_catalog_generated.py"
WIKI_API = "https://runescape.wiki/api.php"
RELEASE_LIST_TITLE = "List of quests by release date"
RELEASE_LIST_SOURCE = "https://runescape.wiki/w/List_of_quests_by_release_date"
EOC_CUTOFF_DATE = dt.date(2012, 11, 20)
EOC_CUTOFF_TIMESTAMP = "2012-11-19T23:59:59Z"
USER_AGENT = "AnkiScape pre-EOC quest catalog builder (local development; contact: local user)"

# These rows are marked former today, but they still existed as quests just
# before the Evolution of Combat release. The current release list is a present
# day page, so this bridge is what makes the generated catalog a cutoff-state
# snapshot instead of a current-live-game snapshot.
FORMER_ROWS_ACTIVE_AT_CUTOFF = {
    "Black Knights' Fortress (quest)",
    "Demon Slayer (historical)",
    "Imp Catcher (historical)",
    "Rune Mysteries (historical)",
}

FORMER_ROWS_REPLACED_BEFORE_CUTOFF = {
    "Death Plateau (historical)",
    "Doric's Quest",
    "Druidic Ritual (historical)",
    "Prince Ali Rescue",
    "Romeo & Juliet",
    "Sheep Shearer (miniquest)",
    "Unstable Foundations",
    "Witch's Potion (miniquest)",
    "Wolf Whistle (historical)",
}

SKILLS: Mapping[str, Tuple[str, str]] = {
    "agility": ("agility", "Agility"),
    "attack": ("attack", "Attack"),
    "combat": ("combat", "Combat"),
    "constitution": ("constitution", "Constitution"),
    "construction": ("construction", "Construction"),
    "cooking": ("cooking", "Cooking"),
    "crafting": ("crafting", "Crafting"),
    "defence": ("defense", "Defence"),
    "defense": ("defense", "Defence"),
    "dungeoneering": ("dungeoneering", "Dungeoneering"),
    "farming": ("farming", "Farming"),
    "firemaking": ("firemaking", "Firemaking"),
    "fishing": ("fishing", "Fishing"),
    "fletching": ("fletching", "Fletching"),
    "herblore": ("herblore", "Herblore"),
    "hunter": ("hunter", "Hunter"),
    "magic": ("magic", "Magic"),
    "mining": ("mining", "Mining"),
    "prayer": ("prayer", "Prayer"),
    "ranged": ("ranged", "Ranged"),
    "runecrafting": ("runecrafting", "Runecrafting"),
    "slayer": ("slayer", "Slayer"),
    "smithing": ("smithing", "Smithing"),
    "strength": ("strength", "Strength"),
    "summoning": ("summoning", "Summoning"),
    "thieving": ("thieving", "Thieving"),
    "woodcutting": ("woodcutting", "Woodcutting"),
}


@dataclass(frozen=True)
class ReleaseRow:
    source_title: str
    display_name: str
    release_date: dt.date
    cumulative_qp: int
    difficulty: str
    former: bool
    nr: str
    update: str


@dataclass(frozen=True)
class Revision:
    title: str
    oldid: int
    timestamp: str
    content: str
    fallback_current: bool


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: List[str] = []

    def handle_starttag(self, tag: str, attrs: Sequence[Tuple[str, Optional[str]]]) -> None:
        if tag in {"br", "li", "p", "div", "tr", "h2", "h3"}:
            self.parts.append("\n")
        if tag == "img":
            attr_map = {key: value for key, value in attrs}
            alt = attr_map.get("alt")
            if alt:
                self.parts.append(f" {alt} ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"li", "p", "div", "tr", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"[ \t]+", " ", "".join(self.parts)).strip()


class AnchorExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.anchors: List[Tuple[str, str]] = []
        self._href: Optional[str] = None
        self._text: List[str] = []

    def handle_starttag(self, tag: str, attrs: Sequence[Tuple[str, Optional[str]]]) -> None:
        if tag != "a":
            return
        attr_map = {key: value for key, value in attrs}
        href = attr_map.get("href")
        if href:
            self._href = href
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._href is None:
            return
        self.anchors.append((self._href, "".join(self._text).strip()))
        self._href = None
        self._text = []


def cached_json(cache_key: str, params: Mapping[str, object]) -> Mapping[str, object]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{cache_key}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(f"{WIKI_API}?{query}", headers={"User-Agent": USER_AGENT})
    last_error: Optional[BaseException] = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = json.loads(response.read().decode("utf-8"))
            tmp_path = cache_path.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            tmp_path.replace(cache_path)
            return payload
        except urllib.error.HTTPError as exc:  # pragma: no cover - network only
            last_error = exc
            if exc.code == 429:
                time.sleep(10 * (attempt + 1))
            else:
                time.sleep(1.5 * (attempt + 1))
        except BaseException as exc:  # pragma: no cover - network only
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Wiki API request failed for {cache_key}: {last_error}")


def slug_key(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", value.lower())
    return re.sub(r"_+", "_", cleaned).strip("_") or "root"


def page_url(title: str, oldid: Optional[int] = None) -> str:
    encoded = urllib.parse.quote(title.replace(" ", "_"), safe="'()")
    url = f"https://runescape.wiki/w/{encoded}"
    return f"{url}?oldid={oldid}" if oldid else url


def normalize_title(value: str) -> str:
    cleaned = html.unescape(value or "")
    cleaned = cleaned.replace("_", " ").replace("’", "'").replace("`", "'")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned.lower()


def display_from_source_title(title: str, alt: str = "") -> str:
    if alt:
        return alt.strip()
    cleaned = re.sub(r"\s+\((historical|quest|miniquest)\)$", "", title, flags=re.I)
    return cleaned.strip()


def quest_id_from_name(name: str) -> str:
    value = html.unescape(name).lower()
    value = value.replace("&", " and ")
    value = value.replace("'", "")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


def split_top_level(value: str, delimiter: str) -> List[str]:
    parts: List[str] = []
    start = 0
    brace_depth = 0
    bracket_depth = 0
    i = 0
    while i < len(value):
        if value.startswith("{{", i):
            brace_depth += 1
            i += 2
            continue
        if value.startswith("}}", i) and brace_depth:
            brace_depth -= 1
            i += 2
            continue
        if value.startswith("[[", i):
            bracket_depth += 1
            i += 2
            continue
        if value.startswith("]]", i) and bracket_depth:
            bracket_depth -= 1
            i += 2
            continue
        if value[i] == delimiter and brace_depth == 0 and bracket_depth == 0:
            parts.append(value[start:i])
            start = i + 1
        i += 1
    parts.append(value[start:])
    return parts


def split_key_value(part: str) -> Optional[Tuple[str, str]]:
    pieces = split_top_level(part, "=")
    if len(pieces) < 2:
        return None
    key = pieces[0].strip()
    value = "=".join(pieces[1:]).strip()
    if not key:
        return None
    return key, value


def parse_template_params(body: str) -> Dict[str, str]:
    parts = split_top_level(body, "|")
    params: Dict[str, str] = {}
    positional = 1
    for raw_part in parts[1:]:
        kv = split_key_value(raw_part)
        if kv is None:
            params[str(positional)] = raw_part.strip()
            positional += 1
        else:
            key, value = kv
            params[key.strip().lower().replace("_", " ")] = value
    return params


def template_name(body: str) -> str:
    first = split_top_level(body, "|")[0]
    return re.sub(r"[\s_]+", " ", first.strip().lower())


def iter_templates(text: str) -> Iterator[str]:
    i = 0
    while i < len(text):
        if not text.startswith("{{", i):
            i += 1
            continue
        start = i + 2
        depth = 1
        i += 2
        while i < len(text):
            if text.startswith("{{", i):
                depth += 1
                i += 2
                continue
            if text.startswith("}}", i):
                depth -= 1
                if depth == 0:
                    yield text[start:i]
                    i += 2
                    break
                i += 2
                continue
            i += 1
    return


def find_first_template(text: str, names: Iterable[str]) -> Dict[str, str]:
    wanted = {re.sub(r"[\s_]+", " ", name.strip().lower()) for name in names}
    for body in iter_templates(text):
        if template_name(body) in wanted:
            return parse_template_params(body)
    return {}


def clean_markup(value: str) -> str:
    text = re.sub(r"<!--.*?-->", "", value, flags=re.S)
    text = re.sub(r"<ref\b.*?</ref>", "", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\{\{[^{}]*\}\}", "", text)
    text = re.sub(r"\[\[([^|\]#]+)(?:#[^|\]]*)?\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^|\]#]+)(?:#[^\]]*)?\]\]", r"\1", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip(" -*\n\t")
    return text


def parse_date(value: str) -> dt.date:
    return dt.datetime.strptime(clean_markup(value).strip(), "%d %B %Y").date()


def parse_int(value: object, default: int = 0) -> int:
    try:
        return int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def canonical_length(value: str) -> str:
    cleaned = clean_markup(value).lower()
    cleaned = cleaned.replace("-", " ").replace("/", " ")
    if "very" in cleaned and "long" in cleaned:
        if cleaned.count("very") >= 2:
            return "Very, Very Long"
        return "Very Long"
    if "long" in cleaned and "medium" in cleaned:
        return "Medium to Long"
    if "short" in cleaned and "medium" in cleaned:
        return "Short to Medium"
    if "long" in cleaned:
        return "Long"
    if "medium" in cleaned:
        return "Medium"
    if "short" in cleaned:
        return "Short"
    return "Medium"


def canonical_timeline(value: str) -> str:
    cleaned = clean_markup(value)
    if not cleaned:
        return "Fifth Age"
    if "Sixth" in cleaned:
        return "Sixth Age"
    if "Ambiguous" in cleaned:
        return "Ambiguous"
    return "Fifth Age"


def parse_members(value: str) -> bool:
    cleaned = clean_markup(value).strip().lower()
    return cleaned not in {"no", "false", "free", "f2p"}


def html_to_text(section_html: str) -> str:
    parser = TextExtractor()
    parser.feed(section_html)
    return parser.text()


def section_html(page_html: str, heading: str) -> str:
    heading_re = re.compile(
        rf"<h2\b[^>]*id=\"[^\"]*{re.escape(heading)}[^\"]*\"[^>]*>|"
        rf"<span[^>]+class=\"mw-headline\"[^>]+id=\"[^\"]*{re.escape(heading)}[^\"]*\"[^>]*>",
        flags=re.I,
    )
    matches = [match for match in heading_re.finditer(page_html)]
    match = next((candidate for candidate in matches if "<li" not in page_html[max(0, candidate.start() - 200) : candidate.start()]), None)
    if not match:
        return ""
    heading_wrapper = page_html.rfind("<div", 0, match.start())
    nearest_h2 = page_html.rfind("<h2", 0, match.start())
    start = heading_wrapper if heading_wrapper >= 0 and heading_wrapper > page_html.rfind("</p>", 0, match.start()) else nearest_h2
    if start < 0:
        start = match.start()
    end_match = re.search(r"<div\b[^>]*mw-heading[^>]*>\s*<h2\b|<h2\b", page_html[match.end() :], flags=re.I)
    end = match.end() + end_match.start() if end_match else len(page_html)
    return page_html[start:end]


def parse_questline_templates(text: str) -> List[ReleaseRow]:
    rows: List[ReleaseRow] = []
    for body in iter_templates(text):
        if template_name(body) != "questline":
            continue
        params = parse_template_params(body)
        source_title = (params.get("name") or params.get("1") or "").strip()
        date_value = (params.get("date") or "").strip()
        if not source_title or not date_value:
            continue
        try:
            release_date = parse_date(date_value)
        except ValueError:
            continue
        rows.append(
            ReleaseRow(
                source_title=source_title,
                display_name=display_from_source_title(source_title, params.get("alt", "")),
                release_date=release_date,
                cumulative_qp=parse_int(params.get("qp")),
                difficulty=clean_markup(params.get("dif") or params.get("difficulty") or "Novice"),
                former=(params.get("former") or "").strip().lower() == "yes",
                nr=(params.get("nr") or "").strip(),
                update=clean_markup(params.get("update") or ""),
            )
        )
    return rows


def include_row(row: ReleaseRow) -> bool:
    if row.release_date >= EOC_CUTOFF_DATE:
        return False
    if row.former:
        return row.source_title in FORMER_ROWS_ACTIVE_AT_CUTOFF
    return row.source_title not in FORMER_ROWS_REPLACED_BEFORE_CUTOFF


def fetch_wikitext(title: str, before_cutoff: bool = True) -> Revision:
    params: Dict[str, object] = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "ids|timestamp|content",
        "rvslots": "main",
        "rvlimit": "1",
        "titles": title,
        "redirects": "1",
        "format": "json",
        "formatversion": "2",
    }
    if before_cutoff:
        params.update({"rvstart": EOC_CUTOFF_TIMESTAMP, "rvdir": "older"})
    payload = cached_json(f"wikitext_{slug_key(title)}_{'old' if before_cutoff else 'current'}", params)
    page = (payload.get("query", {}).get("pages") or [{}])[0]  # type: ignore[union-attr]
    revisions = page.get("revisions") or {}
    if isinstance(revisions, list) and revisions:
        revision = revisions[0]
        return Revision(
            title=str(page.get("title") or title),
            oldid=parse_int(revision.get("revid")),
            timestamp=str(revision.get("timestamp") or ""),
            content=str(((revision.get("slots") or {}).get("main") or {}).get("content") or ""),
            fallback_current=not before_cutoff,
        )
    if before_cutoff:
        return fetch_wikitext(title, before_cutoff=False)
    raise RuntimeError(f"No revision found for {title}")


def fetch_parsed_html(revision: Revision) -> str:
    payload = cached_json(
        f"parse_{revision.oldid}",
        {
            "action": "parse",
            "oldid": revision.oldid,
            "prop": "text",
            "format": "json",
            "formatversion": "2",
        },
    )
    parsed = payload.get("parse") or {}
    return str((parsed.get("text") or ""))


def build_title_lookup(rows: Sequence[ReleaseRow]) -> Dict[str, Tuple[str, str]]:
    lookup: Dict[str, Tuple[str, str]] = {}
    for row in rows:
        quest_id = quest_id_from_name(row.display_name)
        for title in {row.source_title, row.display_name, re.sub(r"\s+\((historical|quest|miniquest)\)$", "", row.source_title, flags=re.I)}:
            key = normalize_title(title)
            if key:
                lookup[key] = (quest_id, row.display_name)
    return lookup


def anchor_title(href: str, label: str) -> str:
    parsed = urllib.parse.urlparse(href)
    if parsed.path.startswith("/w/"):
        raw_title = urllib.parse.unquote(parsed.path[3:]).replace("_", " ")
        return raw_title.split("#", 1)[0]
    return label


def parse_questreq_tables(page_html: str, title_lookup: Mapping[str, Tuple[str, str]], current_id: str) -> List[Tuple[str, str]]:
    quests: List[Tuple[str, str]] = []
    for table_match in re.finditer(r"<table\b[^>]*questreq[^>]*>.*?</table>", page_html, flags=re.I | re.S):
        parser = AnchorExtractor()
        parser.feed(table_match.group(0))
        for href, label in parser.anchors:
            candidates = (anchor_title(href, label), label)
            for candidate in candidates:
                mapped = title_lookup.get(normalize_title(candidate))
                if not mapped:
                    continue
                quest_id, display_name = mapped
                if quest_id != current_id:
                    quests.append((quest_id, display_name))
                break
    return dedupe_pairs(quests)


def parse_linked_quests(requirements: str, title_lookup: Mapping[str, Tuple[str, str]], current_id: str) -> List[Tuple[str, str]]:
    quests: List[Tuple[str, str]] = []
    for target, label in re.findall(r"\[\[([^|\]#]+)(?:#[^|\]]*)?(?:\|([^\]]+))?\]\]", requirements):
        for candidate in (target, label):
            if not candidate:
                continue
            mapped = title_lookup.get(normalize_title(candidate))
            if not mapped:
                continue
            quest_id, display_name = mapped
            if quest_id != current_id:
                quests.append((quest_id, display_name))
            break
    return dedupe_pairs(quests)


def dedupe_pairs(values: Iterable[Tuple[str, str]]) -> List[Tuple[str, str]]:
    seen = set()
    output = []
    for quest_id, display_name in values:
        if quest_id in seen:
            continue
        seen.add(quest_id)
        output.append((quest_id, display_name))
    return output


def parse_skill_requirements(requirements: str, page_html: str) -> List[Tuple[str, str, int]]:
    skill_reqs: Dict[str, Tuple[str, int]] = {}
    for skill_name, level in re.findall(r"\{\{\s*Skillreq\s*\|\s*([^|}]+)\s*\|\s*(\d+)", requirements, flags=re.I):
        mapped = SKILLS.get(normalize_title(skill_name))
        if mapped:
            skill_id, display_name = mapped
            skill_reqs[skill_id] = (display_name, max(skill_reqs.get(skill_id, (display_name, 0))[1], int(level)))

    for level, skill_name in re.findall(
        r"(?:\bLevel\s*)?(\d{1,3})\+?\s*\{\{\s*Skill clickpic\s*\|\s*([^|}]+)",
        requirements,
        flags=re.I,
    ):
        mapped = SKILLS.get(normalize_title(skill_name))
        if mapped:
            skill_id, display_name = mapped
            skill_reqs[skill_id] = (display_name, max(skill_reqs.get(skill_id, (display_name, 0))[1], int(level)))

    for skill_name, level in re.findall(r'data-skill="([^"]+)"[^>]+data-level="(\d+)"', page_html, flags=re.I):
        mapped = SKILLS.get(normalize_title(skill_name))
        if mapped:
            skill_id, display_name = mapped
            skill_reqs[skill_id] = (display_name, max(skill_reqs.get(skill_id, (display_name, 0))[1], int(level)))

    plain = clean_markup(requirements)
    for level, skill_name in re.findall(
        r"\b(\d{1,2})\s+(Agility|Attack|Constitution|Construction|Cooking|Crafting|Defence|Defense|Dungeoneering|Farming|Firemaking|Fishing|Fletching|Herblore|Hunter|Magic|Mining|Prayer|Ranged|Runecrafting|Slayer|Smithing|Strength|Summoning|Thieving|Woodcutting)\b",
        plain,
        flags=re.I,
    ):
        mapped = SKILLS.get(normalize_title(skill_name))
        if mapped:
            skill_id, display_name = mapped
            skill_reqs[skill_id] = (display_name, max(skill_reqs.get(skill_id, (display_name, 0))[1], int(level)))

    return sorted((skill_id, display_name, level) for skill_id, (display_name, level) in skill_reqs.items())


def parse_required_quest_points(requirements: str) -> int:
    plain = clean_markup(requirements)
    values = [int(value) for value in re.findall(r"\b(\d{1,3})\s+quest points?\b", plain, flags=re.I)]
    return max(values) if values else 0


def parse_reward_points(reward_text: str) -> int:
    values = [int(value) for value in re.findall(r"\b(\d{1,2})\s+quest points?\b", reward_text, flags=re.I)]
    return values[0] if values else 0


def parse_xp_rewards(reward_text: str) -> List[Tuple[str, float]]:
    reward_text = "\n".join(
        line for line in reward_text.splitlines()
        if not re.search(r"\bextra\b.*\b(when|after)\b|\b(when|after)\b.*\bextra\b", line, flags=re.I)
    )
    rewards: Dict[str, float] = {}
    skill_names = sorted({display for _, display in SKILLS.values()}, key=len, reverse=True)
    skill_pattern = "|".join(re.escape(name) for name in skill_names)

    for amount_text, target_text in re.findall(
        rf"\b([0-9][0-9,]*(?:\.\d+)?)\s+([A-Za-z, /\-&]+?)\s+(?:XP|experience)\b",
        reward_text,
        flags=re.I,
    ):
        amount = float(amount_text.replace(",", ""))
        target_lower = target_text.lower()
        for skill_name in skill_names:
            if re.search(rf"\b{re.escape(skill_name.lower())}\b", target_lower):
                skill_id = SKILLS[normalize_title(skill_name)][0]
                rewards[skill_id] = rewards.get(skill_id, 0.0) + amount

    for amount_text, skill_name in re.findall(
        rf"\b([0-9][0-9,]*(?:\.\d+)?)\s+(?:XP|experience)(?: points)?(?:\s+(?:in|to|for))?\s+(?:the\s+)?({skill_pattern})\b",
        reward_text,
        flags=re.I,
    ):
        skill_id = SKILLS[normalize_title(skill_name)][0]
        rewards[skill_id] = rewards.get(skill_id, 0.0) + float(amount_text.replace(",", ""))

    return sorted(rewards.items())


def quest_details_from_wikitext(wikitext: str) -> Dict[str, str]:
    return find_first_template(wikitext, ("Quest details", "Questdetails"))


def fallback_reward_points(rows: Sequence[ReleaseRow], row: ReleaseRow, index: int) -> int:
    if index <= 0:
        return max(row.cumulative_qp, 0)
    previous = rows[index - 1]
    return max(row.cumulative_qp - previous.cumulative_qp, 0)


def parse_catalog_row(
    index: int,
    row: ReleaseRow,
    included_rows: Sequence[ReleaseRow],
    title_lookup: Mapping[str, Tuple[str, str]],
) -> Mapping[str, object]:
    quest_id = quest_id_from_name(row.display_name)
    revision = fetch_wikitext(row.source_title, before_cutoff=True)
    parsed_html = fetch_parsed_html(revision)
    details = quest_details_from_wikitext(revision.content)
    requirements_wikitext = details.get("requirements", "")
    reward_html = section_html(parsed_html, "Reward")
    reward_text = html_to_text(reward_html)

    required_quests = parse_questreq_tables(parsed_html, title_lookup, quest_id)
    if not required_quests:
        required_quests = parse_linked_quests(requirements_wikitext, title_lookup, quest_id)
    if not required_quests:
        current_revision = fetch_wikitext(row.source_title, before_cutoff=False)
        current_html = fetch_parsed_html(current_revision)
        required_quests = parse_questreq_tables(current_html, title_lookup, quest_id)
        if not required_quests:
            current_details = quest_details_from_wikitext(current_revision.content)
            required_quests = parse_linked_quests(current_details.get("requirements", ""), title_lookup, quest_id)

    required_skills = parse_skill_requirements(requirements_wikitext, parsed_html)
    required_quest_points = parse_required_quest_points(requirements_wikitext)
    point_reward = parse_reward_points(reward_text) or fallback_reward_points(included_rows, row, index)
    xp_rewards = parse_xp_rewards(reward_text)

    requirement_labels: List[str] = []
    requirement_labels.extend(display_name for _, display_name in required_quests)
    if required_quest_points:
        requirement_labels.append(f"{required_quest_points} Quest Points")
    requirement_labels.extend(f"{display_name} {level}" for _, display_name, level in required_skills)

    start_point = clean_markup(details.get("start", ""))
    combat = clean_markup(details.get("kills", "") or details.get("combat", ""))
    return {
        "id": quest_id,
        "display_name": row.display_name,
        "source_title": row.source_title,
        "source": page_url(revision.title, revision.oldid),
        "source_revision": revision.oldid,
        "source_timestamp": revision.timestamp,
        "source_fallback_current": revision.fallback_current,
        "release_source": RELEASE_LIST_SOURCE,
        "release_order": index + 1,
        "release_date": row.release_date.isoformat(),
        "members": parse_members(details.get("members", "Yes")),
        "difficulty": row.difficulty or clean_markup(details.get("difficulty", "Novice")),
        "length": canonical_length(details.get("length", "")),
        "timeline": canonical_timeline(details.get("timeline") or details.get("age") or ""),
        "start_point": start_point or "See the source guide for the start location.",
        "combat": combat or "See the source guide.",
        "requirements": tuple(requirement_labels),
        "required_quests": tuple({"quest_id": quest_id, "display_name": display_name} for quest_id, display_name in required_quests),
        "required_skills": tuple(
            {"skill_id": skill_id, "display_name": display_name, "level": level}
            for skill_id, display_name, level in required_skills
        ),
        "required_quest_points": required_quest_points,
        "point_reward": point_reward,
        "xp_rewards": tuple({"skill_id": skill_id, "amount": amount} for skill_id, amount in xp_rewards),
    }


def fetch_release_list() -> str:
    revision = fetch_wikitext(RELEASE_LIST_TITLE, before_cutoff=False)
    return revision.content


def main() -> None:
    release_text = fetch_release_list()
    all_rows = parse_questline_templates(release_text)
    included_rows = [row for row in all_rows if include_row(row)]
    included_rows.sort(key=lambda row: (row.release_date, parse_int(row.nr, 9999), row.display_name))
    title_lookup = build_title_lookup(included_rows)

    parsed_by_id: Dict[str, Mapping[str, object]] = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(parse_catalog_row, index, row, included_rows, title_lookup): row
            for index, row in enumerate(included_rows)
        }
        for future in as_completed(futures):
            row = futures[future]
            parsed = future.result()
            parsed_by_id[str(parsed["id"])] = parsed
            print(f"parsed {parsed['release_order']:>3} {row.display_name}")

    catalog = [parsed_by_id[quest_id_from_name(row.display_name)] for row in included_rows]
    missing = sorted(
        {
            req["quest_id"]
            for quest in catalog
            for req in quest.get("required_quests", ())
            if isinstance(req, Mapping) and req.get("quest_id") not in parsed_by_id
        }
    )
    if missing:
        raise RuntimeError(f"Generated catalog has missing required quest ids: {missing}")

    output = (
        '"""Generated pre-EOC quest catalog for AnkiScape."""\n\n'
        "# Generated by tools/build_pre_eoc_quest_catalog.py. Do not edit manually.\n"
        "# Source cutoff: RuneScape quests available before 2012-11-20 (Evolution of Combat release day).\n\n"
        "PRE_EOC_QUEST_CATALOG_SOURCE = {\n"
        f'    "release_list": {RELEASE_LIST_SOURCE!r},\n'
        f'    "cutoff_date": {EOC_CUTOFF_DATE.isoformat()!r},\n'
        f'    "quest_count": {len(catalog)},\n'
        "}\n\n"
        f"PRE_EOC_QUEST_CATALOG = {pprint.pformat(tuple(catalog), width=120, sort_dicts=False)}\n"
    )
    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"wrote {len(catalog)} quests to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
