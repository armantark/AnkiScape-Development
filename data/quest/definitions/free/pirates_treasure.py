from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

PIRATES_TREASURE_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Redbeard Frank wants Karamjan rum in exchange for the treasure location."),
    _simple_stage(2, "Redbeard Frank gave me One-Eyed Hector's chest key for the Blue Moon Inn."),
    _simple_stage(3, "The Blue Moon Inn chest contained a pirate message pointing to Falador Park."),
    _simple_stage(4, "I dug up One-Eyed Hector's treasure in Falador Park.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=PIRATES_TREASURE_ID,
        display_name="Pirate's Treasure",
        stages=4,
        point_reward=2,
        rewards=(("Casket (Pirate's Treasure)", 1),),
        start_point="Talk to Redbeard Frank just south of The Rusty Anchor pub in Port Sarim.",
        requirements=("Used during quest: Karamjan rum x1, Spade x1",),
        required_items=(),
        combat="Optional level 4 gardener near the digging spot.",
        source=f"{PIRATES_TREASURE_SOURCE_PATH}; {PIRATES_TREASURE_REDBEARD_SOURCE_PATH}; {PIRATES_TREASURE_CHEST_SOURCE_PATH}",
        journal_stages=PIRATES_TREASURE_STAGES,
        release_date="2001-06-11",
        members=False,
        difficulty="Novice",
        length="Short to Medium",
        timeline="Fifth Age",
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    PIRATES_TREASURE_ID: (
        _stage_req(
            1,
            "Give Redbeard Frank smuggled Karamjan rum.",
            f"{PIRATES_TREASURE_SOURCE_PATH}; {PIRATES_TREASURE_REDBEARD_SOURCE_PATH}",
            consumed_inventory=(("Karamjan rum", 1),),
            produced_inventory=(("Chest key", 1),),
            auto_actions=("Smuggle Karamjan rum off Karamja",),
        ),
        _stage_req(
            2,
            "Open One-Eyed Hector's chest in the Blue Moon Inn.",
            f"{PIRATES_TREASURE_SOURCE_PATH}; {PIRATES_TREASURE_CHEST_SOURCE_PATH}",
            consumed_inventory=(("Chest key", 1),),
            produced_inventory=(("Pirate message", 1),),
            auto_actions=("Open One-Eyed Hector's chest at the Blue Moon Inn",),
        ),
        _stage_req(
            3,
            "Read the pirate message and dig in Falador Park.",
            f"{PIRATES_TREASURE_SOURCE_PATH}; {PIRATES_TREASURE_CHEST_SOURCE_PATH}",
            required_inventory=(("Pirate message", 1),),
            required_tools=(("Spade", 1),),
            auto_actions=("Read the pirate message and dig in Falador Park",),
        ),
    ),
}

__all__ = (
    'PIRATES_TREASURE_STAGES',
)
