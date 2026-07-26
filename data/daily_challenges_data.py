"""Cutoff Challenge System facts and the review-scale challenge catalog.

The period system is a five-slot queue of Daily Challenges handed out by the
Imperial Guard Quartermaster in Burthorpe. One new challenge arrives per day,
the oldest is dropped when a sixth would be added, one challenge can be pinned,
and a player may opt individual maxed skills out of future assignments. There is
no skip and no reroll: the cutoff revision does not mention either, and an
earlier AnkiScape record that claimed one was an invention.

The catalog below is a real period subset, not a generated one. Every row is a
challenge that appears verbatim on the cutoff guide page, chosen so that the
whole mechanic — item hand-in and no-hand-in, single-item and multi-item credit,
action credit, combat-kill credit, and a level gate above 1 — is exercised by
challenges an ordinary low-level player can actually reach.
"""

from __future__ import annotations

from typing import Any


DAILY_CHALLENGES_SOURCE = (
    "RuneScape Wiki Challenge System (historical) oldid=6579729 "
    "(2012-11-19T02:58:19Z); Challenge System (historical)/Challenges "
    "oldid=6563665 (2012-11-16T09:49:20Z); Challenge Mystery Bag "
    "oldid=6548968 (2012-11-12T03:53:42Z); Challenge XP Lamp oldid=6422002 "
    "(2012-10-15T14:50:21Z)"
)

# "The list of daily challenges is limited to 5 challenges. A new daily
# challenge is added every day. ... if the list exceeds 5 challenges, the oldest
# challenge is removed from the list."
DAILY_CHALLENGE_ACTIVE_LIMIT = 5

# AnkiScape's disclosed review-scale day, shared with every other daily family.
DAILY_CHALLENGE_REVIEW_DAY = 240

DAILY_CHALLENGE_MYSTERY_BAG_ITEM = "Challenge Mystery Bag"
DAILY_CHALLENGE_XP_LAMP_ITEM = "Challenge XP Lamp"

# The period page says a completed challenge grants "extra experience" but never
# states an amount, and neither Darkan nor the rev-742 cache exposes the reward
# table. One constant applied by one rule, per the verification standard's
# preference over a table of fabricated per-row values.
# PLACEHOLDER(daily_challenges.reward_xp): a Darkan challenge-reward table or the
# cache's challenge config would replace this with the period per-challenge XP.
DAILY_CHALLENGE_REWARD_XP_PER_LEVEL = 100

# The skills a Challenge XP Lamp can be spent in, from the lamp's own page.
DAILY_CHALLENGE_LAMP_SKILLS = (
    ("constitution", "Constitution", "constitution_exp"),
    ("magic", "Magic", "magic_exp"),
    ("ranged", "Ranged", "ranged_exp"),
    ("attack", "Attack", "attack_exp"),
    ("defence", "Defence", "defense_exp"),
    ("strength", "Strength", "strength_exp"),
)

DAILY_CHALLENGE_SKILL_LABELS = {
    "combat": "Combat",
    "cooking": "Cooking",
    "firemaking": "Firemaking",
    "fishing": "Fishing",
    "mining": "Mining",
    "woodcutting": "Woodcutting",
}

# Skill-level keys for the level gate. Combat challenges gate on the player's
# combat level, which has no single save key, so it is resolved in the logic.
DAILY_CHALLENGE_SKILL_LEVEL_KEYS = {
    "cooking": "cooking_level",
    "firemaking": "firemaking_level",
    "fishing": "fishing_level",
    "mining": "mining_level",
    "woodcutting": "woodcutting_level",
}

DAILY_CHALLENGE_SKILL_EXP_KEYS = {
    "cooking": "cooking_exp",
    "firemaking": "firemaking_exp",
    "fishing": "fishing_exp",
    "mining": "mining_exp",
    "woodcutting": "woodcutting_exp",
}


def _challenge(
    challenge_id: str,
    name: str,
    task: str,
    skill: str,
    level: int,
    required: int,
    credit: dict[str, Any],
    *,
    hand_in: bool,
) -> dict[str, Any]:
    return {
        "challenge_id": challenge_id,
        "name": name,
        "task": task,
        "skill": skill,
        "level": level,
        "required": required,
        "credit": credit,
        "hand_in": hand_in,
        "reward_xp": DAILY_CHALLENGE_REWARD_XP_PER_LEVEL * level,
        "source": DAILY_CHALLENGES_SOURCE,
    }


# Every name, task text and quantity below is quoted from the cutoff guide page.
DAILY_CHALLENGE_DATA: dict[str, dict[str, Any]] = {
    row["challenge_id"]: row
    for row in (
        _challenge(
            "rampage_mk_i",
            "Rampage Mk I",
            "Kill 9 enemies of at least Combat level 2",
            "combat",
            1,
            9,
            {"kind": "kill", "minimum_combat_level": 2},
            hand_in=False,
        ),
        _challenge(
            "mining_copper_ore",
            "Copper Ore",
            "Mine copper ore: 25",
            "mining",
            1,
            25,
            {"kind": "output_item", "items": ("Copper ore",)},
            hand_in=True,
        ),
        _challenge(
            "mining_tin_ore",
            "Tin Ore",
            "Mine tin ore: 25",
            "mining",
            1,
            25,
            {"kind": "output_item", "items": ("Tin ore",)},
            hand_in=True,
        ),
        _challenge(
            "mining_clay",
            "Clay",
            "Mine clay: 42",
            "mining",
            1,
            42,
            {"kind": "output_item", "items": ("Clay",)},
            hand_in=True,
        ),
        _challenge(
            "cooking_chicken",
            "Chicken",
            "Cook 3 chicken",
            "cooking",
            1,
            3,
            {"kind": "output_item", "items": ("Cooked chicken",)},
            hand_in=True,
        ),
        _challenge(
            "cooking_seafood_buffet",
            "Seafood buffet!",
            "Cook 11 crayfish, shrimp, anchovies or sardines",
            "cooking",
            1,
            11,
            {
                "kind": "output_item",
                "items": ("Crayfish", "Shrimps", "Anchovies", "Sardine"),
            },
            hand_in=True,
        ),
        _challenge(
            "fishing_how_shellfish",
            "How Shellfish",
            "Catch 28 shrimp or crayfish",
            "fishing",
            1,
            28,
            {"kind": "output_item", "items": ("Raw shrimps", "Raw crayfish")},
            hand_in=True,
        ),
        _challenge(
            "firemaking_normal_logs",
            "Normal Logs",
            "Light 12 normal logs or add them to a bonfire",
            "firemaking",
            1,
            12,
            {"kind": "action", "actions": ("logs",)},
            hand_in=False,
        ),
        _challenge(
            "woodcutting_oak_logs",
            "Oak logs",
            "Cut oak logs: 80",
            "woodcutting",
            15,
            80,
            {"kind": "output_item", "items": ("Oak logs",)},
            hand_in=True,
        ),
    )
}


def daily_challenge_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    """The two reward items this family owns, registered without touching
    the generated item tables."""
    return {
        DAILY_CHALLENGE_MYSTERY_BAG_ITEM: {
            "category": "reward",
            "stackable": False,
            "tradeable": False,
            "source": DAILY_CHALLENGES_SOURCE,
            "source_item_id": 25071,
        },
        DAILY_CHALLENGE_XP_LAMP_ITEM: {
            "category": "reward",
            "stackable": False,
            "tradeable": False,
            "source": DAILY_CHALLENGES_SOURCE,
            "source_item_id": 25070,
        },
    }
