from __future__ import annotations

from ..mechanics import (
    COMBAT_SOURCE_ROOT,
)
from ..contract import (
    COMBAT_GEM_DROP_TABLE,
)

DESERT_LIZARD_DROPS = {
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
                    "slots": chance,
                }
                for item_name, quantity, chance in (
                    ("Grimy tarromin", 1, 7009),
                    ("Grimy harralander", 1, 7009),
                    ("Copper ore", 1, 7009),
                    ("Tin ore", 1, 7009),
                    ("Iron ore", 1, 7009),
                    ("Fire rune", (1, 5), 7009),
                    ("Nature rune", 5, 7009),
                    ("Waterskin (0)", 2, 7009),
                    ("Silver bar", 1, 7009),
                    ("Onion seed", 4, 7009),
                    ("Tomato seed", 3, 7009),
                    ("Cabbage seed", 3, 7009),
                    ("Grimy guam", 1, 1401),
                    ("Grimy marrentill", 1, 1401),
                    ("Grimy ranarr", 1, 1401),
                    ("Grimy irit", 1, 1401),
                    ("Grimy avantoe", 1, 1401),
                    ("Silver ore", 1, 1401),
                    ("Coal", 1, 1401),
                    ("Grimy kwuarm", 1, 1401),
                    ("Potato seed", 4, 1401),
                    ("Strawberry seed", 3, 1401),
                    ("Grimy cadantine", 1, 207),
                    ("Grimy lantadyme", 1, 207),
                    ("Grimy dwarf weed", 1, 207),
                    ("Mithril ore", 1, 207),
                    ("Knife", 1, 207),
                    ("Waterskin (4)", 2, 207),
                    ("Kebab", 1, 207),
                    ("Mystic gloves (light)", 1, 207),
                    ("Watermelon seed", 1, 207),
                )
            )
            + ({"slots": 19},),
        },
    ),
}


ROCKSLUG_DROPS = {
    "guaranteed": (),
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
                    ("Copper ore", 1, 647, 10000),
                    ("Tin ore", 1, 647, 10000),
                    ("Iron ore", 1, 647, 10000),
                    ("Coal", 1, 647, 10000),
                    ("Earth rune", (5, 42), 647, 10000),
                    ("Rune essence", 1, 647, 10000),
                    ("Dwarven stout", 1, 647, 10000),
                    ("Hammer", 1, 647, 10000),
                    ("Bronze bar", 1, 647, 10000),
                    ("Iron bar", 1, 647, 10000),
                    ("Potato seed", 4, 647, 10000),
                    ("Onion seed", 4, 647, 10000),
                    ("Cabbage seed", 4, 647, 10000),
                    ("Mithril ore", 1, 2803, 100000),
                    ("Chaos rune", (2, 5), 2803, 100000),
                    ("Coins", (279, 418), 2803, 100000),
                    ("Tomato seed", 3, 2803, 100000),
                    ("Sweetcorn seed", 3, 2803, 100000),
                    ("Mystic gloves", 1, 467, 50000),
                    ("Strawberry seed", 2, 467, 50000),
                )
            )
            + ({"slots": 7},),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 90},
                {"item": "Green charm", "quantity": 1, "slots": 20},
                {"item": "Crimson charm", "quantity": 1, "slots": 10},
                {"item": "Blue charm", "quantity": 1, "slots": 5},
                {"slots": 875},
            ),
        },
    ),
}


GARGOYLE_DROPS = {
    "guaranteed": (),
    "tables": (
        {
            "name": "Darkan main",
            "total": 512,
            "slots": tuple(
                {
                    "item": item_name,
                    "quantity": quantity,
                    "slots": chance * (512 // denominator),
                }
                for item_name, quantity, chance, denominator in (
                    ("Coins", 11, 27, 128),
                    ("Coins", 22, 20, 128),
                    ("Fire rune", 37, 10, 128),
                    ("Steel hatchet", 1, 10, 128),
                    ("Chaos rune", 15, 8, 128),
                    ("Fire rune", 75, 6, 128),
                    ("Pure essence", 35, 6, 128),
                    ("Steel bar", 3, 6, 128),
                    ("Death rune", 5, 5, 128),
                    ("Coins", 460, 5, 128),
                    ("Adamant platelegs", 1, 4, 128),
                    ("Steel battleaxe", 1, 3, 128),
                    ("Gold bar", 1, 3, 128),
                    ("Steel 2h sword", 1, 2, 128),
                    ("Mithril bar", 3, 2, 128),
                    ("Runite ore", 1, 2, 128),
                    ("Adamant boots", 1, 1, 128),
                    ("Thread", 10, 1, 128),
                    ("Rune full helm", 1, 1, 128),
                    ("Granite maul", 1, 1, 256),
                    ("Mystic robe top", 1, 1, 512),
                )
            )
            + (
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 20},
                {"slots": 1},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 100},
                {"item": "Green charm", "quantity": 1, "slots": 50},
                {"item": "Crimson charm", "quantity": 1, "slots": 50},
                {"item": "Blue charm", "quantity": 1, "slots": 70},
                {"slots": 730},
            ),
        },
    ),
}


MUTATED_ZYGOMITE_DROPS = {
    "guaranteed": (("Ashes", 1),),
    "tables": (
        {
            "name": "Period-common abstraction: Fungicide",
            "total": 8,
            "slots": (
                {"item": "Fungicide", "quantity": 1, "slots": 1},
                {"slots": 7},
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
                    "slots": chance * (100000 // denominator),
                }
                for item_name, quantity, chance, denominator in (
                    ("Strawberry seed", (1, 6), 16791, 20000),
                    ("Grimy guam", 1, 233, 50000),
                    ("Grimy marrentill", 1, 233, 50000),
                    ("Grimy tarromin", 1, 233, 50000),
                    ("Grimy harralander", 1, 233, 50000),
                    ("Grimy ranarr", 1, 233, 50000),
                    ("Grimy irit", 1, 233, 50000),
                    ("Grimy avantoe", 1, 233, 50000),
                    ("Grimy kwuarm", 1, 233, 50000),
                    ("Grimy cadantine", 1, 233, 50000),
                    ("Grimy dwarf weed", 1, 233, 50000),
                    ("Grimy lantadyme", 1, 233, 50000),
                    ("Clay", 1, 233, 50000),
                    ("Earth rune", 15, 233, 50000),
                    ("Nature rune", 2, 233, 50000),
                    ("Law rune", (10, 50), 233, 50000),
                    ("Steel 2h sword", 1, 233, 50000),
                    ("Steel hatchet", 1, 233, 50000),
                    ("Mort myre fungus", (1, 3), 233, 50000),
                    ("Limpwurt seed", 1, 233, 50000),
                    ("Jangerberry seed", 1, 233, 50000),
                    ("Whiteberry seed", 1, 233, 50000),
                    ("Poison ivy seed", 1, 233, 50000),
                    ("Bittercap mushroom spore", 1, 233, 50000),
                    ("Toadflax seed", 1, 233, 50000),
                    ("Kwuarm seed", 1, 233, 50000),
                    ("Barley seed", 1, 233, 50000),
                    ("Asgarnian seed", 3, 233, 50000),
                    ("Wildblood seed", 1, 233, 50000),
                    ("Potato seed", 4, 233, 50000),
                    ("Supercompost", (1, 3), 233, 50000),
                    ("Blood rune", 50, 93, 50000),
                    ("Mithril full helm", 1, 93, 50000),
                    ("Rune full helm", 1, 93, 50000),
                    ("Ranarr seed", 1, 93, 50000),
                    ("Snapdragon seed", 1, 93, 50000),
                    ("Torstol seed", 1, 93, 50000),
                    ("Jute seed", 1, 93, 50000),
                    ("Yanillian seed", 1, 93, 50000),
                    ("Watermelon seed", (1, 3), 93, 50000),
                    ("Spirit weed seed", 1, 93, 50000),
                    ("Marigold seed", 1, 37, 100000),
                    ("Woad seed", 1, 37, 100000),
                    ("Onion seed", 4, 37, 100000),
                    ("Tomato seed", 3, 37, 100000),
                    ("Morchella mushroom spore", (1, 3), 37, 100000),
                )
            )
            + ({"slots": 20},),
        },
    ),
}


MUTATED_ZYGOMITE_FINISHER = {
    "item": "Fungicide spray 10",
    "display_item": "Fungicide spray",
    "charge_items": tuple(
        (f"Fungicide spray {charges}", charges)
        for charges in range(10, 0, -1)
    ),
    "empty_item": "Fungicide spray 0",
    "reload_item": "Fungicide",
    "reload_charges": 10,
    "threshold_lifepoints": 19,
    "consume": True,
    "action_label": "Spray with fungicide",
    "quick_unlock_key": "slayer_quick_finishers_unlocked",
    "source_status": (
        "period-exact below-20-LP charged spray; each use spends one charge, "
        "and one Fungicide canister fully reloads the ten-charge spray"
    ),
}


ENEMIES = {
    "desert_lizard": {
        "display_name": "Desert lizard",
        "level": 24,
        "group": "Slayer",
        "required_slayer_level": 22,
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 40,
        "slayer_xp": 25.0,
        "finisher": {
            "item": "Ice cooler",
            "threshold_lifepoints": 30,
            "consume": True,
            "action_label": "Use Ice cooler",
            "quick_unlock_key": "slayer_quick_finishers_unlocked",
            "source_status": (
                "period-exact threshold/item/consumption; Darkan ConditionalDeath "
                "confirms the same item-gated death family"
            ),
        },
        "environmental_hazard": {
            "display_name": "Desert heat",
            "dose_items": (
                "Waterskin (4)",
                "Waterskin (3)",
                "Waterskin (2)",
                "Waterskin (1)",
            ),
            "empty_item": "Waterskin (0)",
            "reviews_per_dose": 1,
            "loadout_cap": 8,
            "source_status": (
                "period-exact water requirement and dose preservation; one dose "
                "per damaging Combat review is a bounded review-native abstraction"
            ),
        },
        "stats": {
            "hitpoints": 250,
            "attack": 20,
            "strength": 22,
            "defence": 20,
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
        "drops": DESERT_LIZARD_DROPS,
        "source": (
            "https://runescape.wiki/w/Desert_lizard?oldid=6548273; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/desert_lizard.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/drops/desert_lizard.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "src/main/java/com/rs/game/content/skills/slayer/npcs/ConditionalDeath.java"
        ),
    },
    "rockslug": {
        "display_name": "Rock slug",
        "level": 29,
        "group": "Slayer",
        "required_slayer_level": 20,
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 59,
        "max_hit": 41,
        "slayer_xp": 27.0,
        "retaliation_stop_lifepoints": 10,
        "finisher": {
            "item": "Bag of salt",
            "threshold_lifepoints": 39,
            "consume": True,
            "action_label": "Use Bag of salt",
            "quick_unlock_key": "slayer_quick_finishers_unlocked",
            "source_status": (
                "period-exact 1–39 LP item/consumption threshold and 10-LP "
                "retaliation stop; Darkan/game-main reconcile combat and drops"
            ),
        },
        "stats": {
            "hitpoints": 270,
            "attack": 22,
            "strength": 27,
            "defence": 27,
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
        "drops": ROCKSLUG_DROPS,
        "source": (
            "https://runescape.wiki/w/Rock_slug?oldid=6530509; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/rockslug_lvl_29.plugin.kts; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/rockslug.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/drops/rockslug.json"
        ),
    },
    "gargoyle": {
        "display_name": "Gargoyle",
        "level": 111,
        "group": "Slayer",
        "required_slayer_level": 75,
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 119,
        "slayer_xp": 105.0,
        "regeneration": {
            "lifepoints_per_tick_numerator": 12,
            "lifepoints_per_tick_denominator": 5,
            "source_status": (
                "period page reports roughly 20 LP per five seconds; expressed "
                "as the exact equivalent 12/5 LP per 0.6-second gameplay tick"
            ),
        },
        "finisher": {
            "item": "Rock hammer",
            "threshold_lifepoints": 89,
            "consume": False,
            "action_label": "Smash with Rock hammer",
            "quick_unlock_key": "slayer_quick_finishers_unlocked",
            "source_status": (
                "period-exact below-90 LP reusable hammer requirement; "
                "Darkan/game-main reconcile combat and drops"
            ),
        },
        "stats": {
            "hitpoints": 1050,
            "attack": 75,
            "strength": 105,
            "defence": 107,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 20,
            "defence_slash": 20,
            "defence_crush": 0,
            "defence_magic": 20,
            "defence_ranged": 20,
            "melee_strength": 0,
        },
        "drops": GARGOYLE_DROPS,
        "source": (
            "https://runescape.wiki/w/Gargoyle?oldid=6579781; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/gargoyle_lvl_111.plugin.kts; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/gargoyle.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/drops/gargoyle.json"
        ),
    },
    "mutated_zygomite_level_74": {
        "display_name": "Mutated zygomite",
        "level": 74,
        "group": "Slayer",
        "required_slayer_level": 57,
        "quest_gate": "lost_city",
        "quest_gate_label": "Complete Lost City",
        "interaction_note": "Pick the fungi to reveal the zygomite, then fight it normally.",
        "attack_style": "magic",
        "attack_speed": 4,
        "respawn_delay": 59,
        "max_hit": 88,
        "slayer_xp": 65.0,
        "finisher": dict(MUTATED_ZYGOMITE_FINISHER),
        "stats": {
            "hitpoints": 650,
            "attack": 65,
            "strength": 65,
            "defence": 65,
            "magic": 65,
            "ranged": 65,
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
        "drops": MUTATED_ZYGOMITE_DROPS,
        "source": (
            "https://runescape.wiki/w/Mutated_zygomite?oldid=6530349; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/mutated_zygomite/"
            "mutated_zygomite_(74).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/drops/mutated_zygomite.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "src/main/java/com/rs/game/content/skills/slayer/npcs/MutatedZygomite.java"
        ),
        "source_status": (
            "period and Darkan reconcile identity, LP, Slayer XP, magical-melee "
            "maximum hit, stats, access, finishing behavior, and one resolved ordinary "
            "selector; four-tick attack speed is the standard bounded combat abstraction; "
            "the occasional 140-LP spore attack frequency remains source_blocked"
        ),
    },
    "mutated_zygomite_level_86": {
        "display_name": "Mutated zygomite",
        "level": 86,
        "group": "Slayer",
        "required_slayer_level": 57,
        "quest_gate": "lost_city",
        "quest_gate_label": "Complete Lost City",
        "interaction_note": "Pick the fungi to reveal the zygomite, then fight it normally.",
        "attack_style": "magic",
        "attack_speed": 4,
        "respawn_delay": 59,
        "max_hit": 88,
        "slayer_xp": 75.0,
        "finisher": dict(MUTATED_ZYGOMITE_FINISHER),
        "stats": {
            "hitpoints": 750,
            "attack": 75,
            "strength": 75,
            "defence": 75,
            "magic": 75,
            "ranged": 75,
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
        "drops": MUTATED_ZYGOMITE_DROPS,
        "source": (
            "https://runescape.wiki/w/Mutated_zygomite?oldid=6530349; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/mutated_zygomite/"
            "mutated_zygomite_(86).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/drops/mutated_zygomite.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "src/main/java/com/rs/game/content/skills/slayer/npcs/MutatedZygomite.java"
        ),
        "source_status": (
            "period and Darkan reconcile identity, LP, Slayer XP, magical-melee "
            "maximum hit, stats, access, finishing behavior, and one resolved ordinary "
            "selector; four-tick attack speed is the standard bounded combat abstraction; "
            "the occasional 140-LP spore attack frequency remains source_blocked"
        ),
    },
}
