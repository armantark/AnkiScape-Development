"""XP per tick of play is the same at speed 1 and speed 10 (plan Part J item 1).

Each sampled route plays at least 3,600 game ticks (36 minutes of
0.6-second ticks) at each speed, over matching windows for 20 paired seeds. A card goes through the add-on's own card glue
(``_spend_card_on_action``), so the carried pack, bank trips, the next-step
check and the after-card recovery run as they do in play. The speed-10 run
answers cards until the window is spent: 60 cards when no card ends early. Its
last card can carry play past the minimum window. Both runs extend to a
common endpoint with no unpaid step debt; otherwise XP that arrives in lumps
or before a borrowed step finishes would depend on the sample's cut point. A card that a
danger stop or a kill ends early leaves its unspent ticks unplayed, so they
count neither as play nor towards the window.

The route passes when the mean XP per tick spent at speed 10 is within four
standard errors of the paired differences from speed 1. Quests and Dungeoneering take one stage
or room per card at every speed (assumption 5), so they are not sampled.

Combat runs with banking off, as Sol's 2026-10-15 kill-cap measurement did,
because a Combat bank run takes two cards at every speed (plan Q12): the engine
gets the same ``allow_bank_run=False`` that encounter-only enemies get, and the
food loadout lasts the window. Gathering drops what it gathers, the player's own
no-banking choice. Processing keeps its bank trips: a trip's travel reviews are
six-tick steps at every speed, and the start of a trip is a danger stop.
"""

from __future__ import annotations

import math
import random
import statistics
import sys
import unittest
from typing import Any, Callable, Mapping
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.skill_registry import trainable_skill_definitions
from ankiscape.data.quest_data import QUESTS
from ankiscape.logic.cadence_coverage import FOREGROUND_ROUTE_TABLES
from ankiscape.runtime.runtime_actions_carried_requirements import (
    _BANK_RUN_TARGET_KEYS,
    _processing_consumable_requirements_for,
    _processing_requirements_for,
)
from tests.test_fight_caves import _entered as _fight_caves_entered
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_livid_farm_logic import _player as _livid_farm_player
from tests.test_sorceress_garden import _player as _sorceress_garden_player
from tests.test_warriors_guild import _player as _warriors_guild_player

SEEDS = range(20)
PLAY_TICKS = 3_600
MAX_STANDARD_ERRORS = 4
# A run that keeps answering without spending play (a stalled route) ends here.
MAX_CARDS = 20 * PLAY_TICKS // 6

STOCK = 1_000_000
MAXED_XP = 13_034_431.0
_GATHERING_KEYS = frozenset({"mining", "woodcutting", "fishing", "hunter"})
_SKILL_NAMES = {
    "agility": "Agility",
    "combat": "Combat",
    "construction": "Construction",
    "cooking": "Cooking",
    "crafting": "Crafting",
    "firemaking": "Firemaking",
    "fishing": "Fishing",
    "fletching": "Fletching",
    "herblore": "Herblore",
    "hunter": "Hunter",
    "magic": "Magic",
    "mining": "Mining",
    "prayer": "Prayer",
    "runecrafting": "Runecrafting",
    "smithing": "Smithing",
    "summoning": "Summoning",
    "thieving": "Thieving",
    "utility": "Utility / Activities",
    "woodcutting": "Woodcutting",
}


class Route:
    """One sampled route: the skill to select and a fresh save that can play it."""

    def __init__(self, handler_key: str, action_id: str, player: Callable[[], dict], name: str = ""):
        self.handler_key = handler_key
        self.action_id = action_id
        self.skill = _SKILL_NAMES[handler_key]
        self.player = player
        self.name = name or f"{handler_key}:{action_id}"

    def __repr__(self) -> str:
        return self.name


def skilling(handler_key: str, action_id: str, *, stock=(), **save: Any) -> Route:
    """A maxed player with every quest done, stocked for one skilling route.

    The bank holds the inputs and tools that the route's catalog row and
    recipe name, plus ``stock`` for the ones they do not (essence, a needle).
    """

    def player() -> dict:
        data = {
            "quests": {quest.id: {"completed": True} for quest in QUESTS},
            "toolbelt": {"mining": ["rune_pickaxe"], "woodcutting": ["rune_hatchet"]},
            _BANK_RUN_TARGET_KEYS[handler_key]: action_id,
        }
        for skill in trainable_skill_definitions():
            data[skill.level_key] = 99
            data[skill.exp_key] = MAXED_XP
        if handler_key in _GATHERING_KEYS:
            data["carried_keep_drop"] = {action_id: "drop"}
        spec = FOREGROUND_ROUTE_TABLES[handler_key][action_id]
        named = [
            item
            for field in ("requirements", "tools", "required_items", "rune_cost")
            for item in ((spec.get(field) or {}) if isinstance(spec, Mapping) else {})
        ]
        named += list(_processing_requirements_for(handler_key, data))
        named += list(_processing_consumable_requirements_for(handler_key, data, action_id, {}, advanced=False))
        data["inventory"] = {item: STOCK for item in (*named, *stock)}
        data.update(save)
        return data

    return Route(handler_key, action_id, player)


# Thieving and Agility failures hurt. Thieving eats from the Combat food
# loadout and Agility from its pack, so both bring Sharks as a player would.
_FED = {
    "stock": ("Shark",),
    "combat_auto_eat_food": ["Shark"],
    "combat_supply_loadout": {"food": {"Shark": 1_000}},
}


def building(action_id: str) -> Route:
    room = FOREGROUND_ROUTE_TABLES["construction"][action_id]["room"]
    return skilling(
        "construction",
        action_id,
        stock=("Saw", "Hammer", "Bronze nails"),
        house_owned=True,
        house_rooms_bought={room: True},
    )


def activity(action_id: str, player: Callable[[], dict]) -> Route:
    def entered() -> dict:
        data = player()
        data["current_utility"] = action_id
        return data

    return Route("utility", action_id, entered)


def _animated_armour_fighter() -> dict:
    data = _warriors_guild_player()
    data["inventory"].update({"Rune full helm": 1, "Rune platebody": 1, "Rune platelegs": 1})
    return data


# For each handler key: the lowest-level, the middle and the highest route by
# (catalog level, id), then that key's rate_limited routes. Where the route at
# a position pays no XP or cannot start for any player, the nearest route
# that can stands in, named in the comment.
SAMPLE: dict[str, tuple[Route, ...]] = {
    "mining": (
        skilling("mining", "clay"),
        skilling("mining", "gem_rocks"),
        skilling("mining", "runite"),
        skilling("mining", "iron"),
        skilling("mining", "concentrated_gold"),
    ),
    "woodcutting": (
        skilling("woodcutting", "achey"),
        skilling("woodcutting", "mahogany"),
        skilling("woodcutting", "curly_jade_root"),
        skilling("woodcutting", "tree"),
        skilling("woodcutting", "oak"),
        skilling("woodcutting", "willow"),
        skilling("woodcutting", "maple"),
        skilling("woodcutting", "yew"),
        skilling("woodcutting", "ivy"),
        skilling("woodcutting", "magic"),
    ),
    "fishing": (
        skilling("fishing", "catch_crayfish"),
        skilling("fishing", "catch_tuna_swordfish"),
        skilling("fishing", "catch_rocktail"),
        skilling("fishing", "catch_sharks"),
        skilling("fishing", "catch_monkfish"),
    ),
    "hunter": (
        skilling("hunter", "catch_crimson_swift"),
        skilling("hunter", "catch_nature_impling_world"),
        skilling("hunter", "barehand_black_warlock"),
        skilling("hunter", "catch_red_chinchompa"),
        skilling("hunter", "catch_orange_salamander"),
        skilling("hunter", "catch_red_salamander"),
    ),
    "smithing": (
        skilling("smithing", "forge_bronze_dagger"),
        skilling("smithing", "forge_steel_platelegs"),
        skilling("smithing", "forge_rune_plateskirt"),
    ),
    "crafting": (
        skilling("crafting", "add_rune_cracked_mining_urn"),
        skilling("crafting", "spin_hair_to_rope"),
        skilling("crafting", "weave_milestone_cape_90"),
        skilling("crafting", "leather_green_dhide_body", stock=("Needle",)),
        skilling("crafting", "battlestaff_water_battlestaff"),
    ),
    "fletching": (
        skilling("fletching", "arrow_shafts"),
        skilling("fletching", "cut_red_topaz_bolt_tips"),
        skilling("fletching", "fletch_dragon_darts"),
    ),
    "firemaking": (
        skilling("firemaking", "achey_logs"),
        skilling("firemaking", "maple_logs"),
        skilling("firemaking", "cursed_magic_logs"),
    ),
    "cooking": (
        skilling("cooking", "burn_seaweed"),
        skilling("cooking", "cook_curry"),
        skilling("cooking", "cook_tiger_shark"),
        skilling("cooking", "churn_milk_cheese_wheel"),
        skilling("cooking", "churn_butter_cheese_wheel"),
    ),
    "runecrafting": (
        # bind_air_talisman_staff, the lowest by id, pays no XP.
        skilling("runecrafting", "bind_air_tiara"),
        skilling("runecrafting", "craft_air_runes", stock=("Pure essence", "Air talisman")),
        skilling("runecrafting", "craft_blood_runes", stock=("Pure essence", "Blood talisman")),
    ),
    "herblore": (
        skilling("herblore", "clean_guam"),
        # unf_kwuarm, the middle route, pays no XP.
        skilling("herblore", "finished_super_strength"),
        skilling("herblore", "finished_overload"),
    ),
    "prayer": (
        skilling("prayer", "bury_ancient_bones"),
        skilling("prayer", "ectofuntus_jogre_bones"),
        skilling("prayer", "scatter_infernal_ashes"),
        skilling("prayer", "gilded_altar_dragon_bones"),
    ),
    "magic": (
        skilling("magic", "enchant_opal_bolts"),
        skilling("magic", "monster_examine"),
        # Every level-99 spell is Borrowed Power, which needs an Arcane capacitor.
        skilling("magic", "ghorrock_teleport"),
        skilling("magic", "high_alchemy", stock=("Rune platebody",), magic_alchemy_item="Rune platebody"),
        skilling("magic", "superheat_mithril_bar"),
    ),
    "construction": (
        building("crude_wooden_chair"),
        building("steel_candlestick"),
        building("magicalcaperack"),
    ),
    "thieving": (
        skilling("thieving", "pickpocket_man", **_FED),
        skilling("thieving", "pickpocket_guard", **_FED),
        # pickpocket_lletya_elf, the highest, is source-blocked and pays no XP.
        skilling("thieving", "pickpocket_hero", **_FED),
    ),
    "agility": (
        skilling("agility", "brimhaven_arena", **_FED),
        skilling("agility", "barbarian_normal", **_FED),
        skilling("agility", "barbarian_advanced", **_FED),
    ),
    "summoning": (
        skilling("summoning", "infuse_spiritwolf"),
        skilling("summoning", "infuse_spiritkyatt"),
        skilling("summoning", "scroll_steeloflegends"),
    ),
    # Activities carry no catalog level: the first, the middle and the last
    # XP-paying activity by id, each on its own suite's entered player.
    "utility": (
        activity("fight_caves", _fight_caves_entered),
        activity("sorceress_garden", _sorceress_garden_player),
        activity("warriors_guild_animated_armour", _animated_armour_fighter),
        activity("livid_farm", lambda: _livid_farm_player(rune_quantity=10_000_000)),
    ),
}


_RUNE_ARMOUR = {"body": "Rune platebody", "legs": "Rune platelegs", "head": "Rune full helm"}
# Sol's setups and pairs (combat-kill-cap-measurement-sol-2026-10-15.md, sections 2 and 3).
COMBAT_SETUPS = {
    20: {"weapon": "Mithril scimitar", "body": "Mithril platebody", "legs": "Mithril platelegs"},
    40: {"weapon": "Rune scimitar", **_RUNE_ARMOUR},
    60: {"weapon": "Dragon scimitar", **_RUNE_ARMOUR},
    80: {"weapon": "Abyssal whip", **_RUNE_ARMOUR, "shield": "Dragon defender", "cape": "Fire cape"},
    99: {"weapon": "Abyssal whip", **_RUNE_ARMOUR, "shield": "Dragon defender", "cape": "Fire cape"},
}
COMBAT_PAIRS = {
    20: ("hill_giant", "cow", "al_kharid_warrior", "rock_crab"),
    40: ("hill_giant", "moss_giant", "rock_crab", "giant_spider_level_50"),
    60: ("moss_giant", "giant_spider_level_50", "lesser_demon", "fire_giant"),
    80: ("giant_spider_level_50", "fire_giant", "greater_demon", "bloodveld"),
    99: ("fire_giant", "black_demon", "abyssal_demon", "bloodveld"),
}
# Sol's 28 Sharks last one trip; chained fights eat under 100 in the window,
# and banking is off, so the loadout holds more than the window needs.
_SHARK_LOADOUT = 1_000


def fighting(band: int, target_id: str) -> Route:
    """Sol's band player: combat stats and Slayer at the band, Prayer and Summoning 1."""

    def player() -> dict:
        data = {
            "inventory": {"Shark": _SHARK_LOADOUT},
            "equipment": dict(COMBAT_SETUPS[band]),
            "current_combat_target": target_id,
            "combat_attack_style": "accurate",
            "combat_lifepoints": band * 10,
            "combat_auto_eat_threshold_percent": 70,
            "combat_auto_eat_food": ["Shark"],
            "combat_supply_loadout": {"food": {"Shark": _SHARK_LOADOUT}},
            "prayer_level": 1,
            "summoning_level": 1,
        }
        for skill in ("attack", "strength", "defense", "constitution", "ranged", "magic", "slayer"):
            data[f"{skill}_level"] = band
        return data

    return Route("combat", target_id, player, f"combat:{target_id} at band {band}")


# Combat's own lowest, middle and highest enemies, fought by the level-99
# band, then Sol's twenty pairs, one group per band.
SAMPLE["combat"] = (
    fighting(99, "chicken"),
    fighting(99, "deadly_red_spider"),
    fighting(99, "soul_wars_enemy_avatar"),
)
SAMPLE.update(
    {f"combat band {band}": tuple(fighting(band, target) for target in targets) for band, targets in COMBAT_PAIRS.items()}
)


def standard_errors_apart(x1: list[float], x10: list[float]) -> float:
    """Compare paired seed results in standard errors of their difference."""
    mean_x1, mean_x10 = statistics.fmean(x1), statistics.fmean(x10)
    # The same XP summed in a different order can differ in the last bits.
    if math.isclose(mean_x1, mean_x10, rel_tol=1e-9):
        return 0.0
    differences = [fast - slow for slow, fast in zip(x1, x10, strict=True)]
    error = statistics.stdev(differences) / math.sqrt(len(differences))
    difference = mean_x10 - mean_x1
    return difference / error if error else math.copysign(math.inf, difference)


class RatePropertyCase(unittest.TestCase):
    """Loads the add-on once per suite and plays its groups of ``SAMPLE`` through it.

    Test modules subclass this through the module (``rate_property.RatePropertyCase``)
    so that test discovery does not also collect the empty base.
    """

    GROUPS: tuple[str, ...] = ()

    @classmethod
    def setUpClass(cls):
        cls._orig_modules = dict(sys.modules)
        _install_runtime_fakes()
        addon = _load_addon_as_package(f"ankiscape_rates_{cls.__name__.lower()}")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda *_args, **_kwargs: None
        cls.addon = addon
        combat_module = sys.modules[f"{addon.__name__}.runtime.runtime_actions_combat"]
        burst = combat_module.apply_combat_burst_pure

        def burst_without_banking(*args, **kwargs):
            return burst(*args, **{**kwargs, "allow_bank_run": False})

        cls._banking_off = patch.object(combat_module, "apply_combat_burst_pure", burst_without_banking)
        cls._banking_off.start()

    @classmethod
    def tearDownClass(cls):
        cls._banking_off.stop()
        sys.modules.clear()
        sys.modules.update(cls._orig_modules)

    def setUp(self):
        # addon.random is the process-wide module; the seeds must not leak out.
        state = random.getstate()
        self.addCleanup(random.setstate, state)
        self.addon.show_error_message = lambda _title, message: self.fail(message)

    def _card_ticks(self, skill: str) -> int:
        addon = self.addon
        handler_key = addon.review_action_handler_key(skill)
        ctx = addon._runtime_action_context()
        budget = ctx.card.ticks_remaining
        last_fight = addon._state.player_data.get("combat_last_result")
        addon._spend_card_on_action(ctx, handler_key, addon._registered_answer_handler(skill))
        if handler_key != "combat":
            return budget - ctx.card.ticks_remaining
        fight = addon._state.player_data.get("combat_last_result")
        return 0 if fight is last_fight else int(fight.get("ticks_elapsed", 0))

    def play(self, route: Route, speed: int, seed: int, ticks: int) -> tuple[float, int]:
        """Play at least ``ticks`` and finish with every borrowed step tick paid."""
        addon = self.addon
        addon._review_action_multiplier = lambda: speed
        addon._state.player_data = route.player()
        addon._state.current_skill = route.skill
        random.seed(seed)
        xp_before = sum(addon._implemented_exp_keys_snapshot().values())
        spent = cards = 0
        while (
            spent < ticks or addon._state.player_data.get("card_tick_debt", 0)
        ) and cards < MAX_CARDS and addon._state.current_skill == route.skill:
            spent += self._card_ticks(route.skill)
            cards += 1
        self.assertGreaterEqual(
            spent,
            ticks,
            f"{route} at speed {speed}, seed {seed}: play stopped after {cards} cards and {spent} ticks "
            f"({addon._state.current_skill}: {addon._state.pending_bankstanding_notice})",
        )
        self.assertFalse(addon._state.player_data.get("card_tick_debt", 0), f"{route}: unpaid sample time")
        return sum(addon._implemented_exp_keys_snapshot().values()) - xp_before, spent

    def rates(self, route: Route) -> dict[int, list[float]]:
        """XP per tick over equal, debt-free windows for every paired seed."""
        rates: dict[int, list[float]] = {1: [], 10: []}
        for seed in SEEDS:
            xp10, window10 = self.play(route, 10, seed, PLAY_TICKS)
            xp1, window1 = self.play(route, 1, seed, window10)
            # Full cards can pass an endpoint; both runs must finish at the same tick.
            while window1 != window10:
                if window1 < window10:
                    xp1, window1 = self.play(route, 1, seed, window10)
                else:
                    xp10, window10 = self.play(route, 10, seed, window1)
            self.assertEqual(window1, window10, f"{route}, seed {seed}: rate windows differ")
            rates[1].append(xp1 / window1)
            rates[10].append(xp10 / window10)
        return rates

    def test_xp_per_tick_is_the_same_at_speed_1_and_speed_10(self):
        for route in (route for group in self.GROUPS for route in SAMPLE[group]):
            with self.subTest(route=repr(route)):
                rates = self.rates(route)
                x1, x10 = statistics.fmean(rates[1]), statistics.fmean(rates[10])
                self.assertGreater(x1, 0.0, f"{route} pays no XP")
                apart = standard_errors_apart(rates[1], rates[10])
                self.assertLessEqual(
                    abs(apart),
                    MAX_STANDARD_ERRORS,
                    f"{route}: XP per tick {x1:.4f} at x1, {x10:.4f} at x10, {apart:+.2f} standard errors apart",
                )
