#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch combat target sprites from the RuneScape wikis."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "tools"))

from combat_data import COMBAT_ENEMY_DATA  # noqa: E402
from fetch_assets import (  # noqa: E402
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    OSRS_WIKI,
    RS3_WIKI,
    fetch_asset,
    wiki_title_for_item,
)

PRE_EOC_CUTOFF = "2012-11-20T23:59:59Z"


TITLE_OVERRIDES = {
    "jackal": ("Jackalnew.png", "Jackal.png"),
    "desert_lizard": ("Desert lizard (green).png", "Desert lizard icon.png"),
    "rockslug": ("Rock slug icon.png", "Rock slug.png"),
    "gargoyle": ("Gargoyle icon.png", "Gargoyle.png"),
    "giant_spider": ("Giant spider (Level 2).png",),
    "giant_spider_level_50": ("Giant spider (Level 50).png",),
    "pirate": ("Pirate (Port Sarim).png", "Pirate (Brimhaven).png"),
    "monk_of_zamorak_level_45": ("Monk of Zamorak (level 30 and 45).png",),
    "big_wolf": ("Big Wolf.png",),
    "hill_giant": ("Hill Giant.png",),
    "market_guard": ("Market Guard (Draynor).png", "Market guard (Varrock).png"),
    "jail_guard": ("Jail guard (1).png",),
    "haakon_the_champion": ("Haakon the champion.png",),
    "ham_guard_level_12": ("H.A.M. Guard (level 12).png",),
    "ham_guard_level_18": ("H.A.M. Guard (level 18).png",),
    "ham_guard_level_22": ("H.A.M. Guard (level 22).png",),
    "white_knight_level_36": ("White Knight (initiate, male).png", "White Knight (historical v3).png"),
    "white_knight_level_38": ("White Knight (partisan, male).png", "White Knight (historical v3).png"),
    "white_knight_level_39": ("White Knight (proselyte, male).png", "White Knight (historical v3).png"),
    "white_knight_level_42": ("White Knight (acolyte, male).png", "White Knight (historical v3).png"),
    "barbarian": ("Barbarian (historical).png",),
    "barbarian_level_10": ("Barbarian (historical).png",),
    "barbarian_level_17": ("Barbarian (historical).png",),
    "al_kharid_warrior": ("Al Kharid warrior.png",),
    "poison_scorpion": ("Poison Scorpion.png",),
    "king_scorpion": ("King Scorpion.png",),
    "pit_scorpion": ("Pit Scorpion.png",),
    "citizen": ("Man.png", "Woman.png"),
    "cuffs": ("Man.png",),
    "narf_jeff_rusty": ("Man.png",),
    "duck_land": ("Duck.png",),
    "duck_water": ("Duck.png",),
    "dwarf_level_10": ("Dwarf.png",),
    "dwarf_level_11": ("Dwarf.png",),
    "guard_varrock": ("Guard.png",),
    "guard_sword": ("Guard.png",),
    "guard_battleaxe": ("Guard.png",),
    "goblin_level_2_unarmed": ("Goblin.png",),
    "goblin_level_2_armed": ("Goblin.png",),
    "hobgoblin_unarmed": ("Hobgoblin.png",),
    "hobgoblin_armed": ("Hobgoblin.png",),
    "vampyre": ("Vampire (historical) (level 61).png",),
    "harpie_bug_swarm": ("Harpie Bugs Swarm.png",),
    "killerwatt": ("Killerwatt icon.png",),
    "sea_snake_hatchling": ("Sea Snake Hatchling.png",),
    "sea_snake_young": ("Sea Snake Young.png",),
    "brine_rat": ("Brine rat icon.png", "Brine rat.png"),
    "molanisk": ("Molanisk icon.png", "Molanisk.png"),
    "turoth": ("Turoth icon.png", "Turoth.png"),
    "fire_giant": ("Fire giant.png",),
    "blue_dragon": ("Blue dragon.png",),
    "baby_blue_dragon": ("Baby blue dragon.png",),
}


def _asset_slug(value: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", value.lower()))


def _display_candidates(display_name: str) -> Iterable[str]:
    clean = re.sub(r"\s*\([^)]*\)", "", display_name).strip()
    yield display_name
    if clean and clean != display_name:
        yield clean
    if "/" in clean:
        for part in clean.split("/"):
            part = part.strip()
            if part:
                yield part


def _wiki_title_candidates(target_id: str, display_name: str) -> tuple[str, ...]:
    seen: set[str] = set()
    titles: list[str] = []
    for title in TITLE_OVERRIDES.get(target_id, ()):
        normalized = wiki_title_for_item(display_name, title)
        if normalized not in seen:
            titles.append(normalized)
            seen.add(normalized)
    for candidate in _display_candidates(display_name):
        normalized = wiki_title_for_item(candidate)
        if normalized not in seen:
            titles.append(normalized)
            seen.add(normalized)
    return tuple(titles)


def fetch_enemy_assets(target_ids: Sequence[str], force: bool = False, size: int = 48) -> int:
    output_dir = REPO_ROOT / "combatenemies"
    client = HttpWikiClient(before_timestamp=PRE_EOC_CUTOFF)
    failures: list[str] = []
    for target_id in target_ids:
        enemy = COMBAT_ENEMY_DATA[target_id]
        display_name = str(enemy.get("display_name", target_id))
        output_path = output_dir / f"{_asset_slug(target_id)}.png"
        if output_path.exists() and not force:
            print(f"skip existing {target_id}: {output_path}")
            continue
        fetched = False
        last_error = ""
        for wiki_title in _wiki_title_candidates(target_id, display_name):
            request = AssetRequest(
                item_name=display_name,
                wiki_title=wiki_title,
                output_path=output_path,
                provenance_path=REPO_ROOT / "assets_provenance.json",
            )
            try:
                outcome = fetch_asset(
                    request,
                    client,
                    size=size,
                    force=force,
                    sources=(RS3_WIKI, OSRS_WIKI),
                )
            except AssetFetchError as exc:
                last_error = str(exc)
                continue
            print(asdict(outcome))
            fetched = True
            break
        if not fetched:
            failures.append(f"{target_id} ({display_name}): {last_error}")
    if failures:
        print("Failed enemy asset fetches:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch combat enemy target icons.")
    parser.add_argument("target_ids", nargs="*", help="Specific combat target ids to fetch. Defaults to all.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing enemy image files.")
    parser.add_argument("--size", type=int, default=48, help="Normalized icon size in pixels.")
    args = parser.parse_args(argv)
    target_ids = tuple(args.target_ids) or tuple(COMBAT_ENEMY_DATA)
    unknown = [target_id for target_id in target_ids if target_id not in COMBAT_ENEMY_DATA]
    if unknown:
        parser.error("Unknown combat target id(s): " + ", ".join(unknown))
    return fetch_enemy_assets(target_ids, force=args.force, size=args.size)


if __name__ == "__main__":
    raise SystemExit(main())
