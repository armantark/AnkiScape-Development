from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

PRIEST_IN_PERIL_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "King Roald asked me to check on Drezel at Paterdomus, east of Varrock."),
    _simple_stage(2, "I spoke through the locked Paterdomus door and was told to kill the guard dog below the temple."),
    _simple_stage(3, "The Temple guardian dog is dead. I should report back to King Roald."),
    _simple_stage(4, "King Roald was furious. The voice at the door was not Drezel, and I must return to Paterdomus."),
    _simple_stage(5, "I found the real Drezel locked in a cell guarded by Zamorakian monks and a trapped vampyre."),
    _simple_stage(6, "I need the correct key from the monument to unlock Drezel's cell."),
    _simple_stage(7, "Drezel is free, but I need blessed Salve water to trap the vampyre in its coffin."),
    _simple_stage(8, "The vampyre is trapped. Drezel needs essence to purify the River Salve."),
    _simple_stage(9, "Drezel purified the Salve, blessed me, and gave me Wolfbane.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=PRIEST_IN_PERIL_ID,
        display_name="Priest in Peril",
        stage_count=9,
        point_reward=1,
        rewards=(("Wolfbane dagger", 1),),
        start_point="Speak to King Roald in the Varrock Palace.",
        requirements=("Used during quest: Bucket x1, Rune essence x50 or Pure essence x25",),
        required_items=(),
        combat="Temple guardian dog (level 30, Magic cannot damage it); Monk of Zamorak (level 30) for the key.",
        source=(
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_SOURCE}; "
            f"{PRIEST_IN_PERIL_DARKAN_CERBERUS_SOURCE}; {PRIEST_IN_PERIL_SOURCE}"
        ),
        journal_stages=PRIEST_IN_PERIL_STAGES,
        release_date="2004-06-29",
        members=True,
        difficulty="Novice",
        length="Medium",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("prayer", 1406),),
        unlocks=("Access to Morytania",),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    PRIEST_IN_PERIL_ID: (
        _stage_req(
            1,
            "Speak through the locked Paterdomus temple door.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_SOURCE}",
            auto_actions=("Speak through the Paterdomus temple door",),
        ),
        _stage_req(
            2,
            "Defeat the Temple guardian dog; Magic cannot damage it.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_CERBERUS_SOURCE}; {PRIEST_IN_PERIL_CERBERUS_NPC_SOURCE}",
            combat_encounters=(
                _combat(
                    PRIEST_IN_PERIL_ID,
                    "temple_guardian_dog_30",
                    "Temple guardian dog",
                    30,
                    f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_CERBERUS_SOURCE}; {PRIEST_IN_PERIL_CERBERUS_NPC_SOURCE}",
                    "2011Scape names a level 30 Temple guardian dog and forbids Magic; Darkan's Cerberus NPC zeroes magic hits and advances Priest in Peril on death.",
                    npc_stats=(
                        ("hitpoints", 450),
                        ("attack", 0),
                        ("strength", 0),
                        ("defence", 0),
                        ("magic", 0),
                        ("ranged", 0),
                    ),
                    npc_configs=(
                        ("max_hit", 30),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "passive"),
                        ("magic_damage_immune", True),
                    ),
                    npc_stats_source=PRIEST_IN_PERIL_CERBERUS_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            3,
            "Report the dead guard dog to King Roald.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_SOURCE}",
            auto_actions=("Report the dead guard dog to King Roald",),
        ),
        _stage_req(
            4,
            "Return to Paterdomus and find Drezel imprisoned upstairs.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_DREZEL_JAIL_SOURCE}",
            auto_actions=("Find Drezel imprisoned in the Paterdomus cell",),
        ),
        _stage_req(
            5,
            "Defeat a Monk of Zamorak to obtain the monument key.",
            f"{PRIEST_IN_PERIL_SOURCE}; {PRIEST_IN_PERIL_DARKAN_SOURCE}; {PRIEST_IN_PERIL_MONK_OF_ZAMORAK_NPC_SOURCE}",
            combat_encounters=(
                _combat(
                    PRIEST_IN_PERIL_ID,
                    "monk_of_zamorak_30",
                    "Monk of Zamorak",
                    30,
                    f"{PRIEST_IN_PERIL_SOURCE}; {PRIEST_IN_PERIL_DARKAN_SOURCE}; {PRIEST_IN_PERIL_MONK_OF_ZAMORAK_NPC_SOURCE}",
                    "Darkan Priest in Peril drops the key from Paterdomus Zamorak monk NPC ids 1044-1046; the level 30 id 1046 combatdef supplies the stats.",
                ),
            ),
        ),
        _stage_req(
            6,
            "Swap the golden key at the monument and unlock Drezel's cell.",
            f"{PRIEST_IN_PERIL_DARKAN_SOURCE}; {PRIEST_IN_PERIL_DARKAN_DREZEL_JAIL_SOURCE}",
            consumed_inventory=(("Golden key", 1),),
            auto_actions=("Swap the golden key at the Paterdomus monument", "Unlock Drezel's cell"),
        ),
        _stage_req(
            7,
            "Bless Salve water in a bucket and pour it over the vampire coffin.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_SOURCE}; {PRIEST_IN_PERIL_DARKAN_DREZEL_JAIL_SOURCE}",
            required_inventory=(("Bucket", 1),),
            auto_actions=("Bless Salve water with Drezel", "Pour blessed Salve water over the vampire coffin"),
        ),
        _stage_req(
            8,
            "Give Drezel essence to purify the River Salve.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_DREZEL_MAUSOLEUM_SOURCE}",
            consumed_inventory_options=((("Rune essence", 50), ("Pure essence", 25)),),
        ),
    ),
}

__all__ = (
    'PRIEST_IN_PERIL_STAGES',
)
