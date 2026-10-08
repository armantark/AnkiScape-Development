from __future__ import annotations

from ....contract import QuestStageRequirementCleanup


OBSERVATORY_QUEST_CLEANUPS = (
    QuestStageRequirementCleanup(
        stage=1,
        remove_required_actions=("Complete Observatory Quest stage 1 objective",),
        add_auto_actions=(
            "Talk to the Observatory professor in the house near the Observatory which is located North of Castle Wars.",
            "Talk to his assistant.",
        ),
    ),
)
