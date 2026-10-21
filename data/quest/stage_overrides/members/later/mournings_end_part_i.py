"""Ordinary dialogue repair and the preceding Mourner acquisition fight."""

from ....contract import QuestStageRequirementCleanup
from ....oronwen_repair_data import DAMAGED_TROUSERS, REPAIR_STAGE_SOURCE

MOURNINGS_END_PART_I_CLEANUPS = (
    QuestStageRequirementCleanup(
        stage=1,
        remove_required_inventory=(
            "Lletya",
            "Elf teleport crystal",
            "Bow",
            "Rope",
            "Plank",
            "Barrel of coal-tar",
            "Barrel",
        ),
        remove_required_actions=("Complete Mourning's End Part I stage 1 objective",),
        add_auto_actions=("Reach Lletya",),
    ),
    QuestStageRequirementCleanup(
        stage=2,
        remove_required_actions=("Complete Mourning's End Part I stage 2 objective",),
        add_auto_actions=("Take the damaged mourner trousers from the defeated Mourner",),
        source=REPAIR_STAGE_SOURCE,
    ),
    QuestStageRequirementCleanup(
        stage=3,
        remove_required_inventory=("Oronwen", "Dye", "Silk"),
        add_required_inventory=((DAMAGED_TROUSERS, 1), ("Silk", 2)),
        remove_required_actions=("Complete Mourning's End Part I stage 3 objective",),
        source=REPAIR_STAGE_SOURCE,
        add_required_actions=("Have Oronwen repair the mourner trousers",),
    ),
    QuestStageRequirementCleanup(
        stage=4,
        remove_required_inventory=("Arrows",),
    ),
    QuestStageRequirementCleanup(
        stage=5,
        remove_required_inventory=("Rotten apple",),
        add_required_actions=("Use the rotten apple to sabotage the mourner food stores",),
    ),
)
