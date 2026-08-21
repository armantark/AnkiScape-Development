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
import os
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
OUTPUT_PATH = ROOT / "generated" / "quest_catalog_generated.py"
WIKI_API = "https://runescape.wiki/api.php"
RELEASE_LIST_TITLE = "List of quests by release date"
RELEASE_LIST_SOURCE = "https://runescape.wiki/w/List_of_quests_by_release_date"
EOC_CUTOFF_DATE = dt.date(2012, 11, 20)
EOC_CUTOFF_TIMESTAMP = "2012-11-19T23:59:59Z"
USER_AGENT = "AnkiScape pre-EOC quest catalog builder (local development; contact: local user)"
LIGHT_SOURCES_SOURCE = "https://runescape.wiki/w/Light_sources?oldid=6581760"
LIT_LIGHT_SOURCE_ITEMS = (
    "Lit torch",
    "Lit candle",
    "Lit black candle",
    "Candle lantern (lit, 4531)",
    "Candle lantern (lit, 4534)",
    "Oil lamp (lit)",
    "Oil lantern (lit)",
    "Bullseye lantern (lit)",
    "Sapphire lantern (lit)",
    "Emerald lantern (lit)",
    "Mining helmet (lit)",
)
PERIOD_LIT_LIGHT_SOURCE_ITEMS = (
    *LIT_LIGHT_SOURCE_ITEMS,
    "Seer's headband 1",
    "Seer's headband 2",
    "Seer's headband 3",
    "Seer's headband 4",
    "Bronze torch",
    "Silver torch",
    "Gold torch",
)
LIGHT_SOURCE_REQUIREMENT_STAGE_BY_QUEST = {
    "rag_and_bone_man": 2,
    "land_of_the_goblins": 7,
    "defender_of_varrock": 4,
    "the_chosen_commander": 3,
}
LIGHT_SOURCE_STAGE_BLOCKED_QUESTS = frozenset({
    "watchtower",
    "another_slice_of_h_a_m",
})
DEFAULT_GAME_MAIN_DIR = Path("/Users/ArmanTarkhanian1/Downloads/game-main")
GAME_MAIN_DIR = Path(os.environ.get("ANKISCAPE_GAME_MAIN", DEFAULT_GAME_MAIN_DIR))
SCAPE_2011_QUEST_IMPL_RELATIVE = Path(
    "game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl"
)
SCAPE_2011_QUEST_IMPL_DIR = GAME_MAIN_DIR / SCAPE_2011_QUEST_IMPL_RELATIVE
SCAPE_2011_NPC_DEFINITION_DIR = (
    GAME_MAIN_DIR / "game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions"
)
DEFAULT_DARKAN_WORLD_SERVER_DIR = Path(
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server"
)
DARKAN_WORLD_SERVER_DIR = Path(
    os.environ.get("ANKISCAPE_DARKAN_WORLD_SERVER", DEFAULT_DARKAN_WORLD_SERVER_DIR)
)
DARKAN_NPC_LIST_PATH = DARKAN_WORLD_SERVER_DIR / "developer-information/npcList.txt"
DARKAN_BEASTS_PATH = DARKAN_WORLD_SERVER_DIR / "developer-information/beasts.txt"
DARKAN_NPC_COMBATDEF_DIR = DARKAN_WORLD_SERVER_DIR / "data/npcs/combatdefs"


def _preserve_source_provenance(rendered: str) -> str:
    for source_root, provenance_root in (
        (GAME_MAIN_DIR, DEFAULT_GAME_MAIN_DIR),
        (DARKAN_WORLD_SERVER_DIR, DEFAULT_DARKAN_WORLD_SERVER_DIR),
    ):
        if source_root != provenance_root:
            rendered = rendered.replace(str(source_root), str(provenance_root))
    return rendered


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

RFD_SUBQUESTS: Tuple[Tuple[str, str], ...] = (
    ("Recipe for Disaster: Another Cook's Quest", "Recipe for Disaster: Another Cook's Quest"),
    ("Recipe for Disaster: Freeing the Mountain Dwarf", "Recipe for Disaster: Freeing the Mountain Dwarf"),
    ("Recipe for Disaster: Freeing the Goblin Generals", "Recipe for Disaster: Freeing the Goblin generals"),
    ("Recipe for Disaster: Freeing Pirate Pete", "Recipe for Disaster: Freeing Pirate Pete"),
    ("Recipe for Disaster: Freeing the Lumbridge Sage", "Recipe for Disaster: Freeing the Lumbridge Sage"),
    ("Recipe for Disaster: Freeing Evil Dave", "Recipe for Disaster: Freeing Evil Dave"),
    ("Recipe for Disaster: Freeing Sir Amik Varze", "Recipe for Disaster: Freeing Sir Amik Varze"),
    ("Recipe for Disaster: Freeing King Awowogei", "Recipe for Disaster: Freeing King Awowogei"),
    ("Recipe for Disaster: Freeing Skrach Uglogwee", "Recipe for Disaster: Freeing Skrach Uglogwee"),
    ("Recipe for Disaster: Defeating the Culinaromancer", "Recipe for Disaster: Defeating the Culinaromancer"),
)

RFD_REQUIREMENT_ALIASES: Mapping[str, str] = {
    "recipe for disaster": "recipe_for_disaster_defeating_the_culinaromancer",
    "recipe for disaster/another cook's quest": "recipe_for_disaster_another_cooks_quest",
    "recipe for disaster/freeing the mountain dwarf": "recipe_for_disaster_freeing_the_mountain_dwarf",
    "recipe for disaster/freeing the goblin generals": "recipe_for_disaster_freeing_the_goblin_generals",
    "recipe for disaster/freeing pirate pete": "recipe_for_disaster_freeing_pirate_pete",
    "recipe for disaster/freeing the lumbridge sage": "recipe_for_disaster_freeing_the_lumbridge_sage",
    "recipe for disaster/freeing the lumbridge guide": "recipe_for_disaster_freeing_the_lumbridge_sage",
    "recipe for disaster/freeing evil dave": "recipe_for_disaster_freeing_evil_dave",
    "recipe for disaster/freeing sir amik varze": "recipe_for_disaster_freeing_sir_amik_varze",
    "recipe for disaster/freeing king awowogei": "recipe_for_disaster_freeing_king_awowogei",
    "recipe for disaster/freeing skrach uglogwee": "recipe_for_disaster_freeing_skrach_uglogwee",
    "recipe for disaster/defeating the culinaromancer": "recipe_for_disaster_defeating_the_culinaromancer",
}

RFD_FINALE_ID = "recipe_for_disaster_defeating_the_culinaromancer"

_UNLOCK_REWARD_PREFIXES = (
    "access to",
    "full access to",
    "further access to",
    "(further) access to",
    "ability to",
    "the ability to",
    "permission to",
    "music unlocked",
    "a new route",
    "you can now",
)

_REWARD_ITEM_SKIP_TITLES = {
    "agility",
    "attack",
    "constitution",
    "cooking",
    "crafting",
    "defence",
    "defense",
    "experience",
    "farming",
    "firemaking",
    "fishing",
    "fletching",
    "herblore",
    "historian minas",
    "hunter",
    "lamp",
    "magic",
    "members",
    "mining",
    "prayer",
    "quest point",
    "quest points",
    "ranged",
    "runecrafting",
    "slayer",
    "squeal of fortune",
    "strength",
    "summoning",
    "thieving",
    "treasure hunter key",
    "woodcutting",
}

_REWARD_ITEM_CATEGORY_HINTS = (
    "amulet",
    "armour",
    "armor",
    "axe",
    "bow",
    "body",
    "boots",
    "dagger",
    "gloves",
    "helmet",
    "helm",
    "mace",
    "platebody",
    "ring",
    "shield",
    "staff",
    "sword",
    "wand",
)

_QUEST_STAGE_TOOL_NAMES = {
    "axe",
    "crayfish cage",
    "hammer",
    "knife",
    "lobster pot",
    "needle",
    "pickaxe",
    "saw",
    "secateurs",
    "shears",
    "spade",
    "tinderbox",
}

_QUEST_REQUIREMENT_LINK_SKIP_TITLES = {
    "black arm gang",
    "champions' guild",
    "falador",
    "grand exchange",
    "karamja",
    "magic",
    "members",
    "phoenix gang",
    "ranged",
    "taverley dungeon",
    "toolbelt",
    "wormbrain",
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


class RewardListExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: List[Dict[str, object]] = []
        self._in_li = False
        self._depth = 0
        self._text: List[str] = []
        self._href: Optional[str] = None
        self._anchor_text: List[str] = []
        self._anchor_title: str = ""
        self._anchors: List[Dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: Sequence[Tuple[str, Optional[str]]]) -> None:
        attr_map = {key: value for key, value in attrs}
        if tag == "li":
            if not self._in_li:
                self._in_li = True
                self._depth = 1
                self._text = []
                self._anchors = []
            else:
                self._depth += 1
                self._text.append("\n")
            return
        if not self._in_li:
            return
        if tag in {"br", "p", "div"}:
            self._text.append("\n")
        if tag == "img":
            alt = attr_map.get("alt")
            if alt:
                self._text.append(f" {alt} ")
        if tag == "a":
            self._href = attr_map.get("href")
            self._anchor_title = html.unescape(attr_map.get("title") or "")
            self._anchor_text = []

    def handle_data(self, data: str) -> None:
        if not self._in_li:
            return
        self._text.append(data)
        if self._href is not None:
            self._anchor_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._in_li:
            return
        if tag == "a" and self._href is not None:
            label = re.sub(r"\s+", " ", "".join(self._anchor_text)).strip()
            self._anchors.append({"href": self._href, "label": label, "title": self._anchor_title})
            self._href = None
            self._anchor_text = []
            self._anchor_title = ""
            return
        if tag == "li":
            self._depth -= 1
            if self._depth <= 0:
                text = re.sub(r"[ \t]+", " ", "".join(self._text))
                text = re.sub(r"\s*\n\s*", " ", text).strip()
                if text:
                    self.items.append({"text": text, "anchors": tuple(self._anchors)})
                self._in_li = False
                self._depth = 0
                self._text = []
                self._anchors = []


class QuickGuideExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lines: List[str] = []
        self._in_li = False
        self._depth = 0
        self._text: List[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: Sequence[Tuple[str, Optional[str]]]) -> None:
        if tag in {"script", "style", "table"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag == "li":
            if not self._in_li:
                self._in_li = True
                self._depth = 1
                self._text = []
            else:
                self._depth += 1
                self._text.append(" ")
        elif self._in_li and tag in {"br", "p", "div"}:
            self._text.append(" ")
        elif self._in_li and tag == "img":
            attr_map = {key: value for key, value in attrs}
            alt = attr_map.get("alt")
            if alt:
                self._text.append(f" {alt} ")

    def handle_data(self, data: str) -> None:
        if self._in_li and not self._skip_depth:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._skip_depth:
            if tag in {"script", "style", "table"}:
                self._skip_depth -= 1
            return
        if tag != "li" or not self._in_li:
            return
        self._depth -= 1
        if self._depth <= 0:
            text = re.sub(r"\s+", " ", "".join(self._text)).strip(" -*\n\t")
            if text:
                self.lines.append(text)
            self._in_li = False
            self._depth = 0
            self._text = []


class WalkthroughProseExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lines: List[str] = []
        self._in_paragraph = False
        self._text: List[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: Sequence[Tuple[str, Optional[str]]]) -> None:
        if tag in {"script", "style", "table"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag == "p" and not self._in_paragraph:
            self._in_paragraph = True
            self._text = []
        elif self._in_paragraph and tag in {"br", "div"}:
            self._text.append(" ")

    def handle_data(self, data: str) -> None:
        if self._in_paragraph and not self._skip_depth:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._skip_depth:
            if tag in {"script", "style", "table"}:
                self._skip_depth -= 1
            return
        if tag != "p" or not self._in_paragraph:
            return
        text = re.sub(r"\s+", " ", "".join(self._text)).strip(" -*\n\t")
        if text:
            self.lines.append(text)
        self._in_paragraph = False
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


RFD_DISPLAY_BY_ID: Mapping[str, str] = {
    quest_id_from_name(display_name): display_name
    for display_name, _ in RFD_SUBQUESTS
}


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


_STAGE_COUNT_BY_LENGTH = {
    "Short": 3,
    "Short to Medium": 4,
    "Medium": 5,
    "Medium to Long": 6,
    "Long": 7,
    "Long to Very Long": 8,
    "Very Long": 9,
    "Very, Very Long": 10,
}


def generated_stage_count(length: str) -> int:
    return _STAGE_COUNT_BY_LENGTH.get(length, 5)


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
    by_id = {quest_id_from_name(row.display_name): row.display_name for row in rows}
    for row in rows:
        quest_id = quest_id_from_name(row.display_name)
        for title in {row.source_title, row.display_name, re.sub(r"\s+\((historical|quest|miniquest)\)$", "", row.source_title, flags=re.I)}:
            key = normalize_title(title)
            if key:
                lookup[key] = (quest_id, row.display_name)
    for alias, quest_id in RFD_REQUIREMENT_ALIASES.items():
        display_name = by_id.get(quest_id)
        if display_name:
            lookup[normalize_title(alias)] = (quest_id, display_name)
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


def rfd_manual_prerequisites(current_id: str) -> Tuple[Tuple[str, str], ...]:
    if current_id != RFD_FINALE_ID:
        return ()
    return tuple(
        (quest_id, display_name)
        for quest_id, display_name in RFD_DISPLAY_BY_ID.items()
        if quest_id != RFD_FINALE_ID
    )


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


def expand_recipe_for_disaster_rows(rows: Sequence[ReleaseRow]) -> List[ReleaseRow]:
    expanded: List[ReleaseRow] = []
    for row in rows:
        if row.source_title != "Recipe for Disaster":
            expanded.append(row)
            continue
        for display_name, source_title in RFD_SUBQUESTS:
            expanded.append(
                ReleaseRow(
                    source_title=source_title,
                    display_name=display_name,
                    release_date=row.release_date,
                    cumulative_qp=row.cumulative_qp,
                    difficulty=row.difficulty,
                    former=row.former,
                    nr=row.nr,
                    update=row.update,
                )
            )
    return expanded


def _unescape_kotlin_string(value: str) -> str:
    try:
        return bytes(value, "utf-8").decode("unicode_escape")
    except UnicodeDecodeError:
        return value


def clean_journal_line(value: str) -> str:
    text = _unescape_kotlin_string(value)
    text = re.sub(r"</?col(?:=[^>]*)?>", "", text)
    text = text.replace("<str>", "").replace("</str>", "")
    text = clean_markup(text)
    text = text.replace("QUEST COMPLETE!", "Quest complete!")
    return text.strip()


def parse_2011scape_journals() -> Dict[str, Tuple[Dict[str, object], ...]]:
    journals: Dict[str, Tuple[Dict[str, object], ...]] = {}
    if not SCAPE_2011_QUEST_IMPL_DIR.exists():
        return journals
    for path in sorted(SCAPE_2011_QUEST_IMPL_DIR.glob("*.kt")):
        text = path.read_text(encoding="utf-8")
        name_match = re.search(r'name\s*=\s*"([^"]+)"', text)
        if not name_match:
            continue
        quest_id = quest_id_from_name(_unescape_kotlin_string(name_match.group(1)))
        stages: List[Dict[str, object]] = []
        for stage_match in re.finditer(
            r"\b(\d+)\s*->\s*(?:\{[^{}]*)?QuestStage\s*\(\s*objectives\s*=\s*listOf\s*\((.*?)\)\s*,?\s*\)",
            text,
            flags=re.S,
        ):
            stage = parse_int(stage_match.group(1), 0)
            if stage <= 0:
                continue
            lines = tuple(
                line
                for line in (clean_journal_line(match.group(1)) for match in re.finditer(r'"((?:\\.|[^"])*)"', stage_match.group(2)))
                if line
            )
            if lines:
                stages.append({"stage": stage, "journal": lines})
        if stages:
            journals[quest_id] = tuple(stages)
    return journals


_SCAPE_2011_JOURNALS = parse_2011scape_journals()


def extract_reward_items(reward_html: str) -> List[Dict[str, object]]:
    parser = RewardListExtractor()
    parser.feed(reward_html)
    return parser.items


def reward_payload_html(reward_html: str) -> str:
    navbox = re.search(r"<table\b[^>]*\bnavbox\b", reward_html, flags=re.I)
    if navbox:
        reward_html = reward_html[: navbox.start()]
    music_heading = re.search(
        r"(?:<h[34]\b[^>]*(?:id=\"[^\"]*Music[^\"]*\"|>.*?Music unlocked).*?</h[34]>|<dt>\s*Music unlocked\s*</dt>)",
        reward_html,
        flags=re.I | re.S,
    )
    if music_heading:
        return reward_html[: music_heading.start()]
    return reward_html


def reward_text_from_items(items: Sequence[Mapping[str, object]]) -> str:
    return "\n".join(str(item.get("text", "")) for item in items)


def _reward_item_category(item_name: str) -> str:
    lower = item_name.lower()
    if any(hint in lower for hint in _REWARD_ITEM_CATEGORY_HINTS):
        return "equipment"
    return "material"


def _quantity_word(value: str) -> int:
    return {
        "a": 1,
        "an": 1,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }.get(value.lower(), 0)


def _quantity_for_item(line: str, item_name: str, label: str) -> int:
    lower = line.lower()
    candidates = {item_name.lower(), label.lower()}
    if item_name.endswith("y"):
        candidates.add(f"{item_name[:-1].lower()}ies")
    else:
        candidates.add(f"{item_name.lower()}s")
    for candidate in sorted(candidates, key=len, reverse=True):
        if not candidate:
            continue
        match = re.search(rf"\b([0-9][0-9,]*)\s+(?:noted\s+)?{re.escape(candidate)}\b", lower, flags=re.I)
        if match:
            return parse_int(match.group(1), 1)
        word_match = re.search(
            rf"\b(a|an|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:noted\s+)?{re.escape(candidate)}\b",
            lower,
            flags=re.I,
        )
        if word_match:
            return _quantity_word(word_match.group(1)) or 1
    return 1


def _clean_anchor_item_name(anchor: Mapping[str, str]) -> str:
    title = clean_markup(anchor.get("title") or "")
    label = clean_markup(anchor.get("label") or "")
    name = title or label
    name = re.sub(r"\s+\((?:item|object|historical|quest)\)$", "", name, flags=re.I)
    if name.lower() == "coins":
        return "Coins"
    return name


def _clean_wikilink_name(target: str, label: str = "") -> str:
    name = clean_markup(target.split("#", 1)[0]) or clean_markup(label)
    name = re.sub(r"\s+\((?:item|object|historical|quest|monster)\)$", "", name, flags=re.I)
    if name.lower() in {"coins", "coin"}:
        return "Coins"
    return name[:1].upper() + name[1:] if name else ""


def _inside_parenthetical(text: str, index: int) -> bool:
    depth = 0
    for char in text[:index]:
        if char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
    return depth > 0


def _iter_wikilink_items(line: str) -> Iterator[Dict[str, object]]:
    for match in re.finditer(r"\[\[([^|\]#]+)(?:#[^|\]]*)?(?:\|([^\]]+))?\]\]", line):
        if _inside_parenthetical(line, match.start()):
            continue
        target = match.group(1)
        label = match.group(2) or target
        name = _clean_wikilink_name(target, label)
        if not name:
            continue
        yield {
            "item_name": name,
            "label": clean_markup(label) or name,
            "quantity": _quantity_for_item(clean_markup(line), name, clean_markup(label) or name),
            "start": match.start(),
            "end": match.end(),
        }


def _quest_detail_lines(value: str) -> Iterator[str]:
    for raw_line in re.split(r"[\r\n]+", value or ""):
        line = raw_line.strip()
        if not line:
            continue
        yield line.lstrip("*#:; ").strip()


def _skip_requirement_line(line: str) -> bool:
    lower = clean_markup(line).lower()
    if not lower:
        return True
    if lower.startswith("for ") and "members" in lower:
        return True
    if lower.startswith("to kill "):
        return True
    if "recommended" in lower:
        return True
    if "optional" in lower:
        return True
    if "only if" in lower:
        return True
    if "if you wish" in lower or "if you want" in lower or "if you do not" in lower:
        return True
    if "not necessary" in lower or "not required" in lower:
        return True
    return False


def _requirement_parse_segment(line: str) -> str:
    segment = re.split(r"\.\s+", line, maxsplit=1)[0]
    if " (found in " in segment.lower():
        segment = re.split(r"\s+\(found in\s+", segment, maxsplit=1, flags=re.I)[0]
    if " (obtained " in segment.lower() and "[[" not in segment.split(" (obtained ", 1)[0]:
        return segment
    return segment


def _is_tool_requirement(item_name: str, source_line: str) -> bool:
    lower = item_name.lower()
    line = clean_markup(source_line).lower()
    if lower in _QUEST_STAGE_TOOL_NAMES:
        return True
    if "toolbelt" in line:
        return True
    return False


def _merge_item_count(target: Dict[str, int], item_name: str, quantity: int) -> None:
    target[item_name] = max(target.get(item_name, 0), max(1, int(quantity)))


def _is_alternative_line(line: str, items: Sequence[Mapping[str, object]]) -> bool:
    if len(items) < 2:
        return False
    if len(items) > 3:
        return False
    lower = clean_markup(line).lower()
    return bool(re.search(r"\b(?:or|either|alternatively)\b", lower))


def _plain_requirement_item(line: str) -> Tuple[str, int]:
    if "[[" in line or "{{" in line or "'''" in line:
        return "", 0
    clean = clean_markup(line).strip()
    if "(" not in clean:
        return "", 0
    name = clean.split("(", 1)[0].strip(" -*:;. ")
    if not name or name.lower().startswith("for "):
        return "", 0
    quantity = 1
    quantity_match = re.match(r"([0-9][0-9,]*)\s+(.+)", name)
    if quantity_match:
        quantity = parse_int(quantity_match.group(1), 1)
        name = quantity_match.group(2)
    words = re.findall(r"[A-Za-z0-9']+", name)
    if not 1 <= len(words) <= 5:
        return "", 0
    return name[:1].upper() + name[1:], quantity


def parse_stage_item_requirements(items_wikitext: str) -> Dict[str, object]:
    required_inventory: Dict[str, int] = {}
    required_tools: Dict[str, int] = {}
    required_inventory_options: List[Tuple[Dict[str, int], ...]] = []

    in_recommended_block = False
    for line in _quest_detail_lines(items_wikitext):
        lower = clean_markup(line).lower()
        if "recommended" in lower:
            in_recommended_block = True
            continue
        if in_recommended_block:
            continue
        if _skip_requirement_line(line):
            continue
        parse_line = _requirement_parse_segment(line)
        items = tuple(
            item
            for item in _iter_wikilink_items(parse_line)
            if str(item["item_name"]).lower() not in _QUEST_REQUIREMENT_LINK_SKIP_TITLES
        )
        coin_match = re.search(r"\b([0-9][0-9,]*)\s+coins?\b", clean_markup(parse_line), flags=re.I)
        if coin_match and items and re.search(r"\b(?:or|either|alternatively)\b", clean_markup(parse_line), flags=re.I):
            options = [{"Coins": parse_int(coin_match.group(1), 1)}]
            for item in items:
                item_name = str(item["item_name"])
                if item_name == "Coins" or _is_tool_requirement(item_name, line):
                    continue
                candidate = {item_name: int(item.get("quantity", 1) or 1)}
                if candidate not in options:
                    options.append(candidate)
            if options:
                required_inventory_options.append(tuple(options))
            continue
        if not items:
            item_name, quantity = _plain_requirement_item(parse_line)
            if item_name:
                if _is_tool_requirement(item_name, line):
                    _merge_item_count(required_tools, item_name, quantity)
                else:
                    _merge_item_count(required_inventory, item_name, quantity)
            if coin_match:
                _merge_item_count(required_inventory, "Coins", parse_int(coin_match.group(1), 1))
            continue
        if _is_alternative_line(parse_line, items):
            options = []
            for item in items:
                item_name = str(item["item_name"])
                if _is_tool_requirement(item_name, line):
                    continue
                options.append({item_name: int(item.get("quantity", 1) or 1)})
            if options:
                required_inventory_options.append(tuple(options))
            continue
        for item in items:
            item_name = str(item["item_name"])
            quantity = int(item.get("quantity", 1) or 1)
            if _is_tool_requirement(item_name, line):
                _merge_item_count(required_tools, item_name, quantity)
            else:
                _merge_item_count(required_inventory, item_name, quantity)

    return {
        "required_inventory": required_inventory,
        "required_tools": required_tools,
        "required_inventory_options": tuple(required_inventory_options),
    }


def _npc_file_display_name(path: Path) -> Tuple[str, int]:
    stem = path.stem.replace(".plugin", "")
    level = 0
    match = re.search(r"_(?:level|lvl|lv)_?(\d+)", stem, flags=re.I)
    if match:
        level = parse_int(match.group(1), 0)
        stem = stem[: match.start()] + stem[match.end() :]
    name = re.sub(r"[_\s]+", " ", stem).strip()
    return name.title(), level


def _normalize_npc_lookup_name(name: str) -> str:
    normalized = name.lower().replace("&", "and")
    normalized = re.sub(r"\([^)]*\)", "", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return normalized.strip()


NPC_NAME_ALIASES: Mapping[str, Tuple[str, ...]] = {
    "poisonous spider": ("poison spider",),
}


def _singularize_npc_token(token: str) -> str:
    if len(token) > 4 and token.endswith("ies"):
        return f"{token[:-3]}y"
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _npc_lookup_name_variants(display_name: str) -> Tuple[str, ...]:
    normalized = _normalize_npc_lookup_name(display_name)
    if not normalized:
        return ()
    variants = [normalized]
    variants.extend(NPC_NAME_ALIASES.get(normalized, ()))

    tokens = normalized.split()
    for index, token in enumerate(tokens):
        singular = _singularize_npc_token(token)
        if singular == token:
            continue
        candidate_tokens = list(tokens)
        candidate_tokens[index] = singular
        variants.append(" ".join(candidate_tokens))

    seen = set()
    ordered = []
    for variant in variants:
        if variant and variant not in seen:
            seen.add(variant)
            ordered.append(variant)
    return tuple(ordered)


def _token_sequence_contains(haystack: str, needle: str) -> bool:
    haystack_tokens = haystack.split()
    needle_tokens = needle.split()
    if not haystack_tokens or not needle_tokens or len(needle_tokens) > len(haystack_tokens):
        return False
    for index in range(0, len(haystack_tokens) - len(needle_tokens) + 1):
        if haystack_tokens[index : index + len(needle_tokens)] == needle_tokens:
            return True
    return False


def _parse_kts_assignment_int(block: str, key: str) -> Optional[int]:
    match = re.search(rf"\b{re.escape(key)}\s*=\s*(-?\d+)", block)
    if not match:
        return None
    return parse_int(match.group(1), 0)


def _load_local_npc_stats() -> Dict[Tuple[str, int], Dict[str, object]]:
    if not SCAPE_2011_NPC_DEFINITION_DIR.exists():
        return {}
    rows: Dict[Tuple[str, int], Dict[str, object]] = {}
    stat_keys = ("hitpoints", "attack", "strength", "defence", "magic", "ranged")
    bonus_keys = (
        "attackStab",
        "attackSlash",
        "attackCrush",
        "attackMagic",
        "attackRanged",
        "defenceStab",
        "defenceSlash",
        "defenceCrush",
        "defenceMagic",
        "defenceRanged",
    )
    for path in SCAPE_2011_NPC_DEFINITION_DIR.rglob("*.plugin.kts"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")
        if "set_combat_def" not in text:
            continue
        display_name, level = _npc_file_display_name(path)
        stats_block = re.search(r"\bstats\s*\{(?P<body>.*?)\n\s*\}", text, flags=re.S)
        configs_block = re.search(r"\bconfigs\s*\{(?P<body>.*?)\n\s*\}", text, flags=re.S)
        bonuses_block = re.search(r"\bbonuses\s*\{(?P<body>.*?)\n\s*\}", text, flags=re.S)
        stats = {}
        if stats_block:
            for key in stat_keys:
                value = _parse_kts_assignment_int(stats_block.group("body"), key)
                if value is not None:
                    stats[key] = value
        bonuses = {}
        if bonuses_block:
            for key in bonus_keys:
                value = _parse_kts_assignment_int(bonuses_block.group("body"), key)
                if value is not None:
                    bonuses[key] = value
        configs = {}
        if configs_block:
            attack_speed = _parse_kts_assignment_int(configs_block.group("body"), "attackSpeed")
            if attack_speed is not None:
                configs["attack_speed"] = attack_speed
            style_match = re.search(r"\battackStyle\s*=\s*StyleType\.([A-Z_]+)", configs_block.group("body"))
            if style_match:
                configs["attack_style"] = style_match.group(1).lower()
        if stats or bonuses or configs:
            key = (_normalize_npc_lookup_name(display_name), level)
            rows[key] = {
                "display_name": display_name,
                "level": level,
                "stats": stats,
                "bonuses": bonuses,
                "configs": configs,
                "source": str(path),
            }
    return rows


_LOCAL_NPC_STATS: Optional[Dict[Tuple[str, int], Dict[str, object]]] = None


def _local_npc_stats() -> Dict[Tuple[str, int], Dict[str, object]]:
    global _LOCAL_NPC_STATS
    if _LOCAL_NPC_STATS is None:
        _LOCAL_NPC_STATS = _load_local_npc_stats()
    return _LOCAL_NPC_STATS


def _matching_local_npc_stats(display_name: str, level: int) -> Dict[str, object]:
    stats = _local_npc_stats()
    for normalized in _npc_lookup_name_variants(display_name):
        key = (normalized, level)
        if key in stats:
            return stats[key]
    if level:
        search_variants = _npc_lookup_name_variants(display_name)
        loose = [
            value
            for (name, row_level), value in stats.items()
            if row_level == level
            and any(
                _token_sequence_contains(name, variant) or _token_sequence_contains(variant, name)
                for variant in search_variants
            )
        ]
        if len(loose) == 1:
            return loose[0]
    return {}


def _parse_optional_int(value: object) -> Optional[int]:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        match = re.search(r"-?\d+", value)
        if match:
            return parse_int(match.group(0), 0)
    return None


def _combat_payload_attack_style(configs: Mapping[str, object]) -> str:
    attack_style = str(configs.get("attack_style", "")).lower()
    if attack_style in {"range", "ranged"}:
        return "ranged"
    if attack_style in {"magic", "melee"}:
        return attack_style
    return ""


def _combat_payload_has_resolver_stats(stats: Mapping[str, object], configs: Mapping[str, object]) -> bool:
    style = _combat_payload_attack_style(configs)
    required = {
        "magic": ("hitpoints", "defence", "magic"),
        "ranged": ("hitpoints", "defence", "ranged"),
    }.get(style, ("hitpoints", "attack", "strength", "defence"))
    if all((_parse_optional_int(stats.get(key)) or 0) > 0 for key in required):
        return True
    if style:
        melee_fallback = ("hitpoints", "attack", "strength", "defence")
        return all((_parse_optional_int(stats.get(key)) or 0) > 0 for key in melee_fallback)
    return False


def _load_darkan_beast_stats() -> Dict[int, Dict[str, int]]:
    if not DARKAN_BEASTS_PATH.exists():
        return {}
    rows: Dict[int, Dict[str, int]] = {}
    for line in DARKAN_BEASTS_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        npc_id = _parse_optional_int(data.get("id"))
        if npc_id is None:
            continue
        stats: Dict[str, int] = {}
        for source_key, stat_key in (
            ("attack", "attack"),
            ("defence", "defence"),
            ("magic", "magic"),
            ("ranged", "ranged"),
        ):
            value = _parse_optional_int(data.get(source_key))
            if value is not None:
                stats[stat_key] = value
        if stats:
            rows[npc_id] = stats
    return rows


_DARKAN_BEAST_STATS: Optional[Dict[int, Dict[str, int]]] = None


def _darkan_beast_stats() -> Dict[int, Dict[str, int]]:
    global _DARKAN_BEAST_STATS
    if _DARKAN_BEAST_STATS is None:
        _DARKAN_BEAST_STATS = _load_darkan_beast_stats()
    return _DARKAN_BEAST_STATS


_DARKAN_NPC_LIST: Optional[Tuple[Dict[int, Dict[str, object]], Dict[str, Tuple[int, ...]]]] = None


def _load_darkan_npc_list_uncached() -> Tuple[Dict[int, Dict[str, object]], Dict[str, Tuple[int, ...]]]:
    if not DARKAN_NPC_LIST_PATH.exists():
        return {}, {}
    by_id: Dict[int, Dict[str, object]] = {}
    levels_by_name: Dict[str, set] = {}
    row_re = re.compile(r"^\s*(\d+)\s+-\s+(.*?)\s+\((\d+)\)\s*$")
    for line in DARKAN_NPC_LIST_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        match = row_re.match(line)
        if not match:
            continue
        npc_id = parse_int(match.group(1), -1)
        name = clean_markup(match.group(2)).strip()
        level = parse_int(match.group(3), 0)
        if npc_id < 0 or not name:
            continue
        by_id[npc_id] = {"display_name": name, "level": level}
        if level > 0:
            levels_by_name.setdefault(_normalize_npc_lookup_name(name), set()).add(level)
    return by_id, {name: tuple(sorted(levels)) for name, levels in levels_by_name.items()}


def _load_darkan_npc_list() -> Tuple[Dict[int, Dict[str, object]], Dict[str, Tuple[int, ...]]]:
    global _DARKAN_NPC_LIST
    if _DARKAN_NPC_LIST is None:
        _DARKAN_NPC_LIST = _load_darkan_npc_list_uncached()
    return _DARKAN_NPC_LIST


def _darkan_beast_stats_for_combatdef(data: Mapping[str, object]) -> Dict[str, int]:
    beast_stats_by_id = _darkan_beast_stats()
    by_id, levels_by_name = _load_darkan_npc_list()
    candidates: List[Dict[str, int]] = []

    for raw_id in data.get("ids", ()) or ():
        npc_id = _parse_optional_int(raw_id)
        if npc_id is None:
            continue
        stats = beast_stats_by_id.get(npc_id)
        if stats:
            candidates.append(stats)

    if not candidates:
        for raw_name in data.get("names", ()) or ():
            if not isinstance(raw_name, str):
                continue
            display_name = clean_markup(raw_name).strip()
            levels = levels_by_name.get(_normalize_npc_lookup_name(display_name), ())
            if len(levels) != 1:
                continue
            level = levels[0]
            for npc_id, npc in by_id.items():
                if int(npc["level"]) != level:
                    continue
                if _normalize_npc_lookup_name(str(npc["display_name"])) != _normalize_npc_lookup_name(display_name):
                    continue
                stats = beast_stats_by_id.get(npc_id)
                if stats:
                    candidates.append(stats)

    signatures = {json.dumps(candidate, sort_keys=True) for candidate in candidates}
    if len(signatures) != 1:
        return {}
    return dict(candidates[0])


def _darkan_beast_stats_for_name_level(display_name: str, level: int) -> Dict[str, int]:
    if level <= 0:
        return {}
    beast_stats_by_id = _darkan_beast_stats()
    by_id, _ = _load_darkan_npc_list()
    normalized_name = _normalize_npc_lookup_name(display_name)
    candidates = [
        stats
        for npc_id, npc in by_id.items()
        if int(npc["level"]) == level
        and _normalize_npc_lookup_name(str(npc["display_name"])) == normalized_name
        for stats in (beast_stats_by_id.get(npc_id),)
        if stats
    ]
    signatures = {json.dumps(candidate, sort_keys=True) for candidate in candidates}
    if len(signatures) != 1:
        return {}
    return dict(candidates[0])


def _darkan_combat_payload(
    path: Path,
    data: Optional[Mapping[str, object]] = None,
    *,
    match_name: str = "",
    match_level: int = 0,
) -> Optional[Dict[str, object]]:
    if data is None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return None
    levels = data.get("combatLevels")
    hitpoints = _parse_optional_int(data.get("hitpoints"))
    if not hitpoints:
        return None
    stats: Dict[str, int] = {
        "hitpoints": hitpoints,
    }
    if isinstance(levels, Mapping):
        for source_key, stat_key in (
            ("ATTACK", "attack"),
            ("STRENGTH", "strength"),
            ("DEFENSE", "defence"),
            ("MAGE", "magic"),
            ("RANGE", "ranged"),
        ):
            value = _parse_optional_int(levels.get(source_key))
            if value is not None:
                stats[stat_key] = value

    configs: Dict[str, object] = {}
    max_hit = _parse_optional_int(data.get("maxHit"))
    if max_hit is not None:
        configs["max_hit"] = max_hit
    attack_range = _parse_optional_int(data.get("attackRange"))
    if attack_range is not None:
        configs["attack_range"] = attack_range
    attack_style = data.get("attackStyle")
    if isinstance(attack_style, str) and attack_style:
        configs["attack_style"] = attack_style.lower()
    attack_bonus = data.get("attackBonus")
    if isinstance(attack_bonus, str) and attack_bonus:
        configs["attack_bonus"] = attack_bonus.lower()
    aggressiveness = data.get("agressivenessType") or data.get("aggressivenessType")
    if isinstance(aggressiveness, str) and aggressiveness:
        configs["aggressiveness_type"] = aggressiveness.lower()
    beast_stats = _darkan_beast_stats_for_combatdef(data)
    if not beast_stats and match_name and match_level:
        beast_stats = _darkan_beast_stats_for_name_level(match_name, match_level)
    merged_beast_stats = False
    if beast_stats:
        for key, value in beast_stats.items():
            if _parse_optional_int(stats.get(key)) in (None, 0) and value > 0:
                stats[key] = value
                merged_beast_stats = True
    if not _combat_payload_has_resolver_stats(stats, configs):
        return None
    source = str(path)
    if merged_beast_stats:
        source = f"{source}; {DARKAN_BEASTS_PATH}"
    return {"stats": stats, "configs": configs, "source": source}


def _darkan_name_level_pairs(
    data: Mapping[str, object],
    by_id: Mapping[int, Mapping[str, object]],
    levels_by_name: Mapping[str, Tuple[int, ...]],
) -> Tuple[Tuple[str, int], ...]:
    pairs = []
    seen = set()

    def add_pair(display_name: str, level: int) -> None:
        if not display_name or level <= 0:
            return
        key = (_normalize_npc_lookup_name(display_name), level)
        if key in seen:
            return
        seen.add(key)
        pairs.append((display_name, level))

    for raw_id in data.get("ids", ()) or ():
        npc_id = _parse_optional_int(raw_id)
        if npc_id is None:
            continue
        npc = by_id.get(npc_id)
        if npc:
            add_pair(str(npc["display_name"]), int(npc["level"]))

    for raw_name in data.get("names", ()) or ():
        if not isinstance(raw_name, str):
            continue
        display_name = clean_markup(raw_name).strip()
        for level in levels_by_name.get(_normalize_npc_lookup_name(display_name), ()):
            add_pair(display_name, level)

    return tuple(pairs)


def _load_darkan_npc_stats() -> Dict[Tuple[str, int], Dict[str, object]]:
    if not DARKAN_NPC_COMBATDEF_DIR.exists():
        return {}
    by_id, levels_by_name = _load_darkan_npc_list()
    rows: Dict[Tuple[str, int], List[Dict[str, object]]] = {}
    for path in DARKAN_NPC_COMBATDEF_DIR.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        for display_name, level in _darkan_name_level_pairs(data, by_id, levels_by_name):
            payload = _darkan_combat_payload(path, data, match_name=display_name, match_level=level)
            if not payload:
                continue
            key = (_normalize_npc_lookup_name(display_name), level)
            rows.setdefault(key, []).append(
                {
                    "display_name": display_name,
                    "level": level,
                    "stats": payload["stats"],
                    "bonuses": {},
                    "configs": payload["configs"],
                    "source": payload["source"],
                }
            )

    unambiguous: Dict[Tuple[str, int], Dict[str, object]] = {}
    for key, candidates in rows.items():
        groups: Dict[Tuple[str, str], List[Dict[str, object]]] = {}
        for candidate in candidates:
            signature = (
                json.dumps(candidate["stats"], sort_keys=True),
                json.dumps(candidate["configs"], sort_keys=True),
            )
            groups.setdefault(signature, []).append(candidate)
        if len(groups) == 1:
            unique_sources = sorted({str(candidate["source"]) for candidate in candidates})
            row = dict(sorted(candidates, key=lambda candidate: str(candidate["source"]))[0])
            row["source"] = "; ".join(unique_sources)
            unambiguous[key] = row
    return unambiguous


_DARKAN_NPC_STATS: Optional[Dict[Tuple[str, int], Dict[str, object]]] = None


def _darkan_npc_stats() -> Dict[Tuple[str, int], Dict[str, object]]:
    global _DARKAN_NPC_STATS
    if _DARKAN_NPC_STATS is None:
        _DARKAN_NPC_STATS = _load_darkan_npc_stats()
    return _DARKAN_NPC_STATS


def _matching_darkan_npc_stats(display_name: str, level: int) -> Dict[str, object]:
    if level <= 0:
        return {}
    stats = _darkan_npc_stats()
    for normalized in _npc_lookup_name_variants(display_name):
        row = stats.get((normalized, level))
        if row:
            return row
    return {}


def _matching_source_npc_stats(display_name: str, level: int) -> Dict[str, object]:
    local_stats = _matching_local_npc_stats(display_name, level)
    if local_stats:
        return local_stats
    return _matching_darkan_npc_stats(display_name, level)


def _skip_combat_line(line: str) -> bool:
    lower = clean_markup(line).lower()
    if not lower:
        return True
    if not _combat_level_from_line(line) and lower.endswith(":"):
        return True
    if not _combat_level_from_line(line) and lower in {"the 6 barrows brothers"}:
        return True
    if lower.startswith("note:") or lower.startswith("see "):
        return True
    if lower in {"none", "n/a", "no"} or lower.startswith("none"):
        return True
    if "see the source guide" in lower:
        return True
    if "optional" in lower or "not required" in lower:
        return True
    if "possibly" in lower:
        return True
    if "if you join" in lower or "can kill" in lower or "can still help" in lower:
        return True
    if "evade" in lower or "avoid" in lower:
        return True
    if "no direct boss" in lower:
        return True
    return False


def _combat_level_from_line(line: str) -> int:
    match = re.search(r"\blevel\s*[- ]?\s*(\d+)", line, flags=re.I)
    if not match:
        match = re.search(r"\blvl\s*[- ]?\s*(\d+)", line, flags=re.I)
    if not match:
        match = re.search(r"\((\d+)\)", line)
    if not match:
        return 0
    return parse_int(match.group(1), 0)


def _combat_quantity_from_line(line: str) -> int:
    clean = clean_markup(line)
    match = re.match(r"\s*(\d+)\s*x\b", clean, flags=re.I)
    if match:
        return parse_int(match.group(1), 1)
    match = re.match(r"\s*(\d+)\b", clean)
    if match:
        return parse_int(match.group(1), 1)
    match = re.match(r"\s*at least\s+(\d+)\b", clean, flags=re.I)
    if match:
        return parse_int(match.group(1), 1)
    match = re.match(
        r"\s*(?:at least\s+)?(a|an|one|two|three|four|five|six|seven|eight|nine|ten)\b",
        clean,
        flags=re.I,
    )
    if match:
        return _quantity_word(match.group(1)) or 1
    match = re.search(r"\bx\s*(\d+)\b", clean, flags=re.I)
    if match:
        return parse_int(match.group(1), 1)
    return 1


def _combat_display_name_from_line(line: str) -> str:
    links = tuple(_iter_wikilink_items(line))
    if links:
        return str(links[0]["item_name"])
    clean = clean_markup(line)
    clean = re.sub(r"^\s*(?:level|lvl)\s*[- ]?\s*\d+(?:\s*[-–]\s*\d+)?\s+", "", clean, flags=re.I)
    clean = re.sub(
        r"^\s*(?:(?:at least\s+)?(?:\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|several)\s+)?",
        "",
        clean,
        flags=re.I,
    )
    clean = re.split(r"\s*(?:[-–]\s*)?\(?\s*(?:level|lvl)\b", clean, maxsplit=1, flags=re.I)[0]
    clean = clean.strip(" -*:;,.()")
    return clean[:1].upper() + clean[1:] if clean else "Combat encounter"


def parse_combat_encounters(combat_wikitext: str, source: str, quest_id: str) -> Tuple[Dict[str, object], ...]:
    encounters = []
    seen = set()
    optional_block = False
    for line in _quest_detail_lines(combat_wikitext):
        clean_line = clean_markup(line)
        lower_line = clean_line.lower()
        if "optional" in lower_line and ("kills" in lower_line or not _combat_level_from_line(line)):
            optional_block = True
            continue
        if optional_block and _combat_level_from_line(line):
            continue
        if _skip_combat_line(line):
            continue
        display_name = _combat_display_name_from_line(line)
        if not display_name:
            continue
        level = _combat_level_from_line(line)
        if level <= 0 and len(clean_markup(line)) > 80:
            continue
        quantity = _combat_quantity_from_line(line)
        source_stats = _matching_source_npc_stats(display_name, level)
        base_id = quest_id_from_name(f"{quest_id} {display_name} {level or len(encounters) + 1}")
        encounter_id = base_id
        suffix = 2
        while encounter_id in seen:
            encounter_id = f"{base_id}_{suffix}"
            suffix += 1
        seen.add(encounter_id)
        row: Dict[str, object] = {
            "encounter_id": encounter_id,
            "display_name": display_name,
            "level": level,
            "quantity": quantity,
            "source": source,
            "source_text": clean_markup(line),
        }
        if source_stats:
            row["npc_stats"] = source_stats.get("stats", {})
            row["npc_bonuses"] = source_stats.get("bonuses", {})
            row["npc_configs"] = source_stats.get("configs", {})
            row["npc_stats_source"] = source_stats.get("source", "")
        encounters.append(row)
    return tuple(encounters)


def _item_mentions_in_stage(stage: Mapping[str, object], item_names: Sequence[str]) -> bool:
    text = " ".join(str(line) for line in (stage.get("journal", ()) or ())).lower()
    for item_name in item_names:
        lower = item_name.lower()
        if lower and lower in text:
            return True
        words = [word for word in re.findall(r"[a-z0-9]+", lower) if len(word) > 2]
        if words and all(word in text for word in words[:3]):
            return True
    return False


def _infer_item_requirement_stage(journal_stages: Sequence[Mapping[str, object]], item_names: Sequence[str]) -> int:
    for stage in journal_stages:
        if not isinstance(stage, Mapping):
            continue
        if _item_mentions_in_stage(stage, item_names):
            return parse_int(stage.get("stage"), 1)
    return 1


def build_stage_requirements(
    *,
    quest_id: str,
    display_name: str,
    stages: int,
    journal_stages: Sequence[Mapping[str, object]],
    journal_source: str,
    item_requirements: Mapping[str, object],
    combat_encounters: Sequence[Mapping[str, object]],
    source: str,
) -> Tuple[Dict[str, object], ...]:
    rows_by_stage: Dict[int, Dict[str, object]] = {}

    def merge_sources(existing: str, new_source: str) -> str:
        if not new_source:
            return existing
        parts = [part.strip() for part in existing.split(";") if part.strip()]
        if new_source not in parts:
            parts.append(new_source)
        return "; ".join(parts)

    def row_for_stage(stage: int, description: str) -> Dict[str, object]:
        if stage not in rows_by_stage:
            rows_by_stage[stage] = {
                "stage": stage,
                "description": description,
                "required_inventory": {},
                "required_tools": {},
                "required_inventory_options": (),
                "required_actions": (),
                "combat_encounters": (),
                "source": source,
            }
        return rows_by_stage[stage]

    for stage_row in journal_stages:
        if not isinstance(stage_row, Mapping):
            continue
        if stage_row.get("source_kind") not in {"quick_guide_checklist", "walkthrough_prose", "source_page_checkpoint"}:
            continue
        stage = max(1, min(stages, parse_int(stage_row.get("stage"), 1)))
        has_objective = any(
            line
            and "quest complete" not in line.lower()
            and not line.lower().startswith("i made progress on ")
            for line in (
                clean_journal_line(str(raw_line))
                for raw_line in (stage_row.get("journal", ()) or ())
            )
        )
        if not has_objective:
            continue
        row = row_for_stage(stage, "Generated from source-backed quest stage checkpoints.")
        existing_actions = tuple(row.get("required_actions", ()))
        action = f"Complete {display_name} stage {stage} objective"
        row["required_actions"] = tuple(dict.fromkeys((*existing_actions, action)))
        row["source"] = merge_sources(str(row.get("source", "")), journal_source)

    required_inventory = item_requirements.get("required_inventory", {})
    if isinstance(required_inventory, Mapping):
        for item_name, quantity in required_inventory.items():
            normalized_item_name = str(item_name)
            stage = (
                LIGHT_SOURCE_REQUIREMENT_STAGE_BY_QUEST.get(quest_id)
                if normalized_item_name in {"Light source", "Light sources"}
                else None
            ) or _infer_item_requirement_stage(journal_stages, (normalized_item_name,))
            row = row_for_stage(stage, "Generated from pre-EOC Quest details item requirements.")
            row["required_inventory"][normalized_item_name] = int(quantity)

    required_tools = item_requirements.get("required_tools", {})
    if isinstance(required_tools, Mapping):
        for item_name, quantity in required_tools.items():
            normalized_item_name = str(item_name)
            stage = (
                LIGHT_SOURCE_REQUIREMENT_STAGE_BY_QUEST.get(quest_id)
                if normalized_item_name in {"Light source", "Light sources"}
                else None
            ) or _infer_item_requirement_stage(journal_stages, (normalized_item_name,))
            row = row_for_stage(stage, "Generated from pre-EOC Quest details item requirements.")
            row["required_tools"][normalized_item_name] = int(quantity)

    option_groups = item_requirements.get("required_inventory_options", ())
    if isinstance(option_groups, Iterable) and not isinstance(option_groups, (str, bytes, Mapping)):
        for option_group in option_groups:
            if not isinstance(option_group, Iterable) or isinstance(option_group, (str, bytes, Mapping)):
                continue
            options = tuple(option for option in option_group if isinstance(option, Mapping))
            if not options:
                continue
            item_names = tuple(str(name) for option in options for name in option)
            stage = _infer_item_requirement_stage(journal_stages, item_names)
            row = row_for_stage(stage, "Generated from pre-EOC Quest details item alternatives.")
            row["required_inventory_options"] = tuple(row["required_inventory_options"]) + (options,)

    if combat_encounters:
        stage = max(1, min(stages, stages - 1 if stages > 1 else 1))
        row = row_for_stage(stage, "Generated combat gate from pre-EOC Quest details.")
        row["combat_encounters"] = tuple(combat_encounters)

    clean_rows = []
    for stage, row in sorted(rows_by_stage.items()):
        has_light_source_requirement = False
        for requirement_key in ("required_inventory", "required_tools"):
            for pseudo_item in ("Light source", "Light sources"):
                if pseudo_item in row[requirement_key]:
                    row[requirement_key].pop(pseudo_item)
                    has_light_source_requirement = True
        if has_light_source_requirement and quest_id not in LIGHT_SOURCE_STAGE_BLOCKED_QUESTS:
            allowed_items = (
                ("Bullseye lantern (lit)",)
                if quest_id == "tears_of_guthix"
                else LIT_LIGHT_SOURCE_ITEMS
            )
            row["required_inventory_options"] = tuple(row["required_inventory_options"]) + (
                tuple({item_name: 1} for item_name in allowed_items),
            )
            row["source"] = merge_sources(str(row.get("source", "")), LIGHT_SOURCES_SOURCE)
        if (
            not row["required_inventory"]
            and not row["required_tools"]
            and not row["required_inventory_options"]
            and not row["required_actions"]
            and not row["combat_encounters"]
        ):
            continue
        clean_rows.append(row)

    # The generic item parser cannot distinguish an item-state transformation
    # from an alternatives list. These two source-backed lantern stages require
    # the exact producible states used by the AnkiScape inventory graph.
    if quest_id == "tears_of_guthix":
        for row in clean_rows:
            if row["stage"] == 2:
                row["required_inventory"].update(
                    {"Bullseye lantern (empty)": 1, "Sapphire": 1}
                )
                row["required_inventory_options"] = ()
            elif row["stage"] == 3:
                row["required_inventory"]["Sapphire lantern (lit)"] = 1
    elif quest_id == "while_guthix_sleeps":
        for row in clean_rows:
            if row["stage"] == 6 and "Sapphire lantern" in row["required_inventory"]:
                row["required_inventory"].pop("Sapphire lantern")
                row["required_inventory"]["Sapphire lantern (lit)"] = 1
    return tuple(clean_rows)


def parse_item_rewards(reward_items: Sequence[Mapping[str, object]], source: str) -> Tuple[Dict[str, object], ...]:
    rewards: Dict[str, Dict[str, object]] = {}
    music_track_tail = 0
    for item in reward_items:
        line = str(item.get("text", "")).strip()
        lower = line.lower()
        if not line:
            continue
        has_explicit_quantity = bool(
            re.match(r"(?:[0-9][0-9,]*|a|an|one|two|three|four|five|six|seven|eight|nine|ten)\b", lower)
            or re.search(r"\b[0-9][0-9,]*\s+coins?\b", lower)
        )
        if music_track_tail and not has_explicit_quantity:
            music_track_tail -= 1
            continue
        if lower.startswith("music unlocked"):
            music_track_tail = 10
            continue
        if "squeal of fortune" in lower or "treasure hunter" in lower:
            continue
        if "quest point" in lower or re.search(r"\b(xp|experience)\b", lower):
            if "coin" not in lower and "lamp" not in lower:
                continue
        if "lamp" in lower or "experience reward" in lower:
            continue
        if any(lower.startswith(prefix) for prefix in _UNLOCK_REWARD_PREFIXES):
            continue
        anchors = item.get("anchors", ())
        if not isinstance(anchors, tuple):
            anchors = ()
        item_name = ""
        label = ""
        for anchor in anchors:
            if not isinstance(anchor, Mapping):
                continue
            candidate = _clean_anchor_item_name(anchor)
            if not candidate or candidate.lower() in _REWARD_ITEM_SKIP_TITLES:
                continue
            item_name = candidate
            label = clean_markup(anchor.get("label") or candidate)
            break
        if not item_name:
            coin_match = re.search(r"\b([0-9][0-9,]*)\s+coins?\b", line, flags=re.I)
            if coin_match:
                item_name = "Coins"
                label = "coins"
            elif (
                len(line) <= 70
                and not any(lower.startswith(prefix) for prefix in _UNLOCK_REWARD_PREFIXES)
                and has_explicit_quantity
            ):
                item_name = clean_markup(line)
                label = item_name
        if not item_name:
            continue
        quantity = _quantity_for_item(line, item_name, label)
        existing = rewards.get(item_name)
        if existing:
            existing["quantity"] = int(existing["quantity"]) + quantity
            continue
        rewards[item_name] = {
            "item_name": item_name,
            "quantity": quantity,
            "category": _reward_item_category(item_name),
            "source": source,
        }
    return tuple(rewards[name] for name in sorted(rewards))


def _skill_options_for_lamp(line: str) -> Tuple[str, ...]:
    lower = line.lower()
    options = []
    for key, (skill_id, display_name) in SKILLS.items():
        if key in {"combat", "defense"}:
            continue
        if re.search(rf"\b{re.escape(display_name.lower())}\b", lower):
            options.append(skill_id)
    explicit_options = tuple(sorted(set(options)))
    combat_options = ("attack", "constitution", "defense", "magic", "ranged", "strength", "summoning")
    if "combat skill" in lower or "combat lamp" in lower:
        if "other than prayer" in lower or "except prayer" in lower:
            return combat_options
        if len(explicit_options) > 1:
            return explicit_options
        return combat_options
    if explicit_options:
        return explicit_options
    if "any skill" in lower or "skill of your choice" in lower:
        return tuple(skill_id for skill_id, _ in sorted({value for key, value in SKILLS.items() if key != "combat"}))
    return ()


def _lamp_minimum_level(line: str) -> int:
    lower = line.lower()
    for pattern in (
        r"at least level\s+(\d+)",
        r"at or over level\s+(\d+)",
        r"level\s+(\d+)\s+or (?:above|higher|over)",
        r"level\s+(\d+)\+",
    ):
        match = re.search(pattern, lower)
        if match:
            return parse_int(match.group(1), 1)
    for pattern in (r"(?:above|over|higher than)\s+level\s+(\d+)", r"(?:above|over|higher than)\s+(\d+)"):
        match = re.search(pattern, lower)
        if match:
            return parse_int(match.group(1), 0) + 1
    return 1


def _lamp_count(line: str) -> int:
    lower = line.lower()
    match = re.search(r"\b([0-9]+)\s*×\s*[a-z ]*lamps?\b", lower)
    if match:
        return parse_int(match.group(1), 1)
    match = re.search(r"\b([0-9]+)\s+x\s+[a-z ]*lamps?\b", lower)
    if match:
        return parse_int(match.group(1), 1)
    match = re.search(r"\b([0-9]+)\s+wishes\s+each\b", lower)
    if match:
        return parse_int(match.group(1), 1)
    match = re.search(r"\b([0-9]+)\s+(?:[a-z]+\s+){0,3}lamps\b", lower)
    if match:
        return parse_int(match.group(1), 1)
    match = re.search(r"\b(a|an|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:[a-z]+\s+){0,3}lamps?\b", lower)
    if match:
        return _quantity_word(match.group(1)) or 1
    if "lamp" in lower:
        return 1
    return 0


def parse_lamp_rewards(reward_items: Sequence[Mapping[str, object]], source: str) -> Tuple[Dict[str, object], ...]:
    lamps: List[Dict[str, object]] = []
    for item in reward_items:
        line = str(item.get("text", "")).strip()
        lower = line.lower()
        if not line or "lamp" not in lower:
            continue
        amount_values = [parse_int(match, 0) for match in re.findall(r"\b([0-9][0-9,]*)\s+(?:xp|experience)\b", line, flags=re.I)]
        if not amount_values:
            continue
        amount = max(amount_values)
        count = _lamp_count(line)
        skill_options = _skill_options_for_lamp(line)
        if amount <= 0 or count <= 0 or not skill_options:
            continue
        lamps.append(
            {
                "display_name": "XP lamp",
                "quantity": count,
                "amount": amount,
                "skill_options": skill_options,
                "minimum_level": _lamp_minimum_level(line),
                "source": source,
                "source_text": clean_markup(line),
            }
        )
    return tuple(lamps)


def parse_unlock_rewards(reward_items: Sequence[Mapping[str, object]]) -> Tuple[str, ...]:
    unlocks = []
    for item in reward_items:
        line = clean_markup(str(item.get("text", "")))
        lower = line.lower()
        if not line:
            continue
        if any(lower.startswith(prefix) for prefix in _UNLOCK_REWARD_PREFIXES):
            unlocks.append(line)
    return tuple(dict.fromkeys(unlocks))


def _quick_guide_title(title: str, display_name: str) -> str:
    cleaned = re.sub(r"\s+\((historical|quest|miniquest)\)$", "", title, flags=re.I).strip()
    return f"{cleaned or display_name}/Quick guide"


def parse_quick_guide_lines(title: str, display_name: str) -> Tuple[Tuple[str, ...], str]:
    quick_title = _quick_guide_title(title, display_name)
    try:
        revision = fetch_wikitext(quick_title, before_cutoff=True)
    except RuntimeError:
        return (), ""
    if revision.fallback_current:
        return (), ""
    source = page_url(revision.title, revision.oldid)
    checklist_lines: List[str] = []
    for body in iter_templates(revision.content):
        if template_name(body) != "checklist":
            continue
        params = parse_template_params(body)
        raw = params.get("1") or ""
        for raw_line in raw.splitlines():
            if not raw_line.lstrip().startswith("*"):
                continue
            line = clean_markup(raw_line)
            line = re.sub(r"\{\{.*$", "", line).strip()
            if not line or "congratulations" in line.lower() or "quest complete" in line.lower():
                continue
            checklist_lines.append(line)
        if checklist_lines:
            break
    if checklist_lines:
        return tuple(dict.fromkeys(checklist_lines)), source

    try:
        quick_html = fetch_parsed_html(revision)
    except RuntimeError:
        return (), ""
    section = section_html(quick_html, "Walkthrough") or quick_html
    parser = QuickGuideExtractor()
    parser.feed(section)
    lines = []
    for line in parser.lines:
        cleaned = clean_markup(line)
        if cleaned and "congratulations" not in cleaned.lower() and "quest complete" not in cleaned.lower():
            lines.append(cleaned)
    return tuple(dict.fromkeys(lines)), source


def parse_walkthrough_prose_lines(page_html: str) -> Tuple[str, ...]:
    section = section_html(page_html, "Walkthrough")
    if not section:
        return ()
    parser = WalkthroughProseExtractor()
    parser.feed(section)
    lines = []
    for line in parser.lines:
        cleaned = clean_markup(line)
        lower = cleaned.lower()
        if not cleaned or "lua error" in lower or "quest complete" in lower:
            continue
        lines.append(cleaned)
    return tuple(dict.fromkeys(lines))


def grouped_journal_stages(lines: Sequence[str], stages: int, display_name: str, source_kind: str) -> Tuple[Dict[str, object], ...]:
    clean_lines = [clean_journal_line(line) for line in lines if clean_journal_line(line)]
    if not clean_lines:
        return ()
    stage_count = max(1, stages)
    groups: List[List[str]] = [[] for _ in range(stage_count)]
    for index, line in enumerate(clean_lines):
        group_index = min(stage_count - 1, int(index * stage_count / max(1, len(clean_lines))))
        groups[group_index].append(line)
    rows = []
    for index, group in enumerate(groups, start=1):
        if not group:
            group = [f"I made progress on {display_name}."]
        if index == stage_count and not any("quest complete" in line.lower() for line in group):
            group = [*group, "Quest complete!"]
        rows.append({"stage": index, "journal": tuple(group), "source_kind": source_kind})
    return tuple(rows)


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
    reward_revision = revision
    if not reward_html:
        reward_html = section_html(parsed_html, "Rewards")
    if not reward_html:
        try:
            reward_revision = fetch_wikitext(_quick_guide_title(row.source_title, row.display_name), before_cutoff=False)
            reward_html = section_html(fetch_parsed_html(reward_revision), "Reward")
            if not reward_html:
                reward_html = section_html(fetch_parsed_html(reward_revision), "Rewards")
        except RuntimeError:
            reward_revision = revision
            reward_html = ""
    reward_html = reward_payload_html(reward_html)
    reward_items = extract_reward_items(reward_html)
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
    required_quests = dedupe_pairs([*required_quests, *rfd_manual_prerequisites(quest_id)])

    required_skills = parse_skill_requirements(requirements_wikitext, parsed_html)
    required_quest_points = parse_required_quest_points(requirements_wikitext)
    point_reward = parse_reward_points(reward_text) or fallback_reward_points(included_rows, row, index)
    xp_rewards = parse_xp_rewards(reward_text)
    item_rewards = parse_item_rewards(reward_items, page_url(reward_revision.title, reward_revision.oldid))
    lamp_rewards = parse_lamp_rewards(reward_items, page_url(reward_revision.title, reward_revision.oldid))
    unlocks = parse_unlock_rewards(reward_items)

    requirement_labels: List[str] = []
    requirement_labels.extend(display_name for _, display_name in required_quests)
    if required_quest_points:
        requirement_labels.append(f"{required_quest_points} Quest Points")
    requirement_labels.extend(f"{display_name} {level}" for _, display_name, level in required_skills)

    start_point = clean_markup(details.get("start", ""))
    source_url = page_url(revision.title, revision.oldid)
    combat_wikitext = details.get("kills", "") or details.get("combat", "")
    combat = clean_markup(combat_wikitext)
    length = canonical_length(details.get("length", ""))
    local_journal = _SCAPE_2011_JOURNALS.get(quest_id)
    if local_journal:
        journal_stages = local_journal
        journal_source = str(SCAPE_2011_QUEST_IMPL_DIR)
        journal_source_kind = "2011scape_quest_stage"
        stages = max(parse_int(stage.get("stage"), 1) for stage in local_journal)
    else:
        stages = generated_stage_count(length)
        quick_lines, quick_source = parse_quick_guide_lines(row.source_title, row.display_name)
        if quick_lines:
            journal_stages = grouped_journal_stages(quick_lines, stages, row.display_name, "quick_guide_checklist")
            journal_source = quick_source
            journal_source_kind = "quick_guide_checklist"
        else:
            walkthrough_lines = parse_walkthrough_prose_lines(parsed_html)
            if walkthrough_lines:
                journal_stages = grouped_journal_stages(walkthrough_lines, stages, row.display_name, "walkthrough_prose")
                journal_source = page_url(revision.title, revision.oldid)
                journal_source_kind = "walkthrough_prose"
            else:
                checkpoint_lines = tuple(
                    f"Complete {row.display_name} stage {stage} objective using the pinned source guide."
                    for stage in range(1, stages + 1)
                )
                journal_stages = grouped_journal_stages(
                    checkpoint_lines,
                    stages,
                    row.display_name,
                    "source_page_checkpoint",
                )
                journal_source = page_url(revision.title, revision.oldid)
                journal_source_kind = "source_page_checkpoint"
    item_requirements = parse_stage_item_requirements(details.get("items", ""))
    combat_encounters = parse_combat_encounters(combat_wikitext, source_url, quest_id)
    stage_requirements = build_stage_requirements(
        quest_id=quest_id,
        display_name=row.display_name,
        stages=stages,
        journal_stages=journal_stages,
        journal_source=journal_source,
        item_requirements=item_requirements,
        combat_encounters=combat_encounters,
        source=source_url,
    )
    return {
        "id": quest_id,
        "display_name": row.display_name,
        "source_title": row.source_title,
        "source": source_url,
        "source_revision": revision.oldid,
        "source_timestamp": revision.timestamp,
        "source_fallback_current": revision.fallback_current,
        "reward_source": page_url(reward_revision.title, reward_revision.oldid),
        "release_source": RELEASE_LIST_SOURCE,
        "release_order": index + 1,
        "release_date": row.release_date.isoformat(),
        "members": parse_members(details.get("members", "Yes")),
        "difficulty": row.difficulty or clean_markup(details.get("difficulty", "Novice")),
        "length": length,
        "timeline": canonical_timeline(details.get("timeline") or details.get("age") or ""),
        "stages": stages,
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
        "item_rewards": item_rewards,
        "lamp_rewards": lamp_rewards,
        "unlocks": unlocks,
        "journal_stages": journal_stages,
        "journal_source": journal_source,
        "journal_source_kind": journal_source_kind,
        "stage_requirements": stage_requirements,
    }


def fetch_release_list() -> str:
    revision = fetch_wikitext(RELEASE_LIST_TITLE, before_cutoff=False)
    return revision.content


def main() -> None:
    release_text = fetch_release_list()
    all_rows = parse_questline_templates(release_text)
    included_rows = [row for row in all_rows if include_row(row)]
    included_rows.sort(key=lambda row: (row.release_date, parse_int(row.nr, 9999), row.display_name))
    included_rows = expand_recipe_for_disaster_rows(included_rows)
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
    OUTPUT_PATH.write_text(_preserve_source_provenance(output), encoding="utf-8")
    print(f"wrote {len(catalog)} quests to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
