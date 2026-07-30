"""Period-pinned Dominion Tower roster, handicap wheel, and reward ladder.

Released 2011-11-01, thirteen months inside the 2012-11-20 cutoff. The tower
re-fights quest bosses, so every encounter carries the quest that unlocks it and
nothing appears until the real quest ledger says that quest is complete.

Sources, in the house evidence order:

- Darkan `darkan-world-server/src/main/java/com/rs/game/content/minigames/
  domtower/DominionTower.java` supplies the two mode multipliers, the maximum
  Dominion Factor, and the claim-resets-progress rule. Its own boss list is
  marked `// custom bosses` and its `getBossesTotalLevel` has a `level = +`
  typo, so only the shape is taken from it, never the roster.
- Darkan `data/npcs/combatdefs/**.json` supplies lifepoints, maximum hits, and
  combat-stat blocks for two thirds of the roster.
- The rev-727 cache dump `developer-information/npcListBonuses.txt` supplies NPC
  ids, client combat levels, and the ten attack/defence bonus values plus the
  three strength values for nearly every NPC named here.
- `Dominion Tower` oldid 6563470 (2012-11-16T06:18:29Z) supplies the entry
  gates, the five modes, the eight boss classes with their floor gates, the
  complete 22-row handicap wheel with its per-round factor deltas, the ten
  special matches, and the achievement ladder.
- Per-boss wiki revisions are pinned on each NPC row.
"""

from __future__ import annotations

import copy
from typing import Any


DOMINION_TOWER_ACTIVITY_ID = "dominion_tower"
DOMINION_TOWER_TARGET_ID = "dominion_tower"

DOMINION_TOWER_WIKI_SOURCE = "https://runescape.wiki/w/Dominion_Tower?oldid=6563470"
DOMINION_TOWER_DARKAN_SOURCE = (
    "darkan-world-server/src/main/java/com/rs/game/content/minigames/domtower/"
    "DominionTower.java"
)
DOMINION_TOWER_CACHE_SOURCE = (
    "rev-727 cache dump developer-information/npcListBonuses.txt"
)
DOMINION_TOWER_SOURCE = (
    f"{DOMINION_TOWER_WIKI_SOURCE}; {DOMINION_TOWER_DARKAN_SOURCE}; "
    f"{DOMINION_TOWER_CACHE_SOURCE}; "
    "memory-bank/source-audits/dominion-tower-harvest-2026-07-28.md"
)

# ---------------------------------------------------------------------------
# Entry gates
# ---------------------------------------------------------------------------

# "Minimum of level 110 combat." Darkan checks the same number through
# getCombatLevelWithSummoning() >= 110.
DOMINION_TOWER_COMBAT_LEVEL_REQUIREMENT = 110
# "Completion of at least 20 of the 38 following quests are required to start."
DOMINION_TOWER_QUEST_REQUIREMENT = 20

# Recipe for Disaster counts as one entry on the tower's list of 38. AnkiScape's
# ledger carries it as its ten subquests, so the tower's single requirement is
# satisfied only when all ten are complete.
RECIPE_FOR_DISASTER_SUBQUESTS = (
    "recipe_for_disaster_another_cooks_quest",
    "recipe_for_disaster_freeing_the_mountain_dwarf",
    "recipe_for_disaster_freeing_the_goblin_generals",
    "recipe_for_disaster_freeing_pirate_pete",
    "recipe_for_disaster_freeing_the_lumbridge_sage",
    "recipe_for_disaster_freeing_evil_dave",
    "recipe_for_disaster_freeing_sir_amik_varze",
    "recipe_for_disaster_freeing_king_awowogei",
    "recipe_for_disaster_freeing_skrach_uglogwee",
    "recipe_for_disaster_defeating_the_culinaromancer",
)
RECIPE_FOR_DISASTER_REQUIREMENT_ID = "recipe_for_disaster"

# The tower's own list, in the order the pinned revision prints it. Each entry is
# one of the 38 the gate counts.
DOMINION_TOWER_QUEST_POOL: tuple[str, ...] = (
    "a_void_dance",
    "between_a_rock",
    "blood_runs_deep",
    "the_chosen_commander",
    "contact",
    "the_curse_of_arrav",
    "demon_slayer",
    "do_no_evil",
    "desert_treasure",
    "dealing_with_scabaras",
    "dragon_slayer",
    "dream_mentor",
    "family_crest",
    "fight_arena",
    "the_fremennik_trials",
    "haunted_mine",
    "holy_grail",
    "horror_from_the_deep",
    "legends_quest",
    "lost_city",
    "love_story",
    "missing_my_mummy",
    "monkey_madness",
    "mountain_daughter",
    "my_arms_big_adventure",
    "nomads_requiem",
    RECIPE_FOR_DISASTER_REQUIREMENT_ID,
    "shadow_of_the_storm",
    "spirits_of_the_elid",
    "the_great_brain_robbery",
    "the_temple_at_senntisten",
    "the_void_stares_back",
    "toktz_ket_dill",
    "troll_romance",
    "troll_stronghold",
    "vampyre_slayer",
    "wanted",
    "while_guthix_sleeps",
)

# ---------------------------------------------------------------------------
# Modes and factor arithmetic
# ---------------------------------------------------------------------------

DOMINION_TOWER_CLIMBER = "climber"
DOMINION_TOWER_ENDURANCE = "endurance"
DOMINION_TOWER_SPECIAL = "special"
DOMINION_TOWER_FREESTYLE = "freestyle"

DOMINION_TOWER_MODES: tuple[dict[str, Any], ...] = (
    {
        "id": DOMINION_TOWER_CLIMBER,
        "display_name": "Climber",
        "handicaps": True,
        "bank_between_fights": True,
        "rewards": True,
        # Darkan: factor = roster combat level total * 100 in climber mode.
        "factor_multiplier": 100,
        "max_floor": 0,
    },
    {
        "id": DOMINION_TOWER_ENDURANCE,
        "display_name": "Endurance",
        "handicaps": False,
        "bank_between_fights": False,
        "rewards": True,
        # Darkan: the same product times 10 in endurance mode, which matches the
        # article's "much less dominion factor per fight".
        "factor_multiplier": 10,
        # "The maximum number of rounds in this mode is 255."
        "max_floor": 255,
    },
    {
        "id": DOMINION_TOWER_SPECIAL,
        "display_name": "Special",
        "handicaps": True,
        "bank_between_fights": True,
        "rewards": True,
        # PLACEHOLDER(dominion_tower.special_mode_factor_multiplier): the article
        # states special mode awards rewards and counts one boss kill per match
        # but never states its factor rate; the climber rate stands in.
        "factor_multiplier": 100,
        "max_floor": 0,
    },
    {
        "id": DOMINION_TOWER_FREESTYLE,
        "display_name": "Freestyle",
        "handicaps": True,
        "bank_between_fights": True,
        # "There are no rewards for using this mode... Players can gain
        # experience in this mode."
        "rewards": False,
        "factor_multiplier": 0,
        "max_floor": 0,
    },
)
DOMINION_TOWER_MODES_BY_ID = {row["id"]: row for row in DOMINION_TOWER_MODES}

# Darkan: MAX_FACTOR = 10000000.
DOMINION_TOWER_MAX_FACTOR = 10_000_000
# "after reaching floor 30 in endurance mode, players will earn dominion factor
# at a further reduced rate."
DOMINION_TOWER_ENDURANCE_REDUCED_FLOOR = 30
# PLACEHOLDER(dominion_tower.endurance_reduced_rate): the article states the rate
# falls again past floor 30 but gives no figure; halving reproduces the stated
# direction and claims nothing more.
DOMINION_TOWER_ENDURANCE_REDUCED_DIVISOR = 2
# PLACEHOLDER(dominion_tower.loss_factor_penalty): "Losing a fight reduces the
# player's dominion factor" with no amount stated anywhere in the period record.
# One round's own earned factor is forfeited, which is the smallest reduction
# that makes the stated cash-out-before-a-likely-loss advice rational.
DOMINION_TOWER_LOSS_FORFEITS_LAST_ROUND = True

# ---------------------------------------------------------------------------
# Handicap wheel
# ---------------------------------------------------------------------------

# The 22 rows in wheel order, exactly as the pinned revision prints them.
# "The handicaps are in order of the wheel. If you nudge the wheel it will land
# on the handicap before it on the list" and "Nudging off the top of the list
# goes to the bottom", so a nudge is index - 1 modulo 22.
#
# `effect` names how AnkiScape applies the handicap. Every effect below either
# drives a mechanic the engine already owns (prayer, food, potions, special
# attack energy, poison, equipment slots, lifepoints) or scales a number this
# family owns (the encounter's own damage). `factor_only` marks the two
# handicaps whose period effect is about standing still, which a review-driven
# fight has no way to represent; their factor delta still applies.
DOMINION_TOWER_HANDICAPS: tuple[dict[str, Any], ...] = (
    {
        "id": "disease",
        "display_name": "Disease",
        "factor_delta": -70,
        "effect": "disease",
        "description": "Diseased at the start of every match; one skill drops 14 points.",
    },
    {
        "id": "reduced_magic_attack",
        "display_name": "Reduced Magic Attack",
        "factor_delta": 70,
        "effect": "reduce_player_attack",
        "combat_class": "magic",
        "description": "Your magic attack bonus is reduced in every match.",
    },
    {
        "id": "slippery_fingers",
        "display_name": "Slippery Fingers",
        "factor_delta": 90,
        "effect": "lose_attack_time",
        "description": "Your weapon occasionally unequips itself mid-match.",
    },
    {
        "id": "no_prayer",
        "display_name": "No Prayer",
        "factor_delta": 130,
        "effect": "no_prayer",
        "description": "You cannot use prayer in the matches.",
    },
    {
        "id": "monster_stun",
        "display_name": "Monster Stun",
        "factor_delta": -190,
        "effect": "monster_stun",
        "description": "Every foe starts the match stunned for about ten seconds.",
    },
    {
        "id": "no_familiar",
        "display_name": "No Familiar",
        "factor_delta": -60,
        "effect": "no_familiar",
        "description": "You cannot summon a familiar during the matches.",
    },
    {
        "id": "reduced_ranged_attack",
        "display_name": "Reduced Range Attack",
        "factor_delta": 70,
        "effect": "reduce_player_attack",
        "combat_class": "ranged",
        "description": "Your ranged attack bonus is reduced in every match.",
    },
    {
        "id": "no_body_armour",
        "display_name": "No Body Armour",
        "factor_delta": 50,
        "effect": "strip_slot",
        "slot": "body",
        "description": "Body armour is sent to your bank and the slot stays empty.",
    },
    {
        "id": "halved_life_points",
        "display_name": "Halved Life Points",
        "factor_delta": -10,
        "effect": "halved_lifepoints",
        "description": "Your starting health is halved at the start of each match.",
    },
    {
        "id": "random_freeze",
        "display_name": "Random Freeze",
        "factor_delta": -40,
        "effect": "factor_only",
        "description": (
            "Occasionally frozen in place, but you can still attack; AnkiScape "
            "has no movement, so only the factor delta applies."
        ),
    },
    {
        "id": "reduced_melee_defence",
        "display_name": "Reduced Melee Defence",
        "factor_delta": 50,
        "effect": "reduce_player_defence",
        "combat_class": "melee",
        "description": "Your melee defence bonus is reduced in every match.",
    },
    {
        "id": "no_food",
        "display_name": "No Food",
        "factor_delta": 120,
        "effect": "no_food",
        "description": "You are not allowed to eat any food during any match.",
    },
    {
        "id": "no_shield",
        "display_name": "No Shield",
        "factor_delta": -20,
        "effect": "strip_slot",
        "slot": "shield",
        "description": "Shields are sent to your bank; two-handed weapons are unaffected.",
    },
    {
        "id": "reduced_melee_attack",
        "display_name": "Reduced Melee Attack",
        "factor_delta": 70,
        "effect": "reduce_player_attack",
        "combat_class": "melee",
        "description": "Your melee attack bonus is reduced in every match.",
    },
    {
        "id": "life_saver",
        "display_name": "Life Saver",
        "factor_delta": -200,
        "effect": "life_saver",
        "description": "Once each match you are restored to full when you fall low.",
    },
    {
        "id": "no_potions",
        "display_name": "No Potions",
        "factor_delta": 50,
        "effect": "no_potions",
        "description": "You cannot drink potions during any match.",
    },
    {
        "id": "no_powerups",
        "display_name": "No Power-ups",
        "factor_delta": -80,
        "effect": "no_powerups",
        "description": "No dominion power-ups, including the dominion weapons.",
    },
    {
        "id": "reduced_ranged_defence",
        "display_name": "Reduced Ranged Defence",
        "factor_delta": 10,
        "effect": "reduce_player_defence",
        "combat_class": "ranged",
        "description": "Your ranged defence bonus is reduced in every match.",
    },
    {
        "id": "poison",
        "display_name": "Poison",
        "factor_delta": -60,
        "effect": "poison",
        # "The damage starts at 98 life points."
        "initial_damage": 98,
        "description": "Poisoned at the start of each match, starting at 98 damage.",
    },
    {
        "id": "random_daze",
        "display_name": "Random Daze",
        "factor_delta": 110,
        "effect": "lose_attack_time",
        "description": "Dazed occasionally: auto-retaliate off and combat interrupted.",
    },
    {
        "id": "reduced_magic_defence",
        "display_name": "Reduced Magic Defence",
        "factor_delta": 10,
        "effect": "reduce_player_defence",
        "combat_class": "magic",
        "description": "Your magic defence bonus is reduced in every match.",
    },
    {
        "id": "no_special_attacks",
        "display_name": "No Special Attacks",
        "factor_delta": -100,
        "effect": "no_special_attacks",
        "description": "No special attacks in any match.",
    },
)
DOMINION_TOWER_HANDICAPS_BY_ID = {row["id"]: row for row in DOMINION_TOWER_HANDICAPS}
DOMINION_TOWER_HANDICAP_IDS = tuple(row["id"] for row in DOMINION_TOWER_HANDICAPS)
DOMINION_TOWER_HANDICAP_COUNT = len(DOMINION_TOWER_HANDICAPS)
# "The player then often has a chance to respin for a different handicap or to
# nudge the handicap spinner up to three places."
DOMINION_TOWER_HANDICAP_NUDGE_LIMIT = 3
DOMINION_TOWER_HANDICAP_RESPIN_LIMIT = 1
# PLACEHOLDER(dominion_tower.handicap_reduction_fraction): the six reduced
# attack/defence handicaps are described only as "reduced" with no magnitude in
# any period source. Halving is the reduction the wheel's own factor deltas are
# priced against here.
DOMINION_TOWER_HANDICAP_REDUCTION_FRACTION = 0.5
# PLACEHOLDER(dominion_tower.lost_attack_time_chance): Slippery Fingers and
# Random Daze both interrupt attacking "occasionally"; no source gives a rate.
DOMINION_TOWER_LOST_ATTACK_TIME_CHANCE = 0.25
# "All foes at the beginning of the battle are stunned for a few seconds (about
# ten)": ten seconds is about sixteen game ticks.
DOMINION_TOWER_MONSTER_STUN_TICKS = 16
# PLACEHOLDER(dominion_tower.life_saver_threshold): the handicap fires "if you
# reach low health" without defining low; the engine's own auto-eat default of
# two fifths stands in.
DOMINION_TOWER_LIFE_SAVER_THRESHOLD_PERCENT = 40

# ---------------------------------------------------------------------------
# Boss classes
# ---------------------------------------------------------------------------

# "Class A - Floor 6+" and every other class "Floor 1+".
DOMINION_TOWER_BOSS_CLASSES: tuple[dict[str, Any], ...] = (
    {"id": "A", "min_floor": 6},
    {"id": "B", "min_floor": 1},
    {"id": "C", "min_floor": 1},
    {"id": "D", "min_floor": 1},
    {"id": "E", "min_floor": 1},
    {"id": "F", "min_floor": 1},
    {"id": "G", "min_floor": 1},
    {"id": "H", "min_floor": 1},
)
DOMINION_TOWER_BOSS_CLASS_MIN_FLOOR = {
    row["id"]: row["min_floor"] for row in DOMINION_TOWER_BOSS_CLASSES
}

_ZERO_BONUSES = (0,) * 10
_ZERO_STRENGTH = (0, 0, 0)

_BONUS_KEYS = (
    "attack_stab",
    "attack_slash",
    "attack_crush",
    "attack_magic",
    "attack_ranged",
    "defence_stab",
    "defence_slash",
    "defence_crush",
    "defence_magic",
    "defence_ranged",
)
_STRENGTH_KEYS = ("melee_strength", "ranged_strength", "magic_damage")


def _bonuses(
    attack_defence: tuple[int, ...] = _ZERO_BONUSES,
    strength: tuple[int, int, int] = _ZERO_STRENGTH,
) -> dict[str, int]:
    """Expand a rev-727 npcListBonuses row into the engine's bonus block."""
    return {
        **dict(zip(_BONUS_KEYS, attack_defence)),
        **dict(zip(_STRENGTH_KEYS, strength)),
    }


# The share of a combat level that stands in for one core combat stat, taken
# from the Temple Trekking family's own reconstruction of the same problem.
DOMINION_TOWER_CORE_STAT_RATIO = 0.72


def _core_stat(level: int) -> int:
    return max(1, min(99, round(int(level) * DOMINION_TOWER_CORE_STAT_RATIO)))


def _npc(
    display_name: str,
    npc_id: int,
    level: int,
    lifepoints: int,
    max_hit: int,
    attack_styles: tuple[str, ...],
    source: str,
    *,
    bonuses: dict[str, int] | None = None,
    stats: dict[str, int] | None = None,
    attack_speed: int = 4,
    role: str = "boss",
    poison_damage: int = 0,
    heals_boss: int = 0,
) -> dict[str, Any]:
    return {
        "display_name": display_name,
        "npc_id": npc_id,
        "level": level,
        "lifepoints": lifepoints,
        "max_hit": max_hit,
        "attack_styles": attack_styles,
        "attack_speed": attack_speed,
        "role": role,
        "poison_damage": poison_damage,
        "heals_boss": heals_boss,
        "bonuses": bonuses if bonuses is not None else _bonuses(),
        # Where Darkan carries a combat-definition stat block it is used
        # verbatim. Where it carries only zeros or no row at all, the NPC's
        # combat level is converted with the same core-stat ratio Temple
        # Trekking already uses, because a RuneScape combat level is a composite
        # and copying it into all four stats makes a level-699 boss unhittable.
        # PLACEHOLDER(dominion_tower.unsourced_boss_stat_blocks): authentic
        # per-NPC Attack/Strength/Defence/Magic combat definitions for the tower
        # bosses Darkan left at zero or never defined.
        "stats": stats
        if stats is not None
        else {
            "attack": _core_stat(level),
            "strength": _core_stat(level),
            "defence": _core_stat(level),
            "magic": _core_stat(level),
            "hitpoints": lifepoints,
        },
        "source": source,
    }


def _stats(attack: int, strength: int, defence: int, magic: int, lifepoints: int) -> dict[str, int]:
    return {
        "attack": attack,
        "strength": strength,
        "defence": defence,
        "magic": magic,
        "hitpoints": lifepoints,
    }


_W = "https://runescape.wiki/w"

DOMINION_TOWER_NPCS: dict[str, dict[str, Any]] = {
    # ---- Class A -------------------------------------------------------
    "nomad": _npc(
        "Nomad", 8528, 699, 10_000, 322, ("magic", "melee"),
        f"{_W}/Nomad_(monster)?oldid=6547956; combatdefs/nomad; npcListBonuses 8528",
        bonuses=_bonuses((0, 0, 0, 0, 0, 100, 100, 100, 20, 100), (100, 0, 0)),
    ),
    "pest_queen": _npc(
        "Pest Queen", 6358, 599, 20_000, 214, ("magic", "melee"),
        f"{_W}/Pest_Queen?oldid=6492869; combatdefs/pest_queen; npcListBonuses 6358",
    ),
    "pest_drone": _npc(
        # "Each drone has 1000 life points... During the fight, they will not
        # attack, but they will heal the queen."
        "Pest drone", 3324, 1, 1_000, 0, ("melee",),
        f"{_W}/Pest_drone?oldid=6332922; npcListBonuses 3324",
        role="healer",
        # PLACEHOLDER(dominion_tower.pest_drone_heal): the drones are stated to
        # heal the Pest Queen but no source gives the amount or cadence.
        heals_boss=200,
    ),
    "decaying_avatar": _npc(
        "Decaying avatar", 9437, 525, 10_000, 460, ("melee",),
        f"{_W}/Decaying_avatar?oldid=6372060; combatdefs/decaying_avatar; npcListBonuses 9437",
        bonuses=_bonuses((0, 0, 0, 0, 0, 80, 80, 80, 130, 80), (31, 0, 0)),
    ),
    "eruni": _npc(
        "Eruni", 13222, 180, 5_000, 250, ("magic", "ranged"),
        f"{_W}/Eruni?oldid=6487478; npcListBonuses 13222",
        bonuses=_bonuses((0, 0, 0, 100, 80, 45, 45, 45, 45, 45), (53, 25, 25)),
    ),
    "ayuni": _npc(
        "Ayuni", 13219, 170, 3_000, 253, ("melee", "ranged", "magic"),
        f"{_W}/Ayuni?oldid=6214735; combatdefs/ayuni; npcListBonuses 13219",
        bonuses=_bonuses((0, 0, 0, 150, 150, 200, 200, 200, 40, 40), (82, 30, 30)),
    ),
    "leeuni": _npc(
        "Leeuni", 13216, 165, 3_000, 272, ("melee", "magic", "ranged"),
        f"{_W}/Leeuni?oldid=6546559; combatdefs/leeuni; npcListBonuses 13216",
        bonuses=_bonuses((0, 0, 0, 800, 800, 25, 80, 50, 120, 120), (53, 80, 80)),
    ),
    "dagannoth_mother_ii": _npc(
        "Dagannoth Mother", 9088, 353, 2_490, 430, ("melee", "magic", "ranged"),
        f"{_W}/Dagannoth_Mother_(Blood_Runs_Deep)?oldid=6245559",
    ),
    "zenevivia": _npc(
        "Zenevivia", 11578, 246, 3_500, 400, ("magic", "melee"),
        f"{_W}/Zenevivia?oldid=6392175; npcListBonuses 11578",
    ),
    # ---- Class B -------------------------------------------------------
    "the_untouchable": _npc(
        "The Untouchable", 5904, 274, 900, 269, ("melee",),
        f"{_W}/The_Untouchable?oldid=6579295; combatdefs/the_untouchable; npcListBonuses 5904",
        stats=_stats(187, 255, 434, 1, 900),
    ),
    "damis": _npc(
        "Damis", 1975, 217, 2_000, 290, ("melee",),
        f"{_W}/Damis?oldid=6182497; npcListBonuses 1975",
        bonuses=_bonuses((0, 0, 0, 0, 0, 100, 100, 100, 80, 120), (100, 0, 0)),
    ),
    "fareed": _npc(
        "Fareed", 1977, 227, 1_300, 360, ("melee", "magic"),
        f"{_W}/Fareed?oldid=5795751; combatdefs/fareed; npcListBonuses 1977",
        bonuses=_bonuses((0, 0, 0, 0, 0, 100, 100, 100, 0, 0), (120, 0, 0)),
        stats=_stats(190, 120, 135, 1, 1_300),
    ),
    "kamil": _npc(
        "Kamil", 1913, 189, 1_300, 240, ("melee", "magic"),
        f"{_W}/Kamil?oldid=6009601; combatdefs/kamil; npcListBonuses 1913",
        bonuses=_bonuses((0, 0, 0, 0, 0, 35, 60, 35, 0, 0), (100, 0, 0)),
        stats=_stats(190, 80, 135, 1, 1_300),
    ),
    "dessous": _npc(
        "Dessous", 1915, 139, 2_000, 190, ("melee", "magic", "ranged"),
        f"{_W}/Dessous?oldid=6351413; combatdefs/dessous; npcListBonuses 1915",
        bonuses=_bonuses((0, 0, 0, 0, 0, 10, 150, 150, 150, 150), (50, 0, 0)),
        stats=_stats(99, 99, 99, 1, 2_000),
    ),
    "the_everlasting": _npc(
        "The Everlasting", 5903, 223, 2_300, 245, ("melee",),
        f"{_W}/The_Everlasting?oldid=5795354; combatdefs/the_everlasting; npcListBonuses 5903",
        stats=_stats(187, 231, 120, 1, 2_300),
    ),
    "the_illusive": _npc(
        "The Illusive", 5905, 108, 1_400, 85, ("melee",),
        f"{_W}/The_Illusive?oldid=5908075; combatdefs/the_illusive; npcListBonuses 5905",
    ),
    "dagannoth_sentinel": _npc(
        "Dagannoth sentinel", 9089, 193, 2_500, 150, ("magic", "melee", "ranged"),
        f"{_W}/Dagannoth_sentinel?oldid=6556338; npcListBonuses 9089",
    ),
    "karamel": _npc(
        "Karamel", 3495, 200, 2_400, 150, ("magic", "melee"),
        f"{_W}/Karamel?oldid=5866031; combatdefs/karamel; npcListBonuses 3495",
        bonuses=_bonuses((50, 50, 50, 0, 134, 150, 150, 150, 150, 150), (0, 55, 0)),
        stats=_stats(1, 1, 100, 1, 2_400),
    ),
    "gelatinnoth_mother": _npc(
        "Gelatinnoth Mother", 3497, 130, 2_400, 200, ("ranged", "melee"),
        f"{_W}/Gelatinnoth_Mother?oldid=6372388; combatdefs/gelatinnoth_mother; npcListBonuses 3497",
        bonuses=_bonuses((0, 0, 0, 0, 0, 150, 150, 150, 50, 50)),
        stats=_stats(78, 78, 81, 1, 2_400),
    ),
    "nezikchened": _npc(
        "Nezikchened", 934, 187, 1_500, 180, ("melee", "magic"),
        f"{_W}/Nezikchened?oldid=6359899; combatdefs/nezikchened; npcListBonuses 934",
        stats=_stats(330, 336, 167, 320, 1_500),
    ),
    # ---- Class C -------------------------------------------------------
    "balance_elemental": _npc(
        "Balance Elemental", 8281, 454, 2_750, 300, ("magic", "ranged", "melee"),
        f"{_W}/Balance_Elemental?oldid=6534303; combatdefs/balance_elemental; npcListBonuses 8281",
    ),
    "jungle_demon": _npc(
        "Jungle demon", 1472, 195, 1_700, 323, ("melee", "magic"),
        f"{_W}/Jungle_demon?oldid=6110939; combatdefs/jungle_demon; npcListBonuses 1472",
        bonuses=_bonuses((0, 0, 0, 0, 0, 0, 50, 0, 50, 0), (50, 0, 0)),
        stats=_stats(170, 170, 170, 170, 1_700),
    ),
    "arrav": _npc(
        "Arrav", 8168, 180, 1_500, 264, ("melee",),
        f"{_W}/Arrav?oldid=6552421; npcListBonuses 8168",
    ),
    "ice_demon": _npc(
        "Ice demon", 9052, 177, 1_500, 230, ("ranged", "magic"),
        f"{_W}/Ice_demon?oldid=6539201; npcListBonuses 9052",
        bonuses=_bonuses((0, 0, 0, 0, 0, 50, 180, 180, 10, 50)),
    ),
    "the_inadequacy": _npc(
        "The Inadequacy", 5902, 343, 1_800, 200, ("melee", "ranged"),
        f"{_W}/The_Inadequacy?oldid=6581130; combatdefs/the_inadequacy; npcListBonuses 5902",
        stats=_stats(564, 170, 240, 1, 1_800),
    ),
    "a_doubt": _npc(
        "A Doubt", 5906, 78, 590, 88, ("melee",),
        f"{_W}/A_Doubt?oldid=5927782; combatdefs/a_doubt; npcListBonuses 5906",
        bonuses=_bonuses(strength=(16, 0, 0)),
    ),
    "giant_roc": _npc(
        "Giant Roc", 4972, 172, 2_000, 200, ("melee", "ranged"),
        f"{_W}/Giant_Roc?oldid=5967444; combatdefs/giant_roc; npcListBonuses 4972",
        bonuses=_bonuses((0, 0, 0, 0, 0, 0, 0, 0, 150, 0)),
        stats=_stats(130, 130, 100, 1, 2_000),
    ),
    # ---- Class D -------------------------------------------------------
    "arrg": _npc(
        "Arrg", 1555, 171, 1_500, 386, ("melee", "ranged"),
        f"{_W}/Arrg?oldid=6196308; combatdefs/arrg; npcListBonuses 1555",
        bonuses=_bonuses((0, 0, 0, 0, 0, 35, 60, 35, 200, 200), (100, 0, 0)),
        stats=_stats(70, 140, 40, 1, 1_500),
    ),
    "barrelchest": _npc(
        "Barrelchest", 5666, 210, 1_340, 351, ("melee", "ranged"),
        f"{_W}/Barrelchest?oldid=6447009; combatdefs/barrelchest; npcListBonuses 5666",
        bonuses=_bonuses(strength=(80, 0, 0)),
        stats=_stats(170, 145, 140, 90, 1_340),
    ),
    "chronozon": _npc(
        "Chronozon", 667, 170, 600, 180, ("melee",),
        f"{_W}/Chronozon?oldid=6406184; combatdefs/chronozon; npcListBonuses 667",
        stats=_stats(173, 172, 173, 1, 600),
    ),
    "evil_chicken": _npc(
        "Evil Chicken", 3375, 159, 1_200, 210, ("magic",),
        f"{_W}/Evil_Chicken_(Recipe_for_Disaster)?oldid=6126305; "
        "combatdefs/evil_chicken; npcListBonuses 3375",
        attack_speed=6,
        stats=_stats(1, 1, 126, 200, 1_200),
    ),
    "flambeed": _npc(
        "Flambeed", 3494, 199, 2_100, 240, ("melee", "magic"),
        f"{_W}/Flambeed?oldid=5796030; combatdefs/flambeed; npcListBonuses 3494",
        bonuses=_bonuses((0, 0, 0, 0, 0, 50, 50, 5, 5, 50)),
        stats=_stats(120, 120, 75, 1, 2_100),
    ),
    "agrith_na_na": _npc(
        # The wiki row says level 146 and rev 727 says 182 for the same NPC id.
        # The cache is the client's own definition, so it wins on identity.
        "Agrith-Na-Na", 3493, 182, 2_000, 170, ("melee", "magic"),
        f"{_W}/Agrith-Na-Na?oldid=6303641; combatdefs/agrith-na-na; npcListBonuses 3493",
        bonuses=_bonuses((0, 0, 0, 0, 0, 100, 100, 100, 100, 100)),
        stats=_stats(83, 150, 82, 100, 2_000),
    ),
    "dessourt": _npc(
        "Dessourt", 3496, 121, 1_400, 190, ("melee", "magic"),
        f"{_W}/Dessourt?oldid=6469481; combatdefs/dessourt; npcListBonuses 3496",
        bonuses=_bonuses((0, 0, 0, 0, 0, 10, 150, 150, 0, 0), (50, 0, 0)),
        stats=_stats(99, 99, 99, 1, 1_400),
    ),
    "giant_scarab": _npc(
        "Giant Scarab", 5253, 191, 1_300, 200, ("melee", "ranged"),
        f"{_W}/Giant_scarab?oldid=6351184; npcListBonuses 5253",
        bonuses=_bonuses((0, 0, 0, 0, 0, 70, 99, 99, 159, 149)),
    ),
    # ---- Class E -------------------------------------------------------
    "bouncer": _npc(
        "Bouncer", 269, 137, 1_160, 140, ("melee",),
        f"{_W}/Bouncer?oldid=6356419; npcListBonuses 269",
    ),
    "koschei": _npc(
        # PLACEHOLDER(dominion_tower.koschei_combat_level): neither the pinned
        # revision ("level = N/A") nor rev 727 (all four forms carry 0) states a
        # combat level, and the tower's factor formula multiplies roster combat
        # levels. The lowest stated level in Koschei's own class E stands in.
        "Koschei the deathless", 1293, 110, 790, 74, ("melee",),
        f"{_W}/Koschei_the_deathless?oldid=6450413; combatdefs/koschei; npcListBonuses 1290-1293",
        attack_speed=6,
    ),
    "arzinian_avatar": _npc(
        # PLACEHOLDER(dominion_tower.arzinian_avatar_form): Between a Rock spawns
        # one of three avatars at level 75 or 125 depending on gold ore mined;
        # no source says which the tower picks. The full-strength Avatar of
        # Strength stands in.
        "Arzinian Avatar", 1851, 125, 1_100, 150, ("melee", "magic", "ranged"),
        f"{_W}/Arzinian_Avatar?oldid=6435649; npcListBonuses 1851",
        bonuses=_bonuses((0, 0, 0, 0, 0, 20, 20, 20, 15, 80)),
    ),
    "black_knight_titan": _npc(
        "Black Knight Titan", 221, 120, 1_420, 150, ("melee",),
        f"{_W}/Black_Knight_Titan?oldid=6435406; combatdefs/black_knight_titan; npcListBonuses 221",
        bonuses=_bonuses((0, 0, 0, 0, 0, 17, 20, 19, 1000, 1000), (22, 0, 0)),
        stats=_stats(91, 100, 91, 1, 1_420),
    ),
    "general_khazard": _npc(
        # PLACEHOLDER(dominion_tower.general_khazard_combat_definition): rev 727
        # pins the Fight Arena Khazard at level 112 (id 7552), but the merged
        # wiki article states no lifepoint total or maximum hit for that form.
        # A level-appropriate 1,300 lifepoints and 150 maximum hit stand in.
        "General Khazard", 7552, 112, 1_300, 150, ("melee",),
        f"{_W}/General_Khazard?oldid=6448916; npcListBonuses 7552",
    ),
    "black_knight_guardian": _npc(
        "Black Knight guardian", 11696, 110, 750, 114, ("melee",),
        f"{_W}/Black_Knight_guardian?oldid=6010042; combatdefs/black_knight_guardian; "
        "npcListBonuses 11696",
        bonuses=_bonuses((0, 0, 0, 0, 0, 230, 230, 210, 200, 280), (25, 0, 0)),
    ),
    # ---- Class F -------------------------------------------------------
    "dad": _npc(
        "Dad", 1125, 101, 1_200, 275, ("melee",),
        f"{_W}/Dad?oldid=6550577; combatdefs/dad; npcListBonuses 1125",
        bonuses=_bonuses((0, 0, 0, 0, 0, 25, 25, 40, 200, 200), (70, 0, 0)),
        stats=_stats(60, 120, 50, 1, 1_200),
    ),
    "dramen_tree_spirit": _npc(
        "Dramen Tree Spirit", 655, 101, 850, 109, ("melee",),
        f"{_W}/Dramen_Tree_Spirit?oldid=6435827",
    ),
    "agrith_naar": _npc(
        "Agrith Naar", 2919, 100, 950, 114, ("melee", "magic"),
        f"{_W}/Agrith_Naar?oldid=6371322; combatdefs/agrith_naar; npcListBonuses 2919",
        stats=_stats(83, 90, 82, 100, 950),
    ),
    "dagannoth_mother": _npc(
        "Dagannoth mother", 1348, 100, 1_000, 160, ("melee", "ranged"),
        f"{_W}/Dagannoth_mother?oldid=6448031; combatdefs/dagannoth_mother; npcListBonuses 1348",
        bonuses=_bonuses((0, 0, 0, 0, 0, 150, 150, 150, 50, 50)),
        stats=_stats(78, 78, 81, 1, 1_000),
    ),
    "toktz_ket_dill": _npc(
        "TokTz-Ket-Dill", 7770, 100, 2_060, 250, ("melee", "ranged"),
        f"{_W}/TokTz-Ket-Dill_(monster)?oldid=6343317; combatdefs/toktz-ket-dill; "
        "npcListBonuses 7770",
        bonuses=_bonuses((0, 0, 0, 10, 0, 30, 30, 50, 30, 50), (30, 0, 0)),
    ),
    "black_golem": _npc(
        "Black golem", 3026, 75, 800, 90, ("melee",),
        f"{_W}/Black_golem?oldid=6351797; combatdefs/black_golem; npcListBonuses 3026",
        bonuses=_bonuses((0, 0, 0, 0, 0, 300, 300, 1, 300, 300)),
        stats=_stats(80, 30, 80, 1, 800),
    ),
    "grey_golem": _npc(
        "Grey golem", 3028, 75, 800, 40, ("melee",),
        f"{_W}/Grey_golem?oldid=6351806; combatdefs/grey_golem; npcListBonuses 3028",
        bonuses=_bonuses((0, 0, 0, 0, 0, 300, 1, 300, 300, 300)),
        stats=_stats(80, 30, 80, 1, 800),
    ),
    "white_golem": _npc(
        "White golem", 3027, 75, 800, 40, ("melee",),
        f"{_W}/White_golem?oldid=6196261; combatdefs/white_golem; npcListBonuses 3027",
        bonuses=_bonuses((0, 0, 0, 0, 0, 1, 300, 300, 300, 300)),
        stats=_stats(80, 30, 80, 1, 800),
    ),
    # ---- Class G -------------------------------------------------------
    "treus_dayth": _npc(
        "Treus Dayth", 1540, 95, 1_000, 150, ("ranged", "melee"),
        f"{_W}/Treus_Dayth?oldid=6351890; combatdefs/treus_dayth; npcListBonuses 1540",
        bonuses=_bonuses((0, 0, 0, 0, 0, 5, 5, 5, -5, 5)),
        stats=_stats(70, 70, 100, 1, 1_000),
    ),
    "elvarg": _npc(
        "Elvarg", 742, 83, 800, 110, ("melee",),
        f"{_W}/Elvarg?oldid=6510444; combatdefs/elvarg; npcListBonuses 742",
        bonuses=_bonuses((0, 0, 0, 0, 0, 20, 40, 40, 30, 20)),
        stats=_stats(70, 70, 70, 70, 800),
    ),
    "culinaromancer": _npc(
        "Culinaromancer", 3387, 75, 1_400, 270, ("melee", "magic"),
        f"{_W}/Culinaromancer?oldid=6335745; combatdefs/culinaromancer; npcListBonuses 3387",
        stats=_stats(10, 100, 10, 1, 1_400),
    ),
    "tumekens_shadow": _npc(
        # PLACEHOLDER(dominion_tower.tumekens_shadow_form): Missing My Mummy
        # spawns five escalating shadows (levels 41/50/55/64/72 in rev 727) and
        # no source says which the tower spawns. The final form stands in.
        "Tumeken's shadow", 7480, 72, 700, 100, ("melee",),
        f"{_W}/Tumeken's_shadow?oldid=6516880; npcListBonuses 7480",
    ),
    "the_kendal": _npc(
        "The Kendal", 1813, 70, 500, 90, ("melee",),
        f"{_W}/The_Kendal_(monster)?oldid=6547349; combatdefs/the_kendal; npcListBonuses 1813",
        bonuses=_bonuses((0, 0, 0, 0, 0, 10, 10, 10, -10, 20), (10, 0, 0)),
        stats=_stats(65, 65, 60, 1, 500),
    ),
    "the_draugen": _npc(
        "The Draugen", 1279, 96, 690, 100, ("melee",),
        f"{_W}/The_Draugen?oldid=6539591; combatdefs/the_draugen; npcListBonuses 1279",
        bonuses=_bonuses((0, 0, 0, 0, 0, 100, 100, 100, 500, 500)),
        stats=_stats(60, 60, 60, 1, 690),
    ),
    # ---- Class H -------------------------------------------------------
    "tarn_razorlor": _npc(
        "Tarn Razorlor", 6477, 69, 650, 190, ("melee", "magic"),
        f"{_W}/Tarn_Razorlor?oldid=6448021",
    ),
    "terror_dog_100": _npc(
        "Terror dog", 5418, 100, 820, 110, ("melee",),
        f"{_W}/Terror_dog?oldid=6547220; npcListBonuses 5418",
        bonuses=_bonuses(strength=(10, 0, 0)),
    ),
    "terror_dog_110": _npc(
        "Terror dog", 5417, 110, 880, 150, ("melee",),
        f"{_W}/Terror_dog?oldid=6547220; npcListBonuses 5417",
        bonuses=_bonuses(strength=(20, 0, 0)),
    ),
    "sigmund": _npc(
        # PLACEHOLDER(dominion_tower.sigmund_combat_definition): rev 727 pins the
        # fighting Sigmund at level 75 (id 1731) and the wiki article carries no
        # Monster infobox at all, so lifepoints and maximum hit are unstated. A
        # level-appropriate 800 lifepoints and 100 maximum hit stand in.
        "Sigmund", 1731, 75, 800, 100, ("melee", "magic"),
        f"{_W}/Sigmund?oldid=6436922; npcListBonuses 1731",
    ),
    "melzar_the_mad": _npc(
        "Melzar the Mad", 753, 43, 440, 54, ("magic", "melee"),
        f"{_W}/Melzar_the_Mad?oldid=6351837; combatdefs/melzar_the_mad; npcListBonuses 753",
        stats=_stats(37, 37, 34, 40, 440),
    ),
    "count_draynor": _npc(
        "Count Draynor", 9356, 37, 350, 40, ("melee",),
        f"{_W}/Count_Draynor?oldid=6546347; combatdefs/count_draynor; npcListBonuses 9356",
        bonuses=_bonuses((0, 0, 0, 0, 0, 2, 1, 3, 0, 0)),
        stats=_stats(30, 25, 30, 1, 350),
    ),
    "delrith": _npc(
        "Delrith", 879, 27, 70, 30, ("melee",),
        f"{_W}/Delrith?oldid=6448000; combatdefs/delrith; npcListBonuses 879",
        stats=_stats(11, 10, 5, 1, 70),
    ),
    "solus_dellagar": _npc(
        # PLACEHOLDER(dominion_tower.solus_dellagar_combat_level): the pinned
        # revision states "level = None" and rev 727 carries 0 for both ids, so
        # the lowest stated level in Solus's own class H stands in for the
        # factor formula.
        "Solus Dellagar", 2780, 27, 400, 960, ("magic", "melee"),
        f"{_W}/Solus_Dellagar?oldid=6342730; combatdefs/solus_dellagar; npcListBonuses 2780",
        bonuses=_bonuses((0, 0, 0, 0, 0, 5, 5, 5, 72, -10), (16, 0, 0)),
    ),
    # ---- Non-quest (special mode only) --------------------------------
    "sunfreet_80": _npc(
        "Sunfreet", 15225, 80, 800, 114, ("magic", "melee"),
        f"{_W}/Sunfreet?oldid=6537433; npcListBonuses 15225",
    ),
    "sunfreet_530": _npc(
        # PLACEHOLDER(dominion_tower.sunfreet_530_max_hit): the pinned revision
        # gives a maximum hit for the level-80 Sunfreet only. The level-530
        # form's hit scales with its own lifepoint ratio here.
        "Sunfreet", 15222, 530, 11_000, 460, ("magic", "melee"),
        f"{_W}/Sunfreet?oldid=6537433; npcListBonuses 15222",
        bonuses=_bonuses((0, 0, 0, 0, 0, 85, 85, 85, 750, 750), (70, 0, 42)),
    ),
}


def _encounter(
    encounter_id: str,
    display_name: str,
    boss_class: str,
    quest_id: str,
    npc_ids: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "id": encounter_id,
        "display_name": display_name,
        "class": boss_class,
        "quest_id": quest_id,
        "npcs": npc_ids,
        "min_floor": DOMINION_TOWER_BOSS_CLASS_MIN_FLOOR[boss_class],
    }


# The eight classes exactly as the pinned revision groups them, each boss with
# the quest whose completion makes it appear.
DOMINION_TOWER_ENCOUNTERS: tuple[dict[str, Any], ...] = (
    # Class A - Floor 6+
    _encounter("nomad", "Nomad", "A", "nomads_requiem", ("nomad",)),
    _encounter(
        "pest_queen",
        "Pest Queen and drones",
        "A",
        "the_void_stares_back",
        ("pest_queen", "pest_drone", "pest_drone", "pest_drone", "pest_drone"),
    ),
    _encounter("decaying_avatar", "Decaying avatar", "A", "nomads_requiem", ("decaying_avatar",)),
    _encounter(
        "eruni_ayuni_leeuni",
        "Eruni, Ayuni and Leeuni",
        "A",
        "do_no_evil",
        ("eruni", "ayuni", "leeuni"),
    ),
    _encounter(
        "dagannoth_mother_ii",
        "Dagannoth Mother",
        "A",
        "blood_runs_deep",
        ("dagannoth_mother_ii",),
    ),
    _encounter("zenevivia", "Zenevivia", "A", "love_story", ("zenevivia",)),
    # Class B - Floor 1+
    _encounter("the_untouchable", "The Untouchable", "B", "dream_mentor", ("the_untouchable",)),
    _encounter(
        "desert_treasure_guardians",
        "Damis, Fareed, Kamil and Dessous",
        "B",
        "desert_treasure",
        ("damis", "fareed", "kamil", "dessous"),
    ),
    _encounter(
        "everlasting_illusive",
        "The Everlasting and The Illusive",
        "B",
        "dream_mentor",
        ("the_everlasting", "the_illusive"),
    ),
    _encounter(
        "dagannoth_sentinels",
        "Dagannoth sentinels",
        "B",
        "blood_runs_deep",
        ("dagannoth_sentinel", "dagannoth_sentinel"),
    ),
    _encounter(
        "karamel_gelatinnoth",
        "Karamel and Gelatinnoth Mother",
        "B",
        RECIPE_FOR_DISASTER_REQUIREMENT_ID,
        ("karamel", "gelatinnoth_mother"),
    ),
    _encounter("nezikchened", "Nezikchened", "B", "legends_quest", ("nezikchened",)),
    # Class C - Floor 1+
    _encounter(
        "balance_elemental",
        "Balance Elemental",
        "C",
        "while_guthix_sleeps",
        ("balance_elemental",),
    ),
    _encounter("jungle_demon", "Jungle demon", "C", "monkey_madness", ("jungle_demon",)),
    _encounter("arrav", "Arrav", "C", "the_curse_of_arrav", ("arrav",)),
    _encounter("ice_demon", "Ice demon", "C", "the_temple_at_senntisten", ("ice_demon",)),
    _encounter(
        "inadequacy_doubts",
        "The Inadequacy and Doubts",
        "C",
        "dream_mentor",
        ("the_inadequacy", "a_doubt", "a_doubt"),
    ),
    _encounter("giant_roc", "Giant Roc", "C", "my_arms_big_adventure", ("giant_roc",)),
    # Class D - Floor 1+
    _encounter("arrg", "Arrg", "D", "troll_romance", ("arrg",)),
    _encounter("barrelchest", "Barrelchest", "D", "the_great_brain_robbery", ("barrelchest",)),
    _encounter("chronozon", "Chronozon", "D", "family_crest", ("chronozon",)),
    _encounter(
        "evil_chicken",
        "Evil Chicken",
        "D",
        RECIPE_FOR_DISASTER_REQUIREMENT_ID,
        ("evil_chicken",),
    ),
    _encounter(
        "flambeed_agrith_dessourt",
        "Flambeed, Agrith-Na-Na and Dessourt",
        "D",
        RECIPE_FOR_DISASTER_REQUIREMENT_ID,
        ("flambeed", "agrith_na_na", "dessourt"),
    ),
    _encounter("giant_scarab", "Giant Scarab", "D", "contact", ("giant_scarab",)),
    # Class E - Floor 1+
    _encounter("bouncer", "Bouncer", "E", "fight_arena", ("bouncer",)),
    _encounter("koschei", "Koschei the deathless", "E", "the_fremennik_trials", ("koschei",)),
    _encounter("arzinian_avatar", "Arzinian Avatar", "E", "between_a_rock", ("arzinian_avatar",)),
    _encounter("black_knight_titan", "Black Knight Titan", "E", "holy_grail", ("black_knight_titan",)),
    _encounter("general_khazard", "General Khazard", "E", "fight_arena", ("general_khazard",)),
    _encounter(
        "black_knight_guardian",
        "Black Knight guardian",
        "E",
        "a_void_dance",
        ("black_knight_guardian",),
    ),
    # Class F - Floor 1+
    _encounter("dad", "Dad", "F", "troll_stronghold", ("dad",)),
    _encounter("dramen_tree_spirit", "Dramen Tree Spirit", "F", "lost_city", ("dramen_tree_spirit",)),
    _encounter("agrith_naar", "Agrith Naar", "F", "shadow_of_the_storm", ("agrith_naar",)),
    _encounter(
        "dagannoth_mother",
        "Dagannoth mother",
        "F",
        "horror_from_the_deep",
        ("dagannoth_mother",),
    ),
    _encounter("toktz_ket_dill", "TokTz-Ket-Dill", "F", "toktz_ket_dill", ("toktz_ket_dill",)),
    _encounter(
        "golems",
        "Black, grey and white golem",
        "F",
        "spirits_of_the_elid",
        ("black_golem", "grey_golem", "white_golem"),
    ),
    # Class G - Floor 1+
    _encounter("treus_dayth", "Treus Dayth", "G", "haunted_mine", ("treus_dayth",)),
    _encounter("elvarg", "Elvarg", "G", "dragon_slayer", ("elvarg",)),
    _encounter(
        "culinaromancer",
        "Culinaromancer",
        "G",
        RECIPE_FOR_DISASTER_REQUIREMENT_ID,
        ("culinaromancer",),
    ),
    _encounter("tumekens_shadow", "Tumeken's shadow", "G", "missing_my_mummy", ("tumekens_shadow",)),
    _encounter("the_kendal", "The Kendal", "G", "mountain_daughter", ("the_kendal",)),
    _encounter("the_draugen", "The Draugen", "G", "the_fremennik_trials", ("the_draugen",)),
    # Class H - Floor 1+
    _encounter(
        "tarn_razorlor",
        "Tarn Razorlor and terror dogs",
        "H",
        # The tower gates this one on the Lair of Tarn Razorlor miniquest, which
        # is not one of the 38 quests. The ledger carries it as a miniquest row,
        # so this gate resolves off that row rather than off the quest pool.
        "lair_of_tarn_razorlor",
        ("tarn_razorlor", "terror_dog_100", "terror_dog_110"),
    ),
    _encounter("sigmund", "Sigmund", "H", "the_chosen_commander", ("sigmund",)),
    _encounter("melzar_the_mad", "Melzar the Mad", "H", "dragon_slayer", ("melzar_the_mad",)),
    _encounter("count_draynor", "Count Draynor", "H", "vampyre_slayer", ("count_draynor",)),
    _encounter("delrith", "Delrith", "H", "demon_slayer", ("delrith",)),
    _encounter("solus_dellagar", "Solus Dellagar", "H", "wanted", ("solus_dellagar",)),
)
DOMINION_TOWER_ENCOUNTERS_BY_ID = {row["id"]: row for row in DOMINION_TOWER_ENCOUNTERS}


def dominion_tower_encounter_roster_pure(encounter_id: str) -> tuple[dict[str, Any], ...]:
    """The encounter's live NPC roster, boss first, in spawn order."""
    encounter = DOMINION_TOWER_ENCOUNTERS_BY_ID.get(str(encounter_id))
    if encounter is None:
        return ()
    return tuple(
        copy.deepcopy(DOMINION_TOWER_NPCS[npc_id]) for npc_id in encounter["npcs"]
    )


def dominion_tower_encounter_total_level_pure(encounter_id: str) -> int:
    """Darkan's factor input: the combat levels of everything in the arena."""
    return sum(int(npc["level"]) for npc in dominion_tower_encounter_roster_pure(encounter_id))


# ---------------------------------------------------------------------------
# Special mode
# ---------------------------------------------------------------------------

# The ten fixed matches the pinned revision lists, each with its own opponents
# and its own handicaps. "A match's handicaps are incurred only for that match",
# and "a special fight only counts as 1 boss killed".
_REDUCED_ATTACK_HANDICAPS = (
    "reduced_melee_attack",
    "reduced_ranged_attack",
    "reduced_magic_attack",
)
_REDUCED_DEFENCE_HANDICAPS = (
    "reduced_melee_defence",
    "reduced_ranged_defence",
    "reduced_magic_defence",
)

DOMINION_TOWER_SPECIAL_MATCHES: tuple[dict[str, Any], ...] = (
    {
        "id": "revenge_of_the_evil_chickens",
        "display_name": "Revenge of the Evil Chickens",
        "npcs": ("evil_chicken",) * 15,
        "handicaps": ("no_prayer",),
        "requires_encounter": "evil_chicken",
        "objective": "kill",
    },
    {
        "id": "finish_him",
        "display_name": "Finish Him!",
        "npcs": (
            "arrav",
            "koschei",
            "general_khazard",
            "black_knight_guardian",
            "the_kendal",
            "black_golem",
            "white_golem",
            "grey_golem",
        ),
        # "Each boss only has 20% health."
        "lifepoint_fraction": (1, 5),
        "handicaps": (
            "no_prayer",
            *_REDUCED_ATTACK_HANDICAPS,
            *_REDUCED_DEFENCE_HANDICAPS,
            "poison",
            "disease",
            "random_daze",
            "no_special_attacks",
            "no_powerups",
        ),
        "requires_encounter": "arrav",
        "objective": "kill",
    },
    {
        "id": "just_die_already",
        "display_name": "Just Die Already",
        "npcs": ("dagannoth_sentinel",) * 6,
        "handicaps": (),
        "requires_encounter": "dagannoth_sentinels",
        "objective": "kill",
    },
    {
        "id": "no_more_nomad",
        "display_name": "No More Nomad...No More!",
        "npcs": ("nomad", "nomad"),
        "handicaps": (),
        "requires_encounter": "nomad",
        "objective": "kill",
    },
    {
        "id": "i_eat_dagannoths_for_breakfast",
        "display_name": "I Eat Dagannoths for Breakfast",
        "npcs": (
            "dagannoth_mother",
            "dagannoth_mother_ii",
            "dagannoth_sentinel",
            "dagannoth_sentinel",
        ),
        "handicaps": (),
        "requires_encounter": "dagannoth_mother",
        "objective": "kill",
    },
    {
        "id": "indigestion",
        "display_name": "Indigestion",
        "npcs": (
            "agrith_na_na",
            "flambeed",
            "karamel",
            "dessourt",
            "gelatinnoth_mother",
            "culinaromancer",
        ),
        "handicaps": (
            *_REDUCED_DEFENCE_HANDICAPS,
            "no_shield",
            "no_body_armour",
            "no_familiar",
            "no_powerups",
            "no_special_attacks",
        ),
        "requires_encounter": "flambeed_agrith_dessourt",
        "objective": "kill",
    },
    {
        "id": "youll_never_defeat_me",
        "display_name": "You'll Never Defeat Me",
        "npcs": ("the_inadequacy", "the_everlasting", "the_illusive", "the_untouchable"),
        "handicaps": (
            *_REDUCED_ATTACK_HANDICAPS,
            *_REDUCED_DEFENCE_HANDICAPS,
            "no_shield",
            "no_body_armour",
            "no_potions",
            "random_daze",
            "halved_life_points",
            "no_prayer",
            "no_food",
            "no_familiar",
        ),
        "requires_encounter": "inadequacy_doubts",
        # "The player must survive for five minutes": 300 seconds is 500 ticks.
        "objective": "survive",
        "survive_ticks": 500,
    },
    {
        "id": "hey_eat_power_up",
        "display_name": "Hey! Eat Power-up",
        # PLACEHOLDER(dominion_tower.hey_eat_powerup_roster): the match is
        # described only as "many low-level boss monsters", and the strategy text
        # names Elvarg and the Culinaromancer. The rest of class G stands in for
        # the unnamed remainder.
        "npcs": (
            "elvarg",
            "culinaromancer",
            "treus_dayth",
            "tumekens_shadow",
            "the_kendal",
            "the_draugen",
        ),
        # "The player will not be able to use armour or weapons."
        "handicaps": ("no_body_armour", "no_shield", "no_special_attacks"),
        "requires_encounter": "elvarg",
        "objective": "kill",
        "bombs_only": True,
    },
    {
        "id": "the_fire_it_burns",
        "display_name": "The Fire! It Burns!",
        "npcs": ("sunfreet_530",),
        "handicaps": ("no_powerups", "no_prayer", "no_special_attacks", "no_familiar"),
        # Sunfreet is not a quest boss, so no climber exposure gates it.
        "requires_encounter": "",
        "objective": "kill",
    },
    {
        "id": "the_fire_it_burns_easy",
        "display_name": "The Fire! It Burns! (easy version)",
        "npcs": ("sunfreet_80",),
        "handicaps": ("no_powerups", "no_prayer", "no_special_attacks", "no_familiar"),
        "requires_encounter": "",
        "objective": "kill",
        # "this could also be attempted by players without 110 combat."
        "waives_combat_requirement": True,
    },
)
DOMINION_TOWER_SPECIAL_MATCHES_BY_ID = {
    row["id"]: row for row in DOMINION_TOWER_SPECIAL_MATCHES
}


# ---------------------------------------------------------------------------
# Reward ladder
# ---------------------------------------------------------------------------

DOMINION_TOWER_GOLIATH_GLOVES = "Goliath gloves"
DOMINION_TOWER_SPELLCASTER_GLOVES = "Spellcaster gloves"
DOMINION_TOWER_SWIFT_GLOVES = "Swift gloves"
DOMINION_TOWER_DREADNIP = "Dreadnip"
DOMINION_TOWER_SWORD = "Dominion sword"
DOMINION_TOWER_STAFF = "Dominion staff"
DOMINION_TOWER_CROSSBOW = "Dominion crossbow"
DOMINION_TOWER_MINE = "Dominion mine"
DOMINION_TOWER_ASCENDANCY_MINE = "Ascendancy mine"
DOMINION_TOWER_MEDALLION = "Dominion medallion"
DOMINION_TOWER_SUPER_MEDALLION = "Super dominion medallion"
DOMINION_TOWER_MARKER = "Dominion marker"
DOMINION_TOWER_JOURNAL_PAGE = "A journal page"
DOMINION_TOWER_SCORPION_MEAT = "Scorpion meat"
DOMINION_TOWER_XP_BOOK = "Xp book"
DOMINION_TOWER_HELP_HORN = "Help horn"
DOMINION_TOWER_DIMINUTIVE_BOMB = "Diminutive bomb"
DOMINION_TOWER_MASSIVE_BOMB = "Massive bomb"
DOMINION_TOWER_COLOSSAL_BOMB = "Colossal bomb"
DOMINION_TOWER_DOM_SUPER_RESTORE = "Dom super restore"
DOMINION_TOWER_DOM_SUPER_PRAYER = "Dom super prayer"
DOMINION_TOWER_DOM_SUPER_ANTIPOISON = "Dom super antipoison"
DOMINION_TOWER_DOM_SARADOMIN_BREW = "Dom saradomin brew"

# "There are 20 of these pages."
DOMINION_TOWER_JOURNAL_PAGE_COUNT = 20
# "you can only store 15 rewards credits for the Dominion Gloves and Dreadnips
# at one time", and one credit becomes available "every 5 boss kills".
DOMINION_TOWER_REWARD_CREDIT_CAP = 15
DOMINION_TOWER_REWARD_CREDIT_KILLS = 5
DOMINION_TOWER_GLOVE_KILL_REQUIREMENT = 500
# "When they are unlocked, 100 dreadnips are awarded."
DOMINION_TOWER_DREADNIP_PER_CREDIT = 100
# "Upon claiming 10 mines from the Strange face, another 500 bosses must be
# defeated to obtain more."
DOMINION_TOWER_ASCENDANCY_MINES_PER_CLAIM = 10
DOMINION_TOWER_ASCENDANCY_KILL_REQUIREMENT = 500
# "Each mine costs 1000 coins", unlocked at 400 kills with every special match
# finished except Sunfreet.
DOMINION_TOWER_MINE_COST = 1_000
DOMINION_TOWER_MINE_KILL_REQUIREMENT = 400
DOMINION_TOWER_DREADNIP_KILL_REQUIREMENT = 450
# "Dominion Factor of 10,000 and all Journal pages" unlocks the colossal bomb.
DOMINION_TOWER_COLOSSAL_BOMB_FACTOR = 10_000

# The three glove sets, exactly as each glove's own pinned revision lists them.
# Every set is two class A, two class B and two class C encounters.
DOMINION_TOWER_GLOVE_SETS: tuple[dict[str, Any], ...] = (
    {
        "id": "set_1",
        "item_name": DOMINION_TOWER_GOLIATH_GLOVES,
        "encounters": (
            "nomad",
            "eruni_ayuni_leeuni",
            "dagannoth_sentinels",
            "the_untouchable",
            "balance_elemental",
            "ice_demon",
        ),
        "source": f"{_W}/Goliath_gloves?oldid=6581523",
    },
    {
        "id": "set_2",
        "item_name": DOMINION_TOWER_SPELLCASTER_GLOVES,
        "encounters": (
            "decaying_avatar",
            "dagannoth_mother_ii",
            "everlasting_illusive",
            "nezikchened",
            "arrav",
            "giant_roc",
        ),
        "source": f"{_W}/Spellcaster_gloves?oldid=6290648",
    },
    {
        "id": "set_3",
        "item_name": DOMINION_TOWER_SWIFT_GLOVES,
        "encounters": (
            "pest_queen",
            "zenevivia",
            "desert_treasure_guardians",
            "karamel_gelatinnoth",
            "jungle_demon",
            "inadequacy_doubts",
        ),
        "source": f"{_W}/Swift_gloves?oldid=6430300",
    },
)

# The achievement ladder. `kind` names the counter the requirement reads, and
# `reward` names what unlocking it makes claimable.
DOMINION_TOWER_ACHIEVEMENTS: tuple[dict[str, Any], ...] = (
    {"id": "climber_floor_5", "kind": "max_floor_climber", "value": 5,
     "display_name": "Reach floor 5 in Climber mode", "reward": "taunt_aggressive"},
    {"id": "climber_floor_10", "kind": "max_floor_climber", "value": 10,
     "display_name": "Reach floor 10 in Climber mode", "reward": "taunt_comedy"},
    {"id": "climber_floor_15", "kind": "max_floor_climber", "value": 15,
     "display_name": "Reach floor 15 in Climber mode", "reward": "powerup_help_horn"},
    {"id": "endurance_floor_15", "kind": "max_floor_endurance", "value": 15,
     "display_name": "Reach floor 15 in Endurance mode", "reward": "taunt_submissive"},
    {"id": "endurance_floor_20", "kind": "max_floor_endurance", "value": 20,
     "display_name": "Reach floor 20 in Endurance mode", "reward": "super_medallion"},
    {"id": "endurance_floor_25", "kind": "max_floor_endurance", "value": 25,
     "display_name": "Reach floor 25 in Endurance mode", "reward": "powerup_crossbow"},
    {"id": "all_handicaps", "kind": "handicaps_suffered", "value": DOMINION_TOWER_HANDICAP_COUNT,
     "display_name": "Suffer every type of handicap", "reward": "powerup_sword"},
    {"id": "half_journal", "kind": "journal_pages", "value": DOMINION_TOWER_JOURNAL_PAGE_COUNT // 2,
     "display_name": "Find half of the journal pages", "reward": "powerup_diminutive_bomb"},
    {"id": "all_journal", "kind": "journal_pages", "value": DOMINION_TOWER_JOURNAL_PAGE_COUNT,
     "display_name": "Find all of the journal pages", "reward": "powerup_massive_bomb"},
    {"id": "colossal_bomb", "kind": "journal_pages_and_factor",
     "value": DOMINION_TOWER_JOURNAL_PAGE_COUNT, "factor": DOMINION_TOWER_COLOSSAL_BOMB_FACTOR,
     "display_name": "All journal pages and a Dominion Factor of 10,000",
     "reward": "powerup_colossal_bomb"},
    {"id": "used_all_powerups", "kind": "powerups_used_in_arena",
     "value": 4,
     "display_name": "Use the help horn and all three bombs in the arena",
     "reward": "powerup_staff"},
    {"id": "kills_100", "kind": "boss_kills", "value": 100,
     "display_name": "Kill 100 bosses", "reward": "marker_stage_1"},
    {"id": "kills_200", "kind": "boss_kills", "value": 200,
     "display_name": "Kill 200 bosses", "reward": "marker_stage_2"},
    {"id": "kills_300", "kind": "boss_kills", "value": 300,
     "display_name": "Kill 300 bosses", "reward": "marker_stage_3"},
    {"id": "mines", "kind": "kills_and_specials", "value": DOMINION_TOWER_MINE_KILL_REQUIREMENT,
     "display_name": "Kill 400 bosses and fight all Special matches", "reward": "mines"},
    {"id": "dreadnip", "kind": "kills_and_spectate", "value": DOMINION_TOWER_DREADNIP_KILL_REQUIREMENT,
     "display_name": "Kill 450 bosses and spectate a match", "reward": "dreadnip"},
    {"id": "ascendancy", "kind": "boss_kills", "value": DOMINION_TOWER_ASCENDANCY_KILL_REQUIREMENT,
     "display_name": "Kill 500 bosses", "reward": "ascendancy_mines"},
    {"id": "set_1", "kind": "glove_set", "value": "set_1",
     "display_name": "Kill every boss in set 1 and 500 bosses", "reward": "goliath_gloves"},
    {"id": "set_2", "kind": "glove_set", "value": "set_2",
     "display_name": "Kill every boss in set 2 and 500 bosses", "reward": "spellcaster_gloves"},
    {"id": "set_3", "kind": "glove_set", "value": "set_3",
     "display_name": "Kill every boss in set 3 and 500 bosses", "reward": "swift_gloves"},
    {"id": "all_achievements", "kind": "all_other_achievements", "value": 0,
     "display_name": "Complete all other achievements", "reward": "marker_stage_4"},
)
DOMINION_TOWER_ACHIEVEMENTS_BY_ID = {row["id"]: row for row in DOMINION_TOWER_ACHIEVEMENTS}

# The four power-ups whose arena use unlocks the Dominion staff.
DOMINION_TOWER_STAFF_POWERUPS = (
    DOMINION_TOWER_HELP_HORN,
    DOMINION_TOWER_DIMINUTIVE_BOMB,
    DOMINION_TOWER_MASSIVE_BOMB,
    DOMINION_TOWER_COLOSSAL_BOMB,
)

# "Only four bombs may be used per match in Dominion Tower."
DOMINION_TOWER_BOMBS_PER_MATCH = 4
# "When fully charged it has 5 uses" and each use spawns one scorpion meat.
DOMINION_TOWER_HELP_HORN_USES = 5
# "It can only be eaten in the Dominion Tower and heals 220 life points."
DOMINION_TOWER_SCORPION_MEAT_HEAL = 220
# "damage one enemy for 1/10th of their current life points"
DOMINION_TOWER_DIMINUTIVE_BOMB_FRACTION = (1, 10)
# "damage up to three enemies at a time" — the share is not stated.
DOMINION_TOWER_MASSIVE_BOMB_TARGETS = 3
# PLACEHOLDER(dominion_tower.massive_bomb_fraction): the massive bomb's damage is
# never quantified; it splits the diminutive bomb's stated tenth across the three
# enemies it is stated to reach.
DOMINION_TOWER_MASSIVE_BOMB_FRACTION = (1, 10)
# PLACEHOLDER(dominion_tower.colossal_bomb_fraction): "a large amount of damage
# to all enemies" is the only description the period record gives. A quarter of
# current lifepoints keeps it strictly above the stated tenth.
DOMINION_TOWER_COLOSSAL_BOMB_FRACTION = (1, 4)

# "These mines will ALWAYS hit 20% of the monster's maximum life points."
DOMINION_TOWER_MINE_FRACTION = (1, 5)

DOMINION_TOWER_POWERUPS: tuple[dict[str, Any], ...] = (
    {
        "item_name": DOMINION_TOWER_HELP_HORN,
        "unlock": "powerup_help_horn",
        "effect": "spawn_food",
        "uses": DOMINION_TOWER_HELP_HORN_USES,
        "source": f"{_W}/Help_horn?oldid=6082361",
    },
    {
        "item_name": DOMINION_TOWER_DIMINUTIVE_BOMB,
        "unlock": "powerup_diminutive_bomb",
        "effect": "bomb",
        "targets": 1,
        "fraction": DOMINION_TOWER_DIMINUTIVE_BOMB_FRACTION,
        "source": f"{_W}/Diminutive_bomb?oldid=6552690",
    },
    {
        "item_name": DOMINION_TOWER_MASSIVE_BOMB,
        "unlock": "powerup_massive_bomb",
        "effect": "bomb",
        "targets": DOMINION_TOWER_MASSIVE_BOMB_TARGETS,
        "fraction": DOMINION_TOWER_MASSIVE_BOMB_FRACTION,
        "source": f"{_W}/Massive_bomb?oldid=5588105",
    },
    {
        "item_name": DOMINION_TOWER_COLOSSAL_BOMB,
        "unlock": "powerup_colossal_bomb",
        "effect": "bomb",
        "targets": 0,  # zero means every enemy in the arena
        "fraction": DOMINION_TOWER_COLOSSAL_BOMB_FRACTION,
        "source": f"{_W}/Colossal_bomb?oldid=5992282",
    },
    {
        "item_name": DOMINION_TOWER_SWORD,
        "unlock": "powerup_sword",
        "effect": "weapon",
        # "degrade into nothing after around 5 minutes of combat": 500 ticks.
        "charges": 500,
        "charge_unit": "ticks",
        "source": f"{_W}/Dominion_sword?oldid=6300686",
    },
    {
        "item_name": DOMINION_TOWER_CROSSBOW,
        "unlock": "powerup_crossbow",
        "effect": "weapon",
        # "only lasts for 100 shots before crumbling to pieces"
        "charges": 100,
        "charge_unit": "shots",
        "required_skill": ("ranged", 90),
        "source": f"{_W}/Dominion_crossbow?oldid=6155090",
    },
    {
        "item_name": DOMINION_TOWER_STAFF,
        "unlock": "powerup_staff",
        "effect": "weapon",
        # PLACEHOLDER(dominion_tower.staff_charges): "degrades based upon how many
        # hits you deal with it" with no number; the crossbow's stated hundred
        # hits stand in for the staff's own hit budget.
        "charges": 100,
        "charge_unit": "hits",
        "required_skill": ("magic", 90),
        "source": f"{_W}/Dominion_staff?oldid=6155092",
    },
)
DOMINION_TOWER_POWERUPS_BY_ITEM = {row["item_name"]: row for row in DOMINION_TOWER_POWERUPS}
DOMINION_TOWER_WEAPON_POWERUPS = tuple(
    row["item_name"] for row in DOMINION_TOWER_POWERUPS if row["effect"] == "weapon"
)
DOMINION_TOWER_BOMB_POWERUPS = tuple(
    row["item_name"] for row in DOMINION_TOWER_POWERUPS if row["effect"] == "bomb"
)
# PLACEHOLDER(dominion_tower.weapon_powerup_damage_bonus): the three tower-only
# weapons are described as powerful arena weapons without a single stated bonus
# or maximum hit. Half again the player's damage stands in while a weapon
# power-up is active.
DOMINION_TOWER_WEAPON_POWERUP_DAMAGE_MULTIPLIER = 1.5

# The two-dose tower-only potions, and what each one stands in for.
DOMINION_TOWER_POTIONS: tuple[dict[str, Any], ...] = (
    {
        "item_name": DOMINION_TOWER_DOM_SUPER_RESTORE,
        "effect": "super_restore",
        "doses": 2,
        "source": f"{_W}/Dom_super_restore?oldid=5588114",
    },
    {
        "item_name": DOMINION_TOWER_DOM_SUPER_PRAYER,
        "effect": "super_prayer",
        "doses": 2,
        "source": f"{_W}/Dom_super_prayer?oldid=5588111",
    },
    {
        "item_name": DOMINION_TOWER_DOM_SUPER_ANTIPOISON,
        "effect": "super_antipoison",
        "doses": 2,
        "source": f"{_W}/Dom_super_antipoison?oldid=5588115",
    },
    {
        "item_name": DOMINION_TOWER_DOM_SARADOMIN_BREW,
        "effect": "saradomin_brew",
        "doses": 2,
        "source": f"{_W}/Dom_saradomin_brew?oldid=5588118",
    },
)
DOMINION_TOWER_POTIONS_BY_ITEM = {row["item_name"]: row for row in DOMINION_TOWER_POTIONS}

# Reward-box contents, exactly the list the pinned Reward box revision gives.
# "The Reward Box will only give players up to 20 of any individual item at
# once, excluding scorpion meat."
DOMINION_TOWER_REWARD_BOX_ITEM_CAP = 20
DOMINION_TOWER_REWARD_BOX_ITEMS: tuple[dict[str, Any], ...] = (
    {"item_name": DOMINION_TOWER_SCORPION_MEAT, "quantity": 28, "capped": False},
    {"item_name": DOMINION_TOWER_DOM_SUPER_RESTORE, "quantity": 2, "capped": True},
    {"item_name": DOMINION_TOWER_DOM_SARADOMIN_BREW, "quantity": 2, "capped": True},
    {"item_name": DOMINION_TOWER_DOM_SUPER_ANTIPOISON, "quantity": 2, "capped": True},
    {"item_name": DOMINION_TOWER_DOM_SUPER_PRAYER, "quantity": 2, "capped": True},
    {"item_name": "Blood rune", "quantity": 20, "capped": True},
    {"item_name": "Soul rune", "quantity": 20, "capped": True},
    {"item_name": "Death rune", "quantity": 20, "capped": True},
    {"item_name": "Nature rune", "quantity": 20, "capped": True},
    {"item_name": "Rune arrows", "quantity": 20, "capped": True},
    {"item_name": "Runite bolts", "quantity": 20, "capped": True},
    {"item_name": "Big bones", "quantity": 20, "capped": True},
    {"item_name": "Dragon bones", "quantity": 20, "capped": True},
    {"item_name": "Dagannoth bones", "quantity": 20, "capped": True},
)
# PLACEHOLDER(dominion_tower.reward_box_rolls): Darkan's reconstructed reward
# routine draws three common rewards, but no period source states the roll count.
DOMINION_TOWER_REWARD_BOX_ROLLS = 3
# PLACEHOLDER(dominion_tower.journal_page_chance): journal pages are stated to
# come from the reward box, and the strategy advice is to claim small boxes often
# to farm them, but no revision gives the rate.
DOMINION_TOWER_JOURNAL_PAGE_CHANCE = 0.25

# "It can give experience in Attack, Strength, Defence, Constitution, Prayer,
# Ranged, and Magic. The chosen skill must be at least level 75 to use."
DOMINION_TOWER_XP_BOOK_SKILL_LEVEL = 75
DOMINION_TOWER_XP_BOOK_SKILLS = (
    "attack",
    "strength",
    "defense",
    "constitution",
    "prayer",
    "ranged",
    "magic",
)
# The worked exchange example — 28 scorpion meat giving 1,410 in attack,
# strength, defence or constitution, 1,287 magic, 1,207 ranged and 677 prayer —
# is the only per-skill ratio the period record states.
DOMINION_TOWER_XP_BOOK_SKILL_RATIOS = {
    "attack": 1.0,
    "strength": 1.0,
    "defense": 1.0,
    "constitution": 1.0,
    "magic": 1287.0 / 1410.0,
    "ranged": 1207.0 / 1410.0,
    "prayer": 677.0 / 1410.0,
}
# PLACEHOLDER(dominion_tower.xp_book_factor_scale): the book's experience is
# stated to depend on the skill's level and the Dominion Factor held, with no
# formula anywhere. One base point of experience per ten factor reproduces the
# 1,410-point worked example at the exchange sizes the article describes.
DOMINION_TOWER_XP_BOOK_FACTOR_SCALE = 0.1
# "The following rewards can be exchanged for Xp books."
DOMINION_TOWER_EXCHANGEABLE_ITEMS = (
    DOMINION_TOWER_SWORD,
    DOMINION_TOWER_STAFF,
    DOMINION_TOWER_CROSSBOW,
    DOMINION_TOWER_DOM_SUPER_RESTORE,
    DOMINION_TOWER_DOM_SUPER_PRAYER,
    DOMINION_TOWER_DOM_SUPER_ANTIPOISON,
    DOMINION_TOWER_DOM_SARADOMIN_BREW,
    DOMINION_TOWER_DIMINUTIVE_BOMB,
    DOMINION_TOWER_MASSIVE_BOMB,
    DOMINION_TOWER_COLOSSAL_BOMB,
    DOMINION_TOWER_SCORPION_MEAT,
    DOMINION_TOWER_HELP_HORN,
)
# PLACEHOLDER(dominion_tower.exchange_factor_per_item): the exchange converts a
# full inventory of rewards into one book whose size depends on "the number and
# type of rewards exchanged". The worked example is 28 scorpion meat for a
# 1,410-point book, which is 50 factor-equivalents per item.
DOMINION_TOWER_EXCHANGE_FACTOR_PER_ITEM = 500

# The medallion and marker boosts, all stated in levels of Attack, Strength,
# Defence, Ranged and Magic and all confined to the tower.
DOMINION_TOWER_MEDALLION_BOOST = 4
DOMINION_TOWER_SUPER_MEDALLION_BOOST = 8
DOMINION_TOWER_MEDALLION_TELEPORTS_PER_DAY = 3
DOMINION_TOWER_MARKER_STAGE_BOOSTS = {1: 4, 2: 6, 3: 8, 4: 10}
DOMINION_TOWER_BOOSTED_SKILLS = ("attack", "strength", "defense", "ranged", "magic")


# "finishing all special challenges, with the exception of Sunfreet" is what the
# Dominion mine unlock actually asks for.
DOMINION_TOWER_MINE_SPECIAL_MATCH_IDS = tuple(
    row["id"]
    for row in DOMINION_TOWER_SPECIAL_MATCHES
    if not row["npcs"][0].startswith("sunfreet")
)

# ---------------------------------------------------------------------------
# Items, equipment and assets
# ---------------------------------------------------------------------------

# item name -> (rev-742/727 item id where recovered, stackable)
# PLACEHOLDER(dominion_tower.reward_item_ids): none of the pinned glove, weapon,
# mine, medallion, marker, journal, potion, bomb or horn revisions prints an item
# id, and the cache item dump carries no row under these display names. Zero
# means "identity not recovered" and is never written into a save.
_DOMINION_TOWER_ITEM_ROWS: dict[str, tuple[int, bool]] = {
    DOMINION_TOWER_GOLIATH_GLOVES: (0, False),
    DOMINION_TOWER_SPELLCASTER_GLOVES: (0, False),
    DOMINION_TOWER_SWIFT_GLOVES: (0, False),
    DOMINION_TOWER_DREADNIP: (0, True),
    DOMINION_TOWER_SWORD: (0, False),
    DOMINION_TOWER_STAFF: (0, False),
    DOMINION_TOWER_CROSSBOW: (0, False),
    DOMINION_TOWER_MINE: (0, True),
    DOMINION_TOWER_ASCENDANCY_MINE: (0, True),
    DOMINION_TOWER_MEDALLION: (0, False),
    DOMINION_TOWER_SUPER_MEDALLION: (0, False),
    DOMINION_TOWER_MARKER: (0, False),
    DOMINION_TOWER_JOURNAL_PAGE: (0, True),
    DOMINION_TOWER_SCORPION_MEAT: (0, True),
    DOMINION_TOWER_XP_BOOK: (0, False),
    DOMINION_TOWER_HELP_HORN: (0, False),
    DOMINION_TOWER_DIMINUTIVE_BOMB: (0, True),
    DOMINION_TOWER_MASSIVE_BOMB: (0, True),
    DOMINION_TOWER_COLOSSAL_BOMB: (0, True),
    DOMINION_TOWER_DOM_SUPER_RESTORE: (0, True),
    DOMINION_TOWER_DOM_SUPER_PRAYER: (0, True),
    DOMINION_TOWER_DOM_SUPER_ANTIPOISON: (0, True),
    DOMINION_TOWER_DOM_SARADOMIN_BREW: (0, True),
}

# The three glove rows exactly as each glove's pinned infobox prints them.
# (item name, combat skill, required level, bonus block)
_DOMINION_TOWER_GLOVE_ROWS: tuple[tuple[str, str, int, dict[str, int]], ...] = (
    (
        DOMINION_TOWER_GOLIATH_GLOVES,
        "attack",
        80,
        {
            "attack_stab": 14,
            "attack_slash": 14,
            "attack_crush": 14,
            "attack_magic": 6,
            "attack_ranged": 12,
            "defence_stab": 16,
            "defence_slash": 16,
            "defence_crush": 16,
            "defence_magic": 6,
            "defence_ranged": 12,
            "melee_strength": 13,
        },
    ),
    (
        DOMINION_TOWER_SPELLCASTER_GLOVES,
        "magic",
        80,
        {
            "attack_stab": 2,
            "attack_slash": 2,
            "attack_crush": 2,
            "attack_magic": 8,
            "defence_stab": 4,
            "defence_slash": 5,
            "defence_crush": 4,
            "defence_magic": 9,
            "defence_ranged": 3,
        },
    ),
    (
        DOMINION_TOWER_SWIFT_GLOVES,
        "ranged",
        80,
        {
            "attack_slash": 2,
            "attack_crush": 2,
            "attack_magic": 2,
            "attack_ranged": 15,
            "defence_stab": 2,
            "defence_slash": 2,
            "defence_crush": 2,
            "defence_magic": 3,
            "defence_ranged": 15,
        },
    ),
)

DOMINION_TOWER_ASSET_MANIFEST: tuple[dict[str, Any], ...] = (
    {
        "item_name": DOMINION_TOWER_ACTIVITY_ID,
        "wiki_title": "Dominion sword.png",
        "output_path": "activityicons/dominion_tower.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_GOLIATH_GLOVES,
        "wiki_title": "Goliath gloves (black).png",
        "output_path": "activityitems/dominion_tower_goliath_gloves.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_SPELLCASTER_GLOVES,
        "wiki_title": "Spellcaster gloves.png",
        "output_path": "activityitems/dominion_tower_spellcaster_gloves.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_SWIFT_GLOVES,
        "wiki_title": "Swift gloves (black).png",
        "output_path": "activityitems/dominion_tower_swift_gloves.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_DREADNIP,
        "wiki_title": "Dreadnip.png",
        "output_path": "activityitems/dominion_tower_dreadnip.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_SWORD,
        "wiki_title": "Dominion sword.png",
        "output_path": "activityitems/dominion_tower_sword.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_STAFF,
        "wiki_title": "Dominion staff.png",
        "output_path": "activityitems/dominion_tower_staff.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_CROSSBOW,
        "wiki_title": "Dominion crossbow.png",
        "output_path": "activityitems/dominion_tower_crossbow.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_JOURNAL_PAGE,
        "wiki_title": "A journal page.png",
        "output_path": "activityitems/dominion_tower_journal_page.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_SCORPION_MEAT,
        "wiki_title": "Scorpion meat.png",
        "output_path": "activityitems/dominion_tower_scorpion_meat.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_XP_BOOK,
        "wiki_title": "Xp book.png",
        "output_path": "activityitems/dominion_tower_xp_book.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_HELP_HORN,
        "wiki_title": "Help horn.png",
        "output_path": "activityitems/dominion_tower_help_horn.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_MEDALLION,
        "wiki_title": "Dominion medallion.png",
        "output_path": "activityitems/dominion_tower_medallion.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_MARKER,
        "wiki_title": "Dominion marker (stage 1).png",
        "output_path": "activityitems/dominion_tower_marker.png",
        "size": 64,
    },
    {
        "item_name": DOMINION_TOWER_MINE,
        "wiki_title": "Dominion mine.png",
        "output_path": "activityitems/dominion_tower_mine.png",
        "size": 64,
    },
)


def dominion_tower_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        item_name: {
            "category": "material",
            "stackable": stackable,
            "tradeable": False,
            "source": DOMINION_TOWER_SOURCE,
        }
        for item_name, (_item_id, stackable) in _DOMINION_TOWER_ITEM_ROWS.items()
    }


def dominion_tower_equipment_data_as_dict() -> dict[str, Any]:
    """The three Dominion glove pairs, as real hands-slot equipment."""
    from .equipment_data import EquipmentBonuses, EquipmentItem

    return {
        item_name: EquipmentItem(
            item_name=item_name,
            slot="hands",
            combat_skill=None,
            required_level=required_level,
            two_handed=False,
            equipment_type="gloves",
            bonuses=EquipmentBonuses(**bonuses),
            attack_speed=4,
            source_item_id=0,
            source=DOMINION_TOWER_SOURCE,
            source_status="pinned pre-cutoff item revision",
            skill_requirements=((combat_skill, required_level),),
        )
        for item_name, combat_skill, required_level, bonuses in _DOMINION_TOWER_GLOVE_ROWS
    }


def dominion_tower_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        DOMINION_TOWER_ACTIVITY_ID: {
            "display_name": "Dominion Tower",
            "requirements": {},
            "batch_size": 1,
            "group": "minigames",
            "outputs": (DOMINION_TOWER_XP_BOOK, DOMINION_TOWER_JOURNAL_PAGE),
            "source": DOMINION_TOWER_SOURCE,
        }
    }


def dominion_tower_enemy_pure(npc: dict[str, Any], attack_style: str) -> dict[str, Any]:
    """Adapt one roster NPC into the shared Combat engine's enemy shape."""
    styles = tuple(npc["attack_styles"])
    return {
        "display_name": npc["display_name"],
        "npc_id": npc["npc_id"],
        "level": npc["level"],
        "group": "Dominion Tower",
        "stats": copy.deepcopy(npc["stats"]),
        "bonuses": dict(npc["bonuses"]),
        "attack_style": attack_style if attack_style in styles else styles[0],
        "attack_speed": npc["attack_speed"],
        "max_hit": npc["max_hit"],
        "poison_damage": npc["poison_damage"],
        "drops": {"guaranteed": (), "tables": ()},
        "slayer_xp": 0.0,
        "encounter_only": True,
        "source": npc["source"],
    }


def dominion_tower_enemy_registry_as_dict() -> dict[str, dict[str, Any]]:
    """One registry row so the shared Combat target list can name the tower."""
    return {
        DOMINION_TOWER_TARGET_ID: dominion_tower_enemy_pure(
            copy.deepcopy(DOMINION_TOWER_NPCS["delrith"]),
            "melee",
        )
    }
