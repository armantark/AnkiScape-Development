from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
)
from ..contract import (
    COMBAT_ALLOTMENT_SEED_DROP_TABLE,
    COMBAT_GEM_DROP_TABLE,
    COMBAT_MINOR_HERB_DROP_TABLE,
)

TUROTH_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 100000,
            "slots": (
                {"item": "Grimy guam", "quantity": 1, "slots": 5597},
                {"item": "Grimy marrentill", "quantity": 1, "slots": 5597},
                {"item": "Grimy tarromin", "quantity": 1, "slots": 5597},
                {"item": "Grimy harralander", "quantity": 1, "slots": 5597},
                {"item": "Limpwurt root", "quantity": 1, "slots": 5597},
                {"item": "Law rune", "quantity": 3, "slots": 5597},
                {"item": "Coins", "quantity_range": (44, 440), "slots": 5597},
                {"item": "Steel platelegs", "quantity": 1, "slots": 5597},
                {"item": "Mithril kiteshield", "quantity": 1, "slots": 5597},
                {"item": "Mithril hatchet", "quantity": 1, "slots": 5597},
                {"item": "Poison ivy seed", "quantity": 1, "slots": 5597},
                {"item": "Cactus seed", "quantity": 1, "slots": 5597},
                {"item": "Belladonna seed", "quantity": 1, "slots": 5597},
                {"item": "Toadflax seed", "quantity": 1, "slots": 5597},
                {"item": "Irit seed", "quantity": 1, "slots": 5597},
                {"item": "Grimy ranarr", "quantity": 1, "slots": 1272},
                {"item": "Grimy irit", "quantity": 1, "slots": 1272},
                {"item": "Grimy avantoe", "quantity": 1, "slots": 1272},
                {"item": "Grimy kwuarm", "quantity": 1, "slots": 1272},
                {
                    "item": "Nature rune",
                    "quantity_range": (3, 15),
                    "slots": 1272,
                },
                {"item": "Adamant full helm", "quantity": 1, "slots": 1272},
                {"item": "Rune dagger", "quantity": 1, "slots": 1272},
                {"item": "Avantoe seed", "quantity": 1, "slots": 1272},
                {"item": "Snapdragon seed", "quantity": 1, "slots": 1272},
                {"item": "Cadantine seed", "quantity": 1, "slots": 1272},
                {
                    "item": "Morchella mushroom spore",
                    "quantity": 3,
                    "slots": 1272,
                },
                {"item": "Death rune", "quantity": 50, "slots": 186},
                {"item": "Grimy cadantine", "quantity": 1, "slots": 169},
                {"item": "Grimy dwarf weed", "quantity": 1, "slots": 169},
                {"item": "Grimy lantadyme", "quantity": 1, "slots": 169},
                {
                    "item": "Mystic robe bottom (light)",
                    "quantity": 1,
                    "slots": 169,
                    "source_item_id": 4113,
                },
                {"item": "Ranarr seed", "quantity": 1, "slots": 169},
                {"item": "Kwuarm seed", "quantity": 1, "slots": 169},
                {"item": "Lantadyme seed", "quantity": 1, "slots": 169},
                {"item": "Dwarf weed seed", "quantity": 1, "slots": 169},
                {"item": "Torstol seed", "quantity": 1, "slots": 169},
                {
                    "item": "Leaf-bladed sword",
                    "quantity": 1,
                    "slots": 169,
                    "source_item_id": 13290,
                },
                {"slots": 177},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 1212,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 34},
                {"item": "Green charm", "quantity": 1, "slots": 214},
                {"item": "Crimson charm", "quantity": 1, "slots": 22},
                {"item": "Blue charm", "quantity": 1, "slots": 6},
                {"slots": 936},
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
    "turoth": {
        "display_name": "Turoth",
        "level": 83,
        "group": "Slayer",
        "required_slayer_level": 55,
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 97,
        "poison_immune": True,
        "slayer_xp": 76.0,
        "stats": {
            "hitpoints": 760,
            "attack": 53,
            "strength": 83,
            "defence": 83,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 20,
            "defence_crush": 20,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "restricted_weapon": {
            "melee_weapons": ("Leaf-bladed spear", "Leaf-bladed sword"),
            "ranged_ammunition": ("Broad arrows", "Broad-tipped bolts"),
            "magic_spells": ("magic_dart",),
        },
        "drops": TUROTH_DROPS,
        "interaction_note": (
            "Turoths only take damage from a leaf-bladed spear or sword, "
            "Broad arrows or Broad-tipped bolts, or Magic Dart."
        ),
        "source": (
            "https://runescape.wiki/w/Turoth?oldid=6565315; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/turoth/"
            "turoth_(83).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/developer-information/npcListBonuses.txt:1630; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/content/items/"
            "CombatEnhancers.kt:136-156; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/turoth.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt:163; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java:"
            "51-94; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/utils/NPCClueDrops.java:160"
        ),
        "source_status": (
            "period exact ordinary level-83 identity, LP, Slayer gate/XP, "
            "passive six-tick melee, 97-LP maximum hit, and implemented effective "
            "weapon, ammunition, and spell routes; Darkan exact stats, bonuses, respawn, "
            "one exact 100,000-slot ordinary selector, executable 1,212-slot "
            "charm selector, and independent 1/128 hard clue"
        ),
    },
    "basilisk": {
        "display_name": "Basilisk",
        "level": 61,
        "group": "Slayer",
        "required_slayer_level": 40,
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 59,
        "slayer_xp": 75.0,
        "protective_equipment": {
            "slot": "shield",
            "items": ("Mirror shield",),
            "warning": (
                "Missing Mirror shield in the shield slot: Basilisk gaze "
                "deals fixed damage and drains one combat stat."
            ),
            "unprotected_effect": {
                "damage": {
                    "kind": "max_lifepoints_fraction_capped",
                    "numerator": 1,
                    "denominator": 10,
                    "cap": 120,
                },
                "protection_prayer_applies": True,
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
                    "floor": 1,
                    "selection": "random_one",
                },
            },
            "source_status": (
                "period exact shield requirement, 120-LP unprotected maximum, "
                "Protect from Melee damage block, and unavoidable stat drain; "
                "abstraction/darkan: fixed max-LP/10 hit and one random combat "
                "stat drained by five"
            ),
        },
        "stats": {
            "hitpoints": 750,
            "attack": 30,
            "strength": 45,
            "defence": 75,
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
                    "name": "Darkan main",
                    "total": 64000,
                    "slots": (
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 17500},
                        {"item": "Coins", "quantity": 44, "slots": 14000},
                        {"item": "Coins", "quantity": 200, "slots": 8500},
                        {"item": "Water rune", "quantity": 75, "slots": 4000},
                        {"item": "Nature rune", "quantity": 15, "slots": 2500},
                        {"item": "Coins", "quantity": 132, "slots": 2500},
                        {"item": "Coins", "quantity": 11, "slots": 2500},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 2500},
                        {"item": "Mithril hatchet", "quantity": 1, "slots": 1500},
                        {"item": "Steel battleaxe", "quantity": 1, "slots": 1500},
                        {"item": "Law rune", "quantity": 3, "slots": 1500},
                        {"item": "Adamantite ore", "quantity": 1, "slots": 1500},
                        {"item": "Mithril spear", "quantity": 1, "slots": 1000},
                        {"item": "Adamant full helm", "quantity": 1, "slots": 500},
                        {
                            "item": "Mithril kiteshield",
                            "quantity": 1,
                            "slots": 500,
                        },
                        {"item": "Rune dagger", "quantity": 1, "slots": 500},
                        {"item": "Nature rune", "quantity": 37, "slots": 500},
                        {"item": "Coins", "quantity": 440, "slots": 500},
                        {
                            "item": "Mystic hat (light)",
                            "quantity": 1,
                            "slots": 125,
                        },
                        {"item": "Basilisk head", "quantity": 1, "slots": 32},
                        {"slots": 343},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Basilisk?oldid=6565796; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/content/skills/"
            "slayer/npcs/combat/Basilisk.java; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "basilisk.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/basilisk.json"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer gate/XP, six-tick melee, "
            "protected and unprotected maximum hits, shield semantics, and "
            "guaranteed Bones; Darkan exact stats, respawn, and one exact "
            "64,000-slot ordinary selector including the light-mystic hat and "
            "Basilisk head rows; charm distribution remains source_blocked"
        ),
    },
    "gelatinous_abomination": {
        "display_name": "Gelatinous abomination",
        "level": 2,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 59,
        "max_hit": 16,
        "slayer_xp": 5.0,
        "stats": {
            "hitpoints": 50,
            "attack": 1,
            "strength": 1,
            "defence": 1,
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
        "finisher": {
            "item": "Spiked gauntlets",
            "threshold_lifepoints": 1,
            "consume": False,
            "must_be_worn": True,
            "action_label": "Crush with Spiked gauntlets",
            "source_status": (
                "period-exact worn, reusable lethal-hit requirement; the "
                "one-lifepoint threshold is the source's explicit fail state"
            ),
        },
        # The period page names common and uncommon drops but does not preserve
        # numerical rates, and the reconciled Darkan tree has no drop table.
        "drops": {"guaranteed": (), "tables": ()},
        "source": (
            "https://runescape.wiki/w/Gelatinous_abomination?oldid=6079671; "
            "https://runescape.wiki/w/Spiked_gauntlets?oldid=5827717; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/"
            "gelatinous_abomination (nostats) (noanims).json"
        ),
        "source_status": (
            "period LP, level, max hit, Slayer XP, style, and finisher; "
            "neutral combat stats are formula-constrained to combat level 2; "
            "numeric non-guaranteed drop rates source_blocked"
        ),
    },
    "young_grotworm": {
        "display_name": "Young grotworm",
        "level": 10,
        "group": "Slayer",
        "attack_style": "magic",
        "attack_speed": 4,
        "respawn_delay": 29,
        "max_hit": 20,
        "slayer_xp": 15.0,
        "stats": {
            "hitpoints": 150,
            "attack": 8,
            "strength": 8,
            "defence": 8,
            "magic": 10,
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
                    "total": 50000,
                    "slots": (
                        {"item": "Coal", "quantity": 1, "slots": 7009},
                        {"item": "Nature rune", "quantity": 1, "slots": 7009},
                        {"item": "Coins", "quantity": 100, "slots": 7009},
                        {"item": "Bronze spear", "quantity": 1, "slots": 7009},
                        {"item": "Coral bolts", "quantity": 20, "slots": 7009},
                        {"item": "Royal cape", "quantity": 1, "slots": 7009},
                        {"item": "Cod", "quantity": 1, "slots": 876},
                        {"item": "Mackerel", "quantity": 1, "slots": 876},
                        {"item": "Iron ore", "quantity": 1, "slots": 876},
                        {"item": "Silver ore", "quantity": 1, "slots": 876},
                        {"item": "Water rune", "quantity": 8, "slots": 876},
                        {"item": "Earth rune", "quantity": 8, "slots": 876},
                        {"item": "Mind rune", "quantity": 8, "slots": 876},
                        {"item": "Flax", "quantity": 4, "slots": 876},
                        {
                            "item": "Strength potion (1)",
                            "quantity": 1,
                            "slots": 467,
                        },
                        {
                            "item": "Attack potion (1)",
                            "quantity": 1,
                            "slots": 467,
                        },
                        {"slots": 4},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Young_grotworm?oldid=6490000; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/young_grotworm (nostats).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/drops/young_grotworm.json"
        ),
        "source_status": (
            "period LP, level, speeds, max hits, Slayer XP, style, and drop "
            "membership reconciled with one exact Darkan selector; neutral melee/defence "
            "stats are formula-constrained to combat level 10 and the single "
            "runtime style uses the source's ranged magic attack"
        ),
    },
    "cockatrice": {
        "display_name": "Cockatrice",
        "level": 37,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "slayer_xp": 37.0,
        "protective_equipment": {
            "slot": "shield",
            "items": ("Mirror shield",),
            "warning": (
                "Missing Mirror shield in the shield slot: Cockatrice eye beams "
                "deal fixed damage and stat drain."
            ),
            "unprotected_effect": {
                "damage": {
                    "kind": "max_lifepoints_fraction_capped",
                    "numerator": 1,
                    "denominator": 6,
                    "cap": 110,
                },
                "stat_drain": {
                    "kind": "base_fraction_to_floor",
                    "skills": ("attack", "strength", "defense", "ranged", "agility"),
                    "numerator": 1,
                    "denominator": 4,
                    "floor_numerator": 1,
                    "floor_denominator": 4,
                },
            },
            "source_status": (
                "abstraction/darkan+period+game-main: fixed max-LP-scaled hit "
                "capped at the period 110 LP maximum; 25%-of-base drains stop at "
                "the period one-quarter floor"
            ),
        },
        "stats": {'hitpoints': 370, 'attack': 22, 'strength': 37, 'defence': 37, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 10,
 'defence_slash': 10,
 'defence_crush': 0,
 'defence_magic': 10,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Bones', 1),),
 'tables': ({'name': 'Main',
             'total': 512,
             'slots': ({'item': 'Iron sword', 'quantity': 1, 'slots': 12},
                       {'item': 'Steel dagger', 'quantity': 1, 'slots': 12},
                       {'item': 'Iron boots', 'quantity': 1, 'slots': 4},
                       {'item': 'Iron javelin', 'quantity': 1, 'slots': 4},
                       {'item': 'Steel longsword', 'quantity': 1, 'slots': 4},
                       {'item': 'Mystic boots', 'quantity': 1, 'slots': 1},
                       {'item': 'Nature rune', 'quantity': 2, 'slots': 24},
                       {'item': 'Nature rune', 'quantity': 4, 'slots': 16},
                       {'item': 'Nature rune', 'quantity': 6, 'slots': 8},
                       {'item': 'Law rune', 'quantity': 2, 'slots': 12},
                       {'item': 'Water rune', 'quantity': 2, 'slots': 8},
                       {'item': 'Fire rune', 'quantity': 7, 'slots': 8},
                       {'table': COMBAT_ALLOTMENT_SEED_DROP_TABLE, 'slots': 72},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 40},
                       {'item': 'Coins', 'quantity': 15, 'slots': 64},
                       {'item': 'Coins', 'quantity': 5, 'slots': 48},
                       {'item': 'Coins', 'quantity': 28, 'slots': 48},
                       {'item': 'Coins', 'quantity': 62, 'slots': 16},
                       {'item': 'Coins', 'quantity': 42, 'slots': 12},
                       {'item': 'Coins', 'quantity': 1, 'slots': 4},
                       {'slots': 3},
                       {'item': 'Limpwurt root', 'quantity': 1, 'slots': 84},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 8})},
            {'name': 'Tertiary',
             'total': 1000,
             'slots': ({'item': 'Cockatrice egg', 'quantity': 1, 'slots': 256},
                       {'item': 'Cockatrice head', 'quantity': 1, 'slots': 1},
                       {'slots': 743})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 90},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 10},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 5},
                       {'slots': 875})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/cockatrice_level_37.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/"
            "scripts/impl/CockatriceCombatScript.kt; "
            "Darkan CockatriceCombat.java; RuneScape Wiki Cockatrice oldid 6579848"
        ),
    },
}
