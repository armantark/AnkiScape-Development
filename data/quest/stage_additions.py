from __future__ import annotations

from .dependencies import *
from .contract import *
from .ids import *
from .sources import *
from .stage_overrides.members.later.as_a_first_resort import AS_A_FIRST_RESORT_STAGE_ADDITIONS
from .stage_overrides.members.later.underground_pass import UNDERGROUND_PASS_STAGE_ADDITIONS

QUEST_STAGE_REQUIREMENT_ADDITIONS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    "as_a_first_resort": AS_A_FIRST_RESORT_STAGE_ADDITIONS,
    "underground_pass": UNDERGROUND_PASS_STAGE_ADDITIONS,
    SWAN_SONG_ID: (
        _stage_req(
            5,
            "Defeat the Sea Troll Queen.",
            f"{SWAN_SONG_SOURCE}; {SWAN_SONG_WIKI_SOURCE}",
            combat_encounters=(
                _combat(
                    SWAN_SONG_ID,
                    "sea_troll_queen",
                    "Sea Troll Queen",
                    170,
                    f"{SWAN_SONG_WIKI_SOURCE}; {SWAN_SONG_SEA_TROLL_QUEEN_NPC_SOURCE}",
                    "Quest details require the level 170 Sea Troll Queen after the sea troll waves.",
                    npc_stats=(
                        ("hitpoints", 2000),
                        ("attack", 100),
                        ("strength", 70),
                        ("defence", 100),
                        ("magic", 150),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 2345),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=SWAN_SONG_SEA_TROLL_QUEEN_NPC_SOURCE,
                ),
            ),
        ),
    ),
    THE_FEUD_ID: (
        _stage_req(
            4,
            "Defeat the Tough guy after the Bandit champion.",
            f"{THE_FEUD_WIKI_SOURCE}; {THE_FEUD_TOUGH_GUY_NPC_SOURCE}",
            combat_encounters=(
                _combat(
                    THE_FEUD_ID,
                    "tough_guy_75",
                    "Tough guy",
                    75,
                    f"{THE_FEUD_WIKI_SOURCE}; {THE_FEUD_TOUGH_GUY_NPC_SOURCE}",
                    "Historical quest details name Tough guy (level 75) after the Bandit champion.",
                    npc_stats=(
                        ("hitpoints", 750),
                        ("attack", 85),
                        ("strength", 50),
                        ("defence", 50),
                        ("magic", 80),
                        ("ranged", 0),
                    ),
                    npc_configs=(
                        ("max_hit", 70),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=THE_FEUD_TOUGH_GUY_NPC_SOURCE,
                ),
            ),
        ),
    ),
    RFD_FREEING_SIR_AMIK_VARZE_ID: (
        _stage_req(
            3,
            "Defeat the Black Dragon after the Evil Chicken.",
            f"{RFD_FREEING_SIR_AMIK_VARZE_WIKI_SOURCE}; {RFD_BLACK_DRAGON_NPC_SOURCE}",
            combat_encounters=(
                _combat(
                    RFD_FREEING_SIR_AMIK_VARZE_ID,
                    "black_dragon_227",
                    "Black Dragon",
                    227,
                    f"{RFD_FREEING_SIR_AMIK_VARZE_WIKI_SOURCE}; {RFD_BLACK_DRAGON_NPC_SOURCE}",
                    "Historical quest details name Black Dragon (Level 227) after the Evil Chicken.",
                    npc_stats=(
                        ("hitpoints", 1900),
                        ("attack", 200),
                        ("strength", 200),
                        ("defence", 200),
                        ("magic", 100),
                        ("ranged", 1),
                    ),
                    npc_configs=(("attack_speed", 4),),
                    npc_stats_source=RFD_BLACK_DRAGON_NPC_SOURCE,
                ),
            ),
        ),
    ),
    KENNITHS_CONCERNS_ID: (
        _stage_req(
            1,
            "Investigate the Witchaven tunnels and speak to a villager.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            required_tools=(("Pickaxe", 1),),
            auto_actions=(
                "Reach the Witchaven shrine tunnels",
                "Talk to a villager past the rocks",
            ),
        ),
        _stage_req(
            2,
            "Warn Kennith and speak to Kent.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            auto_actions=("Warn Kennith", "Speak to Kent near the Legends' Guild"),
        ),
        _stage_req(
            3,
            "Trap the possessed villagers in the church.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            auto_actions=("Trap the possessed villagers in the church",),
        ),
        _stage_req(
            4,
            "Mine rubium and fill the steam vents.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            required_tools=(("Pickaxe", 1),),
            auto_actions=("Mine rubium and fill the steam vents",),
        ),
        _stage_req(
            5,
            "Find the toy train and rescue Kennith.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            auto_actions=("Find Kennith's toy train", "Use the toy train on Kennith"),
        ),
    ),
}

CAT_FOLLOWER_STATE_NAMES: Tuple[str, ...] = (
    "Kitten",
    "Cat",
    "Overgrown cat",
    "Hellcat",
    "Wily cat",
    "Lazy cat",
)

__all__ = (
    'QUEST_STAGE_REQUIREMENT_ADDITIONS_BY_ID', 'CAT_FOLLOWER_STATE_NAMES',
)
