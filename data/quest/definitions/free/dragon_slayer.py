from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

DRAGON_SLAYER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "The Guildmaster says I need to prove myself before Oziach will sell me rune platebodies."),
    _simple_stage(2, "Oziach says I must slay Elvarg on Crandor to prove myself a hero."),
    _simple_stage(3, "The Guildmaster can explain how to reach Crandor and how to survive dragonfire."),
    _simple_stage(4, "The Duke of Lumbridge has an anti-dragon shield for the fight with Elvarg."),
    _simple_stage(5, "Melzar's Maze contains one piece of the Crandor map."),
    _simple_stage(6, "Wormbrain has another piece of the Crandor map in Port Sarim jail."),
    _simple_stage(7, "The Oracle knows how to reach the third map piece under Ice Mountain."),
    _simple_stage(8, "The magic door below Ice Mountain needs the Oracle's four items."),
    _simple_stage(9, "I have all three map pieces and can assemble the Crandor map."),
    _simple_stage(10, "The Lady Lumbridge is for sale in Port Sarim."),
    _simple_stage(11, "The Lady Lumbridge needs planks, steel nails, and a hammer before it can sail."),
    _simple_stage(12, "Ned will captain the Lady Lumbridge if I show him the Crandor map."),
    _simple_stage(13, "Captain Ned is waiting at the Lady Lumbridge to sail for Crandor."),
    _simple_stage(14, "I reached Crandor. Elvarg must be slain while I am protected from dragonfire."),
    _simple_stage(15, "Elvarg is dead. Oziach needs to hear that I defeated the dragon."),
    _simple_stage(16, "Oziach accepted me as a true hero.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=DRAGON_SLAYER_ID,
        display_name="Dragon Slayer",
        stages=16,
        point_reward=2,
        rewards=(),
        start_point="Speak to the Guildmaster inside the Champions' Guild, south of Varrock.",
        requirements=(
            "32 Quest Points",
            (
                "Used during quest: Wizard's mind bomb x1, Silk x1, Bowl (unfired) x1, Crayfish cage or Lobster pot x1, "
                "Coins x12000, Plank x3, Steel nails x90, Hammer x1"
            ),
        ),
        required_items=(),
        combat=(
            "Melzar's Maze requires key-carrying lesser foes, Melzar the Mad, and a lesser demon; "
            "Elvarg (level 83) must be defeated with anti-dragon shield protection. "
            "Wormbrain can be killed for a map piece, but the modeled deterministic route buys it for 10,000 coins."
        ),
        source=(
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_GUILDMASTER_SOURCE}; "
            f"{DARKAN_DRAGON_SLAYER_OZIACH_SOURCE}; {DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; "
            f"{DARKAN_DRAGON_SLAYER_WORMBRAIN_SOURCE}; {DARKAN_DRAGON_SLAYER_KLARENSE_SOURCE}; "
            f"{DARKAN_DRAGON_SLAYER_NED_SOURCE}; {DARKAN_DRAGON_SLAYER_CAPTAIN_NED_SOURCE}; "
            f"{DARKAN_DRAGON_SLAYER_ELVARG_SOURCE}; {RUNE_MYSTERIES_DUKE_SOURCE_PATH}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {DRAGON_SLAYER_WIKI_SOURCE}"
        ),
        journal_stages=DRAGON_SLAYER_STAGES,
        release_date="2001-09-23",
        members=False,
        difficulty="Experienced",
        length="Long",
        timeline="Fifth Age",
        required_quest_points=32,
        xp_rewards=(QuestXpReward("defense", 18650), QuestXpReward("strength", 18650)),
        unlocks=(
            "The ability to equip a rune platebody and a green dragonhide body.",
            "Access to all of Crandor Island",
            "Access to Melzar's Maze",
            "Access to the dragon crest on herald capes",
        ),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    DRAGON_SLAYER_ID: (
        _stage_req(
            2,
            "Accept Oziach's challenge to slay Elvarg.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_OZIACH_SOURCE}",
            auto_actions=("Accept Oziach's dragon-slaying challenge",),
        ),
        _stage_req(
            3,
            "Finish the Guildmaster's Crandor briefing and receive Melzar's Maze key.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_GUILDMASTER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Complete the Guildmaster's Crandor briefing",),
            produced_inventory=(("Maze key", 1),),
        ),
        _stage_req(
            4,
            "Ask Duke Horacio for an anti-dragon shield before facing Elvarg.",
            (
                f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_GUILDMASTER_SOURCE}; "
                f"{DARKAN_LUMBRIDGE_DUKE_SOURCE}; {RUNE_MYSTERIES_DUKE_SOURCE_PATH}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            auto_actions=("Ask Duke Horacio for an anti-dragon shield",),
            produced_inventory=(("Anti-dragon shield", 1),),
        ),
        _stage_req(
            5,
            "Clear Melzar's Maze and search the final chest for a Crandor map piece.",
            (
                f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; "
                f"{DRAGON_SLAYER_2011SCAPE_MAZE_SPAWNS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            required_tools=(("Maze key", 1),),
            produced_inventory=(("Map part", 1),),
            combat_encounters=(
                _combat(
                    DRAGON_SLAYER_ID,
                    "zombie_rat_3",
                    "Zombie rat",
                    3,
                    (
                        f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; "
                        f"{DRAGON_SLAYER_2011SCAPE_MAZE_SPAWNS_SOURCE}; {DARKAN_DRAGON_SLAYER_ZOMBIE_RAT_NPC_SOURCE}"
                    ),
                    "Melzar's Maze gates the red key on zombie rat combat; the Darkan combatdef supplies the level 3 stats.",
                    npc_stats=(
                        ("hitpoints", 50),
                        ("attack", 2),
                        ("strength", 3),
                        ("defence", 2),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 10),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=DARKAN_DRAGON_SLAYER_ZOMBIE_RAT_NPC_SOURCE,
                ),
                _combat(
                    DRAGON_SLAYER_ID,
                    "ghost_19",
                    "Ghost",
                    19,
                    f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; {DRAGON_SLAYER_2011SCAPE_GHOST_NPC_SOURCE}",
                    "The local 2011Scape ghost definition supplies the level 19 Maze ghost combat stats.",
                    npc_stats=(
                        ("hitpoints", 250),
                        ("attack", 13),
                        ("strength", 13),
                        ("defence", 18),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_bonuses=(
                        ("defenceStab", 5),
                        ("defenceSlash", 5),
                        ("defenceCrush", 5),
                        ("defenceMagic", -5),
                        ("defenceRanged", 5),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "melee")),
                    npc_stats_source=DRAGON_SLAYER_2011SCAPE_GHOST_NPC_SOURCE,
                ),
                _combat(
                    DRAGON_SLAYER_ID,
                    "skeleton_22",
                    "Skeleton",
                    22,
                    f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; {DRAGON_SLAYER_2011SCAPE_SKELETON_NPC_SOURCE}",
                    "The local 2011Scape skeleton definition supplies the level 22 Maze skeleton combat stats.",
                    npc_stats=(
                        ("hitpoints", 290),
                        ("attack", 15),
                        ("strength", 18),
                        ("defence", 17),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_bonuses=(
                        ("defenceStab", 5),
                        ("defenceSlash", 5),
                        ("defenceCrush", -5),
                        ("defenceMagic", 0),
                        ("defenceRanged", 5),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "melee")),
                    npc_stats_source=DRAGON_SLAYER_2011SCAPE_SKELETON_NPC_SOURCE,
                ),
                _combat(
                    DRAGON_SLAYER_ID,
                    "zombie_24",
                    "Zombie",
                    24,
                    f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; {DRAGON_SLAYER_2011SCAPE_ZOMBIE_NPC_SOURCE}",
                    "The local 2011Scape zombie definition supplies the level 24 Maze zombie combat stats.",
                    npc_stats=(
                        ("hitpoints", 300),
                        ("attack", 19),
                        ("strength", 21),
                        ("defence", 16),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_bonuses=(
                        ("attackStab", 5),
                        ("attackCrush", 7),
                        ("defenceStab", 9),
                        ("defenceSlash", 8),
                        ("defenceCrush", 12),
                        ("defenceMagic", 10),
                        ("defenceRanged", 11),
                    ),
                    npc_configs=(("attack_speed", 5), ("attack_style", "melee")),
                    npc_stats_source=DRAGON_SLAYER_2011SCAPE_ZOMBIE_NPC_SOURCE,
                ),
                _combat(
                    DRAGON_SLAYER_ID,
                    "melzar_the_mad_43",
                    "Melzar the Mad",
                    43,
                    f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; {DARKAN_DRAGON_SLAYER_MELZAR_NPC_SOURCE}",
                    "Melzar's Maze requires killing Melzar the Mad for the magenta key; the Darkan combatdef supplies the level 43 stats.",
                    npc_stats=(
                        ("hitpoints", 440),
                        ("attack", 37),
                        ("strength", 37),
                        ("defence", 34),
                        ("magic", 40),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 50),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_DRAGON_SLAYER_MELZAR_NPC_SOURCE,
                ),
                _combat(
                    DRAGON_SLAYER_ID,
                    "lesser_demon_82",
                    "Lesser demon",
                    82,
                    f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; {DRAGON_SLAYER_2011SCAPE_LESSER_DEMON_NPC_SOURCE}",
                    "Melzar's Maze requires killing the lesser demon for the final key; local 2011Scape supplies the level 82 stats.",
                    npc_stats=(
                        ("hitpoints", 790),
                        ("attack", 68),
                        ("strength", 70),
                        ("defence", 71),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_bonuses=(
                        ("attackStab", 0),
                        ("attackCrush", 0),
                        ("defenceStab", 0),
                        ("defenceSlash", 0),
                        ("defenceCrush", 0),
                        ("defenceMagic", -10),
                        ("defenceRanged", 0),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "melee"), ("attack_bonus", "slash_att")),
                    npc_stats_source=DRAGON_SLAYER_2011SCAPE_LESSER_DEMON_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            6,
            "Buy Wormbrain's Crandor map piece from Port Sarim jail.",
            (
                f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_WORMBRAIN_SOURCE}; "
                f"{DARKAN_DRAGON_SLAYER_WORMBRAIN_NPC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(("Coins", 10000),),
            produced_inventory=(("Map part", 1),),
        ),
        _stage_req(
            7,
            "Ask the Oracle how to reach Thalzar's map piece.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_ORACLE_SOURCE}",
            auto_actions=("Ask the Oracle about Thalzar's map piece",),
        ),
        _stage_req(
            8,
            "Open the magic door below Ice Mountain with the Oracle's four items.",
            (
                f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_ORACLE_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {DRAGON_SLAYER_WIKI_SOURCE}"
            ),
            consumed_inventory=(("Wizard's mind bomb", 1), ("Silk", 1), ("Bowl (unfired)", 1)),
            consumed_inventory_options=((("Crayfish cage", 1), ("Lobster pot", 1)),),
            produced_inventory=(("Map part", 1),),
        ),
        _stage_req(
            9,
            "Combine the three Crandor map pieces.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Map part", 3),),
            produced_inventory=(("Crandor map", 1),),
        ),
        _stage_req(
            10,
            "Buy the Lady Lumbridge from Klarense.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_KLARENSE_SOURCE}",
            consumed_inventory=(("Coins", 2000),),
        ),
        _stage_req(
            11,
            "Repair the Lady Lumbridge with three planks and ninety steel nails.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Plank", 3), ("Steel nails", 90)),
            required_tools=(("Hammer", 1),),
        ),
        _stage_req(
            12,
            "Recruit Ned as captain and show him the completed Crandor map.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_NED_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Crandor map", 1),),
            auto_actions=("Recruit Ned as captain of the Lady Lumbridge",),
        ),
        _stage_req(
            13,
            "Sail to Crandor with Captain Ned.",
            f"{DARKAN_DRAGON_SLAYER_CAPTAIN_NED_SOURCE}; {DARKAN_DRAGON_SLAYER_BOAT_SCENE_SOURCE}",
            auto_actions=("Sail to Crandor with Captain Ned",),
        ),
        _stage_req(
            14,
            "Fight Elvarg on Crandor while carrying the anti-dragon shield.",
            (
                f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_ELVARG_SOURCE}; "
                f"{DARKAN_DRAGON_SLAYER_ELVARG_NPC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            required_tools=(("Anti-dragon shield", 1),),
            produced_inventory=(("Elvarg's head", 1),),
            combat_encounters=(
                _combat(
                    DRAGON_SLAYER_ID,
                    "elvarg_83",
                    "Elvarg",
                    83,
                    f"{DARKAN_DRAGON_SLAYER_ELVARG_SOURCE}; {DARKAN_DRAGON_SLAYER_ELVARG_NPC_SOURCE}",
                    "Darkan's Elvarg boss adds Elvarg's head and moves Dragon Slayer to the report stage on death; the combatdef supplies Elvarg's level 83 stats.",
                    npc_stats=(
                        ("hitpoints", 800),
                        ("attack", 70),
                        ("strength", 70),
                        ("defence", 70),
                        ("magic", 70),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 100),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_DRAGON_SLAYER_ELVARG_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            15,
            "Report Elvarg's death to Oziach.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_OZIACH_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_inventory=(("Elvarg's head", 1),),
            auto_actions=("Report Elvarg's death to Oziach",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Maze key": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_GUILDMASTER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Anti-dragon shield": {
            "category": "equipment",
            "source": f"{DARKAN_LUMBRIDGE_DUKE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Map part": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Crandor map": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Wizard's mind bomb": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Silk": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Crayfish cage": {
            "category": "tool",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Lobster pot": {
            "category": "tool",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Plank": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Hammer": {
            "category": "tool",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Elvarg's head": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_ELVARG_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'DRAGON_SLAYER_STAGES',
)
