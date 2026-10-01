from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

DEMON_SLAYER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Gypsy Aris saw Delrith returning and said I must follow Wally's path.",
        "She says Sir Prysin in Varrock Palace knows where Silverlight is.",
    ),
    _simple_stage(
        2,
        "Sir Prysin says Silverlight is locked in a special box.",
        "I need three Silverlight keys before he can give me the sword.",
    ),
    _simple_stage(
        3,
        "Sir Prysin's key is stuck in the drain north-east of Varrock Castle.",
        "A bucket of water should wash it into the sewers where I can retrieve it.",
    ),
    _simple_stage(
        4,
        "Wizard Traiborn has another key.",
        "He needs twenty-five regular bones for a ritual to retrieve it.",
    ),
    _simple_stage(
        5,
        "Captain Rovin has the third key at the top of Varrock Palace's north-west tower.",
    ),
    _simple_stage(
        6,
        "I have the three Silverlight keys.",
        "Sir Prysin can now open the box and give me Silverlight.",
    ),
    _simple_stage(
        7,
        "I have Silverlight.",
        "Delrith is at the Dark Wizards' altar south of Varrock, and ordinary weapons will not hurt him.",
    ),
    _simple_stage(
        8,
        "Delrith has been weakened with Silverlight.",
        "I must recite the incantation to banish him: Aber, Gabindo, Purchai, Camerinthum, Carlem.",
    ),
    _simple_stage(
        9,
        "Quest complete!",
    ),
)

QUEST = QuestDefinition(
        id=DEMON_SLAYER_ID,
        display_name="Demon Slayer",
        stages=9,
        point_reward=3,
        rewards=(),
        start_point="Speak to Gypsy Aris in the tent on the western side of Varrock Square.",
        requirements=(
            "Used during quest: Coins x1, Bucket of water x1, Bones x25",
            "Silverlight must be obtained before fighting Delrith.",
        ),
        required_items=(),
        combat="Delrith (level 27) is fought with Silverlight at the Dark Wizards' altar.",
        source=(
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_GYPSY_SOURCE}; "
            f"{DARKAN_DEMON_SLAYER_SIR_PRYSIN_SOURCE}; {DARKAN_DEMON_SLAYER_TRAIBORN_SOURCE}; "
            f"{DARKAN_DEMON_SLAYER_ROVIN_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_SOURCE}; "
            f"{DARKAN_DEMON_SLAYER_DELRITH_CONTROLLER_SOURCE}; {DARKAN_DEMON_SLAYER_INCANTATION_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_NPC_SOURCE}; {DEMON_SLAYER_WIKI_SOURCE}"
        ),
        journal_stages=DEMON_SLAYER_STAGES,
        release_date="2001-01-04",
        members=False,
        difficulty="Novice",
        length="Short to Medium",
        timeline="Fifth Age",
        unlocks=("Silverlight",),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    DEMON_SLAYER_ID: (
        _stage_req(
            1,
            "Cross Gypsy Aris's palm with silver and accept the Delrith prophecy.",
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_GYPSY_SOURCE}",
            consumed_inventory=(("Coins", 1),),
        ),
        _stage_req(
            3,
            "Wash Sir Prysin's key from the drain into the sewers and retrieve it.",
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_SIR_PRYSIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Bucket of water", 1),),
            produced_inventory=(("Bucket", 1), ("Silverlight key", 1)),
        ),
        _stage_req(
            4,
            "Give Wizard Traiborn twenty-five bones for the key ritual.",
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_TRAIBORN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Bones", 25),),
            produced_inventory=(("Silverlight key", 1),),
        ),
        _stage_req(
            5,
            "Convince Captain Rovin to hand over his Silverlight key.",
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_ROVIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            produced_inventory=(("Silverlight key", 1),),
        ),
        _stage_req(
            6,
            "Give Sir Prysin all three Silverlight keys and receive Silverlight.",
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_SIR_PRYSIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Silverlight key", 3),),
            produced_inventory=(("Silverlight", 1),),
        ),
        _stage_req(
            7,
            "Fight Delrith at the Dark Wizards' altar with Silverlight.",
            (
                f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_CONTROLLER_SOURCE}; "
                f"{DARKAN_DEMON_SLAYER_DELRITH_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_NPC_SOURCE}"
            ),
            combat_encounters=(
                _combat(
                    DEMON_SLAYER_ID,
                    "delrith_27",
                    "Delrith",
                    27,
                    (
                        f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_CONTROLLER_SOURCE}; "
                        f"{DARKAN_DEMON_SLAYER_DELRITH_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_NPC_SOURCE}"
                    ),
                    (
                        "Darkan starts the Delrith controller only after Silverlight is obtained and "
                        "DelrithBoss prevents non-Silverlight damage; the controller also spawns "
                        "supporting Dark wizards, but the required quest kill is Delrith. The local "
                        "combatdef supplies Delrith's level 27 melee stats."
                    ),
                    npc_stats=(
                        ("hitpoints", 70),
                        ("attack", 11),
                        ("strength", 10),
                        ("defence", 5),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 30),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "passive"),
                        ("required_weapon", "Silverlight"),
                    ),
                    npc_stats_source=DARKAN_DEMON_SLAYER_DELRITH_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            8,
            "Recite the incantation to banish Delrith.",
            f"{DARKAN_DEMON_SLAYER_GYPSY_SOURCE}; {DARKAN_DEMON_SLAYER_INCANTATION_SOURCE}",
            auto_actions=("Recite Aber, Gabindo, Purchai, Camerinthum, Carlem",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Silverlight": {
            "category": "equipment",
            "source": f"{DARKAN_DEMON_SLAYER_SIR_PRYSIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Silverlight key": {
            "category": "material",
            "source": f"{DARKAN_DEMON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'DEMON_SLAYER_STAGES',
)
