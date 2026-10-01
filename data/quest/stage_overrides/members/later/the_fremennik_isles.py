from __future__ import annotations

from ....contract import *
from ....dependencies import *
from ....ids import *
from ....sources import *

_DARKAN_FREMENNIK_ISLES_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "src/main/java/com/rs/game/content/quests/fremennikisles/FremennikIsles.kt"
    " @ a7e91cb9769642e3e833a523fd5f0688eef21924"
)
_STAGE_ACTION_SOURCE = f"{THE_FREMENNIK_ISLES_SOURCE}; {_DARKAN_FREMENNIK_ISLES_SOURCE}"

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    THE_FREMENNIK_ISLES_ID: (
        _stage_req(
            1,
            "Feed HRH Hrafn and deliver King Sorvott's assigned ore shipment.",
            _STAGE_ACTION_SOURCE,
            consumed_inventory=(("Raw tuna", 1),),
            consumed_inventory_options=(
                (("Tin ore", 8), ("Coal", 7), ("Mithril ore", 6)),
            ),
            auto_actions=(
                "Feed HRH Hrafn and deliver King Sorvott's assigned ore shipment",
            ),
        ),
        _stage_req(
            2,
            "Perform for Mawnis in the jester costume and report the first spying answers to Slug.",
            _STAGE_ACTION_SOURCE,
            auto_actions=(
                "Perform for Mawnis and report the first spying answers to Slug",
            ),
        ),
        _stage_req(
            3,
            "Show Mawnis the supplies, repair both northern bridges, and collect Sorvott's window tax.",
            _STAGE_ACTION_SOURCE,
            consumed_inventory=(
                ("Rope", 8),
                ("Split Arctic pine logs", 8),
            ),
            required_tools=(("Knife", 1),),
            auto_actions=(
                "Repair the Neitiznot bridges and collect Sorvott's window tax",
            ),
        ),
        _stage_req(
            4,
            "Collect Sorvott's facial-hair tax and complete the second spying report.",
            _STAGE_ACTION_SOURCE,
            auto_actions=(
                "Collect Sorvott's facial-hair tax and report the second spying answers",
            ),
        ),
        _stage_req(
            5,
            "Complete the traditional rites and defeat the Ice Troll King.",
            THE_FREMENNIK_ISLES_SOURCE,
            required_actions=(
                "Cure and stitch yak-hide armour",
                "Make a Fremennik round shield",
            ),
            combat_encounters=(
                QuestCombatEncounter(
                    encounter_id="the_fremennik_isles_ice_troll_82",
                    display_name="Ice troll",
                    level=82,
                    quantity=10,
                    source=THE_FREMENNIK_ISLES_SOURCE,
                    source_text="10 Ice trolls (level 82)",
                ),
                QuestCombatEncounter(
                    encounter_id="the_fremennik_isles_ice_troll_king_122",
                    display_name="Ice Troll King",
                    level=122,
                    source=THE_FREMENNIK_ISLES_SOURCE,
                    source_text="Ice Troll King (level 122)",
                    npc_stats=(
                        ("hitpoints", 1500),
                        ("attack", 100),
                        ("strength", 100),
                        ("defence", 80),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 200),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=(
                        "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
                        "darkan-world-server/data/npcs/combatdefs/uncategorized/"
                        "ice_troll_king (noanims).json"
                    ),
                ),
            ),
        ),
        _stage_req(
            6,
            "Take the Ice Troll King's head and return it to Mawnis Burowgar.",
            THE_FREMENNIK_ISLES_SOURCE,
            auto_actions=(
                "Return the Ice Troll King's head to Mawnis Burowgar",
            ),
        ),
    ),
}

__all__ = ()
