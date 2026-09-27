#!/usr/bin/env python3
"""Generate ``data/achievement_diary_catalog.py`` from the harvested sources.

Run ``tools/harvest_achievement_tasks.py --out <json>`` first; this turns that
document into the checked-in catalog.

Translation rule, applied uniformly and deliberately:

Darkan's rev-727 cache owns task identity, names, descriptions, original tier
membership, and encoded ordinary skill/quest requirements. Regional families
are curated into four twelve-row AnkiScape tiers while keeping stable source
identity and recording any cross-tier placement. If a period family contains
fewer than 48 deeds, explicit progression anchors derived from that family's
sourced requirements fill the remaining one-to-three slots per tier. Ordinary
requirements are access gates, never deed triggers. An un-curated deed remains
visible as dormant until its honest runtime predicate ships.
"""

from __future__ import annotations

import argparse
import ast  # noqa: F401  (re-exported)
import functools  # noqa: F401  (re-exported)
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pkg_alias  # noqa: F401,E402  (installs the ankiscape package alias)
from ankiscape.data.quest_data import quests_as_dict  # noqa: F401,E402  (re-exported)
from tools.achievement_diary_ledger import CURATION_LEDGER, resolve_named_counter, resolve_special_counter  # noqa: F401,E402
from ankiscape.logic_pure.shop_diary_transactions import shop_diary_transaction_counter_key_pure  # noqa: F401,E402
from tools.achievement_diary_generation.condition_keys import QUEST_DATA, resolve_condition_key  # noqa: F401,E402
from tools.achievement_diary_generation.sharding import (  # noqa: E402
    catalog_outputs,
    family_module_source,
)
from tools.achievement_diary_generation.task_conditions import (  # noqa: F401,E402  (re-exports the moved rules)
    CONDITION_OVERRIDES,
    QUEST_COMPLETION_SOURCE_IDS,
    _SKILL_TYPE_IDS,
    _access_gates,
    _condition_src,
    _conditions,
    _requirement_conditions,
    _source_conditions,
)
from tools.generation.outputs import write_or_check  # noqa: E402


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


TASKS_PER_TIER = 12  # design contract: twelve curated tasks in every regional tier
BURTHORPE_CUTOFF_TASKS = 55
TOTAL_CUTOFF_TASKS = 534
MISCELLANEOUS_CUTOFF_TASKS = TOTAL_CUTOFF_TASKS - TASKS_PER_TIER * 32 - BURTHORPE_CUTOFF_TASKS
# PLACEHOLDER(achievement_diaries.misc_coin_reward): the cache proves a minimum
# 100-coin reward and monotonic growth by completed-task count, but not the exact
# curve. The least-assumptive recoverable shape is 100 coins per completion
# ordinal; the server-side payout routine or decoded completion script settles it.
MISC_COIN_BASE = 100

TIER_ORDER = ("beginner", "easy", "medium", "hard", "elite")

# Darkan's SetReward table, plus the taskmaster each tier's reward comes from.
FAMILIES = {
    "ardougne": {
        "name": "Ardougne",
        "item": "Ardougne cloak",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Doctor Orbon", "Town Crier", "Aleck", "Aleck"),
        "taskmaster_chathead": "activityicons/diary_doctor_orbon_chathead.png",
        "lamp": (1000, 7500, 28000, 50000),
    },
    "falador": {
        "name": "Falador",
        "item": "Falador shield",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Redbeard Frank", "Chemist", "Squire", "Squire"),
        "taskmaster_chathead": "activityicons/diary_redbeard_frank_chathead.png",
        "lamp": (1000, 5000, 10000, 50000),
    },
    "fremennik": {
        "name": "Fremennik",
        "item": "Fremennik sea boots",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Council workman", "Yrsa", "Advisor Ghrim", "Advisor Ghrim"),
        "taskmaster_chathead": "activityicons/diary_council_workman_chathead.png",
        "lamp": (5000, 10000, 15000, 40000),
    },
    "karamja": {
        "name": "Karamja",
        "item": "Karamja gloves",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Jackie the fruit trader", "Kaleb Paramaya", "Pirate Jackie the Fruit", "Pirate Jackie the Fruit"),
        "taskmaster_chathead": "activityicons/diary_jackie_the_fruit_trader_chathead.png",
        "lamp": (1000, 5000, 10000, 30000),
    },
    "lumbridge": {
        "name": "Lumbridge and Draynor",
        "item": "Explorer's ring",
        "tiers": ("beginner", "easy", "medium", "hard"),
        "taskmasters": ("Explorer Jack", "Bob", "Ned", "Ned"),
        "taskmaster_chathead": "activityicons/diary_explorer_jack_chathead.png",
        "lamp": (500, 1000, 1500, 9000),
    },
    "morytania": {
        "name": "Morytania",
        "item": "Morytania legs",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Hiylik Myna", "Robin", "Strange Old Man", "Old Man Ral"),
        "taskmaster_chathead": "activityicons/diary_hiylik_myna_chathead.png",
        "lamp": (4000, 10000, 20000, 40000),
    },
    "seers": {
        "name": "Seers' Village",
        "item": "Seer's headband",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Seer", "Stankers", "Sir Kay", "Sir Kay"),
        "taskmaster_chathead": "activityicons/diary_seer_chathead.png",
        "lamp": (1000, 5000, 10000, 25000),
    },
    "varrock": {
        "name": "Varrock",
        "item": "Varrock armour",
        "tiers": ("easy", "medium", "hard", "elite"),
        "taskmasters": ("Rat Burgiss", "Reldo", "Vannaka", "Vannaka"),
        "taskmaster_chathead": "activityicons/diary_rat_burgiss_chathead.png",
        "lamp": (1000, 5000, 10000, 30000),
    },
}

# Preserve source-backed rows that were already shipped when more than twelve
# evaluable tasks compete for a regional tier. Remaining slots keep Darkan order.
PREFERRED_SOURCE_IDS = {
    # Preserve the ten shipped rows, then use the two remaining places for the
    # exact live predicates rather than weaker same-item abstractions.
    ("ardougne", "easy"): (0, 1, 3, 5, 6, 7, 8, 9, 11, 14, 13, 15),
    ("karamja", "medium"): (192, 193, 194, 195, 196, 197, 209, 199, 200, 201, 202, 203),
    ("morytania", "medium"): (957, 958, 960, 962, 963, 964, 965, 966, 968, 970, 971, 972, 973),
}

# Owner-approved generic progression anchors. These are deliberately plain,
# mechanically reachable rows, not invented period deeds. Every level below is
# copied from a real requirement in the same Darkan family roster. Their spread
# keeps each curated tier at twelve rows without putting more than three generic
# anchors in any tier.
PROGRESSION_ANCHORS = {
    ("falador", "easy"): (("strength", 37),),
    ("falador", "medium"): (("woodcutting", 60),),
    ("falador", "hard"): (("mining", 80),),
    ("falador", "elite"): (("cooking", 93),),
    ("fremennik", "easy"): (("strength", 35), ("agility", 35)),
    ("fremennik", "medium"): (("crafting", 52), ("fishing", 55)),
    ("fremennik", "hard"): (("magic", 65), ("slayer", 65)),
    ("fremennik", "elite"): (
        ("hunter", 55),
        ("magic", 65),
        ("herblore", 80),
    ),
    ("karamja", "elite"): (("fishing", 65),),
    ("seers", "easy"): (("crafting", 10), ("mining", 30)),
    ("seers", "medium"): (("fishing", 46), ("magic", 57)),
    ("seers", "hard"): (("fletching", 65), ("smithing", 73)),
    ("seers", "elite"): (("magic", 83), ("fletching", 80)),
}

# Burthorpe/Taverley pays one starter-equipment bundle for the whole set, not a
# per-task reward and not an upgradeable worn item. Darkan's `SetReward` enum
# covers eight areas and deliberately excludes Burthorpe for exactly that
# reason. The bundle is transcribed verbatim from the Rewards section of the
# pinned pre-cutoff revision, which lists it as what Major Nigel Corothers hands
# over during the Arise, Hero cutscene.
BURTHORPE_SET_REWARD = (
    ("Varrock teleport tablet", 5),
    ("Falador teleport tablet", 5),
    ("Attack potion (4)", 5),
    ("Strength potion (4)", 5),
    ("Defence potion (4)", 5),
    ("Prayer potion (4)", 5),
    ("Steel full helm", 1),
)

SPECIAL_FAMILIES = {
    "burthorpe": {
        "name": "Burthorpe and Taverley",
        "kind": "onboarding",
        "tier": "period",
        "tier_name": "Beginner",
        "reward_summary": (
            "The Order of the Talon's starter kit: teleport tablets, a set of"
            " combat potions and a steel full helm."
        ),
        "reward_bundle": BURTHORPE_SET_REWARD,
        "taskmaster": "Major Nigel Corothers",
        "taskmaster_chathead": "activityicons/diary_major_nigel_corothers_chathead.png",
    },
    "miscellaneous": {
        "name": "Miscellaneous",
        "kind": "miscellaneous",
        "tier": "miscellaneous",
        "tier_name": "Miscellaneous",
        "reward_summary": "Each completed task pays its task-system coin reward.",
        "reward_bundle": (),
        "taskmaster": "",
        "taskmaster_chathead": "",
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


def _slug(text: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", text.lower()))[:60]


def _items_yml_blocks(items_yml: Path) -> dict:
    text = items_yml.read_text(encoding="utf-8", errors="ignore")
    blocks = {}
    for block in re.split(r"\n(?=- id: )", text):
        name = re.search(r'name:\s*"([^"]+)"', block)
        if not name:
            continue
        blocks.setdefault(name.group(1), block)
    return blocks


def _items_yml_equipment(item_name: str, blocks: dict) -> tuple:
    """``(item id, slot, bonuses, source)`` for a reward item from its items.yml row."""

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
    return item_id, slot, bonuses, "data/cfg/items.yml item %d; achievement diary tier reward" % item_id


def _equipment_rows(items_yml: Path) -> str:
    blocks = _items_yml_blocks(items_yml)
    rows = []
    for meta in FAMILIES.values():
        for tier_index in range(1, 5):
            item_name = f"{meta['item']} {tier_index}"
            item_id, slot, bonuses, source = (
                MORYTANIA_LEG_BONUSES[item_name]
                if item_name in MORYTANIA_LEG_BONUSES
                else _items_yml_equipment(item_name, blocks)
            )
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


def _task_block(
    family_id: str,
    tier_name: str,
    task: dict,
    source: str,
    *,
    coin_reward: int = 0,
    curation_anchor: bool = False,
    conditions_override: tuple[tuple, ...] | None = None,
    identity_tier: str | None = None,
) -> str:
    task_id = f"{family_id}_{identity_tier or tier_name}_{_slug(task['name'])}"
    conditions = list(conditions_override) if conditions_override is not None else CURATION_LEDGER.conditions_for(task_id, _conditions(task))
    condition_src = ", ".join(_condition_src(condition, task_id) for condition in conditions)
    conditions_line = f"({condition_src},)" if conditions else "()"
    access_gate_src = ", ".join(
        _condition_src(condition, task_id) for condition in _access_gates(task)
    )
    access_gates_line = (
        f"                access_gates=({access_gate_src},),\n"
        if access_gate_src
        else ""
    )
    return (
        "            DiaryTask(\n"
        f"                {task_id!r},\n"
        f"                {CURATION_LEDGER.text_for(task_id, task['name'], task['description'])[0]!r},\n"
        f"                {CURATION_LEDGER.text_for(task_id, task['name'], task['description'])[1]!r},\n"
        f"                {conditions_line},\n"
        f"                {source!r},\n"
        f"                {int(task['id'])},\n"
        f"                {coin_reward},\n"
        f"                {curation_anchor},\n"
        f"{access_gates_line}"
        "            ),"
    )


def _ordered_source_ids(
    record: dict, family_id: str, tier_name: str
) -> tuple[int, ...]:
    source_ids = tuple(record["tiers"][tier_name])
    preferred = PREFERRED_SOURCE_IDS.get((family_id, tier_name), ())
    foreign = sorted(set(preferred) - set(source_ids))
    if foreign:
        raise SystemExit(
            f"{family_id} {tier_name} preferred ids are outside that source tier: {foreign}"
        )
    return preferred + tuple(
        source_id for source_id in source_ids if source_id not in preferred
    )


def _source_tiers(
    family_id: str, tiers: tuple[str, ...], record: dict, definitions: dict
) -> tuple[dict[int, str], dict[str, list[int]]]:
    """Map every source deed to its period tier, and rank each tier sourced-first."""

    source_tier_by_id: dict[int, str] = {}
    ranked_by_tier: dict[str, list[int]] = {}
    for tier_name in tiers:
        ordered = _ordered_source_ids(record, family_id, tier_name)
        for source_id in ordered:
            if source_id in source_tier_by_id:
                raise SystemExit(f"duplicate source task {source_id} in {family_id}")
            source_tier_by_id[source_id] = tier_name
        sourced = [
            source_id
            for source_id in ordered
            if _source_conditions(definitions[str(source_id)])
        ]
        dormant = [source_id for source_id in ordered if source_id not in sourced]
        ranked_by_tier[tier_name] = sourced + dormant
    return source_tier_by_id, ranked_by_tier


def _require_sourced_anchors(
    family_id: str,
    tiers: tuple[str, ...],
    source_tier_by_id: dict[int, str],
    definitions: dict,
) -> None:
    sourced_skill_levels = {
        (
            _SKILL_TYPE_IDS.get(int(requirement.get("skill_type", 0))),
            int(requirement.get("level", 0)),
        )
        for source_id in source_tier_by_id
        for requirement in definitions[str(source_id)].get("requirements", ())
        if requirement.get("kind") == "skill"
    }
    for tier_name in tiers:
        for anchor in PROGRESSION_ANCHORS.get((family_id, tier_name), ()):
            if anchor not in sourced_skill_levels:
                raise SystemExit(
                    f"{family_id} {tier_name} progression anchor {anchor} is not a "
                    "sourced requirement in that family"
                )


def _borrow_deeds(
    family_id: str,
    selected: dict[str, list[tuple[int, str]]],
    authentic_targets: dict[str, int],
    source_tier_by_id: dict[int, str],
    definitions: dict,
) -> None:
    """Top up short tiers with the nearest unused deed, sourced deeds first."""

    tier_index = {tier: index for index, tier in enumerate(authentic_targets)}
    source_order = {source_id: index for index, source_id in enumerate(source_tier_by_id)}
    unused = set(source_tier_by_id) - {
        source_id for rows in selected.values() for source_id, _tier in rows
    }
    for tier_name, authentic_target in authentic_targets.items():
        while len(selected[tier_name]) < authentic_target:
            if not unused:
                raise SystemExit(f"{family_id} cannot fill curated tier {tier_name}")
            source_id = min(
                unused,
                key=lambda candidate: (
                    not bool(_source_conditions(definitions[str(candidate)])),
                    abs(
                        tier_index[source_tier_by_id[candidate]]
                        - tier_index[tier_name]
                    ),
                    source_order[candidate],
                ),
            )
            selected[tier_name].append((source_id, source_tier_by_id[source_id]))
            unused.remove(source_id)


def _refuse_duplicated_anchors(
    family_id: str, selected: dict[str, list[tuple[int, str]]], definitions: dict
) -> None:
    for tier_name, rows in selected.items():
        selected_skill_levels = {
            (condition[1], condition[2])
            for source_id, _original_tier in rows
            for condition in _source_conditions(definitions[str(source_id)])
            if condition[0] == "skill_level"
        }
        for anchor in PROGRESSION_ANCHORS.get((family_id, tier_name), ()):
            if anchor in selected_skill_levels:
                raise SystemExit(
                    f"{family_id} {tier_name} progression anchor {anchor} duplicates "
                    "a selected deed requirement"
                )


def _regional_roster(
    family_id: str,
    meta: dict,
    record: dict,
    definitions: dict,
) -> dict[str, list[tuple[int, str]]]:
    """Return exactly twelve authentic-or-anchor rows for every curated tier."""

    tiers = tuple(meta["tiers"])
    source_tier_by_id, ranked_by_tier = _source_tiers(
        family_id, tiers, record, definitions
    )
    _require_sourced_anchors(family_id, tiers, source_tier_by_id, definitions)
    authentic_targets = {
        tier_name: TASKS_PER_TIER
        - len(PROGRESSION_ANCHORS.get((family_id, tier_name), ()))
        for tier_name in tiers
    }
    if len(source_tier_by_id) < sum(authentic_targets.values()):
        raise SystemExit(f"{family_id} has too few sourced deeds and progression anchors")
    for tier_name, authentic_target in authentic_targets.items():
        if authentic_target < TASKS_PER_TIER - 3:
            raise SystemExit(f"{family_id} {tier_name} exceeds the three-anchor limit")

    selected = {
        tier_name: [
            (source_id, tier_name)
            for source_id in ranked_by_tier[tier_name][:authentic_target]
        ]
        for tier_name, authentic_target in authentic_targets.items()
    }
    _borrow_deeds(family_id, selected, authentic_targets, source_tier_by_id, definitions)
    _refuse_duplicated_anchors(family_id, selected, definitions)
    return selected


def _source(record: dict, family_id: str) -> str:
    wiki = record.get("wiki") or {}
    corroboration = ""
    if wiki.get("oldid"):
        corroboration = (
            f"; corroborated by {wiki.get('title', family_id)} oldid={wiki['oldid']} "
            f"({wiki.get('timestamp', 'n/a')})"
        )
    return (
        f"Darkan {record.get('darkan_class', family_id)}; rev-727 cache enum 3483"
        f"{corroboration}"
    )


def _regional_family_block(
    family_id: str, meta: dict, record: dict, definitions: dict
) -> tuple[str, int]:
    """The ``DiaryFamily`` source of one regional family, and its task count."""

    source = _source(record, family_id)
    curated = _regional_roster(family_id, meta, record, definitions)
    tier_blocks: list[str] = []
    for index, tier_name in enumerate(meta["tiers"]):
        darkan_ids = record["tiers"][tier_name]
        task_blocks: list[str] = []
        for source_id, original_tier in curated[tier_name]:
            task_source = source
            if original_tier != tier_name:
                task_source += (
                    f"; original period tier {original_tier}; curated into {tier_name}"
                )
            task_blocks.append(
                _task_block(
                    family_id, tier_name, definitions[str(source_id)], task_source,
                    identity_tier=original_tier,
                )
            )
        for anchor_index, (skill_id, level) in enumerate(
            PROGRESSION_ANCHORS.get((family_id, tier_name), ()), start=1
        ):
            display = skill_id.replace("_", " ").title()
            anchor = {
                "id": 900000 + list(FAMILIES).index(family_id) * 100 + index * 10 + anchor_index,
                "name": f"Reach Level {level} {display}",
                "description": "An AnkiScape curation anchor, not a period task identity.",
            }
            anchor_source = (
                f"AnkiScape progression anchor derived from Darkan "
                f"{record.get('darkan_class', family_id)} and rev-727 cache enum 3483 "
                "requirement rows; not a period task identity"
            )
            task_blocks.append(
                _task_block(
                    family_id, tier_name, anchor, anchor_source, curation_anchor=True,
                    conditions_override=(
                        ("skill_level", skill_id, level, f"Level {level} {display}"),
                    ),
                )
            )
        if len(task_blocks) != TASKS_PER_TIER:
            raise SystemExit(
                f"{family_id} {tier_name} generated {len(task_blocks)} tasks, expected 12"
            )
        label = tier_name.capitalize()
        reward_item = f"{meta['item']} {index + 1}"
        reward = TIER_REWARDS.get((family_id, tier_name), f"{label} {meta['name']} task rewards.")
        lamp_placeholder_id = f"achievement_diaries.{family_id}.{tier_name}.lamp_minimum_level"
        tier_blocks.append(
            "        DiaryTier(\n"
            f"            {family_id + '_' + tier_name!r},\n"
            f"            {label!r},\n"
            f"            {index + 1},\n"
            f"            {reward_item!r},\n"
            f"            {reward!r},\n"
            "            (\n" + "\n".join(task_blocks) + "\n            ),\n"
            f"            # PLACEHOLDER({lamp_placeholder_id}): the exact period\n"
            "            # lamp floor is not recorded in the repository. A period lamp\n"
            "            # dialogue or cache interface script would settle this tier.\n"
            f"            DiaryLamp({meta['lamp'][index]}, 1),\n"
            f"            {'period tier: ' + str(len(darkan_ids)) + ' tasks; ' + source!r},\n"
            f"            designed_task_count={TASKS_PER_TIER},\n"
            "        ),"
        )
    family_block = (
        "DiaryFamily(\n"
        f"        {family_id!r},\n"
        f"        {meta['name']!r},\n"
        "        'regional',\n"
        "        (\n" + "\n".join(tier_blocks) + "\n        ),\n"
        f"        {meta['taskmasters'][0]!r},\n"
        f"        {meta['taskmaster_chathead']!r},\n"
        f"        {source!r},\n"
        "    )"
    )
    return family_block, TASKS_PER_TIER * len(tier_blocks)


def _special_family_block(
    family_id: str, meta: dict, record: dict, definitions: dict
) -> tuple[str, int]:
    """The ``DiaryFamily`` source of one single-pool family, and its task count."""

    source = _source(record, family_id)
    tier_name = meta["tier"]
    coin_reward = MISC_COIN_BASE if family_id == "miscellaneous" else 0
    task_blocks = [
        _task_block(
            family_id, tier_name, definitions[str(source_id)], source,
            coin_reward=coin_reward,
        )
        for source_id in record["tiers"][tier_name]
    ]
    designed_task_count = (
        BURTHORPE_CUTOFF_TASKS if family_id == "burthorpe" else MISCELLANEOUS_CUTOFF_TASKS
    )
    family_block = (
        "DiaryFamily(\n"
        f"        {family_id!r},\n"
        f"        {meta['name']!r},\n"
        f"        {meta['kind']!r},\n"
        "        (\n"
        "        DiaryTier(\n"
        f"            {family_id + '_' + tier_name!r},\n"
        f"            {meta['tier_name']!r},\n"
        "            1,\n"
        "            '',\n"
        f"            {meta['reward_summary']!r},\n"
        "            (\n" + "\n".join(task_blocks) + "\n            ),\n"
        "            None,\n"
        f"            {'period pool: ' + str(len(record['tiers'][tier_name])) + ' tasks; ' + source!r},\n"
        f"            {meta['reward_bundle']!r},\n"
        f"            designed_task_count={designed_task_count},\n"
        "        ),\n"
        "        ),\n"
        f"        {meta['taskmaster']!r},\n"
        f"        {meta['taskmaster_chathead']!r},\n"
        f"        {source!r},\n"
        "    )"
    )
    return family_block, len(task_blocks)


def build(document: dict, items_yml: Path) -> dict[str, str]:
    CURATION_LEDGER.begin()
    families = document["families"]
    definitions = document["task_definitions"]
    rendered = {
        family_id: _regional_family_block(family_id, meta, families[family_id], definitions)
        for family_id, meta in FAMILIES.items()
    } | {
        family_id: _special_family_block(family_id, meta, families[family_id], definitions)
        for family_id, meta in SPECIAL_FAMILIES.items()
    }
    CURATION_LEDGER.assert_complete()
    return catalog_outputs(
        {family_id: family_module_source(block) for family_id, (block, _count) in rendered.items()},
        sum(count for _block, count in rendered.values()),
        TOTAL_CUTOFF_TASKS,
        _equipment_rows(items_yml),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("harvest", type=Path)
    parser.add_argument(
        "--items-yml",
        type=Path,
        required=True,
        help="2011Scape data/cfg/items.yml used for diary reward equipment rows",
    )
    parser.add_argument(
        "--out", type=Path, default=ROOT / "data" / "achievement_diary_catalog.py"
    )
    parser.add_argument("--check", action="store_true", help="compare with the existing files instead of writing")
    args = parser.parse_args(argv)
    document = json.loads(args.harvest.read_text(encoding="utf-8"))
    outputs = build(document, args.items_yml)
    return write_or_check(
        {
            args.out if relative_path == "achievement_diary_catalog.py" else args.out.parent / relative_path: source
            for relative_path, source in outputs.items()
        },
        check=args.check,
    )


if __name__ == "__main__":
    raise SystemExit(main())
