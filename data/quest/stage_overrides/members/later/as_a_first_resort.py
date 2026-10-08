from __future__ import annotations

from ....contract import QuestStageRequirementCleanup


_SOURCE = (
    "https://runescape.wiki/w/As_a_First_Resort?oldid=6538997; "
    "https://runescape.wiki/w/As_a_First_Resort%2FQuick_guide?oldid=6541270"
)

AS_A_FIRST_RESORT_STAGE_CLEANUPS = (
    QuestStageRequirementCleanup(
        stage=1,
        remove_required_inventory=("Hatchet", "Teasing stick", "Raw chompy", "Primweed", "Stinkbloom"),
        remove_required_actions=("Complete As a First Resort stage 1 objective",),
        add_auto_actions=(
            "Head to Oo'glog East of Mobilising Armies and talk to Chief Tess.",
            "Talk to Balnea in the Oo'glog bank.",
        ),
        source=_SOURCE,
    ),
    QuestStageRequirementCleanup(
        stage=2,
        remove_required_inventory=("Achey tree logs", "Eucalyptus logs", "Logs"),
        remove_required_actions=("Complete As a First Resort stage 2 objective",),
        add_consumed_inventory=(("Achey tree logs", 8), ("Eucalyptus logs", 10)),
        add_auto_actions=(
            "Talk to Chargurr North of the bank.",
            "Put eight Achey tree logs and ten Eucalyptus logs in the fire pit.",
        ),
        source=_SOURCE,
    ),
    QuestStageRequirementCleanup(stage=3, remove_required_inventory=("Spears",)),
    QuestStageRequirementCleanup(stage=4, remove_required_inventory=("Larupia furs",)),
)

__all__: tuple[str, ...] = ()
