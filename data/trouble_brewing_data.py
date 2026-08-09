"""Period Trouble Brewing values and disclosed horizontal abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem
from .treasure_trails_data import CLUE_SCROLL_ITEMS


TROUBLE_BREWING_ACTIVITY_ID = "trouble_brewing"
TROUBLE_BREWING_SOURCE = (
    "RuneScape Wiki Trouble Brewing oldid=6579342 "
    "(2012-11-18T20:43:05Z); Honest Jimmy's House of Stuff "
    "oldid=6393015 (2012-10-13T04:08:35Z); OpenRS2 rev-742"
)

# The source game lasted twenty minutes but publishes no discrete action count
# or opponent-team production curve. The owner-settled event-scaled model is a
# sixteen-beat race; every number below is disclosed as provisional/source.
TROUBLE_BREWING_EVENT_REVIEWS = 16
TROUBLE_BREWING_OPPONENT_BATCH_PROGRESS = 10
TROUBLE_BREWING_OPPONENT_EXTRA_PROGRESS_CHANCE = 0.40
TROUBLE_BREWING_OPPONENT_SABOTAGE_CHANCE = 1.0 / 6.0
TROUBLE_BREWING_PLAYER_SABOTAGE_PROGRESS = 3
TROUBLE_BREWING_PLAYER_SABOTAGE_REVIEWS = 2

TROUBLE_BREWING_BOILER_COUNT = 3
TROUBLE_BREWING_BOILER_START_FUEL = 3
TROUBLE_BREWING_BOILER_MAX_FUEL = 10
TROUBLE_BREWING_BOILER_BATCH_FUEL = 3
TROUBLE_BREWING_CONTRIBUTION_CAP = 100

TROUBLE_BREWING_RECIPE = {
    "water": 5,
    "coloured_water": 3,
    "sweetgrubs": 1,
    "scrapey_bark": 1,
    "bitternut": 1,
}

TROUBLE_BREWING_DUTIES = (
    ("water", "Pump water"),
    ("coloured_water", "Prepare coloured water"),
    ("sweetgrubs", "Gather sweetgrubs"),
    ("scrapey_bark", "Cut scrapey bark"),
    ("bitternut", "Send a monkey for bitternuts"),
    ("tend_boilers", "Tend the boilers"),
    ("pack_rum", "Pack finished rum"),
    ("sabotage", "Sabotage the other team"),
)

# Exact source XP per deposited ingredient or duty.
TROUBLE_BREWING_DUTY_XP = {
    "coloured_water": {"cooking": 120.0},
    "sweetgrubs": {"cooking": 40.0},
    "scrapey_bark": {"woodcutting": 25.0, "cooking": 40.0},
    "bitternut": {"agility": 15.0, "cooking": 80.0},
    "sabotage": {"firemaking": 50.0},
    "repair": {"crafting": 25.0},
}
TROUBLE_BREWING_BOTTLE_XP = {
    "crafting": 100.0,
    "cooking": 250.0,
    "firemaking": 150.0,
}


@dataclass(frozen=True)
class TroubleBrewingReward:
    reward_id: str
    display_name: str
    pieces_of_eight: int
    source_item_id: int
    slot: str | None = None
    two_handed: bool = False
    weapon_type: int = -1
    attack_speed: int = 4
    teleport_destination: str = ""
    clue_tier: str = ""
    item_category: str = "food"
    description: str = ""


TROUBLE_BREWING_NAVAL_COLOURS = (
    ("Blue", 8952, 8959, 8991),
    ("Green", 8953, 8960, 8992),
    ("Red", 8954, 8961, 8993),
    ("Brown", 8955, 8962, 8994),
    ("Black", 8956, 8963, 8995),
    ("Purple", 8957, 8964, 8996),
    ("Grey", 8958, 8965, 8997),
)

TROUBLE_BREWING_REWARDS = tuple(
    reward
    for colour, shirt_id, hat_id, slacks_id in TROUBLE_BREWING_NAVAL_COLOURS
    for reward in (
        TroubleBrewingReward(
            reward_id=f"{colour.lower()}_naval_shirt",
            display_name=f"{colour} naval shirt",
            pieces_of_eight=100,
            source_item_id=shirt_id,
            slot="body",
        ),
        TroubleBrewingReward(
            reward_id=f"{colour.lower()}_tricorn_hat",
            display_name=f"{colour} tricorn hat",
            pieces_of_eight=50,
            source_item_id=hat_id,
            slot="head",
        ),
        TroubleBrewingReward(
            reward_id=f"{colour.lower()}_navy_slacks",
            display_name=f"{colour} navy slacks",
            pieces_of_eight=100,
            source_item_id=slacks_id,
            slot="legs",
        ),
    )
) + (
    TroubleBrewingReward(
        "cutthroat_flag",
        "Cutthroat flag",
        200,
        8966,
        "weapon",
        weapon_type=14,
    ),
    TroubleBrewingReward(
        "guilded_smile_flag",
        "Guilded smile flag",
        200,
        8967,
        "weapon",
        weapon_type=14,
        attack_speed=2,
    ),
    TroubleBrewingReward(
        "bronze_fist_flag",
        "Bronze fist flag",
        300,
        8968,
        "weapon",
        weapon_type=14,
    ),
    TroubleBrewingReward(
        "lucky_shot_flag",
        "Lucky shot flag",
        400,
        8969,
        "weapon",
        weapon_type=14,
    ),
    TroubleBrewingReward(
        "treasure_flag",
        "Treasure flag",
        500,
        8970,
        "weapon",
        weapon_type=14,
    ),
    TroubleBrewingReward(
        "phasmatys_flag",
        "Phasmatys flag",
        600,
        8971,
        "weapon",
        two_handed=True,
        weapon_type=14,
    ),
    TroubleBrewingReward(
        "the_stuff",
        "The stuff",
        5,
        8988,
        item_category="material",
        description="Optional brewing additive that greatly improves the chance of mature ale.",
    ),
    TroubleBrewingReward(
        "red_rum",
        "Red rum",
        2,
        8940,
        teleport_destination="Trouble Brewing",
    ),
    TroubleBrewingReward(
        "blue_rum",
        "Blue rum",
        2,
        8941,
        teleport_destination="Trouble Brewing",
    ),
    TroubleBrewingReward(
        "medium_clue",
        CLUE_SCROLL_ITEMS["medium"],
        5_000,
        2801,
        clue_tier="medium",
    ),
)
TROUBLE_BREWING_REWARDS_BY_ID = {
    reward.reward_id: reward for reward in TROUBLE_BREWING_REWARDS
}
TROUBLE_BREWING_RUMS_BY_ITEM = {
    reward.display_name: reward
    for reward in TROUBLE_BREWING_REWARDS
    if reward.teleport_destination
}


def trouble_brewing_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        TROUBLE_BREWING_ACTIVITY_ID: {
            "display_name": "Trouble Brewing",
            "requirements": {},
            "skill_requirements": {"cooking": 40},
            "quest_requirements": ("cabin_fever",),
            "batch_size": 1,
            "group": "minigames",
            "outputs": tuple(
                reward.display_name for reward in TROUBLE_BREWING_REWARDS
            ),
            "source": TROUBLE_BREWING_SOURCE,
        }
    }


def trouble_brewing_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        reward.display_name: {
            "category": "equipment" if reward.slot else reward.item_category,
            "source_item_id": reward.source_item_id,
            "stackable": False,
            "tradeable": False,
            "source": TROUBLE_BREWING_SOURCE,
        }
        for reward in TROUBLE_BREWING_REWARDS
        if not reward.clue_tier
    }


def trouble_brewing_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    return {
        reward.display_name: EquipmentItem(
            item_name=reward.display_name,
            slot=reward.slot,
            combat_skill=None,
            required_level=1,
            two_handed=reward.two_handed,
            equipment_type="trouble_brewing_reward",
            bonuses=EquipmentBonuses(),
            attack_speed=reward.attack_speed,
            source_item_id=reward.source_item_id,
            source=(
                f"2011Scape rev-667 items.yml item {reward.source_item_id}; "
                + TROUBLE_BREWING_SOURCE
            ),
            source_status="items.yml equipment block; rev-742 identity and bonuses",
            skill_requirements=(),
            weapon_type=reward.weapon_type,
        )
        for reward in TROUBLE_BREWING_REWARDS
        if reward.slot
    }
