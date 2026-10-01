from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

COOKS_ASSISTANT_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "I need to collect a super large egg near Lumbridge for the Duke's cake.",
    ),
    _simple_stage(
        2,
        "I need a bucket so I can milk the prized dairy cow for top-quality milk.",
    ),
    _simple_stage(
        3,
        "I need an empty pot so Millie's mill can produce extra fine flour.",
    ),
    _simple_stage(
        4,
        "I have the special egg, milk, and flour. I should give them to the cook.",
    ),
    _simple_stage(
        5,
        "I brought the cook all three ingredients and he made the birthday cake.",
        "Quest complete!",
    ),
)

QUEST = QuestDefinition(
        id=COOKS_ASSISTANT_ID,
        display_name="Cook's Assistant",
        stage_count=5,
        point_reward=1,
        rewards=(("Coins", 500), ("Sardine", 20)),
        start_point="Speak to the cook in Lumbridge Castle kitchen.",
        requirements=("Used during quest: Bucket x1, Empty pot x1",),
        required_items=(),
        combat="No specific combat.",
        source=(
            f"{COOKS_ASSISTANT_SOURCE_PATH}; {COOKS_ASSISTANT_LUMBRIDGE_COOK_SOURCE}; "
            f"{COOKS_ASSISTANT_PRIZED_DAIRY_COW_SOURCE}; {COOKS_ASSISTANT_MILLIE_MILLER_SOURCE}; "
            f"{COOKS_ASSISTANT_FLOUR_BIN_SOURCE}"
        ),
        journal_stages=COOKS_ASSISTANT_STAGES,
        release_date="2001-01-04",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("cooking", 300),),
        unlocks=("Access to the Cook's range",),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    COOKS_ASSISTANT_ID: (
        _stage_req(
            1,
            "Pick up the super large egg for the Duke's cake.",
            COOKS_ASSISTANT_LUMBRIDGE_COOK_SOURCE,
            produced_inventory=(("Super large egg", 1),),
        ),
        _stage_req(
            2,
            "Milk the prized dairy cow for top-quality milk.",
            COOKS_ASSISTANT_PRIZED_DAIRY_COW_SOURCE,
            required_inventory=(("Bucket", 1),),
            consumed_inventory=(("Bucket", 1),),
            produced_inventory=(("Top-quality milk", 1),),
        ),
        _stage_req(
            3,
            "Ask Millie to prepare extra fine flour and collect it from the flour bin.",
            f"{COOKS_ASSISTANT_MILLIE_MILLER_SOURCE}; {COOKS_ASSISTANT_FLOUR_BIN_SOURCE}",
            required_inventory=(("Empty pot", 1),),
            consumed_inventory=(("Empty pot", 1),),
            produced_inventory=(("Extra fine flour", 1),),
        ),
        _stage_req(
            4,
            "Give the Lumbridge cook the three special cake ingredients.",
            f"{COOKS_ASSISTANT_SOURCE_PATH}; {COOKS_ASSISTANT_LUMBRIDGE_COOK_SOURCE}",
            consumed_inventory=(("Top-quality milk", 1), ("Extra fine flour", 1), ("Super large egg", 1)),
        ),
    ),
}

__all__ = (
    'COOKS_ASSISTANT_STAGES',
)
