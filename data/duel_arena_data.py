"""Cutoff Duel Arena rules, cap progression, and bounded opponent metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem


DUEL_ARENA_ACTIVITY_ID = "duel_arena"
DUEL_ARENA_MIN_COMBAT_LEVEL = 3
DUEL_ARENA_MAX_COMBAT_LEVEL = 138
DUEL_ARENA_POINTS_TO_WIN = 3
DUEL_ARENA_MAX_REVIEWS = 5

DUEL_ARENA_SOURCE = (
    "RuneScape Wiki Duel Arena oldid=6398696 "
    "(2012-10-14T03:38:01Z); Duellist's cap oldid=6579418 "
    "(2012-11-18T23:11:12Z); Darkan DuelRules.java and "
    "DuelArenaController.java at "
    "d1d10fe9f9f9692e4a9d14d2435e2028934efe85; OpenRS2 cache rev 742"
)


@dataclass(frozen=True)
class DuelArenaRulePreset:
    id: str
    display_name: str
    description: str
    darkan_rule_id: int


# The cutoff article explicitly says the interface has eleven options. It then
# lists Summoning Enabled as a separate members option, so the counted eleven
# below are the configurable family contract.
DUEL_ARENA_RULE_PRESETS = (
    DuelArenaRulePreset(
        "no_ranged",
        "No Ranged",
        "Ranged attacks are disabled for both duellists.",
        0,
    ),
    DuelArenaRulePreset(
        "no_melee",
        "No Melee",
        "Melee attacks, including bare-handed attacks, are disabled.",
        1,
    ),
    DuelArenaRulePreset(
        "no_magic",
        "No Magic",
        "Magic attack spells are disabled.",
        2,
    ),
    DuelArenaRulePreset(
        "no_special_attacks",
        "No Special Attacks",
        "Weapon special attacks are disabled.",
        9,
    ),
    DuelArenaRulePreset(
        "fun_weapons",
        "Fun Weapons",
        "Only period fun weapons may be used.",
        8,
    ),
    DuelArenaRulePreset(
        "no_forfeit",
        "No Forfeit",
        "The arena trapdoor cannot be used to concede.",
        7,
    ),
    DuelArenaRulePreset(
        "no_drinks",
        "No Drinks",
        "Combat-boosting drinks are disabled.",
        3,
    ),
    DuelArenaRulePreset(
        "no_food",
        "No Food",
        "Food and phoenix-necklace healing are disabled.",
        4,
    ),
    DuelArenaRulePreset(
        "no_prayer",
        "No Prayer",
        "Prayer use is disabled.",
        5,
    ),
    DuelArenaRulePreset(
        "no_movement",
        "No Movement",
        "Both duellists start adjacent and cannot move.",
        25,
    ),
    DuelArenaRulePreset(
        "obstacles",
        "Obstacles",
        "The duel uses an obstacle arena.",
        6,
    ),
)
DUEL_ARENA_RULE_IDS = tuple(rule.id for rule in DUEL_ARENA_RULE_PRESETS)
DUEL_ARENA_RULES_BY_ID = {rule.id: rule for rule in DUEL_ARENA_RULE_PRESETS}


@dataclass(frozen=True)
class DuellistsCapTier:
    tier: int
    minimum_wins: int
    source_item_id: int
    item_name: str
    asset_filename: str


DUELLISTS_CAP_TIERS = (
    DuellistsCapTier(1, 0, 20795, "Duellist's cap (tier 1)", "duellists_cap_tier_1.png"),
    DuellistsCapTier(2, 10, 20796, "Duellist's cap (tier 2)", "duellists_cap_tier_2.png"),
    DuellistsCapTier(3, 100, 20797, "Duellist's cap (tier 3)", "duellists_cap_tier_3.png"),
    DuellistsCapTier(4, 500, 20798, "Duellist's cap (tier 4)", "duellists_cap_tier_4.png"),
    DuellistsCapTier(5, 2_000, 20799, "Duellist's cap (tier 5)", "duellists_cap_tier_5.png"),
    DuellistsCapTier(6, 5_000, 20800, "Duellist's cap (tier 6)", "duellists_cap_tier_6.png"),
)
# Player-relative simulated opponents are an AnkiScape abstraction. Cycling a
# fixed band keeps direct entry deterministic, bounded, and undo-friendly.
DUEL_ARENA_OPPONENT_OFFSETS = (-8, 0, 8)


def duel_arena_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        DUEL_ARENA_ACTIVITY_ID: {
            "display_name": "Duel Arena",
            "requirements": {},
            "skill_requirements": {},
            "outputs": tuple(tier.item_name for tier in DUELLISTS_CAP_TIERS),
            "batch_size": 1,
            "group": "minigames",
            "source": DUEL_ARENA_SOURCE,
        }
    }


def duel_arena_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        tier.item_name: {
            "category": "equipment",
            "source_item_id": tier.source_item_id,
            "stackable": False,
            "tradeable": False,
            "equipment_slot": "head",
            "source": DUEL_ARENA_SOURCE,
        }
        for tier in DUELLISTS_CAP_TIERS
    }


def duel_arena_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    return {
        tier.item_name: EquipmentItem(
            item_name=tier.item_name,
            slot="head",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="duellists_cap",
            bonuses=EquipmentBonuses(),
            attack_speed=4,
            source_item_id=tier.source_item_id,
            source=DUEL_ARENA_SOURCE,
            source_status="pinned period zero-bonus equipment table",
            skill_requirements=(),
            weapon_type=-1,
        )
        for tier in DUELLISTS_CAP_TIERS
    }
