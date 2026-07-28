"""Period Mobilising Armies squads, scenarios, ranks, and Officer Tower shop.

Every value here is either exact from a pinned source or a labelled
``PLACEHOLDER`` for a value the period game had that no recovered source states.
The four scenarios, the squad roster, the rank ladder, the reward-credit formula,
and every Officer Tower price are exact. What the sources never give is the
server's per-second behaviour inside a thirty-minute battle: how fast an
objective advances, how hard squads hit each other, and how the time bonus
curves. Those are the placeholders.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem


MOBILISING_ARMIES_ACTIVITY_ID = "mobilising_armies"

MOBILISING_ARMIES_SOURCE = (
    "RuneScape Wiki Mobilising Armies oldid=6514352 (2012-11-01T00:57:11Z); "
    "Mobilising Armies/Rewards oldid=6339595 (2012-10-03T11:14:47Z); "
    "Mobilising Armies/Investments oldid=6538687 (2012-11-06T04:51:16Z); "
    "Mobilising Armies/Conflict oldid=5371840 (2012-03-13T03:46:44Z); "
    "Mobilising Armies/Siege oldid=6002719 (2012-07-27T14:15:49Z); "
    "Mobilising Armies/Hoard oldid=3819762 (2011-01-29T13:23:56Z); "
    "Mobilising Armies/Rescue oldid=6492730 (2012-10-29T07:20:25Z); "
    "Locator oldid=5509339 (2012-04-18T23:44:45Z); "
    "Quest kit oldid=5565058 (2012-05-04T14:15:02Z); "
    "Serjeant top oldid=6339598 (2012-10-03T11:14:56Z); "
    "game-main data/cfg/items.yml ids 14940 and 15001-15026, 15336"
)


# --- Investment credits -----------------------------------------------------
#
# Exact. The Investments page states the rule as "((low alch value)/2)+1 equals
# how much investment credits you will gain per item", and low alchemy is 40% of
# the cache store value. Cross-checked against seven independent credit figures
# on that page using the Darkan store values already in this repo: Adamant bar
# 129, Adamant bolts 12, Adamant javelin 50, Agility potion (4) 41, Air rune 4,
# Amulet of fury 40,401, Amulet of glory 3,526. All seven match exactly.
MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP = 500_000
MOBILISING_ARMIES_LOW_ALCHEMY_RATE = 0.4


def mobilising_armies_investment_credits_pure(store_value: int) -> int:
    """Investment credits one item is worth, from its cache store value."""
    low_alchemy = int(max(0, int(store_value)) * MOBILISING_ARMIES_LOW_ALCHEMY_RATE)
    return (low_alchemy // 2) + 1 if low_alchemy > 0 else 0


# --- Squads -----------------------------------------------------------------
#
# Exact: every combat level, lifepoint total, and discipline level is stated in
# the "Squad Races" section, and "All squads cost 100 investment credits to
# recruit. You must have 10 squads (of any race) to start a game."
MOBILISING_ARMIES_SQUAD_CREDIT_COST = 100
MOBILISING_ARMIES_SQUAD_CONTRACT_CAP = 10
MOBILISING_ARMIES_SQUADS_REQUIRED = 10


@dataclass(frozen=True)
class MobilisingArmiesSquad:
    id: str
    display_name: str
    race: str
    squad_class: str
    combat_level: int
    lifepoints: int
    discipline: int


MOBILISING_ARMIES_SQUADS = (
    MobilisingArmiesSquad("light_elf", "Light elf", "elf", "light", 225, 4_800, 60),
    MobilisingArmiesSquad("heavy_elf", "Heavy elf", "elf", "heavy", 350, 9_600, 110),
    MobilisingArmiesSquad("light_dwarf", "Light dwarf", "dwarf", "light", 175, 5_300, 60),
    MobilisingArmiesSquad("heavy_dwarf", "Heavy dwarf", "dwarf", "heavy", 350, 10_100, 60),
    MobilisingArmiesSquad("light_goblin", "Light goblin", "goblin", "light", 175, 4_800, 110),
    MobilisingArmiesSquad("heavy_goblin", "Heavy goblin", "goblin", "heavy", 400, 9_600, 60),
)
MOBILISING_ARMIES_SQUADS_BY_ID = {squad.id: squad for squad in MOBILISING_ARMIES_SQUADS}
MOBILISING_ARMIES_SQUAD_IDS = tuple(squad.id for squad in MOBILISING_ARMIES_SQUADS)

# Exact: "Dwarves use Melee, Goblins use Ranged and Elves use Magic. This means
# that Dwarves are more effective against Goblins, which in turn are more
# effective against Elves." Elves close the triangle against Dwarves.
MOBILISING_ARMIES_RACE_STYLE = {"dwarf": "melee", "goblin": "ranged", "elf": "magic"}
MOBILISING_ARMIES_RACE_BEATS = {"dwarf": "goblin", "goblin": "elf", "elf": "dwarf"}

# Exact: only these three races find these three kinds of treasure while
# exploring, and the elf line names white berries directly.
# PLACEHOLDER(mobilising_armies.explore_outcomes): which race finds the
# unattributed rows of the article's loot list (Coins, Pure essence, the three
# uncut gems), how often exploring finds anything at all, and how large the POS
# and NEG effects are. The article lists the loot pool and says a POS effect can
# grant health while a NEG effect costs combat levels, but gives no rates. A
# period server explore table would settle all of it. The healing figure below
# is the one exact number in the area: the Conflict page's "healing potions that
# heal five Hitpoints", read on the pre-EOC ten-times lifepoint scale.
MOBILISING_ARMIES_EXPLORE_LOOT = {
    "dwarf": ("Tin ore", "Coal", "Uncut opal", "Uncut jade", "Uncut red topaz", "Coins"),
    "elf": ("Willow logs", "White berries"),
    "goblin": ("Cabbage seed", "Tomato seed", "Pure essence", "Coins"),
}
MOBILISING_ARMIES_EXPLORE_LOOT_CHANCE = 0.5
MOBILISING_ARMIES_EXPLORE_POSITIVE_CHANCE = 0.25
MOBILISING_ARMIES_EXPLORE_HEAL_LIFEPOINTS = 50
MOBILISING_ARMIES_EXPLORE_NEGATIVE_COMBAT_LOSS = 10


# --- Special units ----------------------------------------------------------
#
# Exact damage bands and exact friendly-fire flags from the "Special Units"
# section; each entry there ends with "It affects your squads too!" except the
# Glider. "Players can buy up to five special units."
# PLACEHOLDER(mobilising_armies.special_unit_credit_cost): the Special Units
# tent's price. The article says investment credits buy units for the armies but
# never prices them, and neither emulator implements the tent. The squad price
# stands in. A period shop table would settle it.
MOBILISING_ARMIES_SPECIAL_UNIT_CAP = 5
MOBILISING_ARMIES_SPECIAL_UNIT_CREDIT_COST = 100


@dataclass(frozen=True)
class MobilisingArmiesSpecialUnit:
    id: str
    display_name: str
    description: str
    minimum_damage: int
    maximum_damage: int
    targets: str
    friendly_fire: bool


MOBILISING_ARMIES_SPECIAL_UNITS = (
    MobilisingArmiesSpecialUnit(
        "chompa",
        "Chompa",
        "Hits multiple targets and your own squads too.",
        50,
        1_000,
        "multiple",
        True,
    ),
    MobilisingArmiesSpecialUnit(
        "cannon",
        "Cannon",
        "Hits every target in the attack line, your own squads included.",
        55,
        1_500,
        "line",
        True,
    ),
    MobilisingArmiesSpecialUnit(
        "glider",
        "Glider",
        "A single strike on one enemy squad; your own squads are safe.",
        4_000,
        4_000,
        "single",
        False,
    ),
    MobilisingArmiesSpecialUnit(
        "distractor",
        "Distractor",
        "Disables all orders to nearby squads, yours as well.",
        0,
        0,
        "orders",
        True,
    ),
    MobilisingArmiesSpecialUnit(
        "barricade",
        "Barricade",
        "Stops all attacks from one direction, including your own.",
        0,
        0,
        "direction",
        True,
    ),
)
MOBILISING_ARMIES_SPECIAL_UNITS_BY_ID = {
    unit.id: unit for unit in MOBILISING_ARMIES_SPECIAL_UNITS
}
MOBILISING_ARMIES_SPECIAL_UNIT_IDS = tuple(
    unit.id for unit in MOBILISING_ARMIES_SPECIAL_UNITS
)


# --- Formations -------------------------------------------------------------
#
# Exact: the nine formations and their rank requirements are a table in the
# "Squad Formations" section.
MOBILISING_ARMIES_FORMATIONS = (
    ("wedge", "Wedge", 0),
    ("wall", "Wall", 0),
    ("flank", "Flank", 0),
    ("eager", "Eager", 51),
    ("spread", "Spread", 101),
    ("lefty", "Lefty", 201),
    ("righty", "Righty", 201),
    ("block", "Block", 301),
    ("grid", "Grid", 401),
)
MOBILISING_ARMIES_FORMATION_IDS = tuple(row[0] for row in MOBILISING_ARMIES_FORMATIONS)
MOBILISING_ARMIES_FORMATION_RANKS = {row[0]: row[2] for row in MOBILISING_ARMIES_FORMATIONS}


# --- Rank ladder ------------------------------------------------------------
#
# Exact: the rank table in the Rewards article gives every band, its maximum
# investment, and its reward modifier as a percentage.
@dataclass(frozen=True)
class MobilisingArmiesRankBand:
    minimum_rank: int
    prefix: str
    maximum_investment: int
    reward_modifier_pct: int


MOBILISING_ARMIES_RANK_BANDS = (
    MobilisingArmiesRankBand(0, "Junior Cadet", 10_000, 110),
    MobilisingArmiesRankBand(100, "Sergeant", 12_500, 120),
    MobilisingArmiesRankBand(200, "Commander", 15_000, 130),
    MobilisingArmiesRankBand(300, "War-Chief", 17_500, 140),
    MobilisingArmiesRankBand(400, "", 20_000, 150),
)


def mobilising_armies_rank_band_pure(rank: int) -> MobilisingArmiesRankBand:
    band = MOBILISING_ARMIES_RANK_BANDS[0]
    for candidate in MOBILISING_ARMIES_RANK_BANDS:
        if int(rank) >= candidate.minimum_rank:
            band = candidate
    return band


# Exact: "The winning player receives +2 rank, any player that did not forfeit
# the game receives +1 rank. In the event that time runs out, all players receive
# +1 rank. Players need to do at least 10 actions (not walking or exploring) to
# get their ranks. The game must last at least 3 minutes ... A maximum of 12
# ranks can be gained per hour".
MOBILISING_ARMIES_RANK_FOR_WIN = 2
MOBILISING_ARMIES_RANK_FOR_PARTICIPATION = 1
MOBILISING_ARMIES_RANK_ACTION_MINIMUM = 10
MOBILISING_ARMIES_RANK_HOURLY_CAP = 12
MOBILISING_ARMIES_SCENARIO_MINUTES = 30
MOBILISING_ARMIES_RANK_MINIMUM_MINUTES = 3

# One review beat is one squad order. A thirty-minute scenario becomes eighteen
# beats, the same disclosed event-scaled translation Soul Wars uses for its
# twenty-minute match, so the sourced ten-order rank gate stays a real gate the
# player can miss. This is a translation of review cadence, not a claim about a
# period rate.
MOBILISING_ARMIES_SCENARIO_BEATS = 18
MOBILISING_ARMIES_RANK_MINIMUM_BEATS = (
    MOBILISING_ARMIES_SCENARIO_BEATS
    * MOBILISING_ARMIES_RANK_MINIMUM_MINUTES
    // MOBILISING_ARMIES_SCENARIO_MINUTES
) + 1

# PLACEHOLDER(mobilising_armies.rank_window_reviews): the hourly rank cap is
# exact at twelve, but AnkiScape has no wall clock inside the review loop, so the
# hour becomes a rolling window of thirty-six review beats — two full scenarios,
# which is one hour of scenario time. A real-time clock in the review loop would
# replace the window.
MOBILISING_ARMIES_RANK_WINDOW_BEATS = MOBILISING_ARMIES_SCENARIO_BEATS * 2


# --- Scenarios --------------------------------------------------------------
#
# Exact: the four scenario names, their unlock chain ("Siege requires you to play
# a game of Conflict, Hoard requires you to play a game of Siege, and Rescue
# requires you to play a game of Hoard"), and each primary objective and its
# target. Conflict eliminates every enemy squad, Siege breaks one of four castle
# walls, Hoard steals 100,000 gold, Rescue saves 28 TzHaar. "Defeating all enemy
# squads is always an objective."
#
# PLACEHOLDER(mobilising_armies.objective_rates): how much one squad order moves
# an objective, how fast the rival army moves its own, and how many catapult
# shots breach a wall. The sources give the targets and the discrete costs around
# them but never a rate. Each rate below is the value that makes the sourced
# target reachable inside the eighteen-beat scenario without making it free. A
# period scenario controller would replace them.
@dataclass(frozen=True)
class MobilisingArmiesScenario:
    id: str
    display_name: str
    description: str
    unlocked_by: str
    objective: str
    objective_label: str
    objective_target: int
    objective_per_order: int
    opponent_per_beat: int


MOBILISING_ARMIES_SCENARIOS = (
    MobilisingArmiesScenario(
        "conflict",
        "Conflict",
        "A free-for-all: defeat every enemy squad.",
        "",
        "squads_defeated",
        "Enemy squads defeated",
        MOBILISING_ARMIES_SQUADS_REQUIRED,
        0,
        1,
    ),
    MobilisingArmiesScenario(
        "siege",
        "Siege",
        "Breach a castle wall with a catapult or a direct assault.",
        "conflict",
        "wall_breach",
        "Castle wall breached",
        100,
        0,
        6,
    ),
    MobilisingArmiesScenario(
        "hoard",
        "Hoard",
        "Steal 100,000 gold from the sleeping dragon's caves.",
        "siege",
        "gold",
        "Dragon gold stolen",
        100_000,
        8_000,
        6_000,
    ),
    MobilisingArmiesScenario(
        "rescue",
        "Rescue",
        "Save 28 TzHaar from the fissures before your rivals do.",
        "hoard",
        "tzhaar",
        "TzHaar rescued",
        28,
        2,
        2,
    ),
)
MOBILISING_ARMIES_SCENARIOS_BY_ID = {
    scenario.id: scenario for scenario in MOBILISING_ARMIES_SCENARIOS
}
MOBILISING_ARMIES_SCENARIO_IDS = tuple(
    scenario.id for scenario in MOBILISING_ARMIES_SCENARIOS
)

# Exact: Siege's catapult needs four parts — "wheels, wood, rope and limbs" — and
# then "4 rocks from the rockpiles" per automatic shot. The shot count that
# breaches a wall, and the wall damage one squad assault deals, belong to
# `mobilising_armies.objective_rates`.
MOBILISING_ARMIES_SIEGE_CATAPULT_PARTS = 4
MOBILISING_ARMIES_SIEGE_ROCKS_PER_SHOT = 4
MOBILISING_ARMIES_SIEGE_SHOT_WALL_DAMAGE = 50
MOBILISING_ARMIES_SIEGE_ASSAULT_WALL_DAMAGE = 10
MOBILISING_ARMIES_SIEGE_TOWER_DAMAGE = 900
MOBILISING_ARMIES_SIEGE_ROUTES = (
    ("catapult", "Build a catapult and feed it rocks"),
    ("assault", "Attack the wall directly under tower fire"),
)
MOBILISING_ARMIES_SIEGE_ROUTE_IDS = tuple(row[0] for row in MOBILISING_ARMIES_SIEGE_ROUTES)

# Exact Hoard gold rules: "if one of your squads is defeated while having the
# Collect order on ... you'll lose 5000 gold", "You also lose 500 gold when
# attacked from time to time", and "If you defeat a collecting squad you'll earn
# 2500 gold".
MOBILISING_ARMIES_HOARD_LOSS_ON_SQUAD_DEATH = 5_000
MOBILISING_ARMIES_HOARD_LOSS_ON_ATTACK = 500
MOBILISING_ARMIES_HOARD_GAIN_ON_KILL = 2_500

# Exact: Rescue lets a player "steal TzHaar from other player's landers". The
# amount one steal order takes belongs to `mobilising_armies.objective_rates`.
MOBILISING_ARMIES_RESCUE_STEAL_PER_ORDER = 2

# PLACEHOLDER(mobilising_armies.squad_combat_resolution): damage one squad order
# deals, the sourced triangle/terrain/first-strike/rear-attack bonuses, and how
# hard the rival army hits back. The article states that all four bonuses exist
# and that special terrain is 2x2 but gives no numbers, and the Conflict page
# only says stacking on special terrain lets troops "hit up to double the
# damage" — which is the multiplier below. A period combat controller would
# settle the base figures.
#
# An order is not one swing. In the source a squad ordered to attack keeps
# fighting until it is re-ordered, so one beat's order is a sustained engagement.
# These two figures are calibrated against the sourced lifepoint roster so that
# the article's own strategic advice is the advice that works here:
#   - clearing ten rival squads inside eighteen beats needs the combat triangle,
#     which is what the whole roster is built around;
#   - light rival squads fall in one ordered engagement and heavy ones need two,
#     which is why the Conflict page says to target the light squads;
#   - a light squad of your own survives two or three rival beats, so the light
#     class stays viable in Siege and Rescue exactly as the article says, while
#     an army left idle is still wiped out before the clock runs out.
MOBILISING_ARMIES_SQUAD_ORDER_DAMAGE = 3_000
MOBILISING_ARMIES_TRIANGLE_MULTIPLIER = 2.0
MOBILISING_ARMIES_OPPONENT_ORDER_DAMAGE = 2_400

MOBILISING_ARMIES_ORDERS = (
    ("objective", "Push the scenario objective"),
    ("attack", "Attack the enemy squads"),
    ("explore", "Explore for treasure"),
)
MOBILISING_ARMIES_ORDER_IDS = tuple(row[0] for row in MOBILISING_ARMIES_ORDERS)


# --- Reward credits ---------------------------------------------------------
#
# Exact formula from the Rewards article: "100 + max[0, timeBonus +
# killCountBonus + investment * rankModifier * endConditionModifier / 10000]",
# with "The kill count bonus is the number of kills times 70." The two modifiers
# are the integer percentages of the rank table and the end-condition list, and
# the /10000 is the two percent divisions. End conditions are sourced on the
# Siege example — 150% for breaking the wall, 120% for killing everyone, 100% for
# losing — and applied across the scenarios, which is why Conflict's elimination
# win takes the primary-objective modifier: elimination is its only win.
MOBILISING_ARMIES_REWARD_BASE = 100
MOBILISING_ARMIES_REWARD_PER_KILL = 70
MOBILISING_ARMIES_END_PRIMARY_PCT = 150
MOBILISING_ARMIES_END_ELIMINATION_PCT = 120
MOBILISING_ARMIES_END_LOSS_PCT = 100

# PLACEHOLDER(mobilising_armies.reward_time_bonus_curve): "The time bonus gets
# larger the longer you survive, it can also be negative if you die too
# quickly." The direction and the sign change are exact; the curve is not. A
# straight line through the three-minute rank threshold reproduces both, at a
# scale comparable to the exact kill bonus. A period reward routine would settle
# the real curve.
MOBILISING_ARMIES_TIME_BONUS_PER_BEAT = 40


def mobilising_armies_reward_credits_pure(
    *,
    beats_survived: int,
    kills: int,
    investment: int,
    rank_modifier_pct: int,
    end_condition_pct: int,
) -> int:
    time_bonus = (
        int(beats_survived) - MOBILISING_ARMIES_RANK_MINIMUM_BEATS
    ) * MOBILISING_ARMIES_TIME_BONUS_PER_BEAT
    kill_bonus = int(kills) * MOBILISING_ARMIES_REWARD_PER_KILL
    staked = int(investment) * int(rank_modifier_pct) * int(end_condition_pct) // 10_000
    return MOBILISING_ARMIES_REWARD_BASE + max(0, time_bonus + kill_bonus + staked)


# --- Officer Tower ----------------------------------------------------------
#
# Exact: four floors gated at rank 0, 100, 200 and 300; every reward-credit
# price; the Spoils of War price per floor and the three-of-five draw ("Players
# may choose three of the following items at the cost of 10K reward credits, a
# maximum of five items will display at one time"); and the refund rates ("quest
# kits and locators are refunded for 80% of the cost while the uniforms are
# refunded for 100%"). The sources state no refund for imbued rings, so none is
# offered.
MOBILISING_ARMIES_SPOILS_CHOICES = 3
MOBILISING_ARMIES_SPOILS_OFFER_SIZE = 5
MOBILISING_ARMIES_KIT_REFUND_PCT = 80
MOBILISING_ARMIES_LOCATOR_REFUND_PCT = 80
MOBILISING_ARMIES_UNIFORM_REFUND_PCT = 100


@dataclass(frozen=True)
class MobilisingArmiesFloor:
    id: str
    display_name: str
    quartermaster: str
    minimum_rank: int
    spoils_cost: int
    prefix: str


MOBILISING_ARMIES_FLOORS = (
    MobilisingArmiesFloor("basement", "Basement", "Serjeant Cole", 0, 10_000, "Junior Cadet"),
    MobilisingArmiesFloor("ground", "Ground floor", "Commander Loman", 100, 30_000, "Serjeant"),
    MobilisingArmiesFloor("first", "First floor", "War-chief Reeves", 200, 50_000, "Commander"),
    MobilisingArmiesFloor("second", "Second floor", "Lord Marshal Brogan", 300, 80_000, "War-Chief"),
)
MOBILISING_ARMIES_FLOORS_BY_ID = {floor.id: floor for floor in MOBILISING_ARMIES_FLOORS}
MOBILISING_ARMIES_FLOOR_IDS = tuple(floor.id for floor in MOBILISING_ARMIES_FLOORS)
MOBILISING_ARMIES_PREFIXES = tuple(floor.prefix for floor in MOBILISING_ARMIES_FLOORS)

# Exact per-floor Spoils of War tables. Where the source gives a range ("93-94
# Iron ore") the lower bound ships, because the article explains the spread as
# live Grand Exchange rounding rather than two different rewards.
MOBILISING_ARMIES_SPOILS = {
    "basement": (
        ("Tin ore", 79),
        ("Pure essence", 21),
        ("Raw bass", 7),
        ("Bronze bar", 18),
        ("Grimy tarromin", 10),
        ("Grimy marrentill", 12),
        ("Guam seed", 1_111),
        ("Tomato seed", 3_333),
        ("Oak logs", 90),
        ("Copper ore", 45),
    ),
    "ground": (
        ("Iron ore", 93),
        ("Coal", 49),
        ("Raw lobster", 26),
        ("Oak logs", 322),
        ("Willow logs", 555),
        ("Iron bar", 38),
        ("Steel bar", 14),
        ("Grimy tarromin", 30),
        ("Grimy harralander", 12),
        ("Grimy ranarr", 1),
        ("Pure essence", 64),
        ("Coins", 10_000),
        ("Jute seed", 400),
    ),
    "first": (
        ("Coal", 78),
        ("Willow logs", 925),
        ("Teak logs", 114),
        ("Pure essence", 107),
        ("Raw tuna", 134),
        ("Steel bar", 23),
        ("Grimy ranarr", 1),
        ("Grimy toadflax", 7),
        ("Sweetcorn seed", 26),
        ("Orange tree seed", 43),
        ("Coins", 16_666),
    ),
    "second": (
        ("Pure essence", 165),
        ("Coal", 126),
        ("Steel bar", 37),
        ("Mithril bar", 19),
        ("Willow logs", 1_481),
        ("Maple logs", 666),
        ("Grimy avantoe", 26),
        ("Grimy kwuarm", 7),
        ("Raw shark", 19),
        ("Toadflax seed", 27),
        ("Curry tree seed", 11),
        ("Pineapple seed", 1),
        ("Cactus seed", 213),
        ("Coins", 26_666),
    ),
}


@dataclass(frozen=True)
class MobilisingArmiesQuestKit:
    item_name: str
    item_id: int
    floor: str
    credit_cost: int
    contents: tuple[str, ...]


# Exact contents, cumulative as the Quest kit article states them. The article's
# "Oil lamp" and "Bullseye lantern" are the unlit registry items, and the elite
# kit's two stated replacements are applied rather than added.
_BASIC_KIT = ("Rope", "Tinderbox", "Spade", "Candle", "Needle", "Pestle and mortar")
_MEDIUM_KIT = _BASIC_KIT + ("Thread", "Bowl", "Bucket", "Bronze pickaxe")
_ADVANCED_KIT = _MEDIUM_KIT + (
    "Oil lamp (unlit)",
    "Machete",
    "Waterskin (4)",
    "Knife",
    "Plank",
)
_ELITE_KIT = tuple(
    item
    for item in _ADVANCED_KIT
    if item not in {"Bronze pickaxe", "Oil lamp (unlit)"}
) + ("Hammer", "Saw", "Steel hatchet", "Chisel", "Steel pickaxe", "Bullseye lantern (unlit)")

MOBILISING_ARMIES_QUEST_KITS = (
    MobilisingArmiesQuestKit("Quest kit (basic)", 15_001, "basement", 61_900, _BASIC_KIT),
    MobilisingArmiesQuestKit("Quest kit (medium)", 15_002, "ground", 119_400, _MEDIUM_KIT),
    MobilisingArmiesQuestKit("Quest kit (advanced)", 15_003, "first", 176_700, _ADVANCED_KIT),
    MobilisingArmiesQuestKit("Quest kit (elite)", 15_004, "second", 267_700, _ELITE_KIT),
)
MOBILISING_ARMIES_QUEST_KITS_BY_ITEM = {
    kit.item_name: kit for kit in MOBILISING_ARMIES_QUEST_KITS
}


@dataclass(frozen=True)
class MobilisingArmiesLocator:
    item_name: str
    item_id: int
    floor: str
    credit_cost: int
    ore_targets: tuple[str, ...]
    tree_targets: tuple[str, ...]
    fishing_targets: tuple[str, ...]


# Exact destination lists from the Locator article, cumulative by tier and
# restricted to resources AnkiScape already gathers. The article's Herblore
# secondary destinations and its Eucalyptus trees have no gathering target yet,
# so those rows are deferred catalog depth rather than a placeholder.
_INFERIOR_ORES = ("tin", "copper", "iron")
_INFERIOR_TREES = ("oak", "willow")
_INFERIOR_FISH = ("catch_shrimp_anchovies",)
_POOR_ORES = _INFERIOR_ORES + ("clay", "silver")
_POOR_TREES = _INFERIOR_TREES + ("maple", "teak", "achey")
_POOR_FISH = _INFERIOR_FISH + ("catch_lobsters",)
_GOOD_ORES = _POOR_ORES + ("gold", "mithril")
_GOOD_TREES = _POOR_TREES + ("yew",)
_SUPERIOR_ORES = _GOOD_ORES + ("adamantite", "runite")
_SUPERIOR_TREES = _GOOD_TREES + ("magic",)

MOBILISING_ARMIES_LOCATORS = (
    MobilisingArmiesLocator(
        "Inferior locator", 15_005, "basement", 24_700,
        _INFERIOR_ORES, _INFERIOR_TREES, _INFERIOR_FISH,
    ),
    MobilisingArmiesLocator(
        "Poor locator", 15_006, "ground", 44_800,
        _POOR_ORES, _POOR_TREES, _POOR_FISH,
    ),
    MobilisingArmiesLocator(
        "Good locator", 15_007, "first", 70_600,
        _GOOD_ORES, _GOOD_TREES, _POOR_FISH,
    ),
    MobilisingArmiesLocator(
        "Superior locator", 15_008, "second", 102_900,
        _SUPERIOR_ORES, _SUPERIOR_TREES, _POOR_FISH,
    ),
)
MOBILISING_ARMIES_LOCATORS_BY_ITEM = {
    locator.item_name: locator for locator in MOBILISING_ARMIES_LOCATORS
}
MOBILISING_ARMIES_LOCATOR_SKILLS = (
    ("mining", "Mining rocks"),
    ("woodcutting", "Trees"),
    ("fishing", "Fishing spots"),
)
MOBILISING_ARMIES_LOCATOR_SKILL_IDS = tuple(
    row[0] for row in MOBILISING_ARMIES_LOCATOR_SKILLS
)
MOBILISING_ARMIES_LOCATOR_TARGET_KEYS = {
    "mining": "current_ore",
    "woodcutting": "current_tree",
    "fishing": "current_fishing",
}


@dataclass(frozen=True)
class MobilisingArmiesUniform:
    item_name: str
    item_id: int
    floor: str
    slot: str
    credit_cost: int


# The Serjeant set is the breadth-one uniform family: six pieces, one per slot,
# exact prices, and the Serjeant top revision states outright that it "does not
# give any stat bonuses", which game-main's empty equipment blocks corroborate.
# The Commander, War-chief and Lord Marshal sets are the same mechanic at higher
# rank gates and stay deferred catalog depth; the quest kits, locators and imbued
# rings already prove every floor's gate.
MOBILISING_ARMIES_UNIFORMS = (
    MobilisingArmiesUniform("Serjeant cap", 15_336, "basement", "head", 37_100),
    MobilisingArmiesUniform("Serjeant top", 15_022, "basement", "body", 49_500),
    MobilisingArmiesUniform("Serjeant trousers", 15_023, "basement", "legs", 49_500),
    MobilisingArmiesUniform("Serjeant skirt", 15_024, "basement", "legs", 49_500),
    MobilisingArmiesUniform("Serjeant boots", 15_025, "basement", "feet", 37_100),
    MobilisingArmiesUniform("Serjeant gloves", 15_026, "basement", "hands", 37_100),
)
MOBILISING_ARMIES_UNIFORMS_BY_ITEM = {
    piece.item_name: piece for piece in MOBILISING_ARMIES_UNIFORMS
}


@dataclass(frozen=True)
class MobilisingArmiesImbueRing:
    base_item: str
    item_name: str
    item_id: int
    floor: str
    credit_cost: int
    bonuses: EquipmentBonuses


# Exact prices from the Rewards article and exact bonus blocks from game-main
# items.yml. The five period rings whose *base* item AnkiScape does not stock yet
# — Lunar, Seers', Warrior's, Archer's and Berserker — are deferred until those
# families ship; every floor is still covered.
MOBILISING_ARMIES_IMBUE_RINGS = (
    MobilisingArmiesImbueRing(
        "Gold ring", "Gold ring (i)", 15_009, "basement", 37_100,
        EquipmentBonuses(
            defence_stab=1, defence_slash=1, defence_crush=1,
            defence_magic=1, defence_ranged=1,
        ),
    ),
    MobilisingArmiesImbueRing(
        "Sapphire ring", "Sapphire ring (i)", 15_010, "ground", 74_600,
        EquipmentBonuses(
            defence_stab=1, defence_slash=1, defence_crush=2,
            defence_magic=1, defence_ranged=1,
        ),
    ),
    MobilisingArmiesImbueRing(
        "Emerald ring", "Emerald ring (i)", 15_011, "ground", 89_600,
        EquipmentBonuses(
            defence_stab=3, defence_slash=2, defence_crush=2,
            defence_magic=2, defence_ranged=2,
        ),
    ),
    MobilisingArmiesImbueRing(
        "Ruby ring", "Ruby ring (i)", 15_012, "ground", 89_600,
        EquipmentBonuses(
            attack_stab=3, attack_slash=3, attack_crush=4,
            attack_magic=3, attack_ranged=3,
        ),
    ),
    MobilisingArmiesImbueRing(
        "Diamond ring", "Diamond ring (i)", 15_013, "ground", 89_600,
        EquipmentBonuses(
            attack_stab=5, attack_slash=4, attack_crush=4,
            attack_magic=4, attack_ranged=4,
        ),
    ),
    MobilisingArmiesImbueRing(
        "Dragonstone ring", "Dragonstone ring (i)", 15_014, "first", 141_300,
        EquipmentBonuses(
            attack_stab=5, attack_slash=5, attack_crush=5,
            attack_magic=5, attack_ranged=5,
            defence_stab=5, defence_slash=5, defence_crush=5,
            defence_magic=5, defence_ranged=5,
        ),
    ),
    MobilisingArmiesImbueRing(
        "Ring of charos (a)", "Ring of charos (a)(i)", 15_016, "first", 106_000,
        EquipmentBonuses(
            defence_stab=4, defence_slash=4, defence_crush=4,
            defence_magic=4, defence_ranged=4,
        ),
    ),
    MobilisingArmiesImbueRing(
        "Onyx ring", "Onyx ring (i)", 15_017, "second", 144_100,
        EquipmentBonuses(
            attack_stab=6, attack_slash=6, attack_crush=6,
            attack_magic=6, attack_ranged=6,
            defence_stab=6, defence_slash=6, defence_crush=6,
            defence_magic=6, defence_ranged=6,
        ),
    ),
)
MOBILISING_ARMIES_IMBUE_RINGS_BY_ITEM = {
    ring.item_name: ring for ring in MOBILISING_ARMIES_IMBUE_RINGS
}


MOBILISING_ARMIES_ASSET_MANIFEST = (
    {
        "item_name": "Mobilising Armies",
        "wiki_title": "Mobilising Armies standard.png",
        "output_path": "activityicons/mobilising_armies.png",
        "size": 64,
    },
    *(
        {
            "item_name": item_name,
            "wiki_title": f"{item_name}.png",
            "output_path": "activityitems/mobilising_armies_"
            + item_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
            + ".png",
            "size": 64,
        }
        for item_name in (
            tuple(kit.item_name for kit in MOBILISING_ARMIES_QUEST_KITS)
            + tuple(locator.item_name for locator in MOBILISING_ARMIES_LOCATORS)
            + tuple(piece.item_name for piece in MOBILISING_ARMIES_UNIFORMS)
            + tuple(
                ring.item_name
                for ring in MOBILISING_ARMIES_IMBUE_RINGS
                if ring.item_name != "Ring of charos (a)(i)"
            )
        )
    ),
)


def mobilising_armies_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        MOBILISING_ARMIES_ACTIVITY_ID: {
            "display_name": "Mobilising Armies",
            "requirements": {},
            "skill_requirements": {},
            "outputs": (),
            "batch_size": 1,
            "group": "minigames",
            "source": MOBILISING_ARMIES_SOURCE,
        }
    }


# Werewolf Skullball already registers the imbued Ring of charos and its art, so
# this family sells that row without re-registering it.
MOBILISING_ARMIES_PREREGISTERED_ITEMS = frozenset({"Ring of charos (a)(i)"})


def _reward_item_rows() -> tuple[tuple[str, int, str | None, bool], ...]:
    """Every registry row this family owns: name, cache id, slot, stackable."""
    return (
        *((kit.item_name, kit.item_id, None, False) for kit in MOBILISING_ARMIES_QUEST_KITS),
        *(
            (locator.item_name, locator.item_id, None, False)
            for locator in MOBILISING_ARMIES_LOCATORS
        ),
        *(
            (piece.item_name, piece.item_id, piece.slot, False)
            for piece in MOBILISING_ARMIES_UNIFORMS
        ),
        *(
            (ring.item_name, ring.item_id, "ring", False)
            for ring in MOBILISING_ARMIES_IMBUE_RINGS
            if ring.item_name not in MOBILISING_ARMIES_PREREGISTERED_ITEMS
        ),
    )


def mobilising_armies_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        item_name: {
            "category": "equipment" if slot else "activity",
            "source_item_id": item_id,
            "stackable": stackable,
            # Every Officer Tower reward carries a "You'll have to buy another
            # from the Mobilising Armies Command Centre" destroy message and the
            # item pages list them as untradeable.
            "tradeable": False,
            **({"equipment_slot": slot} if slot else {}),
            "source": MOBILISING_ARMIES_SOURCE,
        }
        for item_name, item_id, slot, stackable in _reward_item_rows()
    }


def mobilising_armies_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    uniforms = {
        piece.item_name: EquipmentItem(
            item_name=piece.item_name,
            slot=piece.slot,
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="arms_uniform",
            bonuses=EquipmentBonuses(),
            attack_speed=4,
            source_item_id=piece.item_id,
            source=MOBILISING_ARMIES_SOURCE,
            source_status="pinned pre-cutoff item revision; stated to give no bonuses",
            skill_requirements=(),
            weapon_type=-1,
        )
        for piece in MOBILISING_ARMIES_UNIFORMS
    }
    rings = {
        ring.item_name: EquipmentItem(
            item_name=ring.item_name,
            slot="ring",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="imbued_ring",
            bonuses=ring.bonuses,
            attack_speed=4,
            source_item_id=ring.item_id,
            source=MOBILISING_ARMIES_SOURCE,
            source_status="exact game-main items.yml bonus block",
            skill_requirements=(),
            weapon_type=-1,
        )
        for ring in MOBILISING_ARMIES_IMBUE_RINGS
        if ring.item_name not in MOBILISING_ARMIES_PREREGISTERED_ITEMS
    }
    return {**uniforms, **rings}
