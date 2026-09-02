from __future__ import annotations

from ..contract import (
    COMBAT_ALLOTMENT_SEED_DROP_TABLE,
    COMBAT_GEM_DROP_TABLE,
    COMBAT_MINOR_HERB_DROP_TABLE,
    COMBAT_UNCOMMON_SEED_DROP_TABLE,
    DARKAN_GEM_DROP_TABLE,
    DARKAN_HERB_DROP_TABLE,
    DARKAN_STANDARD_RARE_DROP_TABLE,
    HILL_GIANT_SOURCE_PATH,
    ICE_GIANT_SOURCE_PATH,
    MOSS_GIANT_SOURCE_PATH,
)

HILL_GIANT_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron full helm", "quantity": 1, "slots": 4},
                {"item": "Iron dagger", "quantity": 1, "slots": 5},
                {"item": "Iron kiteshield", "quantity": 1, "slots": 3},
                {"item": "Steel longsword", "quantity": 1, "slots": 2},
                {"item": "Iron arrows", "quantity": 3, "slots": 6},
                {"item": "Fire rune", "quantity": 15, "slots": 3},
                {"item": "Water rune", "quantity": 7, "slots": 3},
                {"item": "Law rune", "quantity": 2, "slots": 3},
                {"item": "Steel arrows", "quantity": 10, "slots": 2},
                {"item": "Mind rune", "quantity": 3, "slots": 2},
                {"item": "Cosmic rune", "quantity": 2, "slots": 2},
                {"item": "Nature rune", "quantity": 6, "slots": 2},
                {"item": "Chaos rune", "quantity": 2, "slots": 1},
                {"item": "Death rune", "quantity": 2, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                {"item": "Coins", "quantity": 38, "slots": 15},
                {"item": "Coins", "quantity": 52, "slots": 10},
                {"item": "Coins", "quantity": 15, "slots": 8},
                {"item": "Coins", "quantity": 7, "slots": 6},
                {"item": "Coins", "quantity": 88, "slots": 2},
                {"slots": 1},
                {"item": "Limpwurt root", "quantity": 1, "slots": 11},
                {"item": "Beer", "quantity": 1, "slots": 6},
                {"item": "Body talisman", "quantity": 1, "slots": 2},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 3},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 150},
                {"item": "Green charm", "quantity": 1, "slots": 10},
                {"item": "Crimson charm", "quantity": 1, "slots": 10},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 828},
            ),
        },
    ),
}


MOSS_GIANT_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Black sq shield", "quantity": 1, "slots": 5},
                {"item": "Magic staff", "quantity": 1, "slots": 2},
                {"item": "Steel med helm", "quantity": 1, "slots": 2},
                {"item": "Mithril sword", "quantity": 1, "slots": 2},
                {"item": "Mithril spear", "quantity": 1, "slots": 2},
                {"item": "Steel kiteshield", "quantity": 1, "slots": 1},
                {"item": "Law rune", "quantity": 3, "slots": 4},
                {"item": "Air rune", "quantity": 18, "slots": 3},
                {"item": "Earth rune", "quantity": 27, "slots": 3},
                {"item": "Chaos rune", "quantity": 7, "slots": 3},
                {"item": "Nature rune", "quantity": 6, "slots": 3},
                {"item": "Cosmic rune", "quantity": 3, "slots": 2},
                {"item": "Iron arrows", "quantity": 15, "slots": 2},
                {"item": "Steel arrows", "quantity": 30, "slots": 1},
                {"item": "Death rune", "quantity": 3, "slots": 1},
                {"item": "Blood rune", "quantity": 1, "slots": 1},
                {"item": "Coins", "quantity": 37, "slots": 19},
                {"item": "Coins", "quantity": 2, "slots": 8},
                {"item": "Coins", "quantity": 119, "slots": 10},
                {"item": "Coins", "quantity": 300, "slots": 2},
                {"item": "Steel bar", "quantity": 1, "slots": 6},
                {"item": "Coal", "quantity": 1, "slots": 1},
                {"item": "Spinach roll", "quantity": 1, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 5},
                {"table": COMBAT_UNCOMMON_SEED_DROP_TABLE, "slots": 35},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 4},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 360},
                {"item": "Green charm", "quantity": 1, "slots": 30},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 7},
                {"slots": 573},
            ),
        },
    ),
}


ICE_GIANT_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Iron 2h sword", "quantity": 1, "slots": 40},
                {"item": "Black kiteshield", "quantity": 1, "slots": 32},
                {"item": "Steel hatchet", "quantity": 1, "slots": 32},
                {"item": "Steel sword", "quantity": 1, "slots": 32},
                {"item": "Iron platelegs", "quantity": 1, "slots": 8},
                {"item": "Mithril mace", "quantity": 1, "slots": 8},
                {"item": "Mithril sq shield", "quantity": 1, "slots": 8},
                {"item": "Adamant arrows", "quantity": 5, "slots": 48},
                {"item": "Nature rune", "quantity": 6, "slots": 32},
                {"item": "Mind rune", "quantity": 24, "slots": 24},
                {"item": "Body rune", "quantity": 37, "slots": 24},
                {"item": "Law rune", "quantity": 3, "slots": 16},
                {"item": "Water rune", "quantity": 12, "slots": 8},
                {"item": "Cosmic rune", "quantity": 4, "slots": 8},
                {"item": "Death rune", "quantity": 3, "slots": 8},
                {"item": "Blood rune", "quantity": 2, "slots": 8},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 64},
                {"item": "Coins", "quantity": 117, "slots": 224},
                {"item": "Coins", "quantity": 53, "slots": 76},
                {"item": "Coins", "quantity": 196, "slots": 72},
                {"item": "Coins", "quantity": 5, "slots": 64},
                {"item": "Coins", "quantity": 8, "slots": 54},
                {"item": "Coins", "quantity": 2, "slots": 48},
                {"item": "Coins", "quantity": 400, "slots": 16},
                {"item": "Jug of wine", "quantity": 1, "slots": 24},
                {"item": "Mithril ore", "quantity": 1, "slots": 8},
                {"item": "Banana", "quantity": 1, "slots": 8},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 32},
            ),
        },
        {
            "name": "Tertiary",
            "total": 100000,
            "slots": (
                {"item": "Long bone", "quantity": 1, "slots": 250},
                {"item": "Curved bone", "quantity": 1, "slots": 20},
                {"item": "Champion's scroll", "quantity": 1, "slots": 20},
                {"slots": 99710},
            ),
        },
    ),
}


FIRE_GIANT_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 128,
            "slots": (
                {"item": "Coins", "quantity": 60, "slots": 40},
                {"table": DARKAN_HERB_DROP_TABLE, "slots": 19},
                {"table": DARKAN_GEM_DROP_TABLE, "slots": 11},
                {"item": "Fire rune", "quantity": 150, "slots": 10},
                {"item": "Chaos rune", "quantity": 5, "slots": 7},
                {"item": "Coins", "quantity": 15, "slots": 7},
                {"item": "Coins", "quantity": 25, "slots": 6},
                {"item": "Rune arrows", "quantity": 12, "slots": 5},
                {"item": "Blood rune", "quantity": 5, "slots": 4},
                {"item": "Steel hatchet", "quantity": 1, "slots": 3},
                {"item": "Lobster", "quantity": 1, "slots": 3},
                {"item": "Mithril sq shield", "quantity": 1, "slots": 2},
                {"item": "Coins", "quantity": 300, "slots": 2},
                {"item": "Steel bar", "quantity": 1, "slots": 2},
                {"item": "Fire battlestaff", "quantity": 1, "slots": 1},
                {"item": "Rune scimitar", "quantity": 1, "slots": 1},
                {"item": "Fire rune", "quantity": 37, "slots": 1},
                {"item": "Law rune", "quantity": 2, "slots": 1},
                {"item": "Coins", "quantity": 50, "slots": 1},
                {"item": "Strength potion (2)", "quantity": 1, "slots": 1},
                {"table": DARKAN_STANDARD_RARE_DROP_TABLE, "slots": 1},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 404,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 207},
                {"item": "Green charm", "quantity": 1, "slots": 11},
                {"item": "Crimson charm", "quantity": 1, "slots": 7},
                {"item": "Blue charm", "quantity": 1, "slots": 3},
                {"slots": 176},
            ),
        },
        {
            "name": "Long and curved bones",
            "total": 100000,
            "slots": (
                {"item": "Long bone", "quantity": 1, "slots": 250},
                {"item": "Curved bone", "quantity": 1, "slots": 20},
                {"slots": 99730},
            ),
        },
    ),
}


ENEMIES = {
    "hill_giant": {
        "display_name": "Hill giant",
        "level": 28,
        "group": "Giants",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 30,
        "slayer_xp": 35.0,
        "stats": {
            "hitpoints": 350,
            "attack": 18,
            "strength": 22,
            "defence": 26,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 18,
            "attack_slash": 0,
            "attack_crush": 16,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": HILL_GIANT_DROPS,
        "source": (
            f"{HILL_GIANT_SOURCE_PATH}: id Npcs.HILL_GIANT; "
            "SlayerAssignment.HILL_GIANT level 1 xp 35.0; attackStyle CRUSH; aggro radius 4"
        ),
    },
    "moss_giant": {
        "display_name": "Moss giant",
        "level": 42,
        "group": "Giants",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 30,
        "slayer_xp": 60.0,
        "stats": {
            "hitpoints": 600,
            "attack": 30,
            "strength": 30,
            "defence": 30,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 33,
            "attack_slash": 0,
            "attack_crush": 31,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": MOSS_GIANT_DROPS,
        "source": (
            f"{MOSS_GIANT_SOURCE_PATH}: ids Npcs.MOSS_GIANT/Npcs.MOSS_GIANT_1587/"
            "Npcs.MOSS_GIANT_1588/Npcs.MOSS_GIANT_4688; SlayerAssignment.MOSS_GIANT level 1 "
            "xp 60.0; attackStyle CRUSH; aggro radius 4"
        ),
    },
    "ice_giant": {
        "display_name": "Ice giant",
        "level": 53,
        "group": "Giants",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 30,
        "slayer_xp": 70.0,
        "stats": {
            "hitpoints": 700,
            "attack": 40,
            "strength": 40,
            "defence": 40,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 29,
            "attack_slash": 29,
            "attack_crush": 29,
            "defence_stab": 0,
            "defence_slash": 3,
            "defence_crush": 2,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 31,
        },
        "drops": ICE_GIANT_DROPS,
        "source": (
            f"{ICE_GIANT_SOURCE_PATH}: ids Npcs.ICE_GIANT/Npcs.ICE_GIANT_3072/Npcs.ICE_GIANT_4685/"
            "Npcs.ICE_GIANT_4686/Npcs.ICE_GIANT_4687; SlayerAssignment.ICE_GIANT level 1 "
            "xp 70.0; attackStyle SLASH; attackBonus/strengthBonus; aggro radius 5"
        ),
    },
    "fire_giant": {
        "display_name": "Fire giant",
        "level": 86,
        "group": "Giants",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 59,
        "max_hit": 116,
        "slayer_xp": 111.0,
        "stats": {
            "hitpoints": 1110,
            "attack": 65,
            "strength": 65,
            "defence": 65,
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
        "drops": FIRE_GIANT_DROPS,
        "source": (
            "https://runescape.wiki/w/Fire_giant?oldid=6555306; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/fire_giant/"
            "fire_giant_(86).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/fire_giant.json"
        ),
        "source_status": (
            "period exact ordinary non-Daemonheim level, LP, Slayer XP, melee "
            "style, five-tick attack speed, poison susceptibility, maximum hit, "
            "and guaranteed Big bones; Darkan exact stats, 59-tick respawn, "
            "128-slot ordinary selector, nested tables, independent exact charm "
            "selector, and long/curved-bone tertiaries; location-only quest, "
            "Wilderness, Smoke Dungeon, and Dungeoneering contexts excluded"
        ),
    },
}
