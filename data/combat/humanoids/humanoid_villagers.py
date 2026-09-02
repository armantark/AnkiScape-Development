from __future__ import annotations

from ..mechanics import (
    CHAOS_DRUID_DROP_SOURCE_PATH,
)
from ..contract import (
    CHAOS_DRUID_SOURCE_PATH,
    CITIZEN_SOURCE_PATH,
    COMBAT_ALLOTMENT_SEED_DROP_TABLE,
    COMBAT_GEM_DROP_TABLE,
    COMBAT_MINOR_HERB_DROP_TABLE,
    CUFFS_SOURCE_PATH,
    DWARF_SOURCE_PATH,
    FARMER_SOURCE_PATH,
    MONK_OF_ZAMORAK_LEVEL_45_SOURCE_PATH,
    MONK_SOURCE_PATH,
    NARF_JEFF_RUSTY_SOURCE_PATH,
    PIRATE_SOURCE_PATH,
)

FARMER_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Earth rune", "quantity": 4, "slots": 2},
                {"item": "Fire rune", "quantity": 6, "slots": 2},
                {"item": "Mind rune", "quantity": 9, "slots": 2},
                {"item": "Chaos rune", "quantity": 2, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 11},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 27},
                {"item": "Coins", "quantity": 3, "slots": 38},
                {"item": "Coins", "quantity": 25, "slots": 1},
                {"item": "Fishing bait", "quantity": 1, "slots": 5},
                {"item": "Rake", "quantity": 1, "slots": 3},
                {"item": "Earth talisman", "quantity": 1, "slots": 2},
                {"item": "Gardening boots", "quantity": 1, "slots": 2},
                {"item": "Seed dibber", "quantity": 1, "slots": 2},
                {"item": "Secateurs", "quantity": 1, "slots": 1},
                {"item": "Watering can (8)", "quantity": 1, "slots": 1},
                {"slots": 28},
            ),
        },
        {
            "name": "Tertiary",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


CHAOS_DRUID_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Law rune", "quantity": 2, "slots": 7},
                {"item": "Mithril bolts", "quantity_range": (2, 12), "slots": 5},
                {"item": "Air rune", "quantity": 36, "slots": 3},
                {"item": "Body rune", "quantity": 9, "slots": 2},
                {"item": "Earth rune", "quantity": 9, "slots": 2},
                {"item": "Mind rune", "quantity": 12, "slots": 2},
                {"item": "Nature rune", "quantity": 3, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 46},
                {"item": "Coins", "quantity": 3, "slots": 5},
                {"item": "Coins", "quantity": 8, "slots": 5},
                {"item": "Coins", "quantity": 29, "slots": 3},
                {"item": "Coins", "quantity": 35, "slots": 1},
                {"slots": 32},
                {"item": "Vial of water", "quantity": 1, "slots": 10},
                {"item": "Bronze longsword", "quantity": 1, "slots": 1},
                {"item": "Snape grass", "quantity": 1, "slots": 1},
                {"item": "Unholy mould", "quantity": 1, "slots": 1},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 1},
            ),
        },
    ),
}


LOW_LEVEL_HUMANOID_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Bronze med helm", "quantity": 1, "slots": 16},
                {"item": "Bronze dagger", "quantity": 1, "slots": 8},
                {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 138},
                {"item": "Sling", "quantity": 1, "slots": 16},
                {"item": "Bronze arrows", "quantity": 7, "slots": 24},
                {"item": "Earth rune", "quantity": 4, "slots": 16},
                {"item": "Fire rune", "quantity": 6, "slots": 16},
                {"item": "Mind rune", "quantity": 9, "slots": 16},
                {"item": "Chaos rune", "quantity": 2, "slots": 8},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 152},
                {"item": "Coins", "quantity": 3, "slots": 277},
                {"item": "Coins", "quantity": 10, "slots": 138},
                {"item": "Coins", "quantity": 5, "slots": 73},
                {"item": "Coins", "quantity": 15, "slots": 32},
                {"item": "Coins", "quantity": 25, "slots": 8},
                {"slots": 16},
                {"item": "Fishing bait", "quantity": 1, "slots": 30},
                {"item": "Copper ore", "quantity": 1, "slots": 16},
                {"item": "Earth talisman", "quantity": 1, "slots": 16},
                {"item": "Cabbage", "quantity": 1, "slots": 8},
            ),
        },
        {
            "name": "Tertiary",
            "total": 1024,
            "slots": (
                {"slots": 1016},
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8},
            ),
        },
    ),
}


PIRATE_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Iron dagger", "quantity": 1, "slots": 48},
                {"item": "Bronze scimitar", "quantity": 1, "slots": 32},
                {"item": "Iron platebody", "quantity": 1, "slots": 8},
                {"item": "Iron bolts", "quantity_range": (2, 12), "slots": 80},
                {"item": "Chaos rune", "quantity": 2, "slots": 48},
                {"item": "Nature rune", "quantity": 2, "slots": 40},
                {"item": "Bronze arrows", "quantity": 9, "slots": 24},
                {"item": "Bronze arrows", "quantity": 12, "slots": 16},
                {"item": "Air rune", "quantity": 10, "slots": 16},
                {"item": "Earth rune", "quantity": 9, "slots": 16},
                {"item": "Fire rune", "quantity": 5, "slots": 16},
                {"item": "Law rune", "quantity": 2, "slots": 8},
                {"item": "Coins", "quantity": 4, "slots": 232},
                {"item": "Coins", "quantity": 25, "slots": 104},
                {"item": "Coins", "quantity": 7, "slots": 64},
                {"item": "Coins", "quantity": 12, "slots": 48},
                {"item": "Coins", "quantity": 35, "slots": 32},
                {"item": "Coins", "quantity": 55, "slots": 8},
                {"item": "Eye patch", "quantity": 1, "slots": 96},
                {"slots": 64},
                {"item": "Chef's hat", "quantity": 1, "slots": 8},
                {"item": "Iron bar", "quantity": 1, "slots": 8},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 8},
            ),
        },
    ),
}


MONK_OF_ZAMORAK_LEVEL_45_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 20,
            "slots": (
                {"item": "Zamorak robe top", "quantity": 1, "slots": 1},
                {"item": "Zamorak robe bottom", "quantity": 1, "slots": 1},
                {"slots": 18},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 10},
                {"item": "Green charm", "quantity": 1, "slots": 100},
                {"item": "Crimson charm", "quantity": 1, "slots": 20},
                {"item": "Blue charm", "quantity": 1, "slots": 10},
                {"slots": 860},
            ),
        },
    ),
}


DWARF_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Bronze pickaxe", "quantity": 1, "slots": 13},
                {"item": "Bronze med helm", "quantity": 1, "slots": 4},
                {"item": "Bronze battleaxe", "quantity": 1, "slots": 2},
                {"item": "Iron battleaxe", "quantity": 1, "slots": 1},
                {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 7},
                {"item": "Chaos rune", "quantity": 2, "slots": 4},
                {"item": "Nature rune", "quantity": 2, "slots": 4},
                {"item": "Coins", "quantity": 4, "slots": 20},
                {"item": "Coins", "quantity": 10, "slots": 15},
                {"item": "Coins", "quantity": 30, "slots": 2},
                {"item": "Hammer", "quantity": 1, "slots": 10},
                {"item": "Bronze bar", "quantity": 1, "slots": 7},
                {"item": "Iron ore", "quantity": 1, "slots": 4},
                {"item": "Tin ore", "quantity": 1, "slots": 3},
                {"item": "Copper ore", "quantity": 1, "slots": 3},
                {"item": "Iron bar", "quantity": 1, "slots": 3},
                {"item": "Coal", "quantity": 1, "slots": 2},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 1},
                {"slots": 23},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 40},
                {"item": "Green charm", "quantity": 1, "slots": 20},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 7},
                {"slots": 903},
            ),
        },
        {
            "name": "Tertiary",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


ENEMIES = {
    "farmer": {
        "display_name": "Farmer",
        "level": 7,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 120,
            "attack": 3,
            "strength": 4,
            "defence": 8,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 6,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": FARMER_DROPS,
        "source": f"{FARMER_SOURCE_PATH}: ids FARMER/FARMER_1757/FARMER_1758",
    },
    "chaos_druid": {
        "display_name": "Chaos druid",
        "level": 13,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 200,
            "attack": 8,
            "strength": 8,
            "defence": 12,
            "magic": 10,
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
        "drops": CHAOS_DRUID_DROPS,
        "source": (
            f"{CHAOS_DRUID_SOURCE_PATH}: ids Npcs.CHAOS_DRUID_2547/Npcs.CHAOS_DRUID/"
            "Npcs.CHAOS_DRUID_7105; aggro radius 4; "
            f"{CHAOS_DRUID_DROP_SOURCE_PATH}: item 1594 at 1/128; "
            "RuneScape Wiki Chaos druid oldid 6381798"
        ),
    },
    "citizen": {
        "display_name": "Man/Woman",
        "level": 2,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 70,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": -21,
            "defence_slash": -21,
            "defence_crush": -21,
            "defence_magic": -21,
            "defence_ranged": -21,
            "melee_strength": 0,
        },
        "drops": LOW_LEVEL_HUMANOID_DROPS,
        "source": (
            f"{CITIZEN_SOURCE_PATH}: ids Npcs.MAN/Npcs.MAN_2/Npcs.MAN_3/Npcs.MAN_24/"
            "Npcs.WOMAN_BRUNETTE_LONGSKIRT_4/Npcs.WOMAN_BRUNETTE_PONYTAIL_5/"
            "Npcs.WOMAN_WOMAN_BLOND_PONYTAIL_6/Npcs.MAN_16/Npcs.MAN_3223/"
            "Npcs.WOMAN_BLOND_LONGSKIRT_3226"
        ),
    },
    "monk": {
        "display_name": "Monk",
        "level": 5,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 150,
            "attack": 2,
            "strength": 2,
            "defence": 3,
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
        "source": f"{MONK_SOURCE_PATH}: id Npcs.MONK_7727",
    },
    "cuffs": {
        "display_name": "Cuffs",
        "level": 3,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 70,
            "attack": 1,
            "strength": 1,
            "defence": 3,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 5,
            "defence_magic": 5,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": LOW_LEVEL_HUMANOID_DROPS,
        "source": f"{CUFFS_SOURCE_PATH}: id Npcs.CUFFS",
    },
    "narf_jeff_rusty": {
        "display_name": "Narf/Jeff/Rusty",
        "level": 2,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 70,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 5,
            "defence_magic": 5,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": LOW_LEVEL_HUMANOID_DROPS,
        "source": f"{NARF_JEFF_RUSTY_SOURCE_PATH}: ids Npcs.NARF/Npcs.JEFF/Npcs.RUSTY",
    },
    "pirate": {
        "display_name": "Pirate",
        "level": 23,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 200,
            "attack": 21,
            "strength": 21,
            "defence": 21,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 8,
            "attack_slash": 8,
            "attack_crush": 8,
            "defence_stab": 3,
            "defence_slash": 2,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 10,
        },
        "drops": PIRATE_DROPS,
        "source": (
            f"{PIRATE_SOURCE_PATH}: ids Npcs.PIRATE/Npcs.PIRATE_183/Npcs.PIRATE_184; "
            "source attackBonus/strengthBonus mapped to melee attack/strength bonuses"
        ),
    },
    "monk_of_zamorak_level_45": {
        "display_name": "Monk of Zamorak",
        "level": 45,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 250,
        "stats": {
            "hitpoints": 400,
            "attack": 38,
            "strength": 38,
            "defence": 42,
            "magic": 40,
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
        "drops": MONK_OF_ZAMORAK_LEVEL_45_DROPS,
        "source": (
            f"{MONK_OF_ZAMORAK_LEVEL_45_SOURCE_PATH}: id Npcs.MONK_OF_ZAMORAK_190; "
            "Items.ZAMORAK_ROBE_1035 mapped to Zamorak robe top, "
            "Items.ZAMORAK_ROBE mapped to Zamorak robe bottom; aggro radius 4"
        ),
    },
    "dwarf_level_10": {
        "display_name": "Dwarf (level 10)",
        "level": 10,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 50,
        "slayer_xp": 16.0,
        "stats": {
            "hitpoints": 160,
            "attack": 8,
            "strength": 8,
            "defence": 6,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 5,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": DWARF_DROPS,
        "source": f"{DWARF_SOURCE_PATH}: idsLevel10 Npcs.DWARF_118/Npcs.DWARF_3221/Npcs.DWARF_3272",
    },
    "dwarf_level_11": {
        "display_name": "Dwarf (level 11)",
        "level": 11,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 16.0,
        "stats": {
            "hitpoints": 180,
            "attack": 8,
            "strength": 8,
            "defence": 8,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 5,
            "defence_ranged": 10,
            "melee_strength": 0,
        },
        "drops": DWARF_DROPS,
        "source": (
            f"{DWARF_SOURCE_PATH}: idsLevel11 Npcs.DWARF_3219/Npcs.DWARF_3220/"
            "Npcs.DWARF_3268/Npcs.DWARF_3269/Npcs.DWARF_3270"
        ),
    },
}
