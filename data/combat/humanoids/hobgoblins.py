from __future__ import annotations

from ..contract import (
    COMBAT_ALLOTMENT_SEED_DROP_TABLE,
    COMBAT_GEM_DROP_TABLE,
    COMBAT_MINOR_HERB_DROP_TABLE,
    COMBAT_UNCOMMON_SEED_DROP_TABLE,
    HOBGOBLIN_ARMED_SOURCE_PATH,
    HOBGOBLIN_UNARMED_SOURCE_PATH,
)

HOBGOBLIN_UNARMED_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 127,
            "slots": (
                {"item": "Bronze spear", "quantity": 1, "slots": 3},
                {"item": "Iron sword", "quantity": 1, "slots": 3},
                {"item": "Steel dagger", "quantity": 1, "slots": 3},
                {"item": "Iron spear", "quantity": 1, "slots": 2},
                {"item": "Steel spear", "quantity": 1, "slots": 2},
                {"item": "Steel longsword", "quantity": 1, "slots": 1},
                {"item": "Law rune", "quantity": 2, "slots": 3},
                {"item": "Water rune", "quantity": 2, "slots": 2},
                {"item": "Fire rune", "quantity": 7, "slots": 2},
                {"item": "Body rune", "quantity": 6, "slots": 2},
                {"item": "Chaos rune", "quantity": 3, "slots": 2},
                {"item": "Nature rune", "quantity": 4, "slots": 2},
                {"item": "Cosmic rune", "quantity": 2, "slots": 1},
                {"item": "Coins", "quantity": 15, "slots": 16},
                {"item": "Coins", "quantity": 28, "slots": 12},
                {"item": "Coins", "quantity": 5, "slots": 11},
                {"item": "Coins", "quantity": 62, "slots": 4},
                {"item": "Coins", "quantity": 42, "slots": 3},
                {"item": "Coins", "quantity": 1, "slots": 1},
                {"item": "Limpwurt root", "quantity": 1, "slots": 22},
                {"item": "Goblin mail", "quantity": 1, "slots": 2},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
                {"slots": 1},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 160},
                {"item": "Green charm", "quantity": 1, "slots": 6},
                {"item": "Crimson charm", "quantity": 1, "slots": 11},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 821},
            ),
        },
    ),
}


HOBGOBLIN_ARMED_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron sword", "quantity": 1, "slots": 3},
                {"item": "Steel dagger", "quantity": 1, "slots": 3},
                {"item": "Steel longsword", "quantity": 1, "slots": 1},
                {"item": "Law rune", "quantity": 2, "slots": 3},
                {"item": "Water rune", "quantity": 2, "slots": 2},
                {"item": "Fire rune", "quantity": 7, "slots": 2},
                {"item": "Body rune", "quantity": 6, "slots": 2},
                {"item": "Chaos rune", "quantity": 3, "slots": 2},
                {"item": "Nature rune", "quantity": 4, "slots": 2},
                {"item": "Cosmic rune", "quantity": 2, "slots": 2},
                {"item": "Iron javelin", "quantity": 5, "slots": 2},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_UNCOMMON_SEED_DROP_TABLE, "slots": 12},
                {"item": "Coins", "quantity": 15, "slots": 34},
                {"item": "Coins", "quantity": 5, "slots": 10},
                {"item": "Coins", "quantity": 28, "slots": 4},
                {"item": "Coins", "quantity": 62, "slots": 4},
                {"item": "Coins", "quantity": 42, "slots": 3},
                {"item": "Coins", "quantity": 1, "slots": 1},
                {"slots": 4},
                {"item": "Limpwurt root", "quantity": 1, "slots": 21},
                {"item": "Goblin mail", "quantity": 1, "slots": 2},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
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


ENEMIES = {
    "hobgoblin_unarmed": {
        "display_name": "Hobgoblin (unarmed)",
        "level": 28,
        "group": "Hobgoblins",
        "slayer_xp": 29.0,
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 290,
            "attack": 22,
            "strength": 24,
            "defence": 24,
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
        "drops": HOBGOBLIN_UNARMED_DROPS,
        "source": (
            f"{HOBGOBLIN_UNARMED_SOURCE_PATH}: ids Npcs.HOBGOBLIN/Npcs.HOBGOBLIN_2686/"
            "Npcs.HOBGOBLIN_2687; main table declares total(128), active source slots sum to 127; "
            "Charms table declares total(1024), active source slots sum to 1000; "
            "RuneScape Wiki Hobgoblin oldid 6448782 (290 LP / 29 Slayer XP)"
        ),
    },
    "hobgoblin_armed": {
        "display_name": "Hobgoblin (armed)",
        "level": 28,
        "group": "Hobgoblins",
        "slayer_xp": 49.0,
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 490,
            "attack": 33,
            "strength": 31,
            "defence": 36,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 8,
            "attack_slash": 0,
            "attack_crush": 10,
            "defence_stab": 1,
            "defence_slash": 1,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": HOBGOBLIN_ARMED_DROPS,
        "source": (
            f"{HOBGOBLIN_ARMED_SOURCE_PATH}: ids Npcs.HOBGOBLIN_2688/Npcs.HOBGOBLIN_4898; "
            "aggro radius 4; RuneScape Wiki Hobgoblin oldid 6448782 "
            "(490 LP / 49 Slayer XP)"
        ),
    },
}
