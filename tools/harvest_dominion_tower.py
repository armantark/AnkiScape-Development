#!/usr/bin/env python3
"""Pull the Dominion Tower's boss and reward pages at their pre-EOC revisions.

The tower re-fights forty-eight quest-boss encounters plus the non-quest
Sunfreet, and each encounter needs a combat level, a lifepoint total, a maximum
hit, and an attack style before it can be modelled. Doing that by hand is sixty
wiki lookups, so this tool resolves every page's last revision before the EOC
cutoff and prints the infobox fields it needs as JSON.

Darkan's `data/npcs/combatdefs` corroborates roughly two thirds of the roster;
this is the other source, and the one that covers the bosses Darkan stubbed.

Usage:
    python3 tools/harvest_dominion_tower.py > /tmp/dominion_bosses.json
    python3 tools/harvest_dominion_tower.py --pages rewards
"""
from __future__ import annotations

import argparse
import json
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wiki_parity import EOC, content_by_revid, resolve  # noqa: E402

MONSTER_PAGES = (
    "Nomad (monster)",
    "Pest Queen",
    "Pest drone",
    "Decaying avatar",
    "Eruni",
    "Ayuni",
    "Leeuni",
    "Dagannoth Mother",
    "Zenevivia",
    "The Untouchable",
    "Damis",
    "Fareed",
    "Kamil",
    "Dessous",
    "The Everlasting",
    "The Illusive",
    "Dagannoth sentinel",
    "Karamel",
    "Gelatinnoth Mother",
    "Nezikchened",
    "Balance Elemental",
    "Jungle demon",
    "Arrav",
    "Ice demon",
    "The Inadequacy",
    "A Doubt",
    "Giant Roc",
    "Arrg",
    "Barrelchest",
    "Chronozon",
    "Evil Chicken (Recipe for Disaster)",
    "Flambeed",
    "Agrith-Na-Na",
    "Dessourt",
    "Giant scarab (Contact!)",
    "Bouncer",
    "Koschei the deathless",
    "Arzinian Avatar",
    "Black Knight Titan",
    "General Khazard (monster)",
    "Black Knight guardian",
    "Dad",
    "Dramen Tree Spirit",
    "Agrith Naar",
    "Dagannoth mother",
    "TokTz-Ket-Dill (monster)",
    "Black golem",
    "Grey golem",
    "White golem",
    "Treus Dayth",
    "Elvarg",
    "Culinaromancer",
    "Tumeken's shadow",
    "The Kendal",
    "The Draugen",
    "Tarn Razorlor",
    "Terror dog",
    "Sigmund (monster)",
    "Melzar the Mad",
    "Count Draynor",
    "Delrith",
    "Solus Dellagar",
    "Sunfreet",
)

REWARD_PAGES = (
    "Reward Box",
    "Dominion gloves",
    "Goliath gloves",
    "Spellcaster gloves",
    "Swift gloves",
    "Dreadnip",
    "Dominion sword",
    "Dominion staff",
    "Dominion crossbow",
    "Dominion mine",
    "Ascendency mine",
    "Dominion medallion",
    "Super dominion medallion",
    "Dominion marker",
    "A journal page",
    "Scorpion meat",
    "Dominion potion",
    "Diminutive bomb",
    "Massive bomb",
    "Colossal bomb",
    "Help horn",
    "Xp book",
    "Handicap",
)

_FIELDS = (
    "level",
    "lp",
    "hitpoints",
    "max hit",
    "attack style",
    "weakness",
    "aggressive",
    "poisonous",
    "release",
    "examine",
    "members",
    "tradeable",
    "high",
    "low",
    "destroy",
    "store",
    "value",
)


def _infobox_fields(wikitext: str) -> dict[str, str]:
    """Flat scrape of `|key = value` lines from the first infobox block."""
    fields: dict[str, str] = {}
    for raw in wikitext.splitlines():
        line = raw.strip()
        if not line.startswith("|") or "=" not in line:
            continue
        key, _, value = line[1:].partition("=")
        key = key.strip().lower()
        if key in _FIELDS and key not in fields:
            fields[key] = re.sub(r"\s+", " ", value.strip())
    return fields


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", choices=("monsters", "rewards", "all"), default="all")
    args = parser.parse_args()
    titles = ()
    if args.pages in ("monsters", "all"):
        titles += MONSTER_PAGES
    if args.pages in ("rewards", "all"):
        titles += REWARD_PAGES
    out: dict[str, dict[str, object]] = {}
    for title in titles:
        try:
            resolved = resolve(title, EOC)
        except Exception as error:  # noqa: BLE001 - report and continue the sweep
            out[title] = {"error": str(error)}
            print(f"{title}: FAILED {error}", file=sys.stderr)
            continue
        if resolved is None:
            out[title] = {"error": "no pre-EOC revision"}
            print(f"{title}: no pre-EOC revision", file=sys.stderr)
            continue
        revid, timestamp, resolved_title = resolved
        fetched = content_by_revid(revid)
        wikitext = fetched[0] if fetched else ""
        out[title] = {
            "oldid": revid,
            "timestamp": timestamp,
            "resolved_title": resolved_title,
            "fields": _infobox_fields(wikitext),
            "chars": len(wikitext),
        }
        print(f"{title}: oldid={revid}", file=sys.stderr)
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
