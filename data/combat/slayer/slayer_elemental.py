from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
)
from ..contract import (
    COMBAT_GEM_DROP_TABLE,
    COMBAT_MINOR_HERB_DROP_TABLE,
)

SHADOW_WARRIOR_DROPS = {
    "guaranteed": (),
    "tables": (
        {
            "name": "Darkan main",
            "total": 128,
            "slots": tuple(
                {"item": item_name, "quantity": quantity, "slots": chance}
                for item_name, quantity, chance in (
                    ("Coins", 8, 47),
                    ("Cosmic rune", 3, 9),
                    ("Blood rune", 2, 6),
                    ("Air rune", 45, 4),
                    ("Death rune", 2, 4),
                    ("Mithril bar", 1, 4),
                    ("Adamant spear", 1, 1),
                    ("Black dagger (p)", 1, 1),
                    ("Black knife", 1, 1),
                    ("Black longsword", 1, 1),
                    ("Black robe", 1, 1),
                    ("Weapon poison", 1, 1),
                )
            )
            + (
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 18},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 8},
                {"slots": 22},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 606,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 26},
                {"item": "Green charm", "quantity": 1, "slots": 11},
                {"item": "Crimson charm", "quantity": 1, "slots": 44},
                {"item": "Blue charm", "quantity": 1, "slots": 3},
                {"slots": 522},
            ),
        },
    ),
}


ENEMIES = {
    "killerwatt": {
        "display_name": "Killerwatt",
        "level": 71,
        "group": "Slayer",
        "required_slayer_level": 37,
        "quest_gate": "ernest_the_chicken",
        "quest_gate_label": "Complete Ernest the Chicken",
        "attack_style": "magic_melee",
        "attack_style_by_player_class": {
            "melee": "magic_melee",
            "ranged": "ranged",
            "magic": "ranged",
        },
        "attack_speed": 8,
        "respawn_delay": 59,
        "max_hit": 64,
        "slayer_xp": 51.0,
        "stats": {
            "hitpoints": 510,
            "attack": 50,
            "strength": 50,
            "defence": 40,
            "magic": 67,
            "ranged": 67,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 10,
            "defence_slash": 10,
            "defence_crush": 10,
            "defence_magic": 20,
            "defence_ranged": 20,
            "melee_strength": 0,
        },
        "protective_equipment": {
            "slot": "feet",
            "items": ("Insulated boots",),
            "warning": (
                "Missing Insulated boots: Killerwatt Plane thunderclouds add "
                "0–140 LP damage to each incoming attack."
            ),
            "unprotected_effect": {
                "damage": {"kind": "uniform_max", "max": 140},
                "additive_to_attack": True,
            },
            "source_status": (
                "period-exact equipment consequence and 140-LP maximum; one "
                "additive cloud roll per incoming attack is the bounded "
                "review-native cadence abstraction"
            ),
        },
        "drops": {
            "guaranteed": (("Impious ashes", 1),),
            "tables": (
                {
                    "name": "Darkan main",
                    "total": 100000,
                    "slots": (
                        {"item": "Grimy guam", "quantity": 1, "slots": 12016},
                        {"item": "Grimy marrentill", "quantity": 1, "slots": 12016},
                        {"item": "Grimy tarromin", "quantity": 1, "slots": 12016},
                        {"item": "Grimy harralander", "quantity": 1, "slots": 12016},
                        {
                            "item": "Fire rune",
                            "quantity_range": (18, 45),
                            "slots": 12016,
                        },
                        {
                            "item": "Air rune",
                            "quantity_range": (5, 17),
                            "slots": 12016,
                        },
                        {
                            "item": "Coins",
                            "quantity_range": (11, 200),
                            "slots": 12016,
                        },
                        {"item": "Cannonball", "quantity": 3, "slots": 876},
                        {"item": "Grimy ranarr", "quantity": 1, "slots": 876},
                        {"item": "Grimy irit", "quantity": 1, "slots": 876},
                        {"item": "Grimy avantoe", "quantity": 1, "slots": 876},
                        {"item": "Grimy kwuarm", "quantity": 1, "slots": 876},
                        {"item": "Grimy cadantine", "quantity": 1, "slots": 876},
                        {
                            "item": "Nature rune",
                            "quantity_range": (4, 37),
                            "slots": 876,
                        },
                        {"item": "Chaos rune", "quantity": 4, "slots": 876},
                        {"item": "Fire orb", "quantity": 2, "slots": 876},
                        {"item": "Staff of air", "quantity": 1, "slots": 876},
                        {"item": "Staff of fire", "quantity": 1, "slots": 876},
                        {"item": "Fire battlestaff", "quantity": 1, "slots": 876},
                        {"item": "Air battlestaff", "quantity": 1, "slots": 876},
                        {"item": "Mystic fire staff", "quantity": 1, "slots": 876},
                        {"item": "Soda ash", "quantity": 4, "slots": 876},
                        {"item": "Steam rune", "quantity": 2, "slots": 876},
                        {"item": "Grimy dwarf weed", "quantity": 1, "slots": 623},
                        {"item": "Death rune", "quantity": 2, "slots": 623},
                        {"item": "Grimy lantadyme", "quantity": 1, "slots": 623},
                        {"slots": 3},
                    ),
                },
                {
                    "name": "Darkan charms",
                    "total": 303,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 41},
                        {"item": "Green charm", "quantity": 1, "slots": 2},
                        {"item": "Crimson charm", "quantity": 1, "slots": 2},
                        {"slots": 258},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Killerwatt?oldid=6469837; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "killerwatt (noanims).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/developer-information/npcListBonuses.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/killerwatt.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java"
        ),
        "source_status": (
            "period exact identity, LP, Slayer/quest gates, Slayer XP, "
            "eight-tick magical-melee/ranged styles, maximum hit, guaranteed "
            "ashes, and uninsulated 140-LP cloud maximum; Darkan exact stats, "
            "bonuses, respawn, one 100,000-slot ordinary selector, and "
            "emulator-exact 303-slot charm selector"
        ),
    },
    "icefiend": {
        "display_name": "Icefiend",
        "level": 13,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "max_hit": 20,
        "slayer_xp": 15.0,
        "stats": {
            "hitpoints": 150,
            "attack": 10,
            "strength": 10,
            "defence": 12,
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
        "drops": {
            "guaranteed": (("Impious ashes", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Water talisman", "quantity": 1, "slots": 8},
                        {"item": "Bronze sword", "quantity": 1, "slots": 4},
                        {"item": "Bronze hatchet", "quantity": 1, "slots": 4},
                        {"item": "Iron hatchet", "quantity": 1, "slots": 4},
                        {"item": "Bronze pickaxe", "quantity": 1, "slots": 4},
                        {"item": "Iron pickaxe", "quantity": 1, "slots": 4},
                        {"item": "Bronze arrows", "quantity_range": (2, 9), "slots": 4},
                        {"item": "Iron arrows", "quantity_range": (1, 5), "slots": 4},
                        {"item": "Steel arrows", "quantity": 1, "slots": 4},
                        {"item": "Bronze bolts", "quantity_range": (1, 10), "slots": 4},
                        {"item": "Bronze med helm", "quantity": 1, "slots": 4},
                        {"item": "Bronze full helm", "quantity": 1, "slots": 4},
                        {"item": "Iron chainbody", "quantity": 1, "slots": 4},
                        {"item": "Silver ore", "quantity": 1, "slots": 4},
                        {"item": "Silver bar", "quantity": 1, "slots": 4},
                        {"item": "Steel med helm", "quantity": 1, "slots": 2},
                        {"item": "Jug of wine", "quantity": 1, "slots": 2},
                        {"item": "Steel hatchet", "quantity": 1, "slots": 1},
                        {"item": "Steel pickaxe", "quantity": 1, "slots": 1},
                        {"item": "Staff of air", "quantity": 1, "slots": 1},
                        {"item": "Staff of water", "quantity": 1, "slots": 1},
                        {"item": "Dwarven stout", "quantity": 1, "slots": 1},
                        {"item": "Cake", "quantity": 1, "slots": 1},
                        {"item": "Beer", "quantity": 1, "slots": 1},
                        {"item": "Chaos rune", "quantity_range": (1, 6), "slots": 1},
                        {"item": "Death rune", "quantity_range": (1, 2), "slots": 1},
                        {"slots": 51},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Icefiend?oldid=6419875; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/demons/icefiend_level_13.plugin.kts; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/icefiend/icefiend_(13).json"
        ),
    },
    "pyrefiend": {
        "display_name": "Pyrefiend",
        "level": 43,
        "group": "Slayer",
        "required_slayer_level": 30,
        "attack_style": "magic_melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "max_hit": 44,
        "slayer_xp": 45.0,
        "stats": {
            "hitpoints": 450,
            "attack": 52,
            "strength": 30,
            "defence": 22,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 10,
            "defence_slash": 10,
            "defence_crush": 10,
            "defence_magic": 0,
            "defence_ranged": 10,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Impious ashes", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Steel hatchet", "quantity": 1, "slots": 4},
                        {"item": "Steel full helm", "quantity": 1, "slots": 4},
                        {"item": "Mithril chainbody", "quantity": 1, "slots": 2},
                        {"item": "Staff of fire", "quantity": 1, "slots": 3},
                        {"item": "Steel boots", "quantity": 1, "slots": 1},
                        {"item": "Adamant med helm", "quantity": 1, "slots": 1},
                        {"item": "Fire rune", "quantity": 30, "slots": 21},
                        {"item": "Fire rune", "quantity": 60, "slots": 8},
                        {"item": "Chaos rune", "quantity": 12, "slots": 5},
                        {"item": "Death rune", "quantity": 3, "slots": 3},
                        {"item": "Coins", "quantity": 10, "slots": 7},
                        {"item": "Coins", "quantity": 40, "slots": 24},
                        {"item": "Coins", "quantity": 120, "slots": 20},
                        {"item": "Coins", "quantity": 200, "slots": 10},
                        {"item": "Coins", "quantity": 450, "slots": 2},
                        {"item": "Gold ore", "quantity": 1, "slots": 8},
                        {"item": "Jug of wine", "quantity": 1, "slots": 2},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 3},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Pyrefiend?oldid=6565806; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/demons/pyrefiend_lvl_43.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/"
            "combat/formula/MeleeCombatFormula.kt"
        ),
        "source_status": (
            "period ordinary level-43 identity, LP, maximum hit, Slayer gate/XP, "
            "magic-based melee semantics, and guaranteed ash; game-main exact "
            "stats, speeds, bonuses, and 128-slot drops; level-48 God Wars, Soul "
            "Wars, Daemonheim, revenant, and familiar variants excluded"
        ),
    },
    "jelly": {
        "display_name": "Jelly",
        "level": 78,
        "group": "Slayer",
        "required_slayer_level": 52,
        "attack_style": "magic_melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 60,
        "slayer_xp": 75.0,
        "stats": {
            "hitpoints": 750,
            "attack": 45,
            "strength": 45,
            "defence": 120,
            "magic": 45,
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
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Coins", "quantity": 102, "slots": 39},
                        {"item": "Coins", "quantity": 44, "slots": 30},
                        {"item": "Steel battleaxe", "quantity": 1, "slots": 11},
                        {"item": "Coins", "quantity": 220, "slots": 10},
                        {"item": "Steel 2h sword", "quantity": 1, "slots": 7},
                        {"item": "Coins", "quantity": 11, "slots": 7},
                        {"item": "Chaos rune", "quantity": 15, "slots": 5},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 4},
                        {"item": "Steel hatchet", "quantity": 1, "slots": 3},
                        {"item": "Death rune", "quantity": 5, "slots": 3},
                        {"item": "Mithril kiteshield", "quantity": 1, "slots": 2},
                        {"item": "Coins", "quantity": 460, "slots": 2},
                        {"item": "Gold bar", "quantity": 1, "slots": 2},
                        {"item": "Mithril boots", "quantity": 1, "slots": 1},
                        {"item": "Rune full helm", "quantity": 1, "slots": 1},
                        {"item": "Thread", "quantity": 10, "slots": 1},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Jelly?oldid=6530513; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/jelly.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/jelly.json"
        ),
        "source_status": (
            "period exact ordinary level, LP, Slayer gate/XP, attack speed, "
            "magic-based melee semantics, and no guaranteed outside-Soul-Wars "
            "drop; Darkan exact stats, respawn, approximate-period max hit, and "
            "complete 128-slot ordinary drop table; Soul Wars variant excluded"
        ),
    },
    "infernal_mage": {
        "display_name": "Infernal Mage",
        "level": 66,
        "group": "Slayer",
        "required_slayer_level": 45,
        "attack_style": "magic",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 89,
        "slayer_xp": 60.0,
        "stats": {
            "hitpoints": 600,
            "attack": 1,
            "strength": 1,
            "defence": 60,
            "magic": 75,
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
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Darkan main",
                    "total": 64000,
                    "slots": (
                        {"item": "Coins", "quantity": 1, "slots": 9500},
                        {"item": "Death rune", "quantity": 7, "slots": 9000},
                        {"item": "Coins", "quantity": 2, "slots": 7000},
                        {"item": "Staff", "quantity": 1, "slots": 4000},
                        {"item": "Coins", "quantity": 4, "slots": 4000},
                        {"item": "Earth rune", "quantity": 10, "slots": 3000},
                        {"item": "Fire rune", "quantity": 10, "slots": 3000},
                        {"item": "Earth rune", "quantity": 36, "slots": 2000},
                        {"item": "Air rune", "quantity": 10, "slots": 1500},
                        {"item": "Water rune", "quantity": 10, "slots": 1500},
                        {"item": "Coins", "quantity": 29, "slots": 1500},
                        {"item": "Air rune", "quantity": 18, "slots": 1000},
                        {"item": "Water rune", "quantity": 18, "slots": 1000},
                        {"item": "Earth rune", "quantity": 18, "slots": 1000},
                        {"item": "Fire rune", "quantity": 18, "slots": 1000},
                        {"item": "Mind rune", "quantity": 18, "slots": 1000},
                        {"item": "Body rune", "quantity": 18, "slots": 1000},
                        {"item": "Blood rune", "quantity": 4, "slots": 1000},
                        {"item": "Staff of fire", "quantity": 1, "slots": 500},
                        {
                            "item": "Mystic boots (dark)",
                            "quantity": 1,
                            "slots": 125,
                        },
                        {
                            "item": "Mystic hat (dark)",
                            "quantity": 1,
                            "slots": 125,
                        },
                        {"item": "Lava battlestaff", "quantity": 1, "slots": 64},
                        {"slots": 10186},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Infernal_Mage?oldid=6446423; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "infernal_mage.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/infernal_mage.json"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer gate/XP, six-tick Magic "
            "attack, maximum hit, and guaranteed Bones; Darkan exact stats, "
            "respawn, and one exact 64,000-slot ordinary selector including the "
            "dark-mystic and Lava battlestaff rows; charm distribution remains "
            "source_blocked"
        ),
    },
    "otherworldly_being": {
        "display_name": "Otherworldly being",
        "level": 64,
        "group": "Slayer",
        "required_slayer_level": 1,
        "quest_gate": "lost_city",
        "quest_gate_label": "Complete Lost City",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 70,
        "slayer_xp": 66.0,
        "stats": {
            "hitpoints": 660,
            "attack": 56,
            "strength": 56,
            "defence": 46,
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
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Coins", "quantity": 15, "slots": 59},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 10},
                        {"item": "Nature rune", "quantity": 5, "slots": 9},
                        {"item": "Chaos rune", "quantity": 4, "slots": 8},
                        {"item": "Law rune", "quantity": 2, "slots": 7},
                        {"item": "Cosmic rune", "quantity": 2, "slots": 5},
                        {"item": "Death rune", "quantity": 2, "slots": 4},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 3},
                        {"item": "Ruby ring", "quantity": 1, "slots": 2},
                        {"item": "Blood rune", "quantity": 2, "slots": 1},
                        {"item": "Rune mace", "quantity": 1, "slots": 1},
                        {"item": "Mackerel", "quantity": 1, "slots": 1},
                        {"slots": 18},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Otherworldly_being?oldid=6554205; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/areas/zanaris/"
            "otherworldly_being.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/otherworldly_being.json"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer XP, six-tick melee, "
            "70-LP maximum hit, Vannaka membership, and Zanaris route; Darkan "
            "exact stats, respawn, and complete 128-slot ordinary table"
        ),
    },
    "shadow_warrior": {
        "display_name": "Shadow warrior",
        "level": 48,
        "group": "Slayer",
        "required_slayer_level": 1,
        "quest_gate": "legends_quest",
        "quest_gate_label": "Complete Legends' Quest",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 65,
        "slayer_xp": 67.0,
        "stats": {
            "hitpoints": 670,
            "attack": 36,
            "strength": 36,
            "defence": 33,
            "magic": 0,
            "ranged": 0,
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
        "drops": SHADOW_WARRIOR_DROPS,
        "source": (
            "https://runescape.wiki/w/Shadow_warrior?oldid=6555920; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "shadow_warrior (noanims).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/shadow_warrior.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer XP, six-tick melee, "
            "65-LP maximum hit, Vannaka/Chaeldar membership, Legends' Guild "
            "route, and no guaranteed drop; Darkan exact stats, respawn, one "
            "128-slot ordinary selector, and emulator-exact charm selection"
        ),
    },
}
