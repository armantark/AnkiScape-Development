"""2011Scape and pinned pre-EOC Fletching data for AnkiScape.

The local rev-667 plugin is the baseline. Pinned 2011 knowledge-base rows are
used only for historically live Fletching actions that are absent from the
plugin surface, notably gem bolt tips and tipped bolts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


FLETCHING_SOURCE_ROOT = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/fletching"
)
WHITTLE_ITEM_SOURCE_PATH = f"{FLETCHING_SOURCE_ROOT}/whittling/WhittleItem.kt"
LOG_DATA_SOURCE_PATH = f"{FLETCHING_SOURCE_ROOT}/whittling/LogData.kt"
WHITTLE_ACTION_SOURCE_PATH = f"{FLETCHING_SOURCE_ROOT}/whittling/WhittleAction.kt"
BOW_ITEM_SOURCE_PATH = f"{FLETCHING_SOURCE_ROOT}/stringing/BowItem.kt"
STRING_DATA_SOURCE_PATH = f"{FLETCHING_SOURCE_ROOT}/stringing/StringData.kt"
BOW_STRING_ACTION_SOURCE_PATH = f"{FLETCHING_SOURCE_ROOT}/stringing/BowStringAction.kt"
COMBINATION_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/items/combine/CombinationData.kt"
)
FEATHERING_DATA_SOURCE_PATH = f"{FLETCHING_SOURCE_ROOT}/feathering/FeatheringData.kt"
FEATHER_ACTION_SOURCE_PATH = f"{FLETCHING_SOURCE_ROOT}/feathering/FeatherAction.kt"
ARROW_DATA_SOURCE_PATH = f"{FLETCHING_SOURCE_ROOT}/arrows/ArrowData.kt"
ARROW_ACTION_SOURCE_PATH = f"{FLETCHING_SOURCE_ROOT}/arrows/ArrowAction.kt"
SLAYER_REWARDS_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/inter/slayer/slayer_rewards.plugin.kts"
)
ITEMS_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"
PRE_EOC_BOLTS_SOURCE = "https://www.2011.rs/kb/fletching_making_bolts"
PRE_EOC_DARTS_SOURCE = "https://www.2011.rs/kb/fletching_making_darts"
PRE_EOC_HUNTER_SOURCE = "https://runescape.wiki/w/Hunter?oldid=6484443"

BROAD_FLETCHING_ABILITY = "broad_fletching"
DEFAULT_FLETCHING_TARGET = "arrow_shafts"
FEATHER_ALTERNATIVES = (
    "Feather",
    "Red feather",
    "Orange feather",
    "Yellow feather",
    "Blue feather",
    "Stripy feather",
)

FLETCHING_GROUP_LABELS = {
    "whittling": "Whittling",
    "stringing": "Stringing",
    "combination": "Combinations",
    "arrows": "Arrows",
    "feathering": "Feathering",
    "bolts": "Bolts",
    "darts": "Darts",
    "specials": "Specials",
}
FLETCHING_GROUP_ORDER = tuple(FLETCHING_GROUP_LABELS.keys())


@dataclass(frozen=True)
class FletchingTarget:
    id: str
    display_name: str
    group: str
    action: str
    level: int
    base_exp: float
    requirements: Tuple[Tuple[str, int], ...]
    output_item: str
    output_qty: int = 1
    source: str = WHITTLE_ITEM_SOURCE_PATH
    source_enum: str = ""
    source_item_id: int = 0
    unlock_abilities: Tuple[str, ...] = ()
    notes: str = ""
    tradeable: bool = True
    sort_order: int = 0
    required_items: Tuple[Tuple[str, int], ...] = ()


def _req(*pairs: Tuple[str, int]) -> Tuple[Tuple[str, int], ...]:
    return tuple(pairs)


def _target(
    id: str,
    display_name: str,
    group: str,
    action: str,
    level: int,
    base_exp: float,
    requirements: Tuple[Tuple[str, int], ...],
    output_item: str,
    output_qty: int = 1,
    source: str = WHITTLE_ITEM_SOURCE_PATH,
    source_enum: str = "",
    source_item_id: int = 0,
    unlock_abilities: Tuple[str, ...] = (),
    notes: str = "",
    sort_order: int = 0,
    required_items: Tuple[Tuple[str, int], ...] = (),
) -> FletchingTarget:
    return FletchingTarget(
        id=id,
        display_name=display_name,
        group=group,
        action=action,
        level=level,
        base_exp=base_exp,
        requirements=requirements,
        output_item=output_item,
        output_qty=output_qty,
        source=source,
        source_enum=source_enum,
        source_item_id=source_item_id,
        unlock_abilities=unlock_abilities,
        notes=notes,
        sort_order=sort_order,
        required_items=required_items,
    )


FLETCHING_TARGETS: Tuple[FletchingTarget, ...] = (
    _target("arrow_shafts", "Arrow shafts (Logs)", "whittling", "whittle", 1, 5.0, _req(("Logs", 1)), "Arrow shafts", 15, WHITTLE_ITEM_SOURCE_PATH, "ARROW_SHAFT_15", 52, sort_order=10),
    _target("shortbow_u", "Shortbow (u)", "whittling", "whittle", 5, 5.0, _req(("Logs", 1)), "Shortbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "SHORTBOW_U", 50, sort_order=20),
    _target("longbow_u", "Longbow (u)", "whittling", "whittle", 10, 10.0, _req(("Logs", 1)), "Longbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "LONGBOW_U", 48, sort_order=30),
    _target("wooden_stock", "Wooden stock", "whittling", "whittle", 9, 6.0, _req(("Logs", 1)), "Wooden stock", 1, WHITTLE_ITEM_SOURCE_PATH, "WOODEN_STOCK", 9440, sort_order=40),
    _target("oak_shortbow_u", "Oak shortbow (u)", "whittling", "whittle", 20, 16.5, _req(("Oak logs", 1)), "Oak shortbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "OAK_SHORTBOW_U", 54, sort_order=50),
    _target("oak_longbow_u", "Oak longbow (u)", "whittling", "whittle", 25, 25.0, _req(("Oak logs", 1)), "Oak longbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "OAK_LONGBOW_U", 56, sort_order=60),
    _target("oak_stock", "Oak stock", "whittling", "whittle", 24, 16.0, _req(("Oak logs", 1)), "Oak stock", 1, WHITTLE_ITEM_SOURCE_PATH, "OAK_STOCK", 9442, sort_order=70),
    _target("willow_shortbow_u", "Willow shortbow (u)", "whittling", "whittle", 35, 33.3, _req(("Willow logs", 1)), "Willow shortbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "WILLOW_SHORTBOW_U", 60, sort_order=80),
    _target("willow_longbow_u", "Willow longbow (u)", "whittling", "whittle", 40, 41.5, _req(("Willow logs", 1)), "Willow longbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "WILLOW_LONGBOW_U", 58, sort_order=90),
    _target("willow_stock", "Willow stock", "whittling", "whittle", 39, 22.0, _req(("Willow logs", 1)), "Willow stock", 1, WHITTLE_ITEM_SOURCE_PATH, "WILLOW_STOCK", 9444, sort_order=100),
    _target("teak_stock", "Teak stock", "whittling", "whittle", 46, 27.0, _req(("Teak logs", 1)), "Teak stock", 1, WHITTLE_ITEM_SOURCE_PATH, "TEAK_STOCK", 9446, sort_order=110),
    _target("maple_shortbow_u", "Maple shortbow (u)", "whittling", "whittle", 50, 50.0, _req(("Maple logs", 1)), "Maple shortbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "MAPLE_SHORTBOW_U", 64, sort_order=120),
    _target("maple_longbow_u", "Maple longbow (u)", "whittling", "whittle", 55, 58.3, _req(("Maple logs", 1)), "Maple longbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "MAPLE_LONGBOW_U", 62, sort_order=130),
    _target("maple_stock", "Maple stock", "whittling", "whittle", 54, 32.0, _req(("Maple logs", 1)), "Maple stock", 1, WHITTLE_ITEM_SOURCE_PATH, "MAPLE_STOCK", 9448, sort_order=140),
    _target("mahogany_stock", "Mahogany stock", "whittling", "whittle", 61, 41.0, _req(("Mahogany logs", 1)), "Mahogany stock", 1, WHITTLE_ITEM_SOURCE_PATH, "MAHOGANY_STOCK", 9450, sort_order=150),
    _target("yew_shortbow_u", "Yew shortbow (u)", "whittling", "whittle", 65, 67.5, _req(("Yew logs", 1)), "Yew shortbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "YEW_SHORTBOW_U", 68, sort_order=160),
    _target("yew_longbow_u", "Yew longbow (u)", "whittling", "whittle", 70, 75.0, _req(("Yew logs", 1)), "Yew longbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "YEW_LONGBOW_U", 66, sort_order=170),
    _target("yew_stock", "Yew stock", "whittling", "whittle", 69, 50.0, _req(("Yew logs", 1)), "Yew stock", 1, WHITTLE_ITEM_SOURCE_PATH, "YEW_STOCK", 9452, sort_order=180),
    _target("magic_shortbow_u", "Magic shortbow (u)", "whittling", "whittle", 80, 83.3, _req(("Magic logs", 1)), "Magic shortbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "MAGIC_SHORTBOW_U", 72, sort_order=190),
    _target("magic_longbow_u", "Magic longbow (u)", "whittling", "whittle", 85, 91.5, _req(("Magic logs", 1)), "Magic longbow (u)", 1, WHITTLE_ITEM_SOURCE_PATH, "MAGIC_LONGBOW_U", 70, sort_order=200),
    _target("string_shortbow", "String shortbow", "stringing", "string", 5, 5.0, _req(("Shortbow (u)", 1), ("Bow string", 1)), "Shortbow", 1, STRING_DATA_SOURCE_PATH, "SHORTBOW", 841, sort_order=10),
    _target("string_longbow", "String longbow", "stringing", "string", 10, 10.0, _req(("Longbow (u)", 1), ("Bow string", 1)), "Longbow", 1, STRING_DATA_SOURCE_PATH, "LONGBOW", 839, sort_order=20),
    _target("string_oak_shortbow", "String oak shortbow", "stringing", "string", 20, 16.5, _req(("Oak shortbow (u)", 1), ("Bow string", 1)), "Oak shortbow", 1, STRING_DATA_SOURCE_PATH, "OAK_SHORTBOW", 843, sort_order=30),
    _target("string_oak_longbow", "String oak longbow", "stringing", "string", 25, 25.0, _req(("Oak longbow (u)", 1), ("Bow string", 1)), "Oak longbow", 1, STRING_DATA_SOURCE_PATH, "OAK_LONGBOW", 845, sort_order=40),
    _target("string_willow_shortbow", "String willow shortbow", "stringing", "string", 35, 33.3, _req(("Willow shortbow (u)", 1), ("Bow string", 1)), "Willow shortbow", 1, STRING_DATA_SOURCE_PATH, "WILLOW_SHORTBOW", 849, sort_order=50),
    _target("string_willow_longbow", "String willow longbow", "stringing", "string", 40, 41.5, _req(("Willow longbow (u)", 1), ("Bow string", 1)), "Willow longbow", 1, STRING_DATA_SOURCE_PATH, "WILLOW_LONGBOW", 847, sort_order=60),
    _target("string_maple_shortbow", "String maple shortbow", "stringing", "string", 50, 50.0, _req(("Maple shortbow (u)", 1), ("Bow string", 1)), "Maple shortbow", 1, STRING_DATA_SOURCE_PATH, "MAPLE_SHORTBOW", 853, sort_order=70),
    _target("string_maple_longbow", "String maple longbow", "stringing", "string", 55, 58.3, _req(("Maple longbow (u)", 1), ("Bow string", 1)), "Maple longbow", 1, STRING_DATA_SOURCE_PATH, "MAPLE_LONGBOW", 851, sort_order=80),
    _target("string_yew_shortbow", "String yew shortbow", "stringing", "string", 65, 67.5, _req(("Yew shortbow (u)", 1), ("Bow string", 1)), "Yew shortbow", 1, STRING_DATA_SOURCE_PATH, "YEW_SHORTBOW", 857, sort_order=90),
    _target("string_yew_longbow", "String yew longbow", "stringing", "string", 70, 75.0, _req(("Yew longbow (u)", 1), ("Bow string", 1)), "Yew longbow", 1, STRING_DATA_SOURCE_PATH, "YEW_LONGBOW", 855, sort_order=100),
    _target("string_magic_shortbow", "String magic shortbow", "stringing", "string", 80, 83.3, _req(("Magic shortbow (u)", 1), ("Bow string", 1)), "Magic shortbow", 1, STRING_DATA_SOURCE_PATH, "MAGIC_SHORTBOW", 861, sort_order=110),
    _target("string_magic_longbow", "String magic longbow", "stringing", "string", 85, 91.5, _req(("Magic longbow (u)", 1), ("Bow string", 1)), "Magic longbow", 1, STRING_DATA_SOURCE_PATH, "MAGIC_LONGBOW", 859, sort_order=120),
    _target("combine_bronze_cbow_u", "Bronze c'bow (u)", "combination", "combine", 9, 0.0, _req(("Bronze limbs", 1), ("Wooden stock", 1)), "Bronze c'bow (u)", 1, COMBINATION_SOURCE_PATH, "BRONZE_CBOW_U", 9454, sort_order=10),
    _target("combine_bronze_crossbow", "Bronze crossbow", "combination", "combine", 9, 0.0, _req(("Bronze c'bow (u)", 1), ("Crossbow string", 1)), "Bronze crossbow", 1, COMBINATION_SOURCE_PATH, "BRONZE_CROSSBOW", 9174, sort_order=20),
    _target("combine_blurite_cbow_u", "Blurite c'bow (u)", "combination", "combine", 24, 0.0, _req(("Blurite limbs", 1), ("Oak stock", 1)), "Blurite c'bow (u)", 1, COMBINATION_SOURCE_PATH, "BLURITE_CBOW_U", 9456, sort_order=30),
    _target("combine_blurite_crossbow", "Blurite crossbow", "combination", "combine", 24, 0.0, _req(("Blurite c'bow (u)", 1), ("Crossbow string", 1)), "Blurite crossbow", 1, COMBINATION_SOURCE_PATH, "BLURITE_CROSSBOW", 9176, sort_order=40),
    _target("combine_iron_cbow_u", "Iron c'bow (u)", "combination", "combine", 39, 0.0, _req(("Iron limbs", 1), ("Willow stock", 1)), "Iron c'bow (u)", 1, COMBINATION_SOURCE_PATH, "IRON_CBOW_U", 9457, sort_order=50),
    _target("combine_iron_crossbow", "Iron crossbow", "combination", "combine", 39, 0.0, _req(("Iron c'bow (u)", 1), ("Crossbow string", 1)), "Iron crossbow", 1, COMBINATION_SOURCE_PATH, "IRON_CROSSBOW", 9177, sort_order=60),
    _target("combine_steel_cbow_u", "Steel c'bow (u)", "combination", "combine", 46, 0.0, _req(("Steel limbs", 1), ("Teak stock", 1)), "Steel c'bow (u)", 1, COMBINATION_SOURCE_PATH, "STEEL_CBOW_U", 9459, sort_order=70),
    _target("combine_steel_crossbow", "Steel crossbow", "combination", "combine", 46, 0.0, _req(("Steel c'bow (u)", 1), ("Crossbow string", 1)), "Steel crossbow", 1, COMBINATION_SOURCE_PATH, "STEEL_CROSSBOW", 9179, sort_order=80),
    _target("combine_mithril_cbow_u", "Mithril c'bow (u)", "combination", "combine", 54, 0.0, _req(("Mithril limbs", 1), ("Maple stock", 1)), "Mithril c'bow (u)", 1, COMBINATION_SOURCE_PATH, "MITHRIL_CBOW_U", 9461, sort_order=90),
    _target("combine_mithril_crossbow", "Mith crossbow", "combination", "combine", 54, 0.0, _req(("Mithril c'bow (u)", 1), ("Crossbow string", 1)), "Mith crossbow", 1, COMBINATION_SOURCE_PATH, "MITHRIL_CROSSBOW", 9181, sort_order=100),
    _target("combine_adamant_cbow_u", "Adamant c'bow (u)", "combination", "combine", 61, 0.0, _req(("Adamantite limbs", 1), ("Mahogany stock", 1)), "Adamant c'bow (u)", 1, COMBINATION_SOURCE_PATH, "ADAMANT_CBOW_U", 9463, sort_order=110),
    _target("combine_adamant_crossbow", "Adamant crossbow", "combination", "combine", 61, 0.0, _req(("Adamant c'bow (u)", 1), ("Crossbow string", 1)), "Adamant crossbow", 1, COMBINATION_SOURCE_PATH, "ADAMANT_CROSSBOW", 9183, sort_order=120),
    _target("combine_rune_cbow_u", "Runite c'bow (u)", "combination", "combine", 69, 0.0, _req(("Runite limbs", 1), ("Yew stock", 1)), "Runite c'bow (u)", 1, COMBINATION_SOURCE_PATH, "RUNE_CBOW_U", 9465, sort_order=130),
    _target("combine_rune_crossbow", "Rune crossbow", "combination", "combine", 69, 0.0, _req(("Runite c'bow (u)", 1), ("Crossbow string", 1)), "Rune crossbow", 1, COMBINATION_SOURCE_PATH, "RUNE_CROSSBOW", 9185, sort_order=140),
    _target("headless_arrows", "Headless arrows", "feathering", "feather", 1, 15.0, _req(("Arrow shafts", 15), ("Feather", 15)), "Headless arrows", 15, FEATHERING_DATA_SOURCE_PATH, "HEADLESS_ARROW", 53, sort_order=10),
    _target("bronze_arrows", "Bronze arrows", "arrows", "arrow", 1, 19.5, _req(("Headless arrows", 15), ("Bronze arrowtips", 15)), "Bronze arrows", 15, ARROW_DATA_SOURCE_PATH, "BRONZE", 882, sort_order=10),
    _target("iron_arrows", "Iron arrows", "arrows", "arrow", 15, 37.5, _req(("Headless arrows", 15), ("Iron arrowtips", 15)), "Iron arrows", 15, ARROW_DATA_SOURCE_PATH, "IRON", 884, sort_order=20),
    _target("steel_arrows", "Steel arrows", "arrows", "arrow", 30, 75.0, _req(("Headless arrows", 15), ("Steel arrowtips", 15)), "Steel arrows", 15, ARROW_DATA_SOURCE_PATH, "STEEL", 886, sort_order=30),
    _target("mithril_arrows", "Mithril arrows", "arrows", "arrow", 45, 112.5, _req(("Headless arrows", 15), ("Mithril arrowtips", 15)), "Mithril arrows", 15, ARROW_DATA_SOURCE_PATH, "MITHRIL", 888, sort_order=40),
    _target("broad_arrows", "Broad arrows", "arrows", "arrow", 52, 150.0, _req(("Headless arrows", 15), ("Broad arrow heads", 15)), "Broad arrows", 15, ARROW_DATA_SOURCE_PATH, "BROAD", 4160, (BROAD_FLETCHING_ABILITY,), sort_order=50),
    _target("adamant_arrows", "Adamant arrows", "arrows", "arrow", 60, 150.0, _req(("Headless arrows", 15), ("Adamant arrowtips", 15)), "Adamant arrows", 15, ARROW_DATA_SOURCE_PATH, "ADAMANT", 890, sort_order=60),
    _target("rune_arrows", "Rune arrows", "arrows", "arrow", 75, 187.5, _req(("Headless arrows", 15), ("Rune arrowtips", 15)), "Rune arrows", 15, ARROW_DATA_SOURCE_PATH, "RUNE", 892, sort_order=70),
    _target("dragon_arrows", "Dragon arrows", "arrows", "arrow", 90, 225.0, _req(("Headless arrows", 15), ("Dragon arrowtips", 15)), "Dragon arrows", 15, ARROW_DATA_SOURCE_PATH, "DRAGON", 11212, sort_order=80),
    _target("ogre_arrow_shaft", "Ogre arrow shaft", "specials", "whittle", 5, 1.6, _req(("Achey tree logs", 1)), "Ogre arrow shaft", 1, WHITTLE_ITEM_SOURCE_PATH, "OGRE_ARROW_SHAFT", 2864, notes="The local plugin awards one shaft; the 2011 KB describes a variable multi-shaft action.", sort_order=10),
    _target("flighted_ogre_arrows", "Flighted ogre arrows", "specials", "feather", 1, 5.4, _req(("Ogre arrow shaft", 6), ("Feather", 24)), "Flighted ogre arrows", 6, FEATHERING_DATA_SOURCE_PATH, "FLIGHTED_OGRE_ARROW", 2865, sort_order=20),
    _target("unstrung_comp_bow", "Unstrung comp bow", "specials", "whittle", 30, 45.0, _req(("Achey tree logs", 1)), "Unstrung comp bow", 1, WHITTLE_ITEM_SOURCE_PATH, "UNSTRUNG_COMP_BOW", 4825, notes="The matching comp ogre bow stringing enum is commented out in StringData.kt, so only the live whittling row ships.", sort_order=30),
    _target("feather_bronze_bolts", "Feather bronze bolts", "bolts", "feather", 9, 5.0, _req(("Bronze bolts (unf)", 10), ("Feather", 10)), "Bronze bolts", 10, FEATHERING_DATA_SOURCE_PATH, "BRONZE_BOLT", 877, sort_order=10),
    _target("feather_blurite_bolts", "Feather blurite bolts", "bolts", "feather", 24, 10.0, _req(("Blurite bolts (unf)", 10), ("Feather", 10)), "Blurite bolts", 10, FEATHERING_DATA_SOURCE_PATH, "BLURITE_BOLT", 9139, sort_order=20),
    _target("feather_iron_bolts", "Feather iron bolts", "bolts", "feather", 39, 15.0, _req(("Iron bolts (unf)", 10), ("Feather", 10)), "Iron bolts", 10, FEATHERING_DATA_SOURCE_PATH, "IRON_BOLT", 9140, sort_order=30),
    _target("feather_silver_bolts", "Feather silver bolts", "bolts", "feather", 43, 25.0, _req(("Silver bolts (unf)", 10), ("Feather", 10)), "Silver bolts", 10, FEATHERING_DATA_SOURCE_PATH, "SILVER_BOLT", 9145, sort_order=40),
    _target("feather_steel_bolts", "Feather steel bolts", "bolts", "feather", 46, 35.0, _req(("Steel bolts (unf)", 10), ("Feather", 10)), "Steel bolts", 10, FEATHERING_DATA_SOURCE_PATH, "STEEL_BOLT", 9141, sort_order=50),
    _target("feather_mithril_bolts", "Feather mithril bolts", "bolts", "feather", 54, 50.0, _req(("Mithril bolts (unf)", 10), ("Feather", 10)), "Mithril bolts", 10, FEATHERING_DATA_SOURCE_PATH, "MITHRIL_BOLT", 9142, sort_order=60),
    _target("feather_broad_bolts", "Feather broad bolts", "bolts", "feather", 55, 30.0, _req(("Unfinished broad bolts", 10), ("Feather", 10)), "Broad-tipped bolts", 10, FEATHERING_DATA_SOURCE_PATH, "BROAD_BOLT", 13280, (BROAD_FLETCHING_ABILITY,), sort_order=70),
    _target("feather_adamant_bolts", "Feather adamant bolts", "bolts", "feather", 61, 70.0, _req(("Adamant bolts (unf)", 10), ("Feather", 10)), "Adamant bolts", 10, FEATHERING_DATA_SOURCE_PATH, "ADAMANT_BOLT", 9143, sort_order=80),
    _target("feather_runite_bolts", "Feather runite bolts", "bolts", "feather", 69, 100.0, _req(("Runite bolts (unf)", 10), ("Feather", 10)), "Runite bolts", 10, FEATHERING_DATA_SOURCE_PATH, "RUNITE_BOLT", 9144, sort_order=90),
    _target("cut_opal_bolt_tips", "Cut opal bolt tips", "bolts", "cut_tip", 11, 1.0, _req(("Opal", 1)), "Opal bolt tips", 12, PRE_EOC_BOLTS_SOURCE, sort_order=110),
    _target("tip_opal_bolts", "Tip opal bolts", "bolts", "tip_bolt", 11, 16.0, _req(("Bronze bolts", 10), ("Opal bolt tips", 10)), "Opal bolts", 10, PRE_EOC_BOLTS_SOURCE, sort_order=115),
    _target("cut_jade_bolt_tips", "Cut jade bolt tips", "bolts", "cut_tip", 26, 2.0, _req(("Jade", 1)), "Jade bolt tips", 12, PRE_EOC_BOLTS_SOURCE, sort_order=120),
    _target("tip_jade_bolts", "Tip jade bolts", "bolts", "tip_bolt", 26, 24.0, _req(("Blurite bolts", 10), ("Jade bolt tips", 10)), "Jade bolts", 10, PRE_EOC_BOLTS_SOURCE, sort_order=125),
    _target("cut_pearl_bolt_tips", "Cut pearl bolt tips", "bolts", "cut_tip", 41, 3.0, _req(("Oyster pearl", 1)), "Pearl bolt tips", 6, PRE_EOC_BOLTS_SOURCE, sort_order=130),
    _target("tip_pearl_bolts", "Tip pearl bolts", "bolts", "tip_bolt", 41, 32.0, _req(("Iron bolts", 10), ("Pearl bolt tips", 10)), "Pearl bolts", 10, PRE_EOC_BOLTS_SOURCE, sort_order=135),
    _target(
        "fletch_long_kebbit_bolts",
        "Fletch long kebbit bolts",
        "bolts",
        "chisel",
        42,
        7.98,
        _req(("Long kebbit spike", 1)),
        "Long kebbit bolts",
        6,
        PRE_EOC_HUNTER_SOURCE,
        "LONG_KEBBIT_BOLTS",
        10159,
        notes="One Long kebbit spike produces six bolts at 1.33 Fletching XP each.",
        sort_order=138,
        required_items=_req(("Chisel", 1)),
    ),
    _target("cut_red_topaz_bolt_tips", "Cut red topaz bolt tips", "bolts", "cut_tip", 48, 3.0, _req(("Red topaz", 1)), "Topaz bolt tips", 12, PRE_EOC_BOLTS_SOURCE, sort_order=140),
    _target("tip_topaz_bolts", "Tip topaz bolts", "bolts", "tip_bolt", 48, 39.0, _req(("Steel bolts", 10), ("Topaz bolt tips", 10)), "Topaz bolts", 10, PRE_EOC_BOLTS_SOURCE, sort_order=145),
    _target("tip_barbed_bolts", "Tip barbed bolts", "bolts", "tip_bolt", 51, 95.0, _req(("Bronze bolts", 10), ("Barb bolttips", 10)), "Barbed bolts", 10, PRE_EOC_BOLTS_SOURCE, sort_order=150),
    _target("cut_sapphire_bolt_tips", "Cut sapphire bolt tips", "bolts", "cut_tip", 56, 4.0, _req(("Sapphire", 1)), "Sapphire bolt tips", 12, PRE_EOC_BOLTS_SOURCE, sort_order=160),
    _target("tip_sapphire_bolts", "Tip sapphire bolts", "bolts", "tip_bolt", 56, 47.0, _req(("Mithril bolts", 10), ("Sapphire bolt tips", 10)), "Sapphire bolts", 10, PRE_EOC_BOLTS_SOURCE, sort_order=165),
    _target("cut_emerald_bolt_tips", "Cut emerald bolt tips", "bolts", "cut_tip", 58, 5.0, _req(("Emerald", 1)), "Emerald bolt tips", 12, PRE_EOC_BOLTS_SOURCE, sort_order=170),
    _target("tip_emerald_bolts", "Tip emerald bolts", "bolts", "tip_bolt", 58, 55.0, _req(("Mithril bolts", 10), ("Emerald bolt tips", 10)), "Emerald bolts", 10, PRE_EOC_BOLTS_SOURCE, sort_order=175),
    _target("attach_mithril_grapple", "Attach mithril grapple", "bolts", "tip_bolt", 59, 11.0, _req(("Mithril bolts", 1), ("Mith grapple tip", 1)), "Mith grapple", 1, PRE_EOC_BOLTS_SOURCE, sort_order=180),
    _target("cut_ruby_bolt_tips", "Cut ruby bolt tips", "bolts", "cut_tip", 63, 6.0, _req(("Ruby", 1)), "Ruby bolt tips", 12, PRE_EOC_BOLTS_SOURCE, sort_order=190),
    _target("tip_ruby_bolts", "Tip ruby bolts", "bolts", "tip_bolt", 63, 63.0, _req(("Adamant bolts", 10), ("Ruby bolt tips", 10)), "Ruby bolts", 10, PRE_EOC_BOLTS_SOURCE, sort_order=195),
    _target("cut_diamond_bolt_tips", "Cut diamond bolt tips", "bolts", "cut_tip", 65, 7.0, _req(("Diamond", 1)), "Diamond bolt tips", 12, PRE_EOC_BOLTS_SOURCE, sort_order=200),
    _target("tip_diamond_bolts", "Tip diamond bolts", "bolts", "tip_bolt", 65, 70.0, _req(("Adamant bolts", 10), ("Diamond bolt tips", 10)), "Diamond bolts", 10, PRE_EOC_BOLTS_SOURCE, sort_order=205),
    _target("cut_dragonstone_bolt_tips", "Cut dragonstone bolt tips", "bolts", "cut_tip", 71, 8.0, _req(("Dragonstone", 1)), "Dragon bolt tips", 12, PRE_EOC_BOLTS_SOURCE, sort_order=210),
    _target("tip_dragon_bolts", "Tip dragon bolts", "bolts", "tip_bolt", 71, 82.0, _req(("Runite bolts", 10), ("Dragon bolt tips", 10)), "Dragon bolts", 10, PRE_EOC_BOLTS_SOURCE, sort_order=215),
    _target("cut_onyx_bolt_tips", "Cut onyx bolt tips", "bolts", "cut_tip", 73, 9.0, _req(("Onyx", 1)), "Onyx bolt tips", 24, PRE_EOC_BOLTS_SOURCE, sort_order=220),
    _target("tip_onyx_bolts", "Tip onyx bolts", "bolts", "tip_bolt", 73, 94.0, _req(("Runite bolts", 10), ("Onyx bolt tips", 10)), "Onyx bolts", 10, PRE_EOC_BOLTS_SOURCE, sort_order=225),
    _target("fletch_bronze_darts", "Fletch bronze darts", "darts", "feather", 1, 18.0, _req(("Bronze dart tip", 10), ("Feather", 10)), "Bronze darts", 10, FEATHERING_DATA_SOURCE_PATH, "BRONZE_DART", 806, sort_order=10),
    _target("fletch_iron_darts", "Fletch iron darts", "darts", "feather", 22, 38.0, _req(("Iron dart tip", 10), ("Feather", 10)), "Iron darts", 10, FEATHERING_DATA_SOURCE_PATH, "IRON_DART", 807, sort_order=20),
    _target("fletch_steel_darts", "Fletch steel darts", "darts", "feather", 37, 75.0, _req(("Steel dart tip", 10), ("Feather", 10)), "Steel darts", 10, FEATHERING_DATA_SOURCE_PATH, "STEEL_DART", 808, sort_order=30),
    _target("fletch_mithril_darts", "Fletch mithril darts", "darts", "feather", 52, 112.0, _req(("Mithril dart tip", 10), ("Feather", 10)), "Mithril darts", 10, FEATHERING_DATA_SOURCE_PATH, "MITHRIL_DART", 809, sort_order=40),
    _target("fletch_adamant_darts", "Fletch adamant darts", "darts", "feather", 67, 150.0, _req(("Adamant dart tip", 10), ("Feather", 10)), "Adamant darts", 10, FEATHERING_DATA_SOURCE_PATH, "ADAMANT_DART", 810, sort_order=50),
    _target("fletch_rune_darts", "Fletch rune darts", "darts", "feather", 81, 188.0, _req(("Rune dart tip", 10), ("Feather", 10)), "Rune darts", 10, FEATHERING_DATA_SOURCE_PATH, "RUNE_DART", 811, sort_order=60),
    _target("fletch_dragon_darts", "Fletch dragon darts", "darts", "feather", 95, 250.0, _req(("Dragon dart tip", 10), ("Feather", 10)), "Dragon darts", 10, FEATHERING_DATA_SOURCE_PATH, "DRAGON_DART", 11230, notes="Dragon darts are source-live in FeatheringData.kt; tip acquisition remains input-starved in this pass.", sort_order=70),
)

FLETCHING_TARGETS_BY_ID: Dict[str, FletchingTarget] = {target.id: target for target in FLETCHING_TARGETS}

LEGACY_FLETCHING_TARGETS = {
    "Arrow shafts": "arrow_shafts",
    "Arrow shafts (Logs)": "arrow_shafts",
    "Shortbow (u)": "shortbow_u",
    "Oak shortbow (u)": "oak_shortbow_u",
    "Willow shortbow (u)": "willow_shortbow_u",
    "Maple shortbow (u)": "maple_shortbow_u",
    "Yew shortbow (u)": "yew_shortbow_u",
    "Magic shortbow (u)": "magic_shortbow_u",
    "oak_arrow_shafts": "arrow_shafts",
    "willow_arrow_shafts": "arrow_shafts",
    "maple_arrow_shafts": "arrow_shafts",
    "yew_arrow_shafts": "arrow_shafts",
    "magic_arrow_shafts": "arrow_shafts",
    "redwood_arrow_shafts": "arrow_shafts",
}


def _xp_rewards(target: FletchingTarget) -> Tuple[Dict[str, object], ...]:
    return ({"skill_id": "fletching", "amount": target.base_exp},)


def _target_as_dict(target: FletchingTarget) -> Dict[str, object]:
    row = {
        "id": target.id,
        "display_name": target.display_name,
        "group": target.group,
        "action": target.action,
        "level": target.level,
        "exp": target.base_exp,
        "base_exp": target.base_exp,
        "requirements": dict(target.requirements),
        "required_items": dict(target.required_items),
        "output_item": target.output_item,
        "output_qty": target.output_qty,
        "xp_rewards": _xp_rewards(target),
        "source": target.source,
        "source_enum": target.source_enum,
        "source_item_id": target.source_item_id,
        "unlock_abilities": target.unlock_abilities,
        "notes": target.notes,
        "tradeable": target.tradeable,
    }
    if target.action == "feather":
        row["material_options"] = {"Feather": FEATHER_ALTERNATIVES}
    return row


def fletching_targets_as_dict() -> Dict[str, Dict[str, object]]:
    return {target.id: _target_as_dict(target) for target in FLETCHING_TARGETS}


def fletching_output_items() -> Tuple[str, ...]:
    seen: Dict[str, None] = {}
    for target in FLETCHING_TARGETS:
        seen.setdefault(target.output_item, None)
    return tuple(seen.keys())


def fletching_item_names() -> Tuple[str, ...]:
    seen: Dict[str, None] = {}
    for target in FLETCHING_TARGETS:
        seen.setdefault(target.output_item, None)
        for material, _amount in target.requirements:
            seen.setdefault(material, None)
    return tuple(seen.keys())
