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
GNOME_COOKING_SOURCE = (
    "RuneScape Wiki Gnome cooking oldid=6438943 (2012-10-18T22:02:41Z) ingredient "
    "tables; Cooking oldid=6548144 (2012-11-11T16:17:12Z) level/XP table; "
    "memory-bank/source-audits/gnome-restaurant-harvest-2026-07-28.md"
)
SPIDER_COOKING_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "src/main/java/com/rs/game/content/skills/cooking/Cooking.java"
)
SPIDER_RECIPE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "src/main/java/com/rs/game/content/skills/cooking/CookingCombos.java"
)
# The period built each dish over several clicks, adding the first ingredients to
# the tin, tray or mould and the rest to the part-baked dish. One AnkiScape action
# consumes both stages and awards the sourced grand-total XP; the intermediate
# `Half made`/`Unfinished` items are deferred depth. The container comes back out
# of a finished dish, exactly as `Tangled toads' legs` oldid 5850397 states for the
# gnomebowl mould; a burnt dish loses it, which follows from the shared burn model
# rather than from any source.
CHEESE_WHEEL_WIKI_SOURCE = "https://runescape.wiki/w/Cheese_wheel?oldid=6288901"
CHEESE_WHEEL_TALK_SOURCE = "https://runescape.wiki/w/Talk:Cheese_wheel?oldid=5942573"
DAIRY_CHURN_WIKI_SOURCE = "https://runescape.wiki/w/Dairy_churn?oldid=6474695"
LAVA_EEL_WIKI_SOURCE = "https://runescape.wiki/w/Lava_eel?oldid=5850408"
LAVA_EEL_DARKAN_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "src/main/java/com/rs/game/content/skills/cooking/Cooking.java"
)
TIGER_SHARK_WIKI_SOURCE = (
    "RuneScape Wiki Tiger shark oldid=6448339 "
    "(2012-10-21T04:48:57Z); Raw tiger shark oldid=5992445 "
    "(2012-07-26T02:12:01Z)"
)
BREWING_SOURCE = (
    "RuneScape Wiki Brewing oldid=6447660 (2012-10-20T22:19:26Z); "
    "The Stuff oldid=6447071 (2012-10-20T15:26:18Z); OpenRS2 rev-742"
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
    cooking_gauntlet_no_burn_level: int = 0
    byproduct_item: str = ""
    byproduct_chance: float = 0.0
    byproducts: Mapping[str, int] = ()
    output_quantity_model: str = ""
    xp_per_output: float = 0.0
    failure_kind: str = "burn"
    output_qty: int = 1
    alternate_output_item: str = ""
    alternate_output_qty: int = 0
    outcome_kind: str = ""
    # Gnome cooking assembles one dish from several ingredients in one action, the
    # way the pie and pizza prep bridges assemble theirs.
    extra_requirements: Mapping[str, int] = ()


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


# No recovered source gives a burn rate for any gnome dish, and both emulator
# lineages omit gnome cooking entirely. Each family borrows the 2011Scape burn
# endpoints of the ordinary Cooking row nearest its lowest level requirement:
# Redberry pie at 10 for crunchies, Uncooked stew at 25 for battas, Uncooked apple
# pie at 30 for gnomebowls.
# PLACEHOLDER(gnome_restaurant.gnome_food_burn_endpoints): authentic gnome-dish burn endpoints
_GNOME_CRUNCHY_BURN = (98, 452)
_GNOME_BATTA_BURN = (68, 392)
_GNOME_BOWL_BURN = (58, 372)
# PLACEHOLDER(cooking.spider_on_stick_burn_endpoints): Darkan gives the exact
# level-16 recipe, 80 XP and level-48 no-burn point, but not the pre-EOC roll
# endpoints. The adjacent level-15 trout row has the same one-level burn curve.
_SPIDER_ON_STICK_BURN = (88, 432)
# PLACEHOLDER(cooking.tiger_shark_burn_endpoints): authentic Tiger-shark burn endpoints
# The cutoff article says it can burn at every level but gives no probability.
# Borrow the level-93 Rocktail's 2011Scape endpoints until a period roll ships.
_TIGER_SHARK_BURN = (1, 222)
# PLACEHOLDER(cooking.dwarven_stout_mature_chance): the exact pre-EOC hidden
# maturity roll is not recoverable from period primary evidence. Darkan's
# reconstruction supplies 10% naturally and 75% with The stuff until it is.
_DWARVEN_STOUT_MATURE_CHANCE = 0.10
_DWARVEN_STOUT_STUFF_MATURE_CHANCE = 0.75

COOKING_TARGETS: Tuple[CookingTarget, ...] = (
    CookingTarget('cook_shrimps', 'SHRIMPS', 'Cook raw shrimps', 'fish', 'RAW_SHRIMPS', 317, 'Raw shrimps', 'SHRIMPS', 315, 'Shrimps', 'BURNT_SHRIMP', 7954, 'Burnt shrimp', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('cook_anchovies', 'ANCHOVIES', 'Cook raw anchovies', 'fish', 'RAW_ANCHOVIES', 321, 'Raw anchovies', 'ANCHOVIES', 319, 'Anchovies', 'BURNT_FISH', 323, 'Burnt fish', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('cook_crayfish', 'CRAYFISH', 'Cook raw crayfish', 'fish', 'RAW_CRAYFISH', 13435, 'Raw crayfish', 'CRAYFISH', 13433, 'Crayfish', 'BURNT_CRAYFISH', 13437, 'Burnt crayfish', 1, 30.0, 128, 512, output_variant='primary'),
    CookingTarget('cook_sardine', 'SARDINE', 'Cook raw sardine', 'fish', 'RAW_SARDINE', 327, 'Raw sardine', 'SARDINE', 325, 'Sardine', 'BURNT_FISH_369', 369, 'Burnt fish', 1, 40.0, 118, 492, output_variant='primary'),
    CookingTarget('cook_herring', 'HERRING', 'Cook raw herring', 'fish', 'RAW_HERRING', 345, 'Raw herring', 'HERRING', 347, 'Herring', 'BURNT_FISH_357', 357, 'Burnt fish', 5, 50.0, 108, 472, output_variant='primary'),
    CookingTarget('cook_mackerel', 'MACKEREL', 'Cook raw mackerel', 'fish', 'RAW_MACKEREL', 353, 'Raw mackerel', 'MACKEREL', 355, 'Mackerel', 'BURNT_FISH_357', 357, 'Burnt fish', 10, 60.0, 98, 452, output_variant='primary'),
    CookingTarget('cook_trout', 'TROUT', 'Cook raw trout', 'fish', 'RAW_TROUT', 335, 'Raw trout', 'TROUT', 333, 'Trout', 'BURNT_FISH_343', 343, 'Burnt fish', 15, 70.0, 88, 432, output_variant='primary', cooking_gauntlet_no_burn_level=50),
    CookingTarget('cook_spider_on_a_stick', 'RAW_SPIDER_ON_STICK', 'Cook a spider on a stick', 'meat', 'RAW_SPIDER_ON_STICK', 6293, 'Raw spider on stick', 'SPIDER_ON_STICK_6297', 6297, 'Spider on stick', 'BURNT_SPIDER', 6301, 'Burnt spider', 16, 80.0, *_SPIDER_ON_STICK_BURN, output_variant='primary', source=SPIDER_COOKING_SOURCE_PATH, runtime_source=SPIDER_COOKING_SOURCE_PATH),
    CookingTarget('cook_cod', 'COD', 'Cook raw cod', 'fish', 'RAW_COD', 341, 'Raw cod', 'COD', 339, 'Cod', 'BURNT_FISH_343', 343, 'Burnt fish', 18, 75.0, 88, 432, output_variant='primary'),
    CookingTarget('cook_pike', 'PIKE', 'Cook raw pike', 'fish', 'RAW_PIKE', 349, 'Raw pike', 'PIKE', 351, 'Pike', 'BURNT_FISH_343', 343, 'Burnt fish', 20, 80.0, 78, 412, output_variant='primary'),
    CookingTarget('cook_salmon', 'SALMON', 'Cook raw salmon', 'fish', 'RAW_SALMON', 331, 'Raw salmon', 'SALMON', 329, 'Salmon', 'BURNT_FISH_343', 343, 'Burnt fish', 25, 90.0, 68, 392, output_variant='primary'),
    CookingTarget('cook_tuna', 'TUNA', 'Cook raw tuna', 'fish', 'RAW_TUNA', 359, 'Raw tuna', 'TUNA', 361, 'Tuna', 'BURNT_FISH_367', 367, 'Burnt fish', 30, 100.0, 58, 372, output_variant='primary', cooking_gauntlet_no_burn_level=63),
    CookingTarget('cook_lobster', 'LOBSTER', 'Cook raw lobster', 'fish', 'RAW_LOBSTER', 377, 'Raw lobster', 'LOBSTER', 379, 'Lobster', 'BURNT_LOBSTER', 381, 'Burnt lobster', 40, 120.0, 38, 332, output_variant='primary', cooking_gauntlet_no_burn_level=68),
    CookingTarget('cook_bass', 'BASS', 'Cook raw bass', 'fish', 'RAW_BASS', 363, 'Raw bass', 'BASS', 365, 'Bass', 'BURNT_FISH_367', 367, 'Burnt fish', 43, 130.0, 33, 312, output_variant='primary'),
    CookingTarget('cook_swordfish', 'SWORDFISH', 'Cook raw swordfish', 'fish', 'RAW_SWORDFISH', 371, 'Raw swordfish', 'SWORDFISH', 373, 'Swordfish', 'BURNT_SWORDFISH', 375, 'Burnt swordfish', 45, 140.0, 18, 292, output_variant='primary', cooking_gauntlet_no_burn_level=81),
    CookingTarget('cook_monkfish', 'MONKFISH', 'Cook raw monkfish', 'fish', 'RAW_MONKFISH', 7944, 'Raw monkfish', 'MONKFISH', 7946, 'Monkfish', 'BURNT_MONKFISH', 7948, 'Burnt monkfish', 62, 150.0, 13, 280, output_variant='primary', cooking_gauntlet_no_burn_level=87),
    CookingTarget('cook_shark', 'SHARK', 'Cook raw shark', 'fish', 'RAW_SHARK', 383, 'Raw shark', 'SHARK', 385, 'Shark', 'BURNT_SHARK', 387, 'Burnt shark', 80, 210.0, 1, 232, output_variant='primary', cooking_gauntlet_no_burn_level=94),
    CookingTarget('cook_sea_turtle', 'SEA_TURTLE', 'Cook raw sea turtle', 'fish', 'RAW_SEA_TURTLE', 395, 'Raw sea turtle', 'SEA_TURTLE', 397, 'Sea turtle', 'BURNT_SEA_TURTLE', 399, 'Burnt sea turtle', 82, 211.3, 1, 222, output_variant='primary'),
    CookingTarget('cook_manta_ray', 'MANTA_RAY', 'Cook raw manta ray', 'fish', 'RAW_MANTA_RAY', 389, 'Raw manta ray', 'MANTA_RAY', 391, 'Manta ray', 'BURNT_MANTA_RAY', 393, 'Burnt manta ray', 91, 216.3, 1, 222, output_variant='primary'),
    CookingTarget('cook_cavefish', 'CAVEFISH', 'Cook raw cavefish', 'fish', 'RAW_CAVEFISH', 15264, 'Raw cavefish', 'CAVEFISH', 15266, 'Cavefish', 'BURNT_CAVEFISH', 15268, 'Burnt cavefish', 88, 214.0, 1, 232, output_variant='primary', cooking_gauntlet_no_burn_level=94),
    CookingTarget('cook_rocktail', 'ROCKTAIL', 'Cook raw rocktail', 'fish', 'RAW_ROCKTAIL', 15270, 'Raw rocktail', 'ROCKTAIL', 15272, 'Rocktail', 'BURNT_ROCKTAIL', 15274, 'Burnt rocktail', 93, 225.0, 1, 222, output_variant='primary', cooking_gauntlet_no_burn_level=94),
    CookingTarget('cook_tiger_shark', 'TIGER_SHARK', 'Cook raw tiger shark', 'fish', 'RAW_TIGER_SHARK', 21520, 'Raw tiger shark', 'TIGER_SHARK', 21521, 'Tiger shark', 'BURNT_TIGER_SHARK', 21522, 'Burnt tiger shark', 95, 230.0, *_TIGER_SHARK_BURN, output_variant='primary', source=TIGER_SHARK_WIKI_SOURCE, runtime_source=TIGER_SHARK_WIKI_SOURCE),
    CookingTarget('cook_cave_eel', 'CAVE_EEL', 'Cook raw cave eel', 'eels', 'RAW_CAVE_EEL', 5001, 'Raw cave eel', 'CAVE_EEL', 5003, 'Cave eel', 'BURNT_CAVE_EEL', 5002, 'Burnt cave eel', 38, 115.0, 38, 332, output_variant='primary'),
    CookingTarget('cook_slimy_eel', 'SLIMY_EEL', 'Cook slimy eel', 'eels', 'SLIMY_EEL', 3379, 'Slimy eel', 'COOKED_SLIMY_EEL', 3381, 'Cooked slimy eel', 'BURNT_EEL', 3383, 'Burnt eel', 28, 95.0, 63, 382, output_variant='primary'),
    CookingTarget('cook_lava_eel', 'RAW_LAVA_EEL', 'Cook raw lava eel', 'eels', 'RAW_LAVA_EEL', 2148, 'Raw lava eel', 'LAVA_EEL', 2149, 'Lava eel', '', 0, '', 53, 30.0, 0, 0, output_variant='primary', source=LAVA_EEL_WIKI_SOURCE, runtime_source=LAVA_EEL_DARKAN_SOURCE, source_always_succeeds=True),
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
    CookingTarget('churn_milk_cheese_wheel', 'CHEESE_WHEEL', 'Churn milk into a cheese wheel', 'dairy', 'BUCKET_OF_MILK', 1927, 'Bucket of milk', 'CHEESE_WHEEL', 18789, 'Cheese wheel', '', 0, '', 48, 40.5, 0, 0, source=CHEESE_WHEEL_WIKI_SOURCE, runtime_source=DAIRY_CHURN_WIKI_SOURCE, source_always_succeeds=True, byproducts={'Bucket': 1}, failure_kind='churn'),
    CookingTarget('churn_butter_cheese_wheel', 'CHEESE_WHEEL', 'Churn butter into a cheese wheel', 'dairy', 'PAT_OF_BUTTER', 6697, 'Pat of butter', 'CHEESE_WHEEL', 18789, 'Cheese wheel', '', 0, '', 48, 40.5, 0, 0, source=CHEESE_WHEEL_WIKI_SOURCE, runtime_source=DAIRY_CHURN_WIKI_SOURCE, source_always_succeeds=True, failure_kind='churn'),
    CookingTarget('slice_cheese_wheel', 'CHEESE_WHEEL_SLICED', 'Slice-all cheese wheel', 'dairy', 'CHEESE_WHEEL', 18789, 'Cheese wheel', 'CHEESE', 1985, 'Cheese', '', 0, '', 48, 0.0, 0, 0, source=CHEESE_WHEEL_WIKI_SOURCE, runtime_source=CHEESE_WHEEL_TALK_SOURCE, source_always_succeeds=True, output_quantity_model='cheese_wheel_slices', xp_per_output=4.0, failure_kind='slice'),
    # Gnome cooking. Levels, XP and ingredient lists are exact; the burn endpoints
    # are the registered placeholder _GNOME_BURN_* below.
    CookingTarget('bake_toad_crunchies', 'TOAD_CRUNCHIES', 'Bake toad crunchies', 'gnome_crunchies', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'TOAD_CRUNCHIES', 2217, 'Toad crunchies', 'BURNT_CRUNCHIES', 2199, 'Burnt crunchies', 10, 100.0, *_GNOME_CRUNCHY_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Crunchy tray': 1, "Toad's legs": 2, 'Gnome spice': 1, 'Equa leaves': 1}, byproducts={'Crunchy tray': 1}),
    CookingTarget('bake_spicy_crunchies', 'SPICY_CRUNCHIES', 'Bake spicy crunchies', 'gnome_crunchies', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'SPICY_CRUNCHIES', 2213, 'Spicy crunchies', 'BURNT_CRUNCHIES', 2199, 'Burnt crunchies', 12, 100.0, *_GNOME_CRUNCHY_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Crunchy tray': 1, 'Equa leaves': 2, 'Gnome spice': 2}, byproducts={'Crunchy tray': 1}),
    CookingTarget('bake_worm_crunchies', 'WORM_CRUNCHIES', 'Bake worm crunchies', 'gnome_crunchies', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'WORM_CRUNCHIES', 2205, 'Worm crunchies', 'BURNT_CRUNCHIES', 2199, 'Burnt crunchies', 14, 100.0, *_GNOME_CRUNCHY_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Crunchy tray': 1, 'King worm': 2, 'Gnome spice': 2, 'Equa leaves': 1}, byproducts={'Crunchy tray': 1}),
    CookingTarget('bake_chocchip_crunchies', 'CHOCCHIP_CRUNCHIES', 'Bake chocchip crunchies', 'gnome_crunchies', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'CHOCCHIP_CRUNCHIES', 2209, 'Chocchip crunchies', 'BURNT_CRUNCHIES', 2199, 'Burnt crunchies', 16, 100.0, *_GNOME_CRUNCHY_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Crunchy tray': 1, 'Chocolate bar': 2, 'Gnome spice': 1, 'Chocolate dust': 1}, byproducts={'Crunchy tray': 1}),
    CookingTarget('bake_fruit_batta', 'FRUIT_BATTA', 'Bake a fruit batta', 'gnome_battas', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'FRUIT_BATTA', 2277, 'Fruit batta', 'BURNT_BATTA', 2247, 'Burnt batta', 25, 150.0, *_GNOME_BATTA_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Batta tin': 1, 'Equa leaves': 4, 'Lime chunks': 1, 'Orange chunks': 1, 'Pineapple chunks': 1, 'Gnome spice': 1}, byproducts={'Batta tin': 1}),
    CookingTarget('bake_toad_batta', 'TOAD_BATTA', 'Bake a toad batta', 'gnome_battas', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'TOAD_BATTA', 2255, 'Toad batta', 'BURNT_BATTA', 2247, 'Burnt batta', 26, 152.0, *_GNOME_BATTA_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Batta tin': 1, 'Equa leaves': 1, 'Gnome spice': 1, 'Cheese': 1, "Toad's legs": 1}, byproducts={'Batta tin': 1}),
    CookingTarget('bake_worm_batta', 'WORM_BATTA', 'Bake a worm batta', 'gnome_battas', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'WORM_BATTA', 2253, 'Worm batta', 'BURNT_BATTA', 2247, 'Burnt batta', 27, 154.0, *_GNOME_BATTA_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Batta tin': 1, 'King worm': 1, 'Cheese': 1, 'Gnome spice': 1, 'Equa leaves': 1}, byproducts={'Batta tin': 1}),
    CookingTarget('bake_vegetable_batta', 'VEGETABLE_BATTA', 'Bake a vegetable batta', 'gnome_battas', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'VEGETABLE_BATTA', 2281, 'Vegetable batta', 'BURNT_BATTA', 2247, 'Burnt batta', 28, 156.0, *_GNOME_BATTA_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Batta tin': 1, 'Tomato': 2, 'Dwellberries': 1, 'Onion': 1, 'Cheese': 1, 'Cabbage': 1, 'Equa leaves': 1}, byproducts={'Batta tin': 1}),
    CookingTarget('bake_cheese_tomato_batta', 'CHEESETOM_BATTA', 'Bake a cheese and tomato batta', 'gnome_battas', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'CHEESETOM_BATTA', 2259, 'Cheese+tom batta', 'BURNT_BATTA', 2247, 'Burnt batta', 29, 158.0, *_GNOME_BATTA_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Batta tin': 1, 'Tomato': 1, 'Cheese': 1, 'Equa leaves': 1}, byproducts={'Batta tin': 1}),
    CookingTarget('bake_worm_hole', 'WORM_HOLE', 'Bake a worm hole', 'gnome_bowls', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'WORM_HOLE', 2191, 'Worm hole', 'BURNT_GNOMEBOWL', 2175, 'Burnt gnomebowl', 30, 170.0, *_GNOME_BOWL_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Gnomebowl mould': 1, 'King worm': 4, 'Onion': 2, 'Gnome spice': 1, 'Equa leaves': 1}, byproducts={'Gnomebowl mould': 1}),
    CookingTarget('bake_veg_ball', 'VEG_BALL', 'Bake a veg ball', 'gnome_bowls', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'VEG_BALL', 2195, 'Veg ball', 'BURNT_GNOMEBOWL', 2175, 'Burnt gnomebowl', 35, 175.0, *_GNOME_BOWL_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Gnomebowl mould': 1, 'Onion': 2, 'Potato': 2, 'Gnome spice': 1, 'Equa leaves': 1}, byproducts={'Gnomebowl mould': 1}),
    CookingTarget('bake_tangled_toads_legs', 'TANGLED_TOADS_LEGS', "Bake tangled toads' legs", 'gnome_bowls', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'TANGLED_TOADS_LEGS', 2187, "Tangled toads' legs", 'BURNT_GNOMEBOWL', 2175, 'Burnt gnomebowl', 40, 185.0, *_GNOME_BOWL_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Gnomebowl mould': 1, "Toad's legs": 4, 'Gnome spice': 1, 'Cheese': 2, 'Dwellberries': 1, 'Equa leaves': 2}, byproducts={'Gnomebowl mould': 1}),
    CookingTarget('bake_chocolate_bomb', 'CHOCOLATE_BOMB', 'Bake a chocolate bomb', 'gnome_bowls', 'GIANNE_DOUGH', 2171, 'Gianne dough', 'CHOCOLATE_BOMB', 2185, 'Chocolate bomb', 'BURNT_GNOMEBOWL', 2175, 'Burnt gnomebowl', 42, 190.0, *_GNOME_BOWL_BURN, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, extra_requirements={'Gnomebowl mould': 1, 'Chocolate bar': 4, 'Equa leaves': 1, 'Chocolate dust': 1, 'Pot of cream': 2}, byproducts={'Gnomebowl mould': 1}),
    # No burnt or spoiled cocktail exists anywhere in the period item set, so the
    # pour always succeeds. The shaker comes back; the glass becomes the drink.
    CookingTarget('mix_fruit_blast', 'FRUIT_BLAST', 'Mix a fruit blast', 'gnome_cocktails', 'COCKTAIL_GLASS', 2026, 'Cocktail glass', 'FRUIT_BLAST', 2084, 'Fruit blast', '', 0, '', 6, 50.0, 0, 0, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, source_always_succeeds=True, extra_requirements={'Cocktail shaker': 1, 'Pineapple': 1, 'Lemon': 1, 'Orange': 1, 'Lemon slices': 1}, byproducts={'Cocktail shaker': 1}, failure_kind='pour'),
    CookingTarget('mix_pineapple_punch', 'PINEAPPLE_PUNCH', 'Mix a pineapple punch', 'gnome_cocktails', 'COCKTAIL_GLASS', 2026, 'Cocktail glass', 'PINEAPPLE_PUNCH', 2048, 'Pineapple punch', '', 0, '', 8, 70.0, 0, 0, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, source_always_succeeds=True, extra_requirements={'Cocktail shaker': 1, 'Pineapple': 2, 'Lemon': 1, 'Orange': 1, 'Lime chunks': 1, 'Pineapple chunks': 1, 'Orange slices': 1}, byproducts={'Cocktail shaker': 1}, failure_kind='pour'),
    CookingTarget('mix_wizard_blizzard', 'WIZARD_BLIZZARD', 'Mix a wizard blizzard', 'gnome_cocktails', 'COCKTAIL_GLASS', 2026, 'Cocktail glass', 'WIZARD_BLIZZARD', 2054, 'Wizard blizzard', '', 0, '', 18, 110.0, 0, 0, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, source_always_succeeds=True, extra_requirements={'Cocktail shaker': 1, 'Vodka': 2, 'Gin': 1, 'Lime': 1, 'Lemon': 1, 'Orange': 1, 'Pineapple chunks': 1, 'Lime slices': 1}, byproducts={'Cocktail shaker': 1}, failure_kind='pour'),
    CookingTarget('mix_short_green_guy', 'SHORT_GREEN_GUY', 'Mix a short green guy', 'gnome_cocktails', 'COCKTAIL_GLASS', 2026, 'Cocktail glass', 'SHORT_GREEN_GUY', 2080, 'Short green guy', '', 0, '', 20, 120.0, 0, 0, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, source_always_succeeds=True, extra_requirements={'Cocktail shaker': 1, 'Vodka': 1, 'Lime': 3, 'Lime slices': 1, 'Equa leaves': 1}, byproducts={'Cocktail shaker': 1}, failure_kind='pour'),
    CookingTarget('mix_drunk_dragon', 'DRUNK_DRAGON', 'Mix a drunk dragon', 'gnome_cocktails', 'COCKTAIL_GLASS', 2026, 'Cocktail glass', 'DRUNK_DRAGON', 2092, 'Drunk dragon', '', 0, '', 32, 160.0, 0, 0, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, source_always_succeeds=True, extra_requirements={'Cocktail shaker': 1, 'Vodka': 1, 'Gin': 1, 'Dwellberries': 1, 'Pineapple chunks': 1, 'Pot of cream': 1}, byproducts={'Cocktail shaker': 1}, failure_kind='pour'),
    CookingTarget('mix_choc_saturday', 'CHOC_SATURDAY', 'Mix a choc saturday', 'gnome_cocktails', 'COCKTAIL_GLASS', 2026, 'Cocktail glass', 'CHOC_SATURDAY', 2074, 'Choc saturday', '', 0, '', 33, 170.0, 0, 0, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, source_always_succeeds=True, extra_requirements={'Cocktail shaker': 1, 'Whisky': 1, 'Chocolate bar': 1, 'Equa leaves': 1, 'Bucket of milk': 1, 'Chocolate dust': 1, 'Pot of cream': 1}, byproducts={'Cocktail shaker': 1, 'Bucket': 1}, failure_kind='pour'),
    CookingTarget('mix_blurberry_special', 'BLURBERRY_SPECIAL', 'Mix a blurberry special', 'gnome_cocktails', 'COCKTAIL_GLASS', 2026, 'Cocktail glass', 'BLURBERRY_SPECIAL', 2064, 'Blurberry special', '', 0, '', 37, 180.0, 0, 0, source=GNOME_COOKING_SOURCE, runtime_source=GNOME_COOKING_SOURCE, source_always_succeeds=True, extra_requirements={'Cocktail shaker': 1, 'Vodka': 1, 'Brandy': 1, 'Gin': 1, 'Lemon': 2, 'Orange': 1, 'Lemon chunks': 1, 'Orange chunks': 1, 'Equa leaves': 1, 'Lime slices': 1}, byproducts={'Cocktail shaker': 1}, failure_kind='pour'),
    CookingTarget('brew_dwarven_stout', 'DWARVEN_STOUT_M', 'Brew Dwarven stout', 'brewing', 'ALE_YEAST', 5767, 'Ale yeast', 'DWARVEN_STOUT_M', 5747, 'Dwarven stout (m)', '', 0, '', 19, 215.0, 0, 0, source=BREWING_SOURCE, runtime_source=BREWING_SOURCE, source_success_formula={'base': _DWARVEN_STOUT_MATURE_CHANCE, 'level_multiplier': 0.0, 'level_range': 1.0, 'cap': _DWARVEN_STOUT_MATURE_CHANCE, 'divisor': 1.0}, byproducts={'Bucket': 2}, extra_requirements={'Bucket of water': 2, 'Barley malt': 2, 'Hammerstone hops': 4, 'Beer glass': 8}, failure_kind='mature', output_qty=8, alternate_output_item='Dwarven stout', alternate_output_qty=8, outcome_kind='maturity'),
    CookingTarget('brew_dwarven_stout_with_the_stuff', 'DWARVEN_STOUT_M_STUFF', 'Brew Dwarven stout with The stuff', 'brewing', 'ALE_YEAST', 5767, 'Ale yeast', 'DWARVEN_STOUT_M', 5747, 'Dwarven stout (m)', '', 0, '', 19, 215.0, 0, 0, source=BREWING_SOURCE, runtime_source=BREWING_SOURCE, source_success_formula={'base': _DWARVEN_STOUT_STUFF_MATURE_CHANCE, 'level_multiplier': 0.0, 'level_range': 1.0, 'cap': _DWARVEN_STOUT_STUFF_MATURE_CHANCE, 'divisor': 1.0}, byproducts={'Bucket': 2}, extra_requirements={'Bucket of water': 2, 'Barley malt': 2, 'Hammerstone hops': 4, 'Beer glass': 8, 'The stuff': 1}, failure_kind='mature', output_qty=8, alternate_output_item='Dwarven stout', alternate_output_qty=8, outcome_kind='maturity'),
)

COOKING_TARGETS_BY_ID: Dict[str, CookingTarget] = {target.id: target for target in COOKING_TARGETS}
DEFAULT_COOKING_TARGET = "cook_shrimps"


COOKING_PREP_ACTIVITIES: Tuple[CookingPrepActivity, ...] = (
    CookingPrepActivity("gather_grain", "Gather grain", {}, "Grain", group="gathering", source=WHEAT_PICK_SOURCE_PATH),
    CookingPrepActivity(
        "skewer_spider_on_a_stick",
        "Skewer a spider carcass",
        {"Spider carcass": 1, "Skewer stick": 1},
        "Raw spider on stick",
        source=SPIDER_RECIPE_SOURCE_PATH,
    ),
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
    # Gnome cocktails and the fruit batta need fruit sliced or diced with a knife.
    # Source: Gnome cooking oldid 6438943, which lists the knife as gnome cooking
    # equipment and says the fruit is "used either sliced or diced".
    CookingPrepActivity("slice_lemon", "Slice a lemon", {"Lemon": 1}, "Lemon slices", source=GNOME_COOKING_SOURCE),
    CookingPrepActivity("dice_lemon", "Dice a lemon", {"Lemon": 1}, "Lemon chunks", source=GNOME_COOKING_SOURCE),
    CookingPrepActivity("slice_lime", "Slice a lime", {"Lime": 1}, "Lime slices", source=GNOME_COOKING_SOURCE),
    CookingPrepActivity("dice_lime", "Dice a lime", {"Lime": 1}, "Lime chunks", source=GNOME_COOKING_SOURCE),
    CookingPrepActivity("slice_orange", "Slice an orange", {"Orange": 1}, "Orange slices", source=GNOME_COOKING_SOURCE),
    CookingPrepActivity("dice_orange", "Dice an orange", {"Orange": 1}, "Orange chunks", source=GNOME_COOKING_SOURCE),
    CookingPrepActivity("dice_pineapple", "Dice a pineapple", {"Pineapple": 1}, "Pineapple chunks", source=GNOME_COOKING_SOURCE),
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
    "Bucket of milk": (1927, True),
    "Bucket of water": (1929, True),
    "Pat of butter": (6697, True),
    "Cheese wheel": (18789, False),
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
    "Raw tiger shark": (21520, False),
    "Tiger shark": (21521, False),
    "Burnt tiger shark": (21522, False),
    "Raw lava eel": (2148, False),
    "Lava eel": (2149, False),
    "Spider carcass": (6291, True),
    "Raw spider on stick": (6293, True),
    "Skewer stick": (6305, True),
    # Gnome cooking inputs. Every id is from 2011Scape items.yml; every one is live
    # NPC shop stock (Grand Tree Groceries, Funch's Fine Groceries, Blurberry Bar)
    # except King worm and Toad's legs, which come from pickpocketing gnomes and
    # from the Herblore toad-leg bridge.
    "Gianne dough": (2171, True),
    "Gnome spice": (2169, True),
    "Equa leaves": (2128, True),
    "Batta tin": (2164, True),
    "Crunchy tray": (2165, True),
    "Gnomebowl mould": (2166, True),
    "King worm": (2162, True),
    "Toad's legs": (2152, True),
    "Dwellberries": (2126, True),
    "Pot of cream": (2130, True),
    "Chocolate bar": (1973, True),
    "Chocolate dust": (1975, True),
    "Cocktail shaker": (2025, True),
    "Cocktail glass": (2026, True),
    "Vodka": (2015, True),
    "Gin": (2019, True),
    "Whisky": (2017, True),
    "Brandy": (2021, True),
    "Lemon": (2102, True),
    "Lemon chunks": (2104, True),
    "Lemon slices": (2106, True),
    "Lime": (2120, True),
    "Lime chunks": (2122, True),
    "Lime slices": (2124, True),
    "Orange": (2108, True),
    "Orange chunks": (2110, True),
    "Orange slices": (2112, True),
    "Pineapple": (2114, True),
    "Pineapple chunks": (2116, True),
    "Ale yeast": (5767, True),
    "Barley malt": (6008, True),
    "Hammerstone hops": (5994, True),
    "Beer glass": (1919, True),
    "Dwarven stout": (1913, True),
    "Dwarven stout (m)": (5747, True),
    "The stuff": (8988, False),
}

SOURCE_NONSTACKABLE_ITEMS = frozenset(
    {"Raw tiger shark", "Tiger shark", "Burnt tiger shark"}
)

for _target in COOKING_TARGETS:
    if _target.source in (GUT_FISH_SOURCE_PATH, SEAWEED_COOKING_SOURCE_PATH):
        continue
    SOURCE_ITEM_DATA.setdefault(_target.raw_item, (_target.raw_item_id, True))
    SOURCE_ITEM_DATA.setdefault(_target.cooked_item, (_target.cooked_item_id, True))
    if _target.burnt_item:
        SOURCE_ITEM_DATA.setdefault(_target.burnt_item, (_target.burnt_item_id, False))


_MATERIAL_CATEGORIES = {
    "Batta tin": "crafted",
    "Crunchy tray": "crafted",
    "Gnomebowl mould": "crafted",
    "Cocktail shaker": "crafted",
    "Cocktail glass": "crafted",
    "Bucket": "crafted",
    "Bucket of water": "material",
    "Bowl of water": "material",
    "Empty pot": "crafted",
    "Bowl": "crafted",
    "Pie dish": "crafted",
    "Skewer stick": "crafted",
    "Clay": "ore",
    "Ale yeast": "material",
    "Barley malt": "material",
    "Hammerstone hops": "material",
    "Beer glass": "crafted",
    "The stuff": "material",
}


def cooking_targets_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        target.id: {
            "display_name": target.display_name,
            "family": target.family,
            "level": target.level,
            "exp": target.base_exp,
            "requirements": {target.raw_item: 1, **dict(target.extra_requirements)},
            "raw_item": target.raw_item,
            "raw_item_id": target.raw_item_id,
            "cooked_item": target.cooked_item,
            "cooked_item_id": target.cooked_item_id,
            "output_item": target.cooked_item,
            "output_qty": target.output_qty,
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
            **({"cooking_gauntlet_no_burn_level": target.cooking_gauntlet_no_burn_level} if target.cooking_gauntlet_no_burn_level else {}),
            **({"byproduct_item": target.byproduct_item, "byproduct_chance": target.byproduct_chance} if target.byproduct_item else {}),
            **({"byproducts": dict(target.byproducts)} if target.byproducts else {}),
            **({"output_quantity_model": target.output_quantity_model} if target.output_quantity_model else {}),
            **({"xp_per_output": target.xp_per_output} if target.xp_per_output else {}),
            **({"failure_kind": target.failure_kind} if target.failure_kind != "burn" else {}),
            **({"alternate_output_item": target.alternate_output_item, "alternate_output_qty": target.alternate_output_qty} if target.alternate_output_item else {}),
            **({"outcome_kind": target.outcome_kind} if target.outcome_kind else {}),
        }
        for target in COOKING_TARGETS
    }


def cooking_output_items() -> Tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            item
            for target in COOKING_TARGETS
            for item in (target.cooked_item, target.alternate_output_item)
            if item
        )
    )


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
            **({"stackable": False} if item_name in SOURCE_NONSTACKABLE_ITEMS else {}),
        }
    return result
