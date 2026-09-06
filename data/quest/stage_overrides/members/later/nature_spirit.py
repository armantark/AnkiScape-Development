from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    NATURE_SPIRIT_ID: (
        _stage_req(
            1,
            "Speak to Drezel in the passage beneath Paterdomus.",
            NATURE_SPIRIT_STAGE_ACTION_SOURCE,
            auto_actions=(
                "Talk to Drezel who is located in the passageway between Silvarea and Morytania.",
            ),
        ),
        _stage_req(
            2,
            "Travel through Mort Myre Swamp to Filliman's grotto.",
            NATURE_SPIRIT_STAGE_ACTION_SOURCE,
            auto_actions=(
                "Exit into Morytania and travel Southeast to a fence.",
                "Look along the fence for a gate and go through it.",
                "Go South until a round island is found with a grotto tree.",
                "Jump across the broken bridge and onto the island.",
            ),
        ),
        _stage_req(
            3,
            "Help Filliman remember who he is and ask Drezel for a blessing.",
            NATURE_SPIRIT_STAGE_ACTION_SOURCE,
            required_inventory=(("Ghostspeak amulet", 1),),
            auto_actions=(
                "Equip a Ghostspeak amulet and attempt to enter the grotto.",
                "Take the Washing bowl off of the nearby table and use the Mirror on Filliman.",
                "Search the grotto tree to find his journal and give it to him.",
                "Ask him what his plans are.",
                "Ask him how you can help.",
                "Have Drezel bless you.",
            ),
        ),
        _stage_req(
            4,
            "Complete Filliman's grotto ritual.",
            NATURE_SPIRIT_STAGE_ACTION_SOURCE,
            auto_actions=(
                "Find a rotting log in the swamp and use the druidic spell next to it.",
                "Take a mushroom from the log and show it to Filliman.",
                "Use the mushroom on the brown stone.",
                "Use the used spell card on the grey stone.",
                "Stand on top of the orange stone.",
                "Tell Filliman the puzzle is solved.",
                "Go in the tree and search the grotto.",
            ),
        ),
        _stage_req(
            5,
            "Give Filliman a silver sickle to bless.",
            NATURE_SPIRIT_STAGE_ACTION_SOURCE,
            consumed_inventory=(("Silver sickle", 1),),
            produced_inventory=(("Silver sickle (b)", 1), ("Druid pouch", 1)),
            auto_actions=("Give Filliman a Silver sickle.",),
        ),
        _stage_req(
            6,
            "Bloom the swamp, fill the druid pouch, and defeat three Ghasts.",
            NATURE_SPIRIT_STAGE_ACTION_SOURCE,
            required_inventory=(("Silver sickle (b)", 1), ("Druid pouch", 1)),
            auto_actions=(
                "Operate the sickle in the swamp next to bushes, logs, or twigs.",
                "Collect what grows and fill the Druid pouch with them.",
                "Wander around until a Ghast attacks and kill it. (Or you could use the Druid pouch on the ghast, allowing them to be attacked)",
                "Kill a total of three ghasts and return to Filliman.",
            ),
            combat_encounters=(
                _combat(
                    NATURE_SPIRIT_ID,
                    "ghast_30",
                    "Ghast",
                    30,
                    f"{NATURE_SPIRIT_SOURCE}; {NATURE_SPIRIT_GHASTS_SOURCE}; {NATURE_SPIRIT_GHAST_NPC_SOURCE}",
                    "3 Ghasts (level 30)",
                    quantity=3,
                    npc_stats=(
                        ("hitpoints", 450),
                        ("attack", 22),
                        ("strength", 22),
                        ("defence", 18),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 30),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "slash_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=NATURE_SPIRIT_GHAST_NPC_SOURCE,
                ),
            ),
        ),
    ),
}

__all__: tuple[str, ...] = ()
