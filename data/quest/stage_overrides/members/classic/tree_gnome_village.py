from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

TREE_GNOME_VILLAGE_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "King Bolren sent me to Commander Montai on the battlefield."),
    _simple_stage(2, "Commander Montai needs six normal logs to strengthen the gnome battlements."),
    _simple_stage(3, "Commander Montai is ready to explain the next phase of the attack."),
    _simple_stage(4, "I need coordinates from the three tracker gnomes so the ballista can hit the stronghold."),
    _simple_stage(5, "The ballista broke the stronghold wall. I need the first Orb of protection from the chest."),
    _simple_stage(6, "King Bolren took the first orb. A Khazard warlord has the remaining orbs."),
    _simple_stage(7, "I recovered the remaining Orbs of protection and should return them to King Bolren."),
    _simple_stage(8, "King Bolren replaced the orbs and rewarded me.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    TREE_GNOME_VILLAGE_ID: (
        _stage_req(
            1,
            "Reach Commander Montai on the battlefield.",
            f"{TREE_GNOME_BOLREN_SOURCE}; {TREE_GNOME_MONTAI_SOURCE}",
            auto_actions=(
                "Reach Commander Montai on the battlefield",
                "Ask Commander Montai how to help the gnome battlefield",
            ),
        ),
        _stage_req(
            2,
            "Give six normal logs to Commander Montai.",
            f"{TREE_GNOME_MONTAI_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Logs", 6),),
        ),
        _stage_req(
            3,
            "Ask Commander Montai about the tracker gnomes.",
            TREE_GNOME_MONTAI_SOURCE,
            auto_actions=("Ask Commander Montai about the tracker gnomes",),
        ),
        _stage_req(
            4,
            "Get all three tracker coordinates and fire the battlefield ballista.",
            (
                f"{TREE_GNOME_MONTAI_SOURCE}; {TREE_GNOME_TRACKER1_SOURCE}; {TREE_GNOME_TRACKER2_SOURCE}; "
                f"{TREE_GNOME_TRACKER3_SOURCE}; {TREE_GNOME_DARKAN_SOURCE}"
            ),
            auto_actions=(
                "Get the first tracker coordinate",
                "Get the second tracker coordinate",
                "Get the third tracker coordinate",
                "Fire the battlefield ballista at the Khazard stronghold",
            ),
        ),
        _stage_req(
            5,
            "Enter the Khazard stronghold and recover the first Orb of protection.",
            f"{TREE_GNOME_DARKAN_SOURCE}; {TREE_GNOME_MONTAI_SOURCE}; {TREE_GNOME_KHAZARD_COMMANDER_NPC_SOURCE}",
            auto_actions=(
                "Enter the Khazard stronghold through the broken wall",
                "Search the stronghold chest for the first Orb of protection",
            ),
            produced_inventory=(("Orb of protection", 1),),
            combat_encounters=(
                _combat(
                    TREE_GNOME_VILLAGE_ID,
                    "khazard_commander_48",
                    "Khazard commander",
                    48,
                    TREE_GNOME_WIKI_SOURCE,
                    "Two Khazard commanders (level 48) can block the first Orb of protection.",
                    quantity=2,
                    npc_stats=(
                        ("hitpoints", 220),
                        ("attack", 50),
                        ("strength", 45),
                        ("defence", 50),
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
                    npc_stats_source=TREE_GNOME_KHAZARD_COMMANDER_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            6,
            "Return the first Orb of protection to King Bolren and recover the remaining orbs from the Khazard warlord.",
            f"{TREE_GNOME_BOLREN_SOURCE}; {TREE_GNOME_DARKAN_SOURCE}; {TREE_GNOME_KHAZARD_WARLORD_NPC_SOURCE}",
            consumed_inventory=(("Orb of protection", 1),),
            auto_actions=("Return the first Orb of protection to King Bolren",),
            produced_inventory=(("Orbs of protection", 1),),
            combat_encounters=(
                _combat(
                    TREE_GNOME_VILLAGE_ID,
                    "khazard_warlord_112",
                    "Khazard warlord",
                    112,
                    TREE_GNOME_WIKI_SOURCE,
                    "Khazard warlord (level 112) holds the remaining Orbs of protection.",
                    npc_stats=(
                        ("hitpoints", 1690),
                        ("attack", 75),
                        ("strength", 78),
                        ("defence", 80),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 92),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=TREE_GNOME_KHAZARD_WARLORD_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            7,
            "Return the remaining Orbs of protection to King Bolren.",
            f"{TREE_GNOME_BOLREN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Orbs of protection", 1),),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Orb of protection": {
            "category": "material",
            "tradeable": False,
            "source": f"{TREE_GNOME_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Orbs of protection": {
            "category": "material",
            "tradeable": False,
            "source": f"{TREE_GNOME_DARKAN_SOURCE}; {TREE_GNOME_BOLREN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Gnome amulet": {
            "category": "equipment",
            "equipment_slot": "neck",
            "item_id": 589,
            "tradeable": False,
            "source": f"{TREE_GNOME_DARKAN_SOURCE}; {TREE_GNOME_BOLREN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'TREE_GNOME_VILLAGE_STAGES',
)
