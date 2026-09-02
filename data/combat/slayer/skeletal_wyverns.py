from __future__ import annotations

ENEMIES = {
    "skeletal_wyvern": {
    "display_name": "Skeletal Wyvern",
    "level": 198,
    "group": "Skeletal wyverns",
    "attack_style": "melee",
    "attack_speed": 6,
    "respawn_delay": 59,
    "slayer_xp": 210.0,
    "required_slayer_level": 72,
    "stats": {
        "hitpoints": 2000,
        "attack": 125,
        "strength": 116,
        "defence": 120,
        "magic": 125,
        "ranged": 120,
    },
    "bonuses": {
        "attack_stab": 0,
        "attack_slash": 0,
        "attack_crush": 0,
        "defence_stab": 140,
        "defence_slash": 90,
        "defence_crush": 90,
        "defence_magic": 80,
        "defence_ranged": 140,
        "melee_strength": 0,
    },
    "max_hit": 139,
    "interaction_note": (
        "Uses Melee, Ranged, and freezing ice breath. Elemental, Mind, Body, "
        "Cosmic, Chaos, and Dragonfire shields cap the breath at 150 LP; the "
        "Anti-dragon shield and antifire potions do not protect against it."
    ),
    # PLACEHOLDER(skeletal_wyvern.breath_attack_weight): a period-qualified selector or measured attack sample would replace the uniform branch weights.
    "attack_table": (
        {"kind": "attack", "style": "melee", "weight": 1},
        {"kind": "attack", "style": "ranged", "weight": 1},
        {"kind": "wyvern_breath", "weight": 1},
    ),
    "wyvern_breath": {
        "shielded_max_hit": 150,
        # PLACEHOLDER(skeletal_wyvern.freeze_ticks): a period server handler or qualified timed recording would replace this delay.
        "player_delay_ticks": 5,
        "source": (
            "https://runescape.wiki/w/Skeletal_Wyvern?oldid=6569736; "
            "https://runescape.wiki/w/Talk:Skeletal_Wyvern?oldid=5516744"
        ),
        "source_status": (
            "period shielded maximum, freeze behavior, and Talk-page evidence "
            "that ice breath bypasses ordinary Ranged protection prayer; freeze "
            "duration is a registered placeholder"
        ),
    },
    "protective_equipment": {
        "slot": "shield",
        "items": (
            "Elemental shield",
            "Mind shield",
            "Body shield",
            "Cosmic shield",
            "Chaos shield",
            "Dragonfire shield",
        ),
        "attack_kind": "wyvern_breath",
        "warning": "Wyvern ice breath is uncapped without a period-valid shield.",
        "unprotected_effect": {
            # PLACEHOLDER(skeletal_wyvern.unshielded_breath_max_hit): a period server handler or qualified damage sample would replace the executable 500-LP maximum.
            "damage": {"kind": "uniform_max", "max": 500},
        },
        "source_status": (
            "period valid-shield set; unshielded maximum is a registered placeholder"
        ),
    },
    "drops": {"guaranteed": (("Wyvern bones", 1),), "tables": ()},
    "source": (
        "https://runescape.wiki/w/Skeletal_Wyvern?oldid=6569736; "
        "Darkan data/npcs/combatdefs/uncategorized/skeletal_wyvern.json @ "
        "9376cbc21c31f30b9f4ae1712e7324dafe29387c; "
        "Darkan data/npcs/drops/skeletal_wyvern.json @ "
        "ede51d1a527980f5dd732e6266fec8f60c0c5225; rev-742 NPCs 3068-3071"
    ),
    "source_status": (
        "period identity, stats, cadence, ordinary maxima, breath envelopes, "
        "shield set, and guaranteed bones; optional ordinary loot omitted pending "
        "leaf-level reconciliation"
    ),
},
}
