from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
)

ENEMIES = {
    "barbarian": {
        "display_name": "Barbarian",
        "level": 8,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 140,
            "attack": 6,
            "strength": 5,
            "defence": 5,
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
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze hatchet", "quantity": 1, "slots": 48},
                        {"item": "Staff", "quantity": 1, "slots": 32},
                        {"item": "Iron mace", "quantity": 1, "slots": 8},
                        {"item": "Chaos rune", "quantity": 2, "slots": 32},
                        {"item": "Bronze arrows", "quantity": 15, "slots": 24},
                        {"item": "Earth rune", "quantity": 2, "slots": 24},
                        {"item": "Fire rune", "quantity": 5, "slots": 16},
                        {"item": "Mind rune", "quantity": 5, "slots": 16},
                        {"item": "Law rune", "quantity": 2, "slots": 8},
                        {"item": "Coins", "quantity": 5, "slots": 341},
                        {"item": "Coins", "quantity": 8, "slots": 76},
                        {"item": "Coins", "quantity": 17, "slots": 45},
                        {"item": "Coins", "quantity": 27, "slots": 26},
                        {"slots": 288},
                        {"item": "Tin ore", "quantity": 1, "slots": 8},
                        {"item": "Bear fur", "quantity": 1, "slots": 8},
                        {"item": "Beer", "quantity": 1, "slots": 8},
                        {"item": "Cooked meat", "quantity": 1, "slots": 8},
                        {"item": "Ring mould", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 50},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 5},
                        {"item": "Blue charm", "quantity": 1, "slots": 5},
                        {"slots": 930},
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
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_lvl_8.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_lvl_9.plugin.kts"
        ),
    },
    "barbarian_level_10": {
        "display_name": "Barbarian",
        "level": 10,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 180,
            "attack": 8,
            "strength": 7,
            "defence": 3,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 9,
            "attack_slash": 0,
            "attack_crush": 15,
            "defence_stab": 0,
            "defence_slash": 3,
            "defence_crush": 2,
            "defence_magic": -3,
            "defence_ranged": 2,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze hatchet", "quantity": 1, "slots": 48},
                        {"item": "Staff", "quantity": 1, "slots": 32},
                        {"item": "Iron mace", "quantity": 1, "slots": 8},
                        {"item": "Chaos rune", "quantity": 2, "slots": 32},
                        {"item": "Bronze arrows", "quantity": 15, "slots": 24},
                        {"item": "Earth rune", "quantity": 2, "slots": 24},
                        {"item": "Fire rune", "quantity": 5, "slots": 16},
                        {"item": "Mind rune", "quantity": 5, "slots": 16},
                        {"item": "Law rune", "quantity": 2, "slots": 8},
                        {"item": "Coins", "quantity": 5, "slots": 341},
                        {"item": "Coins", "quantity": 8, "slots": 76},
                        {"item": "Coins", "quantity": 17, "slots": 45},
                        {"item": "Coins", "quantity": 27, "slots": 26},
                        {"slots": 288},
                        {"item": "Tin ore", "quantity": 1, "slots": 8},
                        {"item": "Bear fur", "quantity": 1, "slots": 8},
                        {"item": "Beer", "quantity": 1, "slots": 8},
                        {"item": "Cooked meat", "quantity": 1, "slots": 8},
                        {"item": "Ring mould", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 50},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 5},
                        {"item": "Blue charm", "quantity": 1, "slots": 5},
                        {"slots": 930},
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
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_greataxe_lvl_10.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_spear_lvl_10.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_twohand_sword_lvl_10.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_2hsword_lvl_10.plugin.kts"
        ),
    },
    "barbarian_level_17": {
        "display_name": "Barbarian",
        "level": 17,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 240,
            "attack": 15,
            "strength": 14,
            "defence": 10,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 9,
            "attack_slash": 0,
            "attack_crush": 15,
            "defence_stab": 0,
            "defence_slash": 3,
            "defence_crush": 2,
            "defence_magic": -3,
            "defence_ranged": 2,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze hatchet", "quantity": 1, "slots": 48},
                        {"item": "Staff", "quantity": 1, "slots": 32},
                        {"item": "Iron mace", "quantity": 1, "slots": 8},
                        {"item": "Chaos rune", "quantity": 2, "slots": 32},
                        {"item": "Bronze arrows", "quantity": 15, "slots": 24},
                        {"item": "Earth rune", "quantity": 2, "slots": 24},
                        {"item": "Fire rune", "quantity": 5, "slots": 16},
                        {"item": "Mind rune", "quantity": 5, "slots": 16},
                        {"item": "Law rune", "quantity": 2, "slots": 8},
                        {"item": "Coins", "quantity": 5, "slots": 341},
                        {"item": "Coins", "quantity": 8, "slots": 76},
                        {"item": "Coins", "quantity": 17, "slots": 45},
                        {"item": "Coins", "quantity": 27, "slots": 26},
                        {"slots": 288},
                        {"item": "Tin ore", "quantity": 1, "slots": 8},
                        {"item": "Bear fur", "quantity": 1, "slots": 8},
                        {"item": "Beer", "quantity": 1, "slots": 8},
                        {"item": "Cooked meat", "quantity": 1, "slots": 8},
                        {"item": "Ring mould", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 50},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 5},
                        {"item": "Blue charm", "quantity": 1, "slots": 5},
                        {"slots": 930},
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
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_greataxe_lvl_17.plugin.kts: "
            "ids Npcs.BARBARIAN/Npcs.BARBARIAN_3248; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_spear_lvl_17.plugin.kts: "
            "id Npcs.BARBARIAN_3260; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_twohand_sword_lvl_17.plugin.kts: "
            "id Npcs.BARBARIAN_3249"
        ),
    },
}
