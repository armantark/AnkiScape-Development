from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

TRIBAL_TOTEM_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Kangai Mau asked me to recover the Rantuki totem from Lord Handelmort."),
    _simple_stage(2, "Wizard Cromperty's teleport block can reach the RPDT depot."),
    _simple_stage(3, "I took the address label for Handelmort Mansion from the RPDT crate."),
    _simple_stage(4, "The teleport block has been redirected to Handelmort Mansion."),
    _simple_stage(5, "I found the Rantuki totem and need to return it to Kangai Mau."),
    _simple_stage(6, "Kangai Mau received the Rantuki totem.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    TRIBAL_TOTEM_ID: (
        _stage_req(
            1,
            "Ask Wizard Cromperty about his teleportation block.",
            f"{DARKAN_TRIBAL_TOTEM_KANGAI_SOURCE}; {DARKAN_TRIBAL_TOTEM_WIZARD_SOURCE}",
            auto_actions=("Ask Wizard Cromperty about the teleportation block",),
        ),
        _stage_req(
            2,
            "Take Lord Handelmort's address label from the RPDT crate.",
            f"{DARKAN_TRIBAL_TOTEM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Reach the Ardougne RPDT depot", "Take Lord Handelmort's address label from the RPDT crate"),
            produced_inventory=(("Address label", 1),),
        ),
        _stage_req(
            3,
            "Switch the RPDT crate address labels and request delivery.",
            f"{DARKAN_TRIBAL_TOTEM_SOURCE}; {DARKAN_TRIBAL_TOTEM_RPDT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Address label", 1),),
            auto_actions=("Switch the RPDT crate address labels and request delivery",),
        ),
        _stage_req(
            4,
            "Teleport into Handelmort Mansion, bypass the traps, and loot the Rantuki totem.",
            f"{DARKAN_TRIBAL_TOTEM_SOURCE}; {DARKAN_TRIBAL_TOTEM_WIZARD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=(
                "Teleport into Handelmort Mansion",
                "Disarm Handelmort's trapped stairs",
                "Solve Handelmort's lock with KURT",
                "Loot the Rantuki totem",
            ),
            produced_inventory=(("Totem", 1),),
        ),
        _stage_req(
            5,
            "Return the Rantuki totem to Kangai Mau.",
            f"{DARKAN_TRIBAL_TOTEM_KANGAI_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Totem", 1),),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Address label": {
            "category": "material",
            "source": f"{DARKAN_TRIBAL_TOTEM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Totem": {
            "category": "material",
            "source": f"{DARKAN_TRIBAL_TOTEM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'TRIBAL_TOTEM_STAGES',
)
