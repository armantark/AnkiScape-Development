"""Pinned Troll Invasion route, cadence, reward, and breadth-one front data."""

from __future__ import annotations

from typing import Any


TROLL_INVASION_ACTIVITY_ID = "troll_invasion"
TROLL_INVASION_COMBAT_TARGET_ID = "troll_invasion_wave_front"
TROLL_INVASION_REWARD_BOOK = "Troll Invasion reward book"
TROLL_INVASION_COMBAT_MODE = "combat"
TROLL_INVASION_REPAIR_MODE = "repair"
TROLL_INVASION_STANDARD = "standard"
TROLL_INVASION_HARD = "hard"
TROLL_INVASION_MONTH_REVIEWS = 7_200
TROLL_INVASION_REWARD_ALLOWANCE_CAP = 2
TROLL_INVASION_STANDARD_WAVES = 20
TROLL_INVASION_HARD_WAVES = 7
TROLL_INVASION_COMBAT_TICKS = 6
TROLL_INVASION_SUPPLY_USES_PER_WAVE = 5
TROLL_INVASION_REPAIR_TROLL_TARGET = 1_500
TROLL_INVASION_REPAIR_TROLLS_PER_ACTION = 10
TROLL_INVASION_REPAIR_ACTION_CEILING = 167

TROLL_INVASION_SOURCE = (
    "RuneScape Wiki Troll Invasion oldid=6588736 "
    "(2012-11-19T21:28:55Z); "
    "memory-bank/source-audits/troll-invasion-loop-2026-07-18.md"
)

TROLL_INVASION_MODES = (
    {
        "id": TROLL_INVASION_COMBAT_MODE,
        "display_name": "Combat",
        "description": "Fight persistent six-tick wave fronts in the safe arena.",
    },
    {
        "id": TROLL_INVASION_REPAIR_MODE,
        "display_name": "Gatehouse repair",
        "description": "Automatically maintain the most urgent gatehouse component.",
    },
)
TROLL_INVASION_DIFFICULTIES = (
    {
        "id": TROLL_INVASION_STANDARD,
        "display_name": "Standard · 20 waves",
        "waves": TROLL_INVASION_STANDARD_WAVES,
    },
    {
        "id": TROLL_INVASION_HARD,
        "display_name": "Hard · 7 waves",
        "waves": TROLL_INVASION_HARD_WAVES,
    },
)

# PLACEHOLDER(troll_invasion.wave_front_stats): exact aggregate front combat
# values derived from every cutoff wave roster and its priority threats.
def troll_invasion_wave_front_pure(difficulty: str, wave: int) -> dict[str, Any]:
    hard = difficulty == TROLL_INVASION_HARD
    index = max(1, int(wave))
    final_wave = index >= (TROLL_INVASION_HARD_WAVES if hard else TROLL_INVASION_STANDARD_WAVES)
    core = min(99, (42 if hard else 24) + index * (5 if hard else 3))
    lifepoints = (420 if hard else 240) + index * (80 if hard else 35)
    return {
        "display_name": "Cliff and the final troll wave" if final_wave else f"Troll wave {index} front",
        "level": min(138, core + (25 if final_wave else 0)),
        "group": "Troll Invasion",
        "stats": {
            "attack": core,
            "strength": core,
            "defence": core,
            "hitpoints": lifepoints,
            "magic": max(1, core - 8),
            "ranged": max(1, core - 8),
        },
        "bonuses": {},
        "attack_style": "melee",
        "attack_speed": 4,
        "max_hit": max(10, core * 2),
        "drops": {"guaranteed": (), "tables": ()},
        "xp_multiplier": 1.0,
        "encounter_only": True,
        "source": TROLL_INVASION_SOURCE + "; registered breadth-one aggregate front placeholder",
    }


# PLACEHOLDER(troll_invasion.dynamite_supply_chance): authentic chance that a
# Dynamite troll permanently destroys the supply table during a Combat run.
TROLL_INVASION_DYNAMITE_SUPPLY_CHANCE = 0.05

# PLACEHOLDER(troll_invasion.repair_values): exact repair gains, skill XP,
# component pressure, morale gain, and automatic morale-power threshold/effect.
TROLL_INVASION_REPAIR_JOBS = (
    {
        "id": "walls",
        "display_name": "walls",
        "skill_id": "construction",
        "exp_key": "construction_exp",
        "xp": 24.0,
        "repair": 18,
    },
    {
        "id": "barricades",
        "display_name": "barricades",
        "skill_id": "construction",
        "exp_key": "construction_exp",
        "xp": 20.0,
        "repair": 20,
    },
    {
        "id": "ballista",
        "display_name": "ballista ammunition",
        "skill_id": "crafting",
        "exp_key": "crafting_exp",
        "xp": 18.0,
        "repair": 22,
    },
    {
        "id": "oil",
        "display_name": "oil drums",
        "skill_id": "firemaking",
        "exp_key": "firemaking_exp",
        "xp": 16.0,
        "repair": 24,
    },
)
TROLL_INVASION_REPAIR_PRESSURE = 4
TROLL_INVASION_REPAIR_SEVERE_PRESSURE = 30
TROLL_INVASION_REPAIR_INTERRUPTION_CHANCE = 0.10
TROLL_INVASION_REPAIR_SEVERE_PRESSURE_CHANCE = 0.08
TROLL_INVASION_MORALE_PER_ACTION = 8
TROLL_INVASION_MORALE_POWER_THRESHOLD = 100
TROLL_INVASION_MORALE_POWER_REPAIR = 30


TROLL_INVASION_ASSET_MANIFEST = (
    {
        "item_name": "Troll Invasion",
        "wiki_title": "Troll Invasion.png",
        "output_path": "activityicons/troll_invasion.png",
        "size": 64,
    },
    {
        "item_name": TROLL_INVASION_REWARD_BOOK,
        "wiki_title": "Reward book.png",
        "output_path": "activityitems/troll_invasion_reward_book.png",
        "size": 48,
    },
)


def troll_invasion_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        TROLL_INVASION_ACTIVITY_ID: {
            "display_name": "Troll Invasion",
            "requirements": {},
            "skill_requirements": {},
            "outputs": (TROLL_INVASION_REWARD_BOOK,),
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": TROLL_INVASION_SOURCE,
        }
    }


def troll_invasion_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        TROLL_INVASION_REWARD_BOOK: {
            "category": "material",
            "stackable": False,
            "tradeable": False,
            "source": TROLL_INVASION_SOURCE,
        }
    }
