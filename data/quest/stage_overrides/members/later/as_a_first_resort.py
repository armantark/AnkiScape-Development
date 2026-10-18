from __future__ import annotations

from ....contract import QuestStageRequirementCleanup, _stage_req


_SOURCE = (
    "https://runescape.wiki/w/As_a_First_Resort?oldid=6538997; "
    "https://runescape.wiki/w/As_a_First_Resort%2FQuick_guide?oldid=6541270"
)

AS_A_FIRST_RESORT_STAGE_ADDITIONS = (
    _stage_req(
        3,
        "Set up the chompy spits, light Chargurr's fire pit, and meet Snurgh.",
        _SOURCE,
        consumed_inventory=(("Raw chompy", 2),),
        consumed_inventory_options=(
            (
                ("Bronze spear", 4),
                ("Iron spear", 4),
                ("Steel spear", 4),
                ("Black spear", 4),
                ("Mithril spear", 4),
                ("Adamant spear", 4),
                ("Rune spear", 4),
                ("Dragon spear", 4),
            ),
        ),
        required_tools=(("Tinderbox", 1),),
        auto_actions=(
            "Talk to Chargurr.",
            "Give her four Spears.",
            "Use two raw chompies on the spears.",
            "Use a Tinderbox on the fire pit.",
            "Talk to Balnea.",
            "Talk to Snurgh who is in a building in the Southeast corner of Oo'glog.",
        ),
    ),
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
    QuestStageRequirementCleanup(
        stage=3,
        remove_required_inventory=("Spears",),
        remove_required_actions=("Complete As a First Resort stage 3 objective",),
        source=_SOURCE,
    ),
    QuestStageRequirementCleanup(stage=4, remove_required_inventory=("Larupia furs",), source=_SOURCE),
)

__all__: tuple[str, ...] = ()
