from __future__ import annotations

from ..contract import (
    COMBAT_GEM_DROP_TABLE,
    COMBAT_MINOR_HERB_DROP_TABLE,
    COMBAT_OGRE_SEED_DROP_TABLE,
    DARKAN_GEM_DROP_TABLE,
    DARKAN_HERB_DROP_TABLE,
)

OGRE_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"table": COMBAT_OGRE_SEED_DROP_TABLE, "slots": 19},
                {"slots": 109},
            ),
        },
        {
            "name": "Tertiary",
            "total": 100000,
            "slots": (
                {"item": "Long bone", "quantity": 1, "slots": 250},
                {"item": "Curved bone", "quantity": 1, "slots": 20},
                {"slots": 99730},
            ),
        },
    ),
}


DUST_DEVIL_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Darkan main",
            "total": 32768,
            "slots": (
                {"table": DARKAN_GEM_DROP_TABLE, "slots": 2816},
                {"table": DARKAN_HERB_DROP_TABLE, "slots": 4864},
                {"item": "Rune dagger", "quantity": 1, "slots": 256},
                {"item": "Red d'hide vambraces", "quantity": 1, "slots": 512},
                {"item": "Coins", "quantity": 300, "slots": 512},
                {"item": "Fire rune", "quantity": 150, "slots": 512},
                {"item": "Ugthanki kebab", "quantity": 1, "slots": 768},
                {"item": "Earth battlestaff", "quantity": 1, "slots": 256},
                {"item": "Rune arrows", "quantity": 12, "slots": 1280},
                {"item": "Coins", "quantity": 50, "slots": 256},
                {"item": "Fire rune", "quantity": 150, "slots": 2048},
                {"item": "Steel hatchet", "quantity": 1, "slots": 768},
                {"item": "Coins", "quantity": 60, "slots": 10240},
                {"item": "Fire rune", "quantity": 37, "slots": 256},
                {"item": "Soul rune", "quantity": 5, "slots": 1024},
                {"item": "Coins", "quantity": 25, "slots": 1536},
                {"item": "Mithril bar", "quantity": 1, "slots": 768},
                {"item": "Soul rune", "quantity": 2, "slots": 256},
                {"item": "Chaos rune", "quantity": 5, "slots": 1792},
                {"item": "Coins", "quantity": 15, "slots": 1792},
                {
                    "item": "Dragon chainbody",
                    "quantity": 1,
                    "slots": 1,
                    "source_item_id": 3140,
                },
                {"slots": 255},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 606,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 31},
                {"item": "Green charm", "quantity": 1, "slots": 13},
                {"item": "Crimson charm", "quantity": 1, "slots": 115},
                {"item": "Blue charm", "quantity": 1, "slots": 3},
                {"slots": 444},
            ),
        },
    ),
}


ENEMIES = {
    "ogre": {
        "display_name": "Ogre",
        "level": 53,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 59,
        "max_hit": 73,
        "slayer_xp": 60.0,
        "stats": {
            "hitpoints": 600,
            "attack": 43,
            "strength": 43,
            "defence": 43,
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
        "drops": OGRE_DROPS,
        "source": (
            "https://runescape.wiki/w/Ogre?oldid=6565807; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/ogre/"
            "ogre_(53).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/ogre.json"
        ),
        "source_status": (
            "period exact ordinary level-53 identity, LP, maximum hit, attack "
            "speed, Slayer XP, and guaranteed Big bones; Darkan exact "
            "stats, respawn, 19/128 common-seed roll, and independent long/"
            "curved-bone tertiary rolls; level-58 God Wars and level-63 Combat "
            "Training Camp variants excluded"
        ),
    },
    "jackal": {
        "display_name": "Jackal",
        "level": 21,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 59,
        "max_hit": 80,
        "slayer_xp": 27.0,
        "stats": {
            "hitpoints": 270,
            "attack": 17,
            "strength": 18,
            "defence": 15,
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
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            "https://runescape.wiki/w/Jackal?oldid=6493724; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/jackal.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/drops/jackal.json"
        ),
    },
    "dust_devil": {
        "display_name": "Dust devil",
        "level": 93,
        "group": "Slayer",
        "required_slayer_level": 65,
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 90,
        "slayer_xp": 105.0,
        "stats": {
            "hitpoints": 1050,
            "attack": 105,
            "strength": 70,
            "defence": 40,
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
        "start_equipment": {
            "slot": "head",
            "items": (
                "Face mask",
                "Masked earmuffs",
                "Slayer helmet",
                "Slayer helmet (charged)",
                "Slayer helmet (e)",
                "Full slayer helmet",
                "Full slayer helmet (charged)",
                "Full slayer helmet (e)",
            ),
            "persistent": True,
            "warning": (
                "Equip a Face mask, Masked earmuffs, or a Slayer helmet "
                "to damage Dust devils"
            ),
            "source_status": (
                "period-exact continuous damage gate; the cutoff page says "
                "unprotected players cannot damage Dust devils"
            ),
        },
        "drops": DUST_DEVIL_DROPS,
        "source": (
            "https://runescape.wiki/w/Dust_devil?oldid=6529409; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/content/skills/"
            "slayer/npcs/combat/DustDevil.java; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "dust_devil.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/dust_devil.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer gate/XP, six-tick "
            "melee, maximum hit, continuous protective-headgear damage gate, "
            "and guaranteed Bones; Darkan exact stats, respawn, one exact "
            "32,768-slot ordinary selector with nested herb/gem tables, and "
            "an emulator-exact charm selector; familiar-only Ranged attacks "
            "have no player-combat effect; defensive bonuses are source_blocked"
        ),
    },
    "crocodile": {
        "display_name": "Crocodile",
        "level": 63,
        "group": "Slayer",
        "required_slayer_level": 10,
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 59,
        "max_hit": 67,
        "slayer_xp": 62.0,
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
                "period-exact ordinary River Elid heat/water requirement and "
                "dose preservation; one dose per damaging Combat review is the "
                "existing bounded review-native desert abstraction"
            ),
        },
        "stats": {
            "hitpoints": 630,
            "attack": 53,
            "strength": 54,
            "defence": 54,
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
            "guaranteed": (("Bones", 1),),
            "tables": (),
        },
        "source": (
            "https://runescape.wiki/w/Crocodile?oldid=6529105; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/crocodile/"
            "crocodile_(63).json"
        ),
        "source_status": (
            "period exact level-63 River Elid identity, LP, Slayer gate/XP, "
            "five-tick melee, 67-LP maximum hit, guaranteed Bones, no other "
            "drops, and desert heat; Darkan exact stats and respawn; level-89 "
            "marsh variant and Darkan's merged Big-bones row excluded"
        ),
    },
    "kalphite_soldier": {
        "display_name": "Kalphite Soldier",
        "level": 85,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 80,
        "poison_damage": 5,
        "slayer_xp": 90.0,
        "stats": {
            "hitpoints": 900,
            "attack": 70,
            "strength": 70,
            "defence": 70,
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
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Coins", "quantity": 120, "slots": 40},
                        {"item": "Coins", "quantity": 40, "slots": 29},
                        {"item": "Coins", "quantity": 200, "slots": 10},
                        {"item": "Fire rune", "quantity": 60, "slots": 8},
                        {"item": "Coins", "quantity": 10, "slots": 7},
                        {"item": "Chaos rune", "quantity": 12, "slots": 5},
                        {"item": "Steel full helm", "quantity": 1, "slots": 4},
                        {"item": "Steel hatchet", "quantity": 1, "slots": 4},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 4},
                        {"item": "Steel scimitar", "quantity": 1, "slots": 3},
                        {"item": "Death rune", "quantity": 3, "slots": 3},
                        {"item": "Waterskin (4)", "quantity": 1, "slots": 3},
                        {"item": "Nature rune", "quantity": 1, "slots": 2},
                        {"item": "Rune chainbody", "quantity": 1, "slots": 1},
                        {"item": "Mithril sq shield", "quantity": 1, "slots": 1},
                        {"item": "Adamant med helm", "quantity": 1, "slots": 1},
                        {"item": "Fire rune", "quantity": 30, "slots": 1},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 1},
                        {"item": "Coins", "quantity": 450, "slots": 1},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Kalphite_Soldier?oldid=6565809; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "kalphite_soldier.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/kalphite_soldier.json"
        ),
        "source_status": (
            "period ordinary level-85 identity, LP, maximum hit, attack speed, "
            "Slayer XP, 48-LP initial poison, stab-style melee, assignment "
            "membership, and no guaranteed drop; nearest representable 50-LP "
            "poison abstraction; Darkan exact stats, respawn, and 128-slot "
            "drops; worker, guardian, and queen variants excluded"
        ),
    },
}
