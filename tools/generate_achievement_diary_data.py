#!/usr/bin/env python3
"""Generate ``data/achievement_diary_catalog.py`` from the harvested sources.

Run ``tools/harvest_achievement_tasks.py --out <json>`` first; this turns that
document into the checked-in catalog.

Translation rule, applied uniformly and deliberately:

A period task is kept only when its pinned wiki row states at least one
requirement — a quest, or a skill level. Its AnkiScape condition set is exactly
those stated requirements and nothing else. Rows stating no requirement are
dropped, because once the design contract's curation rule removes geography,
emotes and inventory choreography, nothing measurable is left of them.

The period name and description are preserved verbatim so the feat survives as
identity and narrative even where the predicate is the requirement the period
itself published. That flattening is an AnkiScape abstraction, not a recovered
value, so it is documented here and at the catalog rather than registered as a
placeholder.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pkg_alias  # noqa: F401,E402  (installs the ankiscape package alias)
from ankiscape.core.constants import QUEST_DATA  # noqa: E402
from ankiscape.core.skill_registry import ALL_SKILLS  # noqa: E402


ITEMS_YML = Path(
    "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"
)
SOURCE_SLOT_IDS = {
    0: "head", 1: "cape", 2: "neck", 3: "weapon", 4: "body", 5: "shield",
    7: "legs", 9: "hands", 10: "feet", 12: "ring", 13: "ammunition",
}
BONUS_FIELDS = (
    "attack_stab", "attack_slash", "attack_crush", "attack_magic", "attack_ranged",
    "defence_stab", "defence_slash", "defence_crush", "defence_magic", "defence_ranged",
    "melee_strength", "ranged_strength", "magic_damage", "prayer",
)

# Morytania legs are absent from the 2011Scape item config, so their four rows
# come from their own pinned pre-cutoff wiki revisions instead. Every figure
# below is transcribed from the Infobox Bonuses of the revision named beside it.
MORYTANIA_LEG_BONUSES = {
    "Morytania legs 1": (
        24134, "legs",
        dict(attack_ranged=4, defence_stab=2, defence_slash=2, defence_crush=1),
        "https://runescape.wiki/w/Special:PermanentLink/6333300",
    ),
    "Morytania legs 2": (
        24135, "legs",
        dict(attack_magic=-5, attack_ranged=6, defence_stab=8, defence_slash=8,
             defence_crush=10, defence_magic=4, defence_ranged=10),
        "https://runescape.wiki/w/Special:PermanentLink/6335330",
    ),
    "Morytania legs 3": (
        24136, "legs",
        dict(attack_magic=-10, attack_ranged=11, defence_stab=25, defence_slash=19,
             defence_crush=27, defence_magic=14, defence_ranged=25),
        "https://runescape.wiki/w/Special:PermanentLink/6333281",
    ),
    "Morytania legs 4": (
        24137, "legs",
        dict(attack_magic=-10, attack_ranged=14, defence_stab=28, defence_slash=22,
             defence_crush=30, defence_magic=20, defence_ranged=28),
        "https://runescape.wiki/w/Special:PermanentLink/6588883",
    ),
}


TASKS_PER_TIER = 12  # design contract: twelve curated tasks in every tier

TIER_ORDER = ("beginner", "easy", "medium", "hard", "elite")

# Darkan's SetReward table, plus the taskmaster each tier's reward comes from.
FAMILIES = {
    "ardougne": {
        "name": "Ardougne",
        "item": "Ardougne cloak",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Doctor Orbon", "Town Crier", "Aleck", "Aleck"),
        "lamp": (1000, 7500, 28000, 50000),
    },
    "falador": {
        "name": "Falador",
        "item": "Falador shield",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Redbeard Frank", "Chemist", "Squire", "Squire"),
        "lamp": (1000, 5000, 10000, 50000),
    },
    "fremennik": {
        "name": "Fremennik",
        "item": "Fremennik sea boots",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Council workman", "Yrsa", "Advisor Ghrim", "Advisor Ghrim"),
        "lamp": (5000, 10000, 15000, 40000),
    },
    "karamja": {
        "name": "Karamja",
        "item": "Karamja gloves",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Jackie the fruit trader", "Kaleb Paramaya", "Pirate Jackie the Fruit", "Pirate Jackie the Fruit"),
        "lamp": (1000, 5000, 10000, 30000),
    },
    "lumbridge": {
        "name": "Lumbridge and Draynor",
        "item": "Explorer's ring",
        "tiers": ("beginner", "easy", "medium", "hard"),
        "taskmasters": ("Explorer Jack", "Bob", "Ned", "Ned"),
        "lamp": (500, 1000, 1500, 9000),
    },
    "morytania": {
        "name": "Morytania",
        "item": "Morytania legs",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Hiylik Myna", "Robin", "Strange Old Man", "Old Man Ral"),
        "lamp": (4000, 10000, 20000, 40000),
    },
    "seers": {
        "name": "Seers' Village",
        "item": "Seer's headband",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Seer", "Stankers", "Sir Kay", "Sir Kay"),
        "lamp": (1000, 5000, 10000, 25000),
    },
    "varrock": {
        "name": "Varrock",
        "item": "Varrock armour",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Rat Burgiss", "Reldo", "Vannaka", "Vannaka"),
        "lamp": (1000, 5000, 10000, 30000),
    },
}

# Each tier's own sourced reward line, from the Darkan reward helpers and the
# pinned wiki reward sections. These are the "repeatable services, daily
# allowances and item effects" the design contract puts in the tier package.
TIER_REWARDS = {
    ("varrock", "easy"): "Rat Burgiss buys 16 battlestaves a day from Zaff.",
    ("varrock", "medium"): "Zaff's daily battlestaff allowance rises to 32.",
    ("varrock", "hard"): "Zaff's daily battlestaff allowance rises to 64.",
    ("varrock", "elite"): "Zaff's daily battlestaff allowance rises to 80.",
    ("seers", "easy"): "The coal truck holds more coal for you.",
    ("seers", "medium"): "Cheaper mystic staff enchantment from Stankers.",
    ("seers", "hard"): "The enhanced Excalibur heals for longer.",
    ("seers", "elite"): "Every Seers' Village service runs at its best rate.",
    ("ardougne", "easy"): "Doctor Orbon's blessing; Bert delivers sand each day.",
    ("ardougne", "medium"): "Bert's daily sand delivery grows.",
    ("ardougne", "hard"): "The Watchtower teleport can be retargeted.",
    ("ardougne", "elite"): "Bert delivers his largest daily load of sand.",
    ("fremennik", "easy"): "Peer the Seer stores items for you.",
    ("fremennik", "medium"): "The Lyre reaches Waterbirth Island.",
    ("fremennik", "hard"): "The Lyre reaches the Fremennik Isles.",
    ("fremennik", "elite"): "Every Fremennik service runs at its best rate.",
    ("falador", "easy"): "Redbeard Frank's thanks.",
    ("falador", "medium"): "Enter the Crafting Guild without a brown apron.",
    ("falador", "hard"): "The Squire's full Falador service package.",
    ("falador", "elite"): "Every Falador service runs at its best rate.",
}

_SKILL_IDS = {skill.display_name.lower(): skill.id for skill in ALL_SKILLS}
_SKILL_IDS.update({skill.id: skill.id for skill in ALL_SKILLS})
_SKILL_IDS["defence"] = "defense"
_SKILL_IDS["defense"] = "defense"
_SKILL_IDS["constitution"] = "constitution"
_SKILL_IDS["hitpoints"] = "constitution"

_QUEST_IDS = {
    str(record.get("display_name", "")).lower(): quest_id
    for quest_id, record in QUEST_DATA.items()
    if isinstance(record, dict)
}


def _slug(text: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", text.lower()))[:60]


def _conditions(row: dict) -> list[tuple]:
    conditions: list[tuple] = []
    for skill_name, level in row.get("skills", ()):
        skill_id = _SKILL_IDS.get(str(skill_name).strip().lower())
        if skill_id and int(level) > 1:
            conditions.append(
                ("skill_level", skill_id, int(level), f"Level {int(level)} {skill_name.strip()}")
            )
    for quest_name in row.get("quests", ()):
        quest_id = _QUEST_IDS.get(str(quest_name).strip().lower())
        if quest_id:
            conditions.append(("quest", quest_id, 1, f"Complete {quest_name.strip()}"))
    return conditions


def _items_yml_blocks() -> dict:
    text = ITEMS_YML.read_text(encoding="utf-8", errors="ignore")
    blocks = {}
    for block in re.split(r"\n(?=- id: )", text):
        name = re.search(r'name:\s*"([^"]+)"', block)
        if not name:
            continue
        blocks.setdefault(name.group(1), block)
    return blocks


def _equipment_rows() -> str:
    blocks = _items_yml_blocks()
    rows = []
    for meta in FAMILIES.values():
        for tier_index in range(1, 5):
            item_name = f"{meta['item']} {tier_index}"
            if item_name in MORYTANIA_LEG_BONUSES:
                item_id, slot, bonuses, source = MORYTANIA_LEG_BONUSES[item_name]
            else:
                block = blocks.get(item_name)
                if block is None:
                    raise SystemExit(f"no items.yml row for {item_name}")
                item_id = int(re.search(r"- id:\s*(\d+)", block).group(1))
                fields = dict(
                    (key, int(value))
                    for key, value in re.findall(r"^\s+([a-z_]+):\s*(-?\d+)\s*$", block, re.M)
                )
                slot = SOURCE_SLOT_IDS.get(fields.get("equip_slot", -1))
                if slot is None:
                    raise SystemExit(f"unmapped slot for {item_name}")
                bonuses = {key: fields.get(key, 0) for key in BONUS_FIELDS if fields.get(key)}
                source = "data/cfg/items.yml item %d; achievement diary tier reward" % item_id
            bonus_src = ", ".join(f"{key}={value}" for key, value in sorted(bonuses.items()))
            rows.append(
                f"    {item_name!r}: EquipmentItem(\n"
                f"        item_name={item_name!r},\n"
                f"        slot={slot!r},\n"
                "        combat_skill=None,\n"
                "        required_level=1,\n"
                "        two_handed=False,\n"
                "        equipment_type='achievement_diary_reward',\n"
                f"        bonuses=EquipmentBonuses({bonus_src}),\n"
                "        attack_speed=4,\n"
                f"        source_item_id={item_id},\n"
                f"        source={source!r},\n"
                "        source_status='period diary reward equipment row',\n"
                "        skill_requirements=(),\n"
                "        weapon_type=-1,\n"
                "    ),"
            )
    return "\n".join(rows)


def build(document: dict) -> str:
    lines: list[str] = []
    families = document["families"]
    kept_total = 0
    for family_id, meta in FAMILIES.items():
        record = families.get(family_id, {})
        wiki = record.get("wiki", {})
        permalink = wiki.get("permalink", "")
        source = f"{wiki.get('title', family_id)} oldid={wiki.get('oldid', 'n/a')} ({wiki.get('timestamp', 'n/a')}); Darkan {record.get('darkan_class', '')}"
        tier_blocks: list[str] = []
        for index, tier_name in enumerate(meta["tiers"]):
            rows = (wiki.get("tiers") or {}).get(tier_name, [])
            darkan_ids = record.get("tiers", {}).get(tier_name, [])
            task_blocks: list[str] = []
            for row in rows:
                conditions = _conditions(row)
                if not conditions:
                    continue
                task_id = f"{family_id}_{tier_name}_{_slug(row['name'])}"
                condition_src = ", ".join(
                    f"DiaryCondition({kind!r}, {key!r}, {amount}, {label!r})"
                    for kind, key, amount, label in conditions
                )
                task_blocks.append(
                    "            DiaryTask(\n"
                    f"                {task_id!r},\n"
                    f"                {row['name']!r},\n"
                    f"                {row['description'][:220]!r},\n"
                    f"                ({condition_src},),\n"
                    f"                {permalink!r},\n"
                    "            ),"
                )
                if len(task_blocks) >= TASKS_PER_TIER:
                    break
            kept_total += len(task_blocks)
            label = tier_name.capitalize()
            reward_item = f"{meta['item']} {index + 1}"
            reward = TIER_REWARDS.get(
                (family_id, tier_name), f"{label} {meta['name']} task rewards."
            )
            lamp = meta["lamp"][index]
            tier_blocks.append(
                "        DiaryTier(\n"
                f"            {family_id + '_' + tier_name!r},\n"
                f"            {label!r},\n"
                f"            {index + 1},\n"
                f"            {reward_item!r},\n"
                f"            {reward!r},\n"
                "            (\n" + "\n".join(task_blocks) + "\n            ),\n"
                f"            DiaryLamp({lamp}, 1),\n"
                f"            {'period tier: ' + str(len(darkan_ids)) + ' tasks; ' + source!r},\n"
                "        ),"
            )
        lines.append(
            "    DiaryFamily(\n"
            f"        {family_id!r},\n"
            f"        {meta['name']!r},\n"
            "        'regional',\n"
            "        (\n" + "\n".join(tier_blocks) + "\n        ),\n"
            f"        {meta['taskmasters'][0]!r},\n"
            f"        {source!r},\n"
            "    ),"
        )
    header = (
        '"""Generated by ``tools/generate_achievement_diary_data.py``. Do not hand-edit.\n\n'
        "Sources, in the project's evidence order: Darkan's\n"
        "``com/rs/game/content/achievements`` package owns each family's tier\n"
        "membership, reward items and taskmasters; the pinned pre-cutoff wiki\n"
        "revision cited on every tier owns the per-task requirement text.\n\n"
        f"Tasks kept: {kept_total}. A period task is present only when its pinned row\n"
        "states a requirement; see the generator's module docstring for the rule and\n"
        'for the abstraction it makes explicit."""\n\n'
        "from __future__ import annotations\n\n"
        "from .achievement_diary_data import (\n"
        "    DiaryCondition,\n"
        "    DiaryFamily,\n"
        "    DiaryLamp,\n"
        "    DiaryTask,\n"
        "    DiaryTier,\n"
        ")\n\n"
        "# PLACEHOLDER(achievement_diaries.lamp_minimum_level): every tier lamp ships\n"
        "# with no minimum-level restriction. The pinned task-set infoboxes state each\n"
        "# tier's lamp experience exactly but never the skill-level floor the period\n"
        "# lamp imposed. A period lamp dialogue or a cache interface script would\n"
        "# settle it.\n\n\n"
        "REGIONAL_DIARY_FAMILIES = (\n"
    )
    equipment = (
        "\n\n\ndef diary_equipment_data_as_dict() -> dict:\n"
        '    """Register the 32 tier reward items as real wearable equipment.\n\n'
        "    Without this the whole family would be inert: every tier hands over an\n"
        "    item that the equipment table has never heard of. The generated table is\n"
        "    built from the emulator config and must not be hand-edited, so these rows\n"
        "    join through the same per-family seam Barrows and the penguin ring use.\n"
        '    """\n\n'
        "    from .equipment_data import EquipmentBonuses, EquipmentItem\n\n"
        "    return {\n" + _equipment_rows() + "\n    }\n"
    )
    return header + "\n".join(lines) + "\n)\n" + equipment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("harvest", type=Path)
    parser.add_argument(
        "--out", type=Path, default=ROOT / "data" / "achievement_diary_catalog.py"
    )
    args = parser.parse_args()
    document = json.loads(args.harvest.read_text(encoding="utf-8"))
    args.out.write_text(build(document), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
