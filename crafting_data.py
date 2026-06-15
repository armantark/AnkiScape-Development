"""2011Scape-sourced Crafting data for AnkiScape.

The rows here are transcribed from the local 2011Scape rev 667 Crafting
plugin. Runtime imports only this checked-in Python data; the emulator checkout
is a development-time source audit input.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

CRAFTING_SOURCE_ROOT = "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting"
COMBINATION_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/combine/CombinationData.kt"
ITEMS_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"
DEFAULT_CRAFTING_TARGET = "form_pot_unfired"


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


def _req(*pairs: Tuple[str, int]) -> Tuple[Tuple[str, int], ...]:
    return tuple(pairs)


GEM_SOURCE = f"{CRAFTING_SOURCE_ROOT}/gems/GemData.kt"
POTTERY_SOURCE = f"{CRAFTING_SOURCE_ROOT}/pottery/PotteryData.kt"
POTTERY_RUNE_SOURCE = f"{CRAFTING_SOURCE_ROOT}/pottery/AddRuneAction.kt"
SPINNING_SOURCE = f"{CRAFTING_SOURCE_ROOT}/spinning/SpinningData.kt"
SILVER_SOURCE = f"{CRAFTING_SOURCE_ROOT}/silver/SilverData.kt"
JEWELLERY_SOURCE = f"{CRAFTING_SOURCE_ROOT}/jewellery/JewelleryData.kt"
LEATHER_SOURCE = f"{CRAFTING_SOURCE_ROOT}/leather/LeatherData.kt"
GLASS_SOURCE = f"{CRAFTING_SOURCE_ROOT}/glassblowing/GlassData.kt"
BATTLESTAFF_SOURCE = f"{CRAFTING_SOURCE_ROOT}/weaponry/BattlestaffData.kt"
WEAVING_SOURCE = f"{CRAFTING_SOURCE_ROOT}/weaving/WeavingData.kt"


CRAFTING_RECIPES: Tuple[CraftingRecipe, ...] = (
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
    CraftingRecipe("form_clay_ring_unfired", "Clay ring (unfired)", "pottery", "potters_wheel", 4, 11.3, _req(("Soft clay", 1)), "Clay ring (unfired)", source=POTTERY_SOURCE, source_enum="CLAY_RING"),
    CraftingRecipe("fire_clay_ring", "Clay ring", "pottery", "pottery_oven", 4, 11.0, _req(("Clay ring (unfired)", 1)), "Clay ring", source=POTTERY_SOURCE, source_enum="CLAY_RING"),
    CraftingRecipe("form_pie_dish_unfired", "Pie dish (unfired)", "pottery", "potters_wheel", 7, 15.0, _req(("Soft clay", 1)), "Pie dish (unfired)", source=POTTERY_SOURCE, source_enum="PIE_DISH"),
    CraftingRecipe("fire_pie_dish", "Pie dish", "pottery", "pottery_oven", 7, 10.0, _req(("Pie dish (unfired)", 1)), "Pie dish", source=POTTERY_SOURCE, source_enum="PIE_DISH"),
    CraftingRecipe("form_bowl_unfired", "Bowl (unfired)", "pottery", "potters_wheel", 8, 18.0, _req(("Soft clay", 1)), "Bowl (unfired)", source=POTTERY_SOURCE, source_enum="BOWL"),
    CraftingRecipe("fire_bowl", "Bowl", "pottery", "pottery_oven", 8, 15.0, _req(("Bowl (unfired)", 1)), "Bowl", source=POTTERY_SOURCE, source_enum="BOWL"),
    CraftingRecipe("form_plant_pot_unfired", "Plant pot (unfired)", "pottery", "potters_wheel", 19, 20.0, _req(("Soft clay", 1)), "Plant pot (unfired)", source=POTTERY_SOURCE, source_enum="PLANT_POT"),
    CraftingRecipe("fire_plant_pot", "Plant pot", "pottery", "pottery_oven", 19, 17.5, _req(("Plant pot (unfired)", 1)), "Plant pot", source=POTTERY_SOURCE, source_enum="PLANT_POT"),
    CraftingRecipe("form_pot_lid_unfired", "Pot lid (unfired)", "pottery", "potters_wheel", 25, 20.0, _req(("Soft clay", 1)), "Pot lid (unfired)", source=POTTERY_SOURCE, source_enum="POT_LID"),
    CraftingRecipe("fire_pot_lid", "Pot lid", "pottery", "pottery_oven", 25, 20.0, _req(("Pot lid (unfired)", 1)), "Pot lid", source=POTTERY_SOURCE, source_enum="POT_LID"),

    # Representative urn rows from every source urn family; each is live and input-gated.
    CraftingRecipe("form_cracked_mining_urn_unf", "Cracked mining urn (unf)", "pottery", "potters_wheel", 1, 11.8, _req(("Soft clay", 2)), "Cracked mining urn (unf)", source=POTTERY_SOURCE, source_enum="MINING_URNS", notes="Urn forming uses 2 Soft clay in source."),
    CraftingRecipe("fire_cracked_mining_urn_nr", "Cracked mining urn (nr)", "pottery", "pottery_oven", 1, 16.8, _req(("Cracked mining urn (unf)", 1)), "Cracked mining urn (nr)", source=POTTERY_SOURCE, source_enum="MINING_URNS"),
    CraftingRecipe("add_rune_cracked_mining_urn", "Cracked mining urn", "pottery", "add_rune", 1, 1.0, _req(("Cracked mining urn (nr)", 1), ("Earth rune", 1)), "Cracked mining urn", source=POTTERY_RUNE_SOURCE, source_enum="MINING_URNS", notes="Rune source/use belongs to future Runecrafting/urn behavior; recipe is live and material-gated."),
    CraftingRecipe("form_cracked_cooking_urn_unf", "Cracked cooking urn (unf)", "pottery", "potters_wheel", 2, 12.0, _req(("Soft clay", 2)), "Cracked cooking urn (unf)", source=POTTERY_SOURCE, source_enum="COOKING_URNS"),
    CraftingRecipe("fire_cracked_cooking_urn_nr", "Cracked cooking urn (nr)", "pottery", "pottery_oven", 2, 18.0, _req(("Cracked cooking urn (unf)", 1)), "Cracked cooking urn (nr)", source=POTTERY_SOURCE, source_enum="COOKING_URNS"),
    CraftingRecipe("add_rune_cracked_cooking_urn", "Cracked cooking urn", "pottery", "add_rune", 2, 1.0, _req(("Cracked cooking urn (nr)", 1), ("Fire rune", 1)), "Cracked cooking urn", source=POTTERY_RUNE_SOURCE, source_enum="COOKING_URNS"),
    CraftingRecipe("form_decorated_mining_urn_unf", "Decorated mining urn (unf)", "pottery", "potters_wheel", 59, 38.0, _req(("Soft clay", 2)), "Decorated mining urn (unf)", source=POTTERY_SOURCE, source_enum="MINING_URNS"),
    CraftingRecipe("fire_decorated_mining_urn_nr", "Decorated mining urn (nr)", "pottery", "pottery_oven", 59, 57.0, _req(("Decorated mining urn (unf)", 1)), "Decorated mining urn (nr)", source=POTTERY_SOURCE, source_enum="MINING_URNS"),
    CraftingRecipe("add_rune_decorated_mining_urn", "Decorated mining urn", "pottery", "add_rune", 59, 1.0, _req(("Decorated mining urn (nr)", 1), ("Earth rune", 1)), "Decorated mining urn", source=POTTERY_RUNE_SOURCE, source_enum="MINING_URNS"),

    # Spinning. No XP-bearing batching.
    CraftingRecipe("spin_wool_to_ball_of_wool", "Ball of wool", "spinning", "spinning_wheel", 1, 2.5, _req(("Wool", 1)), "Ball of wool", source=SPINNING_SOURCE, source_enum="WOOL"),
    CraftingRecipe("spin_flax_to_bow_string", "Bow string", "spinning", "spinning_wheel", 10, 15.0, _req(("Flax", 1)), "Bow string", source=SPINNING_SOURCE, source_enum="FLAX"),
    CraftingRecipe("spin_sinew_to_crossbow_string", "Crossbow string", "spinning", "spinning_wheel", 10, 15.0, _req(("Sinew", 1)), "Crossbow string", source=SPINNING_SOURCE, source_enum="CBOW_STRING", notes="Live target; input-starved until sinew acquisition exists."),
    CraftingRecipe("spin_magic_roots_to_magic_string", "Magic string", "spinning", "spinning_wheel", 19, 30.0, _req(("Magic roots", 1)), "Magic string", source=SPINNING_SOURCE, source_enum="MAGIC_STRING", notes="Live target; input-starved until root acquisition exists."),
    CraftingRecipe("spin_hair_to_rope", "Rope", "spinning", "spinning_wheel", 30, 25.0, _req(("Hair", 1)), "Rope", source=SPINNING_SOURCE, source_enum="ROPE", notes="Live target; input-starved until yak hair acquisition exists."),

    # Silver.
    CraftingRecipe("silver_unstrung_symbol", "Unstrung symbol", "silver", "furnace", 16, 50.0, _req(("Silver bar", 1)), "Unstrung symbol", source=SILVER_SOURCE, source_enum="HOLY_SYMBOL"),
    CraftingRecipe("silver_unstrung_emblem", "Unstrung emblem", "silver", "furnace", 17, 50.0, _req(("Silver bar", 1)), "Unstrung emblem", source=SILVER_SOURCE, source_enum="UNHOLY_SYMBOL"),
    CraftingRecipe("silver_silver_sickle", "Silver sickle", "silver", "furnace", 18, 50.0, _req(("Silver bar", 1)), "Silver sickle", source=SILVER_SOURCE, source_enum="SILVER_SICKLE"),
    CraftingRecipe("silver_conductor", "Conductor", "silver", "furnace", 20, 50.0, _req(("Silver bar", 1)), "Conductor", source=SILVER_SOURCE, source_enum="CONDUCTOR_ROD", tradeable=False, notes="Quest item; live but use-starved."),
    CraftingRecipe("silver_silver_bolts_unf", "Silver bolts (unf)", "silver", "furnace", 21, 50.0, _req(("Silver bar", 1)), "Silver bolts (unf)", 10, source=SILVER_SOURCE, source_enum="SILVER_BOLTS"),
    CraftingRecipe("silver_tiara", "Tiara", "silver", "furnace", 23, 52.5, _req(("Silver bar", 1)), "Tiara", source=SILVER_SOURCE, source_enum="TIARA"),
    CraftingRecipe("silver_demonic_sigil", "Demonic sigil", "silver", "furnace", 30, 50.0, _req(("Silver bar", 1)), "Demonic sigil", source=SILVER_SOURCE, source_enum="DEMONIC_SIGIL", tradeable=False, notes="Quest item; live but use-starved."),

    # Jewellery.
    CraftingRecipe("jewellery_gold_ring", "Gold ring", "jewellery", "furnace", 5, 15.0, _req(("Gold bar", 1)), "Gold ring", source=JEWELLERY_SOURCE, source_enum="GOLD"),
    CraftingRecipe("jewellery_gold_necklace", "Gold necklace", "jewellery", "furnace", 6, 20.0, _req(("Gold bar", 1)), "Gold necklace", source=JEWELLERY_SOURCE, source_enum="GOLD"),
    CraftingRecipe("jewellery_gold_bracelet", "Gold bracelet", "jewellery", "furnace", 7, 25.0, _req(("Gold bar", 1)), "Gold bracelet", source=JEWELLERY_SOURCE, source_enum="GOLD"),
    CraftingRecipe("jewellery_gold_amulet", "Gold amulet", "jewellery", "furnace", 8, 30.0, _req(("Gold bar", 1)), "Gold amulet", source=JEWELLERY_SOURCE, source_enum="GOLD"),
    CraftingRecipe("jewellery_sapphire_ring", "Sapphire ring", "jewellery", "furnace", 20, 40.0, _req(("Gold bar", 1), ("Sapphire", 1)), "Sapphire ring", source=JEWELLERY_SOURCE, source_enum="SAPPHIRE"),
    CraftingRecipe("jewellery_sapphire_necklace", "Sapphire necklace", "jewellery", "furnace", 22, 55.0, _req(("Gold bar", 1), ("Sapphire", 1)), "Sapphire necklace", source=JEWELLERY_SOURCE, source_enum="SAPPHIRE"),
    CraftingRecipe("jewellery_sapphire_bracelet", "Sapphire bracelet", "jewellery", "furnace", 23, 60.0, _req(("Gold bar", 1), ("Sapphire", 1)), "Sapphire bracelet", source=JEWELLERY_SOURCE, source_enum="SAPPHIRE"),
    CraftingRecipe("jewellery_sapphire_amulet", "Sapphire amulet", "jewellery", "furnace", 24, 65.0, _req(("Gold bar", 1), ("Sapphire", 1)), "Sapphire amulet", source=JEWELLERY_SOURCE, source_enum="SAPPHIRE"),
    CraftingRecipe("jewellery_emerald_ring", "Emerald ring", "jewellery", "furnace", 27, 55.0, _req(("Gold bar", 1), ("Emerald", 1)), "Emerald ring", source=JEWELLERY_SOURCE, source_enum="EMERALD"),
    CraftingRecipe("jewellery_emerald_necklace", "Emerald necklace", "jewellery", "furnace", 29, 60.0, _req(("Gold bar", 1), ("Emerald", 1)), "Emerald necklace", source=JEWELLERY_SOURCE, source_enum="EMERALD"),
    CraftingRecipe("jewellery_ruby_ring", "Ruby ring", "jewellery", "furnace", 34, 70.0, _req(("Gold bar", 1), ("Ruby", 1)), "Ruby ring", source=JEWELLERY_SOURCE, source_enum="RUBY"),
    CraftingRecipe("jewellery_ruby_necklace", "Ruby necklace", "jewellery", "furnace", 40, 75.0, _req(("Gold bar", 1), ("Ruby", 1)), "Ruby necklace", source=JEWELLERY_SOURCE, source_enum="RUBY"),
    CraftingRecipe("jewellery_diamond_ring", "Diamond ring", "jewellery", "furnace", 43, 85.0, _req(("Gold bar", 1), ("Diamond", 1)), "Diamond ring", source=JEWELLERY_SOURCE, source_enum="DIAMOND"),
    CraftingRecipe("jewellery_diamond_necklace", "Diamond necklace", "jewellery", "furnace", 56, 90.0, _req(("Gold bar", 1), ("Diamond", 1)), "Diamond necklace", source=JEWELLERY_SOURCE, source_enum="DIAMOND"),
    CraftingRecipe("jewellery_dragonstone_ring", "Dragonstone ring", "jewellery", "furnace", 55, 100.0, _req(("Gold bar", 1), ("Dragonstone", 1)), "Dragonstone ring", source=JEWELLERY_SOURCE, source_enum="DRAGONSTONE", notes="Live target; input-starved until dragonstone acquisition exists."),
    CraftingRecipe("jewellery_dragon_necklace", "Dragon necklace", "jewellery", "furnace", 72, 105.0, _req(("Gold bar", 1), ("Dragonstone", 1)), "Dragon necklace", source=JEWELLERY_SOURCE, source_enum="DRAGONSTONE", notes="Live target; input-starved until dragonstone acquisition exists."),
    CraftingRecipe("jewellery_dragonstone_ammy", "Dragonstone ammy", "jewellery", "furnace", 80, 150.0, _req(("Gold bar", 1), ("Dragonstone", 1)), "Dragonstone ammy", source=JEWELLERY_SOURCE, source_enum="DRAGONSTONE", notes="Live target; input-starved until dragonstone acquisition exists."),
    CraftingRecipe("jewellery_onyx_ring", "Onyx ring", "jewellery", "furnace", 67, 115.0, _req(("Gold bar", 1), ("Onyx", 1)), "Onyx ring", source=JEWELLERY_SOURCE, source_enum="ONYX", notes="Live target; input-starved until onyx acquisition exists."),
    CraftingRecipe("jewellery_onyx_necklace", "Onyx necklace", "jewellery", "furnace", 82, 120.0, _req(("Gold bar", 1), ("Onyx", 1)), "Onyx necklace", source=JEWELLERY_SOURCE, source_enum="ONYX", notes="Live target; input-starved until onyx acquisition exists."),
    CraftingRecipe("jewellery_onyx_amulet", "Onyx amulet", "jewellery", "furnace", 90, 165.0, _req(("Gold bar", 1), ("Onyx", 1)), "Onyx amulet", source=JEWELLERY_SOURCE, source_enum="ONYX", notes="Live target; input-starved until onyx acquisition exists."),

    # Leather, glass, battlestaves, weaving, and selected source Crafting combinations.
    CraftingRecipe("leather_leather_gloves", "Leather gloves", "leather", "needle", 1, 13.8, _req(("Leather", 1)), "Leather gloves", source=LEATHER_SOURCE, source_enum="LEATHER"),
    CraftingRecipe("leather_leather_body", "Leather body", "leather", "needle", 14, 25.0, _req(("Leather", 1)), "Leather body", source=LEATHER_SOURCE, source_enum="LEATHER"),
    CraftingRecipe("leather_hardleather_body", "Hardleather body", "leather", "needle", 28, 35.0, _req(("Hard leather", 1)), "Hardleather body", source=LEATHER_SOURCE, source_enum="HARD_LEATHER"),
    CraftingRecipe("leather_green_dhide_body", "Green d'hide body", "leather", "needle", 63, 186.0, _req(("Green dragon leather", 3)), "Green d'hide body", source=LEATHER_SOURCE, source_enum="GREEN_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists."),
    CraftingRecipe("leather_blue_dhide_body", "Blue d'hide body", "leather", "needle", 71, 210.0, _req(("Blue dragon leather", 3)), "Blue d'hide body", source=LEATHER_SOURCE, source_enum="BLUE_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists."),
    CraftingRecipe("leather_black_dhide_body", "Black d'hide body", "leather", "needle", 84, 258.0, _req(("Black dragon leather", 3)), "Black d'hide body", source=LEATHER_SOURCE, source_enum="BLACK_DRAGONHIDE", notes="Live target; input-starved until hide/tanning acquisition loop exists."),
    CraftingRecipe("glass_beer_glass", "Beer glass", "glass", "glassblowing", 1, 17.5, _req(("Molten glass", 1)), "Beer glass", source=GLASS_SOURCE, source_enum="BEER_GLASS", notes="Live target; input-starved until molten glass source exists."),
    CraftingRecipe("glass_vial", "Vial", "glass", "glassblowing", 33, 35.0, _req(("Molten glass", 1)), "Vial", source=GLASS_SOURCE, source_enum="EMPTY_VIAL", notes="Live target; input-starved until molten glass source exists."),
    CraftingRecipe("glass_unpowered_orb", "Unpowered orb", "glass", "glassblowing", 46, 52.5, _req(("Molten glass", 1)), "Unpowered orb", source=GLASS_SOURCE, source_enum="UNPOWERED_ORB", notes="Live target; input-starved until molten glass source exists."),
    CraftingRecipe("battlestaff_water_battlestaff", "Water battlestaff", "battlestaff", "attach_orb", 54, 100.0, _req(("Battlestaff", 1), ("Water orb", 1)), "Water battlestaff", source=BATTLESTAFF_SOURCE, source_enum="WATER_BATTLESTAFF", notes="Orb acquisition/enchanting belongs to future Magic or Utility design."),
    CraftingRecipe("battlestaff_air_battlestaff", "Air battlestaff", "battlestaff", "attach_orb", 66, 137.5, _req(("Battlestaff", 1), ("Air orb", 1)), "Air battlestaff", source=BATTLESTAFF_SOURCE, source_enum="AIR_BATTLESTAFF", notes="Orb acquisition/enchanting belongs to future Magic or Utility design."),
    CraftingRecipe("weave_strip_of_cloth", "Strip of cloth", "weaving", "loom", 10, 12.0, _req(("Ball of wool", 4)), "Strip of cloth", source=WEAVING_SOURCE, source_enum="STRIP_OF_CLOTH"),
    CraftingRecipe("weave_empty_sack", "Empty sack", "weaving", "loom", 21, 38.0, _req(("Jute fibre", 4)), "Empty sack", source=WEAVING_SOURCE, source_enum="EMPTY_SACK", notes="Live target; input-starved until Farming crop loop exists."),
    CraftingRecipe("combine_studded_body", "Studded body", "combination", "combine", 41, 40.0, _req(("Leather body", 1), ("Steel studs", 1)), "Studded body", source=COMBINATION_SOURCE_PATH, source_enum="STUDDED_BODY"),
    CraftingRecipe("string_dragonstone_amulet", "Dragonstone ammy", "combination", "stringing", 1, 4.0, _req(("Dragonstone ammy", 1), ("Ball of wool", 1)), "Dragonstone ammy", source=COMBINATION_SOURCE_PATH, source_enum="DRAGONSTONE_AMULET", notes="Downstream enchant action belongs to future Magic."),
)

CRAFTING_RECIPES_BY_ID: Dict[str, CraftingRecipe] = {recipe.id: recipe for recipe in CRAFTING_RECIPES}

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
        }
        for recipe in CRAFTING_RECIPES
    }


def crafting_output_items() -> Tuple[str, ...]:
    return tuple(dict.fromkeys(recipe.output_item for recipe in CRAFTING_RECIPES))


def crafting_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    outputs = set(crafting_output_items())
    extras: Dict[str, Dict[str, object]] = {}
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
    return extras
