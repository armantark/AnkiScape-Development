from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

DRUIDIC_RITUAL_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Kaqemeex asked me to speak with Sanfew in Taverley."),
    _simple_stage(2, "Sanfew asked me to gather Living water, Wandering wyrmwood, and Stone scales."),
    _simple_stage(3, "I collected Living water from the cave south of Taverley."),
    _simple_stage(4, "I picked Wandering wyrmwood in south Taverley, just north of Nora T. Hagg's house."),
    _simple_stage(5, "I caught a Stone fish at the Sparkling Fishing Spot."),
    _simple_stage(6, "I used a chisel on the Stone fish to gather Stone scales."),
    _simple_stage(7, "Sanfew combined the three ingredients into an Ointment of imbalance."),
    _simple_stage(
        8,
        "I gave the Ointment of imbalance to Kaqemeex and restored the stone circle's balance.",
        "Quest complete!",
    ),
)

QUEST = QuestDefinition(
        id=DRUIDIC_RITUAL_ID,
        display_name="Druidic Ritual",
        stage_count=8,
        point_reward=4,
        rewards=(("Grimy guam", 15), ("Eye of newt", 15)),
        start_point="Speak to Kaqemeex at the stone circle north of Taverley.",
        requirements=("Used during quest: Coins x1, Chisel x1, Fishing rod x1",),
        required_items=(),
        combat="None.",
        source=(
            f"{DRUIDIC_RITUAL_WIKI_SOURCE}; {DRUIDIC_RITUAL_QUICK_GUIDE_SOURCE}; "
            f"{DRUIDIC_RITUAL_DARKAN_SOURCE_PATH}; {DRUIDIC_RITUAL_CACHE_SOURCE}"
        ),
        journal_stages=DRUIDIC_RITUAL_STAGES,
        release_date="2002-02-27",
        members=True,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("herblore", 250),),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    DRUIDIC_RITUAL_ID: (
        _stage_req(
            1,
            "Speak to Sanfew about the ritual ingredients.",
            f"{DRUIDIC_RITUAL_WIKI_SOURCE}; {DRUIDIC_RITUAL_QUICK_GUIDE_SOURCE}; {DRUIDIC_RITUAL_DARKAN_SOURCE_PATH}",
            produced_inventory=(("Vial", 1),),
            auto_actions=("Speak to Sanfew about the ritual ingredients",),
        ),
        _stage_req(
            2,
            "Collect Living water from the cave south of Taverley.",
            f"{DRUIDIC_RITUAL_WIKI_SOURCE}; {DRUIDIC_RITUAL_QUICK_GUIDE_SOURCE}",
            consumed_inventory=(("Vial", 1),),
            produced_inventory=(("Living water", 1),),
            auto_actions=("Collect Living water from the cave south of Taverley",),
        ),
        _stage_req(
            3,
            "Pick Wandering wyrmwood in south Taverley, just north of Nora T. Hagg's house.",
            f"{DRUIDIC_RITUAL_WIKI_SOURCE}; {DRUIDIC_RITUAL_QUICK_GUIDE_SOURCE}",
            produced_inventory=(("Wandering wyrmwood", 1),),
            auto_actions=("Pick Wandering wyrmwood in south Taverley, just north of Nora T. Hagg's house",),
        ),
        _stage_req(
            4,
            "Catch a Stone fish at the Sparkling Fishing Spot.",
            f"{DRUIDIC_RITUAL_WIKI_SOURCE}; {DRUIDIC_RITUAL_QUICK_GUIDE_SOURCE}; {DRUIDIC_RITUAL_CACHE_SOURCE}",
            required_tools=(("Fishing rod", 1),),
            consumed_inventory=(("Coins", 1),),
            produced_inventory=(("Stone fish", 1),),
            auto_actions=("Catch a Stone fish at the Sparkling Fishing Spot",),
        ),
        _stage_req(
            5,
            "Use a chisel on the Stone fish to gather Stone scales.",
            f"{DRUIDIC_RITUAL_WIKI_SOURCE}; {DRUIDIC_RITUAL_QUICK_GUIDE_SOURCE}; {DRUIDIC_RITUAL_CACHE_SOURCE}",
            required_inventory=(("Stone fish", 1),),
            required_tools=(("Chisel", 1),),
            produced_inventory=(("Stone scales", 1),),
            auto_actions=("Use a chisel on the Stone fish",),
        ),
        _stage_req(
            6,
            "Give Sanfew the Living water, Wandering wyrmwood, and Stone scales.",
            f"{DRUIDIC_RITUAL_WIKI_SOURCE}; {DRUIDIC_RITUAL_QUICK_GUIDE_SOURCE}",
            consumed_inventory=(("Living water", 1), ("Wandering wyrmwood", 1), ("Stone scales", 1)),
            produced_inventory=(("Ointment of imbalance", 1),),
            auto_actions=("Give Sanfew the ritual ingredients",),
        ),
        _stage_req(
            7,
            "Give the Ointment of imbalance to Kaqemeex.",
            f"{DRUIDIC_RITUAL_WIKI_SOURCE}; {DRUIDIC_RITUAL_QUICK_GUIDE_SOURCE}; {DRUIDIC_RITUAL_DARKAN_SOURCE_PATH}",
            consumed_inventory=(("Ointment of imbalance", 1),),
            auto_actions=("Give the Ointment of imbalance to Kaqemeex",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Living water": {
            "category": "material",
            "item_id": 23096,
            "tradeable": False,
            "stackable": False,
            "source": f"https://runescape.wiki/w/Living_water?oldid=5871546; {DRUIDIC_RITUAL_CACHE_SOURCE}",
        },
        "Wandering wyrmwood": {
            "category": "material",
            "item_id": 23097,
            "tradeable": False,
            "stackable": False,
            "source": f"https://runescape.wiki/w/Wandering_wyrmwood_(item)?oldid=5987356; {DRUIDIC_RITUAL_CACHE_SOURCE}",
        },
        "Stone fish": {
            "category": "material",
            "item_id": 23098,
            "tradeable": False,
            "stackable": False,
            "source": f"https://runescape.wiki/w/Stone_fish?oldid=5907958; {DRUIDIC_RITUAL_CACHE_SOURCE}",
        },
        "Stone scales": {
            "category": "material",
            "item_id": 23099,
            "tradeable": False,
            "stackable": False,
            "source": f"https://runescape.wiki/w/Stone_scales?oldid=5236531; {DRUIDIC_RITUAL_CACHE_SOURCE}",
        },
        "Ointment of imbalance": {
            "category": "material",
            "item_id": 23100,
            "tradeable": False,
            "stackable": False,
            "source": f"https://runescape.wiki/w/Ointment_of_imbalance?oldid=5236532; {DRUIDIC_RITUAL_CACHE_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'DRUIDIC_RITUAL_STAGES',
)
