from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
)
from ..contract import (
    TZHAAR_KET_SOURCE_PATH,
)

TZHAAR_KET_DROPS = {
    "guaranteed": (),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Tokkul", "quantity_range": (100, 2000), "slots": 69},
                {"item": "Fire battlestaff", "quantity": 1, "slots": 1},
                {"item": "Super strength (1)", "quantity": 1, "slots": 4},
                {"item": "Super defence (1)", "quantity": 1, "slots": 4},
                {"item": "Uncut sapphire", "quantity": 1, "slots": 12},
                {"item": "Uncut emerald", "quantity": 1, "slots": 12},
                {"item": "Uncut ruby", "quantity": 1, "slots": 6},
                {"item": "Uncut diamond", "quantity": 1, "slots": 6},
                {"item": "Lobster", "quantity": 1, "slots": 6},
                {"item": "Chilli potato", "quantity": 1, "slots": 6},
                {"item": "Pure essence", "quantity_range": (5, 10), "slots": 1},
                {"item": "Onyx bolt tips", "quantity_range": (1, 4), "slots": 1},
            ),
        },
        {
            "name": "Obsidian",
            "total": 512,
            "slots": (
                {"item": "Tzhaar-ket-om", "quantity": 1, "slots": 1},
                {"item": "Toktz-ket-xil", "quantity": 1, "slots": 1},
                {"item": "Obsidian cape", "quantity": 1, "slots": 1},
                {"slots": 509},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Obsidian charm", "quantity": 2, "slots": 720},
                {"slots": 280},
            ),
        },
    ),
}


ENEMIES = {
    "tzhaar_ket": {
        "display_name": "TzHaar-Ket",
        "level": 149,
        "group": "TzHaar",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 136.0,
        "stats": {
            "hitpoints": 1400,
            "attack": 120,
            "strength": 140,
            "defence": 120,
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
        "drops": TZHAAR_KET_DROPS,
        "source": (
            f"{TZHAAR_KET_SOURCE_PATH}: id Npcs.TZHAARKET_2616; "
            "pre-death sound only; no source combat bonuses; "
            "RuneScape Wiki Kuradal oldid 6588106 (level 149, 136 Slayer XP)"
        ),
    },
    "tzhaar_hur": {
        "display_name": "TzHaar-Hur",
        "level": 74,
        "group": "TzHaar",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 50,
        "slayer_xp": 80.0,
        "stats": {'hitpoints': 800, 'attack': 60, 'strength': 60, 'defence': 60, 'magic': 80, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 0,
 'defence_slash': 0,
 'defence_crush': 0,
 'defence_magic': 0,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (),
 'tables': ({'name': 'Main',
             'total': 128,
             'slots': ({'item': 'Tokkul', 'quantity_range': (150, 800), 'slots': 32},
                       {'item': 'Gold ore', 'quantity': 1, 'slots': 12},
                       {'item': 'Silver ore', 'quantity_range': (1, 2), 'slots': 11},
                       {'item': 'Soft clay', 'quantity': 3, 'slots': 8},
                       {'item': 'Steel bar', 'quantity': 1, 'slots': 8},
                       {'item': 'Onyx bolt tips', 'quantity': 1, 'slots': 2},
                       {'item': 'Molten glass', 'quantity': 2, 'slots': 6},
                       {'item': 'Battlestaff', 'quantity': 1, 'slots': 6},
                       {'item': 'Hard leather', 'quantity': 1, 'slots': 6},
                       {'item': 'Leather', 'quantity': 3, 'slots': 6},
                       {'item': 'Wool', 'quantity': 8, 'slots': 6},
                       {'item': 'Flax', 'quantity_range': (5, 10), 'slots': 6},
                       {'item': 'Pure essence', 'quantity_range': (4, 6), 'slots': 6},
                       {'item': 'Lobster', 'quantity': 1, 'slots': 6},
                       {'item': 'Super attack (1)', 'quantity': 1, 'slots': 3},
                       {'item': 'Super strength (1)', 'quantity': 1, 'slots': 3})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Obsidian charm', 'quantity': 1, 'slots': 360},
                       {'item': 'Obsidian charm', 'quantity': 2, 'slots': 360},
                       {'slots': 280})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/tzhaar_hur_lvl_74.plugin.kts"
        ),
    },
}
