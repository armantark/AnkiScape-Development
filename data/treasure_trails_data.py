"""Cutoff Treasure Trails facts for the Easy tier, plus the clue-item family.

Two period rules drive the shape of this module. A player may hold **one clue
scroll in total**, not one per tier — the per-tier rule is a 2015 mechanic that
reached an AnkiScape record by anachronism. And the casket reward is rolled when
the casket opens, so a finished trail is worth the same however long it ran.

The step list is a real period subset rather than the full catalog: enough rows
to exercise every step kind the easy tier uses. The reward tables are likewise a
real subset of the period reward families. Both are deliberate breadth-phase
deferrals of catalog depth, not placeholders — the full tables exist in the
sources named below and can be widened without changing a mechanic.

Cryptic steps are not shipped. The easy-clue page lists them as an easy step
kind, but no pinned source tags an individual cryptic row as easy, and a cryptic
resolves exactly as a simple clue does under the settled flattening, so shipping
a guessed tier assignment would add no mechanic and one invention.
"""

from __future__ import annotations

from typing import Any


TREASURE_TRAILS_ACTIVITY_ID = "treasure_trail"

TREASURE_TRAILS_SOURCE = (
    "RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); "
    "Clue scroll (easy) oldid=6333359 (2012-10-02T09:39:55Z); "
    "Treasure Trails/Guide/Simple clues oldid=6579176 (2012-11-18T16:48:49Z); "
    "Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); "
    "Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); "
    "Darkan TreasureTrailsManager.java and "
    "data/npcs/drops/treasure_trails/easy_casket.json"
)

EASY_TIER = "easy"

# "There are four levels of clue scroll difficulty". Only the easy trail ships;
# the rest are named so a clue the player already owns reports an honest reason
# rather than sitting inert in the bank.
CLUE_SCROLL_ITEMS = {
    "easy": "Clue scroll (easy)",
    "medium": "Clue scroll (medium)",
    "hard": "Clue scroll (hard)",
    "elite": "Clue scroll (elite)",
}
CASKET_ITEMS = {
    "easy": "Casket (easy)",
    "medium": "Casket (medium)",
    "hard": "Casket (hard)",
    "elite": "Casket (elite)",
}
IMPLEMENTED_CLUE_TIERS = (EASY_TIER,)

# "Easy trails can be between 1 and 5 clues long". Darkan rolls 1 + random(3),
# which cannot reach five, so the period page wins over the reconstruction.
TREASURE_TRAILS_EASY_MIN_STEPS = 1
TREASURE_TRAILS_EASY_MAX_STEPS = 5

# Darkan: `for (int i = 0; i < Utils.randomInclusive(2, 4); i++)` over the
# easy_casket set, whose two rows are 1/12 rare and 11/12 standard.
TREASURE_TRAILS_EASY_REWARD_SPOTS = (2, 4)
TREASURE_TRAILS_EASY_RARE_CHANCE = (1, 12)


def _step(step_id: str, kind: str, text: str, *, equipment: tuple[str, ...] = (), bare: bool = False) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "kind": kind,
        "text": text,
        "equipment": equipment,
        # One easy emote clue demands the opposite of a gear check: nothing worn
        # at all. It is a real period row and the cheapest proof that the gear
        # gate reads the player's equipment rather than a checklist.
        "bare": bare,
        "source": TREASURE_TRAILS_SOURCE,
    }


TREASURE_TRAILS_EASY_STEPS: dict[str, dict[str, Any]] = {
    row["step_id"]: row
    for row in (
        _step(
            "simple_port_sarim_sailor",
            "simple",
            "One of the sailors in Port Sarim is your next destination.",
        ),
        _step(
            "simple_varrock_palace_crate",
            "simple",
            "Search for a crate in Varrock Palace.",
        ),
        _step(
            "simple_lumbridge_goblin_house",
            "simple",
            "Search the boxes in the Goblin house near Lumbridge.",
        ),
        _step(
            "simple_grand_tree_mushrooms",
            "simple",
            "Dig near some giant mushrooms behind the Grand Tree.",
        ),
        _step(
            "map_clock_tower_crates",
            "map",
            "Map: crates stacked behind the Clock tower building south of Ardougne Castle.",
        ),
        _step(
            "map_lumberyard_crate",
            "map",
            "Map: the crate in the storage area behind the Lumberyard sawmill operator, north-east of Varrock.",
        ),
        _step(
            "emote_duel_arena_bow",
            "emote",
            "Bow or curtsy in the lobby of the Duel Arena. Equip an iron chainbody, leather chaps and a coif.",
            equipment=("Iron chainbody", "Leather chaps", "Coif"),
        ),
        _step(
            "emote_port_sarim_cheer",
            "emote",
            "Cheer for the monks at Port Sarim. Equip a coif, steel plateskirt and a sapphire necklace.",
            equipment=("Coif", "Steel plateskirt", "Sapphire necklace"),
        ),
        _step(
            "emote_burthorpe_games_room_cheer",
            "emote",
            "Cheer at the Burthorpe Games Room. Have nothing equipped at all when you do.",
            bare=True,
        ),
    )
}

# The easy-exclusive uniques, from the pinned Treasure Trails "Easy rewards"
# table. The trimmed black armour ids match Darkan's easy_rare rows exactly,
# which is how we know the two records describe the same table.
TREASURE_TRAILS_EASY_RARE_REWARDS: tuple[dict[str, Any], ...] = (
    {"item": "Black platebody (t)", "minimum": 1, "maximum": 1, "source_item_id": 2583},
    {"item": "Black full helm (t)", "minimum": 1, "maximum": 1, "source_item_id": 2587},
    {"item": "Highwayman mask", "minimum": 1, "maximum": 1, "source_item_id": 2631},
    {"item": "Amulet of magic (t)", "minimum": 1, "maximum": 1, "source_item_id": 10366},
    {"item": "Black cane", "minimum": 1, "maximum": 1, "source_item_id": 13095},
    {"item": "Spiked helmet", "minimum": 1, "maximum": 1, "source_item_id": 13105},
)

# The common rows, with Darkan's own quantities from easy_standard.json.
TREASURE_TRAILS_EASY_STANDARD_REWARDS: tuple[dict[str, Any], ...] = (
    {"item": "Coins", "minimum": 50, "maximum": 200, "source_item_id": 995},
    {"item": "Purple sweets", "minimum": 1, "maximum": 1, "source_item_id": 10476},
    {"item": "Nature rune", "minimum": 5, "maximum": 10, "source_item_id": 561},
    {"item": "Law rune", "minimum": 5, "maximum": 10, "source_item_id": 563},
    {"item": "Fire rune", "minimum": 30, "maximum": 50, "source_item_id": 554},
    {"item": "Air rune", "minimum": 30, "maximum": 50, "source_item_id": 556},
)


def treasure_trails_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        TREASURE_TRAILS_ACTIVITY_ID: {
            "display_name": "Treasure Trails",
            "requirements": {},
            "skill_requirements": {},
            "outputs": (CASKET_ITEMS[EASY_TIER],),
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": TREASURE_TRAILS_SOURCE,
        }
    }


# Art this family owns. Reward items are deliberately absent from the item
# registration below — they already carry identities and exchange rows of their
# own — but they still need a picture, so the icon map is keyed separately.
TREASURE_TRAILS_ART_ITEMS = (
    CLUE_SCROLL_ITEMS["hard"],
    CASKET_ITEMS[EASY_TIER],
    "Purple sweets",
) + tuple(str(row["item"]) for row in TREASURE_TRAILS_EASY_RARE_REWARDS)


def treasure_trails_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    """The two clue-family rows nothing else owns.

    `Clue scroll (hard)` is registered here because three combat drop tables
    already award it while easy, medium and elite were registered and it was
    not. Treasure Trails owns clue scrolls, so it owns that row. The casket
    joins it because this family is the only thing that reads one.

    The reward items are not registered. They already have item identities and
    exchange rows elsewhere, and a second registration would overwrite the
    owning system's metadata rather than add to it.
    """
    return {
        CLUE_SCROLL_ITEMS["hard"]: {
            "category": "material",
            "source": TREASURE_TRAILS_SOURCE,
        },
        CASKET_ITEMS[EASY_TIER]: {
            "category": "material",
            "source": TREASURE_TRAILS_SOURCE,
            "source_item_id": 2714,
        },
    }
