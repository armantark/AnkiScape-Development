from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

HOLY_GRAIL_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "King Arthur sent me to Merlin for clues about the Holy Grail."),
    _simple_stage(2, "Merlin believes the Grail passed through Entrana and Sir Galahad may know more."),
    _simple_stage(3, "The Entrana High Priest and crone pointed me toward Sir Galahad and the Fisher Realm."),
    _simple_stage(4, "Sir Galahad gave me a Holy table napkin from the Fisher Realm."),
    _simple_stage(5, "The Holy table napkin should reveal the Magic whistles hidden in Draynor Manor."),
    _simple_stage(
        6,
        "The Magic whistle can take me to the Fisher Realm from the six stone heads.",
        "The Black Knight Titan blocks the castle and must be defeated with Excalibur.",
    ),
    _simple_stage(7, "The Black Knight Titan is defeated. I can enter the castle and speak to the Fisher King."),
    _simple_stage(8, "The Fisher King asked me to find his son, Sir Percival."),
    _simple_stage(9, "Sir Percival can restore the Fisher Realm if I free him and show him the Magic whistle."),
    _simple_stage(10, "The Fisher Realm is restored. I should take the Holy grail to King Arthur."),
    _simple_stage(11, "King Arthur has the Holy grail.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    HOLY_GRAIL_ID: (
        _stage_req(
            1,
            "Ask Merlin about the Holy Grail.",
            f"{HOLY_GRAIL_KING_ARTHUR_SOURCE}; {HOLY_GRAIL_MERLIN_SOURCE}",
            auto_actions=("Ask Merlin about the Holy Grail",),
        ),
        _stage_req(
            2,
            "Ask the Entrana High Priest and crone about the Grail.",
            f"{HOLY_GRAIL_MERLIN_SOURCE}; {HOLY_GRAIL_ENTRANA_SOURCE}",
            auto_actions=(
                "Travel to Entrana",
                "Ask the Entrana High Priest and crone about the Grail",
            ),
        ),
        _stage_req(
            3,
            "Ask Sir Galahad for an artifact from the Fisher Realm.",
            f"{HOLY_GRAIL_ENTRANA_SOURCE}; {HOLY_GRAIL_GALAHAD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Ask Sir Galahad for an artifact from the Fisher Realm",),
            produced_inventory=(("Holy table napkin", 1),),
        ),
        _stage_req(
            4,
            "Find the Magic whistles in Draynor Manor while carrying the Holy table napkin.",
            f"{HOLY_GRAIL_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Holy table napkin", 1),),
            auto_actions=(
                "Reach the Draynor Manor whistle room",
                "Find the Magic whistles in Draynor Manor",
            ),
            produced_inventory=(("Magic whistle", 2),),
        ),
        _stage_req(
            5,
            "Blow the Magic whistle at the six stone heads and defeat the Black Knight Titan with Excalibur.",
            f"{HOLY_GRAIL_DARKAN_SOURCE}; {HOLY_GRAIL_TITAN_SOURCE}; {HOLY_GRAIL_TITAN_NPC_SOURCE}",
            required_tools=(("Magic whistle", 1), ("Excalibur", 1)),
            auto_actions=(
                "Reach the Fisher Realm crossing at the six stone heads",
                "Blow the Magic whistle at the six stone heads",
            ),
            produced_inventory=(("Grail bell", 1),),
            combat_encounters=(
                _combat(
                    HOLY_GRAIL_ID,
                    "black_knight_titan_120",
                    "Black Knight Titan",
                    120,
                    HOLY_GRAIL_WIKI_SOURCE,
                    "Black Knight Titan (level 120), defeated only with Excalibur.",
                    npc_stats=(
                        ("hitpoints", 1420),
                        ("attack", 91),
                        ("strength", 100),
                        ("defence", 91),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 150),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=HOLY_GRAIL_TITAN_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            6,
            "Ring the Grail bell and ask the Fisher King about Percival.",
            f"{HOLY_GRAIL_DARKAN_SOURCE}; {HOLY_GRAIL_FISHER_KING_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Grail bell", 1),),
            auto_actions=("Ring the Grail bell and ask the Fisher King about Percival",),
        ),
        _stage_req(
            7,
            "Ask King Arthur about Sir Percival and receive the Magic gold feather.",
            f"{HOLY_GRAIL_KING_ARTHUR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Ask King Arthur about Sir Percival",),
            produced_inventory=(("Magic gold feather", 1),),
        ),
        _stage_req(
            8,
            "Use the Magic gold feather to find Sir Percival, then show him a Magic whistle.",
            f"{HOLY_GRAIL_DARKAN_SOURCE}; {HOLY_GRAIL_PERCIVAL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Magic gold feather", 1),),
            consumed_inventory=(("Magic whistle", 1),),
            auto_actions=(
                "Use the Magic gold feather to find Sir Percival",
                "Free Sir Percival from the sack",
                "Show Sir Percival the Magic whistle",
            ),
        ),
        _stage_req(
            9,
            "Take the Holy grail from the restored Fisher Realm.",
            f"{HOLY_GRAIL_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Take the Holy grail from the restored Fisher Realm",),
            produced_inventory=(("Holy grail", 1),),
        ),
        _stage_req(
            10,
            "Give the Holy grail to King Arthur.",
            f"{HOLY_GRAIL_KING_ARTHUR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Holy grail", 1),),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Holy table napkin": {
            "category": "material",
            "tradeable": False,
            "source": f"{HOLY_GRAIL_GALAHAD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Magic whistle": {
            "category": "tool",
            "tradeable": False,
            "source": f"{HOLY_GRAIL_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Grail bell": {
            "category": "tool",
            "tradeable": False,
            "source": f"{HOLY_GRAIL_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Magic gold feather": {
            "category": "tool",
            "tradeable": False,
            "source": f"{HOLY_GRAIL_KING_ARTHUR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Holy grail": {
            "category": "material",
            "tradeable": False,
            "source": f"{HOLY_GRAIL_DARKAN_SOURCE}; {HOLY_GRAIL_KING_ARTHUR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'HOLY_GRAIL_STAGES',
)
