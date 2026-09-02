from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
    DRAGONFIRE_FORMULA_SOURCE_PATH,
    LEATHER_DRAGON_COMBAT_SOURCE_PATH,
)
from ..contract import (
    COMBAT_GEM_DROP_TABLE,
    COMBAT_MINOR_HERB_DROP_TABLE,
    DARKAN_GEM_DROP_TABLE,
    DARKAN_HERB_DROP_TABLE,
    DARKAN_STANDARD_RARE_DROP_TABLE,
)

BLUE_DRAGON_DROPS = {
    "guaranteed": (("Blue dragonhide", 1), ("Dragon bones", 1)),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 128,
            "slots": (
                {"item": "Coins", "quantity": 44, "slots": 29},
                {"item": "Coins", "quantity": 132, "slots": 25},
                {"table": DARKAN_HERB_DROP_TABLE, "slots": 15},
                {"item": "Coins", "quantity": 200, "slots": 10},
                {"item": "Water rune", "quantity": 75, "slots": 8},
                {"item": "Nature rune", "quantity": 15, "slots": 5},
                {"item": "Coins", "quantity": 11, "slots": 5},
                {"table": DARKAN_GEM_DROP_TABLE, "slots": 5},
                {"item": "Steel platelegs", "quantity": 1, "slots": 4},
                {"item": "Mithril hatchet", "quantity": 1, "slots": 3},
                {"item": "Mithril spear", "quantity": 1, "slots": 3},
                {"item": "Law rune", "quantity": 3, "slots": 3},
                {"item": "Adamantite ore", "quantity": 1, "slots": 3},
                {"item": "Bass", "quantity": 1, "slots": 3},
                {"item": "Adamant dagger", "quantity": 1, "slots": 2},
                {"item": "Adamant full helm", "quantity": 1, "slots": 1},
                {"item": "Mithril kiteshield", "quantity": 1, "slots": 1},
                {"item": "Rune dagger", "quantity": 1, "slots": 1},
                {"item": "Fire rune", "quantity": 37, "slots": 1},
                {"item": "Coins", "quantity": 440, "slots": 1},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 404,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 15},
                {"item": "Green charm", "quantity": 1, "slots": 79},
                {"item": "Crimson charm", "quantity": 1, "slots": 15},
                {"item": "Blue charm", "quantity": 1, "slots": 3},
                {"slots": 292},
            ),
        },
        {
            "name": "Blue dragon egg (Summoning 99)",
            "total": 2000,
            "required_skill_levels": (("summoning", 99),),
            "slots": (
                {"item": "Blue dragon egg", "quantity": 1, "slots": 1},
                {"slots": 1999},
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


RED_DRAGON_DROPS = {
    "guaranteed": (("Dragon bones", 1), ("Red dragonhide", 1)),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 128,
            "slots": (
                {"item": "Coins", "quantity": 196, "slots": 39},
                {"item": "Coins", "quantity": 66, "slots": 28},
                {"item": "Coins", "quantity": 330, "slots": 9},
                {"item": "Rune arrows", "quantity": 4, "slots": 8},
                {"item": "Law rune", "quantity": 4, "slots": 5},
                {"table": DARKAN_GEM_DROP_TABLE, "slots": 5},
                {"item": "Mithril 2h sword", "quantity": 1, "slots": 4},
                {"item": "Blood rune", "quantity": 2, "slots": 4},
                {"item": "Mithril hatchet", "quantity": 1, "slots": 3},
                {"item": "Mithril battleaxe", "quantity": 1, "slots": 3},
                {"item": "Rune dart", "quantity": 8, "slots": 3},
                {"item": "Death rune", "quantity": 5, "slots": 3},
                {"item": "Chocolate cake", "quantity": 3, "slots": 3},
                {"table": DARKAN_HERB_DROP_TABLE, "slots": 2},
                {"item": "Mithril javelin", "quantity": 20, "slots": 1},
                {"item": "Mithril kiteshield", "quantity": 1, "slots": 1},
                {"item": "Adamant platebody", "quantity": 1, "slots": 1},
                {"item": "Rune longsword", "quantity": 1, "slots": 1},
                {"item": "Coins", "quantity": 690, "slots": 1},
                {"item": "Adamant bar", "quantity": 1, "slots": 1},
                {"slots": 3},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 1212,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 73},
                {"item": "Green charm", "quantity": 1, "slots": 385},
                {"item": "Crimson charm", "quantity": 1, "slots": 67},
                {"item": "Blue charm", "quantity": 1, "slots": 15},
                {"slots": 672},
            ),
        },
        {
            "name": "Red dragon egg (Summoning 99)",
            "total": 2000,
            "required_skill_levels": (("summoning", 99),),
            "slots": (
                {"item": "Red dragon egg", "quantity": 1, "slots": 1},
                {"slots": 1999},
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


BLACK_DRAGON_DROPS = {
    "guaranteed": (("Dragon bones", 1), ("Black dragonhide", 1)),
    "tables": (
        {
            "name": "game-main ordinary",
            "total": 128,
            "slots": (
                {"item": "Mithril 2h sword", "quantity": 1, "slots": 4},
                {"item": "Mithril hatchet", "quantity": 1, "slots": 3},
                {"item": "Mithril battleaxe", "quantity": 1, "slots": 3},
                {"item": "Rune knife", "quantity": 2, "slots": 3},
                {"item": "Mithril kiteshield", "quantity": 1, "slots": 1},
                {"item": "Adamant platebody", "quantity": 1, "slots": 1},
                {"item": "Rune longsword", "quantity": 1, "slots": 1},
                {"item": "Adamant javelin", "quantity": 30, "slots": 20},
                {"item": "Fire rune", "quantity": 50, "slots": 8},
                {"item": "Adamant dart (p)", "quantity": 16, "slots": 7},
                {"item": "Law rune", "quantity": 10, "slots": 5},
                {"item": "Blood rune", "quantity": 15, "slots": 3},
                {"item": "Air rune", "quantity": 75, "slots": 1},
                {"item": "Coins", "quantity": 196, "slots": 40},
                {"item": "Coins", "quantity": 330, "slots": 10},
                {"item": "Coins", "quantity": 690, "slots": 1},
                {"item": "Adamant bar", "quantity": 1, "slots": 3},
                {"item": "Chocolate cake", "quantity": 1, "slots": 3},
                {"table": DARKAN_GEM_DROP_TABLE, "slots": 3},
                {"table": DARKAN_STANDARD_RARE_DROP_TABLE, "slots": 2},
                {"slots": 6},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 1212,
            "slots": (
                {"item": "Gold charm", "quantity": 3, "slots": 42},
                {"item": "Green charm", "quantity": 3, "slots": 258},
                {"item": "Crimson charm", "quantity": 3, "slots": 30},
                {"item": "Blue charm", "quantity": 3, "slots": 6},
                {"slots": 876},
            ),
        },
        {
            "name": "Black dragon egg (Summoning 99)",
            "total": 2000,
            "required_skill_levels": (("summoning", 99),),
            "slots": (
                {"item": "Black dragon egg", "quantity": 1, "slots": 1},
                {"slots": 1999},
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
    "baby_dragon": {
        "display_name": "Baby dragon",
        "level": 48,
        "group": "Dragons",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 50.0,
        "stats": {'hitpoints': 500, 'attack': 40, 'strength': 40, 'defence': 40, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 30,
 'defence_slash': 50,
 'defence_crush': 50,
 'defence_magic': 40,
 'defence_ranged': 30,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Babydragon bones', 1),), 'tables': ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/dragons/baby_dragon_level_48.plugin.kts"
        ),
    },
    "baby_black_dragon": {
        "display_name": "Baby black dragon",
        "level": 83,
        "group": "Dragons",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 80.0,
        "stats": {'hitpoints': 800, 'attack': 70, 'strength': 70, 'defence': 70, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 30,
 'defence_slash': 50,
 'defence_crush': 50,
 'defence_magic': 40,
 'defence_ranged': 30,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Babydragon bones', 1),), 'tables': ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/dragons/baby_black_dragon_level_83.plugin.kts"
        ),
    },
    "blue_dragon": {
        "display_name": "Blue dragon",
        "level": 111,
        "group": "Dragons",
        "dragonfire": {
            "chance_numerator": 1,
            "chance_denominator": 4,
            "unprotected_max_hit": 500,
            "partial_max_hit": 50,
            "shield_items": ("Anti-dragon shield", "Dragonfire shield"),
            "source": (
                f"{LEATHER_DRAGON_COMBAT_SOURCE_PATH}:45-60; "
                f"{DRAGONFIRE_FORMULA_SOURCE_PATH}:878-908"
            ),
            "source_status": (
                "provisional/darkan hidden attack-selection roll; damage and "
                "protection tiers corroborated by Blue dragon oldid=6506510 "
                "and Dragonfire oldid=6534496"
            ),
        },
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 110,
        "slayer_xp": 107.6,
        "stats": {
            "hitpoints": 1100,
            "attack": 95,
            "strength": 95,
            "defence": 95,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 50,
            "defence_slash": 70,
            "defence_crush": 70,
            "defence_magic": 60,
            "defence_ranged": 50,
            "melee_strength": 0,
        },
        "drops": BLUE_DRAGON_DROPS,
        "source": (
            "https://runescape.wiki/w/Blue_dragon?oldid=6506510; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/"
            "content/npcs/definitions/dragons/blue_dragon_level_111.plugin.kts; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/blue_dragon.json"
        ),
        "source_status": (
            "period exact ordinary level, LP, Slayer XP, six-tick melee, "
            "110-LP melee maximum, close-range dragonfire, poison behavior, "
            "guaranteed Dragon bones/Blue dragonhide, and baby substitution; "
            "game-main exact combat levels/defences; Darkan exact 59-tick "
            "respawn, 128-slot ordinary selector, nested tables, losslessly "
            "enumerated charms, 1/128 hard clue, and 1/2000 Summoning-99 egg; "
            "location and Daemonheim contexts excluded"
        ),
    },
    "baby_blue_dragon": {
        "display_name": "Baby blue dragon",
        "level": 48,
        "group": "Dragons",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 60,
        "slayer_xp": 50.0,
        "stats": {
            "hitpoints": 510,
            "attack": 40,
            "strength": 40,
            "defence": 40,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 30,
            "defence_slash": 50,
            "defence_crush": 50,
            "defence_magic": 40,
            "defence_ranged": 30,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Baby dragon bones", 1),), "tables": ()},
        "source": (
            "https://runescape.wiki/w/Baby_blue_dragon?oldid=6516086; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "baby_blue_dragon.json"
        ),
        "source_status": (
            "period exact level, LP, Slayer XP, six-tick melee, approximate "
            "60-LP maximum represented by the corroborating Darkan maximum, "
            "no dragonfire, poison behavior, guaranteed Baby dragon bones, "
            "and Blue-dragon Slayer substitution; Darkan exact combat levels, "
            "defences, and 59-tick respawn; quest-only bone and post-cutoff "
            "loot excluded"
        ),
    },
    "red_dragon": {
        "display_name": "Red dragon",
        "level": 152,
        "group": "Dragons",
        "dragonfire": {
            "chance_numerator": 1,
            "chance_denominator": 4,
            "unprotected_max_hit": 500,
            "partial_max_hit": 50,
            "shield_items": ("Anti-dragon shield", "Dragonfire shield"),
            "source": (
                f"{LEATHER_DRAGON_COMBAT_SOURCE_PATH}:45-60; "
                f"{DRAGONFIRE_FORMULA_SOURCE_PATH}:878-908"
            ),
            "source_status": (
                "provisional/darkan hidden attack-selection roll; damage and "
                "protection tiers corroborated by Red dragon oldid=6506523 "
                "and Dragonfire oldid=6534496"
            ),
        },
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 158,
        "slayer_xp": 142.5,
        "stats": {
            "hitpoints": 1400,
            "attack": 130,
            "strength": 130,
            "defence": 130,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 50,
            "defence_slash": 70,
            "defence_crush": 70,
            "defence_magic": 60,
            "defence_ranged": 50,
            "melee_strength": 0,
        },
        "drops": RED_DRAGON_DROPS,
        "source": (
            "https://runescape.wiki/w/Red_dragon?oldid=6506523; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "red_dragon/red_dragon_(152).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/red_dragon.json"
        ),
        "source_status": (
            "period exact ordinary level, LP, Slayer XP, six-tick melee, "
            "158-LP melee maximum, close-range dragonfire, poison behavior, "
            "guaranteed Dragon bones/Red dragonhide, Sumona assignment, and "
            "baby substitution; direct period maximum preserves the explicit "
            "144-LP Darkan conflict; Darkan exact combat levels, defences, "
            "59-tick respawn, provisional 1/4 dragonfire selector, 128-slot "
            "ordinary selector including three empty slots, losslessly "
            "enumerated charms, Summoning-99 1/2000 egg, and 1/128 hard clue; "
            "location, challenge-only, quest-only, post-cutoff, and Daemonheim "
            "contexts excluded"
        ),
    },
    "black_dragon": {
        "display_name": "Black dragon",
        "level": 227,
        "group": "Dragons",
        "dragonfire": {
            "chance_numerator": 1,
            "chance_denominator": 4,
            "unprotected_max_hit": 500,
            "partial_max_hit": 50,
            "shield_items": ("Anti-dragon shield", "Dragonfire shield"),
            "source": (
                f"{LEATHER_DRAGON_COMBAT_SOURCE_PATH}:45-60; "
                f"{DRAGONFIRE_FORMULA_SOURCE_PATH}:878-908"
            ),
            "source_status": (
                "provisional/darkan hidden attack-selection roll; damage and "
                "protection tiers corroborated by Black dragon oldid=6580941 "
                "and Dragonfire oldid=6534496"
            ),
        },
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 214,
        "slayer_xp": 199.4,
        "stats": {
            "hitpoints": 1900,
            "attack": 200,
            "strength": 200,
            "defence": 200,
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
            "defence_magic": 60,
            "defence_ranged": 50,
            "melee_strength": 0,
        },
        "drops": BLACK_DRAGON_DROPS,
        "source": (
            "https://runescape.wiki/w/Black_dragon?oldid=6580941; "
            "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/"
            "main/kotlin/gg/rsmod/plugins/content/npcs/definitions/dragons/"
            "black_dragon_level_227.plugin.kts; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "black_dragon/black_dragon_(227).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/black_dragon.json"
        ),
        "source_status": (
            "period exact ordinary level, LP, Slayer XP, six-tick melee, "
            "214-LP melee maximum, close-range dragonfire, aggression, poison "
            "behavior, guaranteed Dragon bones/Black dragonhide, Duradel and "
            "Kuradal assignments, and baby/KBD substitution; game-main exact "
            "combat levels, defences, and complete 128-slot ordinary selector "
            "including six empty slots; Darkan exact 59-tick respawn, "
            "provisional 1/4 dragonfire selector, losslessly enumerated "
            "quantity-three charms, Summoning-99 1/2000 egg, 1/10000 visage, "
            "1/128 hard clue, and 1/500 elite clue; KBD, Queen Black Dragon, "
            "location, quest-only, post-cutoff, and Daemonheim contexts "
            "excluded"
        ),
    },
    "baby_red_dragon": {
        "display_name": "Baby red dragon",
        "level": 48,
        "group": "Dragons",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 54,
        "slayer_xp": 50.0,
        "stats": {
            "hitpoints": 500,
            "attack": 40,
            "strength": 40,
            "defence": 40,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 30,
            "defence_slash": 50,
            "defence_crush": 50,
            "defence_magic": 40,
            "defence_ranged": 30,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Baby dragon bones", 1),), "tables": ()},
        "source": (
            "https://runescape.wiki/w/Baby_red_dragon?oldid=6516030; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "baby_red_dragon/baby_red_dragon_(48) (noanims).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/baby_red_dragon.json"
        ),
        "source_status": (
            "period exact ordinary level, LP, Slayer XP, six-tick melee, "
            "54-LP maximum, no dragonfire, poison behavior, guaranteed Baby "
            "dragon bones, and Red-dragon Slayer substitution; Darkan exact "
            "combat levels, defences, and 59-tick respawn; level-65 POH, "
            "challenge-only, quest-only, and post-cutoff contexts excluded"
        ),
    },
    "green_dragon": {
        "display_name": "Green dragon",
        "level": 79,
        "group": "Dragons",
        "wilderness_risk": {
            "ambush_chance": 0.01,
            "max_hit": 250,
            "unskulled_items_kept": 3,
            "source_status": (
                "owner-approved bounded AnkiScape abstraction; PKer frequency "
                "was live-player behavior rather than source-static data"
            ),
        },
        "dragonfire": {
            "chance_numerator": 1,
            "chance_denominator": 4,
            "unprotected_max_hit": 500,
            "partial_max_hit": 50,
            "shield_items": ("Anti-dragon shield", "Dragonfire shield"),
            "source": (
                f"{LEATHER_DRAGON_COMBAT_SOURCE_PATH}:45-60; "
                f"{DRAGONFIRE_FORMULA_SOURCE_PATH}:878-908"
            ),
            "source_status": (
                "provisional/darkan hidden attack-selection roll; damage and "
                "protection tiers corroborated by Green dragon oldid=6565810 "
                "and Dragonfire oldid=6534496"
            ),
        },
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 85,
        "slayer_xp": 75.0,
        "stats": {
            "hitpoints": 750,
            "attack": 68,
            "strength": 68,
            "defence": 68,
            "magic": 68,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 20,
            "defence_slash": 40,
            "defence_crush": 40,
            "defence_magic": 30,
            "defence_ranged": 20,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Dragon bones", 1), ("Green dragonhide", 1)),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Steel platelegs", "quantity": 1, "slots": 32},
                        {"item": "Steel battleaxe", "quantity": 1, "slots": 24},
                        {"item": "Mithril hatchet", "quantity": 1, "slots": 24},
                        {"item": "Mithril spear", "quantity": 1, "slots": 16},
                        {"item": "Mithril kiteshield", "quantity": 1, "slots": 8},
                        {"item": "Adamant full helm", "quantity": 1, "slots": 8},
                        {"item": "Rune dagger", "quantity": 1, "slots": 8},
                        {"item": "Water rune", "quantity": 75, "slots": 64},
                        {"item": "Nature rune", "quantity": 15, "slots": 40},
                        {"item": "Law rune", "quantity": 3, "slots": 24},
                        {"item": "Fire rune", "quantity": 37, "slots": 8},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 120},
                        {"item": "Coins", "quantity": 44, "slots": 232},
                        {"item": "Coins", "quantity": 132, "slots": 200},
                        {"item": "Coins", "quantity": 200, "slots": 80},
                        {"item": "Coins", "quantity": 11, "slots": 40},
                        {"item": "Coins", "quantity": 440, "slots": 8},
                        {"item": "Bass", "quantity": 1, "slots": 24},
                        {"item": "Adamantite ore", "quantity": 1, "slots": 24},
                        {"slots": 5},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 40},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (hard)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/dragons/green_dragon_level_79.plugin.kts; "
            f"{LEATHER_DRAGON_COMBAT_SOURCE_PATH}"
        ),
    },
}
