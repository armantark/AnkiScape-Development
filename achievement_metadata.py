"""Pure achievement metadata and grouping helpers.

The persisted achievement contract is the display name stored in
``player_data["completed_achievements"]``. Keep those strings stable; this
module only moves the definitions out of the mixed constants/UI layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence


PlayerData = Mapping[str, Any]
AchievementCondition = Callable[[PlayerData], bool]

ACHIEVEMENT_DIFFICULTIES: tuple[str, ...] = (
    "Easy",
    "Moderate",
    "Difficult",
    "Very Challenging",
)


@dataclass(frozen=True)
class AchievementDefinition:
    name: str
    description: str
    difficulty: str
    condition: AchievementCondition

    def as_legacy_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "difficulty": self.difficulty,
            "condition": self.condition,
        }


@dataclass(frozen=True)
class AchievementRow:
    name: str
    description: str
    difficulty: str
    completed: bool


def _inventory(player: PlayerData) -> Mapping[str, Any]:
    inventory = player.get("inventory", {})
    return inventory if isinstance(inventory, Mapping) else {}


def _item_count(player: PlayerData, item_name: str) -> int:
    value = _inventory(player).get(item_name, 0)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _inventory_total(player: PlayerData, items: Iterable[str]) -> int:
    return sum(_item_count(player, item_name) for item_name in items)


def _has_each(player: PlayerData, items: Iterable[str], amount: int) -> bool:
    return all(_item_count(player, item_name) >= amount for item_name in items)


def _level(player: PlayerData, key: str, default: int = 1) -> int:
    value = player.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _completed_achievement_count(player: PlayerData) -> int:
    completed = player.get("completed_achievements", ())
    return len(completed) if isinstance(completed, Sequence) else 0


def _quest_completed(player: PlayerData, quest_id: str) -> bool:
    quests = player.get("quests", {}) or {}
    if not isinstance(quests, Mapping):
        return False
    quest = quests.get(quest_id, {}) or {}
    return isinstance(quest, Mapping) and bool(quest.get("completed", False))


def _claim_completed(player: PlayerData, claim_id: str) -> bool:
    claims = player.get("claims", {}) or {}
    if not isinstance(claims, Mapping):
        return False
    claim = claims.get(claim_id, {}) or {}
    return isinstance(claim, Mapping) and bool(claim.get("claimed", False))


FARMING_LEVEL_ACHIEVEMENTS = (
    ("Novice Farmer", 10, "Easy"),
    ("Intermediate Farmer", 30, "Moderate"),
    ("Expert Farmer", 60, "Difficult"),
    ("Master Farmer", 99, "Very Challenging"),
)

FARMING_PRODUCE_ACHIEVEMENTS = (
    ("Produce Collector", 100, "Easy"),
    ("Produce Hoarder", 1_000, "Moderate"),
    ("Produce Stockpile", 10_000, "Difficult"),
)


def _farming_counter(player: PlayerData, key: str) -> int:
    counters = player.get("farming_counters", {}) or {}
    if not isinstance(counters, Mapping):
        return 0
    try:
        return max(0, int(counters.get(key, 0) or 0))
    except (TypeError, ValueError):
        return 0


def _agility_counter(player: PlayerData, key: str) -> int:
    counters = player.get("agility_lap_counts", {}) or {}
    return _level(counters, key, 0) if isinstance(counters, Mapping) else 0


def _has_completed_agility_activity_families(
    player: PlayerData,
    required_families: Iterable[str],
) -> bool:
    completions = player.get("agility_activity_completions", {}) or {}
    if not isinstance(completions, Mapping):
        return False
    return all(
        _level({"value": completions.get(family)}, "value", 0) > 0
        for family in required_families
    )


def _owns_or_equipped(player: PlayerData, item_name: str) -> bool:
    equipment = player.get("equipment", {}) or {}
    return _item_count(player, item_name) > 0 or (
        isinstance(equipment, Mapping) and item_name in equipment.values()
    )


def build_achievement_definitions(
    mining_output_items: Iterable[str],
    woodcutting_log_items: Iterable[str],
    gem_items: Iterable[str],
    runecrafting_output_items: Iterable[str],
    bar_items: Iterable[str],
    fishing_output_items: Iterable[str],
    hunter_output_items: Iterable[str],
    herblore_finished_items: Iterable[str],
    agility_activity_families: Iterable[str],
) -> tuple[AchievementDefinition, ...]:
    mining_output_items = tuple(mining_output_items)
    woodcutting_log_items = tuple(woodcutting_log_items)
    gem_items = tuple(gem_items)
    runecrafting_output_items = tuple(runecrafting_output_items)
    bar_items = tuple(bar_items)
    fishing_output_items = tuple(fishing_output_items)
    hunter_output_items = tuple(hunter_output_items)
    herblore_finished_items = tuple(herblore_finished_items)
    agility_activity_families = tuple(dict.fromkeys(agility_activity_families))

    definitions: list[AchievementDefinition] = []
    final_count = {"value": 0}

    def add(name: str, description: str, difficulty: str, condition: AchievementCondition) -> None:
        definitions.append(AchievementDefinition(name, description, difficulty, condition))

    add("First Steps", "Mine your first ore", "Easy", lambda player: _inventory_total(player, mining_output_items) > 0)
    add("Novice Miner", "Reach Mining level 10", "Easy", lambda player: _level(player, "mining_level") >= 10)
    add("Ore Collector", "Collect 100 total ores", "Easy", lambda player: _inventory_total(player, mining_output_items) >= 100)
    add("Jack of All Ores", "Mine at least one of each ore type", "Easy", lambda player: _has_each(player, mining_output_items, 1))
    add("Rune Essence Enthusiast", "Mine 500 Rune Essence", "Easy", lambda player: _item_count(player, "Rune essence") >= 500)
    add("Clay Modeler", "Mine 500 Clay", "Easy", lambda player: _item_count(player, "Clay") >= 500)
    add("Copper Collector", "Mine 250 Copper ore", "Easy", lambda player: _item_count(player, "Copper ore") >= 250)
    add("Tin Trader", "Mine 250 Tin ore", "Easy", lambda player: _item_count(player, "Tin ore") >= 250)
    add("Iron Initiate", "Mine 100 Iron ore", "Easy", lambda player: _item_count(player, "Iron ore") >= 100)
    add("Silver Seeker", "Mine 50 Silver ore", "Easy", lambda player: _item_count(player, "Silver ore") >= 50)

    add("Intermediate Miner", "Reach Mining level 30", "Moderate", lambda player: _level(player, "mining_level") >= 30)
    add("Ore Hoarder", "Collect 1,000 total ores", "Moderate", lambda player: _inventory_total(player, mining_output_items) >= 1000)
    add("Coal Connoisseur", "Mine 500 Coal", "Moderate", lambda player: _item_count(player, "Coal") >= 500)
    add("Golden Touch", "Mine 100 Gold ore", "Moderate", lambda player: _item_count(player, "Gold ore") >= 100)
    add("Mithril Mastery", "Mine 250 Mithril ore", "Moderate", lambda player: _item_count(player, "Mithril ore") >= 250)
    add("Adamantite Adept", "Mine 100 Adamantite ore", "Moderate", lambda player: _item_count(player, "Adamantite ore") >= 100)
    add("Runite Rookie", "Mine 50 Runite ore", "Moderate", lambda player: _item_count(player, "Runite ore") >= 50)
    add("Diverse Miner", "Mine 100 of each ore type", "Moderate", lambda player: _has_each(player, mining_output_items, 100))
    add("XP Chaser", "Gain 100,000 total Mining experience", "Moderate", lambda player: float(player.get("mining_exp", 0) or 0) >= 100000)

    add("Expert Miner", "Reach Mining level 60", "Difficult", lambda player: _level(player, "mining_level") >= 60)
    add("Ore Magnate", "Collect 10,000 total ores", "Difficult", lambda player: _inventory_total(player, mining_output_items) >= 10000)
    add("Rune Essence Baron", "Mine 10,000 Rune Essence", "Difficult", lambda player: _item_count(player, "Rune essence") >= 10000)
    add("Clay Empire", "Mine 10,000 Clay", "Difficult", lambda player: _item_count(player, "Clay") >= 10000)
    add("Copper King", "Mine 5,000 Copper ore", "Difficult", lambda player: _item_count(player, "Copper ore") >= 5000)
    add("Tin Tycoon", "Mine 5,000 Tin ore", "Difficult", lambda player: _item_count(player, "Tin ore") >= 5000)
    add("Iron Imperator", "Mine 2,500 Iron ore", "Difficult", lambda player: _item_count(player, "Iron ore") >= 2500)
    add("Silver Sovereign", "Mine 1,000 Silver ore", "Difficult", lambda player: _item_count(player, "Silver ore") >= 1000)
    add("Coal Commander", "Mine 5,000 Coal", "Difficult", lambda player: _item_count(player, "Coal") >= 5000)
    add("Golden Empire", "Mine 1,000 Gold ore", "Difficult", lambda player: _item_count(player, "Gold ore") >= 1000)

    add("Master Miner", "Reach Mining level 99", "Very Challenging", lambda player: _level(player, "mining_level") >= 99)
    add("Ore Tycoon", "Collect 100,000 total ores", "Very Challenging", lambda player: _inventory_total(player, mining_output_items) >= 100000)
    add("Mithril Monarch", "Mine 10,000 Mithril ore", "Very Challenging", lambda player: _item_count(player, "Mithril ore") >= 10000)
    add("Adamantite Overlord", "Mine 5,000 Adamantite ore", "Very Challenging", lambda player: _item_count(player, "Adamantite ore") >= 5000)
    add("Runite Ruler", "Mine 2,500 Runite ore", "Very Challenging", lambda player: _item_count(player, "Runite ore") >= 2500)
    add("Ore Completionist", "Mine 10,000 of each ore type", "Very Challenging", lambda player: _has_each(player, mining_output_items, 10000))
    add("XP Master", "Gain 1,000,000 total Mining experience", "Very Challenging", lambda player: float(player.get("mining_exp", 0) or 0) >= 1000000)

    add("First Chop", "Cut your first log", "Easy", lambda player: _inventory_total(player, woodcutting_log_items) > 0)
    add("Novice Woodcutter", "Reach Woodcutting level 10", "Easy", lambda player: _level(player, "woodcutting_level") >= 10)
    add("Log Collector", "Collect 100 total logs", "Easy", lambda player: _inventory_total(player, woodcutting_log_items) >= 100)
    add("Jack of All Trees", "Cut at least one log from each tree type", "Easy", lambda player: _has_each(player, woodcutting_log_items, 1))
    add("Oak Enthusiast", "Cut 500 Oak logs", "Easy", lambda player: _item_count(player, "Oak logs") >= 500)
    add("Willow Whisperer", "Cut 500 Willow logs", "Easy", lambda player: _item_count(player, "Willow logs") >= 500)

    add("Intermediate Woodcutter", "Reach Woodcutting level 30", "Moderate", lambda player: _level(player, "woodcutting_level") >= 30)
    add("Log Hoarder", "Collect 1,000 total logs", "Moderate", lambda player: _inventory_total(player, woodcutting_log_items) >= 1000)
    add("Maple Master", "Cut 500 Maple logs", "Moderate", lambda player: _item_count(player, "Maple logs") >= 500)
    add("Yew Yeoman", "Cut 250 Yew logs", "Moderate", lambda player: _item_count(player, "Yew logs") >= 250)

    add("Expert Woodcutter", "Reach Woodcutting level 60", "Difficult", lambda player: _level(player, "woodcutting_level") >= 60)
    add("Log Magnate", "Collect 10,000 total logs", "Difficult", lambda player: _inventory_total(player, woodcutting_log_items) >= 10000)
    add("Magic Logger", "Cut 1,000 Magic logs", "Difficult", lambda player: _item_count(player, "Magic logs") >= 1000)

    add("Master Woodcutter", "Reach Woodcutting level 99", "Very Challenging", lambda player: _level(player, "woodcutting_level") >= 99)

    add("Jack of Two Trades", "Reach level 50 in both Mining and Woodcutting", "Moderate", lambda player: _level(player, "mining_level") >= 50 and _level(player, "woodcutting_level") >= 50)
    add(
        "Resource Baron",
        "Collect 10,000 total ores and 10,000 total logs",
        "Difficult",
        lambda player: _inventory_total(player, mining_output_items) >= 10000
        and _inventory_total(player, woodcutting_log_items) >= 10000,
    )
    add("Skilling Prodigy", "Reach level 80 in both Mining and Woodcutting", "Very Challenging", lambda player: _level(player, "mining_level") >= 80 and _level(player, "woodcutting_level") >= 80)
    add("Master of Resources", "Reach level 99 in both Mining and Woodcutting", "Very Challenging", lambda player: _level(player, "mining_level") >= 99 and _level(player, "woodcutting_level") >= 99)

    add(
        "Living Legend",
        "Complete all other achievements",
        "Very Challenging",
        lambda player: _completed_achievement_count(player) >= final_count["value"] - 1,
    )

    add("Gem Finder", "Mine your first gem", "Easy", lambda player: _inventory_total(player, gem_items) > 0)
    add("Sapphire Collector", "Mine 10 uncut sapphires", "Moderate", lambda player: _item_count(player, "Uncut sapphire") >= 10)
    add("Emerald Hunter", "Mine 10 uncut emeralds", "Moderate", lambda player: _item_count(player, "Uncut emerald") >= 10)
    add("Ruby Seeker", "Mine 10 uncut rubies", "Difficult", lambda player: _item_count(player, "Uncut ruby") >= 10)
    add("Diamond Prospector", "Mine 10 uncut diamonds", "Very Challenging", lambda player: _item_count(player, "Uncut diamond") >= 10)
    add("Gem Master", "Mine 100 gems in total", "Very Challenging", lambda player: _inventory_total(player, gem_items) >= 100)

    add("Rune Mysteries", "Complete Rune Mysteries", "Easy", lambda player: _quest_completed(player, "rune_mysteries"))
    add("Novice Runecrafter", "Reach Runecrafting level 10", "Easy", lambda player: _level(player, "runecrafting_level") >= 10)
    add("Hooded Runecrafter", "Claim the Wicked hood", "Easy", lambda player: _claim_completed(player, "wicked_hood"))
    add("Intermediate Runecrafter", "Reach Runecrafting level 30", "Moderate", lambda player: _level(player, "runecrafting_level") >= 30)
    add("Rune Stockpile", "Craft 1,000 total runes", "Moderate", lambda player: _inventory_total(player, runecrafting_output_items) >= 1000)
    add("Expert Runecrafter", "Reach Runecrafting level 60", "Difficult", lambda player: _level(player, "runecrafting_level") >= 60)
    add("Master Runecrafter", "Reach Runecrafting level 99", "Very Challenging", lambda player: _level(player, "runecrafting_level") >= 99)

    add("Novice Smith", "Smelt your first bar", "Easy", lambda player: _inventory_total(player, bar_items) > 0)
    add("Bronze Master", "Smelt 100 Bronze bars", "Easy", lambda player: _item_count(player, "Bronze bar") >= 100)
    add("Iron Forger", "Smelt 500 Iron bars", "Moderate", lambda player: _item_count(player, "Iron bar") >= 500)
    add("Steel Specialist", "Smelt 1000 Steel bars", "Moderate", lambda player: _item_count(player, "Steel bar") >= 1000)
    add("Mithril Maestro", "Smelt 500 Mithril bars", "Difficult", lambda player: _item_count(player, "Mithril bar") >= 500)
    add("Adamantite Artisan", "Smelt 250 Adamantite bars", "Very Challenging", lambda player: _item_count(player, "Adamantite bar") >= 250)
    add("Runite Refiner", "Smelt 100 Runite bars", "Very Challenging", lambda player: _item_count(player, "Runite bar") >= 100)

    add("Novice Crafter", "Reach level 2 in Crafting", "Easy", lambda player: _level(player, "crafting_level") > 1)
    add("Pottery Apprentice", "Craft 100 pots", "Easy", lambda player: _item_count(player, "Empty pot") >= 100)
    add("Jewelry Novice", "Craft 50 gold rings", "Moderate", lambda player: _item_count(player, "Gold ring") >= 50)
    add("Gem Cutter", "Cut 10 of each gem type", "Difficult", lambda player: _has_each(player, ("Sapphire", "Emerald", "Ruby", "Diamond"), 10))
    add("Master Crafter", "Reach Crafting level 99", "Very Challenging", lambda player: _level(player, "crafting_level") >= 99)

    add("First Fire", "Burn your first log", "Easy", lambda player: _item_count(player, "Ashes") > 0)
    add("Novice Firemaker", "Reach Firemaking level 10", "Easy", lambda player: _level(player, "firemaking_level") >= 10)
    add("Ash Collector", "Collect 100 Ashes", "Easy", lambda player: _item_count(player, "Ashes") >= 100)
    add("Intermediate Firemaker", "Reach Firemaking level 30", "Moderate", lambda player: _level(player, "firemaking_level") >= 30)
    add("Ash Hoarder", "Collect 1,000 Ashes", "Moderate", lambda player: _item_count(player, "Ashes") >= 1000)
    add("Expert Firemaker", "Reach Firemaking level 60", "Difficult", lambda player: _level(player, "firemaking_level") >= 60)
    add("Ash Stockpile", "Collect 10,000 Ashes", "Difficult", lambda player: _item_count(player, "Ashes") >= 10000)
    add("Master Firemaker", "Reach Firemaking level 99", "Very Challenging", lambda player: _level(player, "firemaking_level") >= 99)

    add("First Catch", "Catch your first fish", "Easy", lambda player: _inventory_total(player, fishing_output_items) > 0)
    add("Novice Angler", "Reach Fishing level 10", "Easy", lambda player: _level(player, "fishing_level") >= 10)
    add("Fish Collector", "Catch 100 total fish", "Easy", lambda player: _inventory_total(player, fishing_output_items) >= 100)
    add("Intermediate Angler", "Reach Fishing level 30", "Moderate", lambda player: _level(player, "fishing_level") >= 30)
    add("Fish Hoarder", "Catch 1,000 total fish", "Moderate", lambda player: _inventory_total(player, fishing_output_items) >= 1000)
    add("Expert Angler", "Reach Fishing level 60", "Difficult", lambda player: _level(player, "fishing_level") >= 60)
    add("Fish Stockpile", "Catch 10,000 total fish", "Difficult", lambda player: _inventory_total(player, fishing_output_items) >= 10000)
    add("Master Angler", "Reach Fishing level 99", "Very Challenging", lambda player: _level(player, "fishing_level") >= 99)

    add("First Hunt", "Catch your first Hunter creature", "Easy", lambda player: _level(player, "hunter_success_count", 0) >= 1 or _inventory_total(player, hunter_output_items) > 0)
    add("Novice Hunter", "Reach Hunter level 10", "Easy", lambda player: _level(player, "hunter_level") >= 10)
    add("Trap Starter", "Catch 100 Hunter creatures", "Easy", lambda player: _level(player, "hunter_success_count", 0) >= 100)
    add("Intermediate Hunter", "Reach Hunter level 30", "Moderate", lambda player: _level(player, "hunter_level") >= 30)
    add("Hunter Haul", "Catch 1,000 Hunter creatures", "Moderate", lambda player: _level(player, "hunter_success_count", 0) >= 1000)
    add("Expert Hunter", "Reach Hunter level 60", "Difficult", lambda player: _level(player, "hunter_level") >= 60)
    add("Hunter Stockpile", "Catch 10,000 Hunter creatures", "Difficult", lambda player: _level(player, "hunter_success_count", 0) >= 10000)
    add("Master Hunter", "Reach Hunter level 99", "Very Challenging", lambda player: _level(player, "hunter_level") >= 99)

    add("First Cook", "Cook your first food", "Easy", lambda player: _level(player, "cooking_success_count", 0) >= 1)
    add("First Burn", "Burn your first food", "Easy", lambda player: _level(player, "cooking_burn_count", 0) >= 1)
    add("Novice Cook", "Reach Cooking level 10", "Easy", lambda player: _level(player, "cooking_level") >= 10)
    add("Food Collector", "Successfully cook 100 items", "Easy", lambda player: _level(player, "cooking_success_count", 0) >= 100)
    add("Intermediate Cook", "Reach Cooking level 30", "Moderate", lambda player: _level(player, "cooking_level") >= 30)
    add("Kitchen Regular", "Successfully cook 1,000 items", "Moderate", lambda player: _level(player, "cooking_success_count", 0) >= 1000)
    add("Expert Cook", "Reach Cooking level 60", "Difficult", lambda player: _level(player, "cooking_level") >= 60)
    add("Kitchen Stockpile", "Successfully cook 10,000 items", "Difficult", lambda player: _level(player, "cooking_success_count", 0) >= 10000)
    add("Master Cook", "Reach Cooking level 99", "Very Challenging", lambda player: _level(player, "cooking_level") >= 99)

    add("First Potion", "Mix your first potion", "Easy", lambda player: _inventory_total(player, herblore_finished_items) > 0)
    add("Novice Herbalist", "Reach Herblore level 10", "Easy", lambda player: _level(player, "herblore_level") >= 10)
    add("Potion Collector", "Hold 100 finished potions at once", "Easy", lambda player: _inventory_total(player, herblore_finished_items) >= 100)
    add("Intermediate Herbalist", "Reach Herblore level 30", "Moderate", lambda player: _level(player, "herblore_level") >= 30)
    add("Potion Hoarder", "Hold 1,000 finished potions at once", "Moderate", lambda player: _inventory_total(player, herblore_finished_items) >= 1000)
    add("Expert Herbalist", "Reach Herblore level 60", "Difficult", lambda player: _level(player, "herblore_level") >= 60)
    add("Master Herbalist", "Reach Herblore level 99", "Very Challenging", lambda player: _level(player, "herblore_level") >= 99)

    add("Rest in Pieces", "Bury your first bone", "Easy", lambda player: _level(player, "prayer_bury_count", 0) >= 1)
    add("Novice Devotee", "Reach Prayer level 10", "Easy", lambda player: _level(player, "prayer_level") >= 10)
    add("Faithful", "Complete 100 Prayer training actions", "Easy", lambda player: _level(player, "prayer_actions_completed", 0) >= 100)
    add("Intermediate Devotee", "Reach Prayer level 30", "Moderate", lambda player: _level(player, "prayer_level") >= 30)
    add("Ghostly Disciple", "Collect 500 ecto-tokens", "Moderate", lambda player: _item_count(player, "Ecto-token") >= 500)
    add("Expert Devotee", "Reach Prayer level 60", "Difficult", lambda player: _level(player, "prayer_level") >= 60)
    add("Master Devotee", "Reach Prayer level 99", "Very Challenging", lambda player: _level(player, "prayer_level") >= 99)
    add("First Foundations", "Complete your first Construction build", "Easy", lambda player: _level(player, "construction_actions_completed", 0) >= 1)
    add("Novice Builder", "Reach Construction level 10", "Easy", lambda player: _level(player, "construction_level") >= 10)
    add("Established Builder", "Reach Construction level 30", "Moderate", lambda player: _level(player, "construction_level") >= 30)
    add("Master Builder", "Reach Construction level 60", "Difficult", lambda player: _level(player, "construction_level") >= 60)
    add("Construction Cape", "Reach Construction level 99", "Very Challenging", lambda player: _level(player, "construction_level") >= 99)
    add("Packed Flat", "Create 100 Construction outputs", "Difficult", lambda player: _level(player, "construction_outputs_created", 0) >= 100)

    add("First Plant", "Plant your first Farming crop", "Easy", lambda player: _farming_counter(player, "plants") >= 1)
    for name, required_level, difficulty in FARMING_LEVEL_ACHIEVEMENTS:
        add(
            name,
            f"Reach Farming level {required_level}",
            difficulty,
            lambda player, level=required_level: _level(player, "farming_level") >= level,
        )
    for name, required_total, difficulty in FARMING_PRODUCE_ACHIEVEMENTS:
        add(
            name,
            f"Harvest {required_total:,} total Farming produce",
            difficulty,
            lambda player, total=required_total: _farming_counter(player, "produce_harvested") >= total,
        )
    add("Tree Doctor", "Check the health of your first Farming tree", "Easy", lambda player: _farming_counter(player, "tree_health_checks") >= 1)
    add("Full Farm Run", "Queue your first full farm run", "Moderate", lambda player: _farming_counter(player, "full_runs") >= 1)

    add("First Lift", "Complete your first successful Thieving action", "Easy", lambda player: _level(player, "thieving_success_count", 0) >= 1)
    add("Novice Thief", "Reach Thieving level 10", "Easy", lambda player: _level(player, "thieving_level") >= 10)
    add("Sticky Fingers", "Complete 100 successful Thieving actions", "Moderate", lambda player: _level(player, "thieving_success_count", 0) >= 100)
    add("Master Thief", "Reach Thieving level 99", "Very Challenging", lambda player: _level(player, "thieving_level") >= 99)

    add("First Agility Action", "Complete your first Agility action", "Easy", lambda player: _level(player, "agility_actions_completed", 0) >= 1)
    add("Novice Acrobat", "Reach Agility level 10", "Easy", lambda player: _level(player, "agility_level") >= 10)
    add("Course Runner", "Complete your first Agility lap", "Easy", lambda player: _agility_counter(player, "total") >= 1)
    add("Arena Ticket", "Earn your first Brimhaven Agility Arena ticket", "Easy", lambda player: _item_count(player, "Agility arena ticket") >= 1)
    add("Intermediate Acrobat", "Reach Agility level 30", "Moderate", lambda player: _level(player, "agility_level") >= 30)
    add("On the Move", "Complete 100 Agility actions", "Moderate", lambda player: _level(player, "agility_actions_completed", 0) >= 100)
    add("Flawless Footing", "Complete a flawless advanced-course lap", "Moderate", lambda player: max(_agility_counter(player, "gnome_advanced_flawless"), _agility_counter(player, "barbarian_advanced_flawless")) >= 1)
    add("Pit Proven", "Succeed in The Pit", "Moderate", lambda player: _level(player, "agility_pit_successes", 0) >= 1)
    add("Expert Acrobat", "Reach Agility level 60", "Difficult", lambda player: _level(player, "agility_level") >= 60)
    add("Arena Regular", "Hold 100 Brimhaven Agility Arena tickets", "Difficult", lambda player: _item_count(player, "Agility arena ticket") >= 100)
    add("Activity Circuit", "Complete every live Agility activity family", "Difficult", lambda player: _has_completed_agility_activity_families(player, agility_activity_families))
    add("Agile", "Own both pieces of the Agile set", "Difficult", lambda player: all(_owns_or_equipped(player, item) for item in ("Agile top", "Agile legs")))
    add("Master Acrobat", "Reach Agility level 99", "Very Challenging", lambda player: _level(player, "agility_level") >= 99)
    add("Endurance", "Complete 1,000 Agility actions", "Very Challenging", lambda player: _level(player, "agility_actions_completed", 0) >= 1000)

    add("First Cast", "Complete your first standalone Magic cast", "Easy", lambda player: _level(player, "magic_actions_completed", 0) >= 1)
    add("Novice Mage", "Reach Magic level 10", "Easy", lambda player: _level(player, "magic_level") >= 10)
    add("Spell Slinger", "Complete 100 standalone Magic casts", "Easy", lambda player: _level(player, "magic_actions_completed", 0) >= 100)
    add("Intermediate Mage", "Reach Magic level 30", "Moderate", lambda player: _level(player, "magic_level") >= 30)
    add("Kolodion's Challenger", "Complete the Mage Arena landmark", "Moderate", lambda player: bool((player.get("mage_arena", {}) or {}).get("completed")))
    add("Expert Mage", "Reach Magic level 60", "Difficult", lambda player: _level(player, "magic_level") >= 60)
    add("Master Mage", "Reach Magic level 99", "Very Challenging", lambda player: _level(player, "magic_level") >= 99)

    final_count["value"] = len(definitions)
    return tuple(definitions)


def achievements_as_dict(
    definitions: Iterable[AchievementDefinition],
) -> dict[str, dict[str, Any]]:
    return {definition.name: definition.as_legacy_dict() for definition in definitions}


def achievement_rows_for_difficulty(
    achievements: Mapping[str, Mapping[str, Any]],
    player_data: PlayerData,
    difficulty: str,
) -> tuple[AchievementRow, ...]:
    completed = set(player_data.get("completed_achievements", ()) or ())
    return tuple(
        AchievementRow(
            name=name,
            description=str(data.get("description", "")),
            difficulty=str(data.get("difficulty", "")),
            completed=name in completed,
        )
        for name, data in achievements.items()
        if data.get("difficulty") == difficulty
    )


def achievement_difficulty_progress(
    achievements: Mapping[str, Mapping[str, Any]],
    player_data: PlayerData,
    difficulty: str,
) -> tuple[int, int]:
    rows = achievement_rows_for_difficulty(achievements, player_data, difficulty)
    return sum(1 for row in rows if row.completed), len(rows)


def achievement_progress(
    achievements: Mapping[str, Mapping[str, Any]],
    player_data: PlayerData,
) -> tuple[int, int, float]:
    completed_count = len(player_data.get("completed_achievements", ()) or ())
    total_count = len(achievements)
    return completed_count, total_count, (completed_count / max(1, total_count)) * 100
