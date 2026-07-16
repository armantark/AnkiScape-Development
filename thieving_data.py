"""Source-backed pre-EOC Thieving targets.

Loot rows use ``(item, minimum, maximum, slots)`` tuples.  A zero ``slots``
value marks a guaranteed drop.  All 2011Scape values are transcribed from the
two implementation enums cited on each row; wiki-only and Darkan-only additions
are labelled explicitly.
"""

from __future__ import annotations


PICKPOCKET_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/"
    "plugins/content/skills/thieving/pickpocketing/PickpocketTarget.kt"
)
STALL_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/"
    "plugins/content/skills/thieving/stalls/StallTarget.kt"
)
MULTIPICK_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/"
    "plugins/content/skills/thieving/pickpocketing/Pickpocketing.kt:97-113"
)

DEFAULT_THIEVING_TARGET = "pickpocket_man"
THIEVING_GROUP_ORDER = ("pickpocketing", "stalls", "safes", "blackjacking")
THIEVING_GROUP_LABELS = {
    "pickpocketing": "Pickpocketing",
    "stalls": "Stalls",
    "safes": "Safes",
    "blackjacking": "Blackjacking",
}


def _pick(name, level, low, high, xp, damage, stun, *, guaranteed=(), total=0, loot=(), source_lines=""):
    return {
        "display_name": name,
        "kind": "pickpocket",
        "group": "pickpocketing",
        "level": level,
        "min_chance": low,
        "max_chance": high,
        "xp": xp,
        "damage_min": damage[0],
        "damage_max": damage[1],
        "stun_ticks": stun,
        "guaranteed": tuple(guaranteed),
        "loot_total": total,
        "loot": tuple(loot),
        "source": f"{PICKPOCKET_SOURCE}:{source_lines}",
        "multi_pick_source": MULTIPICK_SOURCE,
        "source_status": "provisional/2011Scape",
    }


HAM_LOOT = (
    ("Bronze arrow", 1, 13, 33), ("Bronze hatchet", 1, 1, 33),
    ("Bronze dagger", 1, 1, 33), ("Bronze pickaxe", 1, 1, 33),
    ("Iron hatchet", 1, 1, 33), ("Iron dagger", 1, 1, 33),
    ("Iron pickaxe", 1, 1, 33), ("Leather body", 1, 1, 33),
    ("Steel arrow", 1, 13, 22), ("Steel hatchet", 1, 1, 22),
    ("Steel dagger", 1, 1, 22), ("Steel pickaxe", 1, 1, 22),
    ("H.A.M. boots", 1, 1, 11), ("H.A.M. cloak", 1, 1, 11),
    ("H.A.M. gloves", 1, 1, 11), ("H.A.M. hood", 1, 1, 11),
    ("H.A.M. logo", 1, 1, 11), ("H.A.M. robe", 1, 1, 11),
    ("H.A.M. shirt", 1, 1, 11), ("Coins", 1, 21, 165),
    ("Buttons", 1, 1, 44), ("Damaged armour", 1, 1, 44),
    ("Rusty sword", 1, 1, 44), ("Feather", 1, 7, 33),
    ("Logs", 1, 1, 33), ("Thread", 1, 10, 33),
    ("Cowhide", 1, 1, 33), ("Knife", 1, 1, 22),
    ("Needle", 1, 1, 22), ("Raw anchovies", 1, 1, 22),
    ("Raw chicken", 1, 1, 22), ("Tinderbox", 1, 1, 22),
    ("Uncut opal", 1, 1, 22), ("Clue scroll (easy)", 1, 1, 22),
    ("Coal", 1, 1, 22), ("Iron ore", 1, 1, 22),
    ("Uncut jade", 1, 1, 22), ("Grimy guam", 1, 1, 12),
    ("Grimy marrentill", 1, 1, 6), ("Grimy tarromin", 1, 1, 4),
)

MASTER_FARMER_LOOT = (
    ("Potato seed", 1, 4, 400), ("Onion seed", 1, 3, 300),
    ("Cabbage seed", 1, 3, 150), ("Tomato seed", 1, 2, 140),
    ("Sweetcorn seed", 1, 2, 50), ("Strawberry seed", 1, 1, 25),
    ("Watermelon seed", 1, 1, 15), ("Barley seed", 1, 12, 120),
    ("Hammerstone seed", 1, 9, 120), ("Asgarnian seed", 1, 6, 90),
    ("Jute seed", 1, 9, 90), ("Yanillian seed", 1, 6, 60),
    ("Krandorian seed", 1, 6, 30), ("Wildblood seed", 1, 3, 15),
    ("Marigold seed", 1, 1, 100), ("Nasturtium seed", 1, 1, 70),
    ("Rosemary seed", 1, 1, 40), ("Woad seed", 1, 1, 30),
    ("Limpwurt seed", 1, 1, 25), ("Redberry seed", 1, 1, 85),
    ("Cadavaberry seed", 1, 1, 60), ("Dwellberry seed", 1, 1, 40),
    ("Jangerberry seed", 1, 1, 20), ("Whiteberry seed", 1, 1, 7),
    ("Poison ivy seed", 1, 1, 3), ("Guam seed", 1, 1, 30),
    ("Marrentill seed", 1, 1, 25), ("Tarromin seed", 1, 1, 15),
    ("Harralander seed", 1, 1, 10), ("Ranarr seed", 1, 1, 8),
    ("Toadflax seed", 1, 1, 5), ("Irit seed", 1, 1, 3),
    ("Avantoe seed", 1, 1, 2), ("Kwuarm seed", 1, 1, 2),
    ("Snapdragon seed", 1, 1, 1), ("Cadantine seed", 1, 1, 1),
    ("Lantadyme seed", 1, 1, 1), ("Dwarf weed seed", 1, 1, 1),
    ("Torstol seed", 1, 1, 1), ("Bittercap mushroom spore", 1, 1, 5),
    ("Belladonna seed", 1, 1, 3), ("Cactus seed", 1, 1, 1),
)

PICKPOCKET_TARGETS = {
    "pickpocket_man": _pick("Man / Woman", 1, 180, 240, 8.0, (10, 10), 8, guaranteed=(("Coins", 3),), source_lines="63-74"),
    "pickpocket_farmer": _pick("Farmer", 10, 150, 240, 14.5, (10, 10), 8, guaranteed=(("Coins", 3),), total=256, loot=(("Coins", 9, 9, 246), ("Potato seed", 1, 1, 10)), source_lines="76-95"),
    "pickpocket_female_ham": _pick("Female H.A.M. member", 15, 135, 240, 18.5, (10, 30), 7, total=1100, loot=HAM_LOOT, source_lines="97-150"),
    "pickpocket_male_ham": _pick("Male H.A.M. member", 20, 117, 240, 22.5, (10, 30), 7, total=1100, loot=HAM_LOOT, source_lines="159-212"),
    "pickpocket_warrior": _pick("Warrior", 25, 100, 240, 26.0, (20, 20), 8, guaranteed=(("Coins", 18),), source_lines="221-234"),
    "pickpocket_rogue": _pick("Rogue", 32, 74, 240, 36.5, (20, 20), 8, total=128, loot=(("Coins",25,40,108),("Iron dagger (p)",1,1,1),("Air rune",8,8,8),("Jug of wine",1,1,6),("Lockpick",1,1,5)), source_lines="236-254"),
    "pickpocket_cave_goblin": _pick("Cave goblin", 36, 72, 240, 40.0, (10, 10), 8, total=20, loot=(("Coins",10,50,7),("Bat shish",1,1,1),("Coated frog's legs",1,1,1),("Fingers",1,1,1),("Frogburger",1,1,1),("Frogspawn gumbo",1,1,1),("Green gloop soup",1,1,1),("Bullseye lantern (unlit)",1,1,1),("Cave goblin wire",1,1,1),("Oil lantern (unlit)",1,1,1),("Swamp tar",1,1,1),("Tinderbox",1,1,1),("Unlit torch",1,1,1),("Iron ore",1,4,1)), source_lines="256-286"),
    "pickpocket_master_farmer": _pick("Master farmer", 38, 90, 240, 43.0, (30, 30), 8, total=2199, loot=MASTER_FARMER_LOOT, source_lines="288-343"),
    "pickpocket_guard": _pick("Guard", 40, 50, 240, 46.8, (20, 20), 8, guaranteed=(("Coins",30),), source_lines="346-391"),
    "pickpocket_fremennik": _pick("Fremennik citizen", 45, 65, 240, 65.0, (20, 20), 8, guaranteed=(("Coins",40),), source_lines="393-412"),
    "pickpocket_desert_bandit": _pick("Desert bandit", 53, 50, 240, 79.4, (30, 30), 8, total=7, loot=(("Coins",30,30,5),("Antipoison (1)",1,1,1),("Lockpick",1,1,1)), source_lines="414-438"),
    "pickpocket_ardougne_knight": _pick("Knight of Ardougne", 55, 50, 240, 84.3, (30, 30), 8, guaranteed=(("Coins",50),), source_lines="440-459"),
    "pickpocket_watchman": _pick("Yanille watchman", 65, 15, 160, 137.5, (30, 30), 8, guaranteed=(("Coins",60),("Bread",1)), source_lines="461-481"),
    "pickpocket_paladin": _pick("Paladin", 70, 50, 150, 151.8, (30, 30), 8, guaranteed=(("Coins",80),("Chaos rune",2)), source_lines="483-503"),
    "pickpocket_gnome": _pick("Gnome", 75, 8, 120, 198.3, (10, 10), 8, total=128, loot=(("King worm",1,1,55),("Coins",300,300,30),("Swamp toad",1,1,28),("Gold ore",1,1,8),("Earth rune",1,1,5),("Fire orb",1,1,2)), source_lines="505-532"),
    "pickpocket_hero": _pick("Hero", 80, 6, 100, 273.3, (40, 40), 10, total=128, loot=(("Coins",200,300,105),("Death rune",2,2,8),("Jug of wine",1,1,6),("Blood rune",1,1,5),("Fire orb",1,1,2),("Diamond",1,1,1),("Gold ore",1,1,1)), source_lines="534-565"),
}

# Owner-settled wiki-only exception.
PICKPOCKET_TARGETS["pickpocket_pompous_merchant"] = {
    **_pick("Pompous merchant", 1, 180, 240, 8.0, (10, 10), 8, guaranteed=(("Coins", 3),), source_lines="wiki exception"),
    "source": "https://runescape.wiki/w/Pompous_merchant?oldid=6437126",
    "source_status": "pinned-wiki/owner-approved",
}


def _stall(name, level, xp, ticks, *, guaranteed=(), total=0, loot=(), group="stalls", low=None, high=None, source_lines=""):
    row = {
        "display_name": name, "kind": "stall", "group": group, "level": level,
        "xp": xp, "respawn_ticks": ticks, "guaranteed": tuple(guaranteed),
        "loot_total": total, "loot": tuple(loot), "source": f"{STALL_SOURCE}:{source_lines}",
        "source_status": "provisional/2011Scape",
    }
    if low is not None:
        row.update({"kind": "wall_safe", "min_chance": low, "max_chance": high})
    return row


STALL_TARGETS = {
    "stall_vegetable": _stall("Vegetable stall",2,10.0,3,total=20,loot=(("Potato",1,1,6),("Cabbage",1,1,4),("Onion",1,1,4),("Tomato",1,1,4),("Garlic",1,1,2)),source_lines="22-38"),
    "stall_baker": _stall("Baker stall",5,16.0,3,total=20,loot=(("Cake",1,1,13),("Bread",1,1,5),("Chocolate slice",1,1,2)),source_lines="40-58"),
    "stall_crafting": _stall("Crafting stall",5,16.0,12,total=3,loot=(("Chisel",1,1,1),("Necklace mould",1,1,1),("Ring mould",1,1,1)),source_lines="60-79"),
    "stall_monkey_food": _stall("Monkey food stall",5,16.0,12,total=10,loot=(("Banana",1,1,7),("Monkey nuts",1,1,1),("Banana stew",1,1,1),("Monkey bar",1,1,1)),source_lines="81-96"),
    "stall_monkey_general": _stall("Monkey general stall",5,16.0,12,total=3,loot=(("Hammer",1,1,1),("Pot",1,1,1),("Tinderbox",1,1,1)),source_lines="98-112"),
    "stall_tea": _stall("Tea stall",5,16.0,12,guaranteed=(("Cup of tea",1),),source_lines="114-125"),
    "stall_silk": _stall("Silk stall",20,24.0,8,guaranteed=(("Silk",1),),source_lines="127-138"),
    "stall_wine": _stall("Wine stall",22,27.0,16,total=100,loot=(("Jug",1,1,39),("Jug of water",1,1,20),("Grapes",1,1,17),("Jug of wine",1,1,13),("Bottle of wine",1,1,11)),source_lines="140-157"),
    "stall_seed": _stall("Seed stall",27,10.0,15,total=252,loot=(("Potato seed",1,1,30),("Marigold seed",1,1,30),("Barley seed",1,1,30),("Hammerstone seed",1,1,30),("Onion seed",1,1,23),("Asgarnian seed",1,1,20),("Cabbage seed",1,1,18),("Yanillian seed",1,1,12),("Rosemary seed",1,1,10),("Nasturtium seed",1,1,9),("Tomato seed",1,1,9),("Jute seed",1,1,9),("Sweetcorn seed",1,1,7),("Krandorian seed",1,1,6),("Strawberry seed",1,1,4),("Wildblood seed",1,1,3),("Watermelon seed",1,1,2)),source_lines="159-188"),
    "stall_fur": _stall("Fur stall",35,36.0,16,guaranteed=(("Grey wolf fur",1),),source_lines="190-205"),
    "stall_fish": _stall("Fish stall",42,42.0,16,total=20,loot=(("Raw salmon",1,1,14),("Raw tuna",1,1,5),("Raw lobster",1,1,1)),source_lines="207-226"),
    "stall_crossbow": _stall("Crossbow stall",49,52.0,15,total=10,loot=(("Bronze bolts",1,1,7),("Bronze limbs",1,1,2),("Wooden stock",1,1,1)),source_lines="228-242"),
    "wall_safe": _stall("Rogues' Den wall safe",50,70.0,5,total=128,loot=(("Coins",10,10,25),("Coins",20,20,56),("Coins",40,40,21),("Uncut sapphire",1,1,12),("Uncut emerald",1,1,9),("Uncut ruby",1,1,4),("Uncut diamond",1,1,1)),group="safes",low=8,high=160,source_lines="244-264"),
    "stall_silver": _stall("Silver stall",50,54.0,50,guaranteed=(("Silver ore",1),),source_lines="266-281"),
    "stall_spice": _stall("Spice stall",65,81.0,133,guaranteed=(("Spice",1),),source_lines="283-294"),
    "stall_magic": _stall("Magic stall",65,100.0,133,total=3,loot=(("Air rune",1,1,1),("Earth rune",1,1,1),("Fire rune",1,1,1)),source_lines="296-310"),
    "stall_scimitar": _stall("Scimitar stall",65,160.0,133,total=3,loot=(("Iron scimitar",1,1,2),("Steel scimitar",1,1,1)),source_lines="312-325"),
    "stall_gem": _stall("Gem stall",75,160.0,300,total=128,loot=(("Uncut sapphire",1,1,105),("Uncut emerald",1,1,17),("Uncut ruby",1,1,5),("Uncut diamond",1,1,1)),source_lines="327-351"),
}

BLACKJACK_TARGETS = {
    "blackjack_menaphite_thug": {
        "display_name": "Menaphite thug", "kind": "blackjack", "group": "blackjacking",
        "level": 65, "xp": 137.5, "coins": 60, "knockout_xp": 10.0,
        "knockout_min_chance": 185, "knockout_max_chance": 255,
        "failure_damage": 40, "quest_gate": "the_feud", "quest_gate_label": "The Feud",
        "required_items_any": ("Willow blackjack", "Willow-blackjack", "Willow blackjack (o)"),
        "source": "https://runescape.wiki/w/Menaphite_Thug?oldid=6546629",
        "probability_source": "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/thieving/Knock-Out.kt:13-20",
        "source_status": "period-wiki values; provisional/Darkan hidden roll",
    },
}

SOURCE_BLOCKED_TARGETS = {
    "chest_dorgesh_kaan": {"display_name":"Dorgesh-Kaan chest","kind":"source_blocked","group":"safes","level":52,"xp":0,"quest_gate":"death_to_the_dorgeshuun","source_blocked":True,"source_blocked_reason":"success and loot values are not source-closed"},
    "pickpocket_lletya_elf": {"display_name":"Lletya elf","kind":"source_blocked","group":"pickpocketing","level":85,"xp":0,"quest_gate":"mournings_end_part_i","source_blocked":True,"source_blocked_reason":"2011Scape is silent; Darkan is only a lead"},
}

THIEVING_TARGETS = {**PICKPOCKET_TARGETS, **STALL_TARGETS, **BLACKJACK_TARGETS, **SOURCE_BLOCKED_TARGETS}

# Representative outputs for metadata/icon resolution.  Actual paths are owned
# by the global item registry; the Thieving table remains pure.
THIEVING_ITEM_IMAGES = {
    target_id: (spec.get("guaranteed") or ((spec.get("loot") or (("Coins",),))[0],))[0][0]
    for target_id, spec in THIEVING_TARGETS.items()
    if spec.get("guaranteed") or spec.get("loot")
}


def thieving_extra_items_as_dict():
    """Register source outputs that no other live skill currently owns."""
    stackable = {"Bittercap mushroom spore", "Swamp tar"}
    names = {
        item
        for spec in THIEVING_TARGETS.values()
        for item in (
            *(entry[0] for entry in spec.get("guaranteed", ())),
            *(entry[0] for entry in spec.get("loot", ())),
        )
    }
    return {
        name: {
            "category": "food" if name in {
                "Bat shish", "Coated frog's legs", "Fingers", "Frogburger",
                "Frogspawn gumbo", "Green gloop soup", "King worm",
            } else "material",
            "stackable": name in stackable,
            "source": PICKPOCKET_SOURCE,
        }
        for name in names
    }
