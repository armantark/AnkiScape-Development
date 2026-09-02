from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
)
from ..contract import (
    DUCK_SOURCE_PATH,
)

DUCK_LAND_DROPS = {"guaranteed": (("Bones", 1),), "tables": ()}


DUCK_WATER_DROPS = {"guaranteed": (), "tables": ()}


ENEMIES = {
    "duck_land": {
        "display_name": "Duck (land)",
        "level": 1,
        "group": "Birds",
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
        "drops": DUCK_LAND_DROPS,
        "source": f"{DUCK_SOURCE_PATH}: land ids Npcs.DUCK_6113/Npcs.DRAKE",
    },
    "duck_water": {
        "display_name": "Duck (water)",
        "level": 1,
        "group": "Birds",
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
        "drops": DUCK_WATER_DROPS,
        "source": f"{DUCK_SOURCE_PATH}: water ids Npcs.DUCK/Npcs.DUCK_2693; no death drop callback",
    },
    "seagull": {
        "display_name": "Seagull",
        "level": 2,
        "group": "Coastal",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 5.0,
        "stats": {
            "hitpoints": 60,
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
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/seagull_level_2.plugin.kts"
        ),
    },
}
