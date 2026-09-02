from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
)

ENEMIES = {
    "chicken": {
        "display_name": "Chicken",
        "level": 1,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 3.0,
        "stats": {
            "hitpoints": 30,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -47,
            "attack_slash": 0,
            "attack_crush": -42,
            "defence_stab": -42,
            "defence_slash": -42,
            "defence_crush": -42,
            "defence_magic": -42,
            "defence_ranged": -42,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1), ("Raw chicken", 1)),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Feather", "quantity": 5, "slots": 64},
                        {"item": "Feather", "quantity": 15, "slots": 32},
                        {"slots": 32},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/chicken_level_1.plugin.kts"
        ),
    },
    "cow": {
        "display_name": "Cow",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 45,
        "slayer_xp": 8.0,
        "stats": {
            "hitpoints": 80,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -15,
            "attack_slash": 0,
            "attack_crush": -15,
            "defence_stab": -21,
            "defence_slash": -21,
            "defence_crush": -21,
            "defence_magic": -21,
            "defence_ranged": -21,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1), ("Raw beef", 1), ("Cowhide", 1)),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Sling", "quantity": 1, "slots": 64},
                        {"slots": 960},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 9},
                        {"item": "Green charm", "quantity": 1, "slots": 40},
                        {"item": "Crimson charm", "quantity": 1, "slots": 3},
                        {"item": "Blue charm", "quantity": 1, "slots": 1},
                        {"slots": 947},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/cow_level_2.plugin.kts"
        ),
    },
    "cow_calf": {
        "display_name": "Cow calf",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 45,
        "slayer_xp": 6.0,
        "stats": {
            "hitpoints": 60,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -20,
            "attack_slash": 0,
            "attack_crush": -20,
            "defence_stab": -26,
            "defence_slash": -26,
            "defence_crush": -26,
            "defence_magic": -26,
            "defence_ranged": -26,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1), ("Raw beef", 1), ("Cowhide", 1)), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/cow_calf_level_2.plugin.kts"
        ),
    },
    "ram": {
        "display_name": "Ram",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 45,
        "stats": {
            "hitpoints": 80,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -15,
            "attack_slash": 0,
            "attack_crush": -15,
            "defence_stab": -21,
            "defence_slash": -21,
            "defence_crush": -21,
            "defence_magic": -21,
            "defence_ranged": -21,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/ram_level_2.plugin.kts"
        ),
    },
}
