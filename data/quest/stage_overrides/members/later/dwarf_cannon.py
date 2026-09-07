from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

DWARF_CANNON_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Captain Lawgof needs the Black Guard camp railings repaired."),
    _simple_stage(2, "Captain Lawgof gave me six railings. The broken stockade needs repair."),
    _simple_stage(3, "The six broken railings have been repaired. I should report back to Captain Lawgof."),
    _simple_stage(4, "Captain Lawgof asked me to find Gilob's remains near the watchtower."),
    _simple_stage(5, "I found Gilob's remains and should return them to Captain Lawgof."),
    _simple_stage(6, "Captain Lawgof found a child hidden in the goblin cave south-east of the camp."),
    _simple_stage(7, "I found Lollk in the goblin hideout and need to get him to safety."),
    _simple_stage(8, "Lollk is safe. Captain Lawgof has a toolkit for repairing the sabotaged cannon."),
    _simple_stage(9, "The cannon still needs to be repaired with Captain Lawgof's toolkit."),
    _simple_stage(10, "The cannon is repaired. Captain Lawgof wants help from Nulodion."),
    _simple_stage(11, "Nulodion gave me an ammo mould and notes to take back to Captain Lawgof."),
    _simple_stage(12, "Captain Lawgof needs Nulodion's ammo mould and notes."),
    _simple_stage(13, "Captain Lawgof accepted Nulodion's parts. I should receive his cannon recommendation."),
    _simple_stage(14, "Captain Lawgof gave his recommendation.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    DWARF_CANNON_ID: (
        _stage_req(
            1,
            "Accept replacement railings from Captain Lawgof.",
            f"{DARKAN_DWARF_CANNON_LAWGOF_SOURCE}; {DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Accept replacement railings from Captain Lawgof",),
            produced_inventory=(("Railing", 6),),
        ),
        _stage_req(
            2,
            "Repair the six broken railings around the Black Guard camp.",
            f"{DARKAN_DWARF_CANNON_SOURCE}; {DARKAN_DWARF_CANNON_LAWGOF_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Railing", 6),),
            required_tools=(("Hammer", 1),),
        ),
        _stage_req(
            3,
            "Report the repaired stockade to Captain Lawgof.",
            DARKAN_DWARF_CANNON_LAWGOF_SOURCE,
            auto_actions=("Report the repaired stockade to Captain Lawgof",),
        ),
        _stage_req(
            4,
            "Find Gilob's remains at the watchtower.",
            f"{DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Take Gilob's remains from the watchtower",),
            produced_inventory=(("Dwarf remains", 1),),
        ),
        _stage_req(
            5,
            "Return Gilob's remains to Captain Lawgof.",
            f"{DARKAN_DWARF_CANNON_SOURCE}; {DARKAN_DWARF_CANNON_LAWGOF_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Dwarf remains", 1),),
        ),
        _stage_req(
            6,
            "Find the goblin hideout south-east of the camp.",
            DARKAN_DWARF_CANNON_SOURCE,
            auto_actions=("Reach the Dwarf Cannon goblin hideout",),
        ),
        _stage_req(
            7,
            "Rescue Lollk from the goblin hideout.",
            f"{DARKAN_DWARF_CANNON_SOURCE}; {DARKAN_DWARF_CANNON_LOLLK_SOURCE}",
            auto_actions=("Rescue Lollk from the goblin hideout",),
        ),
        _stage_req(
            8,
            "Return to Captain Lawgof after rescuing Lollk.",
            DARKAN_DWARF_CANNON_LAWGOF_SOURCE,
            auto_actions=("Tell Captain Lawgof that Lollk is safe",),
            produced_inventory=(("Toolkit", 1),),
        ),
        _stage_req(
            9,
            "Repair the sabotaged cannon with Captain Lawgof's toolkit.",
            f"{DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Toolkit", 1),),
            auto_actions=("Repair the sabotaged cannon",),
        ),
        _stage_req(
            10,
            "Tell Captain Lawgof that the cannon is repaired.",
            DARKAN_DWARF_CANNON_LAWGOF_SOURCE,
            auto_actions=("Tell Captain Lawgof that the cannon is repaired",),
        ),
        _stage_req(
            11,
            "Speak to Nulodion for the ammo mould and notes.",
            f"{DARKAN_DWARF_CANNON_NULODION_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Speak to Nulodion about Captain Lawgof's cannon",),
            produced_inventory=(("Ammo mould", 1), ("Nulodion's notes", 1)),
        ),
        _stage_req(
            12,
            "Bring Captain Lawgof the ammo mould and notes.",
            f"{DARKAN_DWARF_CANNON_NULODION_SOURCE}; {DARKAN_DWARF_CANNON_LAWGOF_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Ammo mould", 1), ("Nulodion's notes", 1)),
        ),
        _stage_req(
            13,
            "Receive Captain Lawgof's recommendation to buy and use a multicannon.",
            DARKAN_DWARF_CANNON_LAWGOF_SOURCE,
            auto_actions=("Receive Captain Lawgof's cannon recommendation",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Railing": {
            "category": "material",
            "source": f"{DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Dwarf remains": {
            "category": "material",
            "source": f"{DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Toolkit": {
            "category": "tool",
            "source": f"{DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Nulodion's notes": {
            "category": "material",
            "source": f"{DARKAN_DWARF_CANNON_NULODION_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Ammo mould": {
            "category": "tool",
            "source": f"{DARKAN_DWARF_CANNON_NULODION_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'DWARF_CANNON_STAGES',
)
