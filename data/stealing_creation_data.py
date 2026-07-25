"""Period-pinned Stealing Creation data and bounded review abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..data.equipment_data import EquipmentBonuses, EquipmentItem


STEALING_CREATION_ACTIVITY_ID = "stealing_creation"
STEALING_CREATION_COMBAT_TARGET_ID = "stealing_creation_raider"
STEALING_CREATION_SOURCE = (
    "RuneScape Wiki Stealing Creation oldid=6518618 (2012-11-02); "
    "Sacred clay oldid=5902636; Creation kiln oldid=5905778; "
    "Proto-tool oldid=6514505; Volatile clay tool oldid=6314239"
)

# One source minute maps to one meaningful duty review. The source combat game
# lasted 20 minutes; reviews, never the wall clock, advance this budget.
STEALING_CREATION_SESSION_REVIEWS = 20
STEALING_CREATION_COMBAT_TICKS_PER_REVIEW = 6
STEALING_CREATION_REWARD_COST = 20
STEALING_CREATION_SCORE_PER_CLASS = 15
STEALING_CREATION_CLAY_PER_GATHER_REVIEW = 10
STEALING_CREATION_OPPONENT_CLAY_PER_REVIEW = 5
STEALING_CREATION_RAID_INTERVAL_REVIEWS = (4, 6)

STEALING_CREATION_CLASS_REQUIREMENTS = {
    1: 1,
    2: 20,
    3: 40,
    4: 60,
    5: 80,
}

STEALING_CREATION_GATHER_METHODS: dict[str, dict[str, Any]] = {
    "fragments": {
        "display_name": "Ground fragments",
        "skill_level_key": "",
        "class_cap": 1,
    },
    "mine": {
        "display_name": "Mine sacred clay rock",
        "skill_level_key": "mining_level",
        "class_cap": 5,
    },
    "fish": {
        "display_name": "Fish sacred clay pool",
        "skill_level_key": "fishing_level",
        "class_cap": 5,
    },
    "hunt": {
        "display_name": "Catch sacred clay swarm",
        "skill_level_key": "hunter_level",
        "class_cap": 5,
    },
    "chop": {
        "display_name": "Chop sacred clay tree",
        "skill_level_key": "woodcutting_level",
        "class_cap": 5,
    },
}

STEALING_CREATION_RECIPES: dict[str, dict[str, Any]] = {
    "hatchet": {
        "display_name": "Sacred clay hatchet",
        "skill_level_key": "woodcutting_level",
        "session_slot": "tool",
        "cache_item_ids": (14132, 14133),
    },
    "scimitar": {
        "display_name": "Sacred clay scimitar",
        "skill_level_key": "attack_level",
        "session_slot": "weapon",
        "cache_item_ids": (14287, 14288),
    },
    "platebody": {
        "display_name": "Sacred clay platebody",
        "skill_level_key": "defense_level",
        "session_slot": "armour",
        "cache_item_ids": (14347, 14348),
    },
    "barrier": {
        "display_name": "Sacred clay barrier",
        "skill_level_key": "construction_level",
        "session_slot": "barrier",
        "cache_item_ids": tuple(range(14172, 14182)),
    },
}


@dataclass(frozen=True)
class StealingCreationRewardForm:
    id: str
    display_name: str
    exp_keys: tuple[str, ...]
    bonus_xp_capacity: float
    capacity_status: str
    bonus_xp_capacity_by_exp_key: tuple[tuple[str, float], ...] = ()


# Capacities are bonus-XP budgets. Ranged period statements use their lower
# endpoint. The butterfly net has no recovered lifetime and uses the explicit
# breadth fallback recorded in the source audit.
STEALING_CREATION_REWARD_FORMS = (
    StealingCreationRewardForm(
        "hammer",
        "Hammer",
        ("smithing_exp", "construction_exp"),
        25_375.0,
        "period explicit skill-specific capacities",
        (("smithing_exp", 32_062.0), ("construction_exp", 25_375.0)),
    ),
    StealingCreationRewardForm(
        "needle", "Needle", ("crafting_exp",), 21_948.0, "period lower endpoint / 2"
    ),
    StealingCreationRewardForm(
        "hatchet", "Hatchet", ("woodcutting_exp",), 15_000.0, "period lower endpoint / 2"
    ),
    StealingCreationRewardForm(
        "pickaxe", "Pickaxe", ("mining_exp",), 7_000.0, "period approximate total / 2"
    ),
    StealingCreationRewardForm(
        "harpoon", "Harpoon", ("fishing_exp",), 11_750.0, "period explicit bonus XP"
    ),
    StealingCreationRewardForm(
        "fletching_knife",
        "Fletching knife",
        ("fletching_exp",),
        38_500.0,
        "period lower endpoint / 2",
    ),
    StealingCreationRewardForm(
        "butterfly_net",
        "Butterfly net",
        ("hunter_exp",),
        15_000.0,
        "source_blocked lifetime; bounded breadth fallback",
    ),
)
STEALING_CREATION_REWARD_FORM_BY_ID = {
    form.id: form for form in STEALING_CREATION_REWARD_FORMS
}

STEALING_CREATION_REWARD_ITEMS = {
    "Proto-tool": {
        "category": "tool",
        "item_id": 14106,
        "stackable": False,
        "tradeable": False,
        "source": "RuneScape cache rev 742 item 14106; Proto-tool oldid=6514505",
    },
    "Volatile clay tool": {
        "category": "tool",
        "item_id": 14098,
        "stackable": False,
        "tradeable": False,
        "source": "RuneScape cache rev 742 item 14098; Volatile clay tool oldid=6314239",
    },
}


def _session_scimitar(tier: int) -> EquipmentItem:
    # The cache proves the equipment identity; monotonic bonuses are an explicit
    # bounded abstraction that makes the temporary equipment mechanically live.
    strength = tier * 6
    return EquipmentItem(
        item_name=f"Sacred clay scimitar (class {tier})",
        slot="weapon",
        combat_skill="attack",
        required_level=1,
        two_handed=False,
        equipment_type="scimitar",
        bonuses=EquipmentBonuses(
            attack_slash=tier * 8,
            melee_strength=strength,
        ),
        attack_speed=4,
        source_item_id=14287,
        source=STEALING_CREATION_SOURCE,
        source_status="cache identity; bounded monotonic session bonuses",
        weapon_type=4,
    )


def _session_platebody(tier: int) -> EquipmentItem:
    defence = tier * 7
    return EquipmentItem(
        item_name=f"Sacred clay platebody (class {tier})",
        slot="body",
        combat_skill="defense",
        required_level=1,
        two_handed=False,
        equipment_type="melee_armour",
        bonuses=EquipmentBonuses(
            defence_stab=defence,
            defence_slash=defence,
            defence_crush=defence,
            defence_magic=tier * 3,
            defence_ranged=tier * 6,
        ),
        attack_speed=4,
        source_item_id=14347,
        source=STEALING_CREATION_SOURCE,
        source_status="cache identity; bounded monotonic session bonuses",
    )


STEALING_CREATION_SESSION_EQUIPMENT = {
    spec.item_name: spec
    for tier in range(1, 6)
    for spec in (_session_scimitar(tier), _session_platebody(tier))
}


def stealing_creation_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        STEALING_CREATION_ACTIVITY_ID: {
            "display_name": "Stealing Creation",
            "requirements": {},
            "batch_size": 1,
            "group": "minigames",
            "outputs": tuple(STEALING_CREATION_REWARD_ITEMS),
            "source": STEALING_CREATION_SOURCE,
        }
    }


def stealing_creation_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {name: dict(spec) for name, spec in STEALING_CREATION_REWARD_ITEMS.items()}
