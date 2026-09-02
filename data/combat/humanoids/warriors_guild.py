from __future__ import annotations

CYCLOPS_WARRIORS_GUILD_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Tertiary",
            "total": 100000,
            "slots": (
                {"item": "Long bone", "quantity": 1, "slots": 250},
                {"item": "Curved bone", "quantity": 1, "slots": 20},
                {"slots": 99730},
            ),
        },
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
                    "slots": chance * (100000 // total),
                }
                for item_name, quantity, chance, total in (
                    ("Limpwurt root", 1, 5597, 100000),
                    ("Black knife", (1, 4), 5597, 100000),
                    ("Coins", (1, 5), 5597, 100000),
                    ("Iron chainbody", 1, 5597, 100000),
                    ("Steel chainbody", 1, 5597, 100000),
                    ("Steel dagger", 1, 5597, 100000),
                    ("Black dagger", 1, 5597, 100000),
                    ("Steel sword", 1, 5597, 100000),
                    ("Black sword", 1, 5597, 100000),
                    ("Steel longsword", 1, 5597, 100000),
                    ("Black longsword", 1, 5597, 100000),
                    ("Iron 2h sword", 1, 5597, 100000),
                    ("Steel 2h sword", 1, 5597, 100000),
                    ("Steel battleaxe", 1, 5597, 100000),
                    ("Steel mace", 1, 5597, 100000),
                    ("Bones", 1, 777, 50000),
                    ("Iron full helm", 1, 777, 50000),
                    ("Iron kiteshield", 1, 777, 50000),
                    ("Mithril dagger", 1, 777, 50000),
                    ("Mithril longsword", 1, 777, 50000),
                    ("Black 2h sword", 1, 777, 50000),
                    ("Adamant mace", 1, 777, 50000),
                    ("Fire talisman", 1, 777, 50000),
                    ("Body talisman", 1, 777, 50000),
                    ("Grimy guam", 1, 37, 50000),
                    ("Grimy marrentill", 1, 37, 50000),
                    ("Grimy tarromin", 1, 37, 50000),
                    ("Grimy harralander", 1, 37, 50000),
                    ("Grimy ranarr", 1, 37, 50000),
                    ("Grimy irit", 1, 37, 50000),
                    ("Grimy avantoe", 1, 37, 50000),
                    ("Grimy kwuarm", 1, 37, 50000),
                    ("Grimy cadantine", 1, 37, 50000),
                    ("Grimy dwarf weed", 1, 37, 50000),
                    ("Fire rune", 15, 37, 50000),
                    ("Water rune", 7, 37, 50000),
                    ("Mind rune", (2, 3), 37, 50000),
                    ("Death rune", 2, 37, 50000),
                    ("Nature rune", (2, 3), 37, 50000),
                    ("Law rune", (2, 3), 37, 50000),
                    ("Cosmic rune", (2, 3), 37, 50000),
                    ("Steel arrows", 5, 37, 50000),
                    ("Mithril sq shield", 1, 37, 50000),
                    ("Adamant 2h sword", 1, 37, 50000),
                    ("Grimy lantadyme", 1, 37, 50000),
                    ("Cactus seed", 1, 37, 50000),
                    ("Cadantine seed", 1, 37, 50000),
                    ("Dwarf weed seed", 1, 37, 50000),
                    ("Spirit weed seed", 1, 37, 50000),
                    ("Bones", 1, 7, 100000),
                    ("Rune dagger", 1, 7, 100000),
                    ("Beer", 1, 7, 100000),
                    ("Limpwurt seed", 1, 7, 100000),
                    ("Jangerberry seed", 1, 7, 100000),
                    ("Whiteberry seed", 1, 7, 100000),
                    ("Belladonna seed", 1, 7, 100000),
                    ("Bittercap mushroom spore", 1, 7, 100000),
                    ("Marrentill seed", 1, 7, 100000),
                    ("Tarromin seed", 1, 7, 100000),
                    ("Harralander seed", 1, 7, 100000),
                    ("Ranarr seed", 1, 7, 100000),
                    ("Toadflax seed", 1, 7, 100000),
                    ("Irit seed", 1, 7, 100000),
                    ("Avantoe seed", 1, 7, 100000),
                    ("Snapdragon seed", 1, 7, 100000),
                    ("Lantadyme seed", 1, 7, 100000),
                    ("Yanillian seed", 2, 7, 100000),
                    ("Wildblood seed", 1, 7, 100000),
                    ("Potato seed", 1, 7, 100000),
                    ("Sweetcorn seed", 3, 7, 100000),
                    ("Watermelon seed", 1, 7, 100000),
                    ("Strawberry seed", 1, 7, 100000),
                    ("Cabbage seed", 4, 7, 100000),
                )
            )
            + ({"slots": 41},),
        },
    ),
}


CYCLOSSUS_WARRIORS_GUILD_DROPS = {
    "guaranteed": (("Big bones", 1),),
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
                    "slots": slots,
                }
                for item_name, quantity, slots in (
                    ("Limpwurt root", 5, 11993),
                    ("Big bones", 2, 11993),
                    ("Coins", (1, 1901), 11993),
                    ("Adamant chainbody", 1, 11993),
                    ("Steel warhammer", 1, 11993),
                    ("Mithril warhammer", 1, 11993),
                    ("Cyclopean helmet", 1, 11993),
                    ("Shark", 1, 777),
                    ("Adamantite ore", 1, 777),
                    ("Law rune", 45, 777),
                    ("Blood rune", (5, 18), 777),
                    ("Adamant plateskirt", 1, 777),
                    ("Mithril sq shield", 1, 777),
                    ("Adamant scimitar", 1, 777),
                )
            )
            + ({"slots": 10610},),
        },
        {
            # The period page calls this common; Darkan omits its unique-drop
            # handler, so the common-row weight remains a labeled abstraction.
            "name": "Period-common abstraction: Dragon defender",
            "total": 100000,
            "slots": (
                {"item": "Dragon defender", "quantity": 1, "slots": 11993},
                {"slots": 88007},
            ),
        },
    ),
}


ENEMIES = {
    "cyclops": {
        "display_name": "Cyclops",
        "level": 56,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 64,
        "slayer_xp": 75.0,
        "allowed_combat_classes": ("melee",),
        "warriors_guild_gate": True,
        "stats": {
            "hitpoints": 750,
            "attack": 47,
            "strength": 50,
            "defence": 26,
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
        "drops": CYCLOPS_WARRIORS_GUILD_DROPS,
        "source": (
            "https://runescape.wiki/w/Cyclops?oldid=6565802; "
            "https://runescape.wiki/w/Warriors%27_Guild?oldid=6565080; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/cyclops/"
            "cyclops_(56).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/cyclops_warrior_guild.json"
        ),
        "source_status": (
            "period level, LP, maximum hit, melee-only Guild immunity, "
            "Slayer XP and guaranteed Big bones; Darkan exact combat stats, "
            "respawn and one ordinary selector; defender drops are "
            "resolved by the Warriors' Guild progression state"
        ),
    },
    "cyclossus": {
        "display_name": "Cyclossus",
        "level": 156,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 59,
        "max_hit": 94,
        "slayer_xp": 350.0,
        "allowed_combat_classes": ("melee",),
        "warriors_guild_gate": True,
        "warriors_guild_target": "cyclossus",
        "warriors_guild_spawn_only": True,
        "stats": {
            "hitpoints": 3280,
            "attack": 64,
            "strength": 64,
            "defence": 64,
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
        "drops": CYCLOSSUS_WARRIORS_GUILD_DROPS,
        "source": (
            "https://runescape.wiki/w/Cyclossus?oldid=6510357; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "cyclossus (nostats) (noanims).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/cyclossus.json"
        ),
        "source_status": (
            "period exact level, LP, maximum hit, speed, Slayer XP, defender "
            "requirement, guaranteed Big bones and common unique rewards; "
            "Darkan exact respawn and one ordinary selector; its absent "
            "combat stats are filled from the cache record; the spatial shove "
            "and stun are compressed into the ordinary review combat exchange"
        ),
    },
}
