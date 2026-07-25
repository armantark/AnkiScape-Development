"""Period Trouble Brewing values and disclosed horizontal abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..data.equipment_data import EquipmentBonuses, EquipmentItem


TROUBLE_BREWING_ACTIVITY_ID = "trouble_brewing"
TROUBLE_BREWING_SOURCE = (
    "RuneScape Wiki Trouble Brewing oldid=6573931 "
    "(2012-11-18T20:43:05Z); Honest Jimmy's House of Stuff "
    "oldid=6399561 (2012-10-13T04:08:35Z); OpenRS2 rev-742"
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


# One period cosmetic is sufficient to prove currency earning, direct purchase,
# bank reachability, and equipment use. The remaining colour sets and flags are
# catalog depth rather than a second mechanic.
TROUBLE_BREWING_REWARDS = (
    TroubleBrewingReward(
        reward_id="blue_tricorn_hat",
        display_name="Blue tricorn hat",
        pieces_of_eight=50,
        source_item_id=8959,
        slot="head",
    ),
)
TROUBLE_BREWING_REWARDS_BY_ID = {
    reward.reward_id: reward for reward in TROUBLE_BREWING_REWARDS
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
    reward = TROUBLE_BREWING_REWARDS[0]
    return {
        reward.display_name: {
            "category": "equipment",
            "source_item_id": reward.source_item_id,
            "stackable": False,
            "tradeable": False,
            "source": TROUBLE_BREWING_SOURCE,
        }
    }


def trouble_brewing_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    reward = TROUBLE_BREWING_REWARDS[0]
    return {
        reward.display_name: EquipmentItem(
            item_name=reward.display_name,
            slot="head",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="trouble_brewing_reward",
            bonuses=EquipmentBonuses(),
            attack_speed=4,
            source_item_id=reward.source_item_id,
            source=(
                "2011Scape rev-667 items.yml item 8959; "
                + TROUBLE_BREWING_SOURCE
            ),
            source_status="period item identity and zero-bonus equipment block",
            skill_requirements=(),
            weapon_type=-1,
        )
    }
