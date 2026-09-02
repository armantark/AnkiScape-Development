from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
)
from ..contract import (
    GIANT_RAT_LEVEL_26_SOURCE_PATH,
    GIANT_RAT_LEVEL_6_SOURCE_PATH,
)

GIANT_RAT_DROPS = {"guaranteed": (("Bones", 1), ("Raw rat meat", 1)), "tables": ()}


ENEMIES = {
    "rat": {
        "display_name": "Rat",
        "level": 1,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 1,
        "stats": {
            "hitpoints": 20,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -47,
            "attack_slash": 0,
            "attack_crush": -53,
            "defence_stab": -42,
            "defence_slash": -42,
            "defence_crush": -42,
            "defence_magic": -42,
            "defence_ranged": -42,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/rat_level_1.plugin.kts"
        ),
    },
    "giant_rat": {
        "display_name": "Giant rat",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 50,
            "attack": 2,
            "strength": 3,
            "defence": 2,
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
        "drops": GIANT_RAT_DROPS,
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/giant_rat_level_2.plugin.kts"
        ),
    },
    "giant_rat_level_6": {
        "display_name": "Giant rat",
        "level": 6,
        "group": "Rats",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 100,
            "attack": 6,
            "strength": 5,
            "defence": 2,
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
        "drops": GIANT_RAT_DROPS,
        "source": f"{GIANT_RAT_LEVEL_6_SOURCE_PATH}: id Npcs.GIANT_RAT_2091",
    },
    "giant_rat_level_26": {
        "display_name": "Giant rat",
        "level": 26,
        "group": "Rats",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 250,
            "attack": 22,
            "strength": 23,
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
        "drops": GIANT_RAT_DROPS,
        "source": f"{GIANT_RAT_LEVEL_26_SOURCE_PATH}: ids Npcs.GIANT_RAT_4944/Npcs.GIANT_RAT_4945",
    },
}
