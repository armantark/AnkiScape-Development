"""Cutoff Gnome Restaurant order pools, points, reward token, and tip tables."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .cooking_data import COOKING_TARGETS


GNOME_RESTAURANT_ACTIVITY_ID = "gnome_restaurant"
GNOME_RESTAURANT_SOURCE = (
    "RuneScape Wiki Gnome Restaurant oldid=6491107 (2012-10-28T20:51:36Z); "
    "Reward token (Gnome Restaurant) oldid=6117402 (2012-08-20T10:58:52Z); "
    "Aluft aloft box oldid=6082000 (2012-08-12T22:30:44Z); "
    "Aluft Gianne snr. oldid=6221695 (2012-09-09T19:18:08Z); "
    "Blurberry oldid=6222077 (2012-09-09T19:34:38Z); "
    "memory-bank/source-audits/gnome-restaurant-harvest-2026-07-28.md"
)

# Exact: every easy delivery pays one point, every hard delivery three, twelve
# points pay a Reward token, and each further twelve adds one banked food item up
# to ten. Activating the token resets the banked count.
GNOME_RESTAURANT_EASY_POINTS = 1
GNOME_RESTAURANT_HARD_POINTS = 3
GNOME_RESTAURANT_TOKEN_POINTS = 12
GNOME_RESTAURANT_TOKEN_MEAL_CAP = 10

# Exact: an easy job allows six source minutes and a hard job eleven. The owner
# settled on 2026-07-17 that these bound tip quality rather than expiring the
# order, so the order carries the source minutes and each `Again` spends six world
# minutes of them, the answered-card convention Big Chinchompa already uses.
GNOME_RESTAURANT_EASY_MINUTES = 6
GNOME_RESTAURANT_HARD_MINUTES = 11
GNOME_RESTAURANT_WORLD_MINUTES_PER_REVIEW = 6
# Exact five source minutes, one answered card under the same convention.
GNOME_RESTAURANT_HARD_DECLINE_WAIT_REVIEWS = 1

# Exact: Aluft Gianne snr. asks for four different gnome dishes and Blurberry for
# four different cocktails before the delivery service opens, and snr. hands over
# 100 Gianne dough once the training is done.
GNOME_RESTAURANT_TUTORIAL_DISHES = 4
GNOME_RESTAURANT_TUTORIAL_COCKTAILS = 4
GNOME_RESTAURANT_STARTING_DOUGH = 100
GNOME_RESTAURANT_BOX_ITEM = "Aluft aloft box"
GNOME_RESTAURANT_TOKEN_ITEM = "Reward token"

GNOME_DISH_ITEMS = tuple(
    target.cooked_item
    for target in COOKING_TARGETS
    if target.family in ("gnome_crunchies", "gnome_battas", "gnome_bowls")
)
GNOME_COCKTAIL_ITEMS = tuple(
    target.cooked_item for target in COOKING_TARGETS if target.family == "gnome_cocktails"
)
GNOME_DISH_TARGET_IDS = tuple(
    target.id
    for target in COOKING_TARGETS
    if target.family in ("gnome_crunchies", "gnome_battas", "gnome_bowls")
)
GNOME_COCKTAIL_TARGET_IDS = tuple(
    target.id for target in COOKING_TARGETS if target.family == "gnome_cocktails"
)
# The twenty items an order can ask for. No source states the relative frequency,
# and item pages call some orders "semi-rare", so the draw is uniform.
# PLACEHOLDER(gnome_restaurant.request_weights): authentic per-item order frequency
GNOME_RESTAURANT_REQUEST_ITEMS = GNOME_DISH_ITEMS + GNOME_COCKTAIL_ITEMS
# The token's only sourced rule is that drinks come up more rarely than dishes.
# PLACEHOLDER(gnome_restaurant.token_food_weights): authentic reward-token food weights
GNOME_RESTAURANT_TOKEN_DISH_WEIGHT = 3
GNOME_RESTAURANT_TOKEN_COCKTAIL_WEIGHT = 1


@dataclass(frozen=True)
class GnomeCustomer:
    id: str
    display_name: str
    difficulty: str
    location: str
    required_quest: str = ""
    required_magic: int = 0


GNOME_RESTAURANT_CUSTOMERS: tuple[GnomeCustomer, ...] = (
    GnomeCustomer("burkor", "Burkor", "easy", "Tower guard south-east of the Gnome Ball field"),
    GnomeCustomer("brimstail", "Brimstail", "easy", "Cave in the south-west of the Stronghold"),
    GnomeCustomer("captain_errdo", "Captain Errdo", "easy", "Glider pilot, top of the Grand Tree"),
    GnomeCustomer("coach", "Coach", "easy", "Outside the Gnome Ball field"),
    GnomeCustomer("dalila", "Dalila", "easy", "Restaurant customer, Grand Tree second level"),
    GnomeCustomer("damwin", "Damwin", "easy", "Cheerleader in the bar east of the Gnome Ball field"),
    GnomeCustomer("eebel", "Eebel", "easy", "In a tree south of the Stronghold"),
    GnomeCustomer("ermin", "Ermin", "easy", "Spinner south of the magic tree"),
    GnomeCustomer("femi", "Femi", "easy", "Trader outside the south gates"),
    GnomeCustomer("froono", "Froono", "easy", "In a tree south of the bank"),
    GnomeCustomer("guard_vemmeldo", "Guard Vemmeldo", "easy", "The bank west of the agility course"),
    GnomeCustomer("gulluck", "Gulluck", "easy", "Armourer, Grand Tree third level"),
    GnomeCustomer("king_narnode_shareen", "King Narnode Shareen", "easy", "Base of the Grand Tree"),
    GnomeCustomer("meegle", "Meegle", "easy", "Terrorbird breeder, south-west of the Stronghold"),
    GnomeCustomer("perrdur", "Perrdur", "easy", "Restaurant customer, Grand Tree second level"),
    GnomeCustomer("rometti", "Rometti", "easy", "Master Tailor, Grand Tree first level"),
    GnomeCustomer("sarble", "Sarble", "easy", "The swamp west of the Grand Tree"),
    GnomeCustomer("trainer_nacklepen", "Trainer Nacklepen", "easy", "The tortoise pen north of the swamp"),
    GnomeCustomer("wurbel", "Wurbel", "easy", "Gnome Ball fan, in the tree south of the field"),
    GnomeCustomer("ambassador_ferrnook", "Ambassador Ferrnook", "hard", "First floor of Varrock Palace"),
    GnomeCustomer("ambassador_gimblewap", "Ambassador Gimblewap", "hard", "First floor of Ardougne castle"),
    GnomeCustomer("ambassador_spanfipple", "Ambassador Spanfipple", "hard", "First floor of Falador castle"),
    GnomeCustomer("brambickle", "Brambickle", "hard", "Trollweiss Mountain, by the Ice Troll cave", required_quest="troll_romance"),
    GnomeCustomer("captain_bleemadge", "Captain Bleemadge", "hard", "Glider pilot atop White Wolf Mountain"),
    GnomeCustomer("captain_daerkin", "Captain Daerkin", "hard", "The stands at the Duel Arena"),
    GnomeCustomer("captain_dalbur", "Captain Dalbur", "hard", "Al Kharid glider pilot"),
    GnomeCustomer("captain_klemfoodle", "Captain Klemfoodle", "hard", "Karamja glider pilot"),
    GnomeCustomer("captain_ninto", "Captain Ninto", "hard", "The dwarven bar under White Wolf Mountain", required_quest="fishing_contest"),
    GnomeCustomer("garkor", "Garkor", "hard", "Ape Atoll, north-east of the island", required_quest="monkey_madness"),
    GnomeCustomer("glo_caranock", "G.L.O. Caranock", "hard", "A hut at the Karamja Ship Yard", required_quest="the_grand_tree"),
    GnomeCustomer("gnormadium_avlafrim", "Gnormadium Avlafrim", "hard", "Feldip Hills glider pilot"),
    GnomeCustomer("hazelmere", "Hazelmere", "hard", "His hut on the archipelago east of Yanille"),
    GnomeCustomer("king_bolren", "King Bolren", "hard", "Tree Gnome Village, by the spirit tree"),
    GnomeCustomer("lieutenant_schepbur", "Lieutenant Schepbur", "hard", "Khazard battlefield outside Tree Gnome Village"),
    GnomeCustomer("penwie", "Penwie", "hard", "Karamja jungle"),
    GnomeCustomer("professor_imblewyn", "Professor Imblewyn", "hard", "The Wizards' Tower basement", required_magic=66),
    GnomeCustomer("professor_manglethorp", "Professor Manglethorp", "hard", "Keldagrim", required_quest="the_giant_dwarf"),
    GnomeCustomer("professor_onglewip", "Professor Onglewip", "hard", "The Wizards' Tower"),
    GnomeCustomer("wingstone", "Wingstone", "hard", "The desert south of the Bedabin camp"),
)
GNOME_RESTAURANT_CUSTOMERS_BY_ID = {row.id: row for row in GNOME_RESTAURANT_CUSTOMERS}
GNOME_RESTAURANT_DIFFICULTIES = (
    ("easy", "Easy job, around the Grand Tree"),
    ("hard", "Hard job, anywhere in Gielinor"),
)


@dataclass(frozen=True)
class GnomeTip:
    id: str
    item: str
    low: int
    high: int
    group: str
    customers: tuple[str, ...] = field(default_factory=tuple)


# Exact rows and quantity ranges from the cutoff article. `unique` is the good-tip
# group; the rest are the ordinary hard-delivery tips. Rows naming particular
# gnomes are locked to them.
GNOME_RESTAURANT_TIPS: tuple[GnomeTip, ...] = (
    GnomeTip("gnome_goggles", "Gnome goggles", 1, 1, "unique", ("captain_ninto", "captain_daerkin")),
    GnomeTip("gnome_scarf", "Gnome scarf", 1, 1, "unique", ("captain_ninto", "captain_daerkin")),
    GnomeTip("grand_seed_pod", "Grand seed pod", 8, 15, "unique"),
    GnomeTip("mint_cake", "Mint cake", 8, 10, "unique"),
    GnomeTip("gnomeball", "Gnomeball", 1, 1, "unique"),
    GnomeTip("clean_toadflax", "Clean toadflax", 3, 3, "herb"),
    GnomeTip("clean_snapdragon", "Clean snapdragon", 1, 1, "herb"),
    GnomeTip("goutweed", "Goutweed", 1, 1, "herb"),
    GnomeTip("uncut_jade", "Uncut jade", 2, 3, "gem"),
    GnomeTip("uncut_opal", "Uncut opal", 3, 3, "gem"),
    GnomeTip("uncut_red_topaz", "Uncut red topaz", 1, 1, "gem"),
    GnomeTip("uncut_sapphire", "Uncut sapphire", 6, 16, "gem"),
    GnomeTip("uncut_ruby", "Uncut ruby", 2, 4, "gem"),
    GnomeTip("uncut_emerald", "Uncut emerald", 3, 5, "gem"),
    GnomeTip("uncut_diamond", "Uncut diamond", 1, 1, "gem"),
    GnomeTip("death_rune", "Death rune", 7, 13, "rune", ("professor_imblewyn", "professor_onglewip")),
    GnomeTip("blood_rune", "Blood rune", 6, 10, "rune", ("professor_imblewyn", "professor_onglewip")),
    GnomeTip("soul_rune", "Soul rune", 5, 11, "rune", ("professor_imblewyn", "professor_onglewip")),
    GnomeTip("law_rune", "Law rune", 7, 18, "rune", ("professor_imblewyn", "professor_onglewip")),
    GnomeTip("nature_rune", "Nature rune", 9, 15, "rune", ("professor_imblewyn", "professor_onglewip")),
    GnomeTip("chaos_rune", "Chaos rune", 16, 27, "rune", ("professor_imblewyn", "professor_onglewip")),
    GnomeTip("cosmic_rune", "Cosmic rune", 10, 19, "rune", ("professor_imblewyn", "professor_onglewip")),
    GnomeTip("mithril_bolts", "Mithril bolts", 17, 35, "bolt"),
    GnomeTip("adamant_bolts", "Adamant bolts", 13, 26, "bolt"),
    GnomeTip("runite_bolts", "Runite bolts", 7, 15, "bolt"),
    GnomeTip("magic_seed", "Magic seed", 1, 3, "other"),
    GnomeTip("yew_seed", "Yew seed", 1, 1, "other"),
    GnomeTip("calquat_tree_seed", "Calquat tree seed", 1, 1, "other"),
    GnomeTip("birds_nest", "Bird's nest", 1, 1, "other"),
    GnomeTip("snake_charm", "Snake charm", 1, 1, "other", ("wingstone",)),
    GnomeTip("loop_half_of_a_key", "Loop half of a key", 1, 1, "other"),
    GnomeTip("tooth_half_of_a_key", "Tooth half of a key", 1, 1, "other"),
    GnomeTip("pineapple_seed", "Pineapple seed", 1, 1, "other"),
    GnomeTip("gold_ore", "Gold ore", 6, 11, "other", ("professor_manglethorp",)),
    GnomeTip("coal", "Coal", 12, 22, "other", ("professor_manglethorp",)),
    GnomeTip("raw_oomlie", "Raw oomlie", 1, 1, "other", ("penwie",)),
    GnomeTip("pure_essence", "Pure essence", 51, 97, "other", ("professor_imblewyn", "professor_onglewip")),
)
GNOME_RESTAURANT_TIPS_BY_ID = {row.id: row for row in GNOME_RESTAURANT_TIPS}
GNOME_RESTAURANT_GOOD_TIP_GROUP = "unique"
# Exact: an easy delivery tips 10 to 500 coins.
GNOME_RESTAURANT_EASY_TIP_COINS = (10, 500)
# The article says only that a fast delivery raises the chance of a good tip. The
# punctuality that survives the order becomes that chance directly, and the
# quantity inside each sourced range is a uniform inclusive roll.
# PLACEHOLDER(gnome_restaurant.good_tip_curve): authentic delivery-speed to tip-quality curve
# PLACEHOLDER(gnome_restaurant.tip_weights): authentic tip-row weights and quantity distribution
GNOME_RESTAURANT_TIP_ROW_MODEL = "uniform_over_eligible_rows"

GNOME_RESTAURANT_ASSET_MANIFEST = (
    {
        "item_name": "Gnome Restaurant",
        "wiki_title": "Reward token (Gnome Restaurant).png",
        "output_path": "activityicons/gnome_restaurant.png",
        "size": 64,
    },
    {
        "item_name": GNOME_RESTAURANT_TOKEN_ITEM,
        "wiki_title": "Reward token (Gnome Restaurant).png",
        "output_path": "activityitems/gnome_restaurant_reward_token.png",
        "size": 64,
    },
    {
        "item_name": GNOME_RESTAURANT_BOX_ITEM,
        "wiki_title": "Aluft aloft box.png",
        "output_path": "activityitems/gnome_restaurant_aluft_aloft_box.png",
        "size": 64,
    },
    {
        "item_name": "Mint cake",
        "wiki_title": "Mint cake detail.png",
        "output_path": "activityitems/gnome_restaurant_mint_cake.png",
        "size": 64,
    },
    {
        "item_name": "Gnome scarf",
        "wiki_title": "Gnome scarf.png",
        "output_path": "activityitems/gnome_restaurant_gnome_scarf.png",
        "size": 64,
    },
    {
        "item_name": "Gnome goggles",
        "wiki_title": "Gnome goggles.png",
        "output_path": "activityitems/gnome_restaurant_gnome_goggles.png",
        "size": 64,
    },
    {
        "item_name": "Grand seed pod",
        "wiki_title": "Grand seed pod.png",
        "output_path": "activityitems/gnome_restaurant_grand_seed_pod.png",
        "size": 64,
    },
    {
        "item_name": "Snake charm",
        "wiki_title": "Snake charm.png",
        "output_path": "activityitems/gnome_restaurant_snake_charm.png",
        "size": 64,
    },
)
# Bird's nest has no pre-cutoff upload under any of its wiki titles, so the tip row
# ships without art rather than with a post-cutoff sprite.

# Item ids from 2011Scape items.yml. The Restaurant's own additions live in the
# 94xx block; Bird's nest shares its name with three seed-bearing variants and
# takes the first of them.
_EXTRA_ITEM_IDS = {
    GNOME_RESTAURANT_TOKEN_ITEM: 9474,
    GNOME_RESTAURANT_BOX_ITEM: 9477,
    "Mint cake": 9475,
    "Gnome scarf": 9470,
    "Gnome goggles": 9472,
    "Grand seed pod": 9469,
    "Snake charm": 4605,
    "Bird's nest": 5070,
}
_UNTRADEABLE_EXTRA_ITEMS = frozenset({GNOME_RESTAURANT_TOKEN_ITEM, GNOME_RESTAURANT_BOX_ITEM})


def gnome_restaurant_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        GNOME_RESTAURANT_ACTIVITY_ID: {
            "display_name": "Gnome Restaurant",
            "requirements": {},
            "skill_requirements": {},
            "outputs": (GNOME_RESTAURANT_TOKEN_ITEM, "Coins"),
            "batch_size": 1,
            "group": "minigames",
            "source": GNOME_RESTAURANT_SOURCE,
        }
    }


def gnome_restaurant_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        item_name: {
            "category": "material",
            "source_item_id": item_id,
            "stackable": False,
            "tradeable": item_name not in _UNTRADEABLE_EXTRA_ITEMS,
            "source": GNOME_RESTAURANT_SOURCE,
        }
        for item_name, item_id in _EXTRA_ITEM_IDS.items()
    }


def gnome_restaurant_customers_for_pure(
    difficulty: str,
    completed_quests: frozenset[str],
    magic_level: int,
) -> tuple[GnomeCustomer, ...]:
    """Customers a player can actually reach right now, in pool order."""
    return tuple(
        row
        for row in GNOME_RESTAURANT_CUSTOMERS
        if row.difficulty == difficulty
        and (not row.required_quest or row.required_quest in completed_quests)
        and magic_level >= row.required_magic
    )


def gnome_restaurant_tips_for_pure(customer_id: str, group: str) -> tuple[GnomeTip, ...]:
    return tuple(
        row
        for row in GNOME_RESTAURANT_TIPS
        if row.group == group and (not row.customers or customer_id in row.customers)
    )
