from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
)
from ..contract import (
    COMBAT_MINOR_HERB_DROP_TABLE,
    COMBAT_UNCOMMON_SEED_DROP_TABLE,
    DARKAN_ABERRANT_RARE_SEED_DROP_TABLE,
    DARKAN_GEM_DROP_TABLE,
    DARKAN_HERB_DROP_TABLE,
)

ENEMIES = {
    "nechryael": {
        "display_name": "Nechryael",
        "level": 115,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 59,
        "slayer_xp": 105.0,
        "stats": {'hitpoints': 1050, 'attack': 97, 'strength': 97, 'defence': 105, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 20,
 'defence_slash': 20,
 'defence_crush': 20,
 'defence_magic': 0,
 'defence_ranged': 20,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Infernal ashes', 1),),
 'tables': ({'name': 'Main',
             'total': 624,
             'slots': ({'item': 'Rune full helm', 'quantity': 1, 'slots': 16},
                       {'item': 'Adamant platelegs', 'quantity': 1, 'slots': 16},
                       {'item': 'Mithril kiteshield', 'quantity': 1, 'slots': 16},
                       {'item': 'Rune boots', 'quantity': 1, 'slots': 4},
                       {'item': 'Dragon med helm', 'quantity': 1, 'slots': 1},
                       {'item': 'Rune sq shield', 'quantity': 1, 'slots': 1},
                       {'item': 'Steel 2h sword', 'quantity': 1, 'slots': 64},
                       {'item': 'Steel battleaxe', 'quantity': 1, 'slots': 64},
                       {'item': 'Steel hatchet', 'quantity': 1, 'slots': 64},
                       {'item': 'Rune 2h sword', 'quantity': 1, 'slots': 4},
                       {'item': 'Steel arrows', 'quantity': 1, 'slots': 4},
                       {'item': 'Rune arrows', 'quantity': 1, 'slots': 1},
                       {'item': 'Rune longsword', 'quantity': 1, 'slots': 2},
                       {'item': 'Rune battleaxe', 'quantity': 1, 'slots': 2},
                       {'item': 'Death rune', 'quantity': 1, 'slots': 64},
                       {'item': 'Chaos rune', 'quantity': 1, 'slots': 16},
                       {'item': 'Law rune', 'quantity': 45, 'slots': 4},
                       {'item': 'Nature rune', 'quantity': 68, 'slots': 4},
                       {'table': COMBAT_UNCOMMON_SEED_DROP_TABLE, 'slots': 80},
                       {'item': 'Coins', 'quantity': 1, 'slots': 64},
                       {'item': 'Tuna', 'quantity': 1, 'slots': 64},
                       {'item': 'Thread', 'quantity': 10, 'slots': 16},
                       {'item': 'Gold bar', 'quantity': 1, 'slots': 16},
                       {'item': 'Rune bar', 'quantity': 1, 'slots': 4},
                       {'item': 'Court summons', 'quantity': 1, 'slots': 4},
                       {'item': 'Clue scroll (hard)', 'quantity': 1, 'slots': 4},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 4},
                       {'item': 'Silver ore', 'quantity': 100, 'slots': 1},
                       {'slots': 16})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 90},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 40},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 310},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 11},
                       {'slots': 549})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/demons/nechryael_lvl_115.plugin.kts"
        ),
    },
    "bloodveld": {
        "display_name": "Bloodveld",
        "level": 76,
        "group": "Slayer",
        "required_slayer_level": 50,
        "attack_style": "magic_melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 59,
        "slayer_xp": 120.0,
        "stats": {
            "hitpoints": 1200,
            "attack": 75,
            "strength": 45,
            "defence": 30,
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
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Coins", "quantity": 120, "slots": 20},
                        {"item": "Coins", "quantity": 40, "slots": 29},
                        {"item": "Coins", "quantity": 200, "slots": 10},
                        {"item": "Bones", "quantity": 1, "slots": 10},
                        {"item": "Fire rune", "quantity": 60, "slots": 8},
                        {"item": "Coins", "quantity": 10, "slots": 7},
                        {"item": "Big bones", "quantity": 1, "slots": 7},
                        {"item": "Blood rune", "quantity": 10, "slots": 5},
                        {"item": "Steel hatchet", "quantity": 1, "slots": 4},
                        {"item": "Steel full helm", "quantity": 1, "slots": 4},
                        {"item": "Blood rune", "quantity": 3, "slots": 3},
                        {"item": "Big bones", "quantity": 3, "slots": 3},
                        {"item": "Meat pizza", "quantity": 1, "slots": 3},
                        {"item": "Steel scimitar", "quantity": 1, "slots": 2},
                        {"item": "Gold ore", "quantity": 1, "slots": 2},
                        {"item": "Black boots", "quantity": 1, "slots": 1},
                        {"item": "Mithril sq shield", "quantity": 1, "slots": 1},
                        {"item": "Mithril chainbody", "quantity": 1, "slots": 1},
                        {"item": "Rune med helm", "quantity": 1, "slots": 1},
                        {"item": "Blood rune", "quantity": 30, "slots": 1},
                        {"item": "Coins", "quantity": 450, "slots": 1},
                        {"slots": 5},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Bloodveld?oldid=6565794; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/bloodveld/"
            "bloodveld_(76).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/bloodveld.json"
        ),
        "source_status": (
            "period exact ordinary level-76 identity, LP, Slayer gate/XP, "
            "six-tick magic-based melee, maximum hit, and guaranteed Bones; "
            "Darkan exact stats, respawn, and complete 128-slot ordinary table; "
            "level-81 God Wars variant excluded"
        ),
    },
    "aberrant_spectre": {
        "display_name": "Aberrant spectre",
        "level": 96,
        "group": "Slayer",
        "required_slayer_level": 60,
        "quest_gate": "priest_in_peril",
        "quest_gate_label": "Complete Priest in Peril",
        "attack_style": "magic",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 119,
        "slayer_xp": 90.0,
        "protective_equipment": {
            "slot": "head",
            "items": (
                "Nose peg",
                "Slayer helmet",
                "Slayer helmet (charged)",
                "Slayer helmet (e)",
                "Full slayer helmet",
                "Full slayer helmet (charged)",
                "Full slayer helmet (e)",
            ),
            "warning": (
                "Missing Nose peg or a Slayer helmet in the head slot: "
                "Aberrant spectre stench deals fixed damage and drains one "
                "combat stat unless Protect from Magic is active."
            ),
            "unprotected_effect": {
                "damage": {
                    "kind": "max_lifepoints_fraction_capped",
                    "numerator": 1,
                    "denominator": 10,
                    "cap": 160,
                },
                "stat_drain_protection_prayer": "protect_magic",
                "stat_drain": {
                    "kind": "flat_to_floor",
                    "skills": (
                        "attack",
                        "defense",
                        "strength",
                        "ranged",
                        "prayer",
                        "magic",
                    ),
                    "amount": 5,
                    "floor": 0,
                    "selection": "random_one",
                },
            },
            "source_status": (
                "period exact protective headgear and unavoidable 160-LP "
                "unprotected maximum; Darkan exact max-LP/10 damage, random "
                "five-level combat-stat drain, and Protect from Magic drain block"
            ),
        },
        "stats": {
            "hitpoints": 900,
            "attack": 1,
            "strength": 1,
            "defence": 90,
            "magic": 105,
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
                    "total": 512,
                    "slots": (
                        {
                            "table": DARKAN_HERB_DROP_TABLE,
                            "slots": 312,
                        },
                        {
                            "table": DARKAN_ABERRANT_RARE_SEED_DROP_TABLE,
                            "slots": 76,
                        },
                        {
                            "table": DARKAN_GEM_DROP_TABLE,
                            "slots": 20,
                        },
                        {"item": "Steel hatchet", "quantity": 1, "slots": 12},
                        {
                            "item": "Mithril kiteshield",
                            "quantity": 1,
                            "slots": 4,
                        },
                        {"item": "Lava battlestaff", "quantity": 1, "slots": 4},
                        {"item": "Adamant platelegs", "quantity": 1, "slots": 4},
                        {"item": "Rune full helm", "quantity": 1, "slots": 4},
                        {"item": "Coins", "quantity": 460, "slots": 4},
                        {
                            "item": "Mystic robe bottom (dark)",
                            "quantity": 1,
                            "slots": 1,
                        },
                        {"slots": 71},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1212,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 97},
                        {"item": "Green charm", "quantity": 1, "slots": 25},
                        {"item": "Crimson charm", "quantity": 1, "slots": 15},
                        {"item": "Blue charm", "quantity": 1, "slots": 19},
                        {"slots": 1056},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Aberrant_spectre?oldid=6555339; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/content/skills/"
            "slayer/npcs/combat/AberrantSpectre.java; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "aberrant_spectre.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/aberrant_spectre.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java"
        ),
        "source_status": (
            "period exact ordinary identity, access, LP, Slayer gate/XP, "
            "six-tick Magic attack, protected and unprotected maximum hits, "
            "and protective-headgear behavior; Darkan exact stats, respawn, "
            "exact 512-slot ordinary selector and nested herb/seed/gem tables, "
            "and derived exact charm selector; zero defensive bonuses are "
            "source_blocked pending cutoff-era cache evidence"
        ),
    },
    "vampyre": {
        "display_name": "Vampyre",
        "level": 61,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 74,
        "slayer_xp": 40.0,
        "quest_gate": "priest_in_peril",
        "quest_gate_label": "Complete Priest in Peril",
        "stats": {
            "hitpoints": 400,
            "attack": 55,
            "strength": 60,
            "defence": 55,
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
        "weakening_equipment": {
            "slot": "neck",
            "items": ("Holy symbol",),
            "display_name": "Holy symbol",
            "enemy_accuracy_multiplier": 0.8,
            "enemy_damage_multiplier": 0.8,
            "source_status": (
                "period-authentic Holy symbol weakness; 20% enemy accuracy and "
                "maximum-hit reduction is a bounded abstraction"
            ),
        },
        "bite": {
            "chance_numerator": 1,
            "chance_denominator": 8,
            "max_heal": 20,
            "stat_drain_amount": 1,
            "stat_drain_floor": 1,
            "stat_drain_skills": (
                "attack",
                "strength",
                "defense",
                "ranged",
                "prayer",
                "magic",
                "runecrafting",
                "construction",
                "constitution",
                "agility",
                "herblore",
                "thieving",
                "crafting",
                "fletching",
                "slayer",
                "hunter",
                "mining",
                "smithing",
                "fishing",
                "cooking",
                "firemaking",
                "woodcutting",
                "farming",
                "summoning",
            ),
            "source_status": (
                "period-authentic occasional bite that drains a combat or "
                "non-combat stat and heals the Vampyre; 1/8 landed-hit chance, "
                "20 LP healing cap, and one-level random drain are bounded "
                "abstractions"
            ),
        },
        "drops": {
            "guaranteed": (("Vampyre dust", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 100000,
                    "slots": (
                        {"item": "Grimy marrentill", "quantity": 1, "slots": 20988},
                        {"item": "Death rune", "quantity": 2, "slots": 20988},
                        {"item": "Chaos rune", "quantity": 3, "slots": 20988},
                        {"item": "Coins", "quantity": 15, "slots": 20988},
                        {"item": "Grimy guam", "quantity": 1, "slots": 699},
                        {"item": "Grimy tarromin", "quantity": 1, "slots": 699},
                        {"item": "Grimy harralander", "quantity": 1, "slots": 699},
                        {"item": "Grimy ranarr", "quantity": 1, "slots": 699},
                        {"item": "Earth rune", "quantity": 4, "slots": 699},
                        {"item": "Blood rune", "quantity_range": (1, 2), "slots": 699},
                        {"item": "Black hatchet", "quantity": 1, "slots": 699},
                        {"item": "Limpwurt seed", "quantity": 1, "slots": 699},
                        {"item": "Jangerberry seed", "quantity": 1, "slots": 699},
                        {"item": "Whiteberry seed", "quantity": 1, "slots": 699},
                        {"item": "Poison ivy seed", "quantity": 1, "slots": 699},
                        {"item": "Belladonna seed", "quantity": 1, "slots": 699},
                        {
                            "item": "Bittercap mushroom spore",
                            "quantity_range": (1, 2),
                            "slots": 699,
                        },
                        {"item": "Marrentill seed", "quantity": 1, "slots": 699},
                        {"item": "Tarromin seed", "quantity": 1, "slots": 699},
                        {"item": "Harralander seed", "quantity": 1, "slots": 699},
                        {"item": "Toadflax seed", "quantity": 1, "slots": 699},
                        {"item": "Irit seed", "quantity": 1, "slots": 699},
                        {"item": "Wildblood seed", "quantity": 1, "slots": 699},
                        {"item": "Strawberry seed", "quantity": 1, "slots": 699},
                        {"item": "Grimy irit", "quantity": 1, "slots": 143},
                        {"item": "Grimy avantoe", "quantity": 1, "slots": 143},
                        {"item": "Grimy kwuarm", "quantity": 1, "slots": 143},
                        {"item": "Grimy cadantine", "quantity": 1, "slots": 143},
                        {"item": "Earth talisman", "quantity": 1, "slots": 143},
                        {"item": "Cactus seed", "quantity": 1, "slots": 143},
                        {"item": "Avantoe seed", "quantity": 1, "slots": 143},
                        {"item": "Kwuarm seed", "quantity": 1, "slots": 143},
                        {"item": "Dwarf weed seed", "quantity": 1, "slots": 143},
                        {"item": "Watermelon seed", "quantity": 1, "slots": 143},
                        {"item": "Spirit weed seed", "quantity": 1, "slots": 143},
                        {
                            "item": "Morchella mushroom spore",
                            "quantity": 2,
                            "slots": 143,
                        },
                        {"item": "Grimy dwarf weed", "quantity": 1, "slots": 37},
                        {"item": "Grimy lantadyme", "quantity": 1, "slots": 37},
                        {"item": "Ranarr seed", "quantity": 1, "slots": 37},
                        {"item": "Cadantine seed", "quantity": 1, "slots": 37},
                        {"item": "Lantadyme seed", "quantity": 1, "slots": 37},
                        {"slots": 167},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Feral_vampyre?oldid=6545273; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/vampyre/"
            "vampyre_(61).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/vampyre.json"
        ),
        "source_status": (
            "period ordinary level-61 Feral vampyre identity, LP, maximum hit, "
            "Slayer XP, attack speed, all-weapon vulnerability, Holy symbol "
            "weakness, occasional bite, and guaranteed Vampyre dust; Darkan "
            "exact stats and respawn; Darkan probability rows normalized "
            "losslessly to 100000 mutually exclusive slots with 167 empty "
            "slots; level-72/77, Juvinate, and Vyrewatch variants excluded"
        ),
    },
    "banshee": {
        "display_name": "Banshee",
        "level": 23,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 15,
        "slayer_xp": 22.0,
        "protective_equipment": {
            "slot": "head",
            "items": (
                "Earmuffs",
                "Masked earmuffs",
                "Slayer helmet",
                "Slayer helmet (charged)",
                "Slayer helmet (e)",
                "Full slayer helmet",
                "Full slayer helmet (charged)",
                "Full slayer helmet (e)",
            ),
            "warning": (
                "Missing Earmuffs or a Slayer helmet in the head slot: Banshee "
                "screams deal fixed damage and drain eight skills."
            ),
            "unprotected_effect": {
                "damage": {
                    "kind": "max_lifepoints_fraction_capped",
                    "numerator": 1,
                    "denominator": 10,
                    "cap": 80,
                },
                "stat_drain": {
                    "kind": "flat_to_floor",
                    "skills": (
                        "attack",
                        "strength",
                        "defense",
                        "ranged",
                        "prayer",
                        "magic",
                        "agility",
                        "summoning",
                    ),
                    "amount": 5,
                    "floor": 1,
                },
            },
            "source_status": (
                "abstraction/period+darkan: fixed max-LP/10 hit capped at the "
                "period 80 LP maximum; period eight-skill set uses Darkan's "
                "smallest surviving flat five-level drain magnitude"
            ),
        },
        "stats": {'hitpoints': 220, 'attack': 22, 'strength': 15, 'defence': 22, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 5,
 'defence_slash': 5,
 'defence_crush': 5,
 'defence_magic': 0,
 'defence_ranged': 5,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Bones', 1),),
 'tables': ({'name': 'Main',
             'total': 1148,
             'slots': ({'item': 'Iron dagger', 'quantity': 1, 'slots': 128},
                       {'item': 'Iron mace', 'quantity': 1, 'slots': 128},
                       {'item': 'Iron kiteshield', 'quantity': 1, 'slots': 128},
                       {'item': 'Adamant kiteshield', 'quantity': 1, 'slots': 4},
                       {'item': 'Mystic gloves', 'quantity': 1, 'slots': 8},
                       {'item': 'Mystic gloves', 'quantity': 1, 'slots': 2},
                       {'item': 'Air rune', 'quantity': 3, 'slots': 24},
                       {'item': 'Cosmic rune', 'quantity': 2, 'slots': 24},
                       {'item': 'Pure essence', 'quantity': 13, 'slots': 128},
                       {'item': 'Chaos rune', 'quantity': 7, 'slots': 8},
                       {'item': 'Fire rune', 'quantity': 7, 'slots': 8},
                       {'item': 'Coins', 'quantity': 13, 'slots': 84},
                       {'item': 'Fishing bait', 'quantity': 15, 'slots': 128},
                       {'item': 'Eye of newt', 'quantity': 1, 'slots': 8},
                       {'item': 'Iron ore', 'quantity': 1, 'slots': 8},
                       {'item': 'Clue scroll (easy)', 'quantity': 1, 'slots': 32},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 2},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 272},
                       {'slots': 8})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 3},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 7},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 1},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 1},
                       {'slots': 898})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/undeads/banshee_level_23.plugin.kts; "
            "https://runescape.wiki/w/Banshee?oldid=6589075; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "src/main/java/com/rs/game/content/skills/slayer/npcs/combat/BansheeCombat.java"
        ),
    },
}
