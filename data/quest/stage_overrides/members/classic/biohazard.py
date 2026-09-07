from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

BIOHAZARD_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Elena needs her distillator back from West Ardougne.",
        "Jerico may know another way over the city wall.",
    ),
    _simple_stage(
        2,
        "Jerico arranged help with a rope ladder.",
        "Omart is waiting by the south end of the West Ardougne wall.",
    ),
    _simple_stage(
        3,
        "Omart needs the watchtower mourners distracted.",
        "Jerico may have an idea involving his messenger pigeons.",
    ),
    _simple_stage(
        4,
        "Jerico suggested using his pigeons.",
        "I need bird feed and a pigeon cage to distract the mourners.",
    ),
    _simple_stage(
        5,
        "The mourners are distracted by Jerico's pigeons.",
        "Omart and Kilron should help me cross the wall.",
    ),
    _simple_stage(
        6,
        "I crossed into West Ardougne.",
        "Elena's distillator is in the Mourner HQ, but the mourners are still inside.",
    ),
    _simple_stage(
        7,
        "I found a rotten apple in the Mourner HQ garden.",
        "The apple can spoil the mourners' stew.",
    ),
    _simple_stage(
        8,
        "A rotten apple poisoned the Mourner HQ stew.",
        "A doctors' gown should let me enter and recover the distillator.",
    ),
    _simple_stage(
        9,
        "I recovered Elena's distillator from the Mourner HQ.",
        "Elena needs it back so she can prepare the plague sample reagents.",
    ),
    _simple_stage(
        10,
        "Elena gave me three vials and a plague sample for Guidor.",
        "The Rimmington chemist should provide more touch paper.",
    ),
    _simple_stage(
        11,
        "The chemist gave me touch paper and warned me about Varrock checks.",
        "His errand boys can smuggle the vials to the Dancing Donkey Inn.",
    ),
    _simple_stage(
        12,
        "Guidor found that the plague sample is harmless.",
        "Elena should hear that the plague may be a hoax.",
    ),
    _simple_stage(
        13,
        "Elena told me to take the news straight to King Lathas.",
        "King Lathas should explain what happens next.",
    ),
    _simple_stage(14, "King Lathas rewarded me for exposing the hoax.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    BIOHAZARD_ID: (
        _stage_req(
            1,
            "Ask Jerico for a route back into West Ardougne.",
            f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_JERICO_SOURCE}",
            auto_actions=("Ask Jerico about crossing the West Ardougne wall",),
        ),
        _stage_req(
            2,
            "Meet Omart at the south end of the West Ardougne wall.",
            f"{DARKAN_BIOHAZARD_JERICO_SOURCE}; {DARKAN_BIOHAZARD_OMART_SOURCE}",
            auto_actions=("Ask Omart about the rope ladder",),
        ),
        _stage_req(
            3,
            "Ask Jerico about distracting the watchtower mourners.",
            (
                f"{DARKAN_BIOHAZARD_JERICO_SOURCE}; {DARKAN_BIOHAZARD_UTILS_SOURCE}; "
                f"{DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            produced_inventory=(("Bird feed", 1), ("Pigeon cage", 1)),
            auto_actions=(
                "Ask Jerico about using messenger pigeons",
                "Search Jerico's cupboard for bird feed",
                "Take a pigeon cage from Jerico's house",
            ),
        ),
        _stage_req(
            4,
            "Use bird feed and Jerico's pigeons to distract the watchtower mourners.",
            (
                f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(("Bird feed", 1),),
            required_tools=(("Pigeon cage", 1),),
            auto_actions=(
                "Reach Jerico's pigeon release tile",
                "Scatter bird feed on the watchtower fence",
                "Open the pigeon cage at Jerico's release tile",
            ),
        ),
        _stage_req(
            5,
            "Cross the West Ardougne wall with Omart and Kilron's rope ladder.",
            f"{DARKAN_BIOHAZARD_OMART_SOURCE}; {DARKAN_BIOHAZARD_KILRON_SOURCE}; {DARKAN_BIOHAZARD_UTILS_SOURCE}",
            auto_actions=(
                "Reach Omart by the south West Ardougne wall",
                "Cross the West Ardougne wall with Omart and Kilron",
            ),
        ),
        _stage_req(
            6,
            "Pick up a rotten apple from the Mourner HQ garden.",
            (
                f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            auto_actions=(
                "Reach the Mourner HQ garden in West Ardougne",
                "Pick up a rotten apple from the Mourner HQ garden",
            ),
            produced_inventory=(("Rotten apple", 1),),
        ),
        _stage_req(
            7,
            "Poison the Mourner HQ stew and take a doctors' gown from the nearby box.",
            (
                f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_MOURNER_HQ_DOORS_SOURCE}; "
                f"{DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(("Rotten apple", 1),),
            produced_inventory=(("Doctors' gown", 1),),
            auto_actions=(
                "Reach the Mourner HQ garden in West Ardougne",
                "Put the rotten apple in the Mourner HQ cauldron",
                "Search the box for a doctors' gown",
            ),
        ),
        _stage_req(
            8,
            "Enter Mourner HQ as a doctor, defeat the key mourner, and recover Elena's distillator.",
            (
                f"{DARKAN_BIOHAZARD_MOURNER_HQ_DOORS_SOURCE}; {DARKAN_BIOHAZARD_MOURNER_SOURCE}; "
                f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; "
                f"{DARKAN_BIOHAZARD_MOURNER_NPC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            produced_inventory=(("Key", 1), ("Distillator", 1)),
            required_tools=(("Doctors' gown", 1),),
            auto_actions=(
                "Enter Mourner HQ wearing the doctors' gown",
                "Defeat and search the level 13 mourner",
                "Unlock the distillator cage with the key",
                "Search the crate for Elena's distillator",
            ),
            combat_encounters=(
                _combat(
                    BIOHAZARD_ID,
                    "mourner_13",
                    "Mourner",
                    13,
                    f"{DARKAN_BIOHAZARD_SOURCE}; {DARKAN_BIOHAZARD_MOURNER_SOURCE}; {DARKAN_BIOHAZARD_MOURNER_NPC_SOURCE}",
                    "The Biohazard quest details require a level 13 mourner in Mourner HQ.",
                    npc_stats=(
                        ("hitpoints", 190),
                        ("attack", 24),
                        ("strength", 24),
                        ("defence", 24),
                        ("magic", 1),
                        ("ranged", 0),
                    ),
                    npc_configs=(
                        ("max_hit", 20),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=DARKAN_BIOHAZARD_MOURNER_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            9,
            "Return Elena's distillator so she can prepare Guidor's vials and plague sample.",
            (
                f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_UTILS_SOURCE}; "
                f"{DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(("Distillator", 1),),
            produced_inventory=(
                ("Liquid honey", 1),
                ("Ethenea", 1),
                ("Sulphuric broline", 1),
                ("Plague sample", 1),
            ),
            auto_actions=("Return Elena's distillator",),
        ),
        _stage_req(
            10,
            "Ask the Rimmington chemist for touch paper without exposing the plague sample.",
            (
                f"{DARKAN_BIOHAZARD_CHEMIST_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            required_inventory=(
                ("Liquid honey", 1),
                ("Ethenea", 1),
                ("Sulphuric broline", 1),
                ("Plague sample", 1),
            ),
            produced_inventory=(("Touch paper", 1),),
            auto_actions=("Ask the Rimmington chemist for touch paper for Guidor",),
        ),
        _stage_req(
            11,
            "Smuggle the vials through the chemist's errand boys and give Guidor the full test set.",
            (
                f"{DARKAN_BIOHAZARD_RIMMINGTON_HOPS_SOURCE}; {DARKAN_BIOHAZARD_RIMMINGTON_DA_VINCI_SOURCE}; "
                f"{DARKAN_BIOHAZARD_RIMMINGTON_CHANCY_SOURCE}; {DARKAN_BIOHAZARD_VARROCK_HOPS_SOURCE}; "
                f"{DARKAN_BIOHAZARD_VARROCK_DA_VINCI_SOURCE}; {DARKAN_BIOHAZARD_VARROCK_CHANCY_SOURCE}; "
                f"{DARKAN_BIOHAZARD_GUIDOR_SOURCE}; {DARKAN_BIOHAZARD_GUIDOR_WIFE_SOURCE}; "
                f"{DARKAN_BIOHAZARD_GUIDOR_DOOR_SOURCE}; {DARKAN_BIOHAZARD_VARROCK_GATE_SOURCE}; "
                f"{DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(
                ("Liquid honey", 1),
                ("Ethenea", 1),
                ("Sulphuric broline", 1),
                ("Plague sample", 1),
                ("Touch paper", 1),
            ),
            required_tools=(("Priest gown", 2),),
            auto_actions=(
                "Reach Guidor's house without Varrock guards confiscating the vials",
                "Give sulphuric broline to Hops",
                "Give ethenea to Da Vinci",
                "Give liquid honey to Chancy",
                "Collect the sulphuric broline from Hops in Varrock",
                "Collect the ethenea from Da Vinci in Varrock",
                "Collect the liquid honey from Chancy in Varrock",
                "Enter Guidor's room wearing priest gowns",
                "Give Guidor the vials, plague sample, and touch paper",
            ),
        ),
        _stage_req(
            12,
            "Tell Elena that Guidor found the plague sample harmless.",
            f"{DARKAN_BIOHAZARD_GUIDOR_SOURCE}; {DARKAN_BIOHAZARD_ELENA_SOURCE}",
            auto_actions=("Tell Elena that Guidor found no plague",),
        ),
        _stage_req(
            13,
            "Report Elena's news to King Lathas.",
            f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_KING_SOURCE}",
            auto_actions=("Report the plague hoax to King Lathas",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Bird feed": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pigeon cage": {
            "category": "tool",
            "source": f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Rotten apple": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Doctors' gown": {
            "category": "equipment",
            "source": f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Key": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_MOURNER_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Distillator": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Liquid honey": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Ethenea": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Sulphuric broline": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Plague sample": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Touch paper": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_CHEMIST_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Priest gown": {
            "category": "equipment",
            "source": f"{DARKAN_BIOHAZARD_GUIDOR_WIFE_SOURCE}; {DARKAN_BIOHAZARD_GUIDOR_DOOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'BIOHAZARD_STAGES',
)
