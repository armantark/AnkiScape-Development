"""Larrissa's commission and the journey before Gunnjorn's key interaction."""

from ....contract import QuestStage, QuestStageRequirementCleanup
from ......generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG


HORROR_FROM_THE_DEEP_OPENING_ACTIONS = (
    "Accept Larrissa's request to find her missing boyfriend Jossik in the dark, locked lighthouse; she asks you to seek Gunnjorn's spare key and repair the eastern bridge.",
    "Travel south across the basalt platforms to the Barbarian Outpost.",
)

HORROR_FROM_THE_DEEP_OPENING_CLEANUP = QuestStageRequirementCleanup(
    stage=1,
    remove_required_tools=("Hammer",),
    remove_required_actions=("Complete Horror from the Deep stage 1 objective",),
    add_auto_actions=HORROR_FROM_THE_DEEP_OPENING_ACTIONS,
    source="https://runescape.wiki/w/index.php?title=Horror_from_the_Deep&oldid=6447471; https://runescape.wiki/w/index.php?title=Horror_from_the_Deep/Quick_guide&oldid=6343123",
)

HORROR_FROM_THE_DEEP_JOURNAL_STAGES = (
    QuestStage(1, HORROR_FROM_THE_DEEP_OPENING_ACTIONS),
    *(
        QuestStage(stage["stage"], stage["journal"])
        for quest in PRE_EOC_QUEST_CATALOG if quest["id"] == "horror_from_the_deep"
        for stage in quest["journal_stages"] if stage["stage"] >= 2
    ),
)
