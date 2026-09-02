from __future__ import annotations

from ..mechanics import (
    DRAGONFIRE_FORMULA_SOURCE_PATH,
)
from ..contract import (
    DARKAN_GEM_DROP_TABLE,
    DARKAN_STANDARD_RARE_DROP_TABLE,
)

BRONZE_DRAGON_DROPS = {
    "guaranteed": (("Dragon bones", 1), ("Bronze bar", 5)),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 128,
            "slots": (
                {"item": "Coins", "quantity": 196, "slots": 39},
                {"item": "Adamant javelin", "quantity": 30, "slots": 20},
                {"item": "Coins", "quantity": 330, "slots": 10},
                {"item": "Fire rune", "quantity": 50, "slots": 8},
                {"item": "Adamant dart (p)", "quantity": 16, "slots": 7},
                {
                    "item": "Mithril bolts",
                    "quantity_range": (2, 12),
                    "slots": 6,
                },
                {"item": "Law rune", "quantity": 10, "slots": 5},
                {"item": "Mithril 2h sword", "quantity": 1, "slots": 4},
                {"table": DARKAN_GEM_DROP_TABLE, "slots": 4},
                {"item": "Mithril hatchet", "quantity": 1, "slots": 3},
                {"item": "Mithril battleaxe", "quantity": 1, "slots": 3},
                {"item": "Rune knife", "quantity": 2, "slots": 3},
                {"item": "Blood rune", "quantity": 15, "slots": 3},
                {"item": "Adamant bar", "quantity": 1, "slots": 3},
                {"item": "Swordfish", "quantity": 2, "slots": 2},
                {"item": "Mithril kiteshield", "quantity": 1, "slots": 1},
                {"item": "Adamant platebody", "quantity": 1, "slots": 1},
                {"item": "Rune longsword", "quantity": 1, "slots": 1},
                {"item": "Death rune", "quantity": 25, "slots": 1},
                {"item": "Coins", "quantity": 690, "slots": 1},
                {"item": "Swordfish", "quantity": 1, "slots": 1},
                {"table": DARKAN_STANDARD_RARE_DROP_TABLE, "slots": 1},
                {"slots": 1},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 1212,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 60},
                {"item": "Green charm", "quantity": 1, "slots": 264},
                {"item": "Crimson charm", "quantity": 1, "slots": 48},
                {"item": "Blue charm", "quantity": 1, "slots": 12},
                {"slots": 828},
            ),
        },
        {
            "name": "Dragon plateskirt",
            "total": 2048,
            "slots": (
                {"item": "Dragon plateskirt", "quantity": 1, "slots": 1},
                {"slots": 2047},
            ),
        },
        {
            "name": "Dragon platelegs",
            "total": 2048,
            "slots": (
                {"item": "Dragon platelegs", "quantity": 1, "slots": 1},
                {"slots": 2047},
            ),
        },
        {
            "name": "Hard clue",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (hard)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
        {
            "name": "Elite clue",
            "total": 500,
            "slots": (
                {"item": "Clue scroll (elite)", "quantity": 1, "slots": 1},
                {"slots": 499},
            ),
        },
    ),
}


IRON_DRAGON_DROPS = {
    "guaranteed": (("Dragon bones", 1), ("Iron bar", 5)),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 128,
            "slots": (
                {"item": "Adamant javelin", "quantity": 4, "slots": 19},
                {"item": "Coins", "quantity": 270, "slots": 20},
                {"item": "Blood rune", "quantity": 15, "slots": 19},
                {"item": "Coins", "quantity": 550, "slots": 10},
                {"item": "Super strength (1)", "quantity": 1, "slots": 8},
                {"item": "Rune dart (p)", "quantity": 9, "slots": 7},
                {
                    "item": "Adamant bolts",
                    "quantity_range": (2, 12),
                    "slots": 6,
                },
                {"item": "Soul rune", "quantity": 3, "slots": 5},
                {"item": "Runite limbs", "quantity": 1, "slots": 5},
                {"item": "Adamant 2h sword", "quantity": 1, "slots": 4},
                {"item": "Adamant hatchet", "quantity": 1, "slots": 3},
                {"item": "Adamant battleaxe", "quantity": 1, "slots": 3},
                {"item": "Rune knife", "quantity": 5, "slots": 3},
                {"item": "Adamant bar", "quantity": 2, "slots": 3},
                {"item": "Curry", "quantity": 1, "slots": 3},
                {"table": DARKAN_GEM_DROP_TABLE, "slots": 3},
                {"table": DARKAN_STANDARD_RARE_DROP_TABLE, "slots": 2},
                {"item": "Adamant sq shield", "quantity": 1, "slots": 1},
                {"item": "Rune med helm", "quantity": 1, "slots": 1},
                {"item": "Rune battleaxe", "quantity": 1, "slots": 1},
                {"item": "Coins", "quantity": 990, "slots": 1},
                {"slots": 1},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 1212,
            "slots": (
                {"item": "Gold charm", "quantity": 2, "slots": 48},
                {"item": "Green charm", "quantity": 2, "slots": 282},
                {"item": "Crimson charm", "quantity": 2, "slots": 54},
                {"item": "Blue charm", "quantity": 2, "slots": 12},
                {"slots": 816},
            ),
        },
        {
            "name": "Dragon plateskirt",
            "total": 1024,
            "slots": (
                {"item": "Dragon plateskirt", "quantity": 1, "slots": 1},
                {"slots": 1023},
            ),
        },
        {
            "name": "Dragon platelegs",
            "total": 1024,
            "slots": (
                {"item": "Dragon platelegs", "quantity": 1, "slots": 1},
                {"slots": 1023},
            ),
        },
        {
            "name": "Draconic visage",
            "total": 10000,
            "slots": (
                {"item": "Draconic visage", "quantity": 1, "slots": 1},
                {"slots": 9999},
            ),
        },
        {
            "name": "Hard clue",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (hard)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


STEEL_DRAGON_DROPS = {
    "guaranteed": (("Dragon bones", 1), ("Steel bar", 5)),
    "tables": (
        {
            "name": "Darkan ordinary with OSRS-lineage closure",
            "total": 128,
            "slots": (
                {"item": "Rune javelin", "quantity": 7, "slots": 20},
                {"item": "Blood rune", "quantity": 20, "slots": 19},
                {"item": "Coins", "quantity": 470, "slots": 17},
                {"item": "Super attack (3)", "quantity": 1, "slots": 13},
                {"item": "Runite limbs", "quantity": 1, "slots": 8},
                {"item": "Rune dart (p)", "quantity": 12, "slots": 7},
                {
                    "item": "Runite bolts",
                    "quantity_range": (2, 12),
                    "slots": 6,
                },
                {"item": "Soul rune", "quantity": 5, "slots": 5},
                {"item": "Coins", "quantity": 650, "slots": 5},
                {"item": "Rune mace", "quantity": 1, "slots": 4},
                {"table": DARKAN_STANDARD_RARE_DROP_TABLE, "slots": 4},
                {"table": DARKAN_GEM_DROP_TABLE, "slots": 4},
                {"item": "Rune knife", "quantity": 7, "slots": 3},
                {"item": "Runite bar", "quantity": 1, "slots": 3},
                {"item": "Super defence (2)", "quantity": 1, "slots": 3},
                {"item": "Adamant kiteshield", "quantity": 1, "slots": 2},
                {"item": "Rune hatchet", "quantity": 1, "slots": 2},
                {"item": "Rune full helm", "quantity": 1, "slots": 1},
                {"item": "Curry", "quantity": 1, "slots": 1},
                {"item": "Curry", "quantity": 2, "slots": 1},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 1212,
            "slots": (
                {"item": "Gold charm", "quantity": 3, "slots": 56},
                {"item": "Green charm", "quantity": 3, "slots": 308},
                {"item": "Crimson charm", "quantity": 3, "slots": 56},
                {"item": "Blue charm", "quantity": 3, "slots": 12},
                {"slots": 780},
            ),
        },
        {
            "name": "Dragon plateskirt",
            "total": 512,
            "slots": (
                {"item": "Dragon plateskirt", "quantity": 1, "slots": 1},
                {"slots": 511},
            ),
        },
        {
            "name": "Dragon platelegs",
            "total": 512,
            "slots": (
                {"item": "Dragon platelegs", "quantity": 1, "slots": 1},
                {"slots": 511},
            ),
        },
        {
            "name": "Draconic visage",
            "total": 10000,
            "slots": (
                {"item": "Draconic visage", "quantity": 1, "slots": 1},
                {"slots": 9999},
            ),
        },
        {
            "name": "Hard clue",
            "total": 64,
            "slots": (
                {"item": "Clue scroll (hard)", "quantity": 1, "slots": 1},
                {"slots": 63},
            ),
        },
        {
            "name": "Elite clue",
            "total": 500,
            "slots": (
                {"item": "Clue scroll (elite)", "quantity": 1, "slots": 1},
                {"slots": 499},
            ),
        },
    ),
}


ENEMIES = {
    "bronze_dragon": {
        "display_name": "Bronze dragon",
        "level": 131,
        "group": "Dragons",
        "dragonfire": {
            "chance_numerator": 1,
            "chance_denominator": 2,
            "unprotected_max_hit": 500,
            "partial_max_hit": 50,
            "shield_items": ("Anti-dragon shield", "Dragonfire shield"),
            "source": (
                "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
                "darkan-world-server/src/main/java/com/rs/game/content/world/"
                "npcs/MetalDragonCombat.java:41-61; "
                f"{DRAGONFIRE_FORMULA_SOURCE_PATH}:878-908"
            ),
            "source_status": (
                "bounded no-position abstraction using Darkan's exact adjacent "
                "1/2 attack-selection roll and protection tiers; long-range "
                "dragonfire, damage envelope, and metal-dragon protection "
                "behavior corroborated by Bronze dragon oldid=6550367 and "
                "Dragonfire oldid=6534496"
            ),
        },
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 123,
        "slayer_xp": 125.0,
        "stats": {
            "hitpoints": 1220,
            "attack": 112,
            "strength": 112,
            "defence": 112,
            "magic": 100,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 50,
            "defence_slash": 70,
            "defence_crush": 70,
            "defence_magic": 30,
            "defence_ranged": 90,
            "melee_strength": 0,
        },
        "drops": BRONZE_DRAGON_DROPS,
        "source": (
            "https://runescape.wiki/w/Bronze_dragon?oldid=6550367; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "bronze_dragon.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/bronze_dragon.json"
        ),
        "source_status": (
            "period exact level, LP, Slayer XP, six-tick melee/long-range "
            "dragonfire, approximate maxima, aggression, poison behavior, "
            "guaranteed Dragon bones/five Bronze bars, and Chaeldar assignment; "
            "Darkan exact combat levels, defences, 59-tick respawn, 128-slot "
            "ordinary selector including one empty slot, nested tables, "
            "losslessly enumerated charms, independent 1/2048 plate drops, "
            "1/128 hard clue, and 1/500 elite clue; location, quest-only, "
            "post-cutoff, and Daemonheim contexts excluded"
        ),
    },
    "iron_dragon": {
        "display_name": "Iron dragon",
        "level": 189,
        "group": "Dragons",
        "dragonfire": {
            "chance_numerator": 1,
            "chance_denominator": 2,
            "unprotected_max_hit": 500,
            "partial_max_hit": 50,
            "shield_items": ("Anti-dragon shield", "Dragonfire shield"),
            "source": (
                "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
                "darkan-world-server/src/main/java/com/rs/game/content/world/"
                "npcs/MetalDragonCombat.java:41-61; "
                f"{DRAGONFIRE_FORMULA_SOURCE_PATH}:878-908"
            ),
            "source_status": (
                "existing bounded no-position metal-dragon abstraction using "
                "Darkan's exact adjacent 1/2 attack-selection roll and "
                "protection tiers; long-range dragonfire, damage envelope, "
                "and metal-dragon protection behavior corroborated by Iron "
                "dragon oldid=6530527 and Dragonfire oldid=6534496"
            ),
        },
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 203,
        "slayer_xp": 173.2,
        "stats": {
            "hitpoints": 1650,
            "attack": 165,
            "strength": 165,
            "defence": 165,
            "magic": 100,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 50,
            "defence_slash": 70,
            "defence_crush": 70,
            "defence_magic": 30,
            "defence_ranged": 90,
            "melee_strength": 0,
        },
        "drops": IRON_DRAGON_DROPS,
        "source": (
            "https://runescape.wiki/w/Iron_dragon?oldid=6530527; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "iron_dragon/iron_dragon_(189).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/iron_dragon.json"
        ),
        "source_status": (
            "period exact ordinary level, LP, Slayer XP, six-tick "
            "melee/long-range dragonfire, 203-LP melee maximum, aggression, "
            "poison behavior, guaranteed Dragon bones/five Iron bars, and "
            "Sumona assignment; Darkan exact combat levels, defences, "
            "59-tick respawn, 128-slot ordinary selector including one empty "
            "slot, nested tables, losslessly enumerated quantity-two charms, "
            "independent 1/1024 plate drops, 1/10000 visage, and 1/128 hard "
            "clue; location, quest-only, post-cutoff, pit, and Daemonheim "
            "contexts excluded"
        ),
    },
    "steel_dragon": {
        "display_name": "Steel dragon",
        "level": 246,
        "group": "Dragons",
        "dragonfire": {
            "chance_numerator": 1,
            "chance_denominator": 2,
            "unprotected_max_hit": 500,
            "partial_max_hit": 50,
            "shield_items": ("Anti-dragon shield", "Dragonfire shield"),
            "source": (
                "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
                "darkan-world-server/src/main/java/com/rs/game/content/world/"
                "npcs/MetalDragonCombat.java:41-61; "
                f"{DRAGONFIRE_FORMULA_SOURCE_PATH}:878-908"
            ),
            "source_status": (
                "existing bounded no-position metal-dragon abstraction using "
                "Darkan's exact adjacent 1/2 attack-selection roll and "
                "protection tiers; long-range dragonfire, damage envelope, "
                "and metal-dragon protection behavior corroborated by Steel "
                "dragon oldid=6582075 and Dragonfire oldid=6534496"
            ),
        },
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 225,
        "slayer_xp": 220.4,
        "stats": {
            "hitpoints": 2100,
            "attack": 215,
            "strength": 215,
            "defence": 215,
            "magic": 100,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 50,
            "defence_slash": 70,
            "defence_crush": 70,
            "defence_magic": 30,
            "defence_ranged": 90,
            "melee_strength": 0,
        },
        "drops": STEEL_DRAGON_DROPS,
        "source": (
            "https://runescape.wiki/w/Steel_dragon?oldid=6582075; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "steel_dragon.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/steel_dragon.json"
        ),
        "source_status": (
            "period exact ordinary level, LP, Slayer XP, six-tick "
            "melee/long-range dragonfire, 225-LP melee maximum, aggression, "
            "poison behavior, guaranteed Dragon bones/five Steel bars, and "
            "Duradel/Kuradal assignment; Darkan exact combat levels, "
            "defences, 59-tick respawn, 123/128 ordinary selector, "
            "losslessly enumerated quantity-three charms, independent 1/512 "
            "plate drops, 1/10000 visage, 1/64 hard clue, and 1/500 elite "
            "clue; the missing Coins x650 row is provisional/osrs-lineage at "
            "5/128 because it exactly closes Darkan's five-slot gap and the "
            "period page attests the item; location, POH, post-cutoff, and "
            "Daemonheim contexts excluded"
        ),
    },
}
