from __future__ import annotations

from ..contract import (
    DARKAN_GEM_DROP_TABLE,
    DARKAN_HERB_DROP_TABLE,
)

ELF_WARRIOR_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 128,
            "slots": (
                {"item": "Coins", "quantity": 44, "slots": 29},
                {"item": "Crystal teleport seed", "quantity": 1, "slots": 25},
                {"table": DARKAN_HERB_DROP_TABLE, "slots": 15},
                {"item": "Coins", "quantity": 180, "slots": 10},
                {"item": "Water rune", "quantity": 70, "slots": 8},
                {"item": "Nature rune", "quantity": 12, "slots": 5},
                {"item": "Coins", "quantity": 20, "slots": 5},
                {"table": DARKAN_GEM_DROP_TABLE, "slots": 5},
                {"item": "Green d'hide body", "quantity": 1, "slots": 4},
                {"item": "Green d'hide chaps", "quantity": 1, "slots": 3},
                {"item": "Law rune", "quantity": 2, "slots": 3},
                {"item": "Lobster", "quantity": 1, "slots": 3},
                {"item": "Shark", "quantity": 1, "slots": 3},
                {"item": "Mithril spear", "quantity": 1, "slots": 2},
                {"item": "Fire rune", "quantity": 37, "slots": 2},
                {"item": "Adamantite ore", "quantity": 1, "slots": 2},
                {"item": "Mithril kiteshield", "quantity": 1, "slots": 1},
                {"item": "Adamant full helm", "quantity": 1, "slots": 1},
                {"item": "Rune dagger", "quantity": 1, "slots": 1},
                {"slots": 1},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 1212,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 35},
                {"item": "Green charm", "quantity": 1, "slots": 227},
                {"item": "Crimson charm", "quantity": 1, "slots": 29},
                {"item": "Blue charm", "quantity": 1, "slots": 9},
                {"slots": 912},
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


ENEMIES = {
    "elf_warrior": {
        "display_name": "Elf warrior (ranged)",
        "level": 90,
        "group": "Elves",
        "attack_style": "ranged",
        "attack_speed": 6,
        "respawn_delay": 39,
        "max_hit": 116,
        "slayer_xp": 105.0,
        "quest_gate": "regicide",
        "stats": {
            "hitpoints": 1050,
            "attack": 1,
            "strength": 80,
            "defence": 1,
            "magic": 0,
            "ranged": 95,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 50,
            "defence_slash": 50,
            "defence_crush": 50,
            "defence_magic": 60,
            "defence_ranged": 70,
            "melee_strength": 0,
        },
        "drops": ELF_WARRIOR_DROPS,
        "source": (
            "https://runescape.wiki/w/Elf_warrior?oldid=6547078; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "elf_warrior/elf_warrior_(90).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/elf_warrior.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/utils/NPCClueDrops.java"
        ),
        "source_status": (
            "period exact level, LP, Slayer XP, six-tick ranged style, "
            "116-LP maximum, non-aggression, Regicide access, guaranteed "
            "Bones, Chaeldar assignment, and poison susceptibility; Darkan "
            "exact combat levels, bonuses, 39-tick respawn, one 128-slot "
            "ordinary selector, losslessly enumerated charm selector, and "
            "1/128 hard clue; the no-position target explicitly combines "
            "Lletya's crystal-seed roll and the Elf Camp charm channel as a "
            "location-flattening abstraction"
        ),
    },
    "elf_warrior_level_108": {
        "display_name": "Elf warrior (melee)",
        "level": 108,
        "group": "Elves",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 39,
        "max_hit": 109,
        "slayer_xp": 107.5,
        "quest_gate": "regicide",
        "stats": {
            "hitpoints": 1060,
            "attack": 95,
            "strength": 80,
            "defence": 95,
            "magic": 0,
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
        "drops": ELF_WARRIOR_DROPS,
        "source": (
            "https://runescape.wiki/w/Elf_warrior?oldid=6547078; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "elf_warrior/elf_warrior_(108).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/elf_warrior.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/utils/NPCClueDrops.java"
        ),
        "source_status": (
            "period exact level, 1,060 LP, 107.5 Slayer XP, six-tick melee, "
            "109-LP maximum, non-aggression, Regicide access, guaranteed "
            "Bones, Chaeldar assignment, and poison susceptibility; period "
            "visible LP and maximum override Darkan's conflicting 1,050/120, "
            "while Darkan supplies exact combat levels, bonuses, 39-tick "
            "respawn, one 128-slot ordinary selector, losslessly enumerated "
            "charm selector, and 1/128 hard clue; the no-position target "
            "explicitly combines Lletya's crystal-seed roll and the Elf Camp "
            "charm channel as a location-flattening abstraction"
        ),
    },
}
