from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
)

ENEMIES = {
    "rock_crab": {
        "display_name": "Rock crab",
        "level": 13,
        "group": "Training staples",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 0,
        "slayer_xp": 51.0,
        "stats": {'hitpoints': 510, 'attack': 15, 'strength': 15, 'defence': 10, 'magic': 1, 'ranged': 1},
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
             'slots': ({'item': 'Empty oyster', 'quantity': 1, 'slots': 1},
                       {'item': 'Oyster pearl', 'quantity': 1, 'slots': 1},
                       {'item': 'Casket', 'quantity': 1, 'slots': 1},
                       {'item': 'Spinach roll', 'quantity': 1, 'slots': 1},
                       {'item': 'Seaweed', 'quantity': 1, 'slots': 1},
                       {'item': 'Edible seaweed', 'quantity': 1, 'slots': 1},
                       {'item': 'Opal bolt tips', 'quantity': 1, 'slots': 1},
                       {'item': 'Fishing bait', 'quantity': 1, 'slots': 1},
                       {'item': 'Empty oyster', 'quantity': 1, 'slots': 1},
                       {'item': 'Seaweed', 'quantity': 1, 'slots': 1},
                       {'item': 'Seaweed', 'quantity': 1, 'slots': 1},
                       {'item': 'Coins', 'quantity': 1, 'slots': 1},
                       {'item': 'Coins', 'quantity': 1, 'slots': 1},
                       {'item': 'Oyster', 'quantity': 1, 'slots': 1},
                       {'item': 'Oyster', 'quantity': 1, 'slots': 1},
                       {'item': 'Coins', 'quantity': 1, 'slots': 1})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 100},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 5},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 10},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 3},
                       {'slots': 882})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/rock_crab_lvl_13.plugin.kts"
        ),
    },
}
