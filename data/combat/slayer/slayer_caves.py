from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
    LIT_LIGHT_SOURCE_ITEMS,
)
from ..contract import (
    COMBAT_ALLOTMENT_SEED_DROP_TABLE,
    COMBAT_GEM_DROP_TABLE,
    COMBAT_MINOR_HERB_DROP_TABLE,
    DARKAN_ABERRANT_RARE_SEED_DROP_TABLE,
    DARKAN_GEM_DROP_TABLE,
    DARKAN_HERB_DROP_TABLE,
    DARKAN_VARIABLE_ALLOTMENT_DROP_TABLE,
)

CAVE_HORROR_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 128,
            "slots": (
                {"item": "Coins", "quantity": 44, "slots": 28},
                {
                    "table": DARKAN_ABERRANT_RARE_SEED_DROP_TABLE,
                    "slots": 18,
                },
                {
                    "table": DARKAN_VARIABLE_ALLOTMENT_DROP_TABLE,
                    "slots": 15,
                },
                {"table": DARKAN_HERB_DROP_TABLE, "slots": 13},
                {"item": "Coins", "quantity": 132, "slots": 12},
                {"item": "Limpwurt root", "quantity": 1, "slots": 7},
                {"item": "Teak logs", "quantity": 4, "slots": 7},
                {"item": "Nature rune", "quantity": 6, "slots": 6},
                {"item": "Nature rune", "quantity": 4, "slots": 5},
                {"table": DARKAN_GEM_DROP_TABLE, "slots": 5},
                {"item": "Mithril hatchet", "quantity": 1, "slots": 3},
                {"item": "Mahogany logs", "quantity": 2, "slots": 3},
                {"item": "Rune dagger", "quantity": 1, "slots": 1},
                {"item": "Adamant full helm", "quantity": 1, "slots": 1},
                {"item": "Mithril kiteshield", "quantity": 1, "slots": 1},
                {"item": "Nature rune", "quantity": 3, "slots": 1},
                {"item": "Coins", "quantity": 440, "slots": 1},
                {"slots": 1},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 1212,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 28},
                {"item": "Green charm", "quantity": 1, "slots": 10},
                {"item": "Crimson charm", "quantity": 1, "slots": 136},
                {"item": "Blue charm", "quantity": 1, "slots": 6},
                {"slots": 1032},
            ),
        },
        {
            "name": "Long and curved bones",
            "total": 100000,
            "slots": (
                {"item": "Long bone", "quantity": 1, "slots": 250},
                {"item": "Curved bone", "quantity": 1, "slots": 20},
                {"slots": 99730},
            ),
        },
        {
            "name": "Black mask (10)",
            "total": 512,
            "slots": (
                {"item": "Black mask (10)", "quantity": 1, "slots": 1},
                {"slots": 511},
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
    "cave_horror": {
        "display_name": "Cave horror",
        "level": 80,
        "group": "Slayer",
        "required_slayer_level": 58,
        "quest_gate": "cabin_fever",
        "quest_gate_label": "Complete Cabin Fever",
        "required_item_options": (LIT_LIGHT_SOURCE_ITEMS,),
        "required_item_options_label": (
            "One lit light source in inventory or equipped for Mos Le'Harmless "
            "Caves"
        ),
        "light_source": {"accepted_items": LIT_LIGHT_SOURCE_ITEMS},
        "attack_style": "magic_melee",
        "attack_speed": 4,
        "respawn_delay": 39,
        "max_hit": 90,
        "slayer_xp": 55.0,
        "stats": {
            "hitpoints": 550,
            "attack": 80,
            "strength": 77,
            "defence": 62,
            "magic": 80,
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
        "protective_equipment": {
            "alternatives": (
                {"slot": "neck", "items": ("Witchwood icon",)},
                {
                    "slot": "head",
                    "items": (
                        "Slayer helmet",
                        "Slayer helmet (charged)",
                        "Slayer helmet (e)",
                        "Full slayer helmet",
                        "Full slayer helmet (charged)",
                        "Full slayer helmet (e)",
                    ),
                },
            ),
            "applies_to_player_classes": ("melee",),
            "warning": (
                "Missing a Witchwood icon or Slayer helmet for close combat: "
                "each Cave horror scream deals 87 LP and drains one combat "
                "stat by 5."
            ),
            "unprotected_effect": {
                "damage": {"kind": "fixed", "amount": 87},
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
                    "floor": 0,
                    "selection": "random_one",
                },
            },
            "source_status": (
                "period exact close-combat equipment consequence, safespot "
                "exception, stat-drain magnitude, and Protect/Deflect Melee "
                "damage prevention; 87 LP is the conservative upper endpoint "
                "of the cutoff page's 86-87 range"
            ),
        },
        "drops": CAVE_HORROR_DROPS,
        "source": (
            "https://runescape.wiki/w/Cave_horror?oldid=6550392; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/content/skills/"
            "slayer/npcs/combat/CaveHorrorCombat.java; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "cave_horror (noanims).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/cave_horror.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/utils/NPCClueDrops.java"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer gate/XP, four-to-five-"
            "tick magical melee, aggression, poison behavior, "
            "light/Cabin-Fever access, Witchwood/Slayer-helmet protection, "
            "scream consequence, and ranged safespot exception; four ticks "
            "uses the conservative lower sourced cadence endpoint and the "
            "approximate period 94-LP ordinary maximum is represented by "
            "Darkan's exact 90; Darkan exact stats, zero bonuses, 39-tick "
            "respawn, 128-slot ordinary selector with one empty slot, exact "
            "nested tables, losslessly enumerated charms, long/curved bones, "
            "1/512 Black mask (10), and 1/128 hard clue; "
            "locations excluded and standard reciprocal ranged combat remains "
            "the no-position AnkiScape abstraction"
        ),
    },
    "wall_beast": {
        "display_name": "Wall beast",
        "level": 49,
        "group": "Slayer",
        "required_slayer_level": 35,
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 39,
        "max_hit": 44,
        "poison_immune": True,
        "slayer_xp": 105.0,
        "stats": {
            "hitpoints": 1050,
            "attack": 30,
            "strength": 30,
            "defence": 16,
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
        "start_equipment": {
            "slot": "head",
            "items": ("Spiny helmet",),
            "warning": "Equip a Spiny helmet to start fighting Wall beasts",
            "source_status": (
                "period-exact start-only helmet gate; other equivalent helmets "
                "remain excluded until their equipment identities are live"
            ),
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 100000,
                    "slots": (
                        {"item": "Grimy guam", "quantity": 1, "slots": 6458},
                        {"item": "Grimy marrentill", "quantity": 1, "slots": 6458},
                        {"item": "Grimy tarromin", "quantity": 1, "slots": 6458},
                        {"item": "Grimy harralander", "quantity": 1, "slots": 6458},
                        {"item": "Bones", "quantity": 1, "slots": 12985},
                        {"item": "Air rune", "quantity": 3, "slots": 6458},
                        {"item": "Tinderbox", "quantity": 1, "slots": 6458},
                        {"item": "Unlit torch", "quantity": 1, "slots": 6458},
                        {"item": "Coins", "quantity": 15, "slots": 6458},
                        {"item": "Steel full helm", "quantity": 1, "slots": 6458},
                        {"item": "Lantern lens", "quantity": 1, "slots": 6458},
                        {
                            "item": "Bullseye lantern (unf)",
                            "quantity": 1,
                            "slots": 6458,
                        },
                        {"item": "Grimy kwuarm", "quantity": 1, "slots": 4664},
                        {"item": "Grimy cadantine", "quantity": 1, "slots": 4664},
                        {"item": "Eye of newt", "quantity": 1, "slots": 4664},
                        {"item": "Grimy ranarr", "quantity": 1, "slots": 310},
                        {"item": "Grimy irit", "quantity": 1, "slots": 310},
                        {"item": "Grimy avantoe", "quantity": 1, "slots": 310},
                        {"item": "Chaos rune", "quantity_range": (3, 7), "slots": 310},
                        {"item": "Cosmic rune", "quantity": 2, "slots": 310},
                        {"item": "Mystic hat", "quantity": 1, "slots": 310},
                        {"item": "Grimy dwarf weed", "quantity": 1, "slots": 23},
                        {"item": "Bronze full helm", "quantity": 1, "slots": 23},
                        {"item": "Mithril full helm", "quantity": 1, "slots": 23},
                        {"item": "Black full helm", "quantity": 1, "slots": 23},
                        {"item": "Grimy lantadyme", "quantity": 1, "slots": 23},
                        {"slots": 10},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Wall_beast?oldid=6079584; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "wall_beast (noanims).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/wall_beast.json"
        ),
        "source_status": (
            "period ordinary level-49 identity, LP, maximum hit, Slayer gate/XP, "
            "assignment membership, and start-only helmet behavior; stable "
            "four-tick melee fill from the modern page with no recorded rate "
            "change; Darkan exact stats and respawn; Darkan probability rows "
            "normalized losslessly to 100000 mutually exclusive slots with 10 "
            "empty slots; navigation-only unhelmeted grab excluded"
        ),
    },
    "cave_crawler": {
        "display_name": "Cave crawler",
        "level": 23,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "poison_damage": 8,
        "slayer_xp": 22.0,
        "stats": {'hitpoints': 220, 'attack': 22, 'strength': 18, 'defence': 18, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 10,
 'defence_slash': 10,
 'defence_crush': 5,
 'defence_magic': 5,
 'defence_ranged': 10,
 'melee_strength': 0},
        "drops": {'guaranteed': (),
 'tables': ({'name': 'Main',
             'total': 128,
             'slots': ({'item': 'Bronze boots', 'quantity': 1, 'slots': 1},
                       {'item': 'Nature rune', 'quantity_range': (3, 4), 'slots': 6},
                       {'item': 'Fire rune', 'quantity': 12, 'slots': 5},
                       {'item': 'Earth rune', 'quantity': 12, 'slots': 2},
                       {'table': COMBAT_ALLOTMENT_SEED_DROP_TABLE, 'slots': 26},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 22},
                       {'item': 'Vial of water', 'quantity': 1, 'slots': 13},
                       {'item': 'White berries', 'quantity': 1, 'slots': 5},
                       {'item': 'Unicorn horn dust', 'quantity': 1, 'slots': 2},
                       {'item': 'Eye of newt', 'quantity': 1, 'slots': 1},
                       {'item': "Red spiders' eggs", 'quantity': 1, 'slots': 1},
                       {'item': 'Limpwurt root', 'quantity': 1, 'slots': 1},
                       {'item': 'Snape grass', 'quantity': 1, 'slots': 1},
                       {'item': 'Coins', 'quantity': 3, 'slots': 5},
                       {'item': 'Coins', 'quantity': 8, 'slots': 3},
                       {'item': 'Coins', 'quantity': 29, 'slots': 3},
                       {'item': 'Coins', 'quantity': 10, 'slots': 1},
                       {'slots': 29},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 1})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 90},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 10},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 5},
                       {'slots': 875})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/cave_crawler_lvl_23.plugin.kts: poisonDamage=8"
        ),
    },
    "cave_bug": {
        "display_name": "Cave bug",
        "level": 6,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "slayer_xp": 5.0,
        "stats": {'hitpoints': 50, 'attack': 6, 'strength': 5, 'defence': 6, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 10,
 'defence_slash': 10,
 'defence_crush': 5,
 'defence_magic': 5,
 'defence_ranged': 10,
 'melee_strength': 0},
        "drops": {'guaranteed': (),
 'tables': ({'name': 'Main',
             'total': 128,
             'slots': ({'item': 'Water rune', 'quantity': 8, 'slots': 5},
                       {'item': 'Nature rune', 'quantity': 1, 'slots': 5},
                       {'item': 'Earth rune', 'quantity': 6, 'slots': 2},
                       {'item': 'Nature rune', 'quantity': 2, 'slots': 1},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 23},
                       {'item': 'Unicorn horn dust', 'quantity': 1, 'slots': 2},
                       {'item': 'Eye of newt', 'quantity': 1, 'slots': 2},
                       {'item': "Red spiders' eggs", 'quantity': 1, 'slots': 2},
                       {'item': 'Limpwurt root', 'quantity': 1, 'slots': 1},
                       {'item': 'Snape grass', 'quantity': 1, 'slots': 1},
                       {'item': 'Coins', 'quantity': 3, 'slots': 8},
                       {'item': 'Coins', 'quantity': 8, 'slots': 3},
                       {'slots': 64},
                       {'item': 'Candle', 'quantity': 1, 'slots': 5},
                       {'item': 'Tinderbox', 'quantity': 1, 'slots': 3},
                       {'item': 'Candle lantern (empty)', 'quantity': 1, 'slots': 1})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 90},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 10},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 5},
                       {'slots': 875})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/cave_bug_lvl_6.plugin.kts"
        ),
    },
    "cave_slime": {
        "display_name": "Cave slime",
        "level": 23,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "poison_damage": 3,
        "slayer_xp": 25.0,
        "stats": {'hitpoints': 250, 'attack': 13, 'strength': 13, 'defence': 35, 'magic': 13, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 0,
 'defence_slash': 0,
 'defence_crush': 0,
 'defence_magic': 0,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Swamp tar', 1),),
 'tables': ({'name': 'Main',
             'total': 128,
             'slots': ({'item': 'Bronze hatchet', 'quantity': 1, 'slots': 3},
                       {'item': 'Iron sword', 'quantity': 1, 'slots': 7},
                       {'item': 'Bronze full helm', 'quantity': 1, 'slots': 1},
                       {'item': 'Iron kiteshield', 'quantity': 1, 'slots': 2},
                       {'item': 'Iron boots', 'quantity': 1, 'slots': 1},
                       {'item': 'Water rune', 'quantity': 15, 'slots': 5},
                       {'item': 'Earth rune', 'quantity': 5, 'slots': 3},
                       {'item': 'Coins', 'quantity': 1, 'slots': 7},
                       {'item': 'Coins', 'quantity': 4, 'slots': 30},
                       {'item': 'Coins', 'quantity': 10, 'slots': 39},
                       {'item': 'Coins', 'quantity': 22, 'slots': 10},
                       {'item': 'Coins', 'quantity': 46, 'slots': 2},
                       {'item': 'Unlit torch', 'quantity': 1, 'slots': 11},
                       {'item': 'Oil lantern frame', 'quantity': 1, 'slots': 1},
                       {'item': 'Gold bar', 'quantity': 1, 'slots': 2},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 4})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 90},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 10},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 5},
                       {'slots': 875})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/cave_slime_lvl_23.plugin.kts: poisonDamage=3"
        ),
    },
    "crawling_hand": {
        "display_name": "Crawling hand",
        "level": 8,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "slayer_xp": 16.0,
        "stats": {'hitpoints': 160, 'attack': 8, 'strength': 4, 'defence': 4, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 0,
 'defence_slash': 0,
 'defence_crush': 0,
 'defence_magic': 0,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Bones', 1),),
 'tables': ({'name': 'Main',
             'total': 512,
             'slots': ({'item': 'Leather gloves', 'quantity': 1, 'slots': 64},
                       {'item': 'Gloves', 'quantity': 1, 'slots': 16},
                       {'item': 'Gloves', 'quantity': 1, 'slots': 16},
                       {'item': 'Gloves', 'quantity': 1, 'slots': 16},
                       {'item': 'Gloves', 'quantity': 1, 'slots': 16},
                       {'item': 'Gloves', 'quantity': 1, 'slots': 16},
                       {'item': 'Mystic gloves', 'quantity': 1, 'slots': 1},
                       {'item': 'Gold ring', 'quantity': 1, 'slots': 16},
                       {'item': 'Sapphire ring', 'quantity': 1, 'slots': 16},
                       {'item': 'Emerald ring', 'quantity': 1, 'slots': 16},
                       {'item': 'Ruby ring', 'quantity': 1, 'slots': 16},
                       {'item': 'Coins', 'quantity': 5, 'slots': 16},
                       {'item': 'Coins', 'quantity': 8, 'slots': 16},
                       {'item': 'Coins', 'quantity': 312, 'slots': 16},
                       {'item': 'Ashes', 'quantity': 1, 'slots': 16},
                       {'item': 'Hand bone', 'quantity': 1, 'slots': 16},
                       {'item': 'Crawling hand', 'quantity': 1, 'slots': 1},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 1},
                       {'slots': 218})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 96},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 6},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 6},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 2},
                       {'slots': 890})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/crawling_hand_level_8.plugin.kts; "
            "RuneScape Wiki Crawling hand oldid 6530506"
        ),
    },
}
