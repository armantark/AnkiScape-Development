from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    FAIRY_TALE_I_ID: (
        _stage_req(
            1,
            "Ask the Fairy Godfather why crops across Gielinor are failing.",
            FAIRY_TALE_I_STAGE_ACTION_SOURCE,
            required_inventory_options=((("Dramen staff", 1), ("Lunar staff", 1)),),
            auto_actions=(
                "Martin thinks fairies may be responsible. I should ask the Fairy Godfather in Zanaris.",
            ),
        ),
        _stage_req(
            2,
            "Take Fairy Nuff's symptoms to Zandar Horfyre, then find Malignius Mortifer.",
            FAIRY_TALE_I_STAGE_ACTION_SOURCE,
            auto_actions=(
                "Zandar Horfyre sent me to Malignius Mortifer near Port Sarim.",
            ),
        ),
        _stage_req(
            3,
            "Have the Nature Spirit enchant ordinary secateurs with the assigned ingredients.",
            FAIRY_TALE_I_STAGE_ACTION_SOURCE,
            required_inventory_options=((("Ghostspeak amulet", 1), ("Cramulet", 1)),),
            consumed_inventory=(("Secateurs", 1),),
            produced_inventory=(("Magic secateurs", 1),),
            required_tools=(("Spade", 1),),
            auto_actions=(
                "Malignius will tell you to go ask the Nature Spirit to perform the spell 'Phasma Phasmatis Natura' on an ordinary secateurs, along with three or four specific items.",
            ),
        ),
        _stage_req(
            4,
            "Enter the shady grove and defeat the Tanglefoot with Magic secateurs.",
            FAIRY_TALE_I_STAGE_ACTION_SOURCE,
            required_tools=(("Magic secateurs", 1),),
            auto_actions=(
                "Nature Spirit enchanted my secateurs. I must enter the shady grove and defeat the Tanglefoot.",
            ),
            combat_encounters=(
                _combat(
                    FAIRY_TALE_I_ID,
                    "tanglefoot_111",
                    "Tanglefoot",
                    111,
                    f"{FAIRY_TALE_I_WIKI_SOURCE}; {FAIRY_TALE_I_DARKAN_SOURCE}; {FAIRY_TALE_I_TANGLEFOOT_NPC_SOURCE}",
                    "Tanglefoot (level 111)",
                    npc_stats=(
                        ("hitpoints", 1020),
                        ("attack", 97),
                        ("strength", 97),
                        ("defence", 91),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 110),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "passive"),
                    ),
                    guaranteed_drops=(("Queen's secateurs", 1),),
                    npc_stats_source=FAIRY_TALE_I_TANGLEFOOT_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            5,
            "Return the Queen's secateurs to the Fairy Godfather.",
            FAIRY_TALE_I_STAGE_ACTION_SOURCE,
            consumed_inventory=(("Queen's secateurs", 1),),
            auto_actions=(
                "I have the Queen's secateurs. I should return them to the Fairy Godfather.",
            ),
        ),
    ),
}

__all__: tuple[str, ...] = ()
