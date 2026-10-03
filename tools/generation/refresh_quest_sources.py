#!/usr/bin/env python3
"""Extract and pack the inputs used by the offline quest catalog builder."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import http.client
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Mapping, Optional, Tuple
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools import build_pre_eoc_quest_catalog as builder
from tools.build_pre_eoc_quest_catalog import (
    GAME_MAIN_DIR, DARKAN_WORLD_SERVER_DIR, DARKAN_NPC_COMBATDEF_DIR,
    DARKAN_NPC_LIST_PATH, DARKAN_BEASTS_PATH, SCAPE_2011_QUEST_IMPL_DIR,
    Revision, clean_journal_line, parse_int, quest_id_from_name,
    slug_key, _unescape_kotlin_string, _normalize_npc_lookup_name,
    _load_darkan_npc_list, _darkan_name_level_pairs, _darkan_combat_payload,
)

SCAPE_2011_ITEMS_PATH = GAME_MAIN_DIR / "data/cfg/items.yml"
SCAPE_2011_NPC_DEFINITION_DIR = (
    GAME_MAIN_DIR / "game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions"
)
WIKI_API = "https://runescape.wiki/api.php"
EOC_CUTOFF_TIMESTAMP = "2012-11-19T23:59:59Z"
USER_AGENT = "AnkiScape parity audit"


def _journal_stage(match) -> Optional[Dict[str, object]]:
    stage = parse_int(match.group(1), 0)
    if stage <= 0:
        return None
    lines = tuple(
        line
        for line in (clean_journal_line(entry.group(1)) for entry in re.finditer(r'"((?:\\.|[^"])*)"', match.group(2)))
        if line
    )
    return {"stage": stage, "journal": lines} if lines else None


def parse_2011scape_journals():
    journals = {}
    sources = {}
    for path in sorted(SCAPE_2011_QUEST_IMPL_DIR.glob("*.kt")):
        text = path.read_text(encoding="utf-8")
        name_match = re.search(r'name\s*=\s*"([^"]+)"', text)
        if not name_match:
            continue
        quest_id = quest_id_from_name(_unescape_kotlin_string(name_match.group(1)))
        matches = re.finditer(
            r"\b(\d+)\s*->\s*(?:\{[^{}]*)?QuestStage\s*\(\s*objectives\s*=\s*listOf\s*\((.*?)\)\s*,?\s*\)",
            text, flags=re.S,
        )
        stages = tuple(stage for match in matches if (stage := _journal_stage(match)))
        if stages:
            journals[quest_id] = stages
            sources[quest_id] = path
    return journals, sources


def parse_2011scape_wearable_items() -> Dict[str, bool]:
    """Lower-cased 2011Scape item name -> whether any definition of it is worn."""
    wearable: Dict[str, bool] = {}
    for entry in SCAPE_2011_ITEMS_PATH.read_text(encoding="utf-8").split("\n- id: "):
        name = re.search(r'^  name: "(.*)"$', entry, flags=re.M)
        if name:
            key = name.group(1).lower()
            wearable[key] = wearable.get(key, False) or bool(re.search(r"^    equip_slot: \d", entry, flags=re.M))
    return wearable


def _npc_file_display_name(path: Path) -> Tuple[str, int]:
    stem = path.stem.replace(".plugin", "")
    level = 0
    match = re.search(r"_(?:level|lvl|lv)_?(\d+)", stem, flags=re.I)
    if match:
        level = parse_int(match.group(1), 0)
        stem = stem[: match.start()] + stem[match.end() :]
    name = re.sub(r"[_\s]+", " ", stem).strip()
    return name.title(), level


def _parse_kts_assignment_int(block: str, key: str) -> Optional[int]:
    match = re.search(rf"\b{re.escape(key)}\s*=\s*(-?\d+)", block)
    if not match:
        return None
    return parse_int(match.group(1), 0)


def _kts_block(text: str, name: str) -> str:
    match = re.search(rf"\b{re.escape(name)}\s*\{{(?P<body>.*?)\n\s*\}}", text, flags=re.S)
    return match.group("body") if match else ""


def _kts_int_fields(block: str, keys) -> Dict[str, int]:
    return {key: value for key in keys if (value := _parse_kts_assignment_int(block, key)) is not None}


def _local_npc_payload(path: Path) -> Optional[Dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1")
    if "set_combat_def" not in text:
        return None
    stats = _kts_int_fields(_kts_block(text, "stats"), ("hitpoints", "attack", "strength", "defence", "magic", "ranged"))
    bonuses = _kts_int_fields(_kts_block(text, "bonuses"), (
        "attackStab", "attackSlash", "attackCrush", "attackMagic", "attackRanged",
        "defenceStab", "defenceSlash", "defenceCrush", "defenceMagic", "defenceRanged",
    ))
    configs_block = _kts_block(text, "configs")
    configs = {}
    attack_speed = _parse_kts_assignment_int(configs_block, "attackSpeed")
    if attack_speed is not None:
        configs["attack_speed"] = attack_speed
    style_match = re.search(r"\battackStyle\s*=\s*StyleType\.([A-Z_]+)", configs_block)
    if style_match:
        configs["attack_style"] = style_match.group(1).lower()
    if not (stats or bonuses or configs):
        return None
    display_name, level = _npc_file_display_name(path)
    return {
        "display_name": display_name, "level": level, "stats": stats,
        "bonuses": bonuses, "configs": configs, "source": str(path),
    }


def _load_local_npc_stats() -> Dict[Tuple[str, int], Dict[str, object]]:
    rows = {}
    for path in sorted(SCAPE_2011_NPC_DEFINITION_DIR.rglob("*.plugin.kts")):
        payload = _local_npc_payload(path)
        if payload:
            rows[_normalize_npc_lookup_name(payload["display_name"]), payload["level"]] = payload
    return rows


def _darkan_candidates(path: Path, by_id, levels_by_name):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return
    for display_name, level in _darkan_name_level_pairs(data, by_id, levels_by_name):
        payload = _darkan_combat_payload(path, data, match_name=display_name, match_level=level)
        if not payload:
            continue
        yield (_normalize_npc_lookup_name(display_name), level), {
            "display_name": display_name, "level": level, "stats": payload["stats"],
            "bonuses": {}, "configs": payload["configs"], "source": payload["source"],
        }


def _load_darkan_npc_stats() -> Dict[Tuple[str, int], Dict[str, object]]:
    by_id, levels_by_name = _load_darkan_npc_list()
    rows = {}
    candidates = (
        candidate for path in sorted(DARKAN_NPC_COMBATDEF_DIR.rglob("*.json"))
        for candidate in _darkan_candidates(path, by_id, levels_by_name)
    )
    for key, candidate in candidates:
        rows.setdefault(key, []).append(candidate)
    unambiguous = {}
    for key, candidates in rows.items():
        signatures = {
            (json.dumps(candidate["stats"], sort_keys=True), json.dumps(candidate["configs"], sort_keys=True))
            for candidate in candidates
        }
        if len(signatures) != 1:
            continue
        row = dict(min(candidates, key=lambda candidate: str(candidate["source"])))
        row["source"] = "; ".join(sorted({str(candidate["source"]) for candidate in candidates}))
        unambiguous[key] = row
    return unambiguous


def fetch_wikitext(wiki: WikiSources, title: str, before_cutoff: bool = True) -> Revision:
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
    payload = wiki.read(f"wikitext_{slug_key(title)}_{'old' if before_cutoff else 'current'}", params)
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
        print(f"Warning: {title} has no pre-cutoff revision; using the current revision", file=sys.stderr)
        return fetch_wikitext(wiki, title, before_cutoff=False)
    raise RuntimeError(f"No revision found for {title}")


def fetch_parsed_html(wiki: WikiSources, revision: Revision) -> str:
    payload = wiki.read(
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


def _is_retryable_wiki_error(error: Exception) -> bool:
    if isinstance(error, urllib.error.HTTPError):
        return error.code == 429 or 500 <= error.code < 600
    reason = error.reason if isinstance(error, urllib.error.URLError) else error
    return isinstance(reason, (
        ConnectionResetError, ConnectionRefusedError, TimeoutError,
        http.client.IncompleteRead,
    ))


def request_wiki_payload(cache_key: str, params: Mapping[str, object]) -> Mapping[str, object]:
    request = urllib.request.Request(
        f"{WIKI_API}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": USER_AGENT},
    )
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, http.client.HTTPException) as exc:
            if not _is_retryable_wiki_error(exc):
                raise
            if attempt == 5:
                raise RuntimeError(f"Wiki API request failed for {cache_key}: {exc}") from exc
            time.sleep((10 if getattr(exc, "code", None) == 429 else 1.5) * (attempt + 1))


class WikiSources:
    def __init__(self, cache: Path, offline: bool):
        self.cache = cache
        self.offline = offline
        self.responses = {}

    def read(self, cache_key: str, params: Mapping[str, object]) -> Mapping[str, object]:
        cache_path = self.cache / f"{cache_key}.json"
        cached = cache_path.exists()
        if cached:
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            if self.offline:
                raise FileNotFoundError(f"Missing offline wiki response: {cache_path}")
            payload = request_wiki_payload(cache_key, params)
        if "error" in payload:
            raise RuntimeError(f"Wiki API error for {cache_key}: {payload['error']}")
        if not cached:
            self.cache.mkdir(parents=True, exist_ok=True)
            temporary = cache_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            temporary.replace(cache_path)
        self.responses[cache_key] = payload
        return payload


class UsedLookups(dict):
    def __init__(self, rows):
        super().__init__(rows)
        self.used = set()

    def get(self, key, default=None):
        self.used.add(key)
        return super().get(key, default)

    def retained(self):
        return {key: self[key] for key in sorted(self.used) if key in self}


def retain_npc_matches(matcher, rows, used, *, local=False):
    keys = {id(payload): key for key, payload in rows.items()}

    def match(display_name, level):
        result = matcher(display_name, level)
        if result:
            used.add(keys[id(result)])
            return {**result, "source": builder._preserve_source_provenance(result["source"])}
        if local and level:
            # Preserve rejected ambiguities, so pruning cannot create a unique match.
            variants = builder._npc_lookup_name_variants(display_name)
            used.update(
                key for key in rows
                if key[1] == level and any(
                    builder._token_sequence_contains(key[0], variant)
                    or builder._token_sequence_contains(variant, key[0])
                    for variant in variants
                )
            )
        return result

    return match


def pack_npcs(rows, used, root):
    packed = []
    for name, level in sorted(used):
        payload = dict(rows[name, level])
        payload["field_order"] = {field: list(payload[field]) for field in ("stats", "bonuses", "configs")}
        payload["source"] = "; ".join(
            Path(source).relative_to(root).as_posix() for source in payload["source"].split("; ")
        )
        packed.append([name, level, payload])
    return packed


def source_manifest(journal_paths, local_packed, darkan_packed):
    sources = {}
    for name, root, paths in (
        ("game-main", GAME_MAIN_DIR, [
            *journal_paths, SCAPE_2011_ITEMS_PATH,
            *(GAME_MAIN_DIR / source for _, _, payload in local_packed for source in payload["source"].split("; ")),
        ]),
        ("darkan-world-server", DARKAN_WORLD_SERVER_DIR, [
            DARKAN_NPC_LIST_PATH, DARKAN_BEASTS_PATH,
            *(DARKAN_WORLD_SERVER_DIR / source for _, _, payload in darkan_packed for source in payload["source"].split("; ")),
        ]),
    ):
        revision = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False,
        )
        if revision.returncode and (root / ".git").exists():
            raise RuntimeError(f"Cannot read {name} revision: {revision.stderr}")
        sources[name] = {
            "commit": revision.stdout.strip() if revision.returncode == 0 else None,
            "input_sha256": {
                path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(set(paths))
            },
        }
    return sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki-cache", type=Path, default=ROOT / "tools/.cache/pre_eoc_quest_catalog")
    parser.add_argument("--offline", action="store_true", help="Fail if any wiki cache response is missing.")
    parser.add_argument("--output", type=Path, default=builder.PINNED_INPUTS_PATH)
    parser.add_argument("--check-catalog", type=Path, help="Require exact catalog bytes before writing the pin.")
    args = parser.parse_args()
    for path in (
        SCAPE_2011_QUEST_IMPL_DIR, SCAPE_2011_ITEMS_PATH, SCAPE_2011_NPC_DEFINITION_DIR,
        DARKAN_NPC_LIST_PATH, DARKAN_BEASTS_PATH, DARKAN_NPC_COMBATDEF_DIR,
    ):
        if not path.exists():
            raise FileNotFoundError(f"Missing emulator input: {path}")
    wiki = WikiSources(args.wiki_cache, args.offline)
    journal_rows, journal_sources = parse_2011scape_journals()
    journals = UsedLookups(journal_rows)
    wearable = UsedLookups(parse_2011scape_wearable_items())
    local = _load_local_npc_stats()
    darkan = _load_darkan_npc_stats()
    local_used, darkan_used = set(), set()
    with tempfile.TemporaryDirectory(prefix="quest-sources-") as directory:
        candidate = Path(directory) / "quest_catalog.py"
        with (
            patch.object(builder, "fetch_wikitext", lambda title, before_cutoff=True: fetch_wikitext(wiki, title, before_cutoff)),
            patch.object(builder, "fetch_parsed_html", lambda revision: fetch_parsed_html(wiki, revision)),
            patch.object(builder, "parse_2011scape_journals", lambda: journals),
            patch.object(builder, "parse_2011scape_wearable_items", lambda: wearable),
            patch.object(builder, "_LOCAL_NPC_STATS", local),
            patch.object(builder, "_DARKAN_NPC_STATS", darkan),
            patch.object(builder, "_matching_local_npc_stats", retain_npc_matches(
                builder._matching_local_npc_stats, local, local_used, local=True,
            )),
            patch.object(builder, "_matching_darkan_npc_stats", retain_npc_matches(
                builder._matching_darkan_npc_stats, darkan, darkan_used,
            )),
            patch.object(builder, "OUTPUT_PATH", candidate),
        ):
            builder.main()
        if args.check_catalog and candidate.read_bytes() != args.check_catalog.read_bytes():
            raise RuntimeError("Refreshed sources do not reproduce --check-catalog; pin was not written")
    local_packed = pack_npcs(local, local_used, GAME_MAIN_DIR)
    darkan_packed = pack_npcs(darkan, darkan_used, DARKAN_WORLD_SERVER_DIR)
    manifest = source_manifest(
        [journal_sources[key] for key in journals.retained()], local_packed, darkan_packed,
    )
    snapshot = {
        "journals": journals.retained(), "wearable_items": wearable.retained(),
        "local_npcs": local_packed, "darkan_npcs": darkan_packed,
        "wiki": wiki.responses, "source_revisions": manifest,
    }
    packed = gzip.compress(json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8"), mtime=0)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_bytes(packed)
    temporary.replace(args.output)
    print(f"wrote {len(packed)} bytes to {args.output}")
    print("retained tables:", {key: len(value) for key, value in snapshot.items() if key != "source_revisions"})


if __name__ == "__main__":
    main()
