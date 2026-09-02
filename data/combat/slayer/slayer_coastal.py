from __future__ import annotations

from ..mechanics import (
    LIT_LIGHT_SOURCE_ITEMS,
)
from ..contract import (
    COMBAT_GEM_DROP_TABLE,
)

SEA_SNAKE_HATCHLING_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 13000,
            "slots": (
                {"item": "Casket", "quantity": 1, "slots": 11700},
                {"item": "Pearl bolt tips", "quantity": 3, "slots": 1},
                {"item": "Grimy guam", "quantity": 1, "slots": 1},
                {"item": "Fishing bait", "quantity": 50, "slots": 1},
                {"item": "Raw bass", "quantity": 2, "slots": 1},
                {"item": "Raw lobster", "quantity": 1, "slots": 1},
                {"item": "Seaweed", "quantity_range": (4, 5), "slots": 1},
                {"item": "Edible seaweed", "quantity": 1, "slots": 1},
                {"item": "Oyster pearl", "quantity_range": (1, 2), "slots": 1},
                {"item": "Water rune", "quantity": 15, "slots": 1},
                {"item": "Water orb", "quantity": 1, "slots": 1},
                {"item": "Adamant dart tip", "quantity": 2, "slots": 1},
                {"item": "Coins", "quantity_range": (2, 144), "slots": 1},
                {"item": "Mist rune", "quantity": 1, "slots": 1},
                {"item": "Limpwurt seed", "quantity": 1, "slots": 1},
                {"item": "Dwellberry seed", "quantity": 1, "slots": 1},
                {"item": "Jangerberry seed", "quantity": 1, "slots": 1},
                {"item": "Whiteberry seed", "quantity": 1, "slots": 1},
                {"item": "Harralander seed", "quantity": 1, "slots": 1},
                {"item": "Ranarr seed", "quantity": 1, "slots": 1},
                {"item": "Toadflax seed", "quantity": 1, "slots": 1},
                {"item": "Kwuarm seed", "quantity": 1, "slots": 1},
                {"item": "Snapdragon seed", "quantity": 1, "slots": 1},
                {"item": "Cadantine seed", "quantity": 1, "slots": 1},
                {"item": "Wildblood seed", "quantity": 1, "slots": 1},
                {"item": "Strawberry seed", "quantity": 1, "slots": 1},
                {"item": "Spirit weed seed", "quantity": 1, "slots": 1},
                {"slots": 1274},
            ),
        },
        {
            "name": "Medium clue",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (medium)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


SEA_SNAKE_YOUNG_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Darkan main",
            "total": 128,
            "slots": (
                {"item": "Coins", "quantity": 44, "slots": 60},
                {"item": "Coins", "quantity": 32, "slots": 11},
                {"item": "Adamant dart tip", "quantity": 2, "slots": 10},
                {"item": "Coins", "quantity": 24, "slots": 9},
                {"item": "Coins", "quantity": 23, "slots": 7},
                {"item": "Fishing bait", "quantity": 50, "slots": 4},
                {"item": "Pearl bolt tips", "quantity": 3, "slots": 4},
                {"item": "Raw bass", "quantity": 2, "slots": 4},
                {"item": "Water orb", "quantity": 1, "slots": 3},
                {"item": "Water rune", "quantity": 15, "slots": 2},
                {"item": "Mist rune", "quantity": 1, "slots": 2},
                {"item": "Broad arrows", "quantity": 4, "slots": 2},
                {"item": "Raw lobster", "quantity": 1, "slots": 2},
                {"item": "Seaweed", "quantity": 5, "slots": 2},
                {"item": "Edible seaweed", "quantity": 5, "slots": 2},
                {"item": "Oyster pearl", "quantity": 2, "slots": 1},
                {"item": "Oyster pearls", "quantity": 1, "slots": 1},
                {"item": "Casket", "quantity": 1, "slots": 1},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 1},
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
            "name": "Medium clue",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (medium)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


BRINE_RAT_DROPS = {
    "guaranteed": (("Bones", 1), ("Raw rat meat", 1)),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 512,
            "slots": (
                {"item": "Coins", "quantity": 1, "slots": 84},
                {"item": "Death rune", "quantity": 7, "slots": 72},
                {"item": "Coins", "quantity": 2, "slots": 64},
                {"item": "Coins", "quantity": 4, "slots": 36},
                {"item": "Earth rune", "quantity": 10, "slots": 24},
                {"item": "Raw lobster", "quantity": 10, "slots": 24},
                {"item": "Raw shark", "quantity": 3, "slots": 24},
                {"item": "Earth rune", "quantity": 36, "slots": 16},
                {"item": "Water rune", "quantity": 10, "slots": 12},
                {"item": "Coins", "quantity": 29, "slots": 12},
                {"item": "Water talisman", "quantity": 1, "slots": 12},
                {"item": "Air rune", "quantity": 18, "slots": 8},
                {"item": "Earth rune", "quantity": 18, "slots": 8},
                {"item": "Water rune", "quantity": 18, "slots": 8},
                {"item": "Blood rune", "quantity": 4, "slots": 8},
                {"item": "Raw rat meat", "quantity": 18, "slots": 8},
                {"item": "Raw pike", "quantity": 18, "slots": 8},
                {"item": "Raw shark", "quantity": 8, "slots": 8},
                {"item": "Raw swordfish", "quantity": 9, "slots": 8},
                {"item": "Raw shark", "quantity": 1, "slots": 4},
                {
                    "item": "Brine sabre",
                    "quantity": 1,
                    "slots": 1,
                    "source_item_id": 11037,
                },
                {"slots": 63},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 606,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 133},
                {"item": "Green charm", "quantity": 1, "slots": 7},
                {"item": "Crimson charm", "quantity": 1, "slots": 4},
                {"slots": 462},
            ),
        },
        {
            "name": "Medium clue",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (medium)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


MOLANISK_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 100000,
            "slots": (
                {"item": "Grimy guam", "quantity": 1, "slots": 16791},
                {"item": "Grimy marrentill", "quantity": 1, "slots": 16791},
                {"item": "Water rune", "quantity": 1, "slots": 16791},
                {"item": "Earth rune", "quantity": 1, "slots": 16791},
                {
                    "item": "Swamp weed",
                    "quantity": 1,
                    "slots": 16791,
                    "source_item_id": 10978,
                },
                {"item": "Grimy tarromin", "quantity": 1, "slots": 1749},
                {"item": "Grimy harralander", "quantity": 1, "slots": 1749},
                {"item": "Grimy ranarr", "quantity": 1, "slots": 1749},
                {"item": "Grimy dwarf weed", "quantity": 1, "slots": 1749},
                {"item": "Coins", "quantity": 1, "slots": 1749},
                {"item": "Mud rune", "quantity": 1, "slots": 1749},
                {"item": "Grimy wergali", "quantity": 1, "slots": 1749},
                {"item": "Wergali seed", "quantity": 1, "slots": 1749},
                {"item": "Grimy irit", "quantity": 1, "slots": 207},
                {"item": "Grimy avantoe", "quantity": 1, "slots": 207},
                {"item": "Grimy kwuarm", "quantity": 1, "slots": 207},
                {"item": "Grimy cadantine", "quantity": 1, "slots": 207},
                {"item": "Nature rune", "quantity": 1, "slots": 207},
                {"item": "Cosmic rune", "quantity": 1, "slots": 207},
                {"item": "Grimy lantadyme", "quantity": 1, "slots": 207},
                {
                    "item": "Mole claw",
                    "quantity": 1,
                    "slots": 207,
                    "source_item_id": 7416,
                },
                {"item": "Death rune", "quantity": 50, "slots": 186},
                {"slots": 211},
            ),
        },
        {
            "name": "Easy clue",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


JUNGLE_HORROR_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Darkan main",
            "total": 100000,
            "slots": tuple(
                {
                    "item": item_name,
                    **(
                        {"quantity_range": quantity}
                        if isinstance(quantity, tuple)
                        else {"quantity": quantity}
                    ),
                    "slots": chance * (100000 // denominator),
                }
                for item_name, quantity, chance, denominator in (
                    ("Bones", 1, 1679, 20000),
                    ("Nature rune", (1, 2), 1679, 20000),
                    ("Iron javelin", 5, 1679, 20000),
                    ("Iron kiteshield", 1, 1679, 20000),
                    ("Iron warhammer", 1, 1679, 20000),
                    ("Pineapple", 1, 1679, 20000),
                    ("Potato seed", 1, 1679, 20000),
                    ("Onion seed", 1, 1679, 20000),
                    ("Mahogany logs", 1, 1679, 20000),
                    ("Teak logs", (1, 3), 1679, 20000),
                    ("Grimy guam", 1, 999, 50000),
                    ("Grimy marrentill", 1, 999, 50000),
                    ("Grimy tarromin", 1, 999, 50000),
                    ("Grimy harralander", 1, 999, 50000),
                    ("Big bones", 1, 999, 50000),
                    ("Death rune", 1, 999, 50000),
                    ("Iron spear", 1, 999, 50000),
                    ("Iron ore", 1, 93, 50000),
                    ("Grimy ranarr", 1, 31, 25000),
                    ("Grimy irit", 1, 31, 25000),
                    ("Grimy avantoe", 1, 31, 25000),
                    ("Grimy kwuarm", 1, 31, 25000),
                    ("Grimy cadantine", 1, 31, 25000),
                    ("Grimy dwarf weed", 1, 31, 25000),
                    ("Grimy lantadyme", 1, 31, 25000),
                    ("Sweetcorn seed", 1, 31, 25000),
                    ("Watermelon seed", 1, 31, 25000),
                    ("Tomato seed", 1, 31, 25000),
                    ("Strawberry seed", 1, 31, 25000),
                    ("Cabbage seed", 1, 31, 25000),
                    ("Oak plank", 4, 31, 25000),
                    ("Evil turnip seed", 1, 31, 25000),
                )
            )
            + ({"slots": 142},),
        },
    ),
}


ENEMIES = {
    "harpie_bug_swarm": {
        "display_name": "Harpie Bug Swarm",
        "level": 46,
        "group": "Slayer",
        "required_slayer_level": 33,
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 60,
        "slayer_xp": 25.0,
        "stats": {
            "hitpoints": 250,
            "attack": 54,
            "strength": 46,
            "defence": 32,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 10,
            "defence_slash": 5,
            "defence_crush": 10,
            "defence_magic": 5,
            "defence_ranged": 10,
            "melee_strength": 0,
        },
        "start_equipment": {
            "slot": "shield",
            "items": ("Lit bug lantern",),
            "persistent": True,
            "warning": "Equip a Lit bug lantern to damage Harpie bug swarms",
            "source_status": (
                "period-exact continuous damage gate; every player hit is "
                "zeroed unless item 7053 occupies the shield slot"
            ),
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Darkan main",
                    "total": 100000,
                    "slots": (
                        {"item": "Gold ore", "quantity": 1, "slots": 10514},
                        {
                            "item": "Fire rune",
                            "quantity_range": (20, 90),
                            "slots": 10514,
                        },
                        {
                            "item": "Chaos rune",
                            "quantity_range": (5, 15),
                            "slots": 10514,
                        },
                        {
                            "item": "Coins",
                            "quantity_range": (30, 1000),
                            "slots": 10514,
                        },
                        {
                            "item": "Mithril chainbody",
                            "quantity": 1,
                            "slots": 10514,
                        },
                        {
                            "item": "Steel full helm",
                            "quantity": 1,
                            "slots": 10514,
                        },
                        {
                            "item": "Steel hatchet",
                            "quantity": 1,
                            "slots": 10514,
                        },
                        {
                            "item": "Staff of fire",
                            "quantity": 1,
                            "slots": 10514,
                        },
                        {"item": "Coal", "quantity": 1, "slots": 2336},
                        {"item": "Bones", "quantity": 1, "slots": 2336},
                        {
                            "item": "Death rune",
                            "quantity_range": (3, 50),
                            "slots": 2336,
                        },
                        {
                            "item": "Black 2h sword",
                            "quantity": 1,
                            "slots": 2336,
                        },
                        {"item": "Jug of wine", "quantity": 1, "slots": 2336},
                        {"item": "Steel boots", "quantity": 1, "slots": 2336},
                        {"item": "Bones", "quantity": 1, "slots": 467},
                        {"item": "Blood rune", "quantity": 50, "slots": 467},
                        {"item": "Rune javelin", "quantity": 5, "slots": 467},
                        {"slots": 471},
                    ),
                },
                {
                    "name": "Darkan charms",
                    "total": 202,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 3},
                        {"item": "Green charm", "quantity": 1, "slots": 11},
                        {"slots": 188},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Harpie_Bug_Swarm?oldid=6530649; "
            "https://runescape.wiki/w/Lit_bug_lantern?oldid=6591557; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/content/skills/"
            "slayer/npcs/HarpieBug.java; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "harpie_bug_swarm (noanims).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/harpie_bug_swarm.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer and Firemaking gates, "
            "Slayer XP, six-tick melee, maximum hit, and continuous lit-lantern "
            "damage gate; Darkan exact stats, bonuses, respawn, one exact "
            "100,000-slot ordinary selector, and emulator-exact 202-slot charm "
            "selector; period wiki and Darkan drop contents conflict"
        ),
    },
    "sea_snake_hatchling": {
        "display_name": "Sea Snake Hatchling",
        "level": 62,
        "group": "Slayer",
        "required_slayer_level": 1,
        "quest_gate": "royal_trouble",
        "quest_gate_label": "Complete Royal Trouble",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 69,
        "poison_damage": 5,
        "slayer_xp": 50.0,
        "stats": {
            "hitpoints": 500,
            "attack": 84,
            "strength": 84,
            "defence": 84,
            "magic": 84,
            "ranged": 84,
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
        "drops": SEA_SNAKE_HATCHLING_DROPS,
        "source": (
            "https://runescape.wiki/w/Sea_Snake_Hatchling?oldid=6448392; "
            "https://runescape.wiki/w/Sea_Snake_Hatchling; "
            "https://oldschool.runescape.wiki/w/Sea_Snake_Hatchling; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "sea_snake_hatchling (nostats).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/model/entity/npc/"
            "combat/NPCCombatDefinitions.java; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/sea_snake_hatchling.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/utils/drop/DropList.java; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/utils/NPCClueDrops.java"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer XP, melee style, "
            "69-LP maximum hit, Vannaka membership, 50-LP initial poison, "
            "and Royal Trouble route; corroborated six-tick attack cadence; "
            "Darkan generated combat stats, exact respawn, one exact "
            "13000-slot ordinary selector, and "
            "independent 1/128 medium clue"
        ),
    },
    "sea_snake_young": {
        "display_name": "Sea Snake Young",
        "level": 90,
        "group": "Slayer",
        "required_slayer_level": 40,
        "quest_gate": "royal_trouble",
        "quest_gate_label": "Complete Royal Trouble",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 84,
        "poison_damage": 7,
        "slayer_xp": 85.0,
        "stats": {
            "hitpoints": 850,
            "attack": 90,
            "strength": 70,
            "defence": 70,
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
        "drops": SEA_SNAKE_YOUNG_DROPS,
        "source": (
            "https://runescape.wiki/w/Sea_Snake_Young?oldid=5936978; "
            "https://runescape.wiki/w/Sea_Snake_Young; "
            "https://oldschool.runescape.wiki/w/Sea_Snake_Young; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "sea_snake_young.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/sea_snake_young.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/utils/NPCClueDrops.java"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer gate/XP, melee style, "
            "84-LP maximum hit, Vannaka membership, post-quest 68-LP initial "
            "poison, and Royal Trouble route; corroborated six-tick attack "
            "cadence; nearest representable 70-LP poison abstraction; Darkan "
            "exact stats, respawn, one "
            "128-slot main selector, long/curved-bone tertiary selector, and "
            "independent 1/128 medium clue"
        ),
    },
    "brine_rat": {
        "display_name": "Brine rat",
        "level": 70,
        "group": "Slayer",
        "required_slayer_level": 47,
        "quest_gate": "olafs_quest",
        "quest_gate_label": "Complete Olaf's Quest",
        "partial_quest_access": {
            "quest_id": "olafs_quest",
            "minimum_stage": 40,
            "runtime_policy": "conservative_completion",
        },
        "required_items": {"Spade": 1},
        "required_items_label": (
            "Spade x1 for Brine Rat Cavern (the toolbelt does not count)"
        ),
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 93,
        "slayer_xp": 50.0,
        "stats": {
            "hitpoints": 500,
            "attack": 70,
            "strength": 79,
            "defence": 40,
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
        "drops": BRINE_RAT_DROPS,
        "interaction_note": (
            "Cavern access needs a real Spade. Partial Olaf's Quest access is "
            "represented conservatively by completion until the quest runtime "
            "exports its stage-40 permission."
        ),
        "source": (
            "https://runescape.wiki/w/Brine_rat?oldid=6555564; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/content/skills/"
            "slayer/SlayerTaskManager.java:135-139; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "brine_rat.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/brine_rat.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt:27; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/utils/NPCClueDrops.java"
        ),
        "source_status": (
            "period exact identity, LP, Slayer gate/XP, melee style, six-tick "
            "cadence, maximum hit, passive behavior, cavern Spade requirement, "
            "partial-quest access, and completion-only Brine sabre rule; Darkan "
            "exact stats, zero bonuses, respawn, one exact 512-slot ordinary "
            "selector, emulator-exact 606-slot charm selector, and independent "
            "1/128 medium clue; partial quest access is conservatively gated on "
            "completion until Darkan quest stages expose stage 40"
        ),
    },
    "molanisk": {
        "display_name": "Molanisk",
        "level": 51,
        "group": "Slayer",
        "required_slayer_level": 39,
        "quest_gate": "death_to_the_dorgeshuun",
        "quest_gate_label": "Complete Death to the Dorgeshuun",
        "required_items": {"Slayer bell": 1},
        "required_items_label": "Slayer bell x1 to lure a Molanisk (not consumed)",
        "required_item_options": (LIT_LIGHT_SOURCE_ITEMS,),
        "required_item_options_label": (
            "One lit light source in inventory or equipped for the "
            "Dorgesh-Kaan South Dungeon"
        ),
        "lure": {"item": "Slayer bell", "consumed": False},
        "light_source": {"accepted_items": LIT_LIGHT_SOURCE_ITEMS},
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 53,
        "slayer_xp": 52.0,
        "stats": {
            "hitpoints": 520,
            "attack": 40,
            "strength": 40,
            "defence": 50,
            "magic": 0,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 45,
            "defence_slash": 45,
            "defence_crush": 35,
            "defence_magic": 30,
            "defence_ranged": 55,
            "melee_strength": 0,
        },
        "drops": MOLANISK_DROPS,
        "interaction_note": (
            "Each encounter starts by ringing the non-consumed Slayer bell to "
            "lure the wall-bound Molanisk; a lit light source remains required."
        ),
        "source": (
            "https://runescape.wiki/w/Molanisk?oldid=6565831; "
            "https://runescape.wiki/w/Slayer_bell?oldid=6121349; "
            "https://runescape.wiki/w/Dorgesh-Kaan_South_Dungeon?oldid=6393410; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/molanisk.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/developer-information/npcListBonuses.txt:5753; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/molanisk.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/utils/NPCClueDrops.java:54"
        ),
        "source_status": (
            "period exact identity, LP, Slayer gate/XP, melee style, six-tick "
            "cadence, maximum hit, passive behavior, bell lure, light-source "
            "requirement, and quest access; Darkan exact stats, bonuses, respawn, "
            "one exact 100,000-slot ordinary selector, and independent 1/128 easy "
            "clue; no Darkan charm row, so no charm selector is manufactured"
        ),
    },
    "jungle_horror": {
        "display_name": "Jungle horror",
        "level": 70,
        "group": "Slayer",
        "required_slayer_level": 1,
        "quest_gate": "cabin_fever",
        "quest_gate_label": "Complete Cabin Fever",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 84,
        "slayer_xp": 45.0,
        "stats": {
            "hitpoints": 450,
            "attack": 70,
            "strength": 70,
            "defence": 55,
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
        "drops": JUNGLE_HORROR_DROPS,
        "source": (
            "https://runescape.wiki/w/Jungle_horror?oldid=6534099; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "jungle_horror.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/jungle_horror.json"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer XP, six-tick melee, "
            "84-LP maximum hit, Vannaka membership, guaranteed Bones, and "
            "Mos Le'Harmless route; Darkan exact stats, respawn, and one "
            "100,000-slot ordinary selector"
        ),
    },
}
