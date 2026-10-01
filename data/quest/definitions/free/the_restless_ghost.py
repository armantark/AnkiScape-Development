from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

RESTLESS_GHOST_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Father Aereck asked me to speak to Father Urhney in Lumbridge Swamp."),
    _simple_stage(2, "Father Urhney gave me a ghostspeak amulet so I can talk to the ghost."),
    _simple_stage(3, "The ghost told me his skull was stolen near the mine south of Lumbridge graveyard."),
    _simple_stage(4, "I found the muddy skull and a skeleton warlock appeared."),
    _simple_stage(5, "I returned the skull to the ghost's coffin.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=THE_RESTLESS_GHOST_ID,
        display_name="The Restless Ghost",
        stage_count=5,
        point_reward=1,
        rewards=(("Ancient bones", 5),),
        start_point="Speak to Father Aereck in the chapel south-east of Lumbridge Castle.",
        requirements=(),
        required_items=(),
        combat="Skeleton warlock (level 11) after taking the ghost's skull.",
        source=(
            f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_FATHER_URHNEY_SOURCE_PATH}; "
            f"{RESTLESS_GHOST_DIALOGUE_SOURCE_PATH}; {RESTLESS_GHOST_SKULL_SOURCE_PATH}; "
            f"{RESTLESS_GHOST_COFFIN_SOURCE_PATH}; {RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH}"
        ),
        journal_stages=RESTLESS_GHOST_STAGES,
        release_date="2001-01-04",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("prayer", 125),),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    THE_RESTLESS_GHOST_ID: (
        _stage_req(
            1,
            "Receive the ghostspeak amulet from Father Urhney.",
            f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_FATHER_URHNEY_SOURCE_PATH}",
            auto_actions=("Receive the ghostspeak amulet from Father Urhney",),
            produced_inventory=(("Ghostspeak amulet", 1),),
        ),
        _stage_req(
            2,
            "Speak to the restless ghost while wearing the ghostspeak amulet.",
            f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_DIALOGUE_SOURCE_PATH}",
            required_inventory=(("Ghostspeak amulet", 1),),
            auto_actions=("Speak to the restless ghost",),
        ),
        _stage_req(
            3,
            "Search the Lumbridge Swamp mining spot for the muddy skull.",
            f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_SKULL_SOURCE_PATH}",
            auto_actions=("Search the mining spot for the ghost's skull",),
            produced_inventory=(("Muddy skull", 1),),
        ),
        _stage_req(
            4,
            "Defeat the skeleton warlock and return the muddy skull to the ghost's coffin.",
            (
                f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_SKULL_SOURCE_PATH}; "
                f"{RESTLESS_GHOST_COFFIN_SOURCE_PATH}; {RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH}"
            ),
            required_inventory=(("Muddy skull", 1),),
            consumed_inventory=(("Muddy skull", 1),),
            auto_actions=("Return the muddy skull to the ghost's coffin",),
            combat_encounters=(
                _combat(
                    THE_RESTLESS_GHOST_ID,
                    "skeleton_warlock",
                    "Skeleton warlock",
                    11,
                    (
                        f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_SKULL_SOURCE_PATH}; "
                        f"{RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH}"
                    ),
                    (
                        "The Lumbridge skull object gives the muddy skull and spawns "
                        "Npcs.SKELETON_WARLOCK; the local combat definition supplies "
                        "the magic-style battle stats."
                    ),
                    npc_stats=(
                        ("hitpoints", 180),
                        ("attack", 1),
                        ("strength", 1),
                        ("defence", 1),
                        ("magic", 8),
                    ),
                    npc_bonuses=(
                        ("attackStab", 0),
                        ("attackCrush", 0),
                        ("defenceStab", 0),
                        ("defenceSlash", 0),
                        ("defenceCrush", 0),
                        ("defenceMagic", 5),
                        ("defenceRanged", 0),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "magic")),
                    npc_stats_source=RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH,
                ),
            ),
        ),
    ),
}

__all__ = (
    'RESTLESS_GHOST_STAGES',
)
