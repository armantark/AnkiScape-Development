"""2011Scape-sourced Crafting data for AnkiScape.

The rows here are transcribed from the local 2011Scape rev 667 Crafting
plugin. Runtime imports only this checked-in Python data; the emulator checkout
is a development-time source audit input.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

try:
    from .urn_data import URN_POTTERY_SOURCE, URN_RUNE_SOURCE, URN_TIERS
except ImportError:
    from urn_data import URN_POTTERY_SOURCE, URN_RUNE_SOURCE, URN_TIERS

CRAFTING_SOURCE_ROOT = "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting"
COMBINATION_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/combine/CombinationData.kt"
ITEMS_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"
DEFAULT_CRAFTING_TARGET = "form_pot_unfired"
LIMESTONE_BRICK_SOURCE = "RuneScape Wiki Limestone brick oldid=6308408 (2012-09-27)"
OIL_LANTERN_SOURCE = "https://runescape.wiki/w/Oil_lantern?oldid=5372911"
SAPPHIRE_LANTERN_SOURCE = "https://runescape.wiki/w/Sapphire_lantern_(lit)?oldid=6092552"


@dataclass(frozen=True)
class CraftingRecipe:
    id: str
    display_name: str
    family: str
    station: str
    level: int
    base_exp: float
    requirements: Tuple[Tuple[str, int], ...]
    output_item: str
    output_qty: int = 1
    source: str = CRAFTING_SOURCE_ROOT
    source_enum: str = ""
    tradeable: bool = True
    category: str = "crafted"
    notes: str = ""
    source_item_id: Optional[int] = None
    # Extra items returned alongside the output (e.g. the emptied bucket from
    # molten glass smelting). Granted per action like the output, never gated.
    byproducts: Tuple[Tuple[str, int], ...] = ()
    required_items: Tuple[Tuple[str, int], ...] = ()
    consume_thread_on_roll: bool = False


@dataclass(frozen=True)
class TanningActivity:
    id: str
    display_name: str
    raw_item: str
    output_item: str
    price: int
    source_enum: str


def _req(*pairs: Tuple[str, int]) -> Tuple[Tuple[str, int], ...]:
    return tuple(pairs)


def _urn_crafting_recipes() -> Tuple[CraftingRecipe, ...]:
    recipes = []
    for tier in URN_TIERS:
        stable_item = tier.item_base.lower().replace(" ", "_")
        unfired_id, non_runed_id, runed_id, _active_id, _full_id = tier.source_item_ids
        recipes.extend(
            (
                CraftingRecipe(
                    f"form_{stable_item}_unf",
                    tier.item_unf,
                    "pottery",
                    "potters_wheel",
                    tier.crafting_level,
                    tier.forming_xp,
                    _req(("Soft clay", 2)),
                    tier.item_unf,
                    source=URN_POTTERY_SOURCE,
                    source_enum=tier.source_enum,
                    source_item_id=unfired_id,
                    notes="Urn forming uses 2 Soft clay in source.",
                ),
                CraftingRecipe(
                    f"fire_{stable_item}_nr",
                    tier.item_nr,
                    "pottery",
                    "pottery_oven",
                    tier.crafting_level,
                    tier.firing_xp,
                    _req((tier.item_unf, 1)),
                    tier.item_nr,
                    source=URN_POTTERY_SOURCE,
                    source_enum=tier.source_enum,
                    source_item_id=non_runed_id,
                ),
                CraftingRecipe(
                    f"add_rune_{stable_item}",
                    tier.item_r,
                    "pottery",
                    "add_rune",
                    tier.crafting_level,
                    1.0,
                    _req((tier.item_nr, 1), (tier.rune, 1)),
                    tier.item_r,
                    source=URN_RUNE_SOURCE,
                    source_enum=tier.source_enum,
                    source_item_id=runed_id,
                    tradeable=False,
                    notes="Runed urn recipe is live and material-gated.",
                ),
            )
        )
    return tuple(recipes)


GEM_SOURCE = f"{CRAFTING_SOURCE_ROOT}/gems/GemData.kt"
POTTERY_SOURCE = URN_POTTERY_SOURCE
POTTERY_RUNE_SOURCE = URN_RUNE_SOURCE
SPINNING_SOURCE = f"{CRAFTING_SOURCE_ROOT}/spinning/SpinningData.kt"
SILVER_SOURCE = f"{CRAFTING_SOURCE_ROOT}/silver/SilverData.kt"
JEWELLERY_SOURCE = f"{CRAFTING_SOURCE_ROOT}/jewellery/JewelleryData.kt"
LEATHER_SOURCE = f"{CRAFTING_SOURCE_ROOT}/leather/LeatherData.kt"
TANNING_SOURCE = f"{CRAFTING_SOURCE_ROOT}/tanning/TanningData.kt"
GLASS_SOURCE = f"{CRAFTING_SOURCE_ROOT}/glassblowing/GlassData.kt"
MOULD_ITEMS_SOURCE = f"{CRAFTING_SOURCE_ROOT}/MouldItems.kt"
GLASSBLOWING_ACTION_SOURCE = f"{CRAFTING_SOURCE_ROOT}/glassblowing/GlassblowingAction.kt"
# Molten glass smelting lives with the furnace objects, not the crafting skill tree.
FURNACE_GLASS_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/objs/furnaces/furnaces.plugin.kts"
)
BATTLESTAFF_SOURCE = f"{CRAFTING_SOURCE_ROOT}/weaponry/BattlestaffData.kt"
WEAVING_SOURCE = f"{CRAFTING_SOURCE_ROOT}/weaving/WeavingData.kt"
POLISHED_BUTTON_SOURCE = f"{CRAFTING_SOURCE_ROOT}/other/polished_button.plugin.kts"

CRAFTING_REQUIRED_ITEM_SOURCE_IDS = {
    "Ring mould": 1592,
    "Necklace mould": 1597,
    "Bracelet mould": 11065,
    "Amulet mould": 1595,
    "Tiara mould": 5523,
    "Unholy mould": 1594,
    "Holy mould": 1599,
    "Sickle mould": 2976,
    "Demonic sigil mould": 6747,
    "Chain link mould": 13153,
    "Conductor mould": 4200,
    "Rod clay mould": 7649,
    "Bolt mould": 9434,
    "Glassblowing pipe": 1785,
}
CRAFTING_REQUIRED_ITEM_NONTRADEABLE = frozenset(
    {
        "Unholy mould",
        "Conductor mould",
        "Demonic sigil mould",
        "Rod clay mould",
        "Chain link mould",
    }
)


CRAFTING_RECIPES: Tuple[CraftingRecipe, ...] = (
    CraftingRecipe("chisel_limestone_brick", "Limestone brick", "stone", "chisel", 12, 6.0, _req(("Limestone", 1)), "Limestone brick", source=LIMESTONE_BRICK_SOURCE, source_item_id=3420),
    # Gem cutting. Semiprecious source crush chances are documented but not modeled;
    # one successful review is one completed Crafting action.
    CraftingRecipe("cut_opal", "Opal", "gems", "chisel", 1, 15.0, _req(("Uncut opal", 1)), "Opal", source=GEM_SOURCE, source_enum="OPAL", notes="Source has crush chance; AnkiScape treats the review action as a successful cut."),
    CraftingRecipe("cut_jade", "Jade", "gems", "chisel", 13, 20.0, _req(("Uncut jade", 1)), "Jade", source=GEM_SOURCE, source_enum="JADE", tradeable=False, notes="Source has crush chance; AnkiScape treats the review action as a successful cut."),
    CraftingRecipe("cut_red_topaz", "Red topaz", "gems", "chisel", 16, 25.0, _req(("Uncut red topaz", 1)), "Red topaz", source=GEM_SOURCE, source_enum="TOPAZ", tradeable=False, notes="Source has crush chance; AnkiScape treats the review action as a successful cut."),
    CraftingRecipe("cut_sapphire", "Sapphire", "gems", "chisel", 20, 50.0, _req(("Uncut sapphire", 1)), "Sapphire", source=GEM_SOURCE, source_enum="SAPPHIRE"),
    CraftingRecipe("cut_emerald", "Emerald", "gems", "chisel", 27, 67.0, _req(("Uncut emerald", 1)), "Emerald", source=GEM_SOURCE, source_enum="EMERALD"),
    CraftingRecipe("cut_ruby", "Ruby", "gems", "chisel", 34, 85.0, _req(("Uncut ruby", 1)), "Ruby", source=GEM_SOURCE, source_enum="RUBY"),
    CraftingRecipe("cut_diamond", "Diamond", "gems", "chisel", 43, 107.5, _req(("Uncut diamond", 1)), "Diamond", source=GEM_SOURCE, source_enum="DIAMOND"),
    CraftingRecipe("cut_dragonstone", "Dragonstone", "gems", "chisel", 55, 137.5, _req(("Uncut dragonstone", 1)), "Dragonstone", source=GEM_SOURCE, source_enum="DRAGONSTONE", notes="Live target; input-starved until dragonstone acquisition exists."),
    CraftingRecipe("cut_onyx", "Onyx", "gems", "chisel", 67, 167.5, _req(("Uncut onyx", 1)), "Onyx", source=GEM_SOURCE, source_enum="ONYX", notes="Live target; input-starved until onyx acquisition exists."),

    # Pottery non-urns.
    CraftingRecipe("form_pot_unfired", "Pot (unfired)", "pottery", "potters_wheel", 1, 6.3, _req(("Soft clay", 1)), "Pot (unfired)", source=POTTERY_SOURCE, source_enum="POT"),
    CraftingRecipe("fire_empty_pot", "Empty pot", "pottery", "pottery_oven", 1, 6.3, _req(("Pot (unfired)", 1)), "Empty pot", source=POTTERY_SOURCE, source_enum="POT"),
    CraftingRecipe("form_clay_ring_unfired", "Clay ring (unfired)", "pottery", "potters_wheel", 4, 11.3, _req(("Soft clay", 1)), "Clay ring (unfired)", source=POTTERY_SOURCE, source_enum="CLAY_RING", required_items=_req(("Ring mould", 1))),
    CraftingRecipe("fire_clay_ring", "Clay ring", "pottery", "pottery_oven", 4, 11.0, _req(("Clay ring (unfired)", 1)), "Clay ring", source=POTTERY_SOURCE, source_enum="CLAY_RING"),
    CraftingRecipe("form_pie_dish_unfired", "Pie dish (unfired)", "pottery", "potters_wheel", 7, 15.0, _req(("Soft clay", 1)), "Pie dish (unfired)", source=POTTERY_SOURCE, source_enum="PIE_DISH"),
    CraftingRecipe("fire_pie_dish", "Pie dish", "pottery", "pottery_oven", 7, 10.0, _req(("Pie dish (unfired)", 1)), "Pie dish", source=POTTERY_SOURCE, source_enum="PIE_DISH"),
    CraftingRecipe("form_bowl_unfired", "Bowl (unfired)", "pottery", "potters_wheel", 8, 18.0, _req(("Soft clay", 1)), "Bowl (unfired)", source=POTTERY_SOURCE, source_enum="BOWL"),
    CraftingRecipe("fire_bowl", "Bowl", "pottery", "pottery_oven", 8, 15.0, _req(("Bowl (unfired)", 1)), "Bowl", source=POTTERY_SOURCE, source_enum="BOWL"),
    CraftingRecipe("form_plant_pot_unfired", "Plant pot (unfired)", "pottery", "potters_wheel", 19, 20.0, _req(("Soft clay", 1)), "Plant pot (unfired)", source=POTTERY_SOURCE, source_enum="PLANT_POT"),
    CraftingRecipe("fire_plant_pot", "Plant pot", "pottery", "pottery_oven", 19, 17.5, _req(("Plant pot (unfired)", 1)), "Plant pot", source=POTTERY_SOURCE, source_enum="PLANT_POT"),
    CraftingRecipe("form_pot_lid_unfired", "Pot lid (unfired)", "pottery", "potters_wheel", 25, 20.0, _req(("Soft clay", 1)), "Pot lid (unfired)", source=POTTERY_SOURCE, source_enum="POT_LID"),
    CraftingRecipe("fire_pot_lid", "Pot lid", "pottery", "pottery_oven", 25, 20.0, _req(("Pot lid (unfired)", 1)), "Pot lid", source=POTTERY_SOURCE, source_enum="POT_LID"),

    # Urns. The five physical states, source IDs, and Crafting metadata come
    # from urn_data.py so runtime lifecycle and Crafting exports cannot drift.
    *_urn_crafting_recipes(),

    # Spinning. No XP-bearing batching.
    CraftingRecipe("spin_wool_to_ball_of_wool", "Ball of wool", "spinning", "spinning_wheel", 1, 2.5, _req(("Wool", 1)), "Ball of wool", source=SPINNING_SOURCE, source_enum="WOOL"),
    CraftingRecipe("spin_flax_to_bow_string", "Bow string", "spinning", "spinning_wheel", 10, 15.0, _req(("Flax", 1)), "Bow string", source=SPINNING_SOURCE, source_enum="FLAX"),
    CraftingRecipe("spin_sinew_to_crossbow_string", "Crossbow string", "spinning", "spinning_wheel", 10, 15.0, _req(("Sinew", 1)), "Crossbow string", source=SPINNING_SOURCE, source_enum="CBOW_STRING", notes="Live target; input-starved until sinew acquisition exists."),
    CraftingRecipe("spin_oak_roots_to_crossbow_string", "Crossbow string", "spinning", "spinning_wheel", 10, 15.0, _req(("Oak roots", 1)), "Crossbow string", source=SPINNING_SOURCE, source_enum="CBOW_STRING1", source_item_id=9438, notes="Source accepts each root type as an alternative input; input-starved until root acquisition exists."),
    CraftingRecipe("spin_willow_roots_to_crossbow_string", "Crossbow string", "spinning", "spinning_wheel", 10, 15.0, _req(("Willow roots", 1)), "Crossbow string", source=SPINNING_SOURCE, source_enum="CBOW_STRING1", source_item_id=9438, notes="Source accepts each root type as an alternative input; input-starved until root acquisition exists."),
    CraftingRecipe("spin_maple_roots_to_crossbow_string", "Crossbow string", "spinning", "spinning_wheel", 10, 15.0, _req(("Maple roots", 1)), "Crossbow string", source=SPINNING_SOURCE, source_enum="CBOW_STRING1", source_item_id=9438, notes="Source accepts each root type as an alternative input; input-starved until root acquisition exists."),
    CraftingRecipe("spin_yew_roots_to_crossbow_string", "Crossbow string", "spinning", "spinning_wheel", 10, 15.0, _req(("Yew roots", 1)), "Crossbow string", source=SPINNING_SOURCE, source_enum="CBOW_STRING1", source_item_id=9438, notes="Source accepts each root type as an alternative input; input-starved until root acquisition exists."),
    CraftingRecipe("spin_magic_roots_to_crossbow_string", "Crossbow string", "spinning", "spinning_wheel", 10, 15.0, _req(("Magic roots", 1)), "Crossbow string", source=SPINNING_SOURCE, source_enum="CBOW_STRING1", source_item_id=9438, notes="Source accepts each root type as an alternative input; input-starved until root acquisition exists."),
    CraftingRecipe("spin_spirit_roots_to_crossbow_string", "Crossbow string", "spinning", "spinning_wheel", 10, 15.0, _req(("Spirit roots", 1)), "Crossbow string", source=SPINNING_SOURCE, source_enum="CBOW_STRING1", source_item_id=9438, notes="Source accepts each root type as an alternative input; input-starved until root acquisition exists."),
    CraftingRecipe("spin_magic_roots_to_magic_string", "Magic string", "spinning", "spinning_wheel", 19, 30.0, _req(("Magic roots", 1)), "Magic string", source=SPINNING_SOURCE, source_enum="MAGIC_STRING", notes="Live target; input-starved until root acquisition exists."),
    CraftingRecipe("spin_hair_to_rope", "Rope", "spinning", "spinning_wheel", 30, 25.0, _req(("Hair", 1)), "Rope", source=SPINNING_SOURCE, source_enum="ROPE", notes="Live target; input-starved until yak hair acquisition exists."),

    # Silver.
    CraftingRecipe("silver_unstrung_symbol", "Unstrung symbol", "silver", "furnace", 16, 50.0, _req(("Silver bar", 1)), "Unstrung symbol", source=SILVER_SOURCE, source_enum="HOLY_SYMBOL", required_items=_req(("Holy mould", 1))),
    CraftingRecipe("silver_unstrung_emblem", "Unstrung emblem", "silver", "furnace", 17, 50.0, _req(("Silver bar", 1)), "Unstrung emblem", source=SILVER_SOURCE, source_enum="UNHOLY_SYMBOL", required_items=_req(("Unholy mould", 1))),
    CraftingRecipe("silver_silver_sickle", "Silver sickle", "silver", "furnace", 18, 50.0, _req(("Silver bar", 1)), "Silver sickle", source=SILVER_SOURCE, source_enum="SILVER_SICKLE", required_items=_req(("Sickle mould", 1))),
    CraftingRecipe("silver_conductor", "Conductor", "silver", "furnace", 20, 50.0, _req(("Silver bar", 1)), "Conductor", source=SILVER_SOURCE, source_enum="CONDUCTOR_ROD", tradeable=False, notes="Quest item; live but use-starved.", required_items=_req(("Conductor mould", 1))),
    CraftingRecipe("silver_silver_bolts_unf", "Silver bolts (unf)", "silver", "furnace", 21, 50.0, _req(("Silver bar", 1)), "Silver bolts (unf)", 10, source=SILVER_SOURCE, source_enum="SILVER_BOLTS", required_items=_req(("Bolt mould", 1))),
    CraftingRecipe("silver_tiara", "Tiara", "silver", "furnace", 23, 52.5, _req(("Silver bar", 1)), "Tiara", source=SILVER_SOURCE, source_enum="TIARA", required_items=_req(("Tiara mould", 1))),
    CraftingRecipe("silver_silvthrill_rod", "Silvthrill rod", "silver", "furnace", 25, 55.0, _req(("Silver bar", 1), ("Mithril bar", 1), ("Sapphire", 1)), "Silvthrill rod", source=SILVER_SOURCE, source_enum="SILVTHRILL_ROD", tradeable=False, source_item_id=7637, required_items=_req(("Rod clay mould", 1))),
    CraftingRecipe("silver_demonic_sigil", "Demonic sigil", "silver", "furnace", 30, 50.0, _req(("Silver bar", 1)), "Demonic sigil", source=SILVER_SOURCE, source_enum="DEMONIC_SIGIL", tradeable=False, notes="Quest item; live but use-starved.", required_items=_req(("Demonic sigil mould", 1))),
    CraftingRecipe("silver_silvthrill_chain", "Silvthril chain", "silver", "furnace", 47, 100.0, _req(("Silver bar", 1), ("Mithril bar", 1)), "Silvthril chain", source=SILVER_SOURCE, source_enum="SILVTHRILL_CHAIN", tradeable=False, source_item_id=13154, required_items=_req(("Chain link mould", 1))),

    # Jewellery.
    CraftingRecipe("jewellery_gold_ring", "Gold ring", "jewellery", "furnace", 5, 15.0, _req(("Gold bar", 1)), "Gold ring", source=JEWELLERY_SOURCE, source_enum="GOLD", required_items=_req(("Ring mould", 1))),
    CraftingRecipe("jewellery_gold_necklace", "Gold necklace", "jewellery", "furnace", 6, 20.0, _req(("Gold bar", 1)), "Gold necklace", source=JEWELLERY_SOURCE, source_enum="GOLD", required_items=_req(("Necklace mould", 1))),
    CraftingRecipe("jewellery_gold_bracelet", "Gold bracelet", "jewellery", "furnace", 7, 25.0, _req(("Gold bar", 1)), "Gold bracelet", source=JEWELLERY_SOURCE, source_enum="GOLD", required_items=_req(("Bracelet mould", 1))),
    CraftingRecipe("jewellery_gold_amulet", "Gold amulet (u)", "jewellery", "furnace", 8, 30.0, _req(("Gold bar", 1)), "Gold amulet (u)", source=JEWELLERY_SOURCE, source_enum="GOLD", source_item_id=1673, required_items=_req(("Amulet mould", 1))),
    CraftingRecipe("jewellery_sapphire_ring", "Sapphire ring", "jewellery", "furnace", 20, 40.0, _req(("Gold bar", 1), ("Sapphire", 1)), "Sapphire ring", source=JEWELLERY_SOURCE, source_enum="SAPPHIRE", required_items=_req(("Ring mould", 1))),
    CraftingRecipe("jewellery_sapphire_necklace", "Sapphire necklace", "jewellery", "furnace", 22, 55.0, _req(("Gold bar", 1), ("Sapphire", 1)), "Sapphire necklace", source=JEWELLERY_SOURCE, source_enum="SAPPHIRE", required_items=_req(("Necklace mould", 1))),
    CraftingRecipe("jewellery_sapphire_bracelet", "Sapphire bracelet", "jewellery", "furnace", 23, 60.0, _req(("Gold bar", 1), ("Sapphire", 1)), "Sapphire bracelet", source=JEWELLERY_SOURCE, source_enum="SAPPHIRE", required_items=_req(("Bracelet mould", 1))),
    CraftingRecipe("jewellery_sapphire_amulet", "Sapphire amulet (u)", "jewellery", "furnace", 24, 65.0, _req(("Gold bar", 1), ("Sapphire", 1)), "Sapphire amulet (u)", source=JEWELLERY_SOURCE, source_enum="SAPPHIRE", source_item_id=1675, required_items=_req(("Amulet mould", 1))),
    CraftingRecipe("jewellery_emerald_ring", "Emerald ring", "jewellery", "furnace", 27, 55.0, _req(("Gold bar", 1), ("Emerald", 1)), "Emerald ring", source=JEWELLERY_SOURCE, source_enum="EMERALD", required_items=_req(("Ring mould", 1))),
    CraftingRecipe("jewellery_emerald_necklace", "Emerald necklace", "jewellery", "furnace", 29, 60.0, _req(("Gold bar", 1), ("Emerald", 1)), "Emerald necklace", source=JEWELLERY_SOURCE, source_enum="EMERALD", required_items=_req(("Necklace mould", 1))),
    CraftingRecipe("jewellery_emerald_bracelet", "Emerald bracelet", "jewellery", "furnace", 30, 65.0, _req(("Gold bar", 1), ("Emerald", 1)), "Emerald bracelet", source=JEWELLERY_SOURCE, source_enum="EMERALD", required_items=_req(("Bracelet mould", 1))),
    CraftingRecipe("jewellery_emerald_amulet", "Emerald amulet (u)", "jewellery", "furnace", 31, 70.0, _req(("Gold bar", 1), ("Emerald", 1)), "Emerald amulet (u)", source=JEWELLERY_SOURCE, source_enum="EMERALD", source_item_id=1677, required_items=_req(("Amulet mould", 1))),
    CraftingRecipe("jewellery_ruby_ring", "Ruby ring", "jewellery", "furnace", 34, 70.0, _req(("Gold bar", 1), ("Ruby", 1)), "Ruby ring", source=JEWELLERY_SOURCE, source_enum="RUBY", required_items=_req(("Ring mould", 1))),
    CraftingRecipe("jewellery_ruby_necklace", "Ruby necklace", "jewellery", "furnace", 40, 75.0, _req(("Gold bar", 1), ("Ruby", 1)), "Ruby necklace", source=JEWELLERY_SOURCE, source_enum="RUBY", required_items=_req(("Necklace mould", 1))),
    CraftingRecipe("jewellery_ruby_bracelet", "Ruby bracelet", "jewellery", "furnace", 42, 80.0, _req(("Gold bar", 1), ("Ruby", 1)), "Ruby bracelet", source=JEWELLERY_SOURCE, source_enum="RUBY", required_items=_req(("Bracelet mould", 1))),
    CraftingRecipe("jewellery_ruby_amulet", "Ruby amulet (u)", "jewellery", "furnace", 50, 85.0, _req(("Gold bar", 1), ("Ruby", 1)), "Ruby amulet (u)", source=JEWELLERY_SOURCE, source_enum="RUBY", source_item_id=1679, required_items=_req(("Amulet mould", 1))),
    CraftingRecipe("jewellery_diamond_ring", "Diamond ring", "jewellery", "furnace", 43, 85.0, _req(("Gold bar", 1), ("Diamond", 1)), "Diamond ring", source=JEWELLERY_SOURCE, source_enum="DIAMOND", required_items=_req(("Ring mould", 1))),
    CraftingRecipe("jewellery_diamond_necklace", "Diamond necklace", "jewellery", "furnace", 56, 90.0, _req(("Gold bar", 1), ("Diamond", 1)), "Diamond necklace", source=JEWELLERY_SOURCE, source_enum="DIAMOND", required_items=_req(("Necklace mould", 1))),
    CraftingRecipe("jewellery_diamond_bracelet", "Diamond bracelet", "jewellery", "furnace", 58, 95.0, _req(("Gold bar", 1), ("Diamond", 1)), "Diamond bracelet", source=JEWELLERY_SOURCE, source_enum="DIAMOND", required_items=_req(("Bracelet mould", 1))),
    CraftingRecipe("jewellery_diamond_amulet", "Diamond amulet (u)", "jewellery", "furnace", 70, 100.0, _req(("Gold bar", 1), ("Diamond", 1)), "Diamond amulet (u)", source=JEWELLERY_SOURCE, source_enum="DIAMOND", source_item_id=1681, required_items=_req(("Amulet mould", 1))),
    CraftingRecipe("jewellery_dragonstone_ring", "Dragonstone ring", "jewellery", "furnace", 55, 100.0, _req(("Gold bar", 1), ("Dragonstone", 1)), "Dragonstone ring", source=JEWELLERY_SOURCE, source_enum="DRAGONSTONE", notes="Live target; input-starved until dragonstone acquisition exists.", required_items=_req(("Ring mould", 1))),
    CraftingRecipe("jewellery_dragon_necklace", "Dragon necklace", "jewellery", "furnace", 72, 105.0, _req(("Gold bar", 1), ("Dragonstone", 1)), "Dragon necklace", source=JEWELLERY_SOURCE, source_enum="DRAGONSTONE", notes="Live target; input-starved until dragonstone acquisition exists.", required_items=_req(("Necklace mould", 1))),
    CraftingRecipe("jewellery_dragon_bracelet", "Dragon bracelet", "jewellery", "furnace", 74, 110.0, _req(("Gold bar", 1), ("Dragonstone", 1)), "Dragon bracelet", source=JEWELLERY_SOURCE, source_enum="DRAGONSTONE", notes="Live target; input-starved until dragonstone acquisition exists.", required_items=_req(("Bracelet mould", 1))),
    CraftingRecipe("jewellery_dragonstone_ammy", "Dragonstone ammy (u)", "jewellery", "furnace", 80, 150.0, _req(("Gold bar", 1), ("Dragonstone", 1)), "Dragonstone ammy (u)", source=JEWELLERY_SOURCE, source_enum="DRAGONSTONE", source_item_id=1683, notes="Live target; input-starved until dragonstone acquisition exists.", required_items=_req(("Amulet mould", 1))),
    CraftingRecipe("jewellery_onyx_ring", "Onyx ring", "jewellery", "furnace", 67, 115.0, _req(("Gold bar", 1), ("Onyx", 1)), "Onyx ring", source=JEWELLERY_SOURCE, source_enum="ONYX", notes="Live target; input-starved until onyx acquisition exists.", required_items=_req(("Ring mould", 1))),
    CraftingRecipe("jewellery_onyx_necklace", "Onyx necklace", "jewellery", "furnace", 82, 120.0, _req(("Gold bar", 1), ("Onyx", 1)), "Onyx necklace", source=JEWELLERY_SOURCE, source_enum="ONYX", notes="Live target; input-starved until onyx acquisition exists.", required_items=_req(("Necklace mould", 1))),
    CraftingRecipe("jewellery_onyx_bracelet", "Onyx bracelet", "jewellery", "furnace", 84, 125.0, _req(("Gold bar", 1), ("Onyx", 1)), "Onyx bracelet", source=JEWELLERY_SOURCE, source_enum="ONYX", notes="Live target; input-starved until onyx acquisition exists.", required_items=_req(("Bracelet mould", 1))),
    CraftingRecipe("jewellery_onyx_amulet", "Onyx amulet (u)", "jewellery", "furnace", 90, 165.0, _req(("Gold bar", 1), ("Onyx", 1)), "Onyx amulet (u)", source=JEWELLERY_SOURCE, source_enum="ONYX", source_item_id=6579, notes="Live target; input-starved until onyx acquisition exists.", required_items=_req(("Amulet mould", 1))),
    CraftingRecipe("jewellery_ring_of_slaying_8", "Ring of slaying (8)", "jewellery", "furnace", 75, 15.0, _req(("Gold bar", 1), ("Enchanted gem", 1)), "Ring of slaying (8)", source=JEWELLERY_SOURCE, source_enum="SLAYER_RING", tradeable=False, source_item_id=13281, notes="Source additionally requires the Slayer CRAFT_ROS unlock; AnkiScape has no Slayer system to enforce it.", required_items=_req(("Ring mould", 1))),

    # Leather.
    CraftingRecipe("leather_leather_gloves", "Leather gloves", "leather", "needle", 1, 13.8, _req(("Leather", 1)), "Leather gloves", source=LEATHER_SOURCE, source_enum="LEATHER", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_leather_boots", "Leather boots", "leather", "needle", 7, 16.2, _req(("Leather", 1)), "Leather boots", source=LEATHER_SOURCE, source_enum="LEATHER", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_leather_cowl", "Leather cowl", "leather", "needle", 9, 18.5, _req(("Leather", 1)), "Leather cowl", source=LEATHER_SOURCE, source_enum="LEATHER", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_leather_vambraces", "Leather vambraces", "leather", "needle", 11, 22.0, _req(("Leather", 1)), "Leather vambraces", source=LEATHER_SOURCE, source_enum="LEATHER", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_leather_body", "Leather body", "leather", "needle", 14, 25.0, _req(("Leather", 1)), "Leather body", source=LEATHER_SOURCE, source_enum="LEATHER", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_leather_chaps", "Leather chaps", "leather", "needle", 18, 27.0, _req(("Leather", 1)), "Leather chaps", source=LEATHER_SOURCE, source_enum="LEATHER", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_coif", "Coif", "leather", "needle", 38, 37.0, _req(("Leather", 1)), "Coif", source=LEATHER_SOURCE, source_enum="LEATHER", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_hardleather_body", "Hardleather body", "leather", "needle", 28, 35.0, _req(("Hard leather", 1)), "Hardleather body", source=LEATHER_SOURCE, source_enum="HARD_LEATHER", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_snakeskin_boots", "Snakeskin boots", "leather", "needle", 45, 30.0, _req(("Snakeskin", 6)), "Snakeskin boots", source=LEATHER_SOURCE, source_enum="SNAKESKIN", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_snakeskin_vambraces", "Snakeskin vambraces", "leather", "needle", 47, 35.0, _req(("Snakeskin", 8)), "Snakeskin vambraces", source=LEATHER_SOURCE, source_enum="SNAKESKIN", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_snakeskin_bandana", "Snakeskin bandana", "leather", "needle", 48, 45.0, _req(("Snakeskin", 5)), "Snakeskin bandana", source=LEATHER_SOURCE, source_enum="SNAKESKIN", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_snakeskin_chaps", "Snakeskin chaps", "leather", "needle", 51, 50.0, _req(("Snakeskin", 12)), "Snakeskin chaps", source=LEATHER_SOURCE, source_enum="SNAKESKIN", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_snakeskin_body", "Snakeskin body", "leather", "needle", 53, 55.0, _req(("Snakeskin", 15)), "Snakeskin body", source=LEATHER_SOURCE, source_enum="SNAKESKIN", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_yakhide_armour_10824", "Yak-hide armour", "leather", "needle", 43, 32.0, _req(("Cured yak-hide", 1)), "Yak-hide armour", source=LEATHER_SOURCE, source_enum="YAK_HIDE", tradeable=False, source_item_id=10824, required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_yakhide_armour", "Yak-hide armour", "leather", "needle", 46, 32.0, _req(("Cured yak-hide", 2)), "Yak-hide armour", source=LEATHER_SOURCE, source_enum="YAK_HIDE", tradeable=False, source_item_id=10822, required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_green_dhide_vambraces", "Green d'hide vambraces", "leather", "needle", 57, 62.0, _req(("Green dragon leather", 1)), "Green d'hide vambraces", source=LEATHER_SOURCE, source_enum="GREEN_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_green_dhide_chaps", "Green d'hide chaps", "leather", "needle", 60, 124.0, _req(("Green dragon leather", 2)), "Green d'hide chaps", source=LEATHER_SOURCE, source_enum="GREEN_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_green_dhide_body", "Green d'hide body", "leather", "needle", 63, 186.0, _req(("Green dragon leather", 3)), "Green d'hide body", source=LEATHER_SOURCE, source_enum="GREEN_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_blue_dhide_vambraces", "Blue d'hide vambraces", "leather", "needle", 66, 70.0, _req(("Blue dragon leather", 1)), "Blue d'hide vambraces", source=LEATHER_SOURCE, source_enum="BLUE_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_blue_dhide_chaps", "Blue d'hide chaps", "leather", "needle", 68, 140.0, _req(("Blue dragon leather", 2)), "Blue d'hide chaps", source=LEATHER_SOURCE, source_enum="BLUE_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_blue_dhide_body", "Blue d'hide body", "leather", "needle", 71, 210.0, _req(("Blue dragon leather", 3)), "Blue d'hide body", source=LEATHER_SOURCE, source_enum="BLUE_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_red_dhide_vambraces", "Red d'hide vambraces", "leather", "needle", 73, 78.0, _req(("Red dragon leather", 1)), "Red d'hide vambraces", source=LEATHER_SOURCE, source_enum="RED_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_red_dhide_chaps", "Red d'hide chaps", "leather", "needle", 75, 156.0, _req(("Red dragon leather", 2)), "Red d'hide chaps", source=LEATHER_SOURCE, source_enum="RED_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_red_dhide_body", "Red d'hide body", "leather", "needle", 77, 234.0, _req(("Red dragon leather", 3)), "Red d'hide body", source=LEATHER_SOURCE, source_enum="RED_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_black_dhide_vambraces", "Black d'hide vambraces", "leather", "needle", 79, 86.0, _req(("Black dragon leather", 1)), "Black d'hide vambraces", source=LEATHER_SOURCE, source_enum="BLACK_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_black_dhide_chaps", "Black d'hide chaps", "leather", "needle", 82, 172.0, _req(("Black dragon leather", 2)), "Black d'hide chaps", source=LEATHER_SOURCE, source_enum="BLACK_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),
    CraftingRecipe("leather_black_dhide_body", "Black d'hide body", "leather", "needle", 84, 258.0, _req(("Black dragon leather", 3)), "Black d'hide body", source=LEATHER_SOURCE, source_enum="BLACK_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists.", required_items=_req(("Thread", 1)), consume_thread_on_roll=True),

    # Glass, battlestaves, weaving, and selected source Crafting combinations.
    CraftingRecipe("glass_molten_glass", "Molten glass", "glass", "furnace", 1, 20.0, _req(("Soda ash", 1), ("Bucket of sand", 1)), "Molten glass", byproducts=(("Bucket", 1),), source=FURNACE_GLASS_SOURCE, source_enum="", notes="Furnace smelt (handleMoltenGlass); returns the emptied bucket. Inputs are live NPC shop stock."),
    CraftingRecipe("glass_beer_glass", "Beer glass", "glass", "glassblowing", 1, 17.5, _req(("Molten glass", 1)), "Beer glass", source=GLASS_SOURCE, source_enum="BEER_GLASS", required_items=_req(("Glassblowing pipe", 1))),
    CraftingRecipe("glass_empty_candle_lantern", "Candle lantern (empty)", "glass", "glassblowing", 4, 19.0, _req(("Molten glass", 1)), "Candle lantern (empty)", source=GLASS_SOURCE, source_enum="EMPTY_CANDLE_LANTERN", source_item_id=4527, required_items=_req(("Glassblowing pipe", 1))),
    CraftingRecipe("glass_empty_oil_lamp", "Oil lamp (empty)", "glass", "glassblowing", 12, 25.0, _req(("Molten glass", 1)), "Oil lamp (empty)", source=GLASS_SOURCE, source_enum="EMPTY_OIL_LAMP", source_item_id=4525, required_items=_req(("Glassblowing pipe", 1))),
    CraftingRecipe("glass_vial", "Vial", "glass", "glassblowing", 33, 35.0, _req(("Molten glass", 1)), "Vial", source=GLASS_SOURCE, source_enum="EMPTY_VIAL", required_items=_req(("Glassblowing pipe", 1))),
    CraftingRecipe("glass_fishbowl", "Fishbowl", "glass", "glassblowing", 42, 42.5, _req(("Molten glass", 1)), "Fishbowl", source=GLASS_SOURCE, source_enum="FISHBOWL", source_item_id=6667, required_items=_req(("Glassblowing pipe", 1))),
    CraftingRecipe("glass_unpowered_orb", "Unpowered orb", "glass", "glassblowing", 46, 52.5, _req(("Molten glass", 1)), "Unpowered orb", source=GLASS_SOURCE, source_enum="UNPOWERED_ORB", required_items=_req(("Glassblowing pipe", 1))),
    CraftingRecipe("glass_lantern_lens", "Lantern lens", "glass", "glassblowing", 49, 55.0, _req(("Molten glass", 1)), "Lantern lens", source=GLASS_SOURCE, source_enum="LANTERN_LENS", source_item_id=4542, required_items=_req(("Glassblowing pipe", 1))),
    CraftingRecipe("glass_empty_light_orb", "Empty light orb", "glass", "glassblowing", 87, 70.0, _req(("Molten glass", 1)), "Empty light orb", source=GLASS_SOURCE, source_enum="EMPTY_LIGHT_ORB", tradeable=False, source_item_id=10980, required_items=_req(("Glassblowing pipe", 1))),
    CraftingRecipe("battlestaff_water_battlestaff", "Water battlestaff", "battlestaff", "attach_orb", 54, 100.0, _req(("Battlestaff", 1), ("Water orb", 1)), "Water battlestaff", source=BATTLESTAFF_SOURCE, source_enum="WATER_BATTLESTAFF", notes="The charged orb is supplied by the live Magic Charge Orb action."),
    CraftingRecipe("battlestaff_earth_battlestaff", "Earth battlestaff", "battlestaff", "attach_orb", 58, 112.5, _req(("Battlestaff", 1), ("Earth orb", 1)), "Earth battlestaff", source=BATTLESTAFF_SOURCE, source_enum="EARTH_BATTLESTAFF", notes="The charged orb is supplied by the live Magic Charge Orb action."),
    CraftingRecipe("battlestaff_fire_battlestaff", "Fire battlestaff", "battlestaff", "attach_orb", 62, 125.0, _req(("Battlestaff", 1), ("Fire orb", 1)), "Fire battlestaff", source=BATTLESTAFF_SOURCE, source_enum="FIRE_BATTLESTAFF", notes="The charged orb is supplied by the live Magic Charge Orb action."),
    CraftingRecipe("battlestaff_air_battlestaff", "Air battlestaff", "battlestaff", "attach_orb", 66, 137.5, _req(("Battlestaff", 1), ("Air orb", 1)), "Air battlestaff", source=BATTLESTAFF_SOURCE, source_enum="AIR_BATTLESTAFF", notes="The charged orb is supplied by the live Magic Charge Orb action."),
    CraftingRecipe("weave_strip_of_cloth", "Strip of cloth", "weaving", "loom", 10, 12.0, _req(("Ball of wool", 4)), "Strip of cloth", source=WEAVING_SOURCE, source_enum="STRIP_OF_CLOTH"),
    CraftingRecipe("weave_empty_sack", "Empty sack", "weaving", "loom", 21, 38.0, _req(("Jute fibre", 4)), "Empty sack", source=WEAVING_SOURCE, source_enum="EMPTY_SACK", notes="Live target; input-starved until Farming crop loop exists."),
    CraftingRecipe("weave_empty_basket", "Basket", "weaving", "loom", 36, 56.0, _req(("Willow branch", 6)), "Basket", source=WEAVING_SOURCE, source_enum="EMPTY_BASKET"),
    CraftingRecipe("weave_unfinished_net", "Unfinished net", "weaving", "loom", 52, 0.0, _req(("Flax", 5)), "Unfinished net", source=WEAVING_SOURCE, source_enum="UNFINISHED_NET"),
    CraftingRecipe("weave_milestone_cape_10", "Milestone cape (10)", "weaving", "loom", 10, 10.0, _req(("Ball of wool", 1)), "Milestone cape (10)", source=WEAVING_SOURCE, source_enum="MILESTONE_CAPES", source_item_id=20735, notes="Source requires every skill to be at least level 10; AnkiScape's Crafting model cannot enforce the all-skills gate."),
    CraftingRecipe("weave_milestone_cape_20", "Milestone cape (20)", "weaving", "loom", 20, 20.0, _req(("Ball of wool", 2)), "Milestone cape (20)", source=WEAVING_SOURCE, source_enum="MILESTONE_CAPES", source_item_id=20736, notes="Source requires every skill to be at least level 20; AnkiScape's Crafting model cannot enforce the all-skills gate."),
    CraftingRecipe("weave_milestone_cape_30", "Milestone cape (30)", "weaving", "loom", 30, 30.0, _req(("Ball of wool", 3)), "Milestone cape (30)", source=WEAVING_SOURCE, source_enum="MILESTONE_CAPES", source_item_id=20737, notes="Source requires every skill to be at least level 30; AnkiScape's Crafting model cannot enforce the all-skills gate."),
    CraftingRecipe("weave_milestone_cape_40", "Milestone cape (40)", "weaving", "loom", 40, 40.0, _req(("Ball of wool", 4)), "Milestone cape (40)", source=WEAVING_SOURCE, source_enum="MILESTONE_CAPES", source_item_id=20738, notes="Source requires every skill to be at least level 40; AnkiScape's Crafting model cannot enforce the all-skills gate."),
    CraftingRecipe("weave_milestone_cape_50", "Milestone cape (50)", "weaving", "loom", 50, 50.0, _req(("Ball of wool", 5)), "Milestone cape (50)", source=WEAVING_SOURCE, source_enum="MILESTONE_CAPES", source_item_id=20739, notes="Source requires every skill to be at least level 50; AnkiScape's Crafting model cannot enforce the all-skills gate."),
    CraftingRecipe("weave_milestone_cape_60", "Milestone cape (60)", "weaving", "loom", 60, 60.0, _req(("Ball of wool", 6)), "Milestone cape (60)", source=WEAVING_SOURCE, source_enum="MILESTONE_CAPES", source_item_id=20740, notes="Source requires every skill to be at least level 60; AnkiScape's Crafting model cannot enforce the all-skills gate."),
    CraftingRecipe("weave_milestone_cape_70", "Milestone cape (70)", "weaving", "loom", 70, 70.0, _req(("Ball of wool", 7)), "Milestone cape (70)", source=WEAVING_SOURCE, source_enum="MILESTONE_CAPES", source_item_id=20741, notes="Source requires every skill to be at least level 70; AnkiScape's Crafting model cannot enforce the all-skills gate."),
    CraftingRecipe("weave_milestone_cape_80", "Milestone cape (80)", "weaving", "loom", 80, 80.0, _req(("Ball of wool", 8)), "Milestone cape (80)", source=WEAVING_SOURCE, source_enum="MILESTONE_CAPES", source_item_id=20742, notes="Source requires every skill to be at least level 80; AnkiScape's Crafting model cannot enforce the all-skills gate."),
    CraftingRecipe("weave_milestone_cape_90", "Milestone cape (90)", "weaving", "loom", 90, 90.0, _req(("Ball of wool", 9)), "Milestone cape (90)", source=WEAVING_SOURCE, source_enum="MILESTONE_CAPES", source_item_id=20743, notes="Source requires every skill to be at least level 90; AnkiScape's Crafting model cannot enforce the all-skills gate."),
    # Item combinations and polishing.
    CraftingRecipe("combine_strange_skull", "Strange skull", "combination", "combine", 1, 0.0, _req(("Left skull half", 1), ("Right skull half", 1)), "Strange skull", source=COMBINATION_SOURCE_PATH, source_enum="STRANGE_SKULL", tradeable=False, source_item_id=9009),
    CraftingRecipe("combine_runed_sceptre", "Runed sceptre", "combination", "combine", 1, 0.0, _req(("Bottom of sceptre", 1), ("Top of sceptre", 1)), "Runed sceptre", source=COMBINATION_SOURCE_PATH, source_enum="RUNED_SCEPTRE", tradeable=False, source_item_id=9012),
    CraftingRecipe("combine_skull_sceptre", "Skull sceptre", "combination", "combine", 1, 0.0, _req(("Strange skull", 1), ("Runed sceptre", 1)), "Skull sceptre", source=COMBINATION_SOURCE_PATH, source_enum="SKULL_SCEPTRE", tradeable=False, source_item_id=9013),
    CraftingRecipe("combine_bullseye_lantern", "Fit lantern lens", "combination", "combine", 49, 0.0, _req(("Bullseye lantern (unf)", 1), ("Lantern lens", 1)), "Bullseye lantern (empty)", source=COMBINATION_SOURCE_PATH, source_enum="BULLYEYE_LANTERN", tradeable=False, source_item_id=4546),
    CraftingRecipe("combine_bullseye_emerald_lantern", "Fit emerald lens", "combination", "combine", 49, 0.0, _req(("Bullseye lantern (empty)", 1), ("Emerald lens", 1)), "Emerald lantern (unlit)", source=COMBINATION_SOURCE_PATH, source_enum="BULLYEYE_EMERALD_LANTERN", tradeable=False, source_item_id=9064),
    CraftingRecipe("combine_bullseye_sapphire_lantern", "Fit sapphire lens", "combination", "combine", 49, 0.0, _req(("Bullseye lantern (empty)", 1), ("Sapphire", 1)), "Sapphire lantern (empty)", byproducts=(("Lantern lens", 1),), source=SAPPHIRE_LANTERN_SOURCE, source_enum="SAPPHIRE_LANTERN", tradeable=False, source_item_id=4700),
    CraftingRecipe("combine_empty_oil_lantern", "Assemble empty oil lantern", "combination", "combine", 26, 50.0, _req(("Oil lamp (empty)", 1), ("Oil lantern frame", 1)), "Oil lantern (empty)", source=OIL_LANTERN_SOURCE, source_enum="OIL_LANTERN_EMPTY", source_item_id=4535),
    CraftingRecipe("combine_oil_lantern", "Assemble oil lantern", "combination", "combine", 26, 50.0, _req(("Oil lamp (unlit)", 1), ("Oil lantern frame", 1)), "Oil lantern (unlit)", source=f"{COMBINATION_SOURCE_PATH}; {OIL_LANTERN_SOURCE}", source_enum="OIL_LANTERN", source_item_id=4537),
    CraftingRecipe("combine_studded_body", "Studded body", "combination", "combine", 41, 40.0, _req(("Leather body", 1), ("Steel studs", 1)), "Studded body", source=COMBINATION_SOURCE_PATH, source_enum="STUDDED_BODY"),
    CraftingRecipe("combine_studded_chaps", "Studded chaps", "combination", "combine", 44, 42.0, _req(("Leather chaps", 1), ("Steel studs", 1)), "Studded chaps", source=COMBINATION_SOURCE_PATH, source_enum="STUDDED_CHAPS", source_item_id=1097),
    CraftingRecipe("combine_spiky_vambraces", "Spiky vambraces", "combination", "combine", 32, 6.0, _req(("Leather vambraces", 1), ("Kebbit claws", 1)), "Spiky vambraces", source=COMBINATION_SOURCE_PATH, source_enum="LEATHER_SPIKY_VAMBRACES", source_item_id=10077),
    CraftingRecipe("combine_green_spiky_vambraces", "Green spiky vambraces", "combination", "combine", 32, 6.0, _req(("Green d'hide vambraces", 1), ("Kebbit claws", 1)), "Green spiky vambraces", source=COMBINATION_SOURCE_PATH, source_enum="GREEN_SPIKY_VAMBRACES", source_item_id=10079),
    CraftingRecipe("combine_blue_spiky_vambraces", "Blue spiky vambraces", "combination", "combine", 32, 6.0, _req(("Blue d'hide vambraces", 1), ("Kebbit claws", 1)), "Blue spiky vambraces", source=COMBINATION_SOURCE_PATH, source_enum="BLUE_SPIKY_VAMBRACES", source_item_id=10081),
    CraftingRecipe("combine_red_spiky_vambraces", "Red spiky vambraces", "combination", "combine", 32, 6.0, _req(("Red d'hide vambraces", 1), ("Kebbit claws", 1)), "Red spiky vambraces", source=COMBINATION_SOURCE_PATH, source_enum="RED_SPIKY_VAMBRACES", source_item_id=10083),
    CraftingRecipe("combine_black_spiky_vambraces", "Black spiky vambraces", "combination", "combine", 32, 6.0, _req(("Black d'hide vambraces", 1), ("Kebbit claws", 1)), "Black spiky vambraces", source=COMBINATION_SOURCE_PATH, source_enum="BLACK_SPIKY_VAMBRACES", source_item_id=10085),
    CraftingRecipe("chisel_crab_helmet", "Crab helmet", "combination", "chisel", 15, 32.5, _req(("Fresh crab shell", 1)), "Crab helmet", source=COMBINATION_SOURCE_PATH, source_enum="CRAB_HELMET", tradeable=False, source_item_id=7539),
    CraftingRecipe("chisel_crab_claw", "Crab claw", "combination", "chisel", 15, 32.5, _req(("Fresh crab claw", 1)), "Crab claw", source=COMBINATION_SOURCE_PATH, source_enum="CRAB_CLAW", tradeable=False, source_item_id=7537),
    CraftingRecipe("combine_seaweed_net", "Empty seaweed net", "combination", "combine", 52, 83.0, _req(("Unfinished net", 1), ("Bronze wire", 1)), "Empty seaweed net", source=COMBINATION_SOURCE_PATH, source_enum="SEAWEED_NET", source_item_id=14859),
    CraftingRecipe("combine_armadyl_battlestaff", "Armadyl battlestaff", "combination", "combine", 77, 150.0, _req(("Battlestaff", 1), ("Orb of armadyl", 1)), "Armadyl battlestaff", source=COMBINATION_SOURCE_PATH, source_enum="ARMADYL_BATTLESTAFF", source_item_id=21777),
    CraftingRecipe("string_gold_amulet", "String Gold amulet", "combination", "stringing", 1, 4.0, _req(("Gold amulet (u)", 1), ("Ball of wool", 1)), "Gold amulet", source=COMBINATION_SOURCE_PATH, source_enum="GOLD_AMULET", source_item_id=1692),
    CraftingRecipe("string_sapphire_amulet", "String Sapphire amulet", "combination", "stringing", 1, 4.0, _req(("Sapphire amulet (u)", 1), ("Ball of wool", 1)), "Sapphire amulet", source=COMBINATION_SOURCE_PATH, source_enum="SAPPHIRE_AMULET", source_item_id=1694),
    CraftingRecipe("string_emerald_amulet", "String Emerald amulet", "combination", "stringing", 1, 4.0, _req(("Emerald amulet (u)", 1), ("Ball of wool", 1)), "Emerald amulet", source=COMBINATION_SOURCE_PATH, source_enum="EMERALD_AMULET", source_item_id=1696),
    CraftingRecipe("string_ruby_amulet", "String Ruby amulet", "combination", "stringing", 1, 4.0, _req(("Ruby amulet (u)", 1), ("Ball of wool", 1)), "Ruby amulet", source=COMBINATION_SOURCE_PATH, source_enum="RUBY_AMULET", source_item_id=1698),
    CraftingRecipe("string_diamond_amulet", "String Diamond amulet", "combination", "stringing", 1, 4.0, _req(("Diamond amulet (u)", 1), ("Ball of wool", 1)), "Diamond amulet", source=COMBINATION_SOURCE_PATH, source_enum="DIAMOND_AMULET", source_item_id=1700),
    CraftingRecipe("string_dragonstone_amulet", "String Dragonstone ammy", "combination", "stringing", 1, 4.0, _req(("Dragonstone ammy (u)", 1), ("Ball of wool", 1)), "Dragonstone ammy", source=COMBINATION_SOURCE_PATH, source_enum="DRAGONSTONE_AMULET", source_item_id=1702),
    CraftingRecipe("string_onyx_amulet", "String Onyx amulet", "combination", "stringing", 1, 4.0, _req(("Onyx amulet (u)", 1), ("Ball of wool", 1)), "Onyx amulet", source=COMBINATION_SOURCE_PATH, source_enum="ONYX_AMULET", source_item_id=6581),
    CraftingRecipe("string_unblessed_symbol", "Unblessed symbol", "combination", "stringing", 1, 4.0, _req(("Unstrung symbol", 1), ("Ball of wool", 1)), "Unblessed symbol", source=COMBINATION_SOURCE_PATH, source_enum="UNBLESSED_SYMBOL", source_item_id=1716),
    CraftingRecipe("string_unpowered_symbol", "Unpowered symbol", "combination", "stringing", 1, 4.0, _req(("Unstrung emblem", 1), ("Ball of wool", 1)), "Unpowered symbol", source=COMBINATION_SOURCE_PATH, source_enum="UNPOWERED_SYMBOL", source_item_id=1722),
    CraftingRecipe("polish_buttons", "Polished buttons", "combination", "polish", 3, 5.0, _req(("Buttons", 1)), "Polished buttons", source=POLISHED_BUTTON_SOURCE, source_enum="POLISHED_BUTTONS", tradeable=False, source_item_id=10496),
)

CRAFTING_RECIPES_BY_ID: Dict[str, CraftingRecipe] = {recipe.id: recipe for recipe in CRAFTING_RECIPES}

TANNING_ACTIVITIES: Tuple[TanningActivity, ...] = (
    TanningActivity("tan_soft_leather", "Tan soft leather", "Cowhide", "Leather", 1, "SOFT_LEATHER"),
    TanningActivity("tan_hard_leather", "Tan hard leather", "Cowhide", "Hard leather", 3, "HARD_LEATHER"),
    TanningActivity("tan_snakeskin", "Tan snakeskin", "Snake hide", "Snakeskin", 15, "SNAKESKIN"),
    TanningActivity("tan_swamp_snakeskin", "Tan swamp snakeskin", "Snake hide", "Snakeskin", 20, "SNAKESKIN_SWAMP"),
    TanningActivity("tan_green_dragonhide", "Tan green dragonhide", "Green dragonhide", "Green dragon leather", 20, "GREEN_DRAGONHIDE"),
    TanningActivity("tan_blue_dragonhide", "Tan blue dragonhide", "Blue dragonhide", "Blue dragon leather", 20, "BLUE_DRAGONHIDE"),
    TanningActivity("tan_red_dragonhide", "Tan red dragonhide", "Red dragonhide", "Red dragon leather", 20, "RED_DRAGONHIDE"),
    TanningActivity("tan_black_dragonhide", "Tan black dragonhide", "Black dragonhide", "Black dragon leather", 20, "BLACK_DRAGONHIDE"),
)

LEGACY_CRAFTING_TARGETS: Dict[str, str] = {
    "Soft clay": "",
    "Unfired pot": "form_pot_unfired",
    "Pot": "fire_empty_pot",
    "Ball of wool": "spin_wool_to_ball_of_wool",
    "Gold ring": "jewellery_gold_ring",
    "Gold necklace": "jewellery_gold_necklace",
    "Unfired pie dish": "form_pie_dish_unfired",
    "Pie dish": "fire_pie_dish",
    "Unfired bowl": "form_bowl_unfired",
    "Bowl": "fire_bowl",
    "Bow string": "spin_flax_to_bow_string",
    "Unstrung symbol": "silver_unstrung_symbol",
    "Sapphire ring": "jewellery_sapphire_ring",
    "Sapphire": "cut_sapphire",
    "Silver bolts (unf)": "silver_silver_bolts_unf",
    "Sapphire necklace": "jewellery_sapphire_necklace",
    "Tiara": "silver_tiara",
    "Emerald": "cut_emerald",
    "Emerald ring": "jewellery_emerald_ring",
    "Emerald necklace": "jewellery_emerald_necklace",
    "Ruby ring": "jewellery_ruby_ring",
    "Ruby": "cut_ruby",
    "Ruby necklace": "jewellery_ruby_necklace",
    "Diamond ring": "jewellery_diamond_ring",
    "Diamond": "cut_diamond",
    "Diamond necklace": "jewellery_diamond_necklace",
}

LEGACY_CRAFTING_ITEM_MIGRATIONS: Dict[str, str] = {
    "Unfired pot": "Pot (unfired)",
    "Pot": "Empty pot",
    "Unfired pie dish": "Pie dish (unfired)",
    "Unfired bowl": "Bowl (unfired)",
    "Candle lantern": "Candle lantern (empty)",
    "Oil lamp": "Oil lamp (empty)",
    "Oil lantern": "Oil lantern (unlit)",
    "Bullseye lantern": "Bullseye lantern (empty)",
    "Emerald lantern": "Emerald lantern (unlit)",
    "Mining helmet": "Mining helmet (unlit)",
}


def crafting_recipes_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        recipe.id: {
            "display_name": recipe.display_name,
            "family": recipe.family,
            "station": recipe.station,
            "level": recipe.level,
            "exp": recipe.base_exp,
            "requirements": dict(recipe.requirements),
            "output_item": recipe.output_item,
            "output_qty": recipe.output_qty,
            "source": recipe.source,
            "source_enum": recipe.source_enum,
            "tradeable": recipe.tradeable,
            "category": recipe.category,
            "notes": recipe.notes,
            "source_item_id": recipe.source_item_id,
            "byproducts": dict(recipe.byproducts),
            "required_items": dict(recipe.required_items),
            "consume_thread_on_roll": recipe.consume_thread_on_roll,
        }
        for recipe in CRAFTING_RECIPES
    }


def crafting_output_items() -> Tuple[str, ...]:
    return tuple(dict.fromkeys(recipe.output_item for recipe in CRAFTING_RECIPES))


def tanning_activities_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        activity.id: {
            "display_name": activity.display_name,
            "requirements": {activity.raw_item: 1, "Coins": activity.price},
            "output_item": activity.output_item,
            "output_qty": 1,
            "batch_size": 28,
            "group": "material_processing",
            "source": TANNING_SOURCE,
            "source_enum": activity.source_enum,
        }
        for activity in TANNING_ACTIVITIES
    }


def crafting_required_items_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        item: {
            "level": 1,
            "exp": 0.0,
            "category": "tool",
            "source": GLASSBLOWING_ACTION_SOURCE if item == "Glassblowing pipe" else MOULD_ITEMS_SOURCE,
            "item_id": item_id,
            "tradeable": item not in CRAFTING_REQUIRED_ITEM_NONTRADEABLE,
        }
        for item, item_id in CRAFTING_REQUIRED_ITEM_SOURCE_IDS.items()
    }


def crafting_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    outputs = set(crafting_output_items())
    extras: Dict[str, Dict[str, object]] = {}
    required_items = crafting_required_items_as_dict()
    for recipe in CRAFTING_RECIPES:
        for material, _amount in recipe.requirements:
            if material not in outputs:
                extras.setdefault(
                    material,
                    {
                        "level": 1,
                        "exp": 0.0,
                        "category": "material",
                        "source": f"Crafting input for {recipe.display_name}",
                        "tradeable": True,
                    },
                )
        for item, _amount in recipe.required_items:
            if item not in outputs:
                if item in CRAFTING_REQUIRED_ITEM_SOURCE_IDS:
                    extras.setdefault(item, required_items[item])
                else:
                    extras.setdefault(
                        item,
                        {
                            "level": 1,
                            "exp": 0.0,
                            "category": "material",
                            "source": f"Crafting requirement for {recipe.display_name}",
                            "tradeable": True,
                        },
                    )
    return extras
