from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
)
from ..contract import (
    BIG_WOLF_SOURCE_PATH,
    BLACK_BEAR_SOURCE_PATH,
    BLACK_UNICORN_SOURCE_PATH,
    GIANT_BAT_SOURCE_PATH,
    UNICORN_SOURCE_PATH,
    WHITE_WOLF_LEVEL_25_SOURCE_PATH,
    WHITE_WOLF_LEVEL_38_SOURCE_PATH,
    WOLF_LEVEL_11_SOURCE_PATH,
)

UNICORN_DROPS = {
    "guaranteed": (("Bones", 1), ("Unicorn horn", 1)),
    "tables": (
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 130},
                {"item": "Green charm", "quantity": 1, "slots": 60},
                {"item": "Crimson charm", "quantity": 1, "slots": 40},
                {"item": "Blue charm", "quantity": 1, "slots": 5},
                {"slots": 765},
            ),
        },
    ),
}


BLACK_BEAR_DROPS = {
    "guaranteed": (("Bones", 1), ("Bear fur", 1), ("Raw bear meat", 1)),
    "tables": (
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 180},
                {"item": "Green charm", "quantity": 1, "slots": 8},
                {"item": "Crimson charm", "quantity": 1, "slots": 11},
                {"item": "Blue charm", "quantity": 1, "slots": 5},
                {"slots": 796},
            ),
        },
    ),
}


WOLF_LEVEL_11_DROPS = {
    "guaranteed": (("Wolf bones", 1), ("Bones", 1)),
    "tables": (
        {
            "name": "Main",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 20},
                {"item": "Green charm", "quantity": 1, "slots": 30},
                {"item": "Crimson charm", "quantity": 1, "slots": 50},
                {"item": "Blue charm", "quantity": 1, "slots": 10},
                {"slots": 890},
            ),
        },
    ),
}


WHITE_WOLF_DROPS = {
    "guaranteed": (("Wolf bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 110},
                {"item": "Green charm", "quantity": 1, "slots": 50},
                {"item": "Crimson charm", "quantity": 1, "slots": 140},
                {"item": "Blue charm", "quantity": 1, "slots": 80},
                {"slots": 620},
            ),
        },
    ),
}


GIANT_BAT_DROPS = {"guaranteed": (("Bat bones", 1),), "tables": ()}


ENEMIES = {
    "unicorn": {
        "display_name": "Unicorn",
        "level": 15,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "stats": {
            "hitpoints": 190,
            "attack": 11,
            "strength": 13,
            "defence": 13,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": UNICORN_DROPS,
        "source": f"{UNICORN_SOURCE_PATH}: id Npcs.UNICORN",
    },
    "black_unicorn": {
        "display_name": "Black unicorn",
        "level": 27,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "stats": {
            "hitpoints": 290,
            "attack": 21,
            "strength": 21,
            "defence": 23,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": UNICORN_DROPS,
        "source": f"{BLACK_UNICORN_SOURCE_PATH}: id Npcs.BLACK_UNICORN",
    },
    "black_bear": {
        "display_name": "Black bear",
        "level": 19,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 25.0,
        "stats": {
            "hitpoints": 250,
            "attack": 15,
            "strength": 16,
            "defence": 13,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": BLACK_BEAR_DROPS,
        "source": f"{BLACK_BEAR_SOURCE_PATH}: id Npcs.BLACK_BEAR; SlayerAssignment.BEAR level 1 xp 25.0; aggro radius 4",
    },
    "wolf": {
        "display_name": "Wolf",
        "level": 11,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 10.0,
        "stats": {
            "hitpoints": 100,
            "attack": 10,
            "strength": 10,
            "defence": 10,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": WOLF_LEVEL_11_DROPS,
        "source": f"{WOLF_LEVEL_11_SOURCE_PATH}: ids Npcs.WOLF_4414/Npcs.WOLF_11263; SlayerAssignment.WOLF level 1 xp 10.0; aggro radius 4; attackStyle STAB",
    },
    "white_wolf_level_25": {
        "display_name": "White wolf",
        "level": 25,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 34.0,
        "stats": {
            "hitpoints": 340,
            "attack": 20,
            "strength": 16,
            "defence": 22,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": WHITE_WOLF_DROPS,
        "source": f"{WHITE_WOLF_LEVEL_25_SOURCE_PATH}: ids Npcs.WHITE_WOLF/Npcs.WOLF_4413/Npcs.WOLF_6047; SlayerAssignment.WOLF level 1 xp 34.0; aggro radius 4",
    },
    "white_wolf_level_38": {
        "display_name": "White wolf",
        "level": 38,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 44.0,
        "stats": {
            "hitpoints": 440,
            "attack": 30,
            "strength": 31,
            "defence": 32,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": WHITE_WOLF_DROPS,
        "source": f"{WHITE_WOLF_LEVEL_38_SOURCE_PATH}: id Npcs.WHITE_WOLF_97; SlayerAssignment.WOLF level 1 xp 44.0; aggro radius 4",
    },
    "big_wolf": {
        "display_name": "Big wolf",
        "level": 73,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 74.0,
        "stats": {
            "hitpoints": 740,
            "attack": 60,
            "strength": 61,
            "defence": 62,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": WHITE_WOLF_DROPS,
        "source": f"{BIG_WOLF_SOURCE_PATH}: id Npcs.BIG_WOLF_6046; SlayerAssignment.WOLF level 1 xp 74.0; aggro radius 4",
    },
    "giant_bat": {
        "display_name": "Giant bat",
        "level": 27,
        "group": "Bats",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 32.0,
        "stats": {
            "hitpoints": 320,
            "attack": 22,
            "strength": 22,
            "defence": 22,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 10,
            "defence_slash": 10,
            "defence_crush": 12,
            "defence_magic": 10,
            "defence_ranged": 8,
            "melee_strength": 0,
        },
        "drops": GIANT_BAT_DROPS,
        "source": f"{GIANT_BAT_SOURCE_PATH}: id Npcs.GIANT_BAT; SlayerAssignment.BAT level 1 xp 32.0; aggro radius 4",
    },
    "hellhound": {
        "display_name": "Hellhound",
        "level": 122,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 89,
        "slayer_xp": 116.0,
        "stats": {'hitpoints': 1160, 'attack': 105, 'strength': 104, 'defence': 102, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 0,
 'defence_slash': 0,
 'defence_crush': 0,
 'defence_magic': 0,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Bones', 1),),
 'tables': ({'name': 'Main',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 690},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 50},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 50},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 10},
                       {'slots': 200})},)},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/hellhound_level_122.plugin.kts"
        ),
    },
    "goat": {
        "display_name": "Goat",
        "level": 23,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 59,
        "max_hit": 47,
        "slayer_xp": 21.0,
        "desert_context": True,
        "environmental_hazard": {
            "display_name": "Desert heat",
            "dose_items": (
                "Waterskin (4)",
                "Waterskin (3)",
                "Waterskin (2)",
                "Waterskin (1)",
            ),
            "empty_item": "Waterskin (0)",
            "reviews_per_dose": 1,
            "loadout_cap": 8,
            "source_status": (
                "period-exact Kharidian Desert heat/water requirement and dose "
                "preservation; one dose per damaging Combat review is the existing "
                "bounded review-native desert abstraction"
            ),
        },
        "stats": {
            "hitpoints": 210,
            "attack": 20,
            "strength": 20,
            "defence": 20,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1), ("Desert goat horn", 1)),
            "tables": (),
        },
        "source": (
            "https://runescape.wiki/w/Goat?oldid=5795580; "
            "https://runescape.wiki/w/Desert_goat_horn?oldid=6555637; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/goat.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/goat.json; "
            "OpenRS2 rev-742 NPC 4930 and items 9735/9736"
        ),
        "source_status": (
            "period exact level, LP, passive melee, 47-LP maximum hit, guaranteed "
            "Bones and Desert goat horn, Kharidian Desert location, and heat risk; "
            "Darkan exact combat stats and respawn; four-tick attack speed is the "
            "standard bounded combat abstraction"
        ),
    },
    "monkey": {
        "display_name": "Monkey",
        "level": 3,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 24,
        "max_hit": 20,
        "slayer_xp": 6.0,
        "stats": {
            "hitpoints": 60,
            "attack": 2,
            "strength": 2,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Monkey bones", 1),), "tables": ()},
        "source": (
            "https://runescape.wiki/w/Monkey?oldid=6552407; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/monkey (nostats).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/drops/monkey.json"
        ),
        "source_status": (
            "period LP, level, approximate max hit, Slayer XP, style, and "
            "guaranteed drop; neutral combat stats are formula-constrained to "
            "combat level 3"
        ),
    },
    "bush_snake": {
    "display_name": "Bush snake",
    "level": 35,
    "group": "Animals",
    "skill_requirements": {"woodcutting": 10},
    "quest_gate": "jungle_potion",
    "quest_gate_label": "Complete Jungle Potion",
    "required_item_options": (("Machete",),),
    "required_item_options_label": "Machete",
    "attack_style": "melee",
    "attack_speed": 7,
    "respawn_delay": 59,
    "max_hit": 38,
    # The Combat poison engine resolves 10-LP tiers, so the sourced 68-LP opening tick runs as the nearest 70-LP tier.
    "poison_damage": 7,
    "slayer_xp": 25.0,
    "stats": {
        "hitpoints": 250,
        "attack": 25,
        "strength": 25,
        "defence": 50,
        "magic": 1,
        "ranged": 1,
    },
    # PLACEHOLDER(combat.bush_snake_combat_bonuses): no period source or reconstruction states numeric attack, defence, or strength bonuses.
    "bonuses": {
        "attack_stab": 0,
        "attack_slash": 0,
        "attack_crush": 0,
        "defence_stab": 0,
        "defence_slash": 0,
        "defence_crush": 0,
        "defence_magic": 0,
        "defence_ranged": 0,
        "melee_strength": 0,
    },
    "drops": {
        "guaranteed": (("Bones", 1),),
        "tables": (
            {
                "name": "Main",
                "total": 1,
                "slots": (
                    {
                        "item": "Snake hide",
                        # PLACEHOLDER(combat.bush_snake_hide_quantity_distribution): period sources close the always-on 1-5 range but not its hidden weighting.
                        "quantity_range": (1, 5),
                        "slots": 1,
                    },
                ),
            },
        ),
    },
    "source": (
        "RuneScape Wiki Bush snake oldids 6352282 and 5190727; "
        "RuneScape Wiki Snake hide oldid 6009794; "
        "RuneScape Wiki Tai Bwo Wannai Cleanup oldid 6539724; "
        "RuneScape Wiki Jungle Potion oldid 6555418; "
        "OpenRS2 rev-742 NPCs 2489/2490 and item 6287; "
        "Darkan data/npcs/combatdefs/uncategorized/bush_snake (noanims).json @ "
        "14e49a561bab1441384022421d10dc03a8d837f0; "
        "Darkan data/npcs/drops/bush_snake.json @ "
        "c6fbe036b1743f4dd6067ec178332c69c3708856"
    ),
    "source_status": (
        "period exact identity, combat level, LP, maximum hit, 68-LP poison, "
        "seven-tick attack speed, melee style, completed-Jungle-Potion Cleanup "
        "access, Machete use, Woodcutting 10 minimum, guaranteed bones, and "
        "always-on 1-5 hide range; rev-742 exact client identities. Its "
        "attackDelay=3 is not substituted for the period attack-speed 7. Darkan "
        "reconstructed hidden combat levels and respawn. The live poison tier "
        "rounds 68 LP to 70 LP, and placeholder "
        "combat.bush_snake_hide_quantity_distribution supplies uniform weighting "
        "because Darkan's fixed quantity 1 conflicts with the period 1-5 range; "
        "combat.bush_snake_combat_bonuses supplies the zero bonus vector. "
        "The selectable target translates the period random jungle-hacking "
        "encounter without claiming an encounter frequency."
    ),
},
}
