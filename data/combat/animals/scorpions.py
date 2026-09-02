from __future__ import annotations

from ..contract import (
    KING_SCORPION_SOURCE_PATH,
    PIT_SCORPION_SOURCE_PATH,
    POISON_SCORPION_SOURCE_PATH,
    SCORPION_LEVEL_14_SOURCE_PATH,
    SCORPION_LEVEL_59_SOURCE_PATH,
)

SCORPION_CHARM_DROPS = {
    "guaranteed": (),
    "tables": (
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 30},
                {"item": "Green charm", "quantity": 1, "slots": 70},
                {"item": "Crimson charm", "quantity": 1, "slots": 10},
                {"item": "Blue charm", "quantity": 1, "slots": 5},
                {"slots": 885},
            ),
        },
    ),
}


ENEMIES = {
    "poison_scorpion": {
        "display_name": "Poison scorpion",
        "level": 20,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "poison_damage": 3,
        "slayer_xp": 23.0,
        "stats": {
            "hitpoints": 230,
            "attack": 16,
            "strength": 17,
            "defence": 15,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 15,
            "defence_crush": 15,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (), "tables": ()},
        "source": f"{POISON_SCORPION_SOURCE_PATH}: Npcs.POISON_SCORPION poisonDamage=3; no DropTableFactory registration",
    },
    "scorpion": {
        "display_name": "Scorpion",
        "level": 14,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 17.0,
        "stats": {
            "hitpoints": 170,
            "attack": 11,
            "strength": 12,
            "defence": 11,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 15,
            "defence_crush": 15,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": SCORPION_CHARM_DROPS,
        "source": SCORPION_LEVEL_14_SOURCE_PATH,
    },
    "king_scorpion": {
        "display_name": "King scorpion",
        "level": 32,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 37.0,
        "stats": {
            "hitpoints": 300,
            "attack": 30,
            "strength": 29,
            "defence": 23,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 15,
            "defence_crush": 15,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (), "tables": ()},
        "source": (
            f"{KING_SCORPION_SOURCE_PATH}: Npcs.KING_SCORPION; "
            "SlayerAssignment.SCORPION level 1 xp 37.0; no DropTableFactory registration; aggro radius 4"
        ),
    },
    "pit_scorpion": {
        "display_name": "Pit scorpion",
        "level": 28,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 32.0,
        "stats": {
            "hitpoints": 320,
            "attack": 20,
            "strength": 25,
            "defence": 28,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 13,
            "defence_crush": 13,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (), "tables": ()},
        "source": (
            f"{PIT_SCORPION_SOURCE_PATH}: Npcs.PIT_SCORPION; "
            "SlayerAssignment.SCORPION level 1 xp 32.0; no DropTableFactory registration; aggro radius 4"
        ),
    },
    "scorpion_level_59": {
        "display_name": "Scorpion",
        "level": 59,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 22,
        "slayer_xp": 55.0,
        "stats": {
            "hitpoints": 550,
            "attack": 50,
            "strength": 52,
            "defence": 50,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 15,
            "defence_crush": 15,
            "defence_magic": 0,
            "defence_ranged": 55,
            "melee_strength": 0,
        },
        "drops": SCORPION_CHARM_DROPS,
        "source": (
            f"{SCORPION_LEVEL_59_SOURCE_PATH}: ids Npcs.SCORPION_4402/Npcs.SCORPION_4403; "
            "SlayerAssignment.SCORPION level 1 xp 55.0; aggro radius 4"
        ),
    },
}
