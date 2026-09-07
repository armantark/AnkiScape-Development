from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    HAZEEL_CULT_ID: (
        _stage_req(
            1,
            "Choose whether to expose the cult or help revive Hazeel.",
            "https://runescape.wiki/w/Hazeel_Cult?oldid=6579784",
            required_actions=("Complete Hazeel Cult stage 1 objective",),
        ),
        _stage_req(
            2,
            (
                "Defeat Alomone twice, keep both armour drops until one can be given to Ceril, "
                "and retain the other as the route reward."
            ),
            "https://runescape.wiki/w/Hazeel_Cult?oldid=6579784",
            variant=HAZEEL_CULT_VARIANT_CARNILLEAN,
            required_routes=(HAZEEL_CULT_ROUTE_CARNILLEAN,),
            produced_inventory=(("Carnillean armour", 2),),
            required_actions=("Complete Hazeel Cult stage 2 objective",),
            combat_encounters=(
                _combat(
                    HAZEEL_CULT_ID,
                    "alomone_13",
                    "Alomone",
                    13,
                    "https://runescape.wiki/w/Hazeel_Cult?oldid=6579784",
                    "Alomone (13) (Carnillean side)",
                    quantity=2,
                    npc_stats=(
                        ("hitpoints", 250),
                        ("attack", 10),
                        ("strength", 10),
                        ("defence", 4),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 1),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=DARKAN_HAZEEL_CULT_ALOMONE_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            2,
            "Help the cult prepare Hazeel's revival.",
            "https://runescape.wiki/w/Hazeel_Cult?oldid=6579784",
            variant=HAZEEL_CULT_VARIANT_HAZEEL,
            required_routes=(HAZEEL_CULT_ROUTE_HAZEEL,),
            required_actions=("Complete Hazeel Cult stage 2 objective",),
        ),
        _stage_req(
            3,
            "Give one Carnillean armour to Ceril, expose Butler Jones, and finish the quest.",
            "https://runescape.wiki/w/Hazeel_Cult?oldid=6579784",
            variant=HAZEEL_CULT_VARIANT_CARNILLEAN,
            required_routes=(HAZEEL_CULT_ROUTE_CARNILLEAN,),
            consumed_inventory=(("Carnillean armour", 1),),
            produced_inventory=(("Carnillean armour", 2),),
            repeatable_until_consumed=True,
            required_actions=("Complete Hazeel Cult stage 3 objective",),
        ),
        _stage_req(
            3,
            "Complete Hazeel's revival and finish the quest.",
            "https://runescape.wiki/w/Hazeel_Cult?oldid=6579784",
            variant=HAZEEL_CULT_VARIANT_HAZEEL,
            required_routes=(HAZEEL_CULT_ROUTE_HAZEEL,),
            produced_inventory=(("Mark of Hazeel", 1),),
            required_actions=("Complete Hazeel Cult stage 3 objective",),
        ),
    ),
}

__all__: tuple[str, ...] = ()
