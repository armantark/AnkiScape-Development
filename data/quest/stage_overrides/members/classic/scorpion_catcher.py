from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

SCORPION_CATCHER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Thormac needs his three lesser Kharid scorpions recovered."),
    _simple_stage(2, "Thormac gave me a scorpion cage. The Seer can locate the missing scorpions."),
    _simple_stage(3, "The first scorpion is in Taverley Dungeon."),
    _simple_stage(4, "The second scorpion is at the Barbarian Outpost."),
    _simple_stage(5, "The third scorpion is upstairs in Edgeville Monastery."),
    _simple_stage(6, "All three scorpions are caged. I should return to Thormac."),
    _simple_stage(7, "Thormac has his scorpions back.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    SCORPION_CATCHER_ID: (
        _stage_req(
            1,
            "Accept Thormac's scorpion cage.",
            f"{DARKAN_SCORPION_CATCHER_THORMAC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Accept Thormac's scorpion cage",),
            produced_inventory=(("Scorpion cage", 1),),
        ),
        _stage_req(
            2,
            "Ask the Seer for all three scorpion locations.",
            f"{DARKAN_SCORPION_CATCHER_SEER_SOURCE}; {DARKAN_SCORPION_CATCHER_KHAZ_SCORP_SOURCE}",
            auto_actions=("Ask the Seer for all three scorpion locations",),
        ),
        _stage_req(
            3,
            "Catch the Taverley Dungeon scorpion.",
            (
                f"{DARKAN_SCORPION_CATCHER_SOURCE}; {DARKAN_SCORPION_CATCHER_KHAZ_SCORP_SOURCE}; "
                f"{DARKAN_SCORPION_CATCHER_JAILER_NPC_SOURCE}"
            ),
            required_tools=(("Scorpion cage", 1),),
            auto_actions=(
                "Reach the Taverley Dungeon scorpion room",
                "Catch the Taverley Dungeon Kharid scorpion",
            ),
            combat_encounters=(
                _combat(
                    SCORPION_CATCHER_ID,
                    "jailer",
                    "Jailer",
                    39,
                    f"{DARKAN_SCORPION_CATCHER_SOURCE}; {DARKAN_SCORPION_CATCHER_JAILER_NPC_SOURCE}",
                    "The Scorpion Catcher quest details require a level 39 jailer for the Taverley Dungeon key route.",
                    npc_stats=(
                        ("hitpoints", 470),
                        ("attack", 40),
                        ("strength", 40),
                        ("defence", 40),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 50),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_SCORPION_CATCHER_JAILER_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            4,
            "Catch the Barbarian Outpost scorpion.",
            f"{DARKAN_SCORPION_CATCHER_SOURCE}; {DARKAN_SCORPION_CATCHER_KHAZ_SCORP_SOURCE}",
            required_tools=(("Scorpion cage", 1),),
            required_actions=("Return the signed Barcrawl card to a Barbarian guard",),
            auto_actions=(
                "Reach the Barbarian Outpost scorpion room",
                "Catch the Barbarian Outpost Kharid scorpion",
            ),
        ),
        _stage_req(
            5,
            "Catch the Edgeville Monastery scorpion.",
            f"{DARKAN_SCORPION_CATCHER_SOURCE}; {DARKAN_SCORPION_CATCHER_KHAZ_SCORP_SOURCE}",
            required_tools=(("Scorpion cage", 1),),
            auto_actions=(
                "Reach the Edgeville Monastery scorpion room",
                "Catch the Edgeville Monastery Kharid scorpion",
            ),
        ),
        _stage_req(
            6,
            "Return the caged scorpions to Thormac.",
            f"{DARKAN_SCORPION_CATCHER_THORMAC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Scorpion cage", 1),),
            auto_actions=("Return the caged scorpions to Thormac",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Scorpion cage": {
            "category": "tool",
            "source": f"{DARKAN_SCORPION_CATCHER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'SCORPION_CATCHER_STAGES',
)
