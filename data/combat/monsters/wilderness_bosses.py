from __future__ import annotations

ENEMIES = {
    "chaos_elemental": {
    "display_name": "Chaos Elemental",
    "npc_id": 3200,
    "level": 305,
    "group": "Wilderness bosses",
    "attack_style": "ranged",
    "attack_speed": 5,
    "respawn_delay": 119,
    "slayer_xp": 250.0,
    "stats": {
        "hitpoints": 2500,
        "attack": 270,
        "strength": 270,
        "defence": 270,
        "magic": 270,
        "ranged": 270,
    },
    "bonuses": {},
    "max_hit": 295,
    "interaction_note": (
        "Uses Magic, Ranged, and Melee attacks; teleport delays your next "
        "attack, and equipment removal moves one worn item into the active "
        "carried pack."
    ),
    # PLACEHOLDER(chaos_elemental.special_attack_weights): Darkan reconstruction pending a period-qualified rate table.
    "attack_table": (
        {"kind": "teleport", "weight": 11, "player_delay_ticks": 5},
        {"kind": "unequip", "weight": 8, "max_items": 1},
        {"kind": "attack", "style": "magic", "weight": 27},
        {"kind": "attack", "style": "ranged", "weight": 27},
        {"kind": "attack", "style": "melee", "weight": 27},
    ),
    "drops": {
        "guaranteed": (),
        "tables": (
            {
                "name": "Brawling gloves",
                # PLACEHOLDER(chaos_elemental.brawling_glove_drop_rate): preserves Darkan's per-pair weight while shipping only the six supported skilling pairs.
                "total": 1_300_000,
                "slots": (
                    {"item": "Brawling gloves (wc)", "quantity": 1, "slots": 187},
                    {"item": "Brawling gloves (fm)", "quantity": 1, "slots": 187},
                    {"item": "Brawling gloves (mining)", "quantity": 1, "slots": 187},
                    {"item": "Brawling gloves (smithing)", "quantity": 1, "slots": 187},
                    {"item": "Brawling gloves (fishing)", "quantity": 1, "slots": 187},
                    {"item": "Brawling gloves (cooking)", "quantity": 1, "slots": 187},
                    {"slots": 1_298_878},
                ),
            },
        ),
    },
    "wilderness_risk": {
        "ambush_chance": 0.01,
        "max_hit": 250,
        "unskulled_keep_count": 3,
    },
    "source": (
        "https://runescape.wiki/w/Chaos_Elemental?oldid=6544162; "
        "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
        "src/main/java/com/rs/game/content/bosses/ChaosElementalCombat.java; "
        "data/npcs/combatdefs/uncategorized/chaos_elemental.json; "
        "data/npcs/drops/chaos_elemental.json"
    ),
    "source_status": (
        "period identity/stats/mechanics; special and drop weights are registered placeholders"
    ),
},
}
