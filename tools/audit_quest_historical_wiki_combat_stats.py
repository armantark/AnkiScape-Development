#!/usr/bin/env python3
"""Audit remaining quest combat gaps against pinned historical monster pages."""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import re
import sys
import time
from typing import Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import audit_quest_combat_stat_gaps as gap_audit
from tools import build_pre_eoc_quest_catalog as catalog_builder


CACHE_DIR = ROOT / "tools" / ".cache" / "quest_historical_wiki_combat_stats"
WIKI_API = "https://runescape.wiki/api.php"
EOC_CUTOFF_TIMESTAMP = "2012-11-19T23:59:59Z"
USER_AGENT = "AnkiScape quest combat source audit (local development)"


@dataclass(frozen=True)
class HistoricalRevision:
    requested_title: str
    resolved_title: str
    oldid: int
    timestamp: str
    content: str


@dataclass(frozen=True)
class HistoricalCombatStatAuditRow:
    gap: gap_audit.CombatGap
    status: str
    requested_title: str = ""
    resolved_title: str = ""
    oldid: int = 0
    timestamp: str = ""
    stats: Tuple[Tuple[str, int], ...] = ()
    configs: Tuple[Tuple[str, str], ...] = ()

    @property
    def source_url(self) -> str:
        if not self.oldid:
            return ""
        title = urllib.parse.quote(self.resolved_title.replace(" ", "_"))
        return f"https://runescape.wiki/w/{title}?oldid={self.oldid}"


FetchRevision = Callable[[str], Optional[HistoricalRevision]]


def title_candidates(display_name: str) -> Tuple[str, ...]:
    clean = catalog_builder.clean_markup(display_name)
    clean = re.sub(r"\s+x\d+\s*$", "", clean, flags=re.I).strip()
    stripped_parenthetical = re.sub(r"\s+\([^)]*\)\s*$", "", clean).strip()
    candidates = []
    for title in (clean, stripped_parenthetical):
        if not title:
            continue
        candidates.append(title)
        candidates.append(f"{title} (monster)")
    seen = set()
    output = []
    for title in candidates:
        key = catalog_builder.normalize_title(title)
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(title)
    return tuple(output)


def parse_monster_infobox_metadata(wikitext: str) -> Tuple[Dict[str, int], Dict[str, str]]:
    for body in catalog_builder.iter_templates(wikitext):
        name = catalog_builder.template_name(body)
        if name not in {"infobox monster", "infobox npc"}:
            continue
        params = catalog_builder.parse_template_params(body)
        return _stats_and_configs_from_infobox(params)
    return {}, {}


def _stats_and_configs_from_infobox(params: Mapping[str, str]) -> Tuple[Dict[str, int], Dict[str, str]]:
    stats: Dict[str, int] = {}
    configs: Dict[str, str] = {}
    stat_aliases = {
        "lp": "hitpoints",
        "lifepoints": "hitpoints",
        "life points": "hitpoints",
        "hitpoints": "hitpoints",
        "hp": "hitpoints",
        "attack": "attack",
        "attack level": "attack",
        "att": "attack",
        "att level": "attack",
        "strength": "strength",
        "strength level": "strength",
        "str": "strength",
        "str level": "strength",
        "defence": "defence",
        "defence level": "defence",
        "defense": "defence",
        "defense level": "defence",
        "def": "defence",
        "def level": "defence",
        "magic": "magic",
        "magic level": "magic",
        "mage": "magic",
        "mage level": "magic",
        "ranged": "ranged",
        "ranged level": "ranged",
        "range": "ranged",
        "range level": "ranged",
    }
    config_aliases = {
        "attack style": "attack_style",
        "attackstyle": "attack_style",
        "max hit": "max_hit",
        "maxhit": "max_hit",
    }
    for raw_key, raw_value in params.items():
        key = " ".join(str(raw_key).lower().replace("_", " ").split())
        value = catalog_builder.clean_markup(str(raw_value))
        stat_key = stat_aliases.get(key)
        if stat_key:
            parsed = _first_int(value)
            if parsed is not None:
                stats[stat_key] = parsed
            continue
        config_key = config_aliases.get(key)
        if config_key == "attack_style":
            style = normalized_attack_style(value)
            if style:
                configs[config_key] = style
        elif config_key == "max_hit":
            parsed = _first_int(value)
            if parsed is not None:
                configs[config_key] = str(parsed)
    return stats, configs


def _first_int(value: str) -> Optional[int]:
    match = re.search(r"\d[\d,]*", value)
    if not match:
        return None
    return int(match.group(0).replace(",", ""))


def normalized_attack_style(value: str) -> str:
    lower = catalog_builder.clean_markup(value).lower()
    has_magic = "magic" in lower or "mage" in lower
    has_ranged = "ranged" in lower or "range" in lower or "missile" in lower
    has_melee = any(word in lower for word in ("melee", "slash", "stab", "crush"))
    if has_melee or (has_magic and has_ranged):
        return "melee"
    if has_magic:
        return "magic"
    if has_ranged:
        return "range"
    return ""


def metadata_has_resolver_stats(stats: Mapping[str, int], configs: Mapping[str, str]) -> bool:
    style = configs.get("attack_style", "")
    if style == "magic":
        required = ("hitpoints", "defence", "magic")
    elif style in {"range", "ranged"}:
        required = ("hitpoints", "defence", "ranged")
    else:
        required = ("hitpoints", "attack", "strength", "defence")
    return all(int(stats.get(key, 0) or 0) > 0 for key in required)


def audit_gap(gap: gap_audit.CombatGap, fetch_revision: FetchRevision = None) -> HistoricalCombatStatAuditRow:
    fetch_revision = fetch_revision or fetch_historical_revision
    best_metadata_row: Optional[HistoricalCombatStatAuditRow] = None
    for title in title_candidates(gap.display_name):
        revision = fetch_revision(title)
        if revision is None or not revision.content:
            continue
        stats, configs = parse_monster_infobox_metadata(revision.content)
        if not stats and not configs:
            continue
        status = "historical_wiki_resolver_stats_available" if metadata_has_resolver_stats(stats, configs) else "historical_wiki_metadata_only"
        row = HistoricalCombatStatAuditRow(
            gap=gap,
            status=status,
            requested_title=revision.requested_title,
            resolved_title=revision.resolved_title,
            oldid=revision.oldid,
            timestamp=revision.timestamp,
            stats=tuple(sorted(stats.items())),
            configs=tuple(sorted(configs.items())),
        )
        if status == "historical_wiki_resolver_stats_available":
            return row
        if best_metadata_row is None:
            best_metadata_row = row
    if best_metadata_row is not None:
        return best_metadata_row
    first_title = title_candidates(gap.display_name)[0] if title_candidates(gap.display_name) else gap.display_name
    return HistoricalCombatStatAuditRow(gap=gap, status="historical_wiki_no_monster_metadata", requested_title=first_title)


@lru_cache(maxsize=512)
def fetch_historical_revision(title: str) -> Optional[HistoricalRevision]:
    cache_path = CACHE_DIR / f"{catalog_builder.slug_key(title)}.json"
    if cache_path.exists():
        try:
            return _revision_from_payload(title, json.loads(cache_path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass

    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "ids|timestamp|content",
        "rvslots": "main",
        "rvlimit": "1",
        "titles": title,
        "redirects": "1",
        "format": "json",
        "formatversion": "2",
        "rvstart": EOC_CUTOFF_TIMESTAMP,
        "rvdir": "older",
    }
    url = f"{WIKI_API}?{urllib.parse.urlencode(params)}"
    last_error: Optional[Exception] = None
    for attempt in range(5):
        try:
            time.sleep(0.2)
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            return _revision_from_payload(title, payload)
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 429:
                retry_after = _retry_after_seconds(exc)
                time.sleep(retry_after if retry_after is not None else 2.0 * (attempt + 1))
                continue
            time.sleep(0.75 * (attempt + 1))
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(0.75 * (attempt + 1))
    print(f"warning: failed to fetch {title}: {last_error}", file=sys.stderr)
    return None


def _retry_after_seconds(error: urllib.error.HTTPError) -> Optional[float]:
    value = error.headers.get("Retry-After") if error.headers else None
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        return None


def _revision_from_payload(title: str, payload: Mapping[str, object]) -> Optional[HistoricalRevision]:
    pages = ((payload.get("query") or {}).get("pages") if isinstance(payload.get("query"), Mapping) else None) or []
    if not isinstance(pages, list) or not pages:
        return None
    page = pages[0]
    if not isinstance(page, Mapping):
        return None
    revisions = page.get("revisions") or []
    if not isinstance(revisions, list) or not revisions:
        return None
    revision = revisions[0]
    if not isinstance(revision, Mapping):
        return None
    slots = revision.get("slots") or {}
    main = slots.get("main") if isinstance(slots, Mapping) else {}
    content = main.get("content") if isinstance(main, Mapping) else ""
    return HistoricalRevision(
        requested_title=title,
        resolved_title=str(page.get("title") or title),
        oldid=int(revision.get("revid") or 0),
        timestamp=str(revision.get("timestamp") or ""),
        content=str(content or ""),
    )


def audit_gaps(
    gaps: Sequence[gap_audit.CombatGap],
    fetch_revision: FetchRevision = None,
    *,
    max_workers: int = 2,
) -> Tuple[HistoricalCombatStatAuditRow, ...]:
    if fetch_revision is not None:
        return tuple(audit_gap(gap, fetch_revision) for gap in gaps)
    rows = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(audit_gap, gap): gap for gap in gaps}
        for future in as_completed(futures):
            rows.append(future.result())
    return tuple(sorted(rows, key=lambda row: (row.gap.quest_id, row.gap.stage, row.gap.display_name, row.gap.level)))


def print_summary(rows: Sequence[HistoricalCombatStatAuditRow]) -> None:
    counts = Counter(row.status for row in rows)
    print(f"combat_gaps_checked: {len(rows)}")
    print("historical_wiki_statuses:")
    for status in sorted(counts):
        print(f"  {status}: {counts[status]}")
    print("gaps:")
    for row in rows:
        print(
            "\t".join(
                (
                    row.status,
                    row.gap.quest_id,
                    row.gap.quest_name,
                    str(row.gap.stage),
                    row.gap.display_name,
                    str(row.gap.level),
                    str(dict(row.stats)),
                    str(dict(row.configs)),
                    row.source_url,
                )
            )
        )


def main() -> None:
    print_summary(audit_gaps(gap_audit.statless_combat_gaps()))


if __name__ == "__main__":
    main()
