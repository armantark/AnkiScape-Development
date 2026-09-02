from __future__ import annotations

from typing import Dict, Tuple

from ..firemaking_data import LIT_LIGHT_SOURCE_ITEMS


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
CHAOS_DRUID_DROP_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "data/npcs/drops/chaos_druid.json"
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
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows", "Broad arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: MAGIC_SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS + RUNE_ARROWS + BROAD_ARROWS",
    },
    "Magic longbow": {
        "equipment_type": "magic_longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows", "Broad arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: MAGIC_LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS + RUNE_ARROWS + BROAD_ARROWS",
    },
    "Rune crossbow": {
        "equipment_type": "rune_crossbow",
        "compatible_ammo": ("Broad-tipped bolts",),
        "source": (
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/content/combat/"
            "RangedWeapon.kt:75-88; Turoth broad-bolt route"
        ),
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
    "Broad arrows": {
        "source_item_id": 4160,
        "source_item_name": "Broad arrow",
        "ranged_strength": 28,
        "source": (
            f"{RANGED_BOW_SOURCE_PATH}: MAGIC_SHORTBOW and MAGIC_LONGBOW; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 4160"
        ),
    },
    "Broad-tipped bolts": {
        "source_item_id": 13280,
        "source_item_name": "Broad-tipped bolts",
        "ranged_strength": 100,
        "source": (
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            "darkan-world-server/src/main/java/com/rs/game/content/combat/"
            "AmmoType.kt:55"
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
from ..magic_data import combat_magic_additions_as_dict

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
    "Slayer's staff": {
        "covered_runes": (),
        "source_item_id": 4170,
        "source": (
            "RuneScape Wiki Slayer Dart oldid=6003441; "
            "Darkan cache item 4170"
        ),
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
