from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    A_SOULS_BANE_ID: (
        _stage_req(
            1,
            "Bring a rope and enter Tolna's rift.",
            f"{A_SOULS_BANE_WIKI_SOURCE}; {A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}",
            required_inventory=(("Rope", 1),),
        ),
        _stage_req(
            2,
            "Fill the rage meter with the correct anger weapon before leaving the rage room.",
            f"{A_SOULS_BANE_WIKI_SOURCE}; {A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}",
            auto_actions=("Fill the rage meter with an anger weapon",),
        ),
        _stage_req(
            3,
            "Clear the fear, confusion, and hopelessness rooms.",
            f"{A_SOULS_BANE_WIKI_SOURCE}; {A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}",
            combat_encounters=(
                _combat(
                    A_SOULS_BANE_ID,
                    "fear_reaper_42",
                    "Fear reaper",
                    42,
                    f"{A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {A_SOULS_BANE_FEAR_REAPER_NPC_SOURCE}",
                    "Darkan quick guide says to kill five fear reapers; Darkan NPC id 3649 supplies the level 42 Fear reaper stats.",
                    quantity=5,
                    npc_stats=(
                        ("hitpoints", 570),
                        ("attack", 39),
                        ("strength", 41),
                        ("defence", 40),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 60),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "slash_att"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=A_SOULS_BANE_FEAR_REAPER_NPC_SOURCE,
                ),
                _combat(
                    A_SOULS_BANE_ID,
                    "confusion_beast_43",
                    "Confusion beast",
                    43,
                    f"{A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {A_SOULS_BANE_CONFUSION_BEAST_NPC_SOURCE}",
                    "Darkan quick guide says the real Confusion beast must be killed five times; Darkan NPC ids 3650-3654 supply level 43 stats.",
                    quantity=5,
                    npc_stats=(
                        ("hitpoints", 640),
                        ("attack", 42),
                        ("strength", 41),
                        ("defence", 40),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 50),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "slash_att"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=A_SOULS_BANE_CONFUSION_BEAST_NPC_SOURCE,
                ),
                _combat(
                    A_SOULS_BANE_ID,
                    "hopeless_creature_40",
                    "Hopeless creature",
                    40,
                    f"{A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {A_SOULS_BANE_HOPELESS_CREATURE_NPC_SOURCE}",
                    "Darkan quick guide says Hopeless creatures have three forms; Darkan NPC ids 3655-3657 supply level 40 form stats.",
                    quantity=3,
                    npc_stats=(
                        ("hitpoints", 1),
                        ("attack", 38),
                        ("strength", 36),
                        ("defence", 39),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 1),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=A_SOULS_BANE_HOPELESS_CREATURE_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            4,
            "Defeat all three Tolna heads before speaking to Tolna on the surface.",
            f"{A_SOULS_BANE_WIKI_SOURCE}; {A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}",
            combat_encounters=(
                _combat(
                    A_SOULS_BANE_ID,
                    "tolna_head_46",
                    "Tolna head",
                    46,
                    f"{A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {A_SOULS_BANE_TOLNA_NPC_SOURCE}",
                    "Darkan quick guide says all three Tolna heads must be killed; Darkan NPC ids 3658-3660 list Tolna level 46 and the Tolna combatdef supplies stats.",
                    quantity=3,
                    npc_stats=(
                        ("hitpoints", 450),
                        ("attack", 42),
                        ("strength", 41),
                        ("defence", 40),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 50),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=A_SOULS_BANE_TOLNA_NPC_SOURCE,
                ),
            ),
        ),
    ),
}

__all__: tuple[str, ...] = ()
