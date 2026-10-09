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
        source=(
            "https://runescape.wiki/w/Observatory_Quest?oldid=6496978; "
            "https://runescape.wiki/w/Observatory_Quest%2FQuick_guide?oldid=5706277"
        ),
    ),
    QuestStageRequirementCleanup(
        stage=2,
        remove_required_actions=("Complete Observatory Quest stage 2 objective",),
        add_auto_actions=(
            "Talk to the assistant then the professor to hand over the three planks, bronze bar and molten glass.",
            "Leave the house and go east to the abandoned buildings.",
            "Climb down the stairs in the western building.",
            'Search the dungeon chests, clicking "Click here to continue", until you find the Goblin kitchen key.',
            "Return to the staircase at the entrance without exiting the dungeon.",
        ),
        source=(
            "https://runescape.wiki/w/Observatory_Quest?oldid=6496978; "
            "https://runescape.wiki/w/Observatory_Quest%2FQuick_guide?oldid=5706277"
        ),
    ),
)
