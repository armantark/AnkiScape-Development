from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

IMP_CATCHER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Wizard Mizgog needs his black, red, white, and yellow beads returned.",
    ),
    _simple_stage(
        2,
        "I returned Wizard Mizgog's beads and received an Amulet of accuracy.",
        "Quest complete!",
    ),
)

QUEST = QuestDefinition(
        id=IMP_CATCHER_ID,
        display_name="Imp Catcher",
        stages=2,
        point_reward=1,
        rewards=(("Amulet of accuracy", 1),),
        start_point="Talk to Wizard Mizgog in the Wizards' Tower.",
        requirements=("Used during quest: Black bead x1, Red bead x1, White bead x1, Yellow bead x1",),
        required_items=(),
        combat="Imps can drop the beads, but the quest completion gate is the four beads.",
        source=f"{IMP_CATCHER_SOURCE_PATH}; {IMP_CATCHER_MIZGOG_SOURCE_PATH}",
        journal_stages=IMP_CATCHER_STAGES,
        release_date="2001-02-16",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("magic", 875),),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    IMP_CATCHER_ID: (
        _stage_req(
            1,
            "Return Wizard Mizgog's four beads.",
            f"{IMP_CATCHER_SOURCE_PATH}; {IMP_CATCHER_MIZGOG_SOURCE_PATH}",
            consumed_inventory=(("Black bead", 1), ("Red bead", 1), ("White bead", 1), ("Yellow bead", 1)),
        ),
    ),
}

__all__ = (
    'IMP_CATCHER_STAGES',
)
