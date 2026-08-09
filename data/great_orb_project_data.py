"""Pinned pre-EOC Great Orb Project activity and reward data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem


GREAT_ORB_PROJECT_ACTIVITY_ID = "great_orb_project"
GREAT_ORB_PROJECT_SOURCE = (
    "RuneScape Wiki The Great Orb Project oldid=6564759 "
    "(2012-11-17T03:12:07Z)"
)
GREAT_ORB_PROJECT_ROUNDS = 8
GREAT_ORB_PROJECT_TEMP_CAPACITY = 28
OMNI_TALISMAN_XP = 13_605.0
OMNI_TALISMAN_SOURCE = (
    "RuneScape Wiki Omni-talisman oldid=6359046 "
    "(2012-10-06T21:05:58Z)"
)
OMNI_TIARA_SOURCE = (
    "RuneScape Wiki Omni-tiara oldid=6130195 "
    "(2012-08-23T01:01:50Z)"
)
OMNI_TALISMAN_ACCESS_PAIRS = (
    ("Air talisman", "Air tiara"),
    ("Blood talisman", "Blood tiara"),
    ("Body talisman", "Body tiara"),
    ("Chaos talisman", "Chaos tiara"),
    ("Cosmic talisman", "Cosmic tiara"),
    ("Death talisman", "Death tiara"),
    ("Earth talisman", "Earth tiara"),
    ("Fire talisman", "Fire tiara"),
    ("Law talisman", "Law tiara"),
    ("Mind talisman", "Mind tiara"),
    ("Nature talisman", "Nature tiara"),
    ("Water talisman", "Water tiara"),
)


@dataclass(frozen=True)
class GreatOrbAltar:
    id: str
    label: str
    rune: str
    base_xp: float
    multiplier_divisor: int


# The period members' game used these eight altars in this order. Base XP and
# deterministic multiple-rune thresholds reuse the sourced ordinary
# Runecrafting table; the activity doubles XP per essence.
GREAT_ORB_PROJECT_ALTARS = (
    GreatOrbAltar("air", "Air altar", "Air rune", 5.0, 11),
    GreatOrbAltar("mind", "Mind altar", "Mind rune", 5.5, 14),
    GreatOrbAltar("water", "Water altar", "Water rune", 6.0, 19),
    GreatOrbAltar("earth", "Earth altar", "Earth rune", 6.5, 26),
    GreatOrbAltar("fire", "Fire altar", "Fire rune", 7.0, 35),
    GreatOrbAltar("body", "Body altar", "Body rune", 7.5, 46),
    GreatOrbAltar("chaos", "Chaos altar", "Chaos rune", 8.5, 74),
    GreatOrbAltar("nature", "Nature altar", "Nature rune", 9.0, 91),
)

GREAT_ORB_PROJECT_DOCTRINES = (
    ("balanced", "Balanced"),
    ("attract", "Attract orbs"),
    ("repel", "Repel rivals"),
    ("barrier", "Barrier control"),
)

GREAT_ORB_PROJECT_CRAFTING_POLICIES = (
    ("craft_each_round", "Craft each round"),
    ("save_for_nature", "Save for Nature"),
)

# The cutoff reward article prices free-to-play talismans at 50 tokens and
# members-only talismans at 125. Death and Blood were the two exclusions.
GREAT_ORB_PROJECT_TALISMAN_REWARDS = (
    ("air_talisman", "Air talisman", 50, 1438),
    ("mind_talisman", "Mind talisman", 50, 1448),
    ("water_talisman", "Water talisman", 50, 1444),
    ("earth_talisman", "Earth talisman", 50, 1440),
    ("fire_talisman", "Fire talisman", 50, 1442),
    ("body_talisman", "Body talisman", 50, 1446),
    ("cosmic_talisman", "Cosmic talisman", 125, 1454),
    ("chaos_talisman", "Chaos talisman", 125, 1452),
    ("nature_talisman", "Nature talisman", 125, 1462),
    ("law_talisman", "Law talisman", 125, 1458),
)

MASTER_RUNECRAFTER_REWARDS = (
    (
        "master_runecrafter_hat",
        "Master runecrafter hat",
        15_000,
        21517,
        "head",
        3,
        0.008,
    ),
    (
        "master_runecrafter_body",
        "Master runecrafter body",
        15_000,
        21516,
        "body",
        5,
        0.016,
    ),
    (
        "master_runecrafter_skirt",
        "Master runecrafter skirt",
        15_000,
        21518,
        "legs",
        4,
        0.012,
    ),
    (
        "master_runecrafter_boots",
        "Master runecrafter boots",
        15_000,
        21519,
        "feet",
        2,
        0.004,
    ),
)
MASTER_RUNECRAFTER_SOURCE = (
    "RuneScape Wiki Master runecrafter robes oldid=6514332 "
    "(2012-11-01T00:45:56Z); OpenRS2 cache rev 742 item definitions"
)


# This catalog exercises repeatable consumables, every ordinary talisman,
# equipment, and the two existing cross-skill claim/conversion paths. Staves
# and teleport tablets remain separate mechanic families.
GREAT_ORB_PROJECT_REWARDS: dict[str, dict[str, Any]] = {
    "pure_essence": {
        "item": "Pure essence",
        "tokens": 1,
        "quantity": 1,
        "source_item_id": 7936,
        "tradeable": True,
        "stackable": False,
        "category": "resource",
    },
    **{
        reward_id: {
            "item": item,
            "tokens": tokens,
            "quantity": 1,
            "source_item_id": source_item_id,
            "tradeable": True,
            "stackable": False,
            "category": "tool",
        }
        for reward_id, item, tokens, source_item_id in (
            GREAT_ORB_PROJECT_TALISMAN_REWARDS
        )
    },
    "elemental_talisman": {
        "item": "Elemental talisman",
        "tokens": 125,
        "quantity": 1,
        "source_item_id": 5516,
        "tradeable": True,
        "stackable": False,
        "category": "tool",
    },
    **{
        reward_id: {
            "item": item,
            "tokens": tokens,
            "quantity": 1,
            "source_item_id": source_item_id,
            "tradeable": False,
            "stackable": False,
            "category": "equipment",
        }
        for reward_id, item, tokens, source_item_id, _slot, _bonus, _xp_rate in (
            MASTER_RUNECRAFTER_REWARDS
        )
    },
    "omni_talisman": {
        "item": "Omni-talisman",
        "tokens": 0,
        "quantity": 1,
        "source_item_id": 13649,
        "tradeable": False,
        "stackable": False,
        "category": "claim",
        "shop_label": "Omni-talisman · Elriss",
        "button_label": "Claim",
        "source": OMNI_TALISMAN_SOURCE,
    },
    "omni_tiara": {
        "item": "Omni-tiara",
        "tokens": 0,
        "quantity": 1,
        "source_item_id": 13655,
        "tradeable": False,
        "stackable": False,
        "category": "conversion",
        "shop_label": "Omni-tiara · Korvak",
        "button_label": "Make",
        "source": OMNI_TIARA_SOURCE,
    },
}


def great_orb_project_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        item: {
            "category": "equipment",
            "stackable": False,
            "tradeable": False,
            "source": MASTER_RUNECRAFTER_SOURCE,
            "source_item_id": source_item_id,
            "equipment_slot": slot,
            "equipment_type": "master_runecrafter",
        }
        for _reward_id, item, _tokens, source_item_id, slot, _bonus, _xp_rate in (
            MASTER_RUNECRAFTER_REWARDS
        )
    }


def great_orb_project_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    return {
        item: EquipmentItem(
            item_name=item,
            slot=slot,
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="master_runecrafter",
            bonuses=EquipmentBonuses(
                attack_magic=bonus,
                defence_stab=bonus,
                defence_slash=bonus,
                defence_crush=bonus,
                defence_magic=bonus,
                defence_ranged=bonus,
            ),
            attack_speed=4,
            source_item_id=source_item_id,
            source=MASTER_RUNECRAFTER_SOURCE,
            source_status="period wiki identity and rev-742 equipment definition",
            skill_requirements=(),
            weapon_type=-1,
        )
        for _reward_id, item, _tokens, source_item_id, slot, bonus, _xp_rate in (
            MASTER_RUNECRAFTER_REWARDS
        )
    }


def great_orb_project_activity_as_dict() -> dict[str, dict[str, Any]]:
    outputs = tuple(
        dict.fromkeys(
            tuple(altar.rune for altar in GREAT_ORB_PROJECT_ALTARS)
            + tuple(str(row["item"]) for row in GREAT_ORB_PROJECT_REWARDS.values())
        )
    )
    return {
        GREAT_ORB_PROJECT_ACTIVITY_ID: {
            "display_name": "Great Orb Project",
            "requirements": {},
            "skill_requirements": {"runecrafting": 50},
            "outputs": outputs,
            "batch_size": 1,
            "group": "minigames",
            "source": GREAT_ORB_PROJECT_SOURCE,
        }
    }
