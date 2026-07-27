#!/usr/bin/env python3
"""Generate ``data/achievement_diary_catalog.py`` from the harvested sources.

Run ``tools/harvest_achievement_tasks.py --out <json>`` first; this turns that
document into the checked-in catalog.

Translation rule, applied uniformly and deliberately:

Darkan's rev-727 cache owns the task name, description, and encoded ordinary
skill/quest requirements. Regional tiers retain the first twelve source-order
tasks that have an evaluable predicate. Burthorpe/Taverley and Miscellaneous
retain every source task with either an encoded requirement or an audited exact
mapping to an existing durable gameplay counter. Tasks with no honest predicate
are omitted and reported rather than emitted as inert rows.
"""

from __future__ import annotations

import argparse
import ast
import functools
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pkg_alias  # noqa: F401,E402  (installs the ankiscape package alias)
from ankiscape.data.quest_data import quests_as_dict  # noqa: E402

QUEST_DATA = quests_as_dict()


# ---------------------------------------------------------------------------
# Condition key resolution
# ---------------------------------------------------------------------------
#
# A condition whose key names nothing the runtime writes reads zero forever, so
# the row can never complete. That failure is silent: the panel renders an
# honest-looking 0/1. ``resolve_condition_key`` is the check that turns it into
# a generation failure, and ``tests/test_achievement_diaries.py`` runs the same
# check over the shipped catalog so a hand-edit cannot slip past it either.

# Where each skill's action ids come from. A skill absent here is refused rather
# than waved through, because "no registry" must never read as "anything goes".
_SKILL_ACTION_REGISTRIES = {
    "agility": ("ankiscape.core.constants", "AGILITY_TARGETS_BY_ID"),
    "construction": ("ankiscape.core.constants", "CONSTRUCTION_DATA"),
    "cooking": ("ankiscape.core.constants", "COOKING_DATA"),
    "crafting": ("ankiscape.core.constants", "CRAFTING_DATA"),
    "firemaking": ("ankiscape.core.constants", "FIREMAKING_DATA"),
    "fishing": ("ankiscape.core.constants", "FISHING_DATA"),
    "fletching": ("ankiscape.core.constants", "FLETCHING_DATA"),
    "herblore": ("ankiscape.core.constants", "HERBLORE_DATA"),
    "hunter": ("ankiscape.core.constants", "HUNTER_DATA"),
    "magic": ("ankiscape.core.constants", "MAGIC_DATA"),
    "mining": ("ankiscape.core.constants", "ORE_DATA"),
    "prayer": ("ankiscape.core.constants", "PRAYER_DATA"),
    "runecrafting": ("ankiscape.core.constants", "RUNECRAFTING_DATA"),
    "smithing": ("ankiscape.core.constants", "SMITHING_DATA"),
    "utility": ("ankiscape.core.constants", "UTILITY_ACTIVITY_DATA"),
    "woodcutting": ("ankiscape.core.constants", "TREE_DATA"),
}

# Where the ledger is written from. Activity runtimes record actions whose ids
# are literals rather than rows of a skill's target table, so the registries
# above are unioned with every literal pair these files actually emit.
_LEDGER_WRITE_SITES = ("runtime", "logic")
_LEDGER_WRITE_CALLS = ("_record_action", "record_achievement_progress_pure")


def _import_attr(module_name: str, attribute: str):
    import importlib

    return getattr(importlib.import_module(module_name), attribute)


@functools.lru_cache(maxsize=1)
def _module_level_strings() -> dict:
    """Every ``NAME = "literal"`` in the add-on, for resolving action-id names.

    Activity runtimes pass constants such as ``SHOOTING_STAR_ACTIVITY_ID``
    rather than a bare string, and those constants are the action id.
    """

    found: dict[str, set] = {}
    for path in ROOT.rglob("*.py"):
        if any(part in {".git", "__pycache__", "tests"} for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        for node in tree.body:
            if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Constant):
                continue
            if not isinstance(node.value.value, str):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    found.setdefault(target.id, set()).add(node.value.value)
    return found


def _literal_strings(node: ast.AST) -> set:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.Name):
        return set(_module_level_strings().get(node.id, ()))
    return set()


@functools.lru_cache(maxsize=1)
def _emitted_ledger_actions() -> dict:
    """``skill id -> action ids`` the runtime can actually record."""

    emitted: dict[str, set] = {}
    for skill_id, (module_name, attribute) in _SKILL_ACTION_REGISTRIES.items():
        emitted[skill_id] = set(_import_attr(module_name, attribute))
    for directory in _LEDGER_WRITE_SITES:
        for path in (ROOT / directory).rglob("*.py"):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or len(node.args) < 3:
                    continue
                function = node.func
                name = getattr(function, "id", None) or getattr(function, "attr", None)
                if name not in _LEDGER_WRITE_CALLS:
                    continue
                for skill_id in _literal_strings(node.args[1]):
                    emitted.setdefault(skill_id, set()).update(
                        _literal_strings(node.args[2])
                    )
    return emitted


@functools.lru_cache(maxsize=1)
def _emitted_ledger_outputs() -> dict:
    """``skill id -> output item names`` the ledger can hold under that skill."""

    from ankiscape.core.storage_pure import _achievement_seed_items

    emitted = {
        skill_id: set(items) for skill_id, items in _achievement_seed_items().items()
    }
    for skill_id, (module_name, attribute) in _SKILL_ACTION_REGISTRIES.items():
        bucket = emitted.setdefault(skill_id, set())
        for spec in _import_attr(module_name, attribute).values():
            if not isinstance(spec, dict):
                continue
            if spec.get("output_item"):
                bucket.add(str(spec["output_item"]))
            bucket.update(str(name) for name in (spec.get("outputs") or {}))
    return emitted


@functools.lru_cache(maxsize=1)
def _default_save() -> dict:
    from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
    from ankiscape.core.storage_pure import default_player_data

    return default_player_data(ORE_DATA, ITEM_DEFINITIONS)


def _resolve_ledger_key(kind: str, key: str) -> str:
    skill_id, separator, action_id = key.partition(":")
    if not separator or not skill_id or not action_id:
        return f"{kind} key {key!r} is not '<skill id>:<id>'"
    registry = (
        _emitted_ledger_outputs() if kind == "ledger_output" else _emitted_ledger_actions()
    )
    if skill_id not in registry:
        return (
            f"{kind} key {key!r} names skill {skill_id!r}, which has no registry;"
            " add it to _SKILL_ACTION_REGISTRIES before shipping a row under it"
        )
    if action_id not in registry[skill_id]:
        return f"{kind} key {key!r} is never recorded under skill {skill_id!r}"
    return ""


def resolve_condition_key(kind: str, key: str) -> str:
    """Return an error describing why ``key`` reads nothing, or ``""``."""

    if kind in {"ledger_action", "ledger_output"}:
        return _resolve_ledger_key(kind, key)
    if kind == "derived_value":
        registry = _import_attr(
            "ankiscape.logic.achievement_diary_derived", "DIARY_DERIVED_VALUES"
        )
        ceilings = _import_attr(
            "ankiscape.logic.achievement_diary_derived", "DIARY_DERIVED_VALUE_CEILINGS"
        )
        if key not in registry:
            return f"derived_value {key!r} is not in DIARY_DERIVED_VALUES"
        if key not in ceilings:
            return f"derived_value {key!r} has no DIARY_DERIVED_VALUE_CEILINGS entry"
        return ""
    if kind != "counter":
        return ""
    parts = key.split(".")
    if parts[0] == "combat_kill_counts":
        from ankiscape.core.constants import COMBAT_ENEMY_DATA

        if len(parts) != 2 or parts[1] not in COMBAT_ENEMY_DATA:
            return f"counter key {key!r} names no enemy in COMBAT_ENEMY_DATA"
        return ""
    # The ledger is reachable as a dotted path too, and a fresh save carries no
    # per-skill record, so route those through the ledger registries instead of
    # the save walk below.
    if parts[:2] == ["achievement_progress", "skills"] and len(parts) == 5:
        bucket = {"actions": "ledger_action", "outputs": "ledger_output"}.get(parts[3])
        if bucket is None:
            return f"counter key {key!r} names no ledger bucket"
        return _resolve_ledger_key(bucket, f"{parts[2]}:{parts[4]}")
    node = _default_save()
    for index, part in enumerate(parts):
        if not isinstance(node, dict):
            return f"counter key {key!r} walks through a non-mapping at {part!r}"
        if part not in node:
            if index == len(parts) - 1:
                return ""  # an absent per-key leaf is the zero case, not a typo
            return f"counter key {key!r} has no {part!r} in a default save"
        node = node[part]
    return ""


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

# Preserve source-backed rows that were already shipped when more than twelve
# evaluable tasks compete for a regional tier. Remaining slots keep Darkan order.
PREFERRED_SOURCE_IDS = {
    ("karamja", "medium"): (192, 193, 194, 195, 196, 197, 209, 199, 200, 201, 202, 203),
    ("morytania", "medium"): (957, 958, 960, 962, 963, 964, 966, 968, 970, 971, 972, 973),
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
    },
    "miscellaneous": {
        "name": "Miscellaneous",
        "kind": "miscellaneous",
        "tier": "miscellaneous",
        "tier_name": "Miscellaneous",
        "reward_summary": "Each completed task pays its task-system coin reward.",
        "reward_bundle": (),
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

# AchievementDef.toRealSkillId(), translated to AnkiScape skill ids.
_SKILL_TYPE_IDS = {
    1: "attack",
    2: "strength",
    3: "ranged",
    4: "magic",
    5: "defense",
    6: "constitution",
    7: "prayer",
    8: "agility",
    9: "herblore",
    10: "thieving",
    11: "crafting",
    12: "runecrafting",
    13: "mining",
    14: "smithing",
    15: "fishing",
    16: "cooking",
    17: "woodcutting",
    18: "fletching",
    19: "firemaking",
    20: "slayer",
    21: "farming",
    22: "construction",
    23: "hunter",
    24: "summoning",
    25: "dungeoneering",
}


def _normalise_name(text: str) -> str:
    return "".join(re.findall(r"[a-z0-9]+", text.lower()))


_QUEST_IDS = {}
for _quest_id, _record in QUEST_DATA.items():
    if not isinstance(_record, dict):
        continue
    for _name in (_quest_id, str(_record.get("display_name", ""))):
        _normalised = _normalise_name(_name)
        _QUEST_IDS[_normalised] = _quest_id
        for _prefix in ("the", "a"):
            if _normalised.startswith(_prefix):
                _QUEST_IDS[_normalised[len(_prefix) :]] = _quest_id

# Exact action/counter translations for source tasks whose cache struct carries
# no ordinary skill or quest requirement. Every entry names a durable state seam
# already produced by the live engine; absent entries are deliberately omitted.
CONDITION_OVERRIDES = {
    538: (("hold_item", "Bronze pickaxe", 1, "Own a bronze pickaxe"),),
    546: (("ledger_action", "hunter:catch_crimson_swift", 1, "Catch a crimson swift"),),
    555: (("counter", "slayer_tasks_completed", 1, "Complete a Slayer assignment"),),
    562: (("ledger_action", "fletching:bronze_arrows", 1, "Fletch bronze arrows"),),
    564: (("ledger_action", "fletching:string_shortbow", 1, "Fletch a shortbow"),),
    566: (("ledger_action", "herblore:clean_guam", 1, "Clean guam"),),
    567: (("ledger_action", "herblore:finished_attack_potion", 1, "Brew an attack potion"),),
    574: (("ledger_action", "agility:burthorpe_course", 1, "Complete the Burthorpe Agility Course"),),
    580: (("counter", "house_owned", 1, "Own a player house"),),
    582: (("ledger_action", "construction:crude_wooden_chair", 1, "Build a crude wooden chair"),),
    570: (("ledger_action", "runecrafting:craft_mind_runes", 1, "Craft mind runes"),),
    451: (("quest", "let_them_eat_pie", 1, "Complete Let Them Eat Pie"),),
    440: (("quest", "druidic_ritual", 1, "Complete Druidic Ritual"),),
    441: (("quest", "death_plateau", 1, "Complete Death Plateau"),),
}

# Darkan confirms these tasks' exact tier membership. Their ordinary requirement
# pairs are absent from enum 3483 but present in the already-pinned pre-cutoff
# family tables, so retaining the earlier requirement predicates loses no source
# fidelity and avoids treating cache absence as evidence that a task was invalid.
CONDITION_OVERRIDES.update({
    0: (("quest", "rune_mysteries", 1, "Complete Rune Mysteries"),),
    125: (("quest", "rune_mysteries", 1, "Complete Rune Mysteries"),),
    188: (("skill_level", "fishing", 5, "Level 5 Fishing"),),
    192: (("skill_level", "agility", 40, "Level 40 Agility"),),
    209: (("quest", "shilo_village", 1, "Complete Shilo Village"),),
    97: (("quest", "rune_mysteries", 1, "Complete Rune Mysteries"),),
    107: (("quest", "dragon_slayer", 1, "Complete Dragon Slayer"),),
    952: (("quest", "in_aid_of_the_myreque", 1, "Complete In Aid of the Myreque"),),
    993: (("quest", "ritual_of_the_mahjarrat", 1, "Complete Ritual of the Mahjarrat"),),
    985: (
        ("skill_level", "runecrafting", 50, "Level 50 Runecrafting"),
        ("quest", "legacy_of_seergaze", 1, "Complete Legacy of Seergaze"),
    ),
    983: (("quest", "in_aid_of_the_myreque", 1, "Complete In Aid of the Myreque"),),
    963: (("quest", "ghosts_ahoy", 1, "Complete Ghosts Ahoy"),),
    971: (("quest", "in_search_of_the_myreque", 1, "Complete In Search of the Myreque"),),
    964: (("quest", "in_aid_of_the_myreque", 1, "Complete In Aid of the Myreque"),),
    257: (("quest", "rune_mysteries", 1, "Complete Rune Mysteries"),),
    268: (("quest", "the_dig_site", 1, "Complete The Dig Site"),),
    267: (("skill_level", "construction", 10, "Level 10 Construction"),),
    291: (("quest", "garden_of_tranquillity", 1, "Complete Garden of Tranquillity"),),
})

# Exact terminal counters in the implemented activity families. Activities with
# no durable gameplay proof are omitted unless enum 3483 supplies an ordinary
# evaluable prerequisite of its own.
CONDITION_OVERRIDES.update({
    3000: (("counter", "tears_of_guthix.visits", 1, "Complete a Tears of Guthix visit"),),
    3002: (("counter", "penguin_hide_and_seek.lifetime_spotted", 1, "Spy a penguin"),),
    3003: (("counter", "achievement_progress.skills.woodcutting.actions.evil_tree_fell", 1, "Fell an evil tree"),),
    3004: (("counter", "achievement_progress.skills.mining.actions.shooting_stars", 1, "Mine a shooting star"),),
    3005: (("counter", "achievement_progress.skills.hunter.actions.catch_baby_impling_puro_puro", 1, "Catch an impling in Puro-Puro"),),
    3006: (("counter", "vinesweeper.operations", 1, "Complete a Vinesweeper operation"),),
    3007: (("counter", "circus.lifetime_performances", 1, "Complete a circus performance"),),
    3009: (("quest", "all_fired_up", 1, "Complete All Fired Up"),),
    3010: (("counter", "skeletal_horror.kills", 1, "Defeat the Skeletal Horror"),),
    3012: (("counter", "great_orb_project.games_completed", 1, "Complete a Great Orb Project game"),),
    3013: (("counter", "pest_control_games_won", 1, "Win a Pest Control game"),),
    3014: (("counter", "castle_wars_games_played", 1, "Complete a Castle Wars game"),),
    3015: (("counter", "court_cases_attempts", 1, "Argue a court case"),),
    3017: (("counter", "fight_caves.clears", 1, "Clear the Fight Caves"),),
    3018: (("counter", "tzhaar_fight_pit_matches", 1, "Enter a Fight Pit match"),),
    3019: (("counter", "achievement_progress.skills.agility.outputs.Agility arena ticket", 1, "Earn an Agility arena ticket"),),
    3020: (("counter", "barbarian_assault_runs_completed", 1, "Complete a Barbarian Assault run"),),
    3022: (("counter", "shades_of_mortton_chests_opened", 1, "Open a Shades of Mort'ton chest"),),
    3023: (("counter", "barrows.chests_opened", 1, "Open a Barrows chest"),),
    3024: (("counter", "pyramid_plunder_runs_completed", 1, "Complete a Pyramid Plunder run"),),
    3025: (("counter", "sorceress_garden.successful_trips", 1, "Complete a Sorceress's Garden trip"),),
    3027: (("counter", "duel_arena_matches", 1, "Enter a Duel Arena match"),),
    3028: (("counter", "fist_of_guthix.matches_started", 1, "Enter a Fist of Guthix match"),),
    3029: (("counter", "stealing_creation.games", 1, "Enter a Stealing Creation game"),),
    3030: (("counter", "soul_wars_games_played", 1, "Complete a Soul Wars game"),),
    3031: (("counter", "clan_wars_matches", 1, "Enter a Clan Wars match"),),
    3034: (("counter", "warriors_guild.activity_reviews.warriors_guild_attack_dummy", 1, "Train in the Warriors' Guild"),),
})


def _kill_any_of(label: str, verb: str, enemy_ids: tuple) -> tuple:
    """An ``any_of`` over the kill counters of one species' level variants.

    The period wrote several tasks as "kill a giant rat"; AnkiScape stores one
    counter per level variant, so the honest predicate is the disjunction over
    every variant of that species rather than an arbitrary pick of one.
    """

    from ankiscape.core.constants import COMBAT_ENEMY_DATA

    alternatives = []
    for enemy_id in enemy_ids:
        display = str(COMBAT_ENEMY_DATA[enemy_id]["display_name"]).lower()
        level = re.search(r"_level_(\d+)$", enemy_id)
        if level:
            display = f"{display} (level {level.group(1)})"
        article = "an" if display[0] in "aeiou" else "a"
        alternatives.append(
            (
                "counter",
                f"combat_kill_counts.{enemy_id}",
                1,
                f"{verb} {article} {display}",
            )
        )
    return ("any_of", "", 1, label, tuple(alternatives))


# Source tasks the cache states as a disjunction, or that name one period NPC
# AnkiScape stores as several level variants. Each was previously omitted for
# want of a predicate that could express "any of these".
CONDITION_OVERRIDES.update({
    190: (
        (
            "any_of", "", 1, "Attempt a TzHaar Fight Pit match or the Fight Caves",
            (
                ("counter", "tzhaar_fight_pit_matches", 1, "Enter a Fight Pit match"),
                ("counter", "fight_caves.total_kills", 1, "Land a Fight Caves kill"),
            ),
        ),
    ),
    953: (
        _kill_any_of(
            "Kill a Slayer Tower ground-floor monster",
            "Kill",
            ("crawling_hand", "banshee", "infernal_mage"),
        ),
    ),
    85: (
        _kill_any_of(
            "Defeat a zombie",
            "Defeat",
            tuple(f"zombie_level_{level}" for level in (13, 18, 24, 25, 30, 44, 53)),
        ),
    ),
    93: (
        _kill_any_of(
            "Kill a giant rat",
            "Kill",
            ("giant_rat", "giant_rat_level_6", "giant_rat_level_26"),
        ),
    ),
    123: (
        _kill_any_of("Kill a duck", "Kill", ("duck_land", "duck_water")),
    ),
})

# Kudos is a weighted sum over three append-only museum records, so no leaf
# holds it and a counter would read zero forever. Task 268 was already shipped
# on its quest half alone; the Kudos half it always stated is now evaluated too.
CONDITION_OVERRIDES.update({
    300: (
        ("derived_value", "varrock_museum_kudos", 153, "Earn 153 Kudos"),
    ),
    268: (
        ("quest", "the_dig_site", 1, "Complete The Dig Site"),
        ("derived_value", "varrock_museum_kudos", 50, "Earn 50 Kudos"),
    ),
})


def _slug(text: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", text.lower()))[:60]


def _quest_id(source_name: str) -> str:
    return _QUEST_IDS.get(_normalise_name(source_name.replace("_", " ")), "")


def _conditions(task: dict) -> list[tuple]:
    task_id = int(task["id"])
    override = CONDITION_OVERRIDES.get(task_id)
    if override is not None:
        return list(override)

    conditions: list[tuple] = []
    for requirement in task.get("requirements", ()):
        kind = requirement.get("kind")
        if kind == "skill":
            skill_id = _SKILL_TYPE_IDS.get(int(requirement.get("skill_type", 0)))
            level = int(requirement.get("level", 0))
            if skill_id and level > 1:
                display = skill_id.replace("_", " ").title()
                conditions.append(("skill_level", skill_id, level, f"Level {level} {display}"))
        elif kind == "quest":
            source_name = str(requirement.get("quest", ""))
            quest_id = _quest_id(source_name)
            if quest_id:
                display = str(QUEST_DATA[quest_id].get("display_name", quest_id.replace("_", " ").title()))
                conditions.append(("quest", quest_id, 1, f"Complete {display}"))
    return conditions


def _condition_src(condition: tuple) -> str:
    """Serialise one condition, refusing any key the runtime never writes."""

    kind, key, amount, label = condition[:4]
    alternatives = condition[4] if len(condition) > 4 else ()
    error = resolve_condition_key(kind, key)
    if error:
        raise SystemExit(f"unresolvable diary condition ({label}): {error}")
    if kind == "derived_value":
        ceiling = _import_attr(
            "ankiscape.logic.achievement_diary_derived", "DIARY_DERIVED_VALUE_CEILINGS"
        )[key]
        if amount > ceiling:
            raise SystemExit(
                f"derived_value {key!r} threshold {amount} is above the implemented"
                f" ceiling {ceiling}, so the row could never complete"
            )
    if kind != "any_of":
        return f"DiaryCondition({kind!r}, {key!r}, {amount}, {label!r})"
    if not alternatives:
        raise SystemExit(f"any_of condition {label!r} carries no alternatives")
    for alternative in alternatives:
        if alternative[0] == "any_of":
            raise SystemExit(f"any_of condition {label!r} nests another any_of")
    inner = ", ".join(_condition_src(alternative) for alternative in alternatives)
    return f"DiaryCondition({kind!r}, {key!r}, {amount}, {label!r}, ({inner},))"


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


def _task_block(
    family_id: str,
    tier_name: str,
    task: dict,
    source: str,
    *,
    coin_reward: int = 0,
) -> str:
    conditions = _conditions(task)
    if not conditions:
        return ""
    task_id = f"{family_id}_{tier_name}_{_slug(task['name'])}"
    condition_src = ", ".join(_condition_src(condition) for condition in conditions)
    return (
        "            DiaryTask(\n"
        f"                {task_id!r},\n"
        f"                {task['name']!r},\n"
        f"                {task['description']!r},\n"
        f"                ({condition_src},),\n"
        f"                {source!r},\n"
        f"                {int(task['id'])},\n"
        f"                {coin_reward},\n"
        "            ),"
    )


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


def build(document: dict) -> str:
    lines: list[str] = []
    families = document["families"]
    definitions = document["task_definitions"]
    kept_total = 0

    for family_id, meta in FAMILIES.items():
        record = families[family_id]
        source = _source(record, family_id)
        tier_blocks: list[str] = []
        for index, tier_name in enumerate(meta["tiers"]):
            darkan_ids = record["tiers"][tier_name]
            preferred = PREFERRED_SOURCE_IDS.get((family_id, tier_name), ())
            ordered_ids = preferred + tuple(
                source_id for source_id in darkan_ids if source_id not in preferred
            )
            task_blocks: list[str] = []
            for source_id in ordered_ids:
                task = definitions[str(source_id)]
                block = _task_block(family_id, tier_name, task, source)
                if not block:
                    continue
                task_blocks.append(block)
                if len(task_blocks) >= TASKS_PER_TIER:
                    break
            kept_total += len(task_blocks)
            label = tier_name.capitalize()
            reward_item = f"{meta['item']} {index + 1}"
            reward = TIER_REWARDS.get(
                (family_id, tier_name), f"{label} {meta['name']} task rewards."
            )
            tier_blocks.append(
                "        DiaryTier(\n"
                f"            {family_id + '_' + tier_name!r},\n"
                f"            {label!r},\n"
                f"            {index + 1},\n"
                f"            {reward_item!r},\n"
                f"            {reward!r},\n"
                "            (\n" + "\n".join(task_blocks) + "\n            ),\n"
                f"            DiaryLamp({meta['lamp'][index]}, 1),\n"
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

    for family_id, meta in SPECIAL_FAMILIES.items():
        record = families[family_id]
        source = _source(record, family_id)
        tier_name = meta["tier"]
        task_blocks = []
        for source_id in record["tiers"][tier_name]:
            task = definitions[str(source_id)]
            block = _task_block(
                family_id,
                tier_name,
                task,
                source,
                coin_reward=MISC_COIN_BASE if family_id == "miscellaneous" else 0,
            )
            if block:
                task_blocks.append(block)
        kept_total += len(task_blocks)
        lines.append(
            "    DiaryFamily(\n"
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
            "        ),\n"
            "        ),\n"
            "        '',\n"
            f"        {source!r},\n"
            "    ),"
        )
    header = (
        '"""Generated by ``tools/generate_achievement_diary_data.py``. Do not hand-edit.\n\n'
        "Darkan's achievement classes and rev-727 cache enum 3483 own task identity,\n"
        "tier membership, names, descriptions and ordinary requirements. Pinned\n"
        "pre-cutoff wiki revisions are corroboration only. Tasks without an honest\n"
        "AnkiScape predicate are omitted rather than emitted as inert rows.\n\n"
        f"Tasks kept: {kept_total}.\"\"\"\n\n"
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
        "# settle it.\n\n"
        "# PLACEHOLDER(achievement_diaries.misc_coin_reward): miscellaneous rewards use\n"
        "# the cache-proven 100-coin floor multiplied by completion ordinal. The exact\n"
        "# period curve needs the server payout routine or decoded completion script.\n\n\n"
        "DIARY_FAMILIES = (\n"
    )
    equipment = (
        "\n\ndef diary_equipment_data_as_dict() -> dict:\n"
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
