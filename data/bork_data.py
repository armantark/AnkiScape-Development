"""Period-pinned Bork daily encounter and reward data.

Authority: `memory-bank/source-audits/bork-loop-2026-07-18.md` and
`memory-bank/source-audits/bork-daily-loop-2026-07-30.md`.
"""

from __future__ import annotations

from typing import Any


BORK_ACTIVITY_ID = "bork"
BORK_TARGET_ID = "bork"
BORK_QUEST_ID = "hunt_for_surok"
BORK_VARROCK_ELITE_TIER_ID = "varrock_elite"
BORK_RING_OF_WEALTH_ITEM = "Ring of wealth"
BORK_EFFIGY_ITEM = "Starved ancient effigy"
BORK_COIN_ITEM = "Coins"

BORK_WORLD_DAY_REVIEWS = 240
# One review is one six-tick live Combat slice, the house cadence for every
# boss-instance context.
BORK_REVIEW_TICKS = 6

BORK_MAX_LIFEPOINTS = 3000
BORK_MAX_HIT = 254
BORK_ATTACK_SPEED = 6
BORK_COMBAT_LEVEL = 267

# Darkan `Bork.kt` companion constants: the legion is summoned once, when Bork
# drops to 2,000 life points, and its size is `Utils.random(3, 10)`. The period
# page instead says "up to six legions ... at 75% health"; the server constants
# are the exact reading and the page's own drop table already proved the more
# reliable of the two on the charm bundle. Note the unit: `orkCount` counts
# individual npc 7135 spawns, while the page's "legion" is a group of three of
# them, so every counted figure below and in the interface is an ork.
BORK_ORK_SUMMON_THRESHOLD_LIFEPOINTS = 2000
BORK_ORK_SUMMON_MINIMUM = 3
BORK_ORK_SUMMON_MAXIMUM = 9

ORK_LEGION_TARGET_ID = "ork_legion"
ORK_LEGION_COMBAT_LEVEL = 70
ORK_LEGION_LIFEPOINTS = 500
ORK_LEGION_MAX_HIT = 82
ORK_LEGION_SLAYER_XP = 50.0

# `BorkController.process()` fires the mage every `Ticks.fromSeconds(20)` — 33
# ticks — for `Utils.random(100, 251)` magic damage that Protect from Magic
# zeroes outright. The repeat visit spawns the Dagon'hai Elite (npc 7137);
# Surok himself (7136) only appears on the miniquest run.
BORK_MAGE_DISPLAY_NAME = "Dagon'hai Elite"
BORK_MAGE_TICKS_PER_ATTACK = 33
BORK_MAGE_DAMAGE_MINIMUM = 100
BORK_MAGE_DAMAGE_MAXIMUM = 250

# Every kill inside this loop is a repeat kill: the loop only opens once the
# Hunt for Surok miniquest is complete, and that completion already paid the
# sourced 5,000 first-kill Slayer XP. Darkan reads the same way — `drop()`
# awards `repeatKillSlayerXp` only when `!firstKill`.
BORK_REPEAT_SLAYER_XP = 250.0
BORK_ELITE_REPEAT_SLAYER_XP = 500.0

BORK_COIN_RANGE = (2000, 10000)
BORK_ELITE_COIN_RANGE = (4000, 20000)

# Column order is Darkan's `mode` index: default, Ring of Wealth, Varrock
# Elite, both. It reproduces the pinned drop table column for column, which is
# what settles that table against the same revision's prose (4 blue / 7 crimson
# / 3 green). The table and the server agree; the prose stands alone.
BORK_GUARANTEED_DROPS: tuple[tuple[str, tuple[int, int, int, int]], ...] = (
    ("Big bones", (1, 1, 1, 1)),
    ("Blue charm", (5, 5, 10, 10)),
    ("Crimson charm", (7, 10, 14, 17)),
    ("Green charm", (2, 3, 4, 5)),
    ("Uncut diamond", (0, 1, 0, 1)),
    ("Uncut ruby", (1, 2, 2, 3)),
    ("Uncut emerald", (1, 3, 2, 4)),
    ("Uncut sapphire", (1, 0, 2, 1)),
)

# Three independent rolls in Darkan's `drop()`, in this order.
BORK_RARE_DROPS: tuple[tuple[str, float], ...] = (
    (BORK_EFFIGY_ITEM, 1.0 / 64.0),
    ("Clue scroll (elite)", 1.0 / 32.0),
    ("Clue scroll (hard)", 1.0 / 16.0),
)

BORK_SOURCE = (
    "https://runescape.wiki/w/Bork?oldid=6565904; "
    "https://runescape.wiki/w/Ork_legion?oldid=6269351; "
    "darkan-world-server/src/main/java/com/rs/game/content/miniquests/"
    "huntforsurok/bork/Bork.kt; BorkController.kt; "
    "darkan-world-server/data/npcs/combatdefs/uncategorized/"
    "bork (nostats).json; ork_legion (nostats).json"
)

# Darkan rev-727 cache dump, developer-information/npcListBonuses.txt:7136-7137.
# Both npc 7134 and npc 7135 carry an all-zero attack, defence and strength
# array.
_ZERO_BONUSES: dict[str, int] = {
    "attack_stab": 0,
    "attack_slash": 0,
    "attack_crush": 0,
    "attack_magic": 0,
    "attack_ranged": 0,
    "defence_stab": 0,
    "defence_slash": 0,
    "defence_crush": 0,
    "defence_magic": 0,
    "defence_ranged": 0,
    "melee_strength": 0,
    "ranged_strength": 0,
    "magic_damage": 0,
}


def bork_enemy_pure() -> dict[str, Any]:
    return {
        "display_name": "Bork",
        "npc_id": 7134,
        "level": BORK_COMBAT_LEVEL,
        "group": "Bork",
        # PLACEHOLDER(dominion_tower.unsourced_boss_stat_blocks): Darkan's Bork
        # row is a "nostats" file with every combat level zeroed, so the hidden
        # stats use the registered conversion exactly — 72% of the combat level
        # capped at 99, in all four of attack, strength, defence and magic.
        "stats": {
            "hitpoints": BORK_MAX_LIFEPOINTS,
            "attack": 99,
            "strength": 99,
            "defence": 99,
            "magic": 99,
        },
        "bonuses": dict(_ZERO_BONUSES),
        "attack_style": "melee",
        # `Bork` oldid 6565904 prints `immune to poison = Yes`, and Darkan's
        # `Bork.processEntity()` calls `poison.reset()` on every tick.
        "poison_immune": True,
        "attack_bonus": "crush_att",
        "attack_speed": BORK_ATTACK_SPEED,
        "max_hit": BORK_MAX_HIT,
        "drops": {"guaranteed": (), "tables": ()},
        "slayer_xp": 0.0,
        "encounter_only": True,
        "source": BORK_SOURCE,
    }


def ork_legion_enemy_pure() -> dict[str, Any]:
    return {
        "display_name": "Ork legion",
        "npc_id": 7135,
        "level": ORK_LEGION_COMBAT_LEVEL,
        "group": "Bork",
        # PLACEHOLDER(dominion_tower.unsourced_boss_stat_blocks): the legion's
        # combat definition carries no combat-level block at all, so the same
        # registered conversion supplies all four hidden stats.
        "stats": {
            "hitpoints": ORK_LEGION_LIFEPOINTS,
            "attack": 50,
            "strength": 50,
            "defence": 50,
            "magic": 50,
        },
        "bonuses": dict(_ZERO_BONUSES),
        # Darkan Bork.kt:110-111 and 184-205 settles the switch: adjacent orks
        # use melee and distant orks use ranged. The owner-settled collapsed
        # pressure model represents the guide's stand-near-Bork route, so every
        # review uses the authentic adjacent branch rather than inventing
        # distance state for this encounter.
        "attack_style": "melee",
        # `Ork legion` oldid 6269351 prints `immune to poison = Yes`.
        "poison_immune": True,
        "attack_speed": 4,
        "max_hit": ORK_LEGION_MAX_HIT,
        "drops": {"guaranteed": (), "tables": ()},
        "slayer_xp": ORK_LEGION_SLAYER_XP,
        "encounter_only": True,
        "source": BORK_SOURCE,
    }


def bork_guaranteed_drops_pure(
    varrock_elite: bool,
    ring_of_wealth: bool,
    coin_amount: int,
) -> dict[str, int]:
    mode = (2 if varrock_elite else 0) + (1 if ring_of_wealth else 0)
    drops = {
        item_name: quantities[mode]
        for item_name, quantities in BORK_GUARANTEED_DROPS
        if quantities[mode] > 0
    }
    if coin_amount > 0:
        drops[BORK_COIN_ITEM] = coin_amount
    return drops


def bork_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        BORK_ACTIVITY_ID: {
            "display_name": "Bork",
            "requirements": {},
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "outputs": tuple(item_name for item_name, _ in BORK_GUARANTEED_DROPS)
            + tuple(item_name for item_name, _ in BORK_RARE_DROPS),
            "source": BORK_SOURCE,
        }
    }


def bork_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        BORK_EFFIGY_ITEM: {
            "category": "material",
            "stackable": False,
            "tradeable": True,
            "source": (
                "Bork rare drop, 1/64 in Darkan's drop(); "
                "https://runescape.wiki/w/Bork?oldid=6565904"
            ),
        }
    }
