from __future__ import annotations

DAGANNOTH_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Darkan ordinary",
            "total": 1100,
            "slots": (
                {"item": "Pearl bolt tips", "quantity": 12, "slots": 25},
                {"item": "Lobster pot", "quantity": 1, "slots": 25},
                {"item": "Harpoon", "quantity": 1, "slots": 25},
                {"item": "Fishing bait", "quantity": 50, "slots": 25},
                {"item": "Feather", "quantity": 15, "slots": 45},
                {"item": "Raw sardine", "quantity": 5, "slots": 45},
                {"item": "Raw herring", "quantity": 4, "slots": 45},
                {"item": "Raw lobster", "quantity": 1, "slots": 45},
                {"item": "Seaweed", "quantity": 10, "slots": 45},
                {
                    "item": "Oyster pearls",
                    "quantity_range": (1, 2),
                    "slots": 45,
                },
                {
                    "item": "Water rune",
                    "quantity_range": (15, 30),
                    "slots": 45,
                },
                {"item": "Steel arrows", "quantity": 15, "slots": 45},
                {"item": "Coins", "quantity_range": (1, 85), "slots": 45},
                {"item": "Bronze spear", "quantity": 1, "slots": 45},
                {"item": "Iron spear", "quantity": 1, "slots": 45},
                {"item": "Bronze hatchet", "quantity": 1, "slots": 45},
                {"item": "Poison ivy seed", "quantity": 1, "slots": 45},
                {"item": "Cactus seed", "quantity": 1, "slots": 45},
                {"item": "Belladonna seed", "quantity": 1, "slots": 45},
                {"item": "Toadflax seed", "quantity": 1, "slots": 45},
                {"item": "Irit seed", "quantity": 1, "slots": 45},
                {"item": "Avantoe seed", "quantity": 1, "slots": 45},
                {"item": "Opal bolt tips", "quantity": 12, "slots": 15},
                {"item": "Raw tuna", "quantity": 1, "slots": 15},
                {"item": "Casket", "quantity": 1, "slots": 15},
                {
                    "item": "Mithril javelin",
                    "quantity_range": (3, 4),
                    "slots": 15,
                },
                {"item": "Mithril spear", "quantity": 1, "slots": 15},
                {"item": "Ranarr seed", "quantity": 1, "slots": 15},
                {"item": "Kwuarm seed", "quantity": 1, "slots": 15},
                {"item": "Snapdragon seed", "quantity": 1, "slots": 15},
                {"item": "Cadantine seed", "quantity": 1, "slots": 15},
                {"item": "Lantadyme seed", "quantity": 1, "slots": 15},
                {"item": "Dwarf weed seed", "quantity": 1, "slots": 15},
                {"item": "Torstol seed", "quantity": 1, "slots": 11},
                {"slots": 14},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 1212,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 68},
                {"item": "Green charm", "quantity": 1, "slots": 26},
                {"item": "Crimson charm", "quantity": 1, "slots": 212},
                {"item": "Blue charm", "quantity": 1, "slots": 6},
                {"slots": 900},
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


ENEMIES = {
    "dagannoth": {
        "display_name": "Dagannoth (ranged)",
        "level": 74,
        "group": "Dagannoths",
        "attack_style": "ranged",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 80,
        "slayer_xp": 70.0,
        "stats": {
            "hitpoints": 700,
            "attack": 68,
            "strength": 70,
            "defence": 50,
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
        "drops": DAGANNOTH_DROPS,
        "source": (
            "https://runescape.wiki/w/Dagannoth_(Lighthouse)?oldid=6548464; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "dagannoth/dagannoth_(74).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/dagannoth.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/utils/NPCClueDrops.java"
        ),
        "source_status": (
            "period exact level, LP, Slayer XP, six-tick ranged identity, "
            "aggression, non-poisonous attacks, poison susceptibility, "
            "guaranteed Bones, ordinary family membership, and Chaeldar "
            "assignment; the approximate period 100-LP maximum is represented "
            "by Darkan's exact 80; Darkan exact combat levels, zero bonuses, "
            "59-tick respawn, one losslessly "
            "combined 1,100-slot ordinary selector, exact charm selector, and "
            "1/128 medium clue; the two ordinary Lighthouse forms represent "
            "the baseline family without importing a location gate, while "
            "Waterbirth, Chaos-Tunnel, boss, quest, and Daemonheim contexts "
            "remain excluded"
        ),
    },
    "dagannoth_level_92": {
        "display_name": "Dagannoth (melee)",
        "level": 92,
        "group": "Dagannoths",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 80,
        "slayer_xp": 120.0,
        "stats": {
            "hitpoints": 1200,
            "attack": 68,
            "strength": 70,
            "defence": 71,
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
            "defence_magic": 50,
            "defence_ranged": 50,
            "melee_strength": 0,
        },
        "drops": DAGANNOTH_DROPS,
        "source": (
            "https://runescape.wiki/w/Dagannoth_(Lighthouse)?oldid=6548464; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "dagannoth/dagannoth_(92).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/dagannoth.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/utils/NPCClueDrops.java"
        ),
        "source_status": (
            "period exact level, LP, Slayer XP, six-tick melee, 80-LP "
            "maximum, aggression, non-poisonous attacks, poison susceptibility, "
            "guaranteed Bones, ordinary family membership, and Chaeldar "
            "assignment; Darkan exact combat "
            "levels, magic/ranged defences, 59-tick respawn, one losslessly "
            "combined 1,100-slot ordinary selector, exact charm selector, and "
            "1/128 medium clue; the two ordinary Lighthouse forms represent "
            "the baseline family without importing a location gate, while "
            "Waterbirth, Chaos-Tunnel, boss, quest, and Daemonheim contexts "
            "remain excluded"
        ),
    },
}
