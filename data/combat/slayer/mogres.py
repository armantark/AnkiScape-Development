"""Source-backed Mogre Combat target and unique drops."""

from __future__ import annotations

from ..contract import COMBAT_OGRE_SEED_DROP_TABLE

MOGRE_TARGET_ID = "mogre"
MOGRE_QUEST_ID = "skippy_and_the_mogres"
MOGRE_WIKI_SOURCE = "https://runescape.wiki/w/Mogre?oldid=6493220"
MOGRE_FISHING_EXPLOSIVE_SOURCE = (
    "https://runescape.wiki/w/Fishing_explosive?oldid=6153110"
)
MOGRE_DARKAN_COMBAT_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "data/npcs/combatdefs/uncategorized/mogre (noanims).json"
)
MOGRE_DARKAN_DROPS_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "data/npcs/drops/mogre.json"
)


ENEMIES = {MOGRE_TARGET_ID: {
    "display_name": "Mogre",
    "level": 60,
    "group": "Slayer",
    "required_slayer_level": 32,
    "quest_gate": MOGRE_QUEST_ID,
    "quest_gate_label": "Complete the Mogre miniquest",
    "required_items": {"Fishing explosive": 1},
    "required_items_label": "Fishing explosive x1 to lure a Mogre",
    "lure": {"item": "Fishing explosive", "consumed": True},
    "attack_style": "melee",
    "attack_speed": 6,
    "respawn_delay": 59,
    "max_hit": 89,
    "poison_immune": True,
    "slayer_xp": 48.0,
    "stats": {
        "hitpoints": 480,
        "attack": 58,
        "strength": 55,
        "defence": 48,
        "magic": 1,
        "ranged": 1,
    },
    # PLACEHOLDER(combat.mogre_combat_bonuses): exact numeric Mogre bonuses
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
        "guaranteed": (("Big bones", 1),),
        "tables": (
            {
                "name": "Darkan ordinary",
                "total": 128,
                "slots": (
                    {"item": "Fishing bait", "quantity": 5, "slots": 30},
                    {"item": "Raw swordfish", "quantity": 1, "slots": 20},
                    {"table": COMBAT_OGRE_SEED_DROP_TABLE, "slots": 13},
                    {"item": "Fishing bait", "quantity": 15, "slots": 10},
                    {"item": "Raw tuna", "quantity": 1, "slots": 9},
                    {"item": "Raw pike", "quantity": 1, "slots": 7},
                    {"item": "Mudskipper hat", "quantity": 1, "slots": 5},
                    {"item": "Water rune", "quantity": 5, "slots": 4},
                    {"item": "Water rune", "quantity": 7, "slots": 4},
                    {"item": "Water rune", "quantity": 14, "slots": 4},
                    {"item": "Raw salmon", "quantity": 1, "slots": 4},
                    {"item": "Raw herring", "quantity": 1, "slots": 3},
                    {"item": "Raw sardine", "quantity": 1, "slots": 3},
                    {"item": "Raw shark", "quantity": 1, "slots": 3},
                    {"item": "Oyster", "quantity": 1, "slots": 3},
                    {"item": "Flippers", "quantity": 1, "slots": 2},
                    {"item": "Seaweed", "quantity": 1, "slots": 2},
                    {"item": "Staff of water", "quantity": 1, "slots": 1},
                    {"slots": 1},
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
        ),
    },
    "interaction_note": (
        "Each new encounter consumes one Fishing explosive at an ominous "
        "fishing spot. One Mogre remains active until it dies or the player leaves."
    ),
    "source": "; ".join(
        (
            MOGRE_WIKI_SOURCE,
            MOGRE_FISHING_EXPLOSIVE_SOURCE,
            MOGRE_DARKAN_COMBAT_SOURCE,
            MOGRE_DARKAN_DROPS_SOURCE,
        )
    ),
    "source_status": (
        "period exact level, life points, Slayer gate/XP, melee style, six-tick "
        "cadence, maximum hit, poison immunity, miniquest gate, one-explosive "
        "lure, and one-at-a-time spawn; Darkan exact stats, respawn, 128-slot "
        "ordinary selector, 1,000-slot common-seed selector, and independent "
        "long/curved-bone table; numeric bonuses remain registered placeholders"
    ),
}}
