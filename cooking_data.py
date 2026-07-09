"""2011Scape-sourced Cooking data for AnkiScape.

The XP-bearing rows are copied from the local 2011Scape rev 667 Cooking table.
No-XP prep rows are AnkiScape bridge activities that connect existing source
items into the raw inputs consumed by that table.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Tuple


COOKING_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/cooking/CookingData.kt"
)
COOKING_RUNTIME_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/cooking/CookingAction.kt"
)
COOKING_PLUGIN_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/cooking/raw_food_cooking.plugin.kts"
)
GUT_FISH_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/items/gut_fish.plugin.kts"
)
SEAWEED_COOKING_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/objs/cookingrange/seawead_cooking.plugin.kts"
)
ITEMS_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/api/cfg/Items.kt"
)
ITEMS_YML_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"
WHEAT_PICK_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/objs/pick/pick_wheat.plugin.kts"
)
MILL_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/objs/mill/flour_bin.plugin.kts"
)
WATER_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/objs/watersource/WaterContainerData.kt"
)
_FLOUR_WATER_REQUIREMENTS: Mapping[str, int] = {"Pot of flour": 1, "Bucket of water": 1}
_FLOUR_WATER_BYPRODUCTS: Mapping[str, int] = {"Empty pot": 1, "Bucket": 1}
COOKING_PREP_BRIDGE_SOURCE = "AnkiScape no-XP Cooking prep bridge, item IDs audited from 2011Scape Items.kt/items.yml."


@dataclass(frozen=True)
class CookingTarget:
    id: str
    source_enum: str
    display_name: str
    family: str
    raw_const: str
    raw_item_id: int
    raw_item: str
    cooked_const: str
    cooked_item_id: int
    cooked_item: str
    burnt_const: str
    burnt_item_id: int
    burnt_item: str
    level: int
    base_exp: float
    low_chance: int
    high_chance: int
    output_variant: str = "primary"
    source: str = COOKING_SOURCE_PATH
    runtime_source: str = COOKING_RUNTIME_SOURCE_PATH
    status: str = "implemented"
    source_success_formula: Mapping[str, float] = ()
    source_always_succeeds: bool = False
    source_no_level_requirement: bool = False
    byproduct_item: str = ""
    byproduct_chance: float = 0.0
    failure_kind: str = "burn"


@dataclass(frozen=True)
class CookingPrepActivity:
    id: str
    display_name: str
    requirements: Mapping[str, int]
    output_item: str
    group: str = "cooking_prep"
    output_qty: int = 1
    byproducts: Mapping[str, int] = ()
    batch_size: int = 28
    source: str = COOKING_PREP_BRIDGE_SOURCE


COOKING_TARGETS: Tuple[CookingTarget, ...] = (
    CookingTarget('cook_shrimps', 'SHRIMPS', 'Cook raw shrimps', 'fish', 'RAW_SHRIMPS', 317, 'Raw shrimps', 'SHRIMPS', 315, 'Shrimps', 'BURNT_SHRIMP', 7954, 'Burnt shrimp', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('cook_anchovies', 'ANCHOVIES', 'Cook raw anchovies', 'fish', 'RAW_ANCHOVIES', 321, 'Raw anchovies', 'ANCHOVIES', 319, 'Anchovies', 'BURNT_FISH', 323, 'Burnt fish', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('cook_crayfish', 'CRAYFISH', 'Cook raw crayfish', 'fish', 'RAW_CRAYFISH', 13435, 'Raw crayfish', 'CRAYFISH', 13433, 'Crayfish', 'BURNT_CRAYFISH', 13437, 'Burnt crayfish', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('cook_sardine', 'SARDINE', 'Cook raw sardine', 'fish', 'RAW_SARDINE', 327, 'Raw sardine', 'SARDINE', 325, 'Sardine', 'BURNT_FISH_369', 369, 'Burnt fish', 1, 40.0, 118, 492, output_variant='primary'),
    CookingTarget('cook_herring', 'HERRING', 'Cook raw herring', 'fish', 'RAW_HERRING', 345, 'Raw herring', 'HERRING', 347, 'Herring', 'BURNT_FISH_357', 357, 'Burnt fish', 5, 50.0, 108, 472, output_variant='primary'),
    CookingTarget('cook_mackerel', 'MACKEREL', 'Cook raw mackerel', 'fish', 'RAW_MACKEREL', 353, 'Raw mackerel', 'MACKEREL', 355, 'Mackerel', 'BURNT_FISH_357', 357, 'Burnt fish', 10, 60.0, 98, 452, output_variant='primary'),
    CookingTarget('cook_trout', 'TROUT', 'Cook raw trout', 'fish', 'RAW_TROUT', 335, 'Raw trout', 'TROUT', 333, 'Trout', 'BURNT_FISH_343', 343, 'Burnt fish', 15, 70.0, 88, 432, output_variant='primary'),
    CookingTarget('cook_cod', 'COD', 'Cook raw cod', 'fish', 'RAW_COD', 341, 'Raw cod', 'COD', 339, 'Cod', 'BURNT_FISH_343', 343, 'Burnt fish', 18, 75.0, 88, 432, output_variant='primary'),
    CookingTarget('cook_pike', 'PIKE', 'Cook raw pike', 'fish', 'RAW_PIKE', 349, 'Raw pike', 'PIKE', 351, 'Pike', 'BURNT_FISH_343', 343, 'Burnt fish', 20, 80.0, 78, 412, output_variant='primary'),
    CookingTarget('cook_salmon', 'SALMON', 'Cook raw salmon', 'fish', 'RAW_SALMON', 331, 'Raw salmon', 'SALMON', 329, 'Salmon', 'BURNT_FISH_343', 343, 'Burnt fish', 25, 90.0, 68, 392, output_variant='primary'),
    CookingTarget('cook_tuna', 'TUNA', 'Cook raw tuna', 'fish', 'RAW_TUNA', 359, 'Raw tuna', 'TUNA', 361, 'Tuna', 'BURNT_FISH_367', 367, 'Burnt fish', 30, 100.0, 58, 372, output_variant='primary'),
    CookingTarget('cook_lobster', 'LOBSTER', 'Cook raw lobster', 'fish', 'RAW_LOBSTER', 377, 'Raw lobster', 'LOBSTER', 379, 'Lobster', 'BURNT_LOBSTER', 381, 'Burnt lobster', 40, 120.0, 38, 332, output_variant='primary'),
    CookingTarget('cook_bass', 'BASS', 'Cook raw bass', 'fish', 'RAW_BASS', 363, 'Raw bass', 'BASS', 365, 'Bass', 'BURNT_FISH_367', 367, 'Burnt fish', 43, 130.0, 33, 312, output_variant='primary'),
    CookingTarget('cook_swordfish', 'SWORDFISH', 'Cook raw swordfish', 'fish', 'RAW_SWORDFISH', 371, 'Raw swordfish', 'SWORDFISH', 373, 'Swordfish', 'BURNT_SWORDFISH', 375, 'Burnt swordfish', 45, 140.0, 18, 292, output_variant='primary'),
    CookingTarget('cook_monkfish', 'MONKFISH', 'Cook raw monkfish', 'fish', 'RAW_MONKFISH', 7944, 'Raw monkfish', 'MONKFISH', 7946, 'Monkfish', 'BURNT_MONKFISH', 7948, 'Burnt monkfish', 62, 150.0, 13, 280, output_variant='primary'),
    CookingTarget('cook_shark', 'SHARK', 'Cook raw shark', 'fish', 'RAW_SHARK', 383, 'Raw shark', 'SHARK', 385, 'Shark', 'BURNT_SHARK', 387, 'Burnt shark', 80, 210.0, 1, 232, output_variant='primary'),
    CookingTarget('cook_sea_turtle', 'SEA_TURTLE', 'Cook raw sea turtle', 'fish', 'RAW_SEA_TURTLE', 395, 'Raw sea turtle', 'SEA_TURTLE', 397, 'Sea turtle', 'BURNT_SEA_TURTLE', 399, 'Burnt sea turtle', 82, 211.3, 1, 222, output_variant='primary'),
    CookingTarget('cook_manta_ray', 'MANTA_RAY', 'Cook raw manta ray', 'fish', 'RAW_MANTA_RAY', 389, 'Raw manta ray', 'MANTA_RAY', 391, 'Manta ray', 'BURNT_MANTA_RAY', 393, 'Burnt manta ray', 91, 216.3, 1, 222, output_variant='primary'),
    CookingTarget('cook_cavefish', 'CAVEFISH', 'Cook raw cavefish', 'fish', 'RAW_CAVEFISH', 15264, 'Raw cavefish', 'CAVEFISH', 15266, 'Cavefish', 'BURNT_CAVEFISH', 15268, 'Burnt cavefish', 88, 214.0, 1, 232, output_variant='primary'),
    CookingTarget('cook_rocktail', 'ROCKTAIL', 'Cook raw rocktail', 'fish', 'RAW_ROCKTAIL', 15270, 'Raw rocktail', 'ROCKTAIL', 15272, 'Rocktail', 'BURNT_ROCKTAIL', 15274, 'Burnt rocktail', 93, 225.0, 1, 222, output_variant='primary'),
    CookingTarget('cook_cave_eel', 'CAVE_EEL', 'Cook raw cave eel', 'eels', 'RAW_CAVE_EEL', 5001, 'Raw cave eel', 'CAVE_EEL', 5003, 'Cave eel', 'BURNT_CAVE_EEL', 5002, 'Burnt cave eel', 38, 115.0, 38, 332, output_variant='primary'),
    CookingTarget('cook_slimy_eel', 'SLIMY_EEL', 'Cook slimy eel', 'eels', 'SLIMY_EEL', 3379, 'Slimy eel', 'COOKED_SLIMY_EEL', 3381, 'Cooked slimy eel', 'BURNT_EEL', 3383, 'Burnt eel', 28, 95.0, 63, 382, output_variant='primary'),
    CookingTarget('cook_rainbow_fish', 'RAINBOW_FISH', 'Cook raw rainbow fish', 'fish', 'RAW_RAINBOW_FISH', 10138, 'Raw rainbow fish', 'RAINBOW_FISH', 10136, 'Rainbow fish', 'BURNT_RAINBOW_FISH', 10140, 'Burnt rainbow fish', 35, 110.0, 56, 370, output_variant='primary'),
    CookingTarget('cook_thin_snail', 'THIN_SNAIL', 'Cook thin snail', 'snails', 'THIN_SNAIL', 3363, 'Thin snail', 'THIN_SNAIL_MEAT', 3369, 'Thin snail meat', 'BURNT_SNAIL', 3375, 'Burnt snail', 12, 70.0, 93, 444, output_variant='primary'),
    CookingTarget('cook_lean_snail', 'LEAN_SNAIL', 'Cook lean snail', 'snails', 'LEAN_SNAIL', 3365, 'Lean snail', 'LEAN_SNAIL_MEAT', 3371, 'Lean snail meat', 'BURNT_SNAIL', 3375, 'Burnt snail', 17, 80.0, 93, 444, output_variant='primary'),
    CookingTarget('cook_fat_snail', 'FAT_SNAIL', 'Cook fat snail', 'snails', 'FAT_SNAIL', 3367, 'Fat snail', 'FAT_SNAIL_MEAT', 3373, 'Fat snail meat', 'BURNT_SNAIL', 3375, 'Burnt snail', 22, 95.0, 73, 402, output_variant='primary'),
    CookingTarget('cook_bread', 'BREAD', 'Cook bread dough', 'bread', 'BREAD_DOUGH', 2307, 'Bread dough', 'BREAD', 2309, 'Bread', 'BURNT_BREAD', 2311, 'Burnt bread', 1, 40.0, 118, 492, output_variant='primary'),
    CookingTarget('cook_pitta_bread', 'PITTA_BREAD', 'Cook pitta dough', 'bread', 'PITTA_DOUGH', 1863, 'Pitta dough', 'PITTA_BREAD', 1865, 'Pitta bread', 'BURNT_PITTA_BREAD', 1867, 'Burnt pitta bread', 58, 40.0, 118, 492, output_variant='primary'),
    CookingTarget('cook_redberry_pie', 'REDBERRY_PIE', 'Cook uncooked berry pie', 'pies', 'UNCOOKED_BERRY_PIE', 2321, 'Uncooked berry pie', 'REDBERRY_PIE', 2325, 'Redberry pie', 'BURNT_PIE', 2329, 'Burnt pie', 10, 78.0, 98, 452, output_variant='primary'),
    CookingTarget('cook_meat_pie', 'MEAT_PIE', 'Cook uncooked meat pie', 'pies', 'UNCOOKED_MEAT_PIE', 2319, 'Uncooked meat pie', 'MEAT_PIE', 2327, 'Meat pie', 'BURNT_PIE', 2329, 'Burnt pie', 20, 110.0, 78, 412, output_variant='primary'),
    CookingTarget('cook_mud_pie', 'MUD_PIE', 'Cook raw mud pie', 'pies', 'RAW_MUD_PIE', 7168, 'Raw mud pie', 'MUD_PIE', 7170, 'Mud pie', 'BURNT_PIE', 2329, 'Burnt pie', 29, 128.0, 58, 372, output_variant='primary'),
    CookingTarget('cook_apple_pie', 'APPLE_PIE', 'Cook uncooked apple pie', 'pies', 'UNCOOKED_APPLE_PIE', 2317, 'Uncooked apple pie', 'APPLE_PIE', 2323, 'Apple pie', 'BURNT_PIE', 2329, 'Burnt pie', 30, 130.0, 58, 372, output_variant='primary'),
    CookingTarget('cook_garden_pie', 'GARDEN_PIE', 'Cook raw garden pie', 'pies', 'RAW_GARDEN_PIE', 7176, 'Raw garden pie', 'GARDEN_PIE', 7178, 'Garden pie', 'BURNT_PIE', 2329, 'Burnt pie', 34, 138.0, 48, 352, output_variant='primary'),
    CookingTarget('cook_fish_pie', 'FISH_PIE', 'Cook raw fish pie', 'pies', 'RAW_FISH_PIE', 7186, 'Raw fish pie', 'FISH_PIE', 7188, 'Fish pie', 'BURNT_PIE', 2329, 'Burnt pie', 47, 164.0, 38, 332, output_variant='primary'),
    CookingTarget('cook_admiral_pie', 'ADMIRAL_PIE', 'Cook raw admiral pie', 'pies', 'RAW_ADMIRAL_PIE', 7196, 'Raw admiral pie', 'ADMIRAL_PIE', 7198, 'Admiral pie', 'BURNT_PIE', 2329, 'Burnt pie', 70, 210.0, 15, 270, output_variant='primary'),
    CookingTarget('cook_wild_pie', 'WILD_PIE', 'Cook raw wild pie', 'pies', 'RAW_WILD_PIE', 7206, 'Raw wild pie', 'WILD_PIE', 7208, 'Wild pie', 'BURNT_PIE', 2329, 'Burnt pie', 85, 240.0, 1, 222, output_variant='primary'),
    CookingTarget('cook_summer_pie', 'SUMMER_PIE', 'Cook raw summer pie', 'pies', 'RAW_SUMMER_PIE', 7216, 'Raw summer pie', 'SUMMER_PIE', 7218, 'Summer pie', 'BURNT_PIE', 2329, 'Burnt pie', 95, 260.0, 1, 212, output_variant='primary'),
    CookingTarget('cook_stew', 'STEW', 'Cook uncooked stew', 'stews', 'UNCOOKED_STEW', 2001, 'Uncooked stew', 'STEW', 2003, 'Stew', 'BURNT_STEW', 2005, 'Burnt stew', 25, 117.0, 68, 392, output_variant='primary'),
    CookingTarget('cook_curry', 'CURRY', 'Cook uncooked curry', 'stews', 'UNCOOKED_CURRY', 2009, 'Uncooked curry', 'CURRY', 2011, 'Curry', 'BURNT_CURRY', 2013, 'Burnt curry', 25, 117.0, 68, 392, output_variant='primary'),
    CookingTarget('cook_baked_potato', 'BAKED_POTATO', 'Cook potato', 'vegetables', 'POTATO', 1942, 'Potato', 'BAKED_POTATO', 6701, 'Baked potato', 'BURNT_POTATO', 6699, 'Burnt potato', 7, 15.0, 108, 472, output_variant='primary'),
    CookingTarget('cook_scrambled_egg', 'SCRAMBLED_EGG', 'Cook uncooked egg', 'vegetables', 'UNCOOKED_EGG', 7076, 'Uncooked egg', 'SCRAMBLED_EGG', 7078, 'Scrambled egg', 'BURNT_EGG', 7090, 'Burnt egg', 13, 50.0, 90, 438, output_variant='primary'),
    CookingTarget('cook_cooked_sweetcorn', 'COOKED_SWEETCORN', 'Cook sweetcorn', 'vegetables', 'SWEETCORN', 5986, 'Sweetcorn', 'COOKED_SWEETCORN', 5988, 'Cooked sweetcorn', 'BURNT_SWEETCORN', 5990, 'Burnt sweetcorn', 28, 104.0, 78, 412, output_variant='primary'),
    CookingTarget('cook_fried_onions', 'FRIED_ONIONS', 'Cook chopped onion', 'vegetables', 'CHOPPED_ONION', 1871, 'Chopped onion', 'FRIED_ONIONS', 7084, 'Fried onions', 'BURNT_ONION', 7092, 'Burnt onion', 42, 60.0, 36, 322, output_variant='primary'),
    CookingTarget('cook_fried_mushrooms', 'FRIED_MUSHROOMS', 'Cook sliced mushrooms', 'vegetables', 'SLICED_MUSHROOMS', 7080, 'Sliced mushrooms', 'FRIED_MUSHROOMS', 7082, 'Fried mushrooms', 'BURNT_MUSHROOM', 7094, 'Burnt mushroom', 46, 60.0, 16, 282, output_variant='primary'),
    CookingTarget('cook_plain_pizza', 'PLAIN_PIZZA', 'Cook uncooked pizza', 'pizza', 'UNCOOKED_PIZZA', 2287, 'Uncooked pizza', 'PLAIN_PIZZA', 2289, 'Plain pizza', 'BURNT_PIZZA', 2305, 'Burnt pizza', 35, 143.0, 48, 352, output_variant='primary'),
    CookingTarget('cook_rabbit', 'RABBIT', 'Cook raw rabbit', 'meat', 'RAW_RABBIT', 3226, 'Raw rabbit', 'COOKED_RABBIT', 3228, 'Cooked rabbit', 'BURNT_RABBIT', 7222, 'Burnt rabbit', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('cook_chicken', 'CHICKEN', 'Cook raw chicken', 'meat', 'RAW_CHICKEN', 2138, 'Raw chicken', 'COOKED_CHICKEN', 2140, 'Cooked chicken', 'BURNT_CHICKEN', 2144, 'Burnt chicken', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('cook_beef', 'BEEF', 'Cook raw beef', 'meat', 'RAW_BEEF', 2132, 'Raw beef', 'COOKED_MEAT', 2142, 'Cooked meat', 'BURNT_MEAT', 2146, 'Burnt meat', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('render_beef_sinew', 'BEEF', 'Render beef sinew', 'meat', 'RAW_BEEF', 2132, 'Raw beef', 'SINEW', 9436, 'Sinew', 'BURNT_MEAT', 2146, 'Burnt meat', 1, 30.0, 128, 512, output_variant='secondary'),
    CookingTarget('cook_bear_meat', 'BEAR', 'Cook raw bear meat', 'meat', 'RAW_BEAR_MEAT', 2136, 'Raw bear meat', 'COOKED_MEAT', 2142, 'Cooked meat', 'BURNT_MEAT', 2146, 'Burnt meat', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('render_bear_sinew', 'BEAR', 'Render bear sinew', 'meat', 'RAW_BEAR_MEAT', 2136, 'Raw bear meat', 'SINEW', 9436, 'Sinew', 'BURNT_MEAT', 2146, 'Burnt meat', 1, 30.0, 128, 512, output_variant='secondary'),
    CookingTarget('cook_rat', 'RAT', 'Cook raw rat meat', 'meat', 'RAW_RAT_MEAT', 2134, 'Raw rat meat', 'COOKED_MEAT', 2142, 'Cooked meat', 'BURNT_MEAT', 2146, 'Burnt meat', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('cook_ugthanki', 'UGTHANKI', 'Cook raw ugthanki meat', 'meat', 'RAW_UGTHANKI_MEAT', 1859, 'Raw ugthanki meat', 'UGTHANKI_MEAT', 1861, 'Ugthanki meat', 'BURNT_MEAT', 2146, 'Burnt meat', 1, 40.0, 30, 253, output_variant='primary'),
    CookingTarget('cook_yak', 'YAK', 'Cook raw yak meat', 'meat', 'RAW_YAK_MEAT', 10816, 'Raw yak meat', 'COOKED_MEAT', 2142, 'Cooked meat', 'BURNT_MEAT', 2146, 'Burnt meat', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('gut_leaping_trout', 'LEAPING_TROUT', 'Gut leaping trout', 'fish', 'LEAPING_TROUT', 11328, 'Leaping trout', 'ROE', 11324, 'Roe', '', 0, '', 1, 10.0, 0, 0, source=GUT_FISH_SOURCE_PATH, runtime_source=GUT_FISH_SOURCE_PATH, source_success_formula={'base': 1.0, 'level_multiplier': 65.0, 'level_range': 98.0, 'cap': 99.0, 'divisor': 150.0}, source_no_level_requirement=True, byproduct_item='Fish offcuts', byproduct_chance=0.5, failure_kind='gut'),
    CookingTarget('gut_leaping_salmon', 'LEAPING_SALMON', 'Gut leaping salmon', 'fish', 'LEAPING_SALMON', 11330, 'Leaping salmon', 'ROE', 11324, 'Roe', '', 0, '', 1, 10.0, 0, 0, source=GUT_FISH_SOURCE_PATH, runtime_source=GUT_FISH_SOURCE_PATH, source_success_formula={'base': 1.25, 'level_multiplier': 98.75, 'level_range': 79.0, 'cap': 100.0, 'divisor': 100.0}, source_no_level_requirement=True, byproduct_item='Fish offcuts', byproduct_chance=0.75, failure_kind='gut'),
    CookingTarget('gut_leaping_sturgeon', 'LEAPING_STURGEON', 'Gut leaping sturgeon', 'fish', 'LEAPING_STURGEON', 11332, 'Leaping sturgeon', 'CAVIAR', 11326, 'Caviar', '', 0, '', 1, 15.0, 0, 0, source=GUT_FISH_SOURCE_PATH, runtime_source=GUT_FISH_SOURCE_PATH, source_success_formula={'base': 1.25, 'level_multiplier': 98.75, 'level_range': 79.0, 'cap': 100.0, 'divisor': 100.0}, source_no_level_requirement=True, byproduct_item='Fish offcuts', byproduct_chance=5.0 / 6.0, failure_kind='gut'),
    CookingTarget('burn_seaweed', 'SEAWEED', 'Burn seaweed', 'materials', 'SEAWEED', 401, 'Seaweed', 'SODA_ASH', 1781, 'Soda ash', '', 0, '', 1, 1.0, 0, 0, source=SEAWEED_COOKING_SOURCE_PATH, runtime_source=SEAWEED_COOKING_SOURCE_PATH, source_always_succeeds=True, source_no_level_requirement=True, failure_kind='burn'),
)

COOKING_TARGETS_BY_ID: Dict[str, CookingTarget] = {target.id: target for target in COOKING_TARGETS}
DEFAULT_COOKING_TARGET = "cook_shrimps"


COOKING_PREP_ACTIVITIES: Tuple[CookingPrepActivity, ...] = (
    CookingPrepActivity("gather_grain", "Gather grain", {}, "Grain", group="gathering", source=WHEAT_PICK_SOURCE_PATH),
    CookingPrepActivity("grind_grain_to_flour", "Grind grain to flour", {"Grain": 1, "Empty pot": 1}, "Pot of flour", source=MILL_SOURCE_PATH),
    CookingPrepActivity(
        "wet_flour_to_bread_dough",
        "Make bread dough",
        _FLOUR_WATER_REQUIREMENTS,
        "Bread dough",
        byproducts=_FLOUR_WATER_BYPRODUCTS,
        source=WATER_SOURCE_PATH,
    ),
    CookingPrepActivity(
        "wet_flour_to_pitta_dough",
        "Make pitta dough",
        _FLOUR_WATER_REQUIREMENTS,
        "Pitta dough",
        byproducts=_FLOUR_WATER_BYPRODUCTS,
        source=WATER_SOURCE_PATH,
    ),
    CookingPrepActivity(
        "wet_flour_to_pastry_dough",
        "Make pastry dough",
        _FLOUR_WATER_REQUIREMENTS,
        "Pastry dough",
        byproducts=_FLOUR_WATER_BYPRODUCTS,
        source=WATER_SOURCE_PATH,
    ),
    CookingPrepActivity(
        "wet_flour_to_pizza_base",
        "Make pizza base",
        _FLOUR_WATER_REQUIREMENTS,
        "Pizza base",
        byproducts=_FLOUR_WATER_BYPRODUCTS,
        source=WATER_SOURCE_PATH,
    ),
    CookingPrepActivity("make_pie_shell", "Make pie shell", {"Pastry dough": 1, "Pie dish": 1}, "Pie shell"),
    CookingPrepActivity("fill_bowl_of_water", "Fill bowl with water", {"Bowl": 1}, "Bowl of water", source=WATER_SOURCE_PATH),
    CookingPrepActivity("draw_bucket_of_water", "Draw bucket of water", {"Bucket": 1}, "Bucket of water", source=WATER_SOURCE_PATH),
    CookingPrepActivity("prepare_uncooked_egg", "Prepare uncooked egg", {"Egg": 1, "Bowl": 1}, "Uncooked egg"),
    CookingPrepActivity("chop_onion", "Chop onion", {"Onion": 1}, "Chopped onion"),
    CookingPrepActivity("slice_mushrooms", "Slice mushrooms", {"Mushrooms": 1}, "Sliced mushrooms"),
    CookingPrepActivity("assemble_redberry_pie", "Assemble redberry pie", {"Pie shell": 1, "Redberries": 1}, "Uncooked berry pie"),
    CookingPrepActivity("assemble_meat_pie", "Assemble meat pie", {"Pie shell": 1, "Cooked meat": 1}, "Uncooked meat pie"),
    CookingPrepActivity(
        "assemble_mud_pie",
        "Assemble mud pie",
        {"Pie shell": 1, "Compost": 1, "Bucket of water": 1, "Clay": 1},
        "Raw mud pie",
        byproducts={"Bucket": 1},
    ),
    CookingPrepActivity("assemble_apple_pie", "Assemble apple pie", {"Pie shell": 1, "Cooking apple": 1}, "Uncooked apple pie"),
    CookingPrepActivity("assemble_garden_pie", "Assemble garden pie", {"Pie shell": 1, "Tomato": 1, "Onion": 1, "Cabbage": 1}, "Raw garden pie"),
    CookingPrepActivity("assemble_fish_pie", "Assemble fish pie", {"Pie shell": 1, "Trout": 1, "Cod": 1, "Potato": 1}, "Raw fish pie"),
    CookingPrepActivity("assemble_admiral_pie", "Assemble admiral pie", {"Pie shell": 1, "Salmon": 1, "Tuna": 1, "Potato": 1}, "Raw admiral pie"),
    CookingPrepActivity("assemble_wild_pie", "Assemble wild pie", {"Pie shell": 1, "Raw bear meat": 1, "Raw chompy": 1, "Raw rabbit": 1}, "Raw wild pie"),
    CookingPrepActivity("assemble_summer_pie", "Assemble summer pie", {"Pie shell": 1, "Strawberry": 1, "Watermelon": 1, "Cooking apple": 1}, "Raw summer pie"),
    CookingPrepActivity("assemble_uncooked_stew", "Assemble uncooked stew", {"Bowl of water": 1, "Potato": 1, "Cooked meat": 1}, "Uncooked stew"),
    CookingPrepActivity("assemble_uncooked_curry", "Assemble uncooked curry", {"Uncooked stew": 1, "Spice": 1}, "Uncooked curry"),
    CookingPrepActivity("assemble_uncooked_pizza", "Assemble uncooked pizza", {"Pizza base": 1, "Tomato": 1, "Cheese": 1}, "Uncooked pizza"),
    # 2026-07-07: the shop-covered gather/scavenge bridges (Potato, Onion,
    # Egg, Redberries, Cooking apple, Tomato, Cheese, Cabbage, Sweetcorn,
    # Spice, Raw chicken/beef/bear/rat/rabbit/yak meat, Thin snail) and
    # buy_bucket were retired: every output is live NPC shop stock at cache
    # prices, and combat drops/Fishing remain the free food routes. Only
    # bridges with no shop route stay below.
    CookingPrepActivity("gather_mushrooms", "Gather mushrooms", {}, "Mushrooms", group="gathering"),
    CookingPrepActivity("scavenge_raw_ugthanki_meat", "Scavenge raw ugthanki meat", {}, "Raw ugthanki meat", group="gathering"),
    CookingPrepActivity("gather_lean_snails", "Gather lean snails", {}, "Lean snail", group="gathering"),
    CookingPrepActivity("gather_fat_snails", "Gather fat snails", {}, "Fat snail", group="gathering"),
)


SOURCE_ITEM_DATA: Dict[str, Tuple[int, bool]] = {
    "Grain": (1947, True),
    "Empty pot": (1931, True),
    "Pot of flour": (1933, True),
    "Bread dough": (2307, True),
    "Pitta dough": (1863, True),
    "Pastry dough": (1953, True),
    "Pizza base": (2283, True),
    "Pie dish": (2313, True),
    "Pie shell": (2315, True),
    "Bowl": (1923, True),
    "Bowl of water": (1921, True),
    "Bucket": (1925, True),
    "Bucket of water": (1929, True),
    "Potato": (1942, True),
    "Egg": (1944, True),
    "Uncooked egg": (7076, True),
    "Onion": (1957, True),
    "Chopped onion": (1871, True),
    "Mushrooms": (10968, False),
    "Sliced mushrooms": (7080, True),
    "Redberries": (1951, True),
    "Cooking apple": (1955, True),
    "Tomato": (1982, True),
    "Cheese": (1985, True),
    "Cabbage": (1965, True),
    "Sweetcorn": (5986, True),
    "Spice": (2007, True),
    "Compost": (6032, True),
    "Strawberry": (5504, True),
    "Watermelon": (5982, True),
    "Raw chompy": (2876, True),
    "Uncooked meat pie": (2319, True),
    "Uncooked apple pie": (2317, True),
    "Uncooked berry pie": (2321, True),
    "Raw mud pie": (7168, True),
    "Raw garden pie": (7176, True),
    "Raw fish pie": (7186, True),
    "Raw admiral pie": (7196, True),
    "Raw wild pie": (7206, True),
    "Raw summer pie": (7216, True),
    "Uncooked stew": (2001, True),
    "Uncooked curry": (2009, True),
    "Uncooked pizza": (2287, True),
    "Raw crayfish": (13435, False),
    "Crayfish": (13433, False),
    "Burnt crayfish": (13437, False),
}

for _target in COOKING_TARGETS:
    if _target.source in (GUT_FISH_SOURCE_PATH, SEAWEED_COOKING_SOURCE_PATH):
        continue
    SOURCE_ITEM_DATA.setdefault(_target.raw_item, (_target.raw_item_id, True))
    SOURCE_ITEM_DATA.setdefault(_target.cooked_item, (_target.cooked_item_id, True))
    if _target.burnt_item:
        SOURCE_ITEM_DATA.setdefault(_target.burnt_item, (_target.burnt_item_id, False))


_MATERIAL_CATEGORIES = {
    "Bucket": "crafted",
    "Bucket of water": "material",
    "Bowl of water": "material",
    "Empty pot": "crafted",
    "Bowl": "crafted",
    "Pie dish": "crafted",
    "Clay": "ore",
}


def cooking_targets_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        target.id: {
            "display_name": target.display_name,
            "family": target.family,
            "level": target.level,
            "exp": target.base_exp,
            "requirements": {target.raw_item: 1},
            "raw_item": target.raw_item,
            "raw_item_id": target.raw_item_id,
            "cooked_item": target.cooked_item,
            "cooked_item_id": target.cooked_item_id,
            "output_item": target.cooked_item,
            "output_qty": 1,
            "burnt_item": target.burnt_item,
            "burnt_item_id": target.burnt_item_id,
            "low_chance": target.low_chance,
            "high_chance": target.high_chance,
            "source": target.source,
            "runtime_source": target.runtime_source,
            "source_enum": target.source_enum,
            "output_variant": target.output_variant,
            "status": target.status,
            **({"source_success_formula": dict(target.source_success_formula)} if target.source_success_formula else {}),
            **({"source_always_succeeds": True} if target.source_always_succeeds else {}),
            **({"source_no_level_requirement": True} if target.source_no_level_requirement else {}),
            **({"byproduct_item": target.byproduct_item, "byproduct_chance": target.byproduct_chance} if target.byproduct_item else {}),
            **({"failure_kind": target.failure_kind} if target.failure_kind != "burn" else {}),
        }
        for target in COOKING_TARGETS
    }


def cooking_output_items() -> Tuple[str, ...]:
    return tuple(dict.fromkeys(target.cooked_item for target in COOKING_TARGETS))


def cooking_burnt_items() -> Tuple[str, ...]:
    return tuple(dict.fromkeys(target.burnt_item for target in COOKING_TARGETS if target.burnt_item))


def cooking_raw_items() -> Tuple[str, ...]:
    return tuple(dict.fromkeys(target.raw_item for target in COOKING_TARGETS))


def _cooking_prep_outputs(activity: CookingPrepActivity) -> Dict[str, int]:
    outputs = {activity.output_item: activity.output_qty}
    outputs.update(dict(activity.byproducts))
    return outputs


def cooking_prep_activities_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        activity.id: {
            "display_name": activity.display_name,
            "requirements": dict(activity.requirements),
            "output_item": activity.output_item,
            "output_qty": activity.output_qty,
            "outputs": _cooking_prep_outputs(activity),
            "batch_size": activity.batch_size,
            "group": activity.group,
            "source": activity.source,
        }
        for activity in COOKING_PREP_ACTIVITIES
    }


def cooking_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    item_names = set(SOURCE_ITEM_DATA)
    for activity in COOKING_PREP_ACTIVITIES:
        item_names.add(activity.output_item)
        item_names.update(activity.requirements)
        item_names.update(activity.byproducts)

    result: Dict[str, Dict[str, object]] = {}
    burnt_items = set(cooking_burnt_items())
    for item_name in sorted(item_names):
        item_id, source_tradeable = SOURCE_ITEM_DATA.get(item_name, (0, True))
        category = _MATERIAL_CATEGORIES.get(item_name, "food")
        result[item_name] = {
            "category": category,
            "level": 1,
            "exp": 0.0,
            "source": ITEMS_YML_SOURCE_PATH if item_id else COOKING_PREP_BRIDGE_SOURCE,
            "item_id": item_id,
            "tradeable": False if item_name in burnt_items else bool(source_tradeable),
        }
    return result
