"""Source-backed Combat V1 data.

The enabled rows below are intentionally small: they have complete 2011Scape
combat stats and drop behavior, so runtime combat can fail closed for everything
else while the broader enemy audit continues.
"""

from __future__ import annotations

from typing import Dict, Tuple


DEFAULT_COMBAT_TARGET = "chicken"
DEFAULT_COMBAT_ATTACK_STYLE = "accurate"
DEFAULT_COMBAT_SPELL = "wind_strike"
COMBAT_BURST_TICKS = 50

COMBAT_SOURCE_ROOT = "/Users/ArmanTarkhanian1/Downloads/game-main"
MELEE_FORMULA_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/MeleeCombatFormula.kt"
)
MELEE_STRATEGY_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/MeleeCombatStrategy.kt"
)
ATTACK_STYLE_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/AttackStyleData.kt"
)
RANGED_FORMULA_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/RangedCombatFormula.kt"
)
RANGED_STRATEGY_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/RangedCombatStrategy.kt"
)
RANGED_BOW_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/ranged/weapon/BowType.kt"
)
RANGED_ARROW_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/ranged/ammo/Arrows.kt"
)
MAGIC_FORMULA_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/MagicCombatFormula.kt"
)
MAGIC_STRATEGY_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/MagicCombatStrategy.kt"
)
MAGIC_SPELL_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/magic/CombatSpell.kt"
)
MAGIC_SPELLBOOK_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/SpellbookData.kt"
)
MAGIC_SPELL_REQUIREMENT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/MagicSpells.kt"
)
MAGIC_STAVES_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/MagicStaves.kt"
)
FOOD_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/food/Food.kt"
)
POTION_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/potion/Potion.kt"
)
POTION_TYPE_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/potion/PotionType.kt"
)
DRAGONFIRE_FORMULA_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "src/main/java/com/rs/game/content/combat/PlayerCombat.kt"
)
LEATHER_DRAGON_COMBAT_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "src/main/java/com/rs/game/content/world/npcs/LeatherDragonCombat.java"
)
ITEM_ID_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt"
)
GLOBAL_HERBS_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt"
)
GLOBAL_SEEDS_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Seeds.kt"
)
GLOBAL_GEMS_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Gems.kt"
)
GLOBAL_RARE_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Rare.kt"
)
GLOBAL_MEGA_RARE_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/MegaRare.kt"
)


COMBAT_ATTACK_STYLE_DATA: Dict[str, dict] = {
    "accurate": {
        "display_name": "Accurate",
        "combat_class": "melee",
        "xp_mode": "attack",
        "source": f"{MELEE_FORMULA_SOURCE_PATH}: WeaponStyle.ACCURATE",
    },
    "aggressive": {
        "display_name": "Aggressive",
        "combat_class": "melee",
        "xp_mode": "strength",
        "source": f"{MELEE_FORMULA_SOURCE_PATH}: WeaponStyle.AGGRESSIVE",
    },
    "defensive": {
        "display_name": "Defensive",
        "combat_class": "melee",
        "xp_mode": "defense",
        "source": f"{MELEE_FORMULA_SOURCE_PATH}: WeaponStyle.DEFENSIVE",
    },
    "controlled": {
        "display_name": "Controlled",
        "combat_class": "melee",
        "xp_mode": "shared",
        "source": f"{MELEE_FORMULA_SOURCE_PATH}: WeaponStyle.CONTROLLED",
    },
    "ranged_accurate": {
        "display_name": "Ranged accurate",
        "combat_class": "ranged",
        "xp_mode": "ranged",
        "source": f"{RANGED_FORMULA_SOURCE_PATH}: WeaponStyle.ACCURATE",
    },
    "ranged_rapid": {
        "display_name": "Ranged rapid",
        "combat_class": "ranged",
        "xp_mode": "ranged",
        "attack_speed_delta": -1,
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/"
            "CombatConfigs.kt: WeaponStyle.RAPID"
        ),
    },
    "ranged_longrange": {
        "display_name": "Ranged longrange",
        "combat_class": "ranged",
        "xp_mode": "ranged_defense",
        "source": f"{RANGED_FORMULA_SOURCE_PATH}: WeaponStyle.LONG_RANGE",
    },
    "magic_standard": {
        "display_name": "Magic standard",
        "combat_class": "magic",
        "xp_mode": "magic",
        "source": f"{MAGIC_FORMULA_SOURCE_PATH}: Combat.CASTING_SPELL + MagicCombatStrategy.addCombatXp",
    },
}


# ``weapon_type`` ids (items.yml -> equipment.weapon_type) grouped by attack-style
# behaviour, transcribed slot-for-slot from AttackStyleData.kt's
# ``WeaponCombatData`` enum. Each row is one selectable combat style, in
# CombatStyle ordinal order, carrying:
#   * weapon_style -> drives the accuracy/effective-level bonus
#     (accurate/aggressive/defensive/controlled), matching COMBAT_ATTACK_STYLE_DATA.
#   * style_type   -> the melee attack type the formula rolls against
#     (stab/slash/crush): D1 full parity replaces the old max() with attack_<type>
#     vs defence_<type>.
#   * xp_mode      -> which skill(s) the hit trains. This is *independent* of
#     weapon_style: the two-handed-sword slot 3 is AGGRESSIVE for accuracy yet
#     SHARED for xp (the one AttackStyleData anomaly), so xp is resolved per-slot.
# WeaponType ids: NONE=0 STAFF=1 AXE=2 SCEPTRE=3 PICKAXE=4 DAGGER=5 LONG_SWORD=6
# TWO_HANDED=7 MACE=8 CLAWS=9 HAMMER=10 WHIP=11 HAMMER_EXTRA=12 SPEAR=14
# HALBERD=15 SCYTHE=22 FLAIL=23.
_ATTACK_STYLE_SRC = ATTACK_STYLE_SOURCE_PATH

# Typeless weapons and bare fists (weapon_type -1 / NONE / staves / sceptres /
# hammers) fall back to this UNARMED table -> all crush (D3).
WEAPON_TYPE_UNARMED_STYLES: Tuple[dict, ...] = (
    {"weapon_style": "accurate", "style_type": "crush", "xp_mode": "attack",
     "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.UNARMED slot 0"},
    {"weapon_style": "aggressive", "style_type": "crush", "xp_mode": "strength",
     "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.UNARMED slot 1"},
    {"weapon_style": "defensive", "style_type": "crush", "xp_mode": "defense",
     "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.UNARMED slot 2"},
)

WEAPON_TYPE_ATTACK_STYLES: Dict[int, Tuple[dict, ...]] = {
    # UNARMED group: NONE, STAFF, SCEPTRE, HAMMER, HAMMER_EXTRA.
    0: WEAPON_TYPE_UNARMED_STYLES,
    1: WEAPON_TYPE_UNARMED_STYLES,
    3: WEAPON_TYPE_UNARMED_STYLES,
    10: WEAPON_TYPE_UNARMED_STYLES,
    12: WEAPON_TYPE_UNARMED_STYLES,
    # AXE
    2: (
        {"weapon_style": "accurate", "style_type": "slash", "xp_mode": "attack",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.AXE slot 0"},
        {"weapon_style": "aggressive", "style_type": "slash", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.AXE slot 1"},
        {"weapon_style": "aggressive", "style_type": "crush", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.AXE slot 2"},
        {"weapon_style": "defensive", "style_type": "slash", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.AXE slot 3"},
    ),
    # PICKAXE
    4: (
        {"weapon_style": "accurate", "style_type": "stab", "xp_mode": "attack",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.PICKAXE slot 0"},
        {"weapon_style": "aggressive", "style_type": "stab", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.PICKAXE slot 1"},
        {"weapon_style": "aggressive", "style_type": "crush", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.PICKAXE slot 2"},
        {"weapon_style": "defensive", "style_type": "stab", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.PICKAXE slot 3"},
    ),
    # DAGGER
    5: (
        {"weapon_style": "accurate", "style_type": "stab", "xp_mode": "attack",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.DAGGER slot 0"},
        {"weapon_style": "aggressive", "style_type": "stab", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.DAGGER slot 1"},
        {"weapon_style": "aggressive", "style_type": "slash", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.DAGGER slot 2"},
        {"weapon_style": "defensive", "style_type": "stab", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.DAGGER slot 3"},
    ),
    # LONG_SWORD
    6: (
        {"weapon_style": "accurate", "style_type": "slash", "xp_mode": "attack",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.LONGSWORD slot 0"},
        {"weapon_style": "aggressive", "style_type": "slash", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.LONGSWORD slot 1"},
        {"weapon_style": "controlled", "style_type": "stab", "xp_mode": "shared",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.LONGSWORD slot 2"},
        {"weapon_style": "defensive", "style_type": "slash", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.LONGSWORD slot 3"},
    ),
    # TWO_HANDED_SWORD -- slot 2 is the AttackStyleData anomaly: AGGRESSIVE for
    # accuracy/effective-level, but SHARED xp (splits like controlled).
    7: (
        {"weapon_style": "accurate", "style_type": "slash", "xp_mode": "attack",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.TWO_HANDED_SWORD slot 0"},
        {"weapon_style": "aggressive", "style_type": "slash", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.TWO_HANDED_SWORD slot 1"},
        {"weapon_style": "aggressive", "style_type": "crush", "xp_mode": "shared",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.TWO_HANDED_SWORD slot 2 (aggressive/crush/SHARED anomaly)"},
        {"weapon_style": "defensive", "style_type": "slash", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.TWO_HANDED_SWORD slot 3"},
    ),
    # MACE
    8: (
        {"weapon_style": "accurate", "style_type": "crush", "xp_mode": "attack",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.MACE slot 0"},
        {"weapon_style": "aggressive", "style_type": "crush", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.MACE slot 1"},
        {"weapon_style": "controlled", "style_type": "stab", "xp_mode": "shared",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.MACE slot 2"},
        {"weapon_style": "defensive", "style_type": "crush", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.MACE slot 3"},
    ),
    # CLAWS
    9: (
        {"weapon_style": "accurate", "style_type": "slash", "xp_mode": "attack",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.CLAWS slot 0"},
        {"weapon_style": "aggressive", "style_type": "slash", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.CLAWS slot 1"},
        {"weapon_style": "controlled", "style_type": "stab", "xp_mode": "shared",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.CLAWS slot 2"},
        {"weapon_style": "defensive", "style_type": "slash", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.CLAWS slot 3"},
    ),
    # WHIP
    11: (
        {"weapon_style": "accurate", "style_type": "slash", "xp_mode": "attack",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.WHIP slot 0"},
        {"weapon_style": "controlled", "style_type": "slash", "xp_mode": "shared",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.WHIP slot 1"},
        {"weapon_style": "defensive", "style_type": "slash", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.WHIP slot 2"},
    ),
    # SPEAR
    14: (
        {"weapon_style": "controlled", "style_type": "stab", "xp_mode": "shared",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.SPEAR slot 0"},
        {"weapon_style": "controlled", "style_type": "slash", "xp_mode": "shared",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.SPEAR slot 1"},
        {"weapon_style": "controlled", "style_type": "crush", "xp_mode": "shared",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.SPEAR slot 2"},
        {"weapon_style": "defensive", "style_type": "stab", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.SPEAR slot 3"},
    ),
    # HALBERD
    15: (
        {"weapon_style": "controlled", "style_type": "stab", "xp_mode": "shared",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.HALBERD slot 0"},
        {"weapon_style": "aggressive", "style_type": "slash", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.HALBERD slot 1"},
        {"weapon_style": "defensive", "style_type": "stab", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.HALBERD slot 2"},
    ),
    # SCYTHE
    22: (
        {"weapon_style": "accurate", "style_type": "slash", "xp_mode": "attack",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.SCYTHE slot 0"},
        {"weapon_style": "aggressive", "style_type": "stab", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.SCYTHE slot 1"},
        {"weapon_style": "aggressive", "style_type": "crush", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.SCYTHE slot 2"},
        {"weapon_style": "defensive", "style_type": "slash", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.SCYTHE slot 3"},
    ),
    # FLAIL
    23: (
        {"weapon_style": "accurate", "style_type": "slash", "xp_mode": "attack",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.FLAIL slot 0"},
        {"weapon_style": "aggressive", "style_type": "crush", "xp_mode": "strength",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.FLAIL slot 1"},
        {"weapon_style": "defensive", "style_type": "slash", "xp_mode": "defense",
         "source": f"{_ATTACK_STYLE_SRC}: WeaponCombatData.FLAIL slot 2"},
    ),
}


COMBAT_RANGED_WEAPON_DATA: Dict[str, dict] = {
    "Shortbow": {
        "equipment_type": "shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS",
    },
    "Longbow": {
        "equipment_type": "longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS",
    },
    "Oak shortbow": {
        "equipment_type": "oak_shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: OAK_SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS",
    },
    "Oak longbow": {
        "equipment_type": "oak_longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: OAK_LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS",
    },
    "Willow shortbow": {
        "equipment_type": "willow_shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: WILLOW_SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS",
    },
    "Willow longbow": {
        "equipment_type": "willow_longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: WILLOW_LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS",
    },
    "Maple shortbow": {
        "equipment_type": "maple_shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: MAPLE_SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS",
    },
    "Maple longbow": {
        "equipment_type": "maple_longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: MAPLE_LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS",
    },
    "Yew shortbow": {
        "equipment_type": "yew_shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: YEW_SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS + RUNE_ARROWS",
    },
    "Yew longbow": {
        "equipment_type": "yew_longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: YEW_LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS + RUNE_ARROWS",
    },
    "Magic shortbow": {
        "equipment_type": "magic_shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: MAGIC_SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS + RUNE_ARROWS; BROAD_ARROWS deferred until ammo skill gates exist",
    },
    "Magic longbow": {
        "equipment_type": "magic_longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: MAGIC_LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS + RUNE_ARROWS; BROAD_ARROWS deferred until ammo skill gates exist",
    },
}


COMBAT_RANGED_AMMO_DATA: Dict[str, dict] = {
    "Bronze arrows": {
        "source_item_id": 882,
        "source_item_name": "Bronze arrow",
        "ranged_strength": 7,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: BRONZE_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 882"
        ),
    },
    "Iron arrows": {
        "source_item_id": 884,
        "source_item_name": "Iron arrow",
        "ranged_strength": 10,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: IRON_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 884"
        ),
    },
    "Steel arrows": {
        "source_item_id": 886,
        "source_item_name": "Steel arrow",
        "ranged_strength": 16,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: STEEL_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 886"
        ),
    },
    "Mithril arrows": {
        "source_item_id": 888,
        "source_item_name": "Mithril arrow",
        "ranged_strength": 22,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: MITHRIL_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 888"
        ),
    },
    "Adamant arrows": {
        "source_item_id": 890,
        "source_item_name": "Adamant arrow",
        "ranged_strength": 31,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: ADAMANT_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 890"
        ),
    },
    "Rune arrows": {
        "source_item_id": 892,
        "source_item_name": "Rune arrow",
        "ranged_strength": 49,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: RUNE_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 892"
        ),
    },
}


COMBAT_MAGIC_SPELL_DATA: Dict[str, dict] = {
    "wind_strike": {
        "display_name": "Wind Strike",
        "spellbook": "standard",
        "required_magic_level": 1,
        "rune_cost": {"Air rune": 1, "Mind rune": 1},
        "max_hit_old_hp": 2,
        "base_magic_xp": 5.5,
        "attack_speed": 5,
        "unique_id": 15,
        "component_id": 25,
        "autocast_id": 3,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WIND_STRIKE maxHit=2 experience=5.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WIND_STRIKE level=1 runes AIR_RUNE x1 MIND_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "water_strike": {
        "display_name": "Water Strike",
        "spellbook": "standard",
        "required_magic_level": 5,
        "rune_cost": {"Air rune": 1, "Mind rune": 1, "Water rune": 1},
        "max_hit_old_hp": 4,
        "base_magic_xp": 7.5,
        "attack_speed": 5,
        "unique_id": 17,
        "component_id": 28,
        "autocast_id": 5,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WATER_STRIKE maxHit=4 experience=7.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WATER_STRIKE level=5 runes AIR_RUNE x1 MIND_RUNE x1 WATER_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "earth_strike": {
        "display_name": "Earth Strike",
        "spellbook": "standard",
        "required_magic_level": 9,
        "rune_cost": {"Air rune": 1, "Mind rune": 1, "Earth rune": 2},
        "max_hit_old_hp": 6,
        "base_magic_xp": 9.5,
        "attack_speed": 5,
        "unique_id": 19,
        "component_id": 30,
        "autocast_id": 7,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: EARTH_STRIKE maxHit=6 experience=9.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: EARTH_STRIKE level=9 runes AIR_RUNE x1 MIND_RUNE x1 EARTH_RUNE x2; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "fire_strike": {
        "display_name": "Fire Strike",
        "spellbook": "standard",
        "required_magic_level": 13,
        "rune_cost": {"Air rune": 1, "Mind rune": 1, "Fire rune": 3},
        "max_hit_old_hp": 8,
        "base_magic_xp": 11.5,
        "attack_speed": 5,
        "unique_id": 71,
        "component_id": 32,
        "autocast_id": 9,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: FIRE_STRIKE maxHit=8 experience=11.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: FIRE_STRIKE level=13 runes AIR_RUNE x1 MIND_RUNE x1 FIRE_RUNE x3; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "wind_bolt": {
        "display_name": "Wind Bolt",
        "spellbook": "standard",
        "required_magic_level": 17,
        "rune_cost": {"Air rune": 2, "Chaos rune": 1},
        "max_hit_old_hp": 9,
        "base_magic_xp": 13.5,
        "attack_speed": 5,
        "unique_id": 73,
        "component_id": 34,
        "autocast_id": 11,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WIND_BOLT maxHit=9 experience=13.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WIND_BOLT level=17 runes AIR_RUNE x2 CHAOS_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "water_bolt": {
        "display_name": "Water Bolt",
        "spellbook": "standard",
        "required_magic_level": 23,
        "rune_cost": {"Air rune": 2, "Water rune": 2, "Chaos rune": 1},
        "max_hit_old_hp": 10,
        "base_magic_xp": 16.5,
        "attack_speed": 5,
        "unique_id": 76,
        "component_id": 39,
        "autocast_id": 13,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WATER_BOLT maxHit=10 experience=16.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WATER_BOLT level=23 runes AIR_RUNE x2 WATER_RUNE x2 CHAOS_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "earth_bolt": {
        "display_name": "Earth Bolt",
        "spellbook": "standard",
        "required_magic_level": 29,
        "rune_cost": {"Air rune": 2, "Earth rune": 3, "Chaos rune": 1},
        "max_hit_old_hp": 11,
        "base_magic_xp": 19.5,
        "attack_speed": 5,
        "unique_id": 79,
        "component_id": 42,
        "autocast_id": 15,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: EARTH_BOLT maxHit=11 experience=19.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: EARTH_BOLT level=29 runes AIR_RUNE x2 EARTH_RUNE x3 CHAOS_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "fire_bolt": {
        "display_name": "Fire Bolt",
        "spellbook": "standard",
        "required_magic_level": 35,
        "rune_cost": {"Air rune": 3, "Fire rune": 4, "Chaos rune": 1},
        "max_hit_old_hp": 12,
        "base_magic_xp": 22.5,
        "attack_speed": 5,
        "unique_id": 82,
        "component_id": 45,
        "autocast_id": 17,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: FIRE_BOLT maxHit=12 experience=22.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: FIRE_BOLT level=35 runes AIR_RUNE x3 FIRE_RUNE x4 CHAOS_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "wind_blast": {
        "display_name": "Wind Blast",
        "spellbook": "standard",
        "required_magic_level": 41,
        "rune_cost": {"Air rune": 3, "Death rune": 1},
        "max_hit_old_hp": 13,
        "base_magic_xp": 25.5,
        "attack_speed": 5,
        "unique_id": 85,
        "component_id": 49,
        "autocast_id": 19,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WIND_BLAST maxHit=13 experience=25.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WIND_BLAST level=41 runes AIR_RUNE x3 DEATH_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "water_blast": {
        "display_name": "Water Blast",
        "spellbook": "standard",
        "required_magic_level": 47,
        "rune_cost": {"Air rune": 3, "Water rune": 3, "Death rune": 1},
        "max_hit_old_hp": 14,
        "base_magic_xp": 28.5,
        "attack_speed": 5,
        "unique_id": 88,
        "component_id": 52,
        "autocast_id": 21,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WATER_BLAST maxHit=14 experience=28.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WATER_BLAST level=47 runes AIR_RUNE x3 WATER_RUNE x3 DEATH_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "earth_blast": {
        "display_name": "Earth Blast",
        "spellbook": "standard",
        "required_magic_level": 53,
        "rune_cost": {"Air rune": 3, "Earth rune": 4, "Death rune": 1},
        "max_hit_old_hp": 15,
        "base_magic_xp": 31.5,
        "attack_speed": 5,
        "unique_id": 90,
        "component_id": 58,
        "autocast_id": 23,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: EARTH_BLAST maxHit=15 experience=31.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: EARTH_BLAST level=53 runes AIR_RUNE x3 EARTH_RUNE x4 DEATH_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "fire_blast": {
        "display_name": "Fire Blast",
        "spellbook": "standard",
        "required_magic_level": 59,
        "rune_cost": {"Air rune": 4, "Fire rune": 5, "Death rune": 1},
        "max_hit_old_hp": 16,
        "base_magic_xp": 34.5,
        "attack_speed": 5,
        "unique_id": 95,
        "component_id": 63,
        "autocast_id": 25,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: FIRE_BLAST maxHit=16 experience=34.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: FIRE_BLAST level=59 runes AIR_RUNE x4 FIRE_RUNE x5 DEATH_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "wind_wave": {
        "display_name": "Wind Wave",
        "spellbook": "standard",
        "required_magic_level": 62,
        "rune_cost": {"Air rune": 5, "Blood rune": 1},
        "max_hit_old_hp": 17,
        "base_magic_xp": 36.0,
        "attack_speed": 5,
        "unique_id": 96,
        "component_id": 70,
        "autocast_id": 27,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WIND_WAVE maxHit=17 experience=36.0; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WIND_WAVE level=62 runes AIR_RUNE x5 BLOOD_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "water_wave": {
        "display_name": "Water Wave",
        "spellbook": "standard",
        "required_magic_level": 65,
        "rune_cost": {"Air rune": 5, "Water rune": 7, "Blood rune": 1},
        "max_hit_old_hp": 18,
        "base_magic_xp": 37.5,
        "attack_speed": 5,
        "unique_id": 98,
        "component_id": 73,
        "autocast_id": 29,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WATER_WAVE maxHit=18 experience=37.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WATER_WAVE level=65 runes AIR_RUNE x5 WATER_RUNE x7 BLOOD_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "earth_wave": {
        "display_name": "Earth Wave",
        "spellbook": "standard",
        "required_magic_level": 70,
        "rune_cost": {"Air rune": 5, "Earth rune": 7, "Blood rune": 1},
        "max_hit_old_hp": 19,
        "base_magic_xp": 40.0,
        "attack_speed": 5,
        "unique_id": 101,
        "component_id": 77,
        "autocast_id": 31,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: EARTH_WAVE maxHit=19 experience=40.0; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: EARTH_WAVE level=70 runes AIR_RUNE x5 EARTH_RUNE x7 BLOOD_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "fire_wave": {
        "display_name": "Fire Wave",
        "spellbook": "standard",
        "required_magic_level": 75,
        "rune_cost": {"Air rune": 5, "Fire rune": 7, "Blood rune": 1},
        "max_hit_old_hp": 20,
        "base_magic_xp": 42.5,
        "attack_speed": 5,
        "unique_id": 102,
        "component_id": 80,
        "autocast_id": 33,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: FIRE_WAVE maxHit=20 experience=42.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: FIRE_WAVE level=75 runes AIR_RUNE x5 FIRE_RUNE x7 BLOOD_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
}

# The standalone Magic continuation owns pre-EOC gap spells while Combat keeps
# the original rev-667 ladder.  Import late to avoid making magic_data depend on
# Combat internals and preserve the existing stable spell IDs.
try:
    from .magic_data import combat_magic_additions_as_dict
except ImportError:
    from magic_data import combat_magic_additions_as_dict

COMBAT_MAGIC_SPELL_DATA.update(combat_magic_additions_as_dict())


COMBAT_MAGIC_STAFF_DATA: Dict[str, dict] = {
    "Staff of air": {
        "covered_runes": ("Air rune",),
        "source_item_id": 1381,
        "source": f"{MAGIC_STAVES_SOURCE_PATH}: AIR_RUNE uses STAFF_OF_AIR; {ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_AIR",
    },
    "Staff of water": {
        "covered_runes": ("Water rune",),
        "source_item_id": 1383,
        "source": f"{MAGIC_STAVES_SOURCE_PATH}: WATER_RUNE uses STAFF_OF_WATER; {ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_WATER",
    },
    "Staff of earth": {
        "covered_runes": ("Earth rune",),
        "source_item_id": 1385,
        "source": f"{MAGIC_STAVES_SOURCE_PATH}: EARTH_RUNE uses STAFF_OF_EARTH; {ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_EARTH",
    },
    "Staff of fire": {
        "covered_runes": ("Fire rune",),
        "source_item_id": 1387,
        "source": f"{MAGIC_STAVES_SOURCE_PATH}: FIRE_RUNE uses STAFF_OF_FIRE; {ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_FIRE",
    },
    "Saradomin staff": {
        "covered_runes": (),
        "source_item_id": 2415,
        "source": (
            f"{ITEM_ID_SOURCE_PATH}: Items.SARADOMIN_STAFF; "
            "RuneScape Wiki Mage Arena oldid=6512911"
        ),
    },
    "Guthix staff": {
        "covered_runes": (),
        "source_item_id": 2416,
        "source": (
            f"{ITEM_ID_SOURCE_PATH}: Items.GUTHIX_STAFF; "
            "RuneScape Wiki Mage Arena oldid=6512911"
        ),
    },
    "Zamorak staff": {
        "covered_runes": (),
        "source_item_id": 2417,
        "source": (
            f"{ITEM_ID_SOURCE_PATH}: Items.ZAMORAK_STAFF; "
            "RuneScape Wiki Mage Arena oldid=6512911"
        ),
    },
}


GOBLIN_LEVEL_2_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_2.plugin.kts"
)
GOBLIN_LEVEL_5_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_5.plugin.kts"
)
GOBLIN_LEVEL_11_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_11.plugin.kts"
)
GOBLIN_LEVEL_13_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_13.plugin.kts"
)
GOBLIN_LEVEL_16_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_16.plugin.kts"
)
GOBLIN_LEVEL_25_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_25.plugin.kts"
)
HOBGOBLIN_UNARMED_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/hobgoblin_unarmed_level_28.plugin.kts"
)
HOBGOBLIN_ARMED_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/hobgoblin_armed_lvl_28.plugin.kts"
)
TZHAAR_KET_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/tzhaar_ket_lvl_149.plugin.kts"
)
ALKHARID_WARRIOR_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/alkharid_warrior_level_9.plugin.kts"
)
MUGGER_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/mugger_level_6.plugin.kts"
)
OUTLAW_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/outlaw_level_35.plugin.kts"
)
CHAOS_DWARF_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/chaos_dwarf_lvl_48.plugin.kts"
)
HAAKON_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/haakon_the_champion_lvl_29.plugin.kts"
)
HAM_GUARD_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/ham_guard_level_12_18_22.plugin.kts"
)
IMP_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/demons/imp_level_2.plugin.kts"
)
THUG_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/thug_level_10.plugin.kts"
)
THIEF_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/thief_level_16.plugin.kts"
)
CITIZEN_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/citizen_level_2.plugin.kts"
)
MONK_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/monk_level_5.plugin.kts"
)
MONK_OF_ZAMORAK_LEVEL_45_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/monk_of_zamorak_lvl_45.plugin.kts"
)
CUFFS_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/cuffs_level_3.plugin.kts"
)
NARF_JEFF_RUSTY_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/narf_jeff_rusty_level_2.plugin.kts"
)
PIRATE_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/pirate_level_23.plugin.kts"
)
GIANT_RAT_LEVEL_6_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/giant_rat_level_6.plugin.kts"
)
GIANT_RAT_LEVEL_26_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/giant_rat_level_26.plugin.kts"
)
UNICORN_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/unicorn_level_15.plugin.kts"
)
BLACK_UNICORN_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/black_unicorn_level_27.plugin.kts"
)
BLACK_BEAR_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/black_bear_level_19.plugin.kts"
)
WOLF_LEVEL_11_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/wolf_lvl_11.plugin.kts"
)
WHITE_WOLF_LEVEL_25_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/white_wolf_lvl_25.plugin.kts"
)
WHITE_WOLF_LEVEL_38_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/white_wolf_lvl_38.plugin.kts"
)
BIG_WOLF_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/big_wolf_lvl_73.plugin.kts"
)
GIANT_BAT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/giant_bat_level_27.plugin.kts"
)
HILL_GIANT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/hill_giant_lvl_28.plugin.kts"
)
MOSS_GIANT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/moss_giant_level_42.plugin.kts"
)
ICE_GIANT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/ice_giant_level_53.plugin.kts"
)
GHOST_LEVEL_19_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/ghost_level_19.plugin.kts"
)
ZOMBIE_LEVEL_13_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_13.plugin.kts"
)
ZOMBIE_LEVEL_18_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_18.plugin.kts"
)
ZOMBIE_LEVEL_24_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_24.plugin.kts"
)
ZOMBIE_LEVEL_25_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_25.plugin.kts"
)
ZOMBIE_LEVEL_30_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_30.plugin.kts"
)
ZOMBIE_LEVEL_44_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_44.plugin.kts"
)
ZOMBIE_LEVEL_53_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_53.plugin.kts"
)
SKELETON_LEVEL_21_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_21.plugin.kts"
)
SKELETON_LEVEL_22_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_22.plugin.kts"
)
SKELETON_LEVEL_25_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_25.plugin.kts"
)
SKELETON_LEVEL_45_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_level_45.plugin.kts"
)
SKELETON_LEVEL_60_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_60.plugin.kts"
)
SKELETON_LEVEL_68_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_68.plugin.kts"
)
SKELETON_LEVEL_85_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_85.plugin.kts"
)
DUCK_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/duck_level_1.plugin.kts"
)
GUARD_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/guard_level_21.plugin.kts"
)
JAIL_GUARD_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/jail_guard_level_26.plugin.kts"
)
MARKET_GUARD_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/market_guard_level_20.plugin.kts"
)
BLACK_KNIGHT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/black_knight_level_33.plugin.kts"
)
CHAOS_DRUID_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/chaos_druid_lvl_13.plugin.kts"
)
WHITE_KNIGHT_LEVEL_36_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/white_knight_level_36.plugin.kts"
)
WHITE_KNIGHT_LEVEL_38_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/white_knight_level_38.plugin.kts"
)
WHITE_KNIGHT_LEVEL_39_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/white_knight_level_39.plugin.kts"
)
WHITE_KNIGHT_LEVEL_42_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/white_knight_level_42.plugin.kts"
)
DWARF_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/dwarf_level_10_11.plugin.kts"
)
FARMER_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/farmer_level_7.plugin.kts"
)

POISON_SCORPION_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/poison_scorpion_lvl_20.plugin.kts"
)
POISON_SPIDER_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/poison_spider_lvl_31.plugin.kts"
)
POISON_SPIDER_LEVEL_64_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/poison_spider_lvl_64.plugin.kts"
)
SCORPION_LEVEL_14_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/scorpion_level_14.plugin.kts"
)
KING_SCORPION_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/king_scorpion_level_32.plugin.kts"
)
PIT_SCORPION_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/pit_sorpion_lvl_28.plugin.kts"
)
SCORPION_LEVEL_59_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/scorpion_level_59.plugin.kts"
)
SPIDER_LEVEL_24_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/spider_level_24.plugin.kts"
)
DEADLY_RED_SPIDER_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/deadly_red_spider_level_34.plugin.kts"
)
GIANT_SPIDER_LEVEL_50_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/giant_spider_level_50.plugin.kts"
)


COMBAT_MINOR_HERB_DROP_TABLE = {
    "name": "Minor herb",
    "source": f"{GLOBAL_HERBS_SOURCE_PATH}: Herbs.minorHerbTable",
    "total": 1024,
    "slots": (
        {"item": "Grimy guam", "quantity": 1, "slots": 249},
        {"item": "Grimy marrentill", "quantity": 1, "slots": 198},
        {"item": "Grimy tarromin", "quantity": 1, "slots": 146},
        {"item": "Grimy harralander", "quantity": 1, "slots": 114},
        {"item": "Grimy ranarr", "quantity": 1, "slots": 85},
        {"item": "Grimy irit", "quantity": 1, "slots": 64},
        {"item": "Grimy avantoe", "quantity": 1, "slots": 49},
        {"item": "Grimy kwuarm", "quantity": 1, "slots": 39},
        {"item": "Grimy cadantine", "quantity": 1, "slots": 32},
        {"item": "Grimy lantadyme", "quantity": 1, "slots": 24},
        {"item": "Grimy dwarf weed", "quantity": 1, "slots": 24},
    ),
}


COMBAT_ALLOTMENT_SEED_DROP_TABLE = {
    "name": "Allotment seed",
    "source": f"{GLOBAL_SEEDS_SOURCE_PATH}: Seeds.allotmentSeedTable",
    "total": 90,
    "slots": (
        {"item": "Potato seed", "quantity": 4, "slots": 32},
        {"item": "Onion seed", "quantity": 4, "slots": 25},
        {"item": "Cabbage seed", "quantity": 4, "slots": 16},
        {"item": "Tomato seed", "quantity": 3, "slots": 9},
        {"item": "Sweetcorn seed", "quantity": 3, "slots": 5},
        {"item": "Strawberry seed", "quantity": 2, "slots": 2},
        {"item": "Watermelon seed", "quantity": 2, "slots": 1},
    ),
}


COMBAT_UNCOMMON_SEED_DROP_TABLE = {
    "name": "Uncommon seed",
    "source": f"{GLOBAL_SEEDS_SOURCE_PATH}: Seeds.uncommonSeedTable",
    "total": 1048,
    "slots": (
        {"item": "Limpwurt seed", "quantity": 1, "slots": 137},
        {"item": "Strawberry seed", "quantity": 1, "slots": 131},
        {"item": "Marrentill seed", "quantity": 1, "slots": 125},
        {"item": "Jangerberry seed", "quantity": 1, "slots": 92},
        {"item": "Tarromin seed", "quantity": 1, "slots": 85},
        {"item": "Wildblood seed", "quantity": 1, "slots": 83},
        {"item": "Watermelon seed", "quantity": 1, "slots": 83},
        {"item": "Harralander seed", "quantity": 1, "slots": 86},
        {"item": "Ranarr seed", "quantity": 1, "slots": 49},
        {"item": "Whiteberry seed", "quantity": 1, "slots": 39},
        {"item": "Toadflax seed", "quantity": 1, "slots": 27},
        {"item": "Belladonna seed", "quantity": 1, "slots": 18},
        {"item": "Irit seed", "quantity": 1, "slots": 18},
        {"item": "Poison ivy seed", "quantity": 1, "slots": 13},
        {"item": "Avantoe seed", "quantity": 1, "slots": 18},
        {"item": "Cactus seed", "quantity": 1, "slots": 16},
        {"item": "Kwuarm seed", "quantity": 1, "slots": 13},
        {"item": "Snapdragon seed", "quantity": 1, "slots": 5},
        {"item": "Cadantine seed", "quantity": 1, "slots": 4},
        {"item": "Lantadyme seed", "quantity": 1, "slots": 3},
        {"item": "Dwarf weed seed", "quantity": 1, "slots": 2},
        {"item": "Torstol seed", "quantity": 1, "slots": 1},
    ),
}

COMBAT_OGRE_SEED_DROP_TABLE = {
    "name": "Ogre common seed",
    "source": (
        "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
        "darkan-world-server/data/npcs/drops/special_tables/common_seeds.json"
    ),
    "total": 1000,
    "slots": (
        {"item": "Limpwurt seed", "quantity": 1, "slots": 135},
        {"item": "Strawberry seed", "quantity": 1, "slots": 131},
        {"item": "Marrentill seed", "quantity": 1, "slots": 123},
        {"item": "Jangerberry seed", "quantity": 1, "slots": 94},
        {"item": "Tarromin seed", "quantity": 1, "slots": 84},
        {"item": "Wildblood seed", "quantity": 1, "slots": 83},
        {"item": "Watermelon seed", "quantity": 1, "slots": 63},
        {"item": "Harralander seed", "quantity": 1, "slots": 58},
        {"item": "Ranarr seed", "quantity": 1, "slots": 40},
        {"item": "Whiteberry seed", "quantity": 1, "slots": 34},
        {"item": "Bittercap mushroom spore", "quantity": 1, "slots": 29},
        {"item": "Toadflax seed", "quantity": 1, "slots": 27},
        {"item": "Irit seed", "quantity": 1, "slots": 18},
        {"item": "Belladonna seed", "quantity": 1, "slots": 18},
        {"item": "Poison ivy seed", "quantity": 1, "slots": 13},
        {"item": "Cactus seed", "quantity": 1, "slots": 12},
        {"item": "Avantoe seed", "quantity": 1, "slots": 12},
        {"item": "Kwuarm seed", "quantity": 1, "slots": 9},
        {"item": "Snapdragon seed", "quantity": 1, "slots": 6},
        {"item": "Cadantine seed", "quantity": 1, "slots": 4},
        {"item": "Lantadyme seed", "quantity": 1, "slots": 3},
        {"item": "Dwarf weed seed", "quantity": 1, "slots": 2},
        {"item": "Torstol seed", "quantity": 1, "slots": 1},
        {"slots": 1},
    ),
}


COMBAT_MEGA_RARE_DROP_TABLE = {
    "name": "Mega rare",
    "source": f"{GLOBAL_MEGA_RARE_SOURCE_PATH}: MegaRare.megaRareTable without Ring of Wealth",
    "total": 1024,
    "slots": (
        {"slots": 904},
        {"item": "Rune spear", "quantity": 1, "slots": 64},
        {"item": "Shield left half", "quantity": 1, "slots": 32},
        {"item": "Dragon spear", "quantity": 1, "slots": 24},
    ),
}


COMBAT_GEM_DROP_TABLE = {
    "name": "Gem",
    "source": f"{GLOBAL_GEMS_SOURCE_PATH}: Gems.gemTable without Ring of Wealth",
    "total": 1024,
    "slots": (
        {"slots": 512},
        {"item": "Uncut sapphire", "quantity": 1, "slots": 240},
        {"item": "Uncut emerald", "quantity": 1, "slots": 112},
        {"item": "Uncut ruby", "quantity": 1, "slots": 64},
        {"item": "Chaos talisman", "quantity": 1, "slots": 24},
        {"item": "Nature talisman", "quantity": 1, "slots": 24},
        {"item": "Uncut diamond", "quantity": 1, "slots": 16},
        {"item": "Rune javelin", "quantity": 5, "slots": 8},
        {"item": "Loop half of a key", "quantity": 1, "slots": 8},
        {"item": "Tooth half of a key", "quantity": 1, "slots": 8},
        {"table": COMBAT_MEGA_RARE_DROP_TABLE, "slots": 8},
    ),
}

DARKAN_HERB_DROP_TABLE = {
    "name": "Darkan herb",
    "source": (
        "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
        "darkan-world-server/data/npcs/drops/special_tables/herb.json"
    ),
    "total": 128,
    "slots": (
        {"item": "Grimy guam", "quantity": 1, "slots": 32},
        {"item": "Grimy marrentill", "quantity": 1, "slots": 24},
        {"item": "Grimy tarromin", "quantity": 1, "slots": 18},
        {"item": "Grimy harralander", "quantity": 1, "slots": 14},
        {"item": "Grimy ranarr", "quantity": 1, "slots": 11},
        {"item": "Grimy irit", "quantity": 1, "slots": 8},
        {"item": "Grimy avantoe", "quantity": 1, "slots": 6},
        {"item": "Grimy kwuarm", "quantity": 1, "slots": 5},
        {"item": "Grimy cadantine", "quantity": 1, "slots": 4},
        {"item": "Grimy lantadyme", "quantity": 1, "slots": 3},
        {"item": "Grimy dwarf weed", "quantity": 1, "slots": 3},
    ),
}

DARKAN_ABERRANT_RARE_SEED_DROP_TABLE = {
    "name": "Darkan rare seed",
    "source": (
        "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
        "darkan-world-server/data/npcs/drops/special_tables/rare_seeds.json"
    ),
    "total": 125,
    "slots": (
        {"item": "Toadflax seed", "quantity": 1, "slots": 27},
        {"item": "Irit seed", "quantity": 1, "slots": 18},
        {"item": "Belladonna seed", "quantity": 1, "slots": 18},
        {"item": "Poison ivy seed", "quantity": 1, "slots": 13},
        {"item": "Cactus seed", "quantity": 1, "slots": 12},
        {"item": "Avantoe seed", "quantity": 1, "slots": 12},
        {"item": "Kwuarm seed", "quantity": 1, "slots": 9},
        {"item": "Snapdragon seed", "quantity": 1, "slots": 6},
        {"item": "Cadantine seed", "quantity": 1, "slots": 4},
        {"item": "Lantadyme seed", "quantity": 1, "slots": 3},
        {"item": "Dwarf weed seed", "quantity": 1, "slots": 2},
        {"item": "Torstol seed", "quantity": 1, "slots": 1},
    ),
}

DARKAN_MEGA_RARE_DROP_TABLE = {
    "name": "Darkan mega rare",
    "source": (
        "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
        "darkan-world-server/data/npcs/drops/special_tables/rdt_mega_rare.json"
    ),
    "total": 256,
    "slots": (
        {"item": "Rune spear", "quantity": 1, "slots": 16},
        {"item": "Shield left half", "quantity": 1, "slots": 8},
        {"item": "Dragon spear", "quantity": 1, "slots": 6},
        {"item": "Vecna skull", "quantity": 1, "slots": 1},
        {"slots": 225},
    ),
}

DARKAN_GEM_DROP_TABLE = {
    "name": "Darkan gem",
    "source": (
        "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
        "darkan-world-server/data/npcs/drops/special_tables/rdt_gem.json"
    ),
    "total": 128,
    "slots": (
        {"item": "Uncut sapphire", "quantity": 1, "slots": 32},
        {"item": "Uncut emerald", "quantity": 1, "slots": 16},
        {"item": "Uncut ruby", "quantity": 1, "slots": 8},
        {"item": "Chaos talisman", "quantity": 1, "slots": 3},
        {"item": "Uncut diamond", "quantity": 1, "slots": 2},
        {"item": "Rune javelin", "quantity": 5, "slots": 1},
        {"item": "Tooth half of a key", "quantity": 1, "slots": 1},
        {"item": "Loop half of a key", "quantity": 1, "slots": 1},
        {"table": DARKAN_MEGA_RARE_DROP_TABLE, "slots": 1},
        {"slots": 63},
    ),
}


COMBAT_RARE_DROP_TABLE = {
    "name": "Rare",
    "source": f"{GLOBAL_RARE_SOURCE_PATH}: Rare.rareTable",
    "total": 1024,
    "slots": (
        {"item": "Nature rune", "quantity": 67, "slots": 24},
        {"item": "Adamant javelin", "quantity": 20, "slots": 16},
        {"item": "Death rune", "quantity": 45, "slots": 16},
        {"item": "Law rune", "quantity": 45, "slots": 16},
        {"item": "Rune arrows", "quantity": 42, "slots": 16},
        {"item": "Steel arrows", "quantity": 150, "slots": 16},
        {"item": "Rune 2h sword", "quantity": 1, "slots": 24},
        {"item": "Rune battleaxe", "quantity": 1, "slots": 24},
        {"item": "Rune sq shield", "quantity": 1, "slots": 16},
        {"item": "Dragon med helm", "quantity": 1, "slots": 8},
        {"item": "Rune kiteshield", "quantity": 1, "slots": 8},
        {"item": "Coins", "quantity": 3000, "slots": 168},
        {"item": "Loop half of a key", "quantity": 1, "slots": 160},
        {"item": "Tooth half of a key", "quantity": 1, "slots": 160},
        {"item": "Rune bar", "quantity": 1, "slots": 40},
        {"item": "Dragonstone", "quantity": 1, "slots": 16},
        {"item": "Silver ore", "quantity": 100, "slots": 16},
        {"table": COMBAT_GEM_DROP_TABLE, "slots": 160},
        {"table": COMBAT_MEGA_RARE_DROP_TABLE, "slots": 120},
    ),
}


GOBLIN_LEVEL_2_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Bronze sq shield", "quantity": 1, "slots": 24},
                {"item": "Bronze spear", "quantity": 1, "slots": 32},
                {"item": "Sling", "quantity": 1, "slots": 32},
                {"item": "Water rune", "quantity": 6, "slots": 48},
                {"item": "Body rune", "quantity": 7, "slots": 40},
                {"item": "Earth rune", "quantity": 4, "slots": 24},
                {"item": "Bronze bolts", "quantity": 8, "slots": 24},
                {"item": "Coins", "quantity": 5, "slots": 224},
                {"item": "Coins", "quantity": 9, "slots": 24},
                {"item": "Coins", "quantity": 15, "slots": 24},
                {"item": "Coins", "quantity": 20, "slots": 16},
                {"item": "Coins", "quantity": 1, "slots": 8},
                {"slots": 272},
                {"item": "Hammer", "quantity": 1, "slots": 120},
                {"item": "Goblin book", "quantity": 1, "slots": 16},
                {"item": "Goblin mail", "quantity": 1, "slots": 40},
                {"item": "Chef's hat", "quantity": 1, "slots": 24},
                {"item": "Beer", "quantity": 1, "slots": 16},
                {"item": "Brass necklace", "quantity": 1, "slots": 8},
                {"item": "Air talisman", "quantity": 1, "slots": 8},
            ),
        },
        {
            "name": "Charms",
            "total": 1024,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 82},
                {"item": "Green charm", "quantity": 1, "slots": 21},
                {"item": "Crimson charm", "quantity": 1, "slots": 9},
                {"item": "Blue charm", "quantity": 1, "slots": 1},
                {"slots": 911},
            ),
        },
        {
            "name": "Tertiary",
            "total": 1024,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 6},
                {"slots": 1018},
            ),
        },
    ),
}


GOBLIN_HIGHER_LEVEL_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Bronze spear", "quantity": 1, "slots": 9},
                {"item": "Bronze hatchet", "quantity": 1, "slots": 3},
                {"item": "Bronze scimitar", "quantity": 1, "slots": 1},
                {"item": "Bronze arrows", "quantity": 7, "slots": 3},
                {"item": "Mind rune", "quantity": 2, "slots": 3},
                {"item": "Earth rune", "quantity": 4, "slots": 3},
                {"item": "Body rune", "quantity": 2, "slots": 3},
                {"item": "Bronze javelin", "quantity": 5, "slots": 2},
                {"item": "Chaos rune", "quantity": 1, "slots": 1},
                {"item": "Nature rune", "quantity": 1, "slots": 1},
                {"item": "Coins", "quantity": 1, "slots": 34},
                {"item": "Coins", "quantity": 3, "slots": 13},
                {"item": "Coins", "quantity": 5, "slots": 8},
                {"item": "Coins", "quantity": 16, "slots": 7},
                {"item": "Coins", "quantity": 24, "slots": 3},
                {"item": "Hammer", "quantity": 1, "slots": 9},
                {"item": "Goblin book", "quantity": 1, "slots": 2},
                {"item": "Goblin mail", "quantity": 1, "slots": 10},
                {"item": "Grapes", "quantity": 1, "slots": 1},
                {"item": "Tin ore", "quantity": 1, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 2},
                {"slots": 8},
            ),
        },
        {
            "name": "Charms",
            "total": 1024,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 82},
                {"item": "Green charm", "quantity": 1, "slots": 21},
                {"item": "Crimson charm", "quantity": 1, "slots": 9},
                {"item": "Blue charm", "quantity": 1, "slots": 1},
                {"slots": 911},
            ),
        },
        {
            "name": "Tertiary",
            "total": 1024,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 6},
                {"slots": 1018},
            ),
        },
    ),
}


HOBGOBLIN_UNARMED_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 127,
            "slots": (
                {"item": "Bronze spear", "quantity": 1, "slots": 3},
                {"item": "Iron sword", "quantity": 1, "slots": 3},
                {"item": "Steel dagger", "quantity": 1, "slots": 3},
                {"item": "Iron spear", "quantity": 1, "slots": 2},
                {"item": "Steel spear", "quantity": 1, "slots": 2},
                {"item": "Steel longsword", "quantity": 1, "slots": 1},
                {"item": "Law rune", "quantity": 2, "slots": 3},
                {"item": "Water rune", "quantity": 2, "slots": 2},
                {"item": "Fire rune", "quantity": 7, "slots": 2},
                {"item": "Body rune", "quantity": 6, "slots": 2},
                {"item": "Chaos rune", "quantity": 3, "slots": 2},
                {"item": "Nature rune", "quantity": 4, "slots": 2},
                {"item": "Cosmic rune", "quantity": 2, "slots": 1},
                {"item": "Coins", "quantity": 15, "slots": 16},
                {"item": "Coins", "quantity": 28, "slots": 12},
                {"item": "Coins", "quantity": 5, "slots": 11},
                {"item": "Coins", "quantity": 62, "slots": 4},
                {"item": "Coins", "quantity": 42, "slots": 3},
                {"item": "Coins", "quantity": 1, "slots": 1},
                {"item": "Limpwurt root", "quantity": 1, "slots": 22},
                {"item": "Goblin mail", "quantity": 1, "slots": 2},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
                {"slots": 1},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 160},
                {"item": "Green charm", "quantity": 1, "slots": 6},
                {"item": "Crimson charm", "quantity": 1, "slots": 11},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 821},
            ),
        },
    ),
}


HOBGOBLIN_ARMED_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron sword", "quantity": 1, "slots": 3},
                {"item": "Steel dagger", "quantity": 1, "slots": 3},
                {"item": "Steel longsword", "quantity": 1, "slots": 1},
                {"item": "Law rune", "quantity": 2, "slots": 3},
                {"item": "Water rune", "quantity": 2, "slots": 2},
                {"item": "Fire rune", "quantity": 7, "slots": 2},
                {"item": "Body rune", "quantity": 6, "slots": 2},
                {"item": "Chaos rune", "quantity": 3, "slots": 2},
                {"item": "Nature rune", "quantity": 4, "slots": 2},
                {"item": "Cosmic rune", "quantity": 2, "slots": 2},
                {"item": "Iron javelin", "quantity": 5, "slots": 2},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_UNCOMMON_SEED_DROP_TABLE, "slots": 12},
                {"item": "Coins", "quantity": 15, "slots": 34},
                {"item": "Coins", "quantity": 5, "slots": 10},
                {"item": "Coins", "quantity": 28, "slots": 4},
                {"item": "Coins", "quantity": 62, "slots": 4},
                {"item": "Coins", "quantity": 42, "slots": 3},
                {"item": "Coins", "quantity": 1, "slots": 1},
                {"slots": 4},
                {"item": "Limpwurt root", "quantity": 1, "slots": 21},
                {"item": "Goblin mail", "quantity": 1, "slots": 2},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 150},
                {"item": "Green charm", "quantity": 1, "slots": 10},
                {"item": "Crimson charm", "quantity": 1, "slots": 10},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 828},
            ),
        },
    ),
}


TZHAAR_KET_DROPS = {
    "guaranteed": (),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Tokkul", "quantity_range": (100, 2000), "slots": 69},
                {"item": "Fire battlestaff", "quantity": 1, "slots": 1},
                {"item": "Super strength (1)", "quantity": 1, "slots": 4},
                {"item": "Super defence (1)", "quantity": 1, "slots": 4},
                {"item": "Uncut sapphire", "quantity": 1, "slots": 12},
                {"item": "Uncut emerald", "quantity": 1, "slots": 12},
                {"item": "Uncut ruby", "quantity": 1, "slots": 6},
                {"item": "Uncut diamond", "quantity": 1, "slots": 6},
                {"item": "Lobster", "quantity": 1, "slots": 6},
                {"item": "Chilli potato", "quantity": 1, "slots": 6},
                {"item": "Pure essence", "quantity_range": (5, 10), "slots": 1},
                {"item": "Onyx bolt tips", "quantity_range": (1, 4), "slots": 1},
            ),
        },
        {
            "name": "Obsidian",
            "total": 512,
            "slots": (
                {"item": "Tzhaar-ket-om", "quantity": 1, "slots": 1},
                {"item": "Toktz-ket-xil", "quantity": 1, "slots": 1},
                {"item": "Obsidian cape", "quantity": 1, "slots": 1},
                {"slots": 509},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Obsidian charm", "quantity": 2, "slots": 720},
                {"slots": 280},
            ),
        },
    ),
}


FARMER_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Earth rune", "quantity": 4, "slots": 2},
                {"item": "Fire rune", "quantity": 6, "slots": 2},
                {"item": "Mind rune", "quantity": 9, "slots": 2},
                {"item": "Chaos rune", "quantity": 2, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 11},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 27},
                {"item": "Coins", "quantity": 3, "slots": 38},
                {"item": "Coins", "quantity": 25, "slots": 1},
                {"item": "Fishing bait", "quantity": 1, "slots": 5},
                {"item": "Rake", "quantity": 1, "slots": 3},
                {"item": "Earth talisman", "quantity": 1, "slots": 2},
                {"item": "Gardening boots", "quantity": 1, "slots": 2},
                {"item": "Seed dibber", "quantity": 1, "slots": 2},
                {"item": "Secateurs", "quantity": 1, "slots": 1},
                {"item": "Watering can (8)", "quantity": 1, "slots": 1},
                {"slots": 28},
            ),
        },
        {
            "name": "Tertiary",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


CHAOS_DRUID_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Law rune", "quantity": 2, "slots": 7},
                {"item": "Mithril bolts", "quantity_range": (2, 12), "slots": 5},
                {"item": "Air rune", "quantity": 36, "slots": 3},
                {"item": "Body rune", "quantity": 9, "slots": 2},
                {"item": "Earth rune", "quantity": 9, "slots": 2},
                {"item": "Mind rune", "quantity": 12, "slots": 2},
                {"item": "Nature rune", "quantity": 3, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 46},
                {"item": "Coins", "quantity": 3, "slots": 5},
                {"item": "Coins", "quantity": 8, "slots": 5},
                {"item": "Coins", "quantity": 29, "slots": 3},
                {"item": "Coins", "quantity": 35, "slots": 1},
                {"slots": 33},
                {"item": "Vial of water", "quantity": 1, "slots": 10},
                {"item": "Bronze longsword", "quantity": 1, "slots": 1},
                {"item": "Snape grass", "quantity": 1, "slots": 1},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 1},
            ),
        },
    ),
}


WHITE_KNIGHT_LEVEL_36_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron longsword", "quantity": 1, "slots": 2},
                {"item": "Steel sword", "quantity": 1, "slots": 1},
                {"item": "Steel med helm", "quantity": 1, "slots": 1},
                {"item": "Mind rune", "quantity": 5, "slots": 11},
                {"item": "Nature rune", "quantity": 4, "slots": 4},
                {"item": "Body rune", "quantity_range": (9, 13), "slots": 3},
                {"item": "Chaos rune", "quantity": 2, "slots": 3},
                {"item": "Water rune", "quantity_range": (25, 30), "slots": 3},
                {"item": "Mithril arrows", "quantity": 5, "slots": 2},
                {"item": "Adamant arrows", "quantity": 2, "slots": 1},
                {"item": "Blood rune", "quantity": 2, "slots": 1},
                {"item": "Law rune", "quantity": 2, "slots": 1},
                {"item": "Coins", "quantity": 48, "slots": 15},
                {"item": "Coins", "quantity": 15, "slots": 15},
                {"item": "Coins", "quantity": 8, "slots": 10},
                {"item": "Coins", "quantity_range": (45, 53), "slots": 10},
                {"item": "Coins", "quantity": 1, "slots": 5},
                {"item": "Coins", "quantity": 2, "slots": 5},
                {"item": "Coins", "quantity": 120, "slots": 1},
                {"item": "Iron bar", "quantity": 2, "slots": 6},
                {"item": "Iron bar", "quantity": 1, "slots": 2},
                {"item": "Half an apple pie", "quantity": 1, "slots": 1},
                {"item": "Iron ore", "quantity": 1, "slots": 1},
                {"item": "Pot of flour", "quantity": 1, "slots": 1},
                {"slots": 2},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 5},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 15},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 1},
            ),
        },
        {
            "name": "Tertiary",
            "total": 1024,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8},
                {"slots": 1016},
            ),
        },
    ),
}


WHITE_KNIGHT_LEVEL_38_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 130,
            "slots": (
                {"item": "Iron longsword", "quantity": 1, "slots": 2},
                {"item": "Steel sword", "quantity": 1, "slots": 1},
                {"item": "Steel med helm", "quantity": 1, "slots": 2},
                {"item": "Mind rune", "quantity": 5, "slots": 8},
                {"item": "Nature rune", "quantity": 4, "slots": 4},
                {"item": "Body rune", "quantity_range": (10, 14), "slots": 3},
                {"item": "Chaos rune", "quantity": 3, "slots": 3},
                {"item": "Water rune", "quantity_range": (30, 35), "slots": 3},
                {"item": "Mithril arrows", "quantity": 5, "slots": 2},
                {"item": "Adamant arrows", "quantity": 2, "slots": 3},
                {"item": "Blood rune", "quantity": 2, "slots": 1},
                {"item": "Law rune", "quantity": 3, "slots": 1},
                {"item": "Coins", "quantity": 15, "slots": 13},
                {"item": "Coins", "quantity": 10, "slots": 15},
                {"item": "Coins", "quantity": 54, "slots": 10},
                {"item": "Coins", "quantity_range": (50, 58), "slots": 10},
                {"item": "Coins", "quantity": 3, "slots": 6},
                {"item": "Coins", "quantity": 1, "slots": 1},
                {"item": "Coins", "quantity": 120, "slots": 1},
                {"item": "Iron bar", "quantity": 2, "slots": 8},
                {"item": "Iron bar", "quantity": 1, "slots": 2},
                {"item": "Half an apple pie", "quantity": 1, "slots": 1},
                {"item": "Iron ore", "quantity": 1, "slots": 1},
                {"item": "Pot of flour", "quantity": 1, "slots": 1},
                {"slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
            ),
        },
        {
            "name": "Tertiary",
            "total": 1024,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8},
                {"slots": 1016},
            ),
        },
    ),
}


WHITE_KNIGHT_LEVEL_39_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 127,
            "slots": (
                {"item": "Iron longsword", "quantity": 1, "slots": 2},
                {"item": "Steel sword", "quantity": 1, "slots": 2},
                {"item": "Steel med helm", "quantity": 1, "slots": 2},
                {"item": "Mind rune", "quantity": 10, "slots": 8},
                {"item": "Nature rune", "quantity": 6, "slots": 4},
                {"item": "Body rune", "quantity_range": (15, 19), "slots": 3},
                {"item": "Chaos rune", "quantity": 4, "slots": 3},
                {"item": "Water rune", "quantity_range": (35, 40), "slots": 3},
                {"item": "Mithril arrows", "quantity": 7, "slots": 5},
                {"item": "Adamant arrows", "quantity": 4, "slots": 3},
                {"item": "Blood rune", "quantity": 3, "slots": 1},
                {"item": "Law rune", "quantity": 3, "slots": 1},
                {"item": "Coins", "quantity_range": (15, 19), "slots": 13},
                {"item": "Coins", "quantity": 15, "slots": 10},
                {"item": "Coins", "quantity_range": (55, 63), "slots": 10},
                {"item": "Coins", "quantity_range": (50, 69), "slots": 10},
                {"item": "Coins", "quantity": 5, "slots": 6},
                {"item": "Coins", "quantity": 120, "slots": 2},
                {"item": "Coins", "quantity": 1, "slots": 1},
                {"item": "Iron bar", "quantity": 2, "slots": 6},
                {"item": "Iron bar", "quantity": 1, "slots": 2},
                {"item": "Half an apple pie", "quantity": 1, "slots": 1},
                {"item": "Iron ore", "quantity": 1, "slots": 1},
                {"item": "Pot of flour", "quantity": 1, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
            ),
        },
        {
            "name": "Tertiary",
            "total": 1024,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8},
                {"slots": 1016},
            ),
        },
    ),
}


WHITE_KNIGHT_LEVEL_42_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 127,
            "slots": (
                {"item": "Iron longsword", "quantity": 1, "slots": 2},
                {"item": "Steel sword", "quantity": 1, "slots": 2},
                {"item": "Steel med helm", "quantity": 1, "slots": 2},
                {"item": "Mind rune", "quantity": 12, "slots": 3},
                {"item": "Nature rune", "quantity": 7, "slots": 4},
                {"item": "Body rune", "quantity_range": (15, 24), "slots": 3},
                {"item": "Chaos rune", "quantity": 5, "slots": 3},
                {"item": "Water rune", "quantity_range": (40, 47), "slots": 3},
                {"item": "Mithril arrows", "quantity": 9, "slots": 5},
                {"item": "Adamant arrows", "quantity": 5, "slots": 3},
                {"item": "Blood rune", "quantity": 3, "slots": 1},
                {"item": "Law rune", "quantity": 3, "slots": 1},
                {"item": "Coins", "quantity_range": (51, 55), "slots": 13},
                {"item": "Coins", "quantity": 15, "slots": 10},
                {"item": "Coins", "quantity_range": (65, 73), "slots": 10},
                {"item": "Coins", "quantity": 8, "slots": 6},
                {"item": "Coins", "quantity_range": (50, 69), "slots": 5},
                {"item": "Coins", "quantity": 120, "slots": 3},
                {"item": "Coins", "quantity": 1, "slots": 1},
                {"item": "Iron bar", "quantity": 2, "slots": 5},
                {"item": "Iron bar", "quantity": 1, "slots": 2},
                {"item": "Half an apple pie", "quantity": 1, "slots": 1},
                {"item": "Iron ore", "quantity": 1, "slots": 1},
                {"item": "Pot of flour", "quantity": 1, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 28},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
            ),
        },
        {
            "name": "Tertiary",
            "total": 1024,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8},
                {"slots": 1016},
            ),
        },
    ),
}


OUTLAW_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 127,
            "slots": (
                {"item": "Bronze med helm", "quantity": 1, "slots": 2},
                {"item": "Mind rune", "quantity": 9, "slots": 2},
                {"item": "Water rune", "quantity": 6, "slots": 2},
                {"item": "Earth rune", "quantity": 5, "slots": 2},
                {"item": "Coins", "quantity": 5, "slots": 12},
                {"item": "Coins", "quantity": 15, "slots": 4},
                {"item": "Coins", "quantity": 25, "slots": 1},
                {"item": "Rope", "quantity": 1, "slots": 46},
                {"item": "Fishing bait", "quantity": 1, "slots": 15},
                {"item": "Cabbage", "quantity": 1, "slots": 6},
                {"item": "Copper ore", "quantity": 1, "slots": 2},
                {"item": "Knife", "quantity": 1, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 32},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 360},
                {"item": "Green charm", "quantity": 1, "slots": 30},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 7},
                {"slots": 573},
            ),
        },
    ),
}


CHAOS_DWARF_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Steel full helm", "quantity": 1, "slots": 2},
                {"item": "Mithril longsword", "quantity": 1, "slots": 1},
                {"item": "Mithril sq shield", "quantity": 1, "slots": 1},
                {"item": "Law rune", "quantity": 3, "slots": 4},
                {"item": "Air rune", "quantity": 24, "slots": 3},
                {"item": "Chaos rune", "quantity": 10, "slots": 3},
                {"item": "Mind rune", "quantity": 37, "slots": 3},
                {"item": "Nature rune", "quantity": 9, "slots": 3},
                {"item": "Cosmic rune", "quantity": 3, "slots": 2},
                {"item": "Death rune", "quantity": 3, "slots": 1},
                {"item": "Water rune", "quantity": 10, "slots": 1},
                {"item": "Coins", "quantity": 92, "slots": 40},
                {"item": "Coins", "quantity": 47, "slots": 18},
                {"item": "Coins", "quantity": 25, "slots": 11},
                {"item": "Coins", "quantity": 150, "slots": 10},
                {"item": "Coins", "quantity": 350, "slots": 2},
                {"item": "Coins", "quantity": 15, "slots": 2},
                {"slots": 5},
                {"item": "Coal", "quantity": 1, "slots": 1},
                {"item": "Muddy key", "quantity": 1, "slots": 7},
                {"item": "Cheese", "quantity": 1, "slots": 1},
                {"item": "Mithril bar", "quantity": 1, "slots": 6},
                {"item": "Tomato", "quantity": 1, "slots": 1},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 100},
                {"item": "Green charm", "quantity": 1, "slots": 50},
                {"item": "Crimson charm", "quantity": 1, "slots": 20},
                {"item": "Blue charm", "quantity": 1, "slots": 20},
                {"slots": 810},
            ),
        },
    ),
}


HAAKON_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Iron hatchet", "quantity": 1, "slots": 48},
                {"item": "Bronze battleaxe", "quantity": 1, "slots": 32},
                {"item": "Iron mace", "quantity": 1, "slots": 8},
                {"item": "Chaos rune", "quantity": 3, "slots": 32},
                {"item": "Bronze arrows", "quantity": 10, "slots": 24},
                {"item": "Earth rune", "quantity": 5, "slots": 24},
                {"item": "Iron arrows", "quantity": 8, "slots": 24},
                {"item": "Fire rune", "quantity": 8, "slots": 16},
                {"item": "Mind rune", "quantity": 10, "slots": 16},
                {"item": "Law rune", "quantity": 2, "slots": 8},
                {"item": "Coins", "quantity": 8, "slots": 317},
                {"item": "Coins", "quantity": 12, "slots": 76},
                {"item": "Coins", "quantity": 25, "slots": 45},
                {"item": "Coins", "quantity": 32, "slots": 26},
                {"slots": 288},
                {"item": "Tin ore", "quantity": 1, "slots": 8},
                {"item": "Bear fur", "quantity": 1, "slots": 8},
                {"item": "Beer", "quantity": 1, "slots": 8},
                {"item": "Cooked meat", "quantity": 1, "slots": 8},
                {"item": "Ring mould", "quantity": 1, "slots": 8},
            ),
        },
        {
            "name": "Tertiary",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


HAM_GUARD_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 648,
            "slots": (
                {"item": "Bronze hatchet", "quantity": 1, "slots": 18},
                {"item": "Bronze dagger", "quantity": 1, "slots": 18},
                {"item": "Bronze pickaxe", "quantity": 1, "slots": 18},
                {"item": "Iron hatchet", "quantity": 1, "slots": 18},
                {"item": "Iron dagger", "quantity": 1, "slots": 18},
                {"item": "Iron pickaxe", "quantity": 1, "slots": 18},
                {"item": "Leather body", "quantity": 1, "slots": 18},
                {"item": "Steel hatchet", "quantity": 1, "slots": 12},
                {"item": "Steel dagger", "quantity": 1, "slots": 12},
                {"item": "Steel pickaxe", "quantity": 1, "slots": 12},
                {"item": "H.A.M. boots", "quantity": 1, "slots": 12},
                {"item": "H.A.M. cloak", "quantity": 1, "slots": 6},
                {"item": "H.A.M. gloves", "quantity": 1, "slots": 15},
                {"item": "H.A.M. hood", "quantity": 1, "slots": 6},
                {"item": "H.A.M. logo", "quantity": 1, "slots": 8},
                {"item": "H.A.M. robe", "quantity": 1, "slots": 8},
                {"item": "H.A.M. shirt", "quantity": 1, "slots": 8},
                {"item": "Bronze arrows", "quantity_range": (1, 12), "slots": 16},
                {"item": "Steel arrows", "quantity_range": (1, 10), "slots": 12},
                {"item": "Grimy guam", "quantity": 1, "slots": 6},
                {"item": "Grimy marrentill", "quantity": 1, "slots": 3},
                {"item": "Grimy tarromin", "quantity": 1, "slots": 2},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 57},
                {"item": "Cowhide", "quantity_range": (1, 3), "slots": 18},
                {"item": "Logs", "quantity_range": (1, 3), "slots": 18},
                {"item": "Raw anchovies", "quantity_range": (1, 3), "slots": 12},
                {"item": "Raw chicken", "quantity_range": (1, 3), "slots": 12},
                {"item": "Uncut opal", "quantity": 1, "slots": 12},
                {"item": "Uncut jade", "quantity": 1, "slots": 12},
                {"item": "Iron ore", "quantity": 1, "slots": 12},
                {"item": "Coal", "quantity": 1, "slots": 12},
                {"item": "Coins", "quantity_range": (1, 20), "slots": 81},
                {"item": "Buttons", "quantity": 1, "slots": 24},
                {"item": "Damaged armour", "quantity": 1, "slots": 24},
                {"item": "Rusty sword", "quantity": 1, "slots": 24},
                {"item": "Knife", "quantity": 1, "slots": 12},
                {"item": "Needle", "quantity": 1, "slots": 12},
                {"item": "Tinderbox", "quantity": 1, "slots": 12},
                {"item": "Feather", "quantity_range": (1, 6), "slots": 18},
                {"item": "Thread", "quantity_range": (1, 10), "slots": 12},
            ),
        },
        {
            "name": "Tertiary",
            "total": 55,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                {"slots": 54},
            ),
        },
    ),
}


IMP_DROPS = {
    "guaranteed": (("Impious ashes", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Black bead", "quantity": 1, "slots": 40},
                {"item": "Red bead", "quantity": 1, "slots": 40},
                {"item": "White bead", "quantity": 1, "slots": 40},
                {"item": "Yellow bead", "quantity": 1, "slots": 40},
                {"item": "Bronze bolts", "quantity": 1, "slots": 64},
                {"item": "Wizard hat", "quantity": 1, "slots": 64},
                {"item": "Egg", "quantity": 1, "slots": 47},
                {"item": "Raw chicken", "quantity": 1, "slots": 47},
                {"item": "Burnt bread", "quantity": 1, "slots": 39},
                {"item": "Burnt meat", "quantity": 1, "slots": 39},
                {"item": "Cabbage", "quantity": 1, "slots": 16},
                {"item": "Bread dough", "quantity": 1, "slots": 16},
                {"item": "Bread", "quantity": 1, "slots": 8},
                {"item": "Cooked meat", "quantity": 1, "slots": 8},
                {"item": "Hammer", "quantity": 1, "slots": 47},
                {"item": "Tinderbox", "quantity": 1, "slots": 64},
                {"item": "Shears", "quantity": 1, "slots": 39},
                {"item": "Bucket", "quantity": 1, "slots": 32},
                {"item": "Bucket of water", "quantity": 1, "slots": 16},
                {"item": "Jug", "quantity": 1, "slots": 16},
                {"item": "Jug of water", "quantity": 1, "slots": 16},
                {"item": "Empty pot", "quantity": 1, "slots": 16},
                {"item": "Pot of flour", "quantity": 1, "slots": 16},
                {"item": "Ball of wool", "quantity": 1, "slots": 47},
                {"item": "Mind talisman", "quantity": 1, "slots": 55},
                {"item": "Ashes", "quantity": 1, "slots": 48},
                {"item": "Clay", "quantity": 1, "slots": 32},
                {"item": "Cadava berries", "quantity": 1, "slots": 32},
                {"item": "Grain", "quantity": 1, "slots": 24},
                {"item": "Chef's hat", "quantity": 1, "slots": 16},
            ),
        },
    ),
}


LOW_LEVEL_HUMANOID_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Bronze med helm", "quantity": 1, "slots": 16},
                {"item": "Bronze dagger", "quantity": 1, "slots": 8},
                {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 138},
                {"item": "Sling", "quantity": 1, "slots": 16},
                {"item": "Bronze arrows", "quantity": 7, "slots": 24},
                {"item": "Earth rune", "quantity": 4, "slots": 16},
                {"item": "Fire rune", "quantity": 6, "slots": 16},
                {"item": "Mind rune", "quantity": 9, "slots": 16},
                {"item": "Chaos rune", "quantity": 2, "slots": 8},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 152},
                {"item": "Coins", "quantity": 3, "slots": 277},
                {"item": "Coins", "quantity": 10, "slots": 138},
                {"item": "Coins", "quantity": 5, "slots": 73},
                {"item": "Coins", "quantity": 15, "slots": 32},
                {"item": "Coins", "quantity": 25, "slots": 8},
                {"slots": 16},
                {"item": "Fishing bait", "quantity": 1, "slots": 30},
                {"item": "Copper ore", "quantity": 1, "slots": 16},
                {"item": "Earth talisman", "quantity": 1, "slots": 16},
                {"item": "Cabbage", "quantity": 1, "slots": 8},
            ),
        },
        {
            "name": "Tertiary",
            "total": 1024,
            "slots": (
                {"slots": 1016},
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8},
            ),
        },
    ),
}


PIRATE_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Iron dagger", "quantity": 1, "slots": 48},
                {"item": "Bronze scimitar", "quantity": 1, "slots": 32},
                {"item": "Iron platebody", "quantity": 1, "slots": 8},
                {"item": "Iron bolts", "quantity_range": (2, 12), "slots": 80},
                {"item": "Chaos rune", "quantity": 2, "slots": 48},
                {"item": "Nature rune", "quantity": 2, "slots": 40},
                {"item": "Bronze arrows", "quantity": 9, "slots": 24},
                {"item": "Bronze arrows", "quantity": 12, "slots": 16},
                {"item": "Air rune", "quantity": 10, "slots": 16},
                {"item": "Earth rune", "quantity": 9, "slots": 16},
                {"item": "Fire rune", "quantity": 5, "slots": 16},
                {"item": "Law rune", "quantity": 2, "slots": 8},
                {"item": "Coins", "quantity": 4, "slots": 232},
                {"item": "Coins", "quantity": 25, "slots": 104},
                {"item": "Coins", "quantity": 7, "slots": 64},
                {"item": "Coins", "quantity": 12, "slots": 48},
                {"item": "Coins", "quantity": 35, "slots": 32},
                {"item": "Coins", "quantity": 55, "slots": 8},
                {"item": "Eye patch", "quantity": 1, "slots": 96},
                {"slots": 64},
                {"item": "Chef's hat", "quantity": 1, "slots": 8},
                {"item": "Iron bar", "quantity": 1, "slots": 8},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 8},
            ),
        },
    ),
}


MONK_OF_ZAMORAK_LEVEL_45_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 20,
            "slots": (
                {"item": "Zamorak robe top", "quantity": 1, "slots": 1},
                {"item": "Zamorak robe bottom", "quantity": 1, "slots": 1},
                {"slots": 18},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 10},
                {"item": "Green charm", "quantity": 1, "slots": 100},
                {"item": "Crimson charm", "quantity": 1, "slots": 20},
                {"item": "Blue charm", "quantity": 1, "slots": 10},
                {"slots": 860},
            ),
        },
    ),
}


GIANT_RAT_DROPS = {"guaranteed": (("Bones", 1), ("Raw rat meat", 1)), "tables": ()}


DUCK_LAND_DROPS = {"guaranteed": (("Bones", 1),), "tables": ()}
DUCK_WATER_DROPS = {"guaranteed": (), "tables": ()}


UNICORN_DROPS = {
    "guaranteed": (("Bones", 1), ("Unicorn horn", 1)),
    "tables": (
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 130},
                {"item": "Green charm", "quantity": 1, "slots": 60},
                {"item": "Crimson charm", "quantity": 1, "slots": 40},
                {"item": "Blue charm", "quantity": 1, "slots": 5},
                {"slots": 765},
            ),
        },
    ),
}


BLACK_BEAR_DROPS = {
    "guaranteed": (("Bones", 1), ("Bear fur", 1), ("Raw bear meat", 1)),
    "tables": (
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 180},
                {"item": "Green charm", "quantity": 1, "slots": 8},
                {"item": "Crimson charm", "quantity": 1, "slots": 11},
                {"item": "Blue charm", "quantity": 1, "slots": 5},
                {"slots": 796},
            ),
        },
    ),
}


WOLF_LEVEL_11_DROPS = {
    "guaranteed": (("Wolf bones", 1), ("Bones", 1)),
    "tables": (
        {
            "name": "Main",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 20},
                {"item": "Green charm", "quantity": 1, "slots": 30},
                {"item": "Crimson charm", "quantity": 1, "slots": 50},
                {"item": "Blue charm", "quantity": 1, "slots": 10},
                {"slots": 890},
            ),
        },
    ),
}


WHITE_WOLF_DROPS = {
    "guaranteed": (("Wolf bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 110},
                {"item": "Green charm", "quantity": 1, "slots": 50},
                {"item": "Crimson charm", "quantity": 1, "slots": 140},
                {"item": "Blue charm", "quantity": 1, "slots": 80},
                {"slots": 620},
            ),
        },
    ),
}


GIANT_BAT_DROPS = {"guaranteed": (("Bat bones", 1),), "tables": ()}


SCORPION_CHARM_DROPS = {
    "guaranteed": (),
    "tables": (
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 30},
                {"item": "Green charm", "quantity": 1, "slots": 70},
                {"item": "Crimson charm", "quantity": 1, "slots": 10},
                {"item": "Blue charm", "quantity": 1, "slots": 5},
                {"slots": 885},
            ),
        },
    ),
}


HILL_GIANT_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron full helm", "quantity": 1, "slots": 4},
                {"item": "Iron dagger", "quantity": 1, "slots": 5},
                {"item": "Iron kiteshield", "quantity": 1, "slots": 3},
                {"item": "Steel longsword", "quantity": 1, "slots": 2},
                {"item": "Iron arrows", "quantity": 3, "slots": 6},
                {"item": "Fire rune", "quantity": 15, "slots": 3},
                {"item": "Water rune", "quantity": 7, "slots": 3},
                {"item": "Law rune", "quantity": 2, "slots": 3},
                {"item": "Steel arrows", "quantity": 10, "slots": 2},
                {"item": "Mind rune", "quantity": 3, "slots": 2},
                {"item": "Cosmic rune", "quantity": 2, "slots": 2},
                {"item": "Nature rune", "quantity": 6, "slots": 2},
                {"item": "Chaos rune", "quantity": 2, "slots": 1},
                {"item": "Death rune", "quantity": 2, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                {"item": "Coins", "quantity": 38, "slots": 15},
                {"item": "Coins", "quantity": 52, "slots": 10},
                {"item": "Coins", "quantity": 15, "slots": 8},
                {"item": "Coins", "quantity": 7, "slots": 6},
                {"item": "Coins", "quantity": 88, "slots": 2},
                {"slots": 1},
                {"item": "Limpwurt root", "quantity": 1, "slots": 11},
                {"item": "Beer", "quantity": 1, "slots": 6},
                {"item": "Body talisman", "quantity": 1, "slots": 2},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 3},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 150},
                {"item": "Green charm", "quantity": 1, "slots": 10},
                {"item": "Crimson charm", "quantity": 1, "slots": 10},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 828},
            ),
        },
    ),
}


MOSS_GIANT_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Black sq shield", "quantity": 1, "slots": 5},
                {"item": "Magic staff", "quantity": 1, "slots": 2},
                {"item": "Steel med helm", "quantity": 1, "slots": 2},
                {"item": "Mithril sword", "quantity": 1, "slots": 2},
                {"item": "Mithril spear", "quantity": 1, "slots": 2},
                {"item": "Steel kiteshield", "quantity": 1, "slots": 1},
                {"item": "Law rune", "quantity": 3, "slots": 4},
                {"item": "Air rune", "quantity": 18, "slots": 3},
                {"item": "Earth rune", "quantity": 27, "slots": 3},
                {"item": "Chaos rune", "quantity": 7, "slots": 3},
                {"item": "Nature rune", "quantity": 6, "slots": 3},
                {"item": "Cosmic rune", "quantity": 3, "slots": 2},
                {"item": "Iron arrows", "quantity": 15, "slots": 2},
                {"item": "Steel arrows", "quantity": 30, "slots": 1},
                {"item": "Death rune", "quantity": 3, "slots": 1},
                {"item": "Blood rune", "quantity": 1, "slots": 1},
                {"item": "Coins", "quantity": 37, "slots": 19},
                {"item": "Coins", "quantity": 2, "slots": 8},
                {"item": "Coins", "quantity": 119, "slots": 10},
                {"item": "Coins", "quantity": 300, "slots": 2},
                {"item": "Steel bar", "quantity": 1, "slots": 6},
                {"item": "Coal", "quantity": 1, "slots": 1},
                {"item": "Spinach roll", "quantity": 1, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 5},
                {"table": COMBAT_UNCOMMON_SEED_DROP_TABLE, "slots": 35},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 4},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 360},
                {"item": "Green charm", "quantity": 1, "slots": 30},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 7},
                {"slots": 573},
            ),
        },
    ),
}


ICE_GIANT_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Iron 2h sword", "quantity": 1, "slots": 40},
                {"item": "Black kiteshield", "quantity": 1, "slots": 32},
                {"item": "Steel hatchet", "quantity": 1, "slots": 32},
                {"item": "Steel sword", "quantity": 1, "slots": 32},
                {"item": "Iron platelegs", "quantity": 1, "slots": 8},
                {"item": "Mithril mace", "quantity": 1, "slots": 8},
                {"item": "Mithril sq shield", "quantity": 1, "slots": 8},
                {"item": "Adamant arrows", "quantity": 5, "slots": 48},
                {"item": "Nature rune", "quantity": 6, "slots": 32},
                {"item": "Mind rune", "quantity": 24, "slots": 24},
                {"item": "Body rune", "quantity": 37, "slots": 24},
                {"item": "Law rune", "quantity": 3, "slots": 16},
                {"item": "Water rune", "quantity": 12, "slots": 8},
                {"item": "Cosmic rune", "quantity": 4, "slots": 8},
                {"item": "Death rune", "quantity": 3, "slots": 8},
                {"item": "Blood rune", "quantity": 2, "slots": 8},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 64},
                {"item": "Coins", "quantity": 117, "slots": 224},
                {"item": "Coins", "quantity": 53, "slots": 76},
                {"item": "Coins", "quantity": 196, "slots": 72},
                {"item": "Coins", "quantity": 5, "slots": 64},
                {"item": "Coins", "quantity": 8, "slots": 54},
                {"item": "Coins", "quantity": 2, "slots": 48},
                {"item": "Coins", "quantity": 400, "slots": 16},
                {"item": "Jug of wine", "quantity": 1, "slots": 24},
                {"item": "Mithril ore", "quantity": 1, "slots": 8},
                {"item": "Banana", "quantity": 1, "slots": 8},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 32},
            ),
        },
        {
            "name": "Tertiary",
            "total": 100000,
            "slots": (
                {"item": "Long bone", "quantity": 1, "slots": 250},
                {"item": "Curved bone", "quantity": 1, "slots": 20},
                {"item": "Champion's scroll", "quantity": 1, "slots": 20},
                {"slots": 99710},
            ),
        },
    ),
}

OGRE_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"table": COMBAT_OGRE_SEED_DROP_TABLE, "slots": 19},
                {"slots": 109},
            ),
        },
        {
            "name": "Tertiary",
            "total": 100000,
            "slots": (
                {"item": "Long bone", "quantity": 1, "slots": 250},
                {"item": "Curved bone", "quantity": 1, "slots": 20},
                {"slots": 99730},
            ),
        },
    ),
}

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

SHADOW_WARRIOR_DROPS = {
    "guaranteed": (),
    "tables": (
        {
            "name": "Darkan main",
            "total": 128,
            "slots": tuple(
                {"item": item_name, "quantity": quantity, "slots": chance}
                for item_name, quantity, chance in (
                    ("Coins", 8, 47),
                    ("Cosmic rune", 3, 9),
                    ("Blood rune", 2, 6),
                    ("Air rune", 45, 4),
                    ("Death rune", 2, 4),
                    ("Mithril bar", 1, 4),
                    ("Adamant spear", 1, 1),
                    ("Black dagger (p)", 1, 1),
                    ("Black knife", 1, 1),
                    ("Black longsword", 1, 1),
                    ("Black robe", 1, 1),
                    ("Weapon poison", 1, 1),
                )
            )
            + (
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 18},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 8},
                {"slots": 22},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 606,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 26},
                {"item": "Green charm", "quantity": 1, "slots": 11},
                {"item": "Crimson charm", "quantity": 1, "slots": 44},
                {"item": "Blue charm", "quantity": 1, "slots": 3},
                {"slots": 522},
            ),
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


GHOST_DROPS = {"guaranteed": (), "tables": ()}


ZOMBIE_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron hatchet", "quantity": 1, "slots": 3},
                {"item": "Bronze longsword", "quantity": 1, "slots": 1},
                {"item": "Bronze med helm", "quantity": 1, "slots": 4},
                {"item": "Bronze kiteshield", "quantity": 1, "slots": 3},
                {"item": "Iron arrows", "quantity": 5, "slots": 7},
                {"item": "Body rune", "quantity": 6, "slots": 5},
                {"item": "Mind rune", "quantity": 5, "slots": 5},
                {"item": "Air rune", "quantity": 13, "slots": 4},
                {"item": "Iron arrows", "quantity": 8, "slots": 4},
                {"item": "Steel arrows", "quantity": 6, "slots": 2},
                {"item": "Nature rune", "quantity": 6, "slots": 1},
                {"item": "Cosmic rune", "quantity": 4, "slots": 1},
                {"item": "Fire rune", "quantity": 7, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 25},
                {"item": "Coins", "quantity": 10, "slots": 36},
                {"item": "Coins", "quantity": 4, "slots": 4},
                {"item": "Coins", "quantity": 18, "slots": 3},
                {"item": "Coins", "quantity": 13, "slots": 2},
                {"item": "Coins", "quantity": 28, "slots": 2},
                {"slots": 8},
                {"item": "Fishing bait", "quantity": 5, "slots": 5},
                {"item": "Copper ore", "quantity": 1, "slots": 2},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 30},
                {"item": "Green charm", "quantity": 1, "slots": 17},
                {"item": "Crimson charm", "quantity": 1, "slots": 14},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 937},
            ),
        },
    ),
}


ZOMBIE_LEVEL_25_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron hatchet", "quantity": 1, "slots": 5},
                {"item": "Bronze longsword", "quantity": 1, "slots": 1},
                {"item": "Bronze med helm", "quantity": 1, "slots": 4},
                {"item": "Bronze kiteshield", "quantity": 1, "slots": 3},
                {"item": "Iron arrows", "quantity": 5, "slots": 7},
                {"item": "Body rune", "quantity": 6, "slots": 5},
                {"item": "Mind rune", "quantity": 5, "slots": 5},
                {"item": "Air rune", "quantity": 13, "slots": 4},
                {"item": "Iron arrows", "quantity": 8, "slots": 4},
                {"item": "Steel arrows", "quantity": 6, "slots": 2},
                {"item": "Nature rune", "quantity": 6, "slots": 1},
                {"item": "Cosmic rune", "quantity": 4, "slots": 1},
                {"item": "Fire rune", "quantity": 7, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 25},
                {"item": "Coins", "quantity": 10, "slots": 36},
                {"item": "Coins", "quantity": 4, "slots": 4},
                {"item": "Coins", "quantity": 18, "slots": 3},
                {"item": "Coins", "quantity": 13, "slots": 2},
                {"item": "Coins", "quantity": 28, "slots": 2},
                {"slots": 6},
                {"item": "Fishing bait", "quantity": 5, "slots": 5},
                {"item": "Copper ore", "quantity": 1, "slots": 2},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 30},
                {"item": "Green charm", "quantity": 1, "slots": 17},
                {"item": "Crimson charm", "quantity": 1, "slots": 14},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 937},
            ),
        },
    ),
}


SKELETON_LOW_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Bronze arrows", "quantity": 2, "slots": 56},
                {"item": "Bronze arrows", "quantity": 5, "slots": 32},
                {"item": "Iron arrows", "quantity": 1, "slots": 32},
                {"item": "Steel arrows", "quantity": 1, "slots": 8},
                {"item": "Air rune", "quantity": 15, "slots": 16},
                {"item": "Earth rune", "quantity": 3, "slots": 16},
                {"item": "Fire rune", "quantity": 2, "slots": 16},
                {"item": "Chaos rune", "quantity": 3, "slots": 16},
                {"item": "Nature rune", "quantity": 3, "slots": 16},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 49},
                {"item": "Coins", "quantity": 2, "slots": 175},
                {"item": "Coins", "quantity": 12, "slots": 200},
                {"item": "Coins", "quantity": 4, "slots": 56},
                {"item": "Coins", "quantity": 16, "slots": 32},
                {"item": "Coins", "quantity": 25, "slots": 32},
                {"item": "Coins", "quantity": 33, "slots": 32},
                {"item": "Coins", "quantity": 48, "slots": 8},
                {"slots": 144},
                {"item": "Iron dagger", "quantity": 1, "slots": 48},
                {"item": "Fire talisman", "quantity": 1, "slots": 16},
                {"item": "Iron ore", "quantity": 1, "slots": 8},
                {"item": "Grain", "quantity": 1, "slots": 8},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 8},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 50},
                {"item": "Green charm", "quantity": 1, "slots": 12},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 14},
                {"slots": 894},
            ),
        },
    ),
}


SKELETON_HIGH_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron med helm", "quantity": 1, "slots": 6},
                {"item": "Iron sword", "quantity": 1, "slots": 4},
                {"item": "Iron hatchet", "quantity": 1, "slots": 2},
                {"item": "Iron scimitar", "quantity": 1, "slots": 1},
                {"item": "Air rune", "quantity": 15, "slots": 3},
                {"item": "Water rune", "quantity": 9, "slots": 3},
                {"item": "Chaos rune", "quantity": 5, "slots": 3},
                {"item": "Iron arrows", "quantity": 12, "slots": 2},
                {"item": "Law rune", "quantity": 2, "slots": 2},
                {"item": "Cosmic rune", "quantity": 2, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 20},
                {"item": "Coins", "quantity": 10, "slots": 24},
                {"item": "Coins", "quantity": 5, "slots": 25},
                {"item": "Coins", "quantity": 25, "slots": 8},
                {"item": "Coins", "quantity": 45, "slots": 4},
                {"item": "Coins", "quantity": 65, "slots": 3},
                {"item": "Coins", "quantity": 1, "slots": 2},
                {"slots": 8},
                {"item": "Bronze bar", "quantity": 1, "slots": 5},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 50},
                {"item": "Green charm", "quantity": 1, "slots": 12},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 14},
                {"slots": 894},
            ),
        },
    ),
}


DWARF_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Bronze pickaxe", "quantity": 1, "slots": 13},
                {"item": "Bronze med helm", "quantity": 1, "slots": 4},
                {"item": "Bronze battleaxe", "quantity": 1, "slots": 2},
                {"item": "Iron battleaxe", "quantity": 1, "slots": 1},
                {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 7},
                {"item": "Chaos rune", "quantity": 2, "slots": 4},
                {"item": "Nature rune", "quantity": 2, "slots": 4},
                {"item": "Coins", "quantity": 4, "slots": 20},
                {"item": "Coins", "quantity": 10, "slots": 15},
                {"item": "Coins", "quantity": 30, "slots": 2},
                {"item": "Hammer", "quantity": 1, "slots": 10},
                {"item": "Bronze bar", "quantity": 1, "slots": 7},
                {"item": "Iron ore", "quantity": 1, "slots": 4},
                {"item": "Tin ore", "quantity": 1, "slots": 3},
                {"item": "Copper ore", "quantity": 1, "slots": 3},
                {"item": "Iron bar", "quantity": 1, "slots": 3},
                {"item": "Coal", "quantity": 1, "slots": 2},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 1},
                {"slots": 23},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 40},
                {"item": "Green charm", "quantity": 1, "slots": 20},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 7},
                {"slots": 903},
            ),
        },
        {
            "name": "Tertiary",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


GUARD_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 146,
            "slots": (
                {"item": "Iron bolts", "quantity_range": (2, 12), "slots": 10},
                {"item": "Steel arrows", "quantity": 1, "slots": 4},
                {"item": "Bronze arrows", "quantity": 1, "slots": 3},
                {"item": "Air rune", "quantity": 6, "slots": 2},
                {"item": "Earth rune", "quantity": 3, "slots": 2},
                {"item": "Fire rune", "quantity": 2, "slots": 2},
                {"item": "Bronze arrows", "quantity": 2, "slots": 2},
                {"item": "Blood rune", "quantity": 1, "slots": 1},
                {"item": "Chaos rune", "quantity": 1, "slots": 1},
                {"item": "Nature rune", "quantity": 1, "slots": 1},
                {"item": "Steel arrows", "quantity": 5, "slots": 1},
                {"item": "Coins", "quantity": 1, "slots": 19},
                {"item": "Coins", "quantity": 4, "slots": 8},
                {"item": "Coins", "quantity": 5, "slots": 18},
                {"item": "Coins", "quantity": 7, "slots": 16},
                {"item": "Coins", "quantity": 12, "slots": 9},
                {"item": "Coins", "quantity": 17, "slots": 4},
                {"item": "Coins", "quantity": 25, "slots": 4},
                {"item": "Coins", "quantity": 30, "slots": 2},
                {"item": "Iron dagger", "quantity": 1, "slots": 6},
                {"item": "Body talisman", "quantity": 1, "slots": 2},
                {"item": "Law talisman", "quantity": 1, "slots": 1},
                {"item": "Grain", "quantity": 1, "slots": 1},
                {"item": "Iron ore", "quantity": 1, "slots": 1},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                {"slots": 8},
            ),
        },
        {
            "name": "Tertiary",
            "total": 128,
            "slots": (
                {"slots": 127},
                {"item": "Clue scroll (medium)", "quantity": 1, "slots": 1},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 70},
                {"item": "Green charm", "quantity": 1, "slots": 9},
                {"item": "Crimson charm", "quantity": 1, "slots": 5},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 914},
            ),
        },
    ),
}


DUST_DEVIL_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Darkan main",
            "total": 32768,
            "slots": (
                {"table": DARKAN_GEM_DROP_TABLE, "slots": 2816},
                {"table": DARKAN_HERB_DROP_TABLE, "slots": 4864},
                {"item": "Rune dagger", "quantity": 1, "slots": 256},
                {"item": "Red d'hide vambraces", "quantity": 1, "slots": 512},
                {"item": "Coins", "quantity": 300, "slots": 512},
                {"item": "Fire rune", "quantity": 150, "slots": 512},
                {"item": "Ugthanki kebab", "quantity": 1, "slots": 768},
                {"item": "Earth battlestaff", "quantity": 1, "slots": 256},
                {"item": "Rune arrows", "quantity": 12, "slots": 1280},
                {"item": "Coins", "quantity": 50, "slots": 256},
                {"item": "Fire rune", "quantity": 150, "slots": 2048},
                {"item": "Steel hatchet", "quantity": 1, "slots": 768},
                {"item": "Coins", "quantity": 60, "slots": 10240},
                {"item": "Fire rune", "quantity": 37, "slots": 256},
                {"item": "Soul rune", "quantity": 5, "slots": 1024},
                {"item": "Coins", "quantity": 25, "slots": 1536},
                {"item": "Mithril bar", "quantity": 1, "slots": 768},
                {"item": "Soul rune", "quantity": 2, "slots": 256},
                {"item": "Chaos rune", "quantity": 5, "slots": 1792},
                {"item": "Coins", "quantity": 15, "slots": 1792},
                {
                    "item": "Dragon chainbody",
                    "quantity": 1,
                    "slots": 1,
                    "source_item_id": 3140,
                },
                {"slots": 255},
            ),
        },
        {
            "name": "Darkan charms",
            "total": 606,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 31},
                {"item": "Green charm", "quantity": 1, "slots": 13},
                {"item": "Crimson charm", "quantity": 1, "slots": 115},
                {"item": "Blue charm", "quantity": 1, "slots": 3},
                {"slots": 444},
            ),
        },
    ),
}


# Stat-affecting consumables (edible, but excluded from COMBAT_FOOD_DATA so
# combat auto-eat never picks them by default — owner decision 2026-07-07:
# eligible only if the player explicitly opts in). Effects are applied by
# logic_pure.apply_consumable_pure; the tables below are source-audited in
# memory-bank/source-audits/kebab-beer-consumables-2026-07-07.md.
KEBAB_SOURCE = f"{FOOD_SOURCE_PATH}: calculateKebabEffect (wiki oldid 4868155)"
BEER_SOURCE = f"{POTION_TYPE_SOURCE_PATH}: BEER beerHealth/beerStrength/beerDrain"

CONSUMABLE_DATA: Dict[str, dict] = {
    # Kebab: roll nextDouble(100) over the source effect table. Heal amounts
    # are lifepoints (AnkiScape level*10 model); boosts/drains are levels.
    "Kebab": {
        "kind": "kebab_random",
        "verb": "Eat",
        "source": KEBAB_SOURCE,
        "effect_table": (
            {"upto": 8.71, "message": "That kebab didn't seem to do a lot."},
            {"upto": 69.95, "heal_max_pct": 0.10, "message": "It restores some health."},
            {"upto": 91.07, "heal_range": (100, 200), "message": "That was a good kebab. You feel a lot better."},
            {"upto": 94.72, "heal": 300, "boost_levels": {"attack": (2, 3), "strength": (2, 3), "defense": (2, 3)},
             "message": "Wow, that was an amazing kebab! You feel really invigorated."},
            {"upto": 100.0, "drain_random_skill": (2, 4), "message": "That kebab tasted a bit dodgy."},
        ),
    },
    # Beer: engine potion. +1 Constitution tick (10 LP), +4% current Strength,
    # -7% current Attack (floored).
    "Beer": {
        "kind": "beer",
        "source": BEER_SOURCE,
        "heal_constitution_ticks": 1,
        "strength_boost_pct": 0.04,
        "attack_drain_pct": 0.07,
        "message": "You drink the beer. You feel slightly reinvigorated... and slightly dizzy.",
    },
}

try:
    from .potion_data import potion_consumables_as_dict
except ImportError:
    from potion_data import potion_consumables_as_dict
CONSUMABLE_DATA.update(potion_consumables_as_dict())

# Agility boosts are deliberately action-budgeted. RuneScape's minute-based
# decay cannot use the wall clock in AnkiScape, so one dose holds for ten
# answered Agility actions and then expires atomically.
for _dose in range(1, 5):
    CONSUMABLE_DATA[f"Agility potion ({_dose})"] = {
        "kind": "agility_boost",
        "boost": 3,
        "action_budget": 10,
        "leaves": f"Agility potion ({_dose - 1})" if _dose > 1 else "Vial",
        "message": "You drink the agility potion. Your next Agility actions use a +3 boost.",
        "source": "Agility potion oldid 6288977; action budget is an AnkiScape abstraction",
    }
for _dose in range(1, 3):
    CONSUMABLE_DATA[f"Agility mix ({_dose})"] = {
        "kind": "agility_boost",
        "boost": 3,
        "action_budget": 10,
        "heal": 60,
        "leaves": f"Agility mix ({_dose - 1})" if _dose > 1 else "Vial",
        "message": "You drink the agility mix. It restores 60 LP and grants a +3 Agility boost.",
        "source": "Agility mix oldid 6288968; action budget is an AnkiScape abstraction",
    }
CONSUMABLE_DATA["Summer pie"] = {
    "kind": "agility_boost",
    "verb": "Eat",
    "boost": 5,
    "action_budget": 10,
    "heal": 110,
    "leaves": "Half a summer pie",
    "message": "You eat half the summer pie. It restores 110 LP and grants a +5 Agility boost.",
    "source": "Summer pie oldid 6358590; action budget is an AnkiScape abstraction",
}
CONSUMABLE_DATA["Half a summer pie"] = {
    "kind": "agility_boost",
    "verb": "Eat",
    "boost": 5,
    "action_budget": 10,
    "heal": 110,
    "leaves": "Pie dish",
    "message": "You finish the summer pie. It restores 110 LP and grants a +5 Agility boost.",
    "source": "Summer pie oldid 6358590; action budget is an AnkiScape abstraction",
}
for _dose in range(1, 5):
    CONSUMABLE_DATA[f"Juju farming potion ({_dose})"] = {
        "kind": "farming_juju",
        "farm_minutes": 5,
        "leaves": f"Juju farming potion ({_dose - 1})" if _dose > 1 else "Vial",
        "message": "You drink the juju farming potion. Its harvest effect lasts for 5 farm minutes.",
        "source": "Juju farming potion oldid 6439645; farming-skill contract section 23",
    }

# Skills a kebab's dodgy roll can drain (source: any non-Constitution skill id).
KEBAB_DRAINABLE_SKILLS = (
    "attack", "strength", "defense", "ranged", "magic", "prayer", "mining",
    "smithing", "fishing", "cooking", "woodcutting", "firemaking", "crafting",
    "fletching", "runecrafting", "hunter",
)

COMBAT_FOOD_DATA: Dict[str, dict] = {
    "Crayfish": {"heal_lifepoints": 20, "source": FOOD_SOURCE_PATH},
    "Shrimps": {"heal_lifepoints": 30, "source": FOOD_SOURCE_PATH},
    "Cooked chicken": {"heal_lifepoints": 40, "source": FOOD_SOURCE_PATH},
    "Cooked meat": {"heal_lifepoints": 40, "source": FOOD_SOURCE_PATH},
    "Half an apple pie": {"heal_lifepoints": 70, "source": f"{FOOD_SOURCE_PATH}: HALF_AN_APPLE_PIE"},
    "Trout": {"heal_lifepoints": 70, "source": FOOD_SOURCE_PATH},
    "Salmon": {"heal_lifepoints": 90, "source": FOOD_SOURCE_PATH},
    "Tuna": {"heal_lifepoints": 100, "source": FOOD_SOURCE_PATH},
    "Lobster": {"heal_lifepoints": 120, "source": FOOD_SOURCE_PATH},
    "Chilli potato": {"heal_lifepoints": 140, "source": f"{FOOD_SOURCE_PATH}: CHILLI_POTATO"},
    "Swordfish": {"heal_lifepoints": 140, "source": FOOD_SOURCE_PATH},
    "Monkfish": {"heal_lifepoints": 160, "source": FOOD_SOURCE_PATH},
    "Shark": {"heal_lifepoints": 200, "source": FOOD_SOURCE_PATH},
}


COMBAT_ANTIPOISON_POTION_DATA: Dict[str, dict] = {
    "Antipoison (4)": {
        "replacement": "Antipoison (3)",
        "immunity_ticks": 1500,
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON4; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON",
    },
    "Antipoison (3)": {
        "replacement": "Antipoison (2)",
        "immunity_ticks": 1500,
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON3; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON",
    },
    "Antipoison (2)": {
        "replacement": "Antipoison (1)",
        "immunity_ticks": 1500,
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON2; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON",
    },
    "Antipoison (1)": {
        "replacement": "Vial",
        "immunity_ticks": 1500,
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON1; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON",
    },
    "Super antipoison (4)": {
        "replacement": "Super antipoison (3)",
        "immunity_ticks": 6000,
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON4; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON",
    },
    "Super antipoison (3)": {
        "replacement": "Super antipoison (2)",
        "immunity_ticks": 6000,
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON3; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON",
    },
    "Super antipoison (2)": {
        "replacement": "Super antipoison (1)",
        "immunity_ticks": 6000,
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON2; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON",
    },
    "Super antipoison (1)": {
        "replacement": "Vial",
        "immunity_ticks": 6000,
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON1; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON",
    },
}


COMBAT_ENEMY_DATA: Dict[str, dict] = {
    "menaphite_thug": {
        "display_name": "Menaphite Thug",
        "level": 55,
        "group": "Pollnivneach",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 59,
        "stats": {
            "hitpoints": 600,
            "attack": 60,
            "strength": 50,
            "defence": 20,
            "magic": 0,
            "ranged": 0,
        },
        "bonuses": {},
        "drops": {"guaranteed": (), "tables": ()},
        "source": (
            "https://runescape.wiki/w/Menaphite_Thug?oldid=6546629; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/menaphite_thug (noanims).json"
        ),
        "source_status": "provisional/Darkan; owner-approved blackjack fight-back bridge",
        "encounter_only": True,
    },
    "chicken": {
        "display_name": "Chicken",
        "level": 1,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 3.0,
        "stats": {
            "hitpoints": 30,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -47,
            "attack_slash": 0,
            "attack_crush": -42,
            "defence_stab": -42,
            "defence_slash": -42,
            "defence_crush": -42,
            "defence_magic": -42,
            "defence_ranged": -42,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1), ("Raw chicken", 1)),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Feather", "quantity": 5, "slots": 64},
                        {"item": "Feather", "quantity": 15, "slots": 32},
                        {"slots": 32},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/chicken_level_1.plugin.kts"
        ),
    },
    "rat": {
        "display_name": "Rat",
        "level": 1,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 1,
        "stats": {
            "hitpoints": 20,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -47,
            "attack_slash": 0,
            "attack_crush": -53,
            "defence_stab": -42,
            "defence_slash": -42,
            "defence_crush": -42,
            "defence_magic": -42,
            "defence_ranged": -42,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/rat_level_1.plugin.kts"
        ),
    },
    "spider": {
        "display_name": "Spider",
        "level": 1,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 2.0,
        "stats": {
            "hitpoints": 20,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -35,
            "attack_slash": 0,
            "attack_crush": -58,
            "defence_stab": -53,
            "defence_slash": -53,
            "defence_crush": -53,
            "defence_magic": -53,
            "defence_ranged": -53,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 200,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 5},
                        {"item": "Green charm", "quantity": 1, "slots": 7},
                        {"item": "Crimson charm", "quantity": 1, "slots": 3},
                        {"item": "Blue charm", "quantity": 1, "slots": 2},
                        {"slots": 183},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/spider_level_1.plugin.kts"
        ),
    },
    "giant_rat": {
        "display_name": "Giant rat",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 50,
            "attack": 2,
            "strength": 3,
            "defence": 2,
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
        "drops": GIANT_RAT_DROPS,
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/giant_rat_level_2.plugin.kts"
        ),
    },
    "giant_rat_level_6": {
        "display_name": "Giant rat",
        "level": 6,
        "group": "Rats",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 100,
            "attack": 6,
            "strength": 5,
            "defence": 2,
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
        "drops": GIANT_RAT_DROPS,
        "source": f"{GIANT_RAT_LEVEL_6_SOURCE_PATH}: id Npcs.GIANT_RAT_2091",
    },
    "giant_rat_level_26": {
        "display_name": "Giant rat",
        "level": 26,
        "group": "Rats",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 250,
            "attack": 22,
            "strength": 23,
            "defence": 22,
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
        "drops": GIANT_RAT_DROPS,
        "source": f"{GIANT_RAT_LEVEL_26_SOURCE_PATH}: ids Npcs.GIANT_RAT_4944/Npcs.GIANT_RAT_4945",
    },
    "giant_spider": {
        "display_name": "Giant spider",
        "level": 2,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
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
            "attack_stab": -10,
            "attack_slash": 0,
            "attack_crush": -10,
            "defence_stab": -10,
            "defence_slash": -10,
            "defence_crush": -10,
            "defence_magic": -10,
            "defence_ranged": -10,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 48,
                    "slots": (
                        {"item": "Air rune", "quantity_range": (4, 6), "slots": 7},
                        {"item": "Earth rune", "quantity": 4, "slots": 7},
                        {"item": "Fire rune", "quantity": 6, "slots": 7},
                        {"item": "Body rune", "quantity": 7, "slots": 3},
                        {"slots": 24},
                    ),
                },
                {
                    "name": "Secondary",
                    "total": 128,
                    "slots": (
                        {"item": "Bronze med helm", "quantity": 1, "slots": 48},
                        {"item": "Bronze bolts", "quantity": 1, "slots": 12},
                        {"item": "Bronze arrows", "quantity": 1, "slots": 12},
                        {"item": "Longbow", "quantity": 1, "slots": 4},
                        {"item": "Bronze kiteshield", "quantity": 1, "slots": 1},
                        {"slots": 51},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Staff of air", "quantity": 1, "slots": 1},
                        {"item": "Sling", "quantity": 1, "slots": 1},
                        {"slots": 126},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 90},
                        {"item": "Green charm", "quantity": 1, "slots": 11},
                        {"item": "Crimson charm", "quantity": 1, "slots": 30},
                        {"item": "Blue charm", "quantity": 1, "slots": 9},
                        {"slots": 860},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/giant_spider_level_2.plugin.kts"
        ),
    },
    "goblin_level_2_unarmed": {
        "display_name": "Goblin (unarmed)",
        "level": 2,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
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
            "attack_stab": -21,
            "attack_slash": 0,
            "attack_crush": -15,
            "defence_stab": -15,
            "defence_slash": -15,
            "defence_crush": -15,
            "defence_magic": -15,
            "defence_ranged": -15,
            "melee_strength": 0,
        },
        "drops": GOBLIN_LEVEL_2_DROPS,
        "source": f"{GOBLIN_LEVEL_2_SOURCE_PATH}: unarmed ids GOBLIN_4261/GOBLIN_4263-GOBLIN_4271",
    },
    "goblin_level_2_armed": {
        "display_name": "Goblin (armed)",
        "level": 2,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 5.0,
        "stats": {
            "hitpoints": 50,
            "attack": 3,
            "strength": 1,
            "defence": 4,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -21,
            "attack_slash": 0,
            "attack_crush": -15,
            "defence_stab": -15,
            "defence_slash": -15,
            "defence_crush": -15,
            "defence_magic": -15,
            "defence_ranged": -15,
            "melee_strength": 0,
        },
        "drops": GOBLIN_LEVEL_2_DROPS,
        "source": f"{GOBLIN_LEVEL_2_SOURCE_PATH}: armed id GOBLIN_4262",
    },
    "goblin_level_5": {
        "display_name": "Goblin",
        "level": 5,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 35,
        "slayer_xp": 12.0,
        "stats": {
            "hitpoints": 120,
            "attack": 3,
            "strength": 1,
            "defence": 4,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 12,
            "attack_slash": 0,
            "attack_crush": 12,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": GOBLIN_HIGHER_LEVEL_DROPS,
        "source": f"{GOBLIN_LEVEL_5_SOURCE_PATH}: ids GOBLIN_3265 et al.",
    },
    "goblin_level_11": {
        "display_name": "Goblin",
        "level": 11,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 16.0,
        "stats": {
            "hitpoints": 160,
            "attack": 12,
            "strength": 13,
            "defence": 7,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 6,
            "attack_crush": 8,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": GOBLIN_HIGHER_LEVEL_DROPS,
        "source": f"{GOBLIN_LEVEL_11_SOURCE_PATH}: ids GOBLIN_4409/GOBLIN_11259/GOBLIN_11260",
    },
    "goblin_level_13": {
        "display_name": "Goblin",
        "level": 13,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 16.0,
        "stats": {
            "hitpoints": 120,
            "attack": 12,
            "strength": 13,
            "defence": 7,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 6,
            "attack_crush": 8,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": GOBLIN_HIGHER_LEVEL_DROPS,
        "source": f"{GOBLIN_LEVEL_13_SOURCE_PATH}: ids GOBLIN_4408/GOBLIN_6283/GOBLIN_11261/GOBLIN_13097",
    },
    "goblin_level_16": {
        "display_name": "Goblin",
        "level": 16,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 17.0,
        "stats": {
            "hitpoints": 170,
            "attack": 16,
            "strength": 13,
            "defence": 10,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 6,
            "attack_crush": 8,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": GOBLIN_HIGHER_LEVEL_DROPS,
        "source": f"{GOBLIN_LEVEL_16_SOURCE_PATH}: id GOBLIN_4412",
    },
    "goblin_level_25": {
        "display_name": "Goblin",
        "level": 25,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 17.0,
        "stats": {
            "hitpoints": 350,
            "attack": 22,
            "strength": 17,
            "defence": 15,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 6,
            "attack_crush": 8,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": GOBLIN_HIGHER_LEVEL_DROPS,
        "source": f"{GOBLIN_LEVEL_25_SOURCE_PATH}: id GOBLIN_4411",
    },
    "hobgoblin_unarmed": {
        "display_name": "Hobgoblin (unarmed)",
        "level": 28,
        "group": "Hobgoblins",
        "slayer_xp": 29.0,
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 290,
            "attack": 22,
            "strength": 24,
            "defence": 24,
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
        "drops": HOBGOBLIN_UNARMED_DROPS,
        "source": (
            f"{HOBGOBLIN_UNARMED_SOURCE_PATH}: ids Npcs.HOBGOBLIN/Npcs.HOBGOBLIN_2686/"
            "Npcs.HOBGOBLIN_2687; main table declares total(128), active source slots sum to 127; "
            "Charms table declares total(1024), active source slots sum to 1000; "
            "RuneScape Wiki Hobgoblin oldid 6448782 (290 LP / 29 Slayer XP)"
        ),
    },
    "hobgoblin_armed": {
        "display_name": "Hobgoblin (armed)",
        "level": 28,
        "group": "Hobgoblins",
        "slayer_xp": 49.0,
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 490,
            "attack": 33,
            "strength": 31,
            "defence": 36,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 8,
            "attack_slash": 0,
            "attack_crush": 10,
            "defence_stab": 1,
            "defence_slash": 1,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": HOBGOBLIN_ARMED_DROPS,
        "source": (
            f"{HOBGOBLIN_ARMED_SOURCE_PATH}: ids Npcs.HOBGOBLIN_2688/Npcs.HOBGOBLIN_4898; "
            "aggro radius 4; RuneScape Wiki Hobgoblin oldid 6448782 "
            "(490 LP / 49 Slayer XP)"
        ),
    },
    "tzhaar_ket": {
        "display_name": "TzHaar-Ket",
        "level": 149,
        "group": "TzHaar",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 136.0,
        "stats": {
            "hitpoints": 1400,
            "attack": 120,
            "strength": 140,
            "defence": 120,
            "magic": 40,
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
        "drops": TZHAAR_KET_DROPS,
        "source": (
            f"{TZHAAR_KET_SOURCE_PATH}: id Npcs.TZHAARKET_2616; "
            "pre-death sound only; no source combat bonuses; "
            "RuneScape Wiki Kuradal oldid 6588106 (level 149, 136 Slayer XP)"
        ),
    },
    "farmer": {
        "display_name": "Farmer",
        "level": 7,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 120,
            "attack": 3,
            "strength": 4,
            "defence": 8,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 6,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": FARMER_DROPS,
        "source": f"{FARMER_SOURCE_PATH}: ids FARMER/FARMER_1757/FARMER_1758",
    },
    "chaos_druid": {
        "display_name": "Chaos druid",
        "level": 13,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 200,
            "attack": 8,
            "strength": 8,
            "defence": 12,
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
        "drops": CHAOS_DRUID_DROPS,
        "source": (
            f"{CHAOS_DRUID_SOURCE_PATH}: ids Npcs.CHAOS_DRUID_2547/Npcs.CHAOS_DRUID/"
            "Npcs.CHAOS_DRUID_7105; aggro radius 4"
        ),
    },
    "citizen": {
        "display_name": "Man/Woman",
        "level": 2,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 70,
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
            "defence_stab": -21,
            "defence_slash": -21,
            "defence_crush": -21,
            "defence_magic": -21,
            "defence_ranged": -21,
            "melee_strength": 0,
        },
        "drops": LOW_LEVEL_HUMANOID_DROPS,
        "source": (
            f"{CITIZEN_SOURCE_PATH}: ids Npcs.MAN/Npcs.MAN_2/Npcs.MAN_3/Npcs.MAN_24/"
            "Npcs.WOMAN_BRUNETTE_LONGSKIRT_4/Npcs.WOMAN_BRUNETTE_PONYTAIL_5/"
            "Npcs.WOMAN_WOMAN_BLOND_PONYTAIL_6/Npcs.MAN_16/Npcs.MAN_3223/"
            "Npcs.WOMAN_BLOND_LONGSKIRT_3226"
        ),
    },
    "monk": {
        "display_name": "Monk",
        "level": 5,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 150,
            "attack": 2,
            "strength": 2,
            "defence": 3,
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
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": f"{MONK_SOURCE_PATH}: id Npcs.MONK_7727",
    },
    "cuffs": {
        "display_name": "Cuffs",
        "level": 3,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 70,
            "attack": 1,
            "strength": 1,
            "defence": 3,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 5,
            "defence_magic": 5,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": LOW_LEVEL_HUMANOID_DROPS,
        "source": f"{CUFFS_SOURCE_PATH}: id Npcs.CUFFS",
    },
    "narf_jeff_rusty": {
        "display_name": "Narf/Jeff/Rusty",
        "level": 2,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 70,
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
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 5,
            "defence_magic": 5,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": LOW_LEVEL_HUMANOID_DROPS,
        "source": f"{NARF_JEFF_RUSTY_SOURCE_PATH}: ids Npcs.NARF/Npcs.JEFF/Npcs.RUSTY",
    },
    "pirate": {
        "display_name": "Pirate",
        "level": 23,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 200,
            "attack": 21,
            "strength": 21,
            "defence": 21,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 8,
            "attack_slash": 8,
            "attack_crush": 8,
            "defence_stab": 3,
            "defence_slash": 2,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 10,
        },
        "drops": PIRATE_DROPS,
        "source": (
            f"{PIRATE_SOURCE_PATH}: ids Npcs.PIRATE/Npcs.PIRATE_183/Npcs.PIRATE_184; "
            "source attackBonus/strengthBonus mapped to melee attack/strength bonuses"
        ),
    },
    "monk_of_zamorak_level_45": {
        "display_name": "Monk of Zamorak",
        "level": 45,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 250,
        "stats": {
            "hitpoints": 400,
            "attack": 38,
            "strength": 38,
            "defence": 42,
            "magic": 40,
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
        "drops": MONK_OF_ZAMORAK_LEVEL_45_DROPS,
        "source": (
            f"{MONK_OF_ZAMORAK_LEVEL_45_SOURCE_PATH}: id Npcs.MONK_OF_ZAMORAK_190; "
            "Items.ZAMORAK_ROBE_1035 mapped to Zamorak robe top, "
            "Items.ZAMORAK_ROBE mapped to Zamorak robe bottom; aggro radius 4"
        ),
    },
    "unicorn": {
        "display_name": "Unicorn",
        "level": 15,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "stats": {
            "hitpoints": 190,
            "attack": 11,
            "strength": 13,
            "defence": 13,
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
        "drops": UNICORN_DROPS,
        "source": f"{UNICORN_SOURCE_PATH}: id Npcs.UNICORN",
    },
    "black_unicorn": {
        "display_name": "Black unicorn",
        "level": 27,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "stats": {
            "hitpoints": 290,
            "attack": 21,
            "strength": 21,
            "defence": 23,
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
        "drops": UNICORN_DROPS,
        "source": f"{BLACK_UNICORN_SOURCE_PATH}: id Npcs.BLACK_UNICORN",
    },
    "black_bear": {
        "display_name": "Black bear",
        "level": 19,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 25.0,
        "stats": {
            "hitpoints": 250,
            "attack": 15,
            "strength": 16,
            "defence": 13,
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
        "drops": BLACK_BEAR_DROPS,
        "source": f"{BLACK_BEAR_SOURCE_PATH}: id Npcs.BLACK_BEAR; SlayerAssignment.BEAR level 1 xp 25.0; aggro radius 4",
    },
    "wolf": {
        "display_name": "Wolf",
        "level": 11,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 10.0,
        "stats": {
            "hitpoints": 100,
            "attack": 10,
            "strength": 10,
            "defence": 10,
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
        "drops": WOLF_LEVEL_11_DROPS,
        "source": f"{WOLF_LEVEL_11_SOURCE_PATH}: ids Npcs.WOLF_4414/Npcs.WOLF_11263; SlayerAssignment.WOLF level 1 xp 10.0; aggro radius 4; attackStyle STAB",
    },
    "white_wolf_level_25": {
        "display_name": "White wolf",
        "level": 25,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 34.0,
        "stats": {
            "hitpoints": 340,
            "attack": 20,
            "strength": 16,
            "defence": 22,
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
        "drops": WHITE_WOLF_DROPS,
        "source": f"{WHITE_WOLF_LEVEL_25_SOURCE_PATH}: ids Npcs.WHITE_WOLF/Npcs.WOLF_4413/Npcs.WOLF_6047; SlayerAssignment.WOLF level 1 xp 34.0; aggro radius 4",
    },
    "white_wolf_level_38": {
        "display_name": "White wolf",
        "level": 38,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 44.0,
        "stats": {
            "hitpoints": 440,
            "attack": 30,
            "strength": 31,
            "defence": 32,
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
        "drops": WHITE_WOLF_DROPS,
        "source": f"{WHITE_WOLF_LEVEL_38_SOURCE_PATH}: id Npcs.WHITE_WOLF_97; SlayerAssignment.WOLF level 1 xp 44.0; aggro radius 4",
    },
    "big_wolf": {
        "display_name": "Big wolf",
        "level": 73,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 74.0,
        "stats": {
            "hitpoints": 740,
            "attack": 60,
            "strength": 61,
            "defence": 62,
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
        "drops": WHITE_WOLF_DROPS,
        "source": f"{BIG_WOLF_SOURCE_PATH}: id Npcs.BIG_WOLF_6046; SlayerAssignment.WOLF level 1 xp 74.0; aggro radius 4",
    },
    "giant_bat": {
        "display_name": "Giant bat",
        "level": 27,
        "group": "Bats",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 32.0,
        "stats": {
            "hitpoints": 320,
            "attack": 22,
            "strength": 22,
            "defence": 22,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 10,
            "defence_slash": 10,
            "defence_crush": 12,
            "defence_magic": 10,
            "defence_ranged": 8,
            "melee_strength": 0,
        },
        "drops": GIANT_BAT_DROPS,
        "source": f"{GIANT_BAT_SOURCE_PATH}: id Npcs.GIANT_BAT; SlayerAssignment.BAT level 1 xp 32.0; aggro radius 4",
    },
    "hill_giant": {
        "display_name": "Hill giant",
        "level": 28,
        "group": "Giants",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 30,
        "slayer_xp": 35.0,
        "stats": {
            "hitpoints": 350,
            "attack": 18,
            "strength": 22,
            "defence": 26,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 18,
            "attack_slash": 0,
            "attack_crush": 16,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": HILL_GIANT_DROPS,
        "source": (
            f"{HILL_GIANT_SOURCE_PATH}: id Npcs.HILL_GIANT; "
            "SlayerAssignment.HILL_GIANT level 1 xp 35.0; attackStyle CRUSH; aggro radius 4"
        ),
    },
    "moss_giant": {
        "display_name": "Moss giant",
        "level": 42,
        "group": "Giants",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 30,
        "slayer_xp": 60.0,
        "stats": {
            "hitpoints": 600,
            "attack": 30,
            "strength": 30,
            "defence": 30,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 33,
            "attack_slash": 0,
            "attack_crush": 31,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": MOSS_GIANT_DROPS,
        "source": (
            f"{MOSS_GIANT_SOURCE_PATH}: ids Npcs.MOSS_GIANT/Npcs.MOSS_GIANT_1587/"
            "Npcs.MOSS_GIANT_1588/Npcs.MOSS_GIANT_4688; SlayerAssignment.MOSS_GIANT level 1 "
            "xp 60.0; attackStyle CRUSH; aggro radius 4"
        ),
    },
    "ice_giant": {
        "display_name": "Ice giant",
        "level": 53,
        "group": "Giants",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 30,
        "slayer_xp": 70.0,
        "stats": {
            "hitpoints": 700,
            "attack": 40,
            "strength": 40,
            "defence": 40,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 29,
            "attack_slash": 29,
            "attack_crush": 29,
            "defence_stab": 0,
            "defence_slash": 3,
            "defence_crush": 2,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 31,
        },
        "drops": ICE_GIANT_DROPS,
        "source": (
            f"{ICE_GIANT_SOURCE_PATH}: ids Npcs.ICE_GIANT/Npcs.ICE_GIANT_3072/Npcs.ICE_GIANT_4685/"
            "Npcs.ICE_GIANT_4686/Npcs.ICE_GIANT_4687; SlayerAssignment.ICE_GIANT level 1 "
            "xp 70.0; attackStyle SLASH; attackBonus/strengthBonus; aggro radius 5"
        ),
    },
    "ghost": {
        "display_name": "Ghost",
        "level": 19,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 40,
        "slayer_xp": 25.0,
        "stats": {
            "hitpoints": 250,
            "attack": 13,
            "strength": 13,
            "defence": 18,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 5,
            "defence_magic": -5,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": GHOST_DROPS,
        "source": f"{GHOST_LEVEL_19_SOURCE_PATH}: ids Npcs.GHOST/Npcs.GHOST_104/Npcs.GHOST_5349/Npcs.GHOST_5350/Npcs.GHOST_5351/Npcs.GHOST_5352; SlayerAssignment.GHOST level 1 xp 25.0; attackStyle CRUSH; no on_npc_death drop callback",
    },
    "zombie_level_13": {
        "display_name": "Zombie",
        "level": 13,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 22.0,
        "stats": {
            "hitpoints": 220,
            "attack": 8,
            "strength": 9,
            "defence": 10,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_13_SOURCE_PATH}: id Npcs.ZOMBIE; SlayerAssignment.ZOMBIE level 1 xp 22.0; aggro radius 4",
    },
    "zombie_level_18": {
        "display_name": "Zombie",
        "level": 18,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 24.0,
        "stats": {
            "hitpoints": 240,
            "attack": 13,
            "strength": 13,
            "defence": 18,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_18_SOURCE_PATH}: id Npcs.ZOMBIE_74; SlayerAssignment.ZOMBIE level 1 xp 24.0; aggro radius 4",
    },
    "zombie_level_24": {
        "display_name": "Zombie",
        "level": 24,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 30.0,
        "stats": {
            "hitpoints": 300,
            "attack": 19,
            "strength": 21,
            "defence": 16,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 9,
            "defence_slash": 8,
            "defence_crush": 12,
            "defence_magic": 10,
            "defence_ranged": 11,
            "melee_strength": 0,
        },
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_24_SOURCE_PATH}: id Npcs.ZOMBIE_75; SlayerAssignment.ZOMBIE level 1 xp 30.0; aggro radius 4",
    },
    "zombie_level_25": {
        "display_name": "Zombie",
        "level": 25,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 30.0,
        "stats": {
            "hitpoints": 300,
            "attack": 19,
            "strength": 21,
            "defence": 16,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 9,
            "defence_slash": 8,
            "defence_crush": 12,
            "defence_magic": 10,
            "defence_ranged": 11,
            "melee_strength": 0,
        },
        "drops": ZOMBIE_LEVEL_25_DROPS,
        "source": f"{ZOMBIE_LEVEL_25_SOURCE_PATH}: id Npcs.ZOMBIE_76; SlayerAssignment.ZOMBIE level 1 xp 30.0; level-specific main table has Iron hatchet 5/128 and empty 6/128",
    },
    "zombie_level_30": {
        "display_name": "Zombie",
        "level": 30,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 30.0,
        "stats": {
            "hitpoints": 300,
            "attack": 25,
            "strength": 29,
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
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_30_SOURCE_PATH}: ids Npcs.ZOMBIE_5375/Npcs.ZOMBIE_4392/Npcs.ZOMBIE_5376; SlayerAssignment.ZOMBIE level 1 xp 30.0; aggro radius 4",
    },
    "zombie_level_44": {
        "display_name": "Zombie",
        "level": 44,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 30.0,
        "stats": {
            "hitpoints": 400,
            "attack": 35,
            "strength": 40,
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
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_44_SOURCE_PATH}: ids Npcs.ZOMBIE_4393/Npcs.ZOMBIE_5377/Npcs.ZOMBIE_5378; SlayerAssignment.ZOMBIE level 1 xp 30.0; aggro radius 4",
    },
    "zombie_level_53": {
        "display_name": "Zombie",
        "level": 53,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 50.0,
        "stats": {
            "hitpoints": 500,
            "attack": 55,
            "strength": 40,
            "defence": 48,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 19,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 18,
            "defence_crush": 0,
            "defence_magic": 20,
            "defence_ranged": 21,
            "melee_strength": 0,
        },
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_53_SOURCE_PATH}: ids Npcs.ZOMBIE_4394/Npcs.ZOMBIE_5379/Npcs.ZOMBIE_5380; SlayerAssignment.ZOMBIE level 1 xp 50.0; aggro radius 4",
    },
    "skeleton_level_21": {
        "display_name": "Skeleton",
        "level": 21,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 24.0,
        "stats": {
            "hitpoints": 240,
            "attack": 17,
            "strength": 17,
            "defence": 17,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": -5,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": SKELETON_LOW_DROPS,
        "source": f"{SKELETON_LEVEL_21_SOURCE_PATH}: id Npcs.SKELETON_91; SlayerAssignment.SKELETON level 1 xp 24.0; aggro radius 4",
    },
    "skeleton_level_22": {
        "display_name": "Skeleton",
        "level": 22,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 70,
        "slayer_xp": 29.0,
        "stats": {
            "hitpoints": 290,
            "attack": 15,
            "strength": 18,
            "defence": 17,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": -5,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": SKELETON_LOW_DROPS,
        "source": f"{SKELETON_LEVEL_22_SOURCE_PATH}: ids Npcs.SKELETON/Npcs.SKELETON_5332/Npcs.SKELETON_5333/Npcs.SKELETON_5334; SlayerAssignment.SKELETON level 1 xp 29.0; aggro radius 4",
    },
    "skeleton_level_25": {
        "display_name": "Skeleton",
        "level": 25,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 60,
        "slayer_xp": 17.0,
        "stats": {
            "hitpoints": 170,
            "attack": 24,
            "strength": 24,
            "defence": 24,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 15,
            "attack_slash": 0,
            "attack_crush": 14,
            "defence_stab": 9,
            "defence_slash": 11,
            "defence_crush": -2,
            "defence_magic": 1,
            "defence_ranged": 4,
            "melee_strength": 0,
        },
        "drops": SKELETON_HIGH_DROPS,
        "source": f"{SKELETON_LEVEL_25_SOURCE_PATH}: id Npcs.SKELETON_92; SlayerAssignment.SKELETON level 1 xp 17.0; aggro radius 4",
    },
    "skeleton_level_45": {
        "display_name": "Skeleton",
        "level": 45,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 59.0,
        "stats": {
            "hitpoints": 590,
            "attack": 32,
            "strength": 35,
            "defence": 36,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 15,
            "attack_slash": 0,
            "attack_crush": 14,
            "defence_stab": 9,
            "defence_slash": 11,
            "defence_crush": -2,
            "defence_magic": 1,
            "defence_ranged": 4,
            "melee_strength": 0,
        },
        "drops": SKELETON_HIGH_DROPS,
        "source": f"{SKELETON_LEVEL_45_SOURCE_PATH}: id Npcs.SKELETON_93; SlayerAssignment.SKELETON level 1 xp 59.0; no aggro block in source",
    },
    "skeleton_level_60": {
        "display_name": "Skeleton",
        "level": 60,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 70,
        "slayer_xp": 70.0,
        "stats": {
            "hitpoints": 700,
            "attack": 50,
            "strength": 50,
            "defence": 40,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 35,
            "defence_slash": 35,
            "defence_crush": -5,
            "defence_magic": 0,
            "defence_ranged": 35,
            "melee_strength": 0,
        },
        "drops": SKELETON_HIGH_DROPS,
        "source": f"{SKELETON_LEVEL_60_SOURCE_PATH}: ids Npcs.SKELETON_4385/Npcs.SKELETON_5365/Npcs.SKELETON_5366; SlayerAssignment.SKELETON level 1 xp 70.0; aggro radius 4",
    },
    "skeleton_level_68": {
        "display_name": "Skeleton",
        "level": 68,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 60,
        "slayer_xp": 65.0,
        "stats": {
            "hitpoints": 700,
            "attack": 60,
            "strength": 50,
            "defence": 60,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 35,
            "defence_slash": 35,
            "defence_crush": -5,
            "defence_magic": 0,
            "defence_ranged": 35,
            "melee_strength": 0,
        },
        "drops": SKELETON_HIGH_DROPS,
        "source": f"{SKELETON_LEVEL_68_SOURCE_PATH}: id Npcs.SKELETON_4384; SlayerAssignment.SKELETON level 1 xp 65.0; aggro radius 4",
    },
    "skeleton_level_85": {
        "display_name": "Skeleton",
        "level": 85,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 60,
        "slayer_xp": 65.0,
        "stats": {
            "hitpoints": 770,
            "attack": 74,
            "strength": 74,
            "defence": 74,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 15,
            "attack_slash": 14,
            "attack_crush": 0,
            "defence_stab": 79,
            "defence_slash": 31,
            "defence_crush": 20,
            "defence_magic": 5,
            "defence_ranged": 70,
            "melee_strength": 0,
        },
        "drops": SKELETON_HIGH_DROPS,
        "source": f"{SKELETON_LEVEL_85_SOURCE_PATH}: ids Npcs.SKELETON_4386/Npcs.SKELETON_5367/Npcs.SKELETON_5368; SlayerAssignment.SKELETON level 1 xp 65.0; aggro radius 4",
    },
    "duck_land": {
        "display_name": "Duck (land)",
        "level": 1,
        "group": "Birds",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 3.0,
        "stats": {
            "hitpoints": 30,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -47,
            "attack_slash": 0,
            "attack_crush": -42,
            "defence_stab": -42,
            "defence_slash": -42,
            "defence_crush": -42,
            "defence_magic": -42,
            "defence_ranged": -42,
            "melee_strength": 0,
        },
        "drops": DUCK_LAND_DROPS,
        "source": f"{DUCK_SOURCE_PATH}: land ids Npcs.DUCK_6113/Npcs.DRAKE",
    },
    "duck_water": {
        "display_name": "Duck (water)",
        "level": 1,
        "group": "Birds",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 3.0,
        "stats": {
            "hitpoints": 30,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -47,
            "attack_slash": 0,
            "attack_crush": -42,
            "defence_stab": -42,
            "defence_slash": -42,
            "defence_crush": -42,
            "defence_magic": -42,
            "defence_ranged": -42,
            "melee_strength": 0,
        },
        "drops": DUCK_WATER_DROPS,
        "source": f"{DUCK_SOURCE_PATH}: water ids Npcs.DUCK/Npcs.DUCK_2693; no death drop callback",
    },
    "cow": {
        "display_name": "Cow",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 45,
        "slayer_xp": 8.0,
        "stats": {
            "hitpoints": 80,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -15,
            "attack_slash": 0,
            "attack_crush": -15,
            "defence_stab": -21,
            "defence_slash": -21,
            "defence_crush": -21,
            "defence_magic": -21,
            "defence_ranged": -21,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1), ("Raw beef", 1), ("Cowhide", 1)),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Sling", "quantity": 1, "slots": 64},
                        {"slots": 960},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 9},
                        {"item": "Green charm", "quantity": 1, "slots": 40},
                        {"item": "Crimson charm", "quantity": 1, "slots": 3},
                        {"item": "Blue charm", "quantity": 1, "slots": 1},
                        {"slots": 947},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/cow_level_2.plugin.kts"
        ),
    },
    "cow_calf": {
        "display_name": "Cow calf",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 45,
        "slayer_xp": 6.0,
        "stats": {
            "hitpoints": 60,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -20,
            "attack_slash": 0,
            "attack_crush": -20,
            "defence_stab": -26,
            "defence_slash": -26,
            "defence_crush": -26,
            "defence_magic": -26,
            "defence_ranged": -26,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1), ("Raw beef", 1), ("Cowhide", 1)), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/cow_calf_level_2.plugin.kts"
        ),
    },
    "ram": {
        "display_name": "Ram",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 45,
        "stats": {
            "hitpoints": 80,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -15,
            "attack_slash": 0,
            "attack_crush": -15,
            "defence_stab": -21,
            "defence_slash": -21,
            "defence_crush": -21,
            "defence_magic": -21,
            "defence_ranged": -21,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/ram_level_2.plugin.kts"
        ),
    },
    "highwayman": {
        "display_name": "Highwayman",
        "level": 5,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 60,
        "stats": {
            "hitpoints": 130,
            "attack": 2,
            "strength": 2,
            "defence": 4,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 6,
            "attack_slash": 6,
            "attack_crush": 6,
            "defence_stab": 0,
            "defence_slash": 3,
            "defence_crush": 2,
            "defence_magic": 0,
            "defence_ranged": 2,
            "melee_strength": 7,
        },
        "drops": {
            "guaranteed": (("Bones", 1), ("Cape", 1)),
            "tables": (
                {
                    "name": "Main",
                    "total": 20,
                    "slots": (
                        {"item": "Iron bolts", "quantity_range": (2, 12), "slots": 1},
                        {"slots": 19},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/highwayman_level_5.plugin.kts"
        ),
    },
    "mugger": {
        "display_name": "Mugger",
        "level": 6,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 80,
            "attack": 5,
            "strength": 5,
            "defence": 5,
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
            "melee_strength": -21,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 162},
                        {"item": "Mind rune", "quantity": 9, "slots": 24},
                        {"item": "Water rune", "quantity": 6, "slots": 16},
                        {"item": "Earth rune", "quantity": 5, "slots": 16},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 104},
                        {"item": "Coins", "quantity": 10, "slots": 104},
                        {"item": "Coins", "quantity": 5, "slots": 96},
                        {"item": "Coins", "quantity": 15, "slots": 24},
                        {"item": "Coins", "quantity": 25, "slots": 8},
                        {"item": "Rope", "quantity": 1, "slots": 270},
                        {"slots": 104},
                        {"item": "Fishing bait", "quantity": 1, "slots": 48},
                        {"item": "Copper ore", "quantity": 1, "slots": 16},
                        {"item": "Bronze med helm", "quantity": 1, "slots": 16},
                        {"item": "Knife", "quantity": 1, "slots": 8},
                        {"item": "Cabbage", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": f"{MUGGER_SOURCE_PATH}: ids = Npcs.MUGGER/Npcs.MUGGER_7161/Npcs.MUGGER_7162",
    },
    "thug": {
        "display_name": "Thug",
        "level": 10,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 180,
            "attack": 7,
            "strength": 5,
            "defence": 9,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 5,
            "defence_stab": 2,
            "defence_slash": 3,
            "defence_crush": 3,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Iron med helm", "quantity": 1, "slots": 4},
                        {"item": "Iron battleaxe", "quantity": 1, "slots": 2},
                        {"item": "Steel hatchet", "quantity": 1, "slots": 1},
                        {"item": "Nature rune", "quantity": 2, "slots": 13},
                        {"item": "Chaos rune", "quantity": 2, "slots": 4},
                        {"item": "Cosmic rune", "quantity": 2, "slots": 1},
                        {"item": "Law rune", "quantity": 2, "slots": 1},
                        {"item": "Death rune", "quantity": 2, "slots": 1},
                        {"item": "Iron ore", "quantity": 1, "slots": 4},
                        {"item": "Iron bar", "quantity": 1, "slots": 3},
                        {"item": "Coal", "quantity": 1, "slots": 2},
                        {"item": "Coins", "quantity": 8, "slots": 23},
                        {"item": "Coins", "quantity": 15, "slots": 12},
                        {"item": "Coins", "quantity": 30, "slots": 2},
                        {"item": "Coins", "quantity": 20, "slots": 1},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 24},
                        {"slots": 30},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 120},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 8},
                        {"item": "Blue charm", "quantity": 1, "slots": 5},
                        {"slots": 857},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": (
            f"{THUG_SOURCE_PATH}: ids = Npcs.THUG_7106/Npcs.THUG_7107/"
            "Npcs.THUG_7109/Npcs.THUG_7110/Npcs.THUG_7112/Npcs.THUG_7113/Npcs.THUG_7114"
        ),
    },
    "thief": {
        "display_name": "Thief",
        "level": 16,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 170,
            "attack": 14,
            "strength": 13,
            "defence": 12,
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
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Bronze med helm", "quantity": 1, "slots": 2},
                        {"item": "Iron dagger", "quantity": 1, "slots": 1},
                        {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 22},
                        {"item": "Bronze arrows", "quantity": 7, "slots": 3},
                        {"item": "Earth rune", "quantity": 4, "slots": 2},
                        {"item": "Fire rune", "quantity": 6, "slots": 2},
                        {"item": "Mind rune", "quantity": 9, "slots": 2},
                        {"item": "Chaos rune", "quantity": 2, "slots": 1},
                        {"item": "Coins", "quantity": 3, "slots": 38},
                        {"item": "Coins", "quantity": 5, "slots": 9},
                        {"item": "Coins", "quantity": 15, "slots": 4},
                        {"item": "Coins", "quantity": 25, "slots": 1},
                        {"item": "Fishing bait", "quantity": 1, "slots": 5},
                        {"item": "Copper ore", "quantity": 1, "slots": 2},
                        {"item": "Earth talisman", "quantity": 1, "slots": 2},
                        {"item": "Cabbage", "quantity": 1, "slots": 1},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 23},
                        {"slots": 8},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": f"{THIEF_SOURCE_PATH}: ids = Npcs.THIEF_5926/Npcs.THIEF_5927/Npcs.THIEF_5928/Npcs.THIEF_5929",
    },
    "dwarf_level_10": {
        "display_name": "Dwarf (level 10)",
        "level": 10,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 50,
        "slayer_xp": 16.0,
        "stats": {
            "hitpoints": 160,
            "attack": 8,
            "strength": 8,
            "defence": 6,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 5,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": DWARF_DROPS,
        "source": f"{DWARF_SOURCE_PATH}: idsLevel10 Npcs.DWARF_118/Npcs.DWARF_3221/Npcs.DWARF_3272",
    },
    "dwarf_level_11": {
        "display_name": "Dwarf (level 11)",
        "level": 11,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 16.0,
        "stats": {
            "hitpoints": 180,
            "attack": 8,
            "strength": 8,
            "defence": 8,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 5,
            "defence_ranged": 10,
            "melee_strength": 0,
        },
        "drops": DWARF_DROPS,
        "source": (
            f"{DWARF_SOURCE_PATH}: idsLevel11 Npcs.DWARF_3219/Npcs.DWARF_3220/"
            "Npcs.DWARF_3268/Npcs.DWARF_3269/Npcs.DWARF_3270"
        ),
    },
    "market_guard": {
        "display_name": "Market guard",
        "level": 20,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 220,
            "attack": 17,
            "strength": 18,
            "defence": 13,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 9,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 24,
            "defence_slash": 14,
            "defence_crush": 19,
            "defence_magic": 4,
            "defence_ranged": 16,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": f"{MARKET_GUARD_SOURCE_PATH}: id Npcs.MARKET_GUARD_2236",
    },
    "jail_guard": {
        "display_name": "Jail guard",
        "level": 26,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 320,
            "attack": 19,
            "strength": 23,
            "defence": 21,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 9,
            "defence_stab": 8,
            "defence_slash": 9,
            "defence_crush": 10,
            "defence_magic": 4,
            "defence_ranged": 9,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            f"{JAIL_GUARD_SOURCE_PATH}: ids Npcs.JAIL_GUARD/Npcs.JAIL_GUARD_448/"
            "Npcs.JAIL_GUARD_449/Npcs.JAIL_GUARD_917; aggro radius 4"
        ),
    },
    "guard_varrock": {
        "display_name": "Guard (Varrock)",
        "level": 21,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 220,
            "attack": 19,
            "strength": 18,
            "defence": 14,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 0,
            "attack_crush": 5,
            "defence_stab": 24,
            "defence_slash": 30,
            "defence_crush": 25,
            "defence_magic": -9,
            "defence_ranged": 25,
            "melee_strength": 0,
        },
        "drops": GUARD_DROPS,
        "source": f"{GUARD_SOURCE_PATH}: varrockId Npcs.GUARD_5919/Npcs.GUARD_5920; faladorCrossbowId excluded because source comments no definition yet",
    },
    "guard_sword": {
        "display_name": "Guard (sword)",
        "level": 21,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 220,
            "attack": 19,
            "strength": 18,
            "defence": 14,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 0,
            "attack_crush": 5,
            "defence_stab": 18,
            "defence_slash": 25,
            "defence_crush": 19,
            "defence_magic": -4,
            "defence_ranged": 20,
            "melee_strength": 0,
        },
        "drops": GUARD_DROPS,
        "source": (
            f"{GUARD_SOURCE_PATH}: faladorSwordId Npcs.GUARD/Npcs.GUARD_3228; "
            "edgevilleId Npcs.GUARD_296/Npcs.GUARD_297/Npcs.GUARD_298/Npcs.GUARD_299/"
            "Npcs.GUARD_3407/Npcs.GUARD_3408; faladorCrossbowId excluded because source comments no definition yet"
        ),
    },
    "guard_battleaxe": {
        "display_name": "Guard (battleaxe)",
        "level": 21,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 220,
            "attack": 15,
            "strength": 15,
            "defence": 16,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 6,
            "attack_slash": 0,
            "attack_crush": 10,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 5,
            "defence_magic": -4,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": GUARD_DROPS,
        "source": f"{GUARD_SOURCE_PATH}: faladorBattleaxeId Npcs.GUARD_3230/Npcs.GUARD_3241; faladorCrossbowId excluded because source comments no definition yet",
    },
    "black_knight": {
        "display_name": "Black knight",
        "level": 33,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 420,
            "attack": 25,
            "strength": 25,
            "defence": 25,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 18,
            "attack_slash": 0,
            "attack_crush": 16,
            "defence_stab": 73,
            "defence_slash": 76,
            "defence_crush": 70,
            "defence_magic": -11,
            "defence_ranged": 72,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 116,
                    "slots": (
                        {"item": "Iron sword", "quantity": 1, "slots": 4},
                        {"item": "Iron full helm", "quantity": 1, "slots": 2},
                        {"item": "Steel mace", "quantity": 1, "slots": 1},
                        {"item": "Mithril arrows", "quantity": 3, "slots": 4},
                        {"item": "Body rune", "quantity": 9, "slots": 3},
                        {"item": "Chaos rune", "quantity": 6, "slots": 3},
                        {"item": "Earth rune", "quantity": 10, "slots": 3},
                        {"item": "Death rune", "quantity": 2, "slots": 2},
                        {"item": "Law rune", "quantity": 3, "slots": 2},
                        {"item": "Cosmic rune", "quantity": 7, "slots": 1},
                        {"item": "Mind rune", "quantity": 2, "slots": 1},
                        {"item": "Steel bar", "quantity": 1, "slots": 6},
                        {"item": "Tin ore", "quantity": 1, "slots": 1},
                        {"item": "Pot of flour", "quantity": 1, "slots": 1},
                        {"item": "Coins", "quantity": 35, "slots": 21},
                        {"item": "Coins", "quantity": 6, "slots": 11},
                        {"item": "Coins", "quantity": 58, "slots": 10},
                        {"item": "Coins", "quantity": 12, "slots": 9},
                        {"item": "Coins", "quantity": 80, "slots": 2},
                        {"item": "Coins", "quantity": 1, "slots": 1},
                        {"item": "Coins", "quantity": 13, "slots": 1},
                        {"item": "Bread", "quantity": 1, "slots": 1},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 3},
                        {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 3},
                        {"slots": 2},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 30},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 8},
                        {"item": "Blue charm", "quantity": 1, "slots": 8},
                        {"slots": 944},
                    ),
                },
            ),
        },
        "source": (
            f"{BLACK_KNIGHT_SOURCE_PATH}: id Npcs.BLACK_KNIGHT; "
            "main table declares total(128), active source slots sum to 116"
        ),
    },
    "outlaw": {
        "display_name": "Outlaw",
        "level": 35,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 2,
        "xp_multiplier": 0.025,
        "stats": {
            "hitpoints": 200,
            "attack": 35,
            "strength": 30,
            "defence": 25,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": -21,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": OUTLAW_DROPS,
        "source": (
            f"{OUTLAW_SOURCE_PATH}: ids Npcs.OUTLAW through Npcs.OUTLAW_5851; "
            "xpMultiplier 0.025; aggro radius 4; "
            "main table declares total(128), active source slots sum to 127"
        ),
    },
    "chaos_dwarf": {
        "display_name": "Chaos dwarf",
        "level": 48,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 61.0,
        "stats": {
            "hitpoints": 610,
            "attack": 38,
            "strength": 42,
            "defence": 28,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 13,
            "attack_slash": 0,
            "attack_crush": 9,
            "defence_stab": 40,
            "defence_slash": 34,
            "defence_crush": 25,
            "defence_magic": 10,
            "defence_ranged": 35,
            "melee_strength": 0,
        },
        "drops": CHAOS_DWARF_DROPS,
        "source": (
            f"{CHAOS_DWARF_SOURCE_PATH}: id Npcs.CHAOS_DWARF; "
            "SlayerAssignment.DWARF level 1 xp 61.0; aggro radius 4"
        ),
    },
    "haakon_the_champion": {
        "display_name": "Haakon the Champion",
        "level": 29,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 350,
            "attack": 22,
            "strength": 22,
            "defence": 25,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 8,
            "attack_slash": 0,
            "attack_crush": 9,
            "defence_stab": 12,
            "defence_slash": 14,
            "defence_crush": 10,
            "defence_magic": -1,
            "defence_ranged": 11,
            "melee_strength": 0,
        },
        "drops": HAAKON_DROPS,
        "source": f"{HAAKON_SOURCE_PATH}: id Npcs.HAAKON_THE_CHAMPION; no Charms table in source",
    },
    "ham_guard_level_12": {
        "display_name": "H.A.M. guard",
        "level": 12,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 150,
            "attack": 8,
            "strength": 12,
            "defence": 8,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": HAM_GUARD_DROPS,
        "source": (
            f"{HAM_GUARD_SOURCE_PATH}: id Npcs.HAM_GUARD; "
            "main table declares total(660), active source slots sum to 648"
        ),
    },
    "ham_guard_level_18": {
        "display_name": "H.A.M. guard",
        "level": 18,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 200,
            "attack": 14,
            "strength": 18,
            "defence": 12,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 6,
            "defence_slash": 6,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 6,
            "melee_strength": 0,
        },
        "drops": HAM_GUARD_DROPS,
        "source": (
            f"{HAM_GUARD_SOURCE_PATH}: id Npcs.HAM_GUARD_1711; "
            "main table declares total(660), active source slots sum to 648"
        ),
    },
    "ham_guard_level_22": {
        "display_name": "H.A.M. guard",
        "level": 22,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 300,
            "attack": 16,
            "strength": 20,
            "defence": 12,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 7,
            "defence_slash": 7,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 7,
            "melee_strength": 0,
        },
        "drops": HAM_GUARD_DROPS,
        "source": (
            f"{HAM_GUARD_SOURCE_PATH}: id Npcs.HAM_GUARD_1712; "
            "main table declares total(660), active source slots sum to 648"
        ),
    },
    "imp": {
        "display_name": "Imp",
        "level": 2,
        "group": "Demons",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 80,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -42,
            "attack_slash": 0,
            "attack_crush": -37,
            "defence_stab": -42,
            "defence_slash": -42,
            "defence_crush": -42,
            "defence_magic": -42,
            "defence_ranged": -42,
            "melee_strength": 0,
        },
        "drops": IMP_DROPS,
        "source": (
            f"{IMP_SOURCE_PATH}: ids Npcs.IMP/Npcs.IMP_709; "
            "source teleport timer is spatial movement only"
        ),
    },
    "white_knight_level_36": {
        "display_name": "White knight",
        "level": 36,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 520,
            "attack": 27,
            "strength": 29,
            "defence": 21,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 30,
            "attack_slash": 30,
            "attack_crush": 30,
            "defence_stab": 83,
            "defence_slash": 76,
            "defence_crush": 70,
            "defence_magic": -11,
            "defence_ranged": 74,
            "melee_strength": 31,
        },
        "drops": WHITE_KNIGHT_LEVEL_36_DROPS,
        "source": (
            f"{WHITE_KNIGHT_LEVEL_36_SOURCE_PATH}: id Npcs.WHITE_KNIGHT; "
            "source attackBonus/strengthBonus mapped to melee attack/strength bonuses"
        ),
    },
    "white_knight_level_38": {
        "display_name": "White knight",
        "level": 38,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 520,
            "attack": 30,
            "strength": 29,
            "defence": 25,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 30,
            "attack_slash": 30,
            "attack_crush": 30,
            "defence_stab": 83,
            "defence_slash": 76,
            "defence_crush": 70,
            "defence_magic": -11,
            "defence_ranged": 74,
            "melee_strength": 31,
        },
        "drops": WHITE_KNIGHT_LEVEL_38_DROPS,
        "source": (
            f"{WHITE_KNIGHT_LEVEL_38_SOURCE_PATH}: id Npcs.WHITE_KNIGHT_3348; "
            "source attackBonus/strengthBonus mapped to melee attack/strength bonuses; "
            "main table declares total(128), active source slots sum to 130"
        ),
    },
    "white_knight_level_39": {
        "display_name": "White knight",
        "level": 39,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 520,
            "attack": 32,
            "strength": 29,
            "defence": 27,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 30,
            "attack_slash": 30,
            "attack_crush": 30,
            "defence_stab": 83,
            "defence_slash": 76,
            "defence_crush": 70,
            "defence_magic": -11,
            "defence_ranged": 74,
            "melee_strength": 31,
        },
        "drops": WHITE_KNIGHT_LEVEL_39_DROPS,
        "source": (
            f"{WHITE_KNIGHT_LEVEL_39_SOURCE_PATH}: id Npcs.WHITE_KNIGHT_3349; "
            "source attackBonus/strengthBonus mapped to melee attack/strength bonuses; "
            "main table declares total(128), active source slots sum to 127"
        ),
    },
    "white_knight_level_42": {
        "display_name": "White knight",
        "level": 42,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 520,
            "attack": 32,
            "strength": 29,
            "defence": 27,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 30,
            "attack_slash": 30,
            "attack_crush": 30,
            "defence_stab": 83,
            "defence_slash": 76,
            "defence_crush": 70,
            "defence_magic": -11,
            "defence_ranged": 74,
            "melee_strength": 31,
        },
        "drops": WHITE_KNIGHT_LEVEL_42_DROPS,
        "source": (
            f"{WHITE_KNIGHT_LEVEL_42_SOURCE_PATH}: id Npcs.WHITE_KNIGHT_3350; "
            "source attackBonus/strengthBonus mapped to melee attack/strength bonuses; "
            "main table declares total(128), active source slots sum to 127"
        ),
    },
    "barbarian": {
        "display_name": "Barbarian",
        "level": 8,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 140,
            "attack": 6,
            "strength": 5,
            "defence": 5,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 8,
            "attack_slash": 0,
            "attack_crush": 10,
            "defence_stab": 1,
            "defence_slash": 1,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze hatchet", "quantity": 1, "slots": 48},
                        {"item": "Staff", "quantity": 1, "slots": 32},
                        {"item": "Iron mace", "quantity": 1, "slots": 8},
                        {"item": "Chaos rune", "quantity": 2, "slots": 32},
                        {"item": "Bronze arrows", "quantity": 15, "slots": 24},
                        {"item": "Earth rune", "quantity": 2, "slots": 24},
                        {"item": "Fire rune", "quantity": 5, "slots": 16},
                        {"item": "Mind rune", "quantity": 5, "slots": 16},
                        {"item": "Law rune", "quantity": 2, "slots": 8},
                        {"item": "Coins", "quantity": 5, "slots": 341},
                        {"item": "Coins", "quantity": 8, "slots": 76},
                        {"item": "Coins", "quantity": 17, "slots": 45},
                        {"item": "Coins", "quantity": 27, "slots": 26},
                        {"slots": 288},
                        {"item": "Tin ore", "quantity": 1, "slots": 8},
                        {"item": "Bear fur", "quantity": 1, "slots": 8},
                        {"item": "Beer", "quantity": 1, "slots": 8},
                        {"item": "Cooked meat", "quantity": 1, "slots": 8},
                        {"item": "Ring mould", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 50},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 5},
                        {"item": "Blue charm", "quantity": 1, "slots": 5},
                        {"slots": 930},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_lvl_8.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_lvl_9.plugin.kts"
        ),
    },
    "barbarian_level_10": {
        "display_name": "Barbarian",
        "level": 10,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 180,
            "attack": 8,
            "strength": 7,
            "defence": 3,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 9,
            "attack_slash": 0,
            "attack_crush": 15,
            "defence_stab": 0,
            "defence_slash": 3,
            "defence_crush": 2,
            "defence_magic": -3,
            "defence_ranged": 2,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze hatchet", "quantity": 1, "slots": 48},
                        {"item": "Staff", "quantity": 1, "slots": 32},
                        {"item": "Iron mace", "quantity": 1, "slots": 8},
                        {"item": "Chaos rune", "quantity": 2, "slots": 32},
                        {"item": "Bronze arrows", "quantity": 15, "slots": 24},
                        {"item": "Earth rune", "quantity": 2, "slots": 24},
                        {"item": "Fire rune", "quantity": 5, "slots": 16},
                        {"item": "Mind rune", "quantity": 5, "slots": 16},
                        {"item": "Law rune", "quantity": 2, "slots": 8},
                        {"item": "Coins", "quantity": 5, "slots": 341},
                        {"item": "Coins", "quantity": 8, "slots": 76},
                        {"item": "Coins", "quantity": 17, "slots": 45},
                        {"item": "Coins", "quantity": 27, "slots": 26},
                        {"slots": 288},
                        {"item": "Tin ore", "quantity": 1, "slots": 8},
                        {"item": "Bear fur", "quantity": 1, "slots": 8},
                        {"item": "Beer", "quantity": 1, "slots": 8},
                        {"item": "Cooked meat", "quantity": 1, "slots": 8},
                        {"item": "Ring mould", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 50},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 5},
                        {"item": "Blue charm", "quantity": 1, "slots": 5},
                        {"slots": 930},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_greataxe_lvl_10.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_spear_lvl_10.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_twohand_sword_lvl_10.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_2hsword_lvl_10.plugin.kts"
        ),
    },
    "barbarian_level_17": {
        "display_name": "Barbarian",
        "level": 17,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 240,
            "attack": 15,
            "strength": 14,
            "defence": 10,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 9,
            "attack_slash": 0,
            "attack_crush": 15,
            "defence_stab": 0,
            "defence_slash": 3,
            "defence_crush": 2,
            "defence_magic": -3,
            "defence_ranged": 2,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze hatchet", "quantity": 1, "slots": 48},
                        {"item": "Staff", "quantity": 1, "slots": 32},
                        {"item": "Iron mace", "quantity": 1, "slots": 8},
                        {"item": "Chaos rune", "quantity": 2, "slots": 32},
                        {"item": "Bronze arrows", "quantity": 15, "slots": 24},
                        {"item": "Earth rune", "quantity": 2, "slots": 24},
                        {"item": "Fire rune", "quantity": 5, "slots": 16},
                        {"item": "Mind rune", "quantity": 5, "slots": 16},
                        {"item": "Law rune", "quantity": 2, "slots": 8},
                        {"item": "Coins", "quantity": 5, "slots": 341},
                        {"item": "Coins", "quantity": 8, "slots": 76},
                        {"item": "Coins", "quantity": 17, "slots": 45},
                        {"item": "Coins", "quantity": 27, "slots": 26},
                        {"slots": 288},
                        {"item": "Tin ore", "quantity": 1, "slots": 8},
                        {"item": "Bear fur", "quantity": 1, "slots": 8},
                        {"item": "Beer", "quantity": 1, "slots": 8},
                        {"item": "Cooked meat", "quantity": 1, "slots": 8},
                        {"item": "Ring mould", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 50},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 5},
                        {"item": "Blue charm", "quantity": 1, "slots": 5},
                        {"slots": 930},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_greataxe_lvl_17.plugin.kts: "
            "ids Npcs.BARBARIAN/Npcs.BARBARIAN_3248; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_spear_lvl_17.plugin.kts: "
            "id Npcs.BARBARIAN_3260; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_twohand_sword_lvl_17.plugin.kts: "
            "id Npcs.BARBARIAN_3249"
        ),
    },
    "seagull": {
        "display_name": "Seagull",
        "level": 2,
        "group": "Coastal",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 5.0,
        "stats": {
            "hitpoints": 60,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -47,
            "attack_slash": 0,
            "attack_crush": -42,
            "defence_stab": -42,
            "defence_slash": -42,
            "defence_crush": -42,
            "defence_magic": -42,
            "defence_ranged": -42,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/seagull_level_2.plugin.kts"
        ),
    },
    "al_kharid_warrior": {
        "display_name": "Al-Kharid warrior",
        "level": 9,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 190,
            "attack": 7,
            "strength": 5,
            "defence": 4,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 10,
            "attack_slash": 10,
            "attack_crush": 10,
            "defence_stab": 12,
            "defence_slash": 15,
            "defence_crush": 10,
            "defence_magic": -1,
            "defence_ranged": 12,
            "melee_strength": 9,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze med helm", "quantity": 1, "slots": 16},
                        {"item": "Iron dagger", "quantity": 1, "slots": 8},
                        {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 146},
                        {"item": "Bronze arrows", "quantity": 7, "slots": 24},
                        {"item": "Earth rune", "quantity": 4, "slots": 16},
                        {"item": "Fire rune", "quantity": 6, "slots": 16},
                        {"item": "Mind rune", "quantity": 9, "slots": 16},
                        {"item": "Chaos rune", "quantity": 2, "slots": 8},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 84},
                        {"item": "Coins", "quantity": 3, "slots": 204},
                        {"item": "Coins", "quantity": 10, "slots": 84},
                        {"item": "Coins", "quantity": 5, "slots": 72},
                        {"item": "Coins", "quantity": 15, "slots": 32},
                        {"item": "Coins", "quantity": 25, "slots": 8},
                        {"slots": 146},
                        {"slots": 64},
                        {"item": "Fishing bait", "quantity": 1, "slots": 40},
                        {"item": "Copper ore", "quantity": 1, "slots": 16},
                        {"item": "Earth talisman", "quantity": 1, "slots": 16},
                        {"item": "Cabbage", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 1024,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8},
                        {"slots": 1016},
                    ),
                },
            ),
        },
        "source": f"{ALKHARID_WARRIOR_SOURCE_PATH}: NPC_ID = Npcs.ALKHARID_WARRIOR",
    },
    "poison_scorpion": {
        "display_name": "Poison scorpion",
        "level": 20,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "poison_damage": 3,
        "slayer_xp": 23.0,
        "stats": {
            "hitpoints": 230,
            "attack": 16,
            "strength": 17,
            "defence": 15,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 15,
            "defence_crush": 15,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (), "tables": ()},
        "source": f"{POISON_SCORPION_SOURCE_PATH}: Npcs.POISON_SCORPION poisonDamage=3; no DropTableFactory registration",
    },
    "scorpion": {
        "display_name": "Scorpion",
        "level": 14,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 17.0,
        "stats": {
            "hitpoints": 170,
            "attack": 11,
            "strength": 12,
            "defence": 11,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 15,
            "defence_crush": 15,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": SCORPION_CHARM_DROPS,
        "source": SCORPION_LEVEL_14_SOURCE_PATH,
    },
    "king_scorpion": {
        "display_name": "King scorpion",
        "level": 32,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 37.0,
        "stats": {
            "hitpoints": 300,
            "attack": 30,
            "strength": 29,
            "defence": 23,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 15,
            "defence_crush": 15,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (), "tables": ()},
        "source": (
            f"{KING_SCORPION_SOURCE_PATH}: Npcs.KING_SCORPION; "
            "SlayerAssignment.SCORPION level 1 xp 37.0; no DropTableFactory registration; aggro radius 4"
        ),
    },
    "pit_scorpion": {
        "display_name": "Pit scorpion",
        "level": 28,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 32.0,
        "stats": {
            "hitpoints": 320,
            "attack": 20,
            "strength": 25,
            "defence": 28,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 13,
            "defence_crush": 13,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (), "tables": ()},
        "source": (
            f"{PIT_SCORPION_SOURCE_PATH}: Npcs.PIT_SCORPION; "
            "SlayerAssignment.SCORPION level 1 xp 32.0; no DropTableFactory registration; aggro radius 4"
        ),
    },
    "scorpion_level_59": {
        "display_name": "Scorpion",
        "level": 59,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 22,
        "slayer_xp": 55.0,
        "stats": {
            "hitpoints": 550,
            "attack": 50,
            "strength": 52,
            "defence": 50,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 15,
            "defence_crush": 15,
            "defence_magic": 0,
            "defence_ranged": 55,
            "melee_strength": 0,
        },
        "drops": SCORPION_CHARM_DROPS,
        "source": (
            f"{SCORPION_LEVEL_59_SOURCE_PATH}: ids Npcs.SCORPION_4402/Npcs.SCORPION_4403; "
            "SlayerAssignment.SCORPION level 1 xp 55.0; aggro radius 4"
        ),
    },
    "poison_spider": {
        "display_name": "Poison spider",
        "level": 31,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "poison_damage": 3,
        "slayer_xp": 25.0,
        "stats": {
            "hitpoints": 250,
            "attack": 28,
            "strength": 28,
            "defence": 28,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 20,
            "defence_slash": 17,
            "defence_crush": 10,
            "defence_magic": 14,
            "defence_ranged": 14,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (), "tables": ()},
        "source": f"{POISON_SPIDER_SOURCE_PATH}: Npcs.POISON_SPIDER_1009 poisonDamage=3; no DropTableFactory registration",
    },
    "poison_spider_level_64": {
        "display_name": "Poison spider",
        "level": 64,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "poison_damage": 6,
        "slayer_xp": 64.0,
        "stats": {
            "hitpoints": 640,
            "attack": 50,
            "strength": 58,
            "defence": 52,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 20,
            "defence_slash": 17,
            "defence_crush": 10,
            "defence_magic": 14,
            "defence_ranged": 14,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (), "tables": ()},
        "source": (
            f"{POISON_SPIDER_LEVEL_64_SOURCE_PATH}: Npcs.POISON_SPIDER poisonDamage=6; "
            "attackStyle STAB; no DropTableFactory registration; aggro radius 4"
        ),
    },
    "spider_level_24": {
        "display_name": "Spider",
        "level": 24,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 27,
        "slayer_xp": 22.0,
        "stats": {
            "hitpoints": 220,
            "attack": 21,
            "strength": 21,
            "defence": 21,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 53,
            "attack_slash": 0,
            "attack_crush": 53,
            "defence_stab": 53,
            "defence_slash": 53,
            "defence_crush": 53,
            "defence_magic": 53,
            "defence_ranged": 53,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 200,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 5},
                        {"item": "Green charm", "quantity": 1, "slots": 7},
                        {"item": "Crimson charm", "quantity": 1, "slots": 3},
                        {"item": "Blue charm", "quantity": 1, "slots": 2},
                        {"slots": 183},
                    ),
                },
            ),
        },
        "source": SPIDER_LEVEL_24_SOURCE_PATH,
    },
    "deadly_red_spider": {
        "display_name": "Deadly red spider",
        "level": 34,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 35.0,
        "stats": {
            "hitpoints": 350,
            "attack": 30,
            "strength": 25,
            "defence": 30,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 15,
            "defence_slash": 16,
            "defence_crush": 7,
            "defence_magic": 12,
            "defence_ranged": 16,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 260},
                        {"item": "Green charm", "quantity": 1, "slots": 11},
                        {"item": "Crimson charm", "quantity": 1, "slots": 20},
                        {"item": "Blue charm", "quantity": 1, "slots": 2},
                        {"slots": 707},
                    ),
                },
            ),
        },
        "source": DEADLY_RED_SPIDER_SOURCE_PATH,
    },
    "giant_spider_level_50": {
        "display_name": "Giant spider",
        "level": 50,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 50.0,
        "stats": {
            "hitpoints": 500,
            "attack": 41,
            "strength": 51,
            "defence": 31,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 10,
            "attack_slash": 0,
            "attack_crush": 10,
            "defence_stab": 10,
            "defence_slash": 10,
            "defence_crush": 10,
            "defence_magic": 10,
            "defence_ranged": 10,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 48,
                    "slots": (
                        {"item": "Air rune", "quantity_range": (4, 6), "slots": 7},
                        {"item": "Earth rune", "quantity": 4, "slots": 7},
                        {"item": "Fire rune", "quantity": 6, "slots": 7},
                        {"item": "Body rune", "quantity": 7, "slots": 3},
                        {"slots": 24},
                    ),
                },
                {
                    "name": "Secondary",
                    "total": 128,
                    "slots": (
                        {"item": "Bronze med helm", "quantity": 1, "slots": 48},
                        {"item": "Bronze bolts", "quantity": 1, "slots": 12},
                        {"item": "Bronze arrows", "quantity": 1, "slots": 12},
                        {"item": "Longbow", "quantity": 1, "slots": 4},
                        {"item": "Bronze kiteshield", "quantity": 1, "slots": 1},
                        {"slots": 51},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Staff of air", "quantity": 1, "slots": 1},
                        {"item": "Sling", "quantity": 1, "slots": 1},
                        {"slots": 126},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 90},
                        {"item": "Green charm", "quantity": 1, "slots": 11},
                        {"item": "Crimson charm", "quantity": 1, "slots": 30},
                        {"item": "Blue charm", "quantity": 1, "slots": 9},
                        {"slots": 860},
                    ),
                },
            ),
        },
        "source": GIANT_SPIDER_LEVEL_50_SOURCE_PATH,
    },
    "baby_dragon": {
        "display_name": "Baby dragon",
        "level": 48,
        "group": "Dragons",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 50.0,
        "stats": {'hitpoints': 500, 'attack': 40, 'strength': 40, 'defence': 40, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 30,
 'defence_slash': 50,
 'defence_crush': 50,
 'defence_magic': 40,
 'defence_ranged': 30,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Babydragon bones', 1),), 'tables': ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/dragons/baby_dragon_level_48.plugin.kts"
        ),
    },
    "baby_black_dragon": {
        "display_name": "Baby black dragon",
        "level": 83,
        "group": "Dragons",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 80.0,
        "stats": {'hitpoints': 800, 'attack': 70, 'strength': 70, 'defence': 70, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 30,
 'defence_slash': 50,
 'defence_crush': 50,
 'defence_magic': 40,
 'defence_ranged': 30,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Babydragon bones', 1),), 'tables': ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/dragons/baby_black_dragon_level_83.plugin.kts"
        ),
    },
    "lesser_demon": {
        "display_name": "Lesser demon",
        "level": 82,
        "group": "Demons",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 79.0,
        "stats": {'hitpoints': 790, 'attack': 68, 'strength': 70, 'defence': 71, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 0,
 'defence_slash': 0,
 'defence_crush': 0,
 'defence_magic': -10,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Accursed ashes', 1),),
 'tables': ({'name': 'Main',
             'total': 1024,
             'slots': ({'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 8},
                       {'item': 'Steel full helm', 'quantity': 1, 'slots': 42},
                       {'item': 'Steel hatchet', 'quantity': 1, 'slots': 42},
                       {'item': 'Steel scimitar', 'quantity': 1, 'slots': 24},
                       {'item': 'Mithril sq shield', 'quantity': 1, 'slots': 8},
                       {'item': 'Mithril chainbody', 'quantity': 1, 'slots': 8},
                       {'item': 'Rune med helm', 'quantity': 1, 'slots': 8},
                       {'item': 'Fire rune', 'quantity': 60, 'slots': 64},
                       {'item': 'Chaos rune', 'quantity': 12, 'slots': 46},
                       {'item': 'Death rune', 'quantity': 3, 'slots': 23},
                       {'item': 'Fire rune', 'quantity': 30, 'slots': 8},
                       {'item': 'Coins', 'quantity': 120, 'slots': 320},
                       {'item': 'Coins', 'quantity': 40, 'slots': 231},
                       {'item': 'Coins', 'quantity': 200, 'slots': 80},
                       {'item': 'Coins', 'quantity': 10, 'slots': 56},
                       {'item': 'Coins', 'quantity': 450, 'slots': 8},
                       {'item': 'Coins', 'quantity': 10, 'slots': 8},
                       {'item': 'Jug of wine', 'quantity': 1, 'slots': 24},
                       {'item': 'Gold ore', 'quantity': 1, 'slots': 16})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 8},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 30},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 7},
                       {'slots': 935})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/demons/lesser_demon_lvl_82.plugin.kts"
        ),
    },
    "greater_demon": {
        "display_name": "Greater demon",
        "level": 92,
        "group": "Demons",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "slayer_xp": 87.0,
        "stats": {'hitpoints': 870, 'attack': 76, 'strength': 78, 'defence': 81, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 0,
 'defence_slash': 0,
 'defence_crush': 0,
 'defence_magic': -10,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Accursed ashes', 1),),
 'tables': ({'name': 'Main',
             'total': 246,
             'slots': ({'item': 'Fire rune', 'quantity': 1, 'slots': 16},
                       {'item': 'Chaos rune', 'quantity': 15, 'slots': 6},
                       {'item': 'Death rune', 'quantity': 5, 'slots': 6},
                       {'item': 'Steel 2h sword', 'quantity': 1, 'slots': 8},
                       {'item': 'Steel hatchet', 'quantity': 1, 'slots': 6},
                       {'item': 'Steel battleaxe', 'quantity': 1, 'slots': 6},
                       {'item': 'Mithril kiteshield', 'quantity': 1, 'slots': 2},
                       {'item': 'Adamant platelegs', 'quantity': 1, 'slots': 2},
                       {'item': 'Rune full helm', 'quantity': 1, 'slots': 2},
                       {'item': 'Coins', 'quantity': 132, 'slots': 80},
                       {'item': 'Coins', 'quantity': 44, 'slots': 58},
                       {'item': 'Coins', 'quantity': 220, 'slots': 20},
                       {'item': 'Coins', 'quantity': 11, 'slots': 14},
                       {'item': 'Coins', 'quantity': 460, 'slots': 2},
                       {'item': 'Tuna', 'quantity': 1, 'slots': 6},
                       {'item': 'Gold bar', 'quantity': 1, 'slots': 4},
                       {'item': 'Thread', 'quantity': 10, 'slots': 4},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 10})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 70},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 40},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 260},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 10},
                       {'slots': 620})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/demons/greater_demon_level_92.plugin.kts"
        ),
    },
    "black_demon": {
        "display_name": "Black demon",
        "level": 172,
        "group": "Demons",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 157.0,
        "stats": {'hitpoints': 1570, 'attack': 145, 'strength': 148, 'defence': 152, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 0,
 'defence_slash': 0,
 'defence_crush': 0,
 'defence_magic': -10,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Infernal ashes', 1),),
 'tables': ({'name': 'Main',
             'total': 128,
             'slots': ({'item': 'Black sword', 'quantity': 1, 'slots': 4},
                       {'item': 'Steel battleaxe', 'quantity': 1, 'slots': 3},
                       {'item': 'Black hatchet', 'quantity': 1, 'slots': 2},
                       {'item': 'Mithril kiteshield', 'quantity': 1, 'slots': 1},
                       {'item': 'Rune med helm', 'quantity': 1, 'slots': 1},
                       {'item': 'Rune chainbody', 'quantity': 1, 'slots': 1},
                       {'item': 'Air rune', 'quantity': 50, 'slots': 8},
                       {'item': 'Chaos rune', 'quantity': 10, 'slots': 7},
                       {'item': 'Blood rune', 'quantity': 7, 'slots': 4},
                       {'item': 'Fire rune', 'quantity': 37, 'slots': 1},
                       {'item': 'Law rune', 'quantity': 3, 'slots': 1},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 23},
                       {'item': 'Coins', 'quantity': 132, 'slots': 40},
                       {'item': 'Coins', 'quantity': 30, 'slots': 7},
                       {'item': 'Coins', 'quantity': 44, 'slots': 6},
                       {'item': 'Coins', 'quantity': 220, 'slots': 6},
                       {'item': 'Coins', 'quantity': 460, 'slots': 1},
                       {'item': 'Lobster', 'quantity': 1, 'slots': 3},
                       {'item': 'Adamant bar', 'quantity': 1, 'slots': 2},
                       {'item': 'Defence potion (3)', 'quantity': 1, 'slots': 1},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 5})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 21},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 11},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 44},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 2},
                       {'slots': 922})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/demons/black_demon_lvl_172.plugin.kts"
        ),
    },
    "abyssal_demon": {
        "display_name": "Abyssal demon",
        "level": 124,
        "group": "Demons",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 3,
        "slayer_xp": 150.0,
        "stats": {'hitpoints': 1500, 'attack': 97, 'strength': 67, 'defence': 135, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 20,
 'defence_slash': 20,
 'defence_crush': 20,
 'defence_magic': 0,
 'defence_ranged': 20,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Infernal ashes', 1),),
 'tables': ({'name': 'Main',
             'total': 1024,
             'slots': ({'item': 'Black sword', 'quantity': 1, 'slots': 32},
                       {'item': 'Black hatchet', 'quantity': 1, 'slots': 16},
                       {'item': 'Steel battleaxe', 'quantity': 1, 'slots': 24},
                       {'item': 'Rune battleaxe', 'quantity': 1, 'slots': 8},
                       {'item': 'Rune 2h sword', 'quantity': 1, 'slots': 8},
                       {'item': 'Abyssal whip', 'quantity': 1, 'slots': 2},
                       {'item': 'Mithril kiteshield', 'quantity': 1, 'slots': 16},
                       {'item': 'Rune chainbody', 'quantity': 1, 'slots': 8},
                       {'item': 'Rune med helm', 'quantity': 1, 'slots': 8},
                       {'item': 'Rune sq shield', 'quantity': 1, 'slots': 8},
                       {'item': 'Dragon med helm', 'quantity': 1, 'slots': 16},
                       {'item': 'Air rune', 'quantity': 1, 'slots': 64},
                       {'item': 'Blood rune', 'quantity_choices': (7, 50), 'slots': 32},
                       {'item': 'Chaos rune', 'quantity': 1, 'slots': 56},
                       {'item': 'Law rune', 'quantity_choices': (3, 45), 'slots': 32},
                       {'item': 'Death rune', 'quantity': 1, 'slots': 8},
                       {'item': 'Nature rune', 'quantity_range': (61, 77), 'slots': 8},
                       {'item': 'Earth talisman', 'quantity': 1, 'slots': 41},
                       {'item': 'Cosmic talisman', 'quantity': 1, 'slots': 41},
                       {'item': 'Coins', 'quantity_choices': (9, 10, 486), 'slots': 41},
                       {'item': 'Lobster', 'quantity': 1, 'slots': 41},
                       {'item': 'Pure essence', 'quantity': 1, 'slots': 41},
                       {'item': 'Adamant bar', 'quantity': 1, 'slots': 32},
                       {'slots': 32},
                       {'item': 'Defence potion (3)', 'quantity': 1, 'slots': 32},
                       {'item': 'Rune bar', 'quantity': 1, 'slots': 2},
                       {'item': 'Dragonstone', 'quantity': 1, 'slots': 2},
                       {'item': 'Court summons', 'quantity': 1, 'slots': 8},
                       {'item': 'Clue scroll (hard)', 'quantity': 1, 'slots': 8},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 8},
                       {'item': 'Abyssal head', 'quantity': 1, 'slots': 2},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 152},
                       {'table': COMBAT_RARE_DROP_TABLE, 'slots': 16},
                       {'slots': 179})},)},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/demons/abyssal_demon_level_124.plugin.kts; "
            "Ferocious ring excluded outside Kuradal's Dungeon"
        ),
    },
    "nechryael": {
        "display_name": "Nechryael",
        "level": 115,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 59,
        "slayer_xp": 105.0,
        "stats": {'hitpoints': 1050, 'attack': 97, 'strength': 97, 'defence': 105, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 20,
 'defence_slash': 20,
 'defence_crush': 20,
 'defence_magic': 0,
 'defence_ranged': 20,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Infernal ashes', 1),),
 'tables': ({'name': 'Main',
             'total': 624,
             'slots': ({'item': 'Rune full helm', 'quantity': 1, 'slots': 16},
                       {'item': 'Adamant platelegs', 'quantity': 1, 'slots': 16},
                       {'item': 'Mithril kiteshield', 'quantity': 1, 'slots': 16},
                       {'item': 'Rune boots', 'quantity': 1, 'slots': 4},
                       {'item': 'Dragon med helm', 'quantity': 1, 'slots': 1},
                       {'item': 'Rune sq shield', 'quantity': 1, 'slots': 1},
                       {'item': 'Steel 2h sword', 'quantity': 1, 'slots': 64},
                       {'item': 'Steel battleaxe', 'quantity': 1, 'slots': 64},
                       {'item': 'Steel hatchet', 'quantity': 1, 'slots': 64},
                       {'item': 'Rune 2h sword', 'quantity': 1, 'slots': 4},
                       {'item': 'Steel arrows', 'quantity': 1, 'slots': 4},
                       {'item': 'Rune arrows', 'quantity': 1, 'slots': 1},
                       {'item': 'Rune longsword', 'quantity': 1, 'slots': 2},
                       {'item': 'Rune battleaxe', 'quantity': 1, 'slots': 2},
                       {'item': 'Death rune', 'quantity': 1, 'slots': 64},
                       {'item': 'Chaos rune', 'quantity': 1, 'slots': 16},
                       {'item': 'Law rune', 'quantity': 45, 'slots': 4},
                       {'item': 'Nature rune', 'quantity': 68, 'slots': 4},
                       {'table': COMBAT_UNCOMMON_SEED_DROP_TABLE, 'slots': 80},
                       {'item': 'Coins', 'quantity': 1, 'slots': 64},
                       {'item': 'Tuna', 'quantity': 1, 'slots': 64},
                       {'item': 'Thread', 'quantity': 10, 'slots': 16},
                       {'item': 'Gold bar', 'quantity': 1, 'slots': 16},
                       {'item': 'Rune bar', 'quantity': 1, 'slots': 4},
                       {'item': 'Court summons', 'quantity': 1, 'slots': 4},
                       {'item': 'Clue scroll (hard)', 'quantity': 1, 'slots': 4},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 4},
                       {'item': 'Silver ore', 'quantity': 100, 'slots': 1},
                       {'slots': 16})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 90},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 40},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 310},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 11},
                       {'slots': 549})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/demons/nechryael_lvl_115.plugin.kts"
        ),
    },
    "death_spawn": {
        "display_name": "Death spawn",
        "level": 46,
        "group": "Demons",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 0,
        "slayer_xp": 0.0,
        "stats": {'hitpoints': 600, 'attack': 67, 'strength': 7, 'defence': 30, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 20,
 'defence_slash': 20,
 'defence_crush': 20,
 'defence_magic': 0,
 'defence_ranged': 20,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Accursed ashes', 1),), 'tables': ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/demons/death_spawn_lvl_46.plugin.kts; "
            "RuneScape Wiki Death spawn oldid 6327456 (no Slayer level or XP)"
        ),
    },
    "hellhound": {
        "display_name": "Hellhound",
        "level": 122,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 89,
        "slayer_xp": 116.0,
        "stats": {'hitpoints': 1160, 'attack': 105, 'strength': 104, 'defence': 102, 'magic': 1, 'ranged': 1},
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
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 690},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 50},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 50},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 10},
                       {'slots': 200})},)},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/hellhound_level_122.plugin.kts"
        ),
    },
    "rock_crab": {
        "display_name": "Rock crab",
        "level": 13,
        "group": "Training staples",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 0,
        "slayer_xp": 51.0,
        "stats": {'hitpoints': 510, 'attack': 15, 'strength': 15, 'defence': 10, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 0,
 'defence_slash': 0,
 'defence_crush': 0,
 'defence_magic': 0,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (),
 'tables': ({'name': 'Main',
             'total': 128,
             'slots': ({'item': 'Empty oyster', 'quantity': 1, 'slots': 1},
                       {'item': 'Oyster pearl', 'quantity': 1, 'slots': 1},
                       {'item': 'Casket', 'quantity': 1, 'slots': 1},
                       {'item': 'Spinach roll', 'quantity': 1, 'slots': 1},
                       {'item': 'Seaweed', 'quantity': 1, 'slots': 1},
                       {'item': 'Edible seaweed', 'quantity': 1, 'slots': 1},
                       {'item': 'Opal bolt tips', 'quantity': 1, 'slots': 1},
                       {'item': 'Fishing bait', 'quantity': 1, 'slots': 1},
                       {'item': 'Empty oyster', 'quantity': 1, 'slots': 1},
                       {'item': 'Seaweed', 'quantity': 1, 'slots': 1},
                       {'item': 'Seaweed', 'quantity': 1, 'slots': 1},
                       {'item': 'Coins', 'quantity': 1, 'slots': 1},
                       {'item': 'Coins', 'quantity': 1, 'slots': 1},
                       {'item': 'Oyster', 'quantity': 1, 'slots': 1},
                       {'item': 'Oyster', 'quantity': 1, 'slots': 1},
                       {'item': 'Coins', 'quantity': 1, 'slots': 1})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 100},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 5},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 10},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 3},
                       {'slots': 882})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/rock_crab_lvl_13.plugin.kts"
        ),
    },
    "ghoul": {
        "display_name": "Ghoul",
        "level": 42,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 60,
        "slayer_xp": 50.0,
        "stats": {'hitpoints': 500, 'attack': 30, 'strength': 40, 'defence': 30, 'magic': 1, 'ranged': 1},
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
             'slots': ({'item': 'Law talisman', 'quantity': 1, 'slots': 16},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 1},
                       {'item': 'Death talisman', 'quantity': 1, 'slots': 16},
                       {'item': 'Blood tiara', 'quantity': 1, 'slots': 2})},)},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/undeads/ghoul_level_42.plugin.kts"
        ),
    },
    "werewolf": {
        "display_name": "Werewolf",
        "level": 88,
        "group": "Canifis",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 0,
        "slayer_xp": 100.0,
        "stats": {'hitpoints': 1000, 'attack': 70, 'strength': 70, 'defence': 70, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 0,
 'defence_slash': 0,
 'defence_crush': 0,
 'defence_magic': 60,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Wolf bones', 1),),
 'tables': ({'name': 'Main',
             'total': 128,
             'slots': ({'item': 'Raw chicken', 'quantity': 5, 'slots': 16},
                       {'item': 'Raw beef', 'quantity': 5, 'slots': 16},
                       {'item': 'Raw bear meat', 'quantity': 5, 'slots': 16},
                       {'item': 'Jug of wine', 'quantity': 1, 'slots': 16},
                       {'item': 'Steel scimitar', 'quantity': 1, 'slots': 16},
                       {'item': 'Steel hatchet', 'quantity': 1, 'slots': 16},
                       {'item': 'Steel arrow (p)', 'quantity': 5, 'slots': 4},
                       {'item': 'Steel arrows', 'quantity': 50, 'slots': 4},
                       {'item': 'Steel full helm', 'quantity': 1, 'slots': 4},
                       {'item': 'Mithril scimitar', 'quantity': 1, 'slots': 4},
                       {'item': 'Mithril sq shield', 'quantity': 1, 'slots': 4},
                       {'item': 'Rune med helm', 'quantity': 1, 'slots': 4},
                       {'item': 'Rune javelin', 'quantity': 1, 'slots': 1},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 3},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 3})},)},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/werewolf_level_88.plugin.kts"
        ),
    },
    "ice_warrior": {
        "display_name": "Ice warrior",
        "level": 57,
        "group": "Warriors",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 59.0,
        "stats": {'hitpoints': 590, 'attack': 47, 'strength': 47, 'defence': 47, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 30,
 'defence_slash': 40,
 'defence_crush': 20,
 'defence_magic': 10,
 'defence_ranged': 30,
 'melee_strength': 0},
        "drops": {'guaranteed': (),
 'tables': ({'name': 'Main',
             'total': 1024,
             'slots': ({'item': 'Iron battleaxe', 'quantity': 1, 'slots': 24},
                       {'item': 'Mithril mace', 'quantity': 1, 'slots': 8},
                       {'item': 'Nature rune', 'quantity': 4, 'slots': 80},
                       {'item': 'Chaos rune', 'quantity': 3, 'slots': 64},
                       {'item': 'Law rune', 'quantity': 2, 'slots': 56},
                       {'item': 'Cosmic rune', 'quantity': 2, 'slots': 40},
                       {'item': 'Mithril arrows', 'quantity': 3, 'slots': 40},
                       {'item': 'Adamant arrows', 'quantity': 2, 'slots': 16},
                       {'item': 'Death rune', 'quantity': 2, 'slots': 24},
                       {'item': 'Blood rune', 'quantity': 2, 'slots': 8},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 75},
                       {'table': COMBAT_ALLOTMENT_SEED_DROP_TABLE, 'slots': 125},
                       {'item': 'Coins', 'quantity': 15, 'slots': 224},
                       {'item': 'Coins', 'quantity': 5, 'slots': 104},
                       {'item': 'Coins', 'quantity': 10, 'slots': 62},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 24})},
            {'name': 'Tertiary',
             'total': 128,
             'slots': ({'item': 'Clue scroll (medium)', 'quantity': 1, 'slots': 1},)})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/ice_warrior_level_57.plugin.kts"
        ),
    },
    "earth_warrior": {
        "display_name": "Earth warrior",
        "level": 51,
        "group": "Warriors",
        "wilderness_risk": {
            "ambush_chance": 0.01,
            "max_hit": 250,
            "unskulled_items_kept": 3,
            "source_status": (
                "owner-approved bounded AnkiScape abstraction; PKer frequency "
                "was live-player behavior rather than source-static data"
            ),
        },
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 54.0,
        "stats": {'hitpoints': 540, 'attack': 42, 'strength': 42, 'defence': 42, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 30,
 'defence_slash': 40,
 'defence_crush': 20,
 'defence_magic': 10,
 'defence_ranged': 30,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Bones', 1),),
 'tables': ({'name': 'Main',
             'total': 128,
             'slots': ({'item': 'Steel spear', 'quantity': 1, 'slots': 3},
                       {'item': 'Staff of earth', 'quantity': 1, 'slots': 2},
                       {'item': 'Earth rune', 'quantity': 12, 'slots': 13},
                       {'item': 'Nature rune', 'quantity': 3, 'slots': 9},
                       {'item': 'Chaos rune', 'quantity': 3, 'slots': 7},
                       {'item': 'Law rune', 'quantity': 2, 'slots': 6},
                       {'item': 'Death rune', 'quantity': 2, 'slots': 4},
                       {'item': 'Blood rune', 'quantity': 2, 'slots': 3},
                       {'item': 'Earth rune', 'quantity': 2, 'slots': 1},
                       {'item': 'Coins', 'quantity': 12, 'slots': 18},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 14},
                       {'table': COMBAT_UNCOMMON_SEED_DROP_TABLE, 'slots': 18},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 2})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 90},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 50},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 110},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 7},
                       {'slots': 743})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/earth_warrior_level_51.plugin.kts"
        ),
    },
    "green_dragon": {
        "display_name": "Green dragon",
        "level": 79,
        "group": "Dragons",
        "wilderness_risk": {
            "ambush_chance": 0.01,
            "max_hit": 250,
            "unskulled_items_kept": 3,
            "source_status": (
                "owner-approved bounded AnkiScape abstraction; PKer frequency "
                "was live-player behavior rather than source-static data"
            ),
        },
        "dragonfire": {
            "chance_numerator": 1,
            "chance_denominator": 4,
            "unprotected_max_hit": 500,
            "partial_max_hit": 50,
            "shield_items": ("Anti-dragon shield", "Dragonfire shield"),
            "source": (
                f"{LEATHER_DRAGON_COMBAT_SOURCE_PATH}:45-60; "
                f"{DRAGONFIRE_FORMULA_SOURCE_PATH}:878-908"
            ),
            "source_status": (
                "provisional/darkan hidden attack-selection roll; damage and "
                "protection tiers corroborated by Green dragon oldid=6565810 "
                "and Dragonfire oldid=6534496"
            ),
        },
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 85,
        "slayer_xp": 75.0,
        "stats": {
            "hitpoints": 750,
            "attack": 68,
            "strength": 68,
            "defence": 68,
            "magic": 68,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 20,
            "defence_slash": 40,
            "defence_crush": 40,
            "defence_magic": 30,
            "defence_ranged": 20,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Dragon bones", 1), ("Green dragonhide", 1)),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Steel platelegs", "quantity": 1, "slots": 32},
                        {"item": "Steel battleaxe", "quantity": 1, "slots": 24},
                        {"item": "Mithril hatchet", "quantity": 1, "slots": 24},
                        {"item": "Mithril spear", "quantity": 1, "slots": 16},
                        {"item": "Mithril kiteshield", "quantity": 1, "slots": 8},
                        {"item": "Adamant full helm", "quantity": 1, "slots": 8},
                        {"item": "Rune dagger", "quantity": 1, "slots": 8},
                        {"item": "Water rune", "quantity": 75, "slots": 64},
                        {"item": "Nature rune", "quantity": 15, "slots": 40},
                        {"item": "Law rune", "quantity": 3, "slots": 24},
                        {"item": "Fire rune", "quantity": 37, "slots": 8},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 120},
                        {"item": "Coins", "quantity": 44, "slots": 232},
                        {"item": "Coins", "quantity": 132, "slots": 200},
                        {"item": "Coins", "quantity": 200, "slots": 80},
                        {"item": "Coins", "quantity": 11, "slots": 40},
                        {"item": "Coins", "quantity": 440, "slots": 8},
                        {"item": "Bass", "quantity": 1, "slots": 24},
                        {"item": "Adamantite ore", "quantity": 1, "slots": 24},
                        {"slots": 5},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 40},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (hard)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/dragons/green_dragon_level_79.plugin.kts; "
            f"{LEATHER_DRAGON_COMBAT_SOURCE_PATH}"
        ),
    },
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
    "killerwatt": {
        "display_name": "Killerwatt",
        "level": 71,
        "group": "Slayer",
        "required_slayer_level": 37,
        "quest_gate": "ernest_the_chicken",
        "quest_gate_label": "Complete Ernest the Chicken",
        "attack_style": "magic_melee",
        "attack_style_by_player_class": {
            "melee": "magic_melee",
            "ranged": "ranged",
            "magic": "ranged",
        },
        "attack_speed": 8,
        "respawn_delay": 59,
        "max_hit": 64,
        "slayer_xp": 51.0,
        "stats": {
            "hitpoints": 510,
            "attack": 50,
            "strength": 50,
            "defence": 40,
            "magic": 67,
            "ranged": 67,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 10,
            "defence_slash": 10,
            "defence_crush": 10,
            "defence_magic": 20,
            "defence_ranged": 20,
            "melee_strength": 0,
        },
        "protective_equipment": {
            "slot": "feet",
            "items": ("Insulated boots",),
            "warning": (
                "Missing Insulated boots: Killerwatt Plane thunderclouds add "
                "0–140 LP damage to each incoming attack."
            ),
            "unprotected_effect": {
                "damage": {"kind": "uniform_max", "max": 140},
                "additive_to_attack": True,
            },
            "source_status": (
                "period-exact equipment consequence and 140-LP maximum; one "
                "additive cloud roll per incoming attack is the bounded "
                "review-native cadence abstraction"
            ),
        },
        "drops": {
            "guaranteed": (("Impious ashes", 1),),
            "tables": (
                {
                    "name": "Darkan main",
                    "total": 100000,
                    "slots": (
                        {"item": "Grimy guam", "quantity": 1, "slots": 12016},
                        {"item": "Grimy marrentill", "quantity": 1, "slots": 12016},
                        {"item": "Grimy tarromin", "quantity": 1, "slots": 12016},
                        {"item": "Grimy harralander", "quantity": 1, "slots": 12016},
                        {
                            "item": "Fire rune",
                            "quantity_range": (18, 45),
                            "slots": 12016,
                        },
                        {
                            "item": "Air rune",
                            "quantity_range": (5, 17),
                            "slots": 12016,
                        },
                        {
                            "item": "Coins",
                            "quantity_range": (11, 200),
                            "slots": 12016,
                        },
                        {"item": "Cannonball", "quantity": 3, "slots": 876},
                        {"item": "Grimy ranarr", "quantity": 1, "slots": 876},
                        {"item": "Grimy irit", "quantity": 1, "slots": 876},
                        {"item": "Grimy avantoe", "quantity": 1, "slots": 876},
                        {"item": "Grimy kwuarm", "quantity": 1, "slots": 876},
                        {"item": "Grimy cadantine", "quantity": 1, "slots": 876},
                        {
                            "item": "Nature rune",
                            "quantity_range": (4, 37),
                            "slots": 876,
                        },
                        {"item": "Chaos rune", "quantity": 4, "slots": 876},
                        {"item": "Fire orb", "quantity": 2, "slots": 876},
                        {"item": "Staff of air", "quantity": 1, "slots": 876},
                        {"item": "Staff of fire", "quantity": 1, "slots": 876},
                        {"item": "Fire battlestaff", "quantity": 1, "slots": 876},
                        {"item": "Air battlestaff", "quantity": 1, "slots": 876},
                        {"item": "Mystic fire staff", "quantity": 1, "slots": 876},
                        {"item": "Soda ash", "quantity": 4, "slots": 876},
                        {"item": "Steam rune", "quantity": 2, "slots": 876},
                        {"item": "Grimy dwarf weed", "quantity": 1, "slots": 623},
                        {"item": "Death rune", "quantity": 2, "slots": 623},
                        {"item": "Grimy lantadyme", "quantity": 1, "slots": 623},
                        {"slots": 3},
                    ),
                },
                {
                    "name": "Darkan charms",
                    "total": 303,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 41},
                        {"item": "Green charm", "quantity": 1, "slots": 2},
                        {"item": "Crimson charm", "quantity": 1, "slots": 2},
                        {"slots": 258},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Killerwatt?oldid=6469837; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "killerwatt (noanims).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/developer-information/npcListBonuses.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/killerwatt.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java"
        ),
        "source_status": (
            "period exact identity, LP, Slayer/quest gates, Slayer XP, "
            "eight-tick magical-melee/ranged styles, maximum hit, guaranteed "
            "ashes, and uninsulated 140-LP cloud maximum; Darkan exact stats, "
            "bonuses, respawn, one 100,000-slot ordinary selector, and "
            "emulator-exact 303-slot charm selector"
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
    "ogre": {
        "display_name": "Ogre",
        "level": 53,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 59,
        "max_hit": 73,
        "slayer_xp": 60.0,
        "stats": {
            "hitpoints": 600,
            "attack": 43,
            "strength": 43,
            "defence": 43,
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
        "drops": OGRE_DROPS,
        "source": (
            "https://runescape.wiki/w/Ogre?oldid=6565807; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/ogre/"
            "ogre_(53).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/ogre.json"
        ),
        "source_status": (
            "period exact ordinary level-53 identity, LP, maximum hit, attack "
            "speed, Slayer XP, and guaranteed Big bones; Darkan exact "
            "stats, respawn, 19/128 common-seed roll, and independent long/"
            "curved-bone tertiary rolls; level-58 God Wars and level-63 Combat "
            "Training Camp variants excluded"
        ),
    },
    "jackal": {
        "display_name": "Jackal",
        "level": 21,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 59,
        "max_hit": 80,
        "slayer_xp": 27.0,
        "stats": {
            "hitpoints": 270,
            "attack": 17,
            "strength": 18,
            "defence": 15,
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
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            "https://runescape.wiki/w/Jackal?oldid=6493724; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/jackal.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/drops/jackal.json"
        ),
    },
    "icefiend": {
        "display_name": "Icefiend",
        "level": 13,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "max_hit": 20,
        "slayer_xp": 15.0,
        "stats": {
            "hitpoints": 150,
            "attack": 10,
            "strength": 10,
            "defence": 12,
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
            "guaranteed": (("Impious ashes", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Water talisman", "quantity": 1, "slots": 8},
                        {"item": "Bronze sword", "quantity": 1, "slots": 4},
                        {"item": "Bronze hatchet", "quantity": 1, "slots": 4},
                        {"item": "Iron hatchet", "quantity": 1, "slots": 4},
                        {"item": "Bronze pickaxe", "quantity": 1, "slots": 4},
                        {"item": "Iron pickaxe", "quantity": 1, "slots": 4},
                        {"item": "Bronze arrows", "quantity_range": (2, 9), "slots": 4},
                        {"item": "Iron arrows", "quantity_range": (1, 5), "slots": 4},
                        {"item": "Steel arrows", "quantity": 1, "slots": 4},
                        {"item": "Bronze bolts", "quantity_range": (1, 10), "slots": 4},
                        {"item": "Bronze med helm", "quantity": 1, "slots": 4},
                        {"item": "Bronze full helm", "quantity": 1, "slots": 4},
                        {"item": "Iron chainbody", "quantity": 1, "slots": 4},
                        {"item": "Silver ore", "quantity": 1, "slots": 4},
                        {"item": "Silver bar", "quantity": 1, "slots": 4},
                        {"item": "Steel med helm", "quantity": 1, "slots": 2},
                        {"item": "Jug of wine", "quantity": 1, "slots": 2},
                        {"item": "Steel hatchet", "quantity": 1, "slots": 1},
                        {"item": "Steel pickaxe", "quantity": 1, "slots": 1},
                        {"item": "Staff of air", "quantity": 1, "slots": 1},
                        {"item": "Staff of water", "quantity": 1, "slots": 1},
                        {"item": "Dwarven stout", "quantity": 1, "slots": 1},
                        {"item": "Cake", "quantity": 1, "slots": 1},
                        {"item": "Beer", "quantity": 1, "slots": 1},
                        {"item": "Chaos rune", "quantity_range": (1, 6), "slots": 1},
                        {"item": "Death rune", "quantity_range": (1, 2), "slots": 1},
                        {"slots": 51},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Icefiend?oldid=6419875; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/demons/icefiend_level_13.plugin.kts; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/icefiend/icefiend_(13).json"
        ),
    },
    "pyrefiend": {
        "display_name": "Pyrefiend",
        "level": 43,
        "group": "Slayer",
        "required_slayer_level": 30,
        "attack_style": "magic_melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "max_hit": 44,
        "slayer_xp": 45.0,
        "stats": {
            "hitpoints": 450,
            "attack": 52,
            "strength": 30,
            "defence": 22,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 10,
            "defence_slash": 10,
            "defence_crush": 10,
            "defence_magic": 0,
            "defence_ranged": 10,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Impious ashes", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Steel hatchet", "quantity": 1, "slots": 4},
                        {"item": "Steel full helm", "quantity": 1, "slots": 4},
                        {"item": "Mithril chainbody", "quantity": 1, "slots": 2},
                        {"item": "Staff of fire", "quantity": 1, "slots": 3},
                        {"item": "Steel boots", "quantity": 1, "slots": 1},
                        {"item": "Adamant med helm", "quantity": 1, "slots": 1},
                        {"item": "Fire rune", "quantity": 30, "slots": 21},
                        {"item": "Fire rune", "quantity": 60, "slots": 8},
                        {"item": "Chaos rune", "quantity": 12, "slots": 5},
                        {"item": "Death rune", "quantity": 3, "slots": 3},
                        {"item": "Coins", "quantity": 10, "slots": 7},
                        {"item": "Coins", "quantity": 40, "slots": 24},
                        {"item": "Coins", "quantity": 120, "slots": 20},
                        {"item": "Coins", "quantity": 200, "slots": 10},
                        {"item": "Coins", "quantity": 450, "slots": 2},
                        {"item": "Gold ore", "quantity": 1, "slots": 8},
                        {"item": "Jug of wine", "quantity": 1, "slots": 2},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 3},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Pyrefiend?oldid=6565806; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/demons/pyrefiend_lvl_43.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/"
            "combat/formula/MeleeCombatFormula.kt"
        ),
        "source_status": (
            "period ordinary level-43 identity, LP, maximum hit, Slayer gate/XP, "
            "magic-based melee semantics, and guaranteed ash; game-main exact "
            "stats, speeds, bonuses, and 128-slot drops; level-48 God Wars, Soul "
            "Wars, Daemonheim, revenant, and familiar variants excluded"
        ),
    },
    "jelly": {
        "display_name": "Jelly",
        "level": 78,
        "group": "Slayer",
        "required_slayer_level": 52,
        "attack_style": "magic_melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 60,
        "slayer_xp": 75.0,
        "stats": {
            "hitpoints": 750,
            "attack": 45,
            "strength": 45,
            "defence": 120,
            "magic": 45,
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
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Coins", "quantity": 102, "slots": 39},
                        {"item": "Coins", "quantity": 44, "slots": 30},
                        {"item": "Steel battleaxe", "quantity": 1, "slots": 11},
                        {"item": "Coins", "quantity": 220, "slots": 10},
                        {"item": "Steel 2h sword", "quantity": 1, "slots": 7},
                        {"item": "Coins", "quantity": 11, "slots": 7},
                        {"item": "Chaos rune", "quantity": 15, "slots": 5},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 4},
                        {"item": "Steel hatchet", "quantity": 1, "slots": 3},
                        {"item": "Death rune", "quantity": 5, "slots": 3},
                        {"item": "Mithril kiteshield", "quantity": 1, "slots": 2},
                        {"item": "Coins", "quantity": 460, "slots": 2},
                        {"item": "Gold bar", "quantity": 1, "slots": 2},
                        {"item": "Mithril boots", "quantity": 1, "slots": 1},
                        {"item": "Rune full helm", "quantity": 1, "slots": 1},
                        {"item": "Thread", "quantity": 10, "slots": 1},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Jelly?oldid=6530513; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/jelly.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/jelly.json"
        ),
        "source_status": (
            "period exact ordinary level, LP, Slayer gate/XP, attack speed, "
            "magic-based melee semantics, and no guaranteed outside-Soul-Wars "
            "drop; Darkan exact stats, respawn, approximate-period max hit, and "
            "complete 128-slot ordinary drop table; Soul Wars variant excluded"
        ),
    },
    "bloodveld": {
        "display_name": "Bloodveld",
        "level": 76,
        "group": "Slayer",
        "required_slayer_level": 50,
        "attack_style": "magic_melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 59,
        "slayer_xp": 120.0,
        "stats": {
            "hitpoints": 1200,
            "attack": 75,
            "strength": 45,
            "defence": 30,
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
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Coins", "quantity": 120, "slots": 20},
                        {"item": "Coins", "quantity": 40, "slots": 29},
                        {"item": "Coins", "quantity": 200, "slots": 10},
                        {"item": "Bones", "quantity": 1, "slots": 10},
                        {"item": "Fire rune", "quantity": 60, "slots": 8},
                        {"item": "Coins", "quantity": 10, "slots": 7},
                        {"item": "Big bones", "quantity": 1, "slots": 7},
                        {"item": "Blood rune", "quantity": 10, "slots": 5},
                        {"item": "Steel hatchet", "quantity": 1, "slots": 4},
                        {"item": "Steel full helm", "quantity": 1, "slots": 4},
                        {"item": "Blood rune", "quantity": 3, "slots": 3},
                        {"item": "Big bones", "quantity": 3, "slots": 3},
                        {"item": "Meat pizza", "quantity": 1, "slots": 3},
                        {"item": "Steel scimitar", "quantity": 1, "slots": 2},
                        {"item": "Gold ore", "quantity": 1, "slots": 2},
                        {"item": "Black boots", "quantity": 1, "slots": 1},
                        {"item": "Mithril sq shield", "quantity": 1, "slots": 1},
                        {"item": "Mithril chainbody", "quantity": 1, "slots": 1},
                        {"item": "Rune med helm", "quantity": 1, "slots": 1},
                        {"item": "Blood rune", "quantity": 30, "slots": 1},
                        {"item": "Coins", "quantity": 450, "slots": 1},
                        {"slots": 5},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Bloodveld?oldid=6565794; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/bloodveld/"
            "bloodveld_(76).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/bloodveld.json"
        ),
        "source_status": (
            "period exact ordinary level-76 identity, LP, Slayer gate/XP, "
            "six-tick magic-based melee, maximum hit, and guaranteed Bones; "
            "Darkan exact stats, respawn, and complete 128-slot ordinary table; "
            "level-81 God Wars variant excluded"
        ),
    },
    "infernal_mage": {
        "display_name": "Infernal Mage",
        "level": 66,
        "group": "Slayer",
        "required_slayer_level": 45,
        "attack_style": "magic",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 89,
        "slayer_xp": 60.0,
        "stats": {
            "hitpoints": 600,
            "attack": 1,
            "strength": 1,
            "defence": 60,
            "magic": 75,
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
                        {"item": "Coins", "quantity": 1, "slots": 9500},
                        {"item": "Death rune", "quantity": 7, "slots": 9000},
                        {"item": "Coins", "quantity": 2, "slots": 7000},
                        {"item": "Staff", "quantity": 1, "slots": 4000},
                        {"item": "Coins", "quantity": 4, "slots": 4000},
                        {"item": "Earth rune", "quantity": 10, "slots": 3000},
                        {"item": "Fire rune", "quantity": 10, "slots": 3000},
                        {"item": "Earth rune", "quantity": 36, "slots": 2000},
                        {"item": "Air rune", "quantity": 10, "slots": 1500},
                        {"item": "Water rune", "quantity": 10, "slots": 1500},
                        {"item": "Coins", "quantity": 29, "slots": 1500},
                        {"item": "Air rune", "quantity": 18, "slots": 1000},
                        {"item": "Water rune", "quantity": 18, "slots": 1000},
                        {"item": "Earth rune", "quantity": 18, "slots": 1000},
                        {"item": "Fire rune", "quantity": 18, "slots": 1000},
                        {"item": "Mind rune", "quantity": 18, "slots": 1000},
                        {"item": "Body rune", "quantity": 18, "slots": 1000},
                        {"item": "Blood rune", "quantity": 4, "slots": 1000},
                        {"item": "Staff of fire", "quantity": 1, "slots": 500},
                        {
                            "item": "Mystic boots (dark)",
                            "quantity": 1,
                            "slots": 125,
                        },
                        {
                            "item": "Mystic hat (dark)",
                            "quantity": 1,
                            "slots": 125,
                        },
                        {"item": "Lava battlestaff", "quantity": 1, "slots": 64},
                        {"slots": 10186},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Infernal_Mage?oldid=6446423; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "infernal_mage.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/infernal_mage.json"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer gate/XP, six-tick Magic "
            "attack, maximum hit, and guaranteed Bones; Darkan exact stats, "
            "respawn, and one exact 64,000-slot ordinary selector including the "
            "dark-mystic and Lava battlestaff rows; charm distribution remains "
            "source_blocked"
        ),
    },
    "dust_devil": {
        "display_name": "Dust devil",
        "level": 93,
        "group": "Slayer",
        "required_slayer_level": 65,
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 90,
        "slayer_xp": 105.0,
        "stats": {
            "hitpoints": 1050,
            "attack": 105,
            "strength": 70,
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
        "start_equipment": {
            "slot": "head",
            "items": (
                "Face mask",
                "Masked earmuffs",
                "Slayer helmet",
                "Slayer helmet (charged)",
                "Slayer helmet (e)",
                "Full slayer helmet",
                "Full slayer helmet (charged)",
                "Full slayer helmet (e)",
            ),
            "persistent": True,
            "warning": (
                "Equip a Face mask, Masked earmuffs, or a Slayer helmet "
                "to damage Dust devils"
            ),
            "source_status": (
                "period-exact continuous damage gate; the cutoff page says "
                "unprotected players cannot damage Dust devils"
            ),
        },
        "drops": DUST_DEVIL_DROPS,
        "source": (
            "https://runescape.wiki/w/Dust_devil?oldid=6529409; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/content/skills/"
            "slayer/npcs/combat/DustDevil.java; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "dust_devil.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/dust_devil.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer gate/XP, six-tick "
            "melee, maximum hit, continuous protective-headgear damage gate, "
            "and guaranteed Bones; Darkan exact stats, respawn, one exact "
            "32,768-slot ordinary selector with nested herb/gem tables, and "
            "an emulator-exact charm selector; familiar-only Ranged attacks "
            "have no player-combat effect; defensive bonuses are source_blocked"
        ),
    },
    "aberrant_spectre": {
        "display_name": "Aberrant spectre",
        "level": 96,
        "group": "Slayer",
        "required_slayer_level": 60,
        "quest_gate": "priest_in_peril",
        "quest_gate_label": "Complete Priest in Peril",
        "attack_style": "magic",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 119,
        "slayer_xp": 90.0,
        "protective_equipment": {
            "slot": "head",
            "items": (
                "Nose peg",
                "Slayer helmet",
                "Slayer helmet (charged)",
                "Slayer helmet (e)",
                "Full slayer helmet",
                "Full slayer helmet (charged)",
                "Full slayer helmet (e)",
            ),
            "warning": (
                "Missing Nose peg or a Slayer helmet in the head slot: "
                "Aberrant spectre stench deals fixed damage and drains one "
                "combat stat unless Protect from Magic is active."
            ),
            "unprotected_effect": {
                "damage": {
                    "kind": "max_lifepoints_fraction_capped",
                    "numerator": 1,
                    "denominator": 10,
                    "cap": 160,
                },
                "stat_drain_protection_prayer": "protect_magic",
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
                "period exact protective headgear and unavoidable 160-LP "
                "unprotected maximum; Darkan exact max-LP/10 damage, random "
                "five-level combat-stat drain, and Protect from Magic drain block"
            ),
        },
        "stats": {
            "hitpoints": 900,
            "attack": 1,
            "strength": 1,
            "defence": 90,
            "magic": 105,
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
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 512,
                    "slots": (
                        {
                            "table": DARKAN_HERB_DROP_TABLE,
                            "slots": 312,
                        },
                        {
                            "table": DARKAN_ABERRANT_RARE_SEED_DROP_TABLE,
                            "slots": 76,
                        },
                        {
                            "table": DARKAN_GEM_DROP_TABLE,
                            "slots": 20,
                        },
                        {"item": "Steel hatchet", "quantity": 1, "slots": 12},
                        {
                            "item": "Mithril kiteshield",
                            "quantity": 1,
                            "slots": 4,
                        },
                        {"item": "Lava battlestaff", "quantity": 1, "slots": 4},
                        {"item": "Adamant platelegs", "quantity": 1, "slots": 4},
                        {"item": "Rune full helm", "quantity": 1, "slots": 4},
                        {"item": "Coins", "quantity": 460, "slots": 4},
                        {
                            "item": "Mystic robe bottom (dark)",
                            "quantity": 1,
                            "slots": 1,
                        },
                        {"slots": 71},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1212,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 97},
                        {"item": "Green charm", "quantity": 1, "slots": 25},
                        {"item": "Crimson charm", "quantity": 1, "slots": 15},
                        {"item": "Blue charm", "quantity": 1, "slots": 19},
                        {"slots": 1056},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Aberrant_spectre?oldid=6555339; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/content/skills/"
            "slayer/npcs/combat/AberrantSpectre.java; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "aberrant_spectre.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/aberrant_spectre.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java"
        ),
        "source_status": (
            "period exact ordinary identity, access, LP, Slayer gate/XP, "
            "six-tick Magic attack, protected and unprotected maximum hits, "
            "and protective-headgear behavior; Darkan exact stats, respawn, "
            "exact 512-slot ordinary selector and nested herb/seed/gem tables, "
            "and derived exact charm selector; zero defensive bonuses are "
            "source_blocked pending cutoff-era cache evidence"
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
    "crocodile": {
        "display_name": "Crocodile",
        "level": 63,
        "group": "Slayer",
        "required_slayer_level": 10,
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 59,
        "max_hit": 67,
        "slayer_xp": 62.0,
        "desert_context": True,
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
                "period-exact ordinary River Elid heat/water requirement and "
                "dose preservation; one dose per damaging Combat review is the "
                "existing bounded review-native desert abstraction"
            ),
        },
        "stats": {
            "hitpoints": 630,
            "attack": 53,
            "strength": 54,
            "defence": 54,
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
            "tables": (),
        },
        "source": (
            "https://runescape.wiki/w/Crocodile?oldid=6529105; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/crocodile/"
            "crocodile_(63).json"
        ),
        "source_status": (
            "period exact level-63 River Elid identity, LP, Slayer gate/XP, "
            "five-tick melee, 67-LP maximum hit, guaranteed Bones, no other "
            "drops, and desert heat; Darkan exact stats and respawn; level-89 "
            "marsh variant and Darkan's merged Big-bones row excluded"
        ),
    },
    "otherworldly_being": {
        "display_name": "Otherworldly being",
        "level": 64,
        "group": "Slayer",
        "required_slayer_level": 1,
        "quest_gate": "lost_city",
        "quest_gate_label": "Complete Lost City",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 70,
        "slayer_xp": 66.0,
        "stats": {
            "hitpoints": 660,
            "attack": 56,
            "strength": 56,
            "defence": 46,
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
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Coins", "quantity": 15, "slots": 59},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 10},
                        {"item": "Nature rune", "quantity": 5, "slots": 9},
                        {"item": "Chaos rune", "quantity": 4, "slots": 8},
                        {"item": "Law rune", "quantity": 2, "slots": 7},
                        {"item": "Cosmic rune", "quantity": 2, "slots": 5},
                        {"item": "Death rune", "quantity": 2, "slots": 4},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 3},
                        {"item": "Ruby ring", "quantity": 1, "slots": 2},
                        {"item": "Blood rune", "quantity": 2, "slots": 1},
                        {"item": "Rune mace", "quantity": 1, "slots": 1},
                        {"item": "Mackerel", "quantity": 1, "slots": 1},
                        {"slots": 18},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Otherworldly_being?oldid=6554205; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/areas/zanaris/"
            "otherworldly_being.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/otherworldly_being.json"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer XP, six-tick melee, "
            "70-LP maximum hit, Vannaka membership, and Zanaris route; Darkan "
            "exact stats, respawn, and complete 128-slot ordinary table"
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
    "shadow_warrior": {
        "display_name": "Shadow warrior",
        "level": 48,
        "group": "Slayer",
        "required_slayer_level": 1,
        "quest_gate": "legends_quest",
        "quest_gate_label": "Complete Legends' Quest",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 65,
        "slayer_xp": 67.0,
        "stats": {
            "hitpoints": 670,
            "attack": 36,
            "strength": 36,
            "defence": 33,
            "magic": 0,
            "ranged": 0,
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
        "drops": SHADOW_WARRIOR_DROPS,
        "source": (
            "https://runescape.wiki/w/Shadow_warrior?oldid=6555920; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "shadow_warrior (noanims).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/shadow_warrior.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/charmDrops.txt; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/tools/old/CharmDrop.java"
        ),
        "source_status": (
            "period exact ordinary identity, LP, Slayer XP, six-tick melee, "
            "65-LP maximum hit, Vannaka/Chaeldar membership, Legends' Guild "
            "route, and no guaranteed drop; Darkan exact stats, respawn, one "
            "128-slot ordinary selector, and emulator-exact charm selection"
        ),
    },
    "kalphite_soldier": {
        "display_name": "Kalphite Soldier",
        "level": 85,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 80,
        "poison_damage": 5,
        "slayer_xp": 90.0,
        "stats": {
            "hitpoints": 900,
            "attack": 70,
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
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Coins", "quantity": 120, "slots": 40},
                        {"item": "Coins", "quantity": 40, "slots": 29},
                        {"item": "Coins", "quantity": 200, "slots": 10},
                        {"item": "Fire rune", "quantity": 60, "slots": 8},
                        {"item": "Coins", "quantity": 10, "slots": 7},
                        {"item": "Chaos rune", "quantity": 12, "slots": 5},
                        {"item": "Steel full helm", "quantity": 1, "slots": 4},
                        {"item": "Steel hatchet", "quantity": 1, "slots": 4},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 4},
                        {"item": "Steel scimitar", "quantity": 1, "slots": 3},
                        {"item": "Death rune", "quantity": 3, "slots": 3},
                        {"item": "Waterskin (4)", "quantity": 1, "slots": 3},
                        {"item": "Nature rune", "quantity": 1, "slots": 2},
                        {"item": "Rune chainbody", "quantity": 1, "slots": 1},
                        {"item": "Mithril sq shield", "quantity": 1, "slots": 1},
                        {"item": "Adamant med helm", "quantity": 1, "slots": 1},
                        {"item": "Fire rune", "quantity": 30, "slots": 1},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 1},
                        {"item": "Coins", "quantity": 450, "slots": 1},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Kalphite_Soldier?oldid=6565809; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/"
            "kalphite_soldier.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/kalphite_soldier.json"
        ),
        "source_status": (
            "period ordinary level-85 identity, LP, maximum hit, attack speed, "
            "Slayer XP, 48-LP initial poison, stab-style melee, assignment "
            "membership, and no guaranteed drop; nearest representable 50-LP "
            "poison abstraction; Darkan exact stats, respawn, and 128-slot "
            "drops; worker, guardian, and queen variants excluded"
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
    "vampyre": {
        "display_name": "Vampyre",
        "level": 61,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 59,
        "max_hit": 74,
        "slayer_xp": 40.0,
        "quest_gate": "priest_in_peril",
        "quest_gate_label": "Complete Priest in Peril",
        "stats": {
            "hitpoints": 400,
            "attack": 55,
            "strength": 60,
            "defence": 55,
            "magic": 0,
            "ranged": 0,
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
        "weakening_equipment": {
            "slot": "neck",
            "items": ("Holy symbol",),
            "display_name": "Holy symbol",
            "enemy_accuracy_multiplier": 0.8,
            "enemy_damage_multiplier": 0.8,
            "source_status": (
                "period-authentic Holy symbol weakness; 20% enemy accuracy and "
                "maximum-hit reduction is a bounded abstraction"
            ),
        },
        "bite": {
            "chance_numerator": 1,
            "chance_denominator": 8,
            "max_heal": 20,
            "stat_drain_amount": 1,
            "stat_drain_floor": 1,
            "stat_drain_skills": (
                "attack",
                "strength",
                "defense",
                "ranged",
                "prayer",
                "magic",
                "runecrafting",
                "construction",
                "constitution",
                "agility",
                "herblore",
                "thieving",
                "crafting",
                "fletching",
                "slayer",
                "hunter",
                "mining",
                "smithing",
                "fishing",
                "cooking",
                "firemaking",
                "woodcutting",
                "farming",
                "summoning",
            ),
            "source_status": (
                "period-authentic occasional bite that drains a combat or "
                "non-combat stat and heals the Vampyre; 1/8 landed-hit chance, "
                "20 LP healing cap, and one-level random drain are bounded "
                "abstractions"
            ),
        },
        "drops": {
            "guaranteed": (("Vampyre dust", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 100000,
                    "slots": (
                        {"item": "Grimy marrentill", "quantity": 1, "slots": 20988},
                        {"item": "Death rune", "quantity": 2, "slots": 20988},
                        {"item": "Chaos rune", "quantity": 3, "slots": 20988},
                        {"item": "Coins", "quantity": 15, "slots": 20988},
                        {"item": "Grimy guam", "quantity": 1, "slots": 699},
                        {"item": "Grimy tarromin", "quantity": 1, "slots": 699},
                        {"item": "Grimy harralander", "quantity": 1, "slots": 699},
                        {"item": "Grimy ranarr", "quantity": 1, "slots": 699},
                        {"item": "Earth rune", "quantity": 4, "slots": 699},
                        {"item": "Blood rune", "quantity_range": (1, 2), "slots": 699},
                        {"item": "Black hatchet", "quantity": 1, "slots": 699},
                        {"item": "Limpwurt seed", "quantity": 1, "slots": 699},
                        {"item": "Jangerberry seed", "quantity": 1, "slots": 699},
                        {"item": "Whiteberry seed", "quantity": 1, "slots": 699},
                        {"item": "Poison ivy seed", "quantity": 1, "slots": 699},
                        {"item": "Belladonna seed", "quantity": 1, "slots": 699},
                        {
                            "item": "Bittercap mushroom spore",
                            "quantity_range": (1, 2),
                            "slots": 699,
                        },
                        {"item": "Marrentill seed", "quantity": 1, "slots": 699},
                        {"item": "Tarromin seed", "quantity": 1, "slots": 699},
                        {"item": "Harralander seed", "quantity": 1, "slots": 699},
                        {"item": "Toadflax seed", "quantity": 1, "slots": 699},
                        {"item": "Irit seed", "quantity": 1, "slots": 699},
                        {"item": "Wildblood seed", "quantity": 1, "slots": 699},
                        {"item": "Strawberry seed", "quantity": 1, "slots": 699},
                        {"item": "Grimy irit", "quantity": 1, "slots": 143},
                        {"item": "Grimy avantoe", "quantity": 1, "slots": 143},
                        {"item": "Grimy kwuarm", "quantity": 1, "slots": 143},
                        {"item": "Grimy cadantine", "quantity": 1, "slots": 143},
                        {"item": "Earth talisman", "quantity": 1, "slots": 143},
                        {"item": "Cactus seed", "quantity": 1, "slots": 143},
                        {"item": "Avantoe seed", "quantity": 1, "slots": 143},
                        {"item": "Kwuarm seed", "quantity": 1, "slots": 143},
                        {"item": "Dwarf weed seed", "quantity": 1, "slots": 143},
                        {"item": "Watermelon seed", "quantity": 1, "slots": 143},
                        {"item": "Spirit weed seed", "quantity": 1, "slots": 143},
                        {
                            "item": "Morchella mushroom spore",
                            "quantity": 2,
                            "slots": 143,
                        },
                        {"item": "Grimy dwarf weed", "quantity": 1, "slots": 37},
                        {"item": "Grimy lantadyme", "quantity": 1, "slots": 37},
                        {"item": "Ranarr seed", "quantity": 1, "slots": 37},
                        {"item": "Cadantine seed", "quantity": 1, "slots": 37},
                        {"item": "Lantadyme seed", "quantity": 1, "slots": 37},
                        {"slots": 167},
                    ),
                },
            ),
        },
        "source": (
            "https://runescape.wiki/w/Feral_vampyre?oldid=6545273; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/combatdefs/uncategorized/vampyre/"
            "vampyre_(61).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/data/npcs/drops/vampyre.json"
        ),
        "source_status": (
            "period ordinary level-61 Feral vampyre identity, LP, maximum hit, "
            "Slayer XP, attack speed, all-weapon vulnerability, Holy symbol "
            "weakness, occasional bite, and guaranteed Vampyre dust; Darkan "
            "exact stats and respawn; Darkan probability rows normalized "
            "losslessly to 100000 mutually exclusive slots with 167 empty "
            "slots; level-72/77, Juvinate, and Vyrewatch variants excluded"
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
    "monkey": {
        "display_name": "Monkey",
        "level": 3,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 24,
        "max_hit": 20,
        "slayer_xp": 6.0,
        "stats": {
            "hitpoints": 60,
            "attack": 2,
            "strength": 2,
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
        "drops": {"guaranteed": (("Monkey bones", 1),), "tables": ()},
        "source": (
            "https://runescape.wiki/w/Monkey?oldid=6552407; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/combatdefs/uncategorized/monkey (nostats).json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "data/npcs/drops/monkey.json"
        ),
        "source_status": (
            "period LP, level, approximate max hit, Slayer XP, style, and "
            "guaranteed drop; neutral combat stats are formula-constrained to "
            "combat level 3"
        ),
    },
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
    "banshee": {
        "display_name": "Banshee",
        "level": 23,
        "group": "Slayer",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 15,
        "slayer_xp": 22.0,
        "protective_equipment": {
            "slot": "head",
            "items": (
                "Earmuffs",
                "Masked earmuffs",
                "Slayer helmet",
                "Slayer helmet (charged)",
                "Slayer helmet (e)",
                "Full slayer helmet",
                "Full slayer helmet (charged)",
                "Full slayer helmet (e)",
            ),
            "warning": (
                "Missing Earmuffs or a Slayer helmet in the head slot: Banshee "
                "screams deal fixed damage and drain eight skills."
            ),
            "unprotected_effect": {
                "damage": {
                    "kind": "max_lifepoints_fraction_capped",
                    "numerator": 1,
                    "denominator": 10,
                    "cap": 80,
                },
                "stat_drain": {
                    "kind": "flat_to_floor",
                    "skills": (
                        "attack",
                        "strength",
                        "defense",
                        "ranged",
                        "prayer",
                        "magic",
                        "agility",
                        "summoning",
                    ),
                    "amount": 5,
                    "floor": 1,
                },
            },
            "source_status": (
                "abstraction/period+darkan: fixed max-LP/10 hit capped at the "
                "period 80 LP maximum; period eight-skill set uses Darkan's "
                "smallest surviving flat five-level drain magnitude"
            ),
        },
        "stats": {'hitpoints': 220, 'attack': 22, 'strength': 15, 'defence': 22, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 5,
 'defence_slash': 5,
 'defence_crush': 5,
 'defence_magic': 0,
 'defence_ranged': 5,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Bones', 1),),
 'tables': ({'name': 'Main',
             'total': 1148,
             'slots': ({'item': 'Iron dagger', 'quantity': 1, 'slots': 128},
                       {'item': 'Iron mace', 'quantity': 1, 'slots': 128},
                       {'item': 'Iron kiteshield', 'quantity': 1, 'slots': 128},
                       {'item': 'Adamant kiteshield', 'quantity': 1, 'slots': 4},
                       {'item': 'Mystic gloves', 'quantity': 1, 'slots': 8},
                       {'item': 'Mystic gloves', 'quantity': 1, 'slots': 2},
                       {'item': 'Air rune', 'quantity': 3, 'slots': 24},
                       {'item': 'Cosmic rune', 'quantity': 2, 'slots': 24},
                       {'item': 'Pure essence', 'quantity': 13, 'slots': 128},
                       {'item': 'Chaos rune', 'quantity': 7, 'slots': 8},
                       {'item': 'Fire rune', 'quantity': 7, 'slots': 8},
                       {'item': 'Coins', 'quantity': 13, 'slots': 84},
                       {'item': 'Fishing bait', 'quantity': 15, 'slots': 128},
                       {'item': 'Eye of newt', 'quantity': 1, 'slots': 8},
                       {'item': 'Iron ore', 'quantity': 1, 'slots': 8},
                       {'item': 'Clue scroll (easy)', 'quantity': 1, 'slots': 32},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 2},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 272},
                       {'slots': 8})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 3},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 7},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 1},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 1},
                       {'slots': 898})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/undeads/banshee_level_23.plugin.kts; "
            "https://runescape.wiki/w/Banshee?oldid=6589075; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
            "src/main/java/com/rs/game/content/skills/slayer/npcs/combat/BansheeCombat.java"
        ),
    },
    "shade": {
        "display_name": "Shade",
        "level": 83,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 3.5,
        "xp_multiplier": 0.25,
        "stats": {'hitpoints': 700, 'attack': 74, 'strength': 74, 'defence': 70, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 0,
 'defence_slash': 0,
 'defence_crush': 0,
 'defence_magic': 0,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (),
 'tables': ({'name': 'Main',
             'total': 4,
             'slots': ({'item': 'Shade robe', 'quantity': 1, 'slots': 1},
                       {'item': 'Shade robe', 'quantity': 1, 'slots': 1})},)},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/undeads/shade_level_83.plugin.kts; RuneScape Wiki Shade oldid 6564222"
        ),
    },
    "ghost_level_77": {
        "display_name": "Ghost (level 77)",
        "level": 77,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 40,
        "slayer_xp": 80.0,
        "stats": {'hitpoints': 800, 'attack': 63, 'strength': 63, 'defence': 68, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 55,
 'defence_slash': 55,
 'defence_crush': 5,
 'defence_magic': 55,
 'defence_ranged': 55,
 'melee_strength': 0},
        "drops": {'guaranteed': (), 'tables': ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/undeads/ghost_level_77.plugin.kts"
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
    "flesh_crawler_level_28": {
        "display_name": "Flesh crawler (level 28)",
        "level": 28,
        "group": "Stronghold of Security",
        "attack_style": "melee",
        "attack_speed": 3,
        "respawn_delay": 15,
        "slayer_xp": 25.0,
        "stats": {'hitpoints': 250, 'attack': 60, 'strength': 2, 'defence': 10, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 15,
 'defence_slash': 15,
 'defence_crush': 15,
 'defence_magic': 15,
 'defence_ranged': 15,
 'melee_strength': 0},
        "drops": {'guaranteed': (),
 'tables': ({'name': 'Main',
             'total': 256,
             'slots': ({'item': 'Body rune', 'quantity': 1, 'slots': 25},
                       {'item': 'Dust rune', 'quantity': 1, 'slots': 17},
                       {'item': 'Fire rune', 'quantity': 42, 'slots': 8},
                       {'item': 'Nature rune', 'quantity': 1, 'slots': 2},
                       {'item': 'Coins', 'quantity': 1, 'slots': 25},
                       {'item': 'Iron ore', 'quantity': 1, 'slots': 25},
                       {'item': 'Ashes', 'quantity': 1, 'slots': 25},
                       {'item': 'Bottom of sceptre', 'quantity': 1, 'slots': 2},
                       {'item': 'Silver bar', 'quantity': 1, 'slots': 25},
                       {'item': 'Black full helm', 'quantity': 1, 'slots': 8},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 1},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 43})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 40},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 60},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 8},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 2},
                       {'slots': 890})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/flesh_crawler_lvl_28.plugin.kts"
        ),
    },
    "flesh_crawler_level_35": {
        "display_name": "Flesh crawler (level 35)",
        "level": 35,
        "group": "Stronghold of Security",
        "attack_style": "melee",
        "attack_speed": 3,
        "respawn_delay": 15,
        "slayer_xp": 25.0,
        "stats": {'hitpoints': 250, 'attack': 80, 'strength': 2, 'defence': 10, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 15,
 'defence_slash': 15,
 'defence_crush': 15,
 'defence_magic': 15,
 'defence_ranged': 15,
 'melee_strength': 0},
        "drops": {'guaranteed': (),
 'tables': ({'name': 'Main',
             'total': 256,
             'slots': ({'item': 'Body rune', 'quantity': 1, 'slots': 25},
                       {'item': 'Dust rune', 'quantity': 1, 'slots': 17},
                       {'item': 'Fire rune', 'quantity': 42, 'slots': 8},
                       {'item': 'Nature rune', 'quantity': 1, 'slots': 2},
                       {'item': 'Coins', 'quantity': 1, 'slots': 25},
                       {'item': 'Iron ore', 'quantity': 1, 'slots': 25},
                       {'item': 'Ashes', 'quantity': 1, 'slots': 25},
                       {'item': 'Bottom of sceptre', 'quantity': 1, 'slots': 2},
                       {'item': 'Silver bar', 'quantity': 1, 'slots': 25},
                       {'item': 'Black full helm', 'quantity': 1, 'slots': 8},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 1},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 43})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 40},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 60},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 8},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 2},
                       {'slots': 890})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/flesh_crawler_lvl_35.plugin.kts"
        ),
    },
    "flesh_crawler_level_41": {
        "display_name": "Flesh crawler (level 41)",
        "level": 41,
        "group": "Stronghold of Security",
        "attack_style": "melee",
        "attack_speed": 3,
        "respawn_delay": 15,
        "slayer_xp": 25.0,
        "stats": {'hitpoints': 250, 'attack': 100, 'strength': 2, 'defence': 10, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 15,
 'defence_slash': 15,
 'defence_crush': 15,
 'defence_magic': 15,
 'defence_ranged': 15,
 'melee_strength': 0},
        "drops": {'guaranteed': (),
 'tables': ({'name': 'Main',
             'total': 256,
             'slots': ({'item': 'Body rune', 'quantity': 1, 'slots': 25},
                       {'item': 'Dust rune', 'quantity': 1, 'slots': 17},
                       {'item': 'Fire rune', 'quantity': 42, 'slots': 8},
                       {'item': 'Nature rune', 'quantity': 1, 'slots': 2},
                       {'item': 'Coins', 'quantity': 1, 'slots': 25},
                       {'item': 'Iron ore', 'quantity': 1, 'slots': 25},
                       {'item': 'Ashes', 'quantity': 1, 'slots': 25},
                       {'item': 'Bottom of sceptre', 'quantity': 1, 'slots': 2},
                       {'item': 'Silver bar', 'quantity': 1, 'slots': 25},
                       {'item': 'Black full helm', 'quantity': 1, 'slots': 8},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 1},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 43})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 40},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 60},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 8},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 2},
                       {'slots': 890})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/flesh_crawler_lvl_41.plugin.kts"
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
    "ankou_level_75": {
        "display_name": "Ankou (level 75)",
        "level": 75,
        "group": "Stronghold of Security",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 60.0,
        "stats": {'hitpoints': 600, 'attack': 70, 'strength': 70, 'defence': 60, 'magic': 1, 'ranged': 1},
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
             'total': 256,
             'slots': ({'item': 'Black robe', 'quantity': 1, 'slots': 16},
                       {'item': 'Black knife', 'quantity': 1, 'slots': 9},
                       {'item': 'Battlestaff', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant arrows', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant arrows', 'quantity': 25, 'slots': 9},
                       {'item': 'Wizard hat', 'quantity': 1, 'slots': 2},
                       {'item': 'Blood rune', 'quantity': 1, 'slots': 16},
                       {'item': 'Blood rune', 'quantity': 1, 'slots': 16},
                       {'item': 'Blood rune', 'quantity': 16, 'slots': 16},
                       {'item': 'Law rune', 'quantity': 2, 'slots': 9},
                       {'item': 'Fire rune', 'quantity': 1, 'slots': 9},
                       {'item': 'Death rune', 'quantity': 1, 'slots': 9},
                       {'item': 'Bass', 'quantity': 1, 'slots': 16},
                       {'item': 'Fried mushrooms', 'quantity': 1, 'slots': 9},
                       {'item': 'Coins', 'quantity': 1, 'slots': 16},
                       {'item': 'Left skull half', 'quantity': 1, 'slots': 9},
                       {'item': 'Rune essence', 'quantity': 15, 'slots': 9},
                       {'item': 'Pure essence', 'quantity': 15, 'slots': 9},
                       {'item': 'Weapon poison', 'quantity': 1, 'slots': 9},
                       {'item': 'Mithril ore', 'quantity': 1, 'slots': 9},
                       {'item': 'Fire talisman', 'quantity': 1, 'slots': 2},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 2},
                       {'item': 'Clue scroll (hard)', 'quantity': 1, 'slots': 1},
                       {'table': COMBAT_UNCOMMON_SEED_DROP_TABLE, 'slots': 3},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 8},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 5})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 240},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 5},
                       {'slots': 715})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/undeads/ankou_lvl_75.plugin.kts"
        ),
    },
    "ankou_level_82": {
        "display_name": "Ankou (level 82)",
        "level": 82,
        "group": "Stronghold of Security",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 65.0,
        "stats": {'hitpoints': 650, 'attack': 80, 'strength': 70, 'defence': 70, 'magic': 1, 'ranged': 1},
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
             'total': 256,
             'slots': ({'item': 'Black robe', 'quantity': 1, 'slots': 16},
                       {'item': 'Black knife', 'quantity': 1, 'slots': 9},
                       {'item': 'Battlestaff', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant arrows', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant arrows', 'quantity': 25, 'slots': 9},
                       {'item': 'Wizard hat', 'quantity': 1, 'slots': 2},
                       {'item': 'Blood rune', 'quantity': 1, 'slots': 16},
                       {'item': 'Blood rune', 'quantity': 1, 'slots': 16},
                       {'item': 'Blood rune', 'quantity': 16, 'slots': 16},
                       {'item': 'Law rune', 'quantity': 2, 'slots': 9},
                       {'item': 'Fire rune', 'quantity': 1, 'slots': 9},
                       {'item': 'Death rune', 'quantity': 1, 'slots': 9},
                       {'item': 'Bass', 'quantity': 1, 'slots': 16},
                       {'item': 'Fried mushrooms', 'quantity': 1, 'slots': 9},
                       {'item': 'Coins', 'quantity': 1, 'slots': 16},
                       {'item': 'Left skull half', 'quantity': 1, 'slots': 9},
                       {'item': 'Rune essence', 'quantity': 15, 'slots': 9},
                       {'item': 'Pure essence', 'quantity': 15, 'slots': 9},
                       {'item': 'Weapon poison', 'quantity': 1, 'slots': 9},
                       {'item': 'Mithril ore', 'quantity': 1, 'slots': 9},
                       {'item': 'Fire talisman', 'quantity': 1, 'slots': 2},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 2},
                       {'item': 'Clue scroll (hard)', 'quantity': 1, 'slots': 1},
                       {'table': COMBAT_UNCOMMON_SEED_DROP_TABLE, 'slots': 3},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 8},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 5})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 240},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 5},
                       {'slots': 715})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/undeads/ankou_lvl_82.plugin.kts"
        ),
    },
    "ankou_level_86": {
        "display_name": "Ankou (level 86)",
        "level": 86,
        "group": "Stronghold of Security",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 70.0,
        "stats": {'hitpoints': 700, 'attack': 75, 'strength': 75, 'defence': 80, 'magic': 1, 'ranged': 1},
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
             'total': 256,
             'slots': ({'item': 'Black robe', 'quantity': 1, 'slots': 16},
                       {'item': 'Black knife', 'quantity': 1, 'slots': 9},
                       {'item': 'Battlestaff', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant arrows', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant arrows', 'quantity': 25, 'slots': 9},
                       {'item': 'Wizard hat', 'quantity': 1, 'slots': 2},
                       {'item': 'Blood rune', 'quantity': 1, 'slots': 16},
                       {'item': 'Blood rune', 'quantity': 1, 'slots': 16},
                       {'item': 'Blood rune', 'quantity': 16, 'slots': 16},
                       {'item': 'Law rune', 'quantity': 2, 'slots': 9},
                       {'item': 'Fire rune', 'quantity': 1, 'slots': 9},
                       {'item': 'Death rune', 'quantity': 1, 'slots': 9},
                       {'item': 'Bass', 'quantity': 1, 'slots': 16},
                       {'item': 'Fried mushrooms', 'quantity': 1, 'slots': 9},
                       {'item': 'Coins', 'quantity': 1, 'slots': 16},
                       {'item': 'Left skull half', 'quantity': 1, 'slots': 9},
                       {'item': 'Rune essence', 'quantity': 15, 'slots': 9},
                       {'item': 'Pure essence', 'quantity': 15, 'slots': 9},
                       {'item': 'Weapon poison', 'quantity': 1, 'slots': 9},
                       {'item': 'Mithril ore', 'quantity': 1, 'slots': 9},
                       {'item': 'Fire talisman', 'quantity': 1, 'slots': 2},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 2},
                       {'item': 'Clue scroll (hard)', 'quantity': 1, 'slots': 1},
                       {'table': COMBAT_UNCOMMON_SEED_DROP_TABLE, 'slots': 3},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 8},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 5})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 240},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 5},
                       {'slots': 715})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/undeads/ankou_lvl_86.plugin.kts"
        ),
    },
    "catablepon_level_49": {
        "display_name": "Catablepon (level 49)",
        "level": 49,
        "group": "Stronghold of Security",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 20,
        "slayer_xp": 40.0,
        "stats": {'hitpoints': 400, 'attack': 45, 'strength': 40, 'defence': 40, 'magic': 60, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 40,
 'defence_slash': 30,
 'defence_crush': 20,
 'defence_magic': 20,
 'defence_ranged': 40,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Bones', 1),),
 'tables': ({'name': 'Main',
             'total': 256,
             'slots': ({'item': 'Black full helm', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant med helm', 'quantity': 1, 'slots': 9},
                       {'item': 'Mithril arrows', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant arrows', 'quantity': 1, 'slots': 9},
                       {'item': 'Trout', 'quantity': 1, 'slots': 9},
                       {'item': 'Salmon', 'quantity': 1, 'slots': 9},
                       {'item': 'Rune essence', 'quantity': 15, 'slots': 20},
                       {'item': 'Pure essence', 'quantity': 15, 'slots': 9},
                       {'item': 'Water rune', 'quantity': 7, 'slots': 20},
                       {'item': 'Fire rune', 'quantity': 15, 'slots': 9},
                       {'item': 'Cosmic rune', 'quantity': 1, 'slots': 9},
                       {'item': 'Chaos rune', 'quantity': 7, 'slots': 9},
                       {'item': 'Law rune', 'quantity': 2, 'slots': 9},
                       {'item': 'Coins', 'quantity': 1, 'slots': 20},
                       {'item': 'Eye of newt', 'quantity': 1, 'slots': 20},
                       {'item': 'Unlit torch', 'quantity': 1, 'slots': 20},
                       {'item': 'Clue scroll (medium)', 'quantity': 1, 'slots': 2},
                       {'item': 'Coal', 'quantity': 1, 'slots': 2},
                       {'item': 'Top of sceptre', 'quantity': 1, 'slots': 2},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 1},
                       {'item': 'Rune essence', 'quantity': 30, 'slots': 25},
                       {'table': COMBAT_ALLOTMENT_SEED_DROP_TABLE, 'slots': 10},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 10},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 5})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 200},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 30},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 5},
                       {'slots': 745})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/catablepon_lvl_49.plugin.kts"
        ),
    },
    "catablepon_level_64": {
        "display_name": "Catablepon (level 64)",
        "level": 64,
        "group": "Stronghold of Security",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 20,
        "slayer_xp": 70.0,
        "stats": {'hitpoints': 700, 'attack': 55, 'strength': 50, 'defence': 50, 'magic': 45, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 50,
 'defence_slash': 40,
 'defence_crush': 30,
 'defence_magic': 30,
 'defence_ranged': 50,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Bones', 1),),
 'tables': ({'name': 'Main',
             'total': 256,
             'slots': ({'item': 'Black full helm', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant med helm', 'quantity': 1, 'slots': 9},
                       {'item': 'Mithril arrows', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant arrows', 'quantity': 1, 'slots': 9},
                       {'item': 'Trout', 'quantity': 1, 'slots': 9},
                       {'item': 'Salmon', 'quantity': 1, 'slots': 9},
                       {'item': 'Rune essence', 'quantity': 15, 'slots': 20},
                       {'item': 'Pure essence', 'quantity': 15, 'slots': 9},
                       {'item': 'Water rune', 'quantity': 7, 'slots': 20},
                       {'item': 'Fire rune', 'quantity': 15, 'slots': 9},
                       {'item': 'Cosmic rune', 'quantity': 1, 'slots': 9},
                       {'item': 'Chaos rune', 'quantity': 7, 'slots': 9},
                       {'item': 'Law rune', 'quantity': 2, 'slots': 9},
                       {'item': 'Coins', 'quantity': 1, 'slots': 20},
                       {'item': 'Eye of newt', 'quantity': 1, 'slots': 20},
                       {'item': 'Unlit torch', 'quantity': 1, 'slots': 20},
                       {'item': 'Clue scroll (medium)', 'quantity': 1, 'slots': 2},
                       {'item': 'Coal', 'quantity': 1, 'slots': 2},
                       {'item': 'Top of sceptre', 'quantity': 1, 'slots': 2},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 1},
                       {'item': 'Rune essence', 'quantity': 30, 'slots': 25},
                       {'table': COMBAT_ALLOTMENT_SEED_DROP_TABLE, 'slots': 10},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 10},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 5})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 200},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 30},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 5},
                       {'slots': 745})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/catablepon_lvl_64.plugin.kts"
        ),
    },
    "catablepon_level_68": {
        "display_name": "Catablepon (level 68)",
        "level": 68,
        "group": "Stronghold of Security",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 20,
        "slayer_xp": 70.0,
        "stats": {'hitpoints': 500, 'attack': 65, 'strength': 60, 'defence': 60, 'magic': 60, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 50,
 'defence_slash': 40,
 'defence_crush': 30,
 'defence_magic': 30,
 'defence_ranged': 50,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Bones', 1),),
 'tables': ({'name': 'Main',
             'total': 256,
             'slots': ({'item': 'Black full helm', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant med helm', 'quantity': 1, 'slots': 9},
                       {'item': 'Mithril arrows', 'quantity': 1, 'slots': 9},
                       {'item': 'Adamant arrows', 'quantity': 1, 'slots': 9},
                       {'item': 'Trout', 'quantity': 1, 'slots': 9},
                       {'item': 'Salmon', 'quantity': 1, 'slots': 9},
                       {'item': 'Rune essence', 'quantity': 15, 'slots': 20},
                       {'item': 'Pure essence', 'quantity': 15, 'slots': 9},
                       {'item': 'Water rune', 'quantity': 7, 'slots': 20},
                       {'item': 'Fire rune', 'quantity': 15, 'slots': 9},
                       {'item': 'Cosmic rune', 'quantity': 1, 'slots': 9},
                       {'item': 'Chaos rune', 'quantity': 7, 'slots': 9},
                       {'item': 'Law rune', 'quantity': 2, 'slots': 9},
                       {'item': 'Coins', 'quantity': 1, 'slots': 20},
                       {'item': 'Eye of newt', 'quantity': 1, 'slots': 20},
                       {'item': 'Unlit torch', 'quantity': 1, 'slots': 20},
                       {'item': 'Clue scroll (medium)', 'quantity': 1, 'slots': 2},
                       {'item': 'Coal', 'quantity': 1, 'slots': 2},
                       {'item': 'Top of sceptre', 'quantity': 1, 'slots': 2},
                       {'item': 'Starved ancient effigy', 'quantity': 1, 'slots': 1},
                       {'item': 'Rune essence', 'quantity': 30, 'slots': 25},
                       {'table': COMBAT_ALLOTMENT_SEED_DROP_TABLE, 'slots': 10},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 10},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 5})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 200},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 20},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 30},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 5},
                       {'slots': 745})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/catablepon_lvl_68.plugin.kts"
        ),
    },
    "minotaur_level_12": {
        "display_name": "Minotaur (level 12)",
        "level": 12,
        "group": "Stronghold of Security",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "slayer_xp": 10.0,
        "stats": {'hitpoints': 100, 'attack': 12, 'strength': 10, 'defence': 10, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': -21,
 'defence_slash': -21,
 'defence_crush': -21,
 'defence_magic': -21,
 'defence_ranged': -21,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Bones', 1),),
 'tables': ({'name': 'Main',
             'total': 459,
             'slots': ({'item': 'Bronze spear', 'quantity': 1, 'slots': 51},
                       {'item': 'Bronze full helm', 'quantity': 1, 'slots': 51},
                       {'item': 'Iron arrows', 'quantity': 1, 'slots': 51},
                       {'item': 'Bronze dagger', 'quantity': 1, 'slots': 20},
                       {'item': 'Bronze arrows', 'quantity': 3, 'slots': 15},
                       {'item': 'Sling', 'quantity': 1, 'slots': 16},
                       {'item': 'Staff of air', 'quantity': 1, 'slots': 16},
                       {'item': 'Rune javelin', 'quantity': 5, 'slots': 4},
                       {'item': 'Tin ore', 'quantity': 1, 'slots': 32},
                       {'item': 'Copper ore', 'quantity': 1, 'slots': 32},
                       {'item': 'Pure essence', 'quantity': 1, 'slots': 25},
                       {'item': 'Rune essence', 'quantity': 1, 'slots': 25},
                       {'item': 'Gold bar', 'quantity': 1, 'slots': 4},
                       {'item': 'Coins', 'quantity': 1, 'slots': 25},
                       {'item': 'Water rune', 'quantity': 5, 'slots': 16},
                       {'item': 'Earth rune', 'quantity': 5, 'slots': 16},
                       {'item': 'Cooked meat', 'quantity': 1, 'slots': 4},
                       {'item': 'Mind rune', 'quantity': 1, 'slots': 25},
                       {'item': 'Fire talisman', 'quantity': 1, 'slots': 4},
                       {'item': 'Nature talisman', 'quantity': 1, 'slots': 4},
                       {'item': 'Right skull half', 'quantity': 1, 'slots': 15},
                       {'item': 'Clue scroll (easy)', 'quantity': 1, 'slots': 4})},)},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/minotaur/minotaur_lvl_12.plugin.kts"
        ),
    },
    "minotaur_level_27": {
        "display_name": "Minotaur (level 27)",
        "level": 27,
        "group": "Stronghold of Security",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 15,
        "slayer_xp": 22.0,
        "stats": {'hitpoints': 220, 'attack': 23, 'strength': 25, 'defence': 25, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': -10,
 'defence_slash': -10,
 'defence_crush': -10,
 'defence_magic': -21,
 'defence_ranged': -10,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Bones', 1),),
 'tables': ({'name': 'Main',
             'total': 459,
             'slots': ({'item': 'Bronze spear', 'quantity': 1, 'slots': 51},
                       {'item': 'Bronze full helm', 'quantity': 1, 'slots': 51},
                       {'item': 'Iron arrows', 'quantity': 1, 'slots': 51},
                       {'item': 'Bronze dagger', 'quantity': 1, 'slots': 20},
                       {'item': 'Bronze arrows', 'quantity': 3, 'slots': 15},
                       {'item': 'Sling', 'quantity': 1, 'slots': 16},
                       {'item': 'Staff of air', 'quantity': 1, 'slots': 16},
                       {'item': 'Rune javelin', 'quantity': 5, 'slots': 4},
                       {'item': 'Tin ore', 'quantity': 1, 'slots': 32},
                       {'item': 'Copper ore', 'quantity': 1, 'slots': 32},
                       {'item': 'Pure essence', 'quantity': 1, 'slots': 25},
                       {'item': 'Rune essence', 'quantity': 1, 'slots': 25},
                       {'item': 'Gold bar', 'quantity': 1, 'slots': 4},
                       {'item': 'Coins', 'quantity': 1, 'slots': 25},
                       {'item': 'Water rune', 'quantity': 5, 'slots': 16},
                       {'item': 'Earth rune', 'quantity': 5, 'slots': 16},
                       {'item': 'Cooked meat', 'quantity': 1, 'slots': 4},
                       {'item': 'Mind rune', 'quantity': 1, 'slots': 25},
                       {'item': 'Fire talisman', 'quantity': 1, 'slots': 4},
                       {'item': 'Nature talisman', 'quantity': 1, 'slots': 4},
                       {'item': 'Right skull half', 'quantity': 1, 'slots': 15},
                       {'item': 'Clue scroll (easy)', 'quantity': 1, 'slots': 4})},)},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/minotaur/minotaur_lvl_27.plugin.kts"
        ),
    },
    "cave_goblin": {
        "display_name": "Cave goblin",
        "level": 3,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 10.0,
        "stats": {'hitpoints': 100, 'attack': 0, 'strength': 0, 'defence': 0, 'magic': 1, 'ranged': 1},
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
             'total': 50,
             'slots': ({'item': 'Body rune', 'quantity': 7, 'slots': 5},
                       {'item': 'Water rune', 'quantity': 6, 'slots': 5},
                       {'item': 'Earth rune', 'quantity': 4, 'slots': 5},
                       {'item': 'Coins', 'quantity': 15, 'slots': 6},
                       {'item': 'Coins', 'quantity': 20, 'slots': 5},
                       {'item': 'Coins', 'quantity': 5, 'slots': 4},
                       {'item': 'Coins', 'quantity': 9, 'slots': 4},
                       {'item': 'Coins', 'quantity': 1, 'slots': 1},
                       {'item': 'Hammer', 'quantity': 1, 'slots': 4},
                       {'item': 'Tinderbox', 'quantity': 1, 'slots': 4},
                       {'item': 'Brass necklace', 'quantity': 1, 'slots': 1},
                       {'slots': 16})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Gold charm', 'quantity': 1, 'slots': 60},
                       {'item': 'Green charm', 'quantity': 1, 'slots': 30},
                       {'item': 'Crimson charm', 'quantity': 1, 'slots': 30},
                       {'item': 'Blue charm', 'quantity': 1, 'slots': 15},
                       {'slots': 865})},
            {'name': 'Tertiary',
             'total': 128,
             'slots': ({'slots': 127}, {'item': 'Clue scroll (easy)', 'quantity': 1, 'slots': 1})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/cave_goblin_level_3.plugin.kts"
        ),
    },
    "canifis_citizen": {
        "display_name": "Canifis citizen",
        "level": 24,
        "group": "Canifis",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 60.0,
        "stats": {'hitpoints': 600, 'attack': 10, 'strength': 10, 'defence': 10, 'magic': 1, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': -21,
 'defence_slash': -21,
 'defence_crush': -21,
 'defence_magic': -21,
 'defence_ranged': -21,
 'melee_strength': 0},
        "drops": {'guaranteed': (('Wolf bones', 1),),
 'tables': ({'name': 'Main',
             'total': 128,
             'slots': ({'item': 'Raw chicken', 'quantity': 5, 'slots': 16},
                       {'item': 'Raw beef', 'quantity': 5, 'slots': 16},
                       {'item': 'Raw bear meat', 'quantity': 5, 'slots': 16},
                       {'item': 'Jug of wine', 'quantity': 1, 'slots': 16},
                       {'item': 'Steel scimitar', 'quantity': 1, 'slots': 16},
                       {'item': 'Steel hatchet', 'quantity': 1, 'slots': 16},
                       {'item': 'Steel arrow (p)', 'quantity': 5, 'slots': 4},
                       {'item': 'Steel arrows', 'quantity': 50, 'slots': 4},
                       {'item': 'Steel full helm', 'quantity': 1, 'slots': 4},
                       {'item': 'Mithril scimitar', 'quantity': 1, 'slots': 4},
                       {'item': 'Mithril sq shield', 'quantity': 1, 'slots': 4},
                       {'item': 'Rune med helm', 'quantity': 1, 'slots': 4},
                       {'item': 'Rune javelin', 'quantity': 1, 'slots': 1},
                       {'table': COMBAT_MINOR_HERB_DROP_TABLE, 'slots': 3},
                       {'table': COMBAT_GEM_DROP_TABLE, 'slots': 3})},)},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/canifis_citizen_level_24.plugin.kts"
        ),
    },
    "tzhaar_hur": {
        "display_name": "TzHaar-Hur",
        "level": 74,
        "group": "TzHaar",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 50,
        "slayer_xp": 80.0,
        "stats": {'hitpoints': 800, 'attack': 60, 'strength': 60, 'defence': 60, 'magic': 80, 'ranged': 1},
        "bonuses": {'attack_stab': 0,
 'attack_slash': 0,
 'attack_crush': 0,
 'defence_stab': 0,
 'defence_slash': 0,
 'defence_crush': 0,
 'defence_magic': 0,
 'defence_ranged': 0,
 'melee_strength': 0},
        "drops": {'guaranteed': (),
 'tables': ({'name': 'Main',
             'total': 128,
             'slots': ({'item': 'Tokkul', 'quantity_range': (150, 800), 'slots': 32},
                       {'item': 'Gold ore', 'quantity': 1, 'slots': 12},
                       {'item': 'Silver ore', 'quantity_range': (1, 2), 'slots': 11},
                       {'item': 'Soft clay', 'quantity': 3, 'slots': 8},
                       {'item': 'Steel bar', 'quantity': 1, 'slots': 8},
                       {'item': 'Onyx bolt tips', 'quantity': 1, 'slots': 2},
                       {'item': 'Molten glass', 'quantity': 2, 'slots': 6},
                       {'item': 'Battlestaff', 'quantity': 1, 'slots': 6},
                       {'item': 'Hard leather', 'quantity': 1, 'slots': 6},
                       {'item': 'Leather', 'quantity': 3, 'slots': 6},
                       {'item': 'Wool', 'quantity': 8, 'slots': 6},
                       {'item': 'Flax', 'quantity_range': (5, 10), 'slots': 6},
                       {'item': 'Pure essence', 'quantity_range': (4, 6), 'slots': 6},
                       {'item': 'Lobster', 'quantity': 1, 'slots': 6},
                       {'item': 'Super attack (1)', 'quantity': 1, 'slots': 3},
                       {'item': 'Super strength (1)', 'quantity': 1, 'slots': 3})},
            {'name': 'Charms',
             'total': 1000,
             'slots': ({'item': 'Obsidian charm', 'quantity': 1, 'slots': 360},
                       {'item': 'Obsidian charm', 'quantity': 2, 'slots': 360},
                       {'slots': 280})})},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/other/tzhaar_hur_lvl_74.plugin.kts"
        ),
    },
}


COMBAT_EXTRA_ITEM_DATA: Dict[str, dict] = {
    "Antipoison (1)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_1"},
    "Antipoison (2)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_2"},
    "Antipoison (3)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_3"},
    "Antipoison (4)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_4"},
    "Avantoe seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.AVANTOE_SEED"},
    "Banana": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BANANA"},
    "Bat bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BAT_BONES"},
    "Bear fur": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BEAR_FUR"},
    "Belladonna seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BELLADONNA_SEED"},
    "Big bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BIG_BONES"},
    "Black bead": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLACK_BEAD"},
    "Black kiteshield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLACK_KITESHIELD"},
    "Black sq shield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLACK_SQ_SHIELD"},
    "Bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BONES"},
    "Brass necklace": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRASS_NECKLACE"},
    "Brine sabre": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 11037; "
            "RuneScape Wiki Brine rat oldid=6555564"
        ),
        "source_item_id": 11037,
        "stackable": False,
        "tradeable": True,
    },
    "Bronze javelin": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRONZE_JAVELIN"},
    "Bronze spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRONZE_SPEAR"},
    "Buttons": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BUTTONS"},
    "Cactus seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CACTUS_SEED"},
    "Cape": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CAPE_1019"},
    "Coral bolts": {
        "category": "equipment",
        "source": "RuneScape Wiki Coral bolts oldid 6146806; Darkan item config 24304",
        "source_item_id": 24304,
        "stackable": True,
        "tradeable": False,
    },
    "Saradomin cape": {
        "category": "equipment",
        "source": "RuneScape cache item 2412; Mage Arena oldid=6512911",
        "source_item_id": 2412,
        "stackable": False,
        "tradeable": False,
    },
    "Guthix cape": {
        "category": "equipment",
        "source": "RuneScape cache item 2413; Mage Arena oldid=6512911",
        "source_item_id": 2413,
        "stackable": False,
        "tradeable": False,
    },
    "Zamorak cape": {
        "category": "equipment",
        "source": "RuneScape cache item 2414; Mage Arena oldid=6512911",
        "source_item_id": 2414,
        "stackable": False,
        "tradeable": False,
    },
    "Cadantine seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CADANTINE_SEED"},
    "Cadava berries": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CADAVA_BERRIES"},
    "Champion's scroll": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CHAMPIONS_SCROLL_6800"},
    "Chef's hat": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CHEFS_HAT"},
    "Chilli potato": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CHILLI_POTATO"},
    "Cabbage seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CABBAGE_SEED"},
    "Clue scroll (easy)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CLUE_SCROLL_EASY"},
    "Clue scroll (medium)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CLUE_SCROLL_MEDIUM"},
    "Coins": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.COINS_995"},
    "Cowhide": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.COWHIDE"},
    "Curved bone": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CURVED_BONE"},
    **{
        item_name: {
            "category": "equipment",
            "source": (
                f"RuneScape Wiki Defenders oldid=6513277; "
                f"Darkan cache item {item_id}"
            ),
            "source_item_id": item_id,
            "stackable": False,
            "tradeable": False,
        }
        for item_name, item_id in (
            ("Bronze defender", 8844),
            ("Iron defender", 8845),
            ("Steel defender", 8846),
            ("Black defender", 8847),
            ("Mithril defender", 8848),
            ("Adamant defender", 8849),
            ("Rune defender", 8850),
            ("Dragon defender", 20072),
        )
    },
    "Cyclopean helmet": {
        "category": "equipment",
        "source": "RuneScape Wiki Cyclopean helmet oldid=5825578; Darkan cache item 20070",
        "source_item_id": 20070,
        "stackable": False,
        "tradeable": True,
    },
    "Damaged armour": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.DAMAGED_ARMOUR"},
    "Beer": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BEER"},
    "Dragon spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.DRAGON_SPEAR"},
    "Dwarf weed seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.DWARF_WEED_SEED"},
    "Edible seaweed": {
        "category": "food",
        "source": f"{ITEM_ID_SOURCE_PATH}: Items.EDIBLE_SEAWEED",
        "source_item_id": 403,
        "stackable": False,
        "tradeable": True,
    },
    "Eye patch": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.EYE_PATCH"},
    "Fire battlestaff": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.FIRE_BATTLESTAFF"},
    "Fungicide": {
        "category": "material",
        "source": "Darkan cache item 7432; RuneScape Wiki Mutated zygomite oldid 6530349",
        "source_item_id": 7432,
        "stackable": False,
        "tradeable": False,
    },
    **{
        f"Fungicide spray {charges}": {
            "category": "tool",
            "source": (
                f"Darkan cache item {7431 - charges}; "
                "RuneScape Wiki Mutated zygomite oldid 6530349"
            ),
            "source_item_id": 7431 - charges,
            "stackable": False,
            "tradeable": False,
        }
        for charges in range(11)
    },
    "Gardening boots": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GARDENING_BOOTS"},
    "Goblin book": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GOBLIN_BOOK"},
    "Grapes": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRAPES"},
    "Grimy avantoe": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_AVANTOE"},
    "Grimy cadantine": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_CADANTINE"},
    "Grimy dwarf weed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_DWARF_WEED"},
    "Grimy guam": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_GUAM"},
    "Grimy harralander": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_HARRALANDER"},
    "Grimy irit": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_IRIT"},
    "Grimy kwuarm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_KWUARM"},
    "Grimy lantadyme": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_LANTADYME"},
    "Grimy marrentill": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_MARRENTILL"},
    "Grimy ranarr": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_RANARR"},
    "Grimy snapdragon": {
        "category": "material",
        "source": "Darkan cache item 3051; Darkan herb special table item 3051",
        "source_item_id": 3051,
        "stackable": False,
        "tradeable": True,
    },
    "Grimy tarromin": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_TARROMIN"},
    "Half an apple pie": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HALF_AN_APPLE_PIE"},
    "Half a summer pie": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HALF_A_SUMMER_PIE"},
    "H.A.M. boots": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_BOOTS"},
    "H.A.M. cloak": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_CLOAK"},
    "H.A.M. gloves": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_GLOVES"},
    "H.A.M. hood": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_HOOD"},
    "H.A.M. logo": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_LOGO"},
    "H.A.M. robe": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_ROBE"},
    "H.A.M. shirt": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_SHIRT"},
    "Harralander seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HARRALANDER_SEED"},
    "Irit seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.IRIT_SEED"},
    "Impious ashes": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.IMPIOUS_ASHES"},
    "Iron javelin": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.IRON_JAVELIN"},
    "Iron spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.IRON_SPEAR"},
    "Jangerberry seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.JANGERBERRY_SEED"},
    "Jug of wine": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.JUG_OF_WINE"},
    "Kebab": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.KEBAB"},
    "Jug": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.JUG"},
    "Knife": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.KNIFE"},
    "Kwuarm seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.KWUARM_SEED"},
    "Lantadyme seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LANTADYME_SEED"},
    "Limpwurt root": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LIMPWURT_ROOT"},
    "Limpwurt seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LIMPWURT_SEED"},
    "Loop half of a key": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LOOP_HALF_OF_A_KEY"},
    "Long bone": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LONG_BONE"},
    "Magic staff": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MAGIC_STAFF"},
    "Marrentill seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MARRENTILL_SEED"},
    "Lava battlestaff": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 3053; "
            "RuneScape Wiki Lava battlestaff oldid 6037449"
        ),
        "source_item_id": 3053,
        "stackable": False,
        "tradeable": True,
    },
    "Mystic hat (dark)": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4099; "
            "RuneScape Wiki Mystic hat oldid 5971728"
        ),
        "source_item_id": 4099,
        "stackable": False,
        "tradeable": True,
    },
    "Mystic boots (dark)": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4107; "
            "RuneScape Wiki Mystic boots oldid 6315992"
        ),
        "source_item_id": 4107,
        "stackable": False,
        "tradeable": True,
    },
    "Mystic robe bottom (dark)": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4103; "
            "RuneScape Wiki Mystic robe bottom oldid 6436814"
        ),
        "source_item_id": 4103,
        "stackable": False,
        "tradeable": True,
    },
    "Mystic hat (light)": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4109; "
            "RuneScape Wiki Basilisk oldid 6565796"
        ),
        "source_item_id": 4109,
        "stackable": False,
        "tradeable": True,
    },
    "Basilisk head": {
        "category": "material",
        "source": (
            "game-main data/cfg/items.yml item 7977; "
            "RuneScape Wiki Basilisk oldid 6565796"
        ),
        "source_item_id": 7977,
        "stackable": False,
        "tradeable": False,
    },
    "Black boots": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4125; "
            "RuneScape Wiki Black boots oldid 6426419"
        ),
        "source_item_id": 4125,
        "stackable": False,
        "tradeable": True,
    },
    "Mithril boots": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4127; "
            "RuneScape Wiki Mithril armoured boots oldid 6007782"
        ),
        "source_item_id": 4127,
        "stackable": False,
        "tradeable": True,
    },
    "Mithril spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MITHRIL_SPEAR"},
    "Monkey bones": {
        "category": "material",
        "source": "RuneScape Wiki Monkey oldid 6552407; Darkan item config 3183",
        "source_item_id": 3183,
        "stackable": False,
        "tradeable": True,
    },
    "Muddy key": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MUDDY_KEY"},
    "Needle": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.NEEDLE"},
    "Obsidian cape": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.OBSIDIAN_CAPE"},
    "Obsidian charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.OBSIDIAN_CHARM"},
    "Onion seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ONION_SEED"},
    "Poison ivy seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.POISON_IVY_SEED"},
    "Potato seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.POTATO_SEED"},
    "Rake": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RAKE"},
    "Ranarr seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RANARR_SEED"},
    "Raw rat meat": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RAW_RAT_MEAT"},
    "Red bead": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RED_BEAD"},
    "Rusty sword": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RUSTY_SWORD"},
    "Rune javelin": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RUNE_JAVELIN"},
    "Rune spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RUNE_SPEAR"},
    "Royal cape": {
        "category": "equipment",
        "source": "RuneScape Wiki Royal cape oldid 6308196; Darkan item config 24315",
        "source_item_id": 24315,
        "stackable": False,
        "tradeable": True,
    },
    "Spiked gauntlets": {
        "category": "equipment",
        "source": "RuneScape Wiki Spiked gauntlets oldid 5827717; Darkan item config 23035",
        "source_item_id": 23035,
        "stackable": False,
        "tradeable": False,
    },
    "Secateurs": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SECATEURS"},
    "Seed dibber": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SEED_DIBBER"},
    "Shears": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SHEARS"},
    "Shield left half": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SHIELD_LEFT_HALF"},
    "Sling": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SLING"},
    "Snapdragon seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SNAPDRAGON_SEED"},
    "Spinach roll": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SPINACH_ROLL"},
    "Staff": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF"},
    "Staff of air": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_AIR"},
    "Staff of water": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_WATER"},
    "Staff of earth": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_EARTH"},
    "Staff of fire": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_FIRE"},
    "Steel spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STEEL_SPEAR"},
    "Steel boots": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4123; "
            "OpenRS2 revision-742 item 4123"
        ),
        "source_item_id": 4123,
        "stackable": False,
        "tradeable": True,
    },
    "Strawberry seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STRAWBERRY_SEED"},
    "Super defence (1)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_DEFENCE_1"},
    "Super antipoison (1)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_1"},
    "Super antipoison (2)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_2"},
    "Super antipoison (3)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_3"},
    "Super antipoison (4)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_4"},
    "Super strength (1)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_STRENGTH_1"},
    "Sweetcorn seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SWEETCORN_SEED"},
    "Tarromin seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TARROMIN_SEED"},
    "Thread": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.THREAD"},
    "Toadflax seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOADFLAX_SEED"},
    "Tooth half of a key": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOOTH_HALF_OF_A_KEY"},
    "Tomato seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOMATO_SEED"},
    "Tokkul": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOKKUL"},
    "Toktz-ket-xil": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOKTZKETXIL"},
    "Torstol seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TORSTOL_SEED"},
    "Tzhaar-ket-om": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TZHAARKETOM"},
    "Unicorn horn": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.UNICORN_HORN"},
    "Vial": {"category": "crafted", "source": f"{ITEM_ID_SOURCE_PATH}: Items.VIAL"},
    "Vial of water": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.VIAL_OF_WATER"},
    "Vecna skull": {
        "category": "material",
        "source": (
            "Darkan cache item 20667; "
            "Darkan rdt_mega_rare special table item 20667"
        ),
        "source_item_id": 20667,
        "stackable": False,
        "tradeable": True,
    },
    "Watering can (8)": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WATERING_CAN_8"},
    "Watermelon seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WATERMELON_SEED"},
    "White bead": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WHITE_BEAD"},
    "Whiteberry seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WHITEBERRY_SEED"},
    "Wildblood seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WILDBLOOD_SEED"},
    "Wooden shield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WOODEN_SHIELD"},
    "Wolf bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WOLF_BONES"},
    "Wizard hat": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WIZARD_HAT"},
    "Yellow bead": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.YELLOW_BEAD"},
    "Zamorak robe bottom": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ZAMORAK_ROBE"},
    "Zamorak robe top": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ZAMORAK_ROBE_1035"},
    "Tinderbox": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TINDERBOX_590"},
    "Gold charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GOLD_CHARM"},
    "Green charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GREEN_CHARM"},
    "Crimson charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CRIMSON_CHARM"},
    "Blue charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLUE_CHARM"},
}


COMBAT_TARGET_GROUP_ORDER: Tuple[str, ...] = (
    "Lumbridge",
    "Spiders",
    "Scorpions",
    "Goblins",
    "Humanoids",
    "TzHaar",
    "Coastal",
)
