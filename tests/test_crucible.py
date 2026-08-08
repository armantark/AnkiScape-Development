"""The Crucible: entry gate, bounty fee, arena combat, and the Trophy bone shop.

Every reward here is reached by playing, not by writing the winning state into
the save. That is deliberate. Two families shipped this month whose mechanics
tests mocked the combat kernel, so a green suite was compatible with a boss that
could not be fought and a match no one could win or lose. The helpers below run
the real `apply_combat_burst_pure` from a real `default_player_data`, and the
rank-ladder tests play far enough to be named Supreme Champion before they claim
the helm is buyable.
"""

from __future__ import annotations

import copy
import json
import random
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    COMBAT_ENEMY_DATA,
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.crucible_data import (
    CRUCIBLE_ABANDONMENT_FEE,
    CRUCIBLE_ACTIVITY_ID,
    CRUCIBLE_ASSET_MANIFEST,
    CRUCIBLE_BONES_PER_KILL,
    CRUCIBLE_COMBAT_TARGET_ID,
    CRUCIBLE_CURRENCY,
    CRUCIBLE_EVENT_INTERVAL_REVIEWS,
    CRUCIBLE_LESSONS,
    CRUCIBLE_MINIMUM_COMBAT_LEVEL,
    CRUCIBLE_POINTS_PER_CHAMPION_HIT,
    CRUCIBLE_PVP_BOOST_CAPS,
    CRUCIBLE_RANKS,
    CRUCIBLE_RISK_EXPECTATION_BASE,
    CRUCIBLE_RISK_EXPECTATION_PER_LEVEL,
    CRUCIBLE_SUPREME_HELM,
    CRUCIBLE_SUPREME_HELM_COST,
    CRUCIBLE_SUPREME_TIER,
    CRUCIBLE_TARGET_LEVEL_OFFSETS,
    CRUCIBLE_TAUNTS,
    CRUCIBLE_TITLES,
    CRUCIBLE_UNLOCKS,
)
from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
from ankiscape.logic.crucible_logic import (
    apply_crucible_command_pure,
    apply_crucible_review_pure,
    buy_crucible_supreme_helm_pure,
    buy_crucible_unlock_pure,
    crucible_fee_quote_pure,
    crucible_rank_pure,
    crucible_view_pure,
    default_crucible_state_pure,
    enter_crucible_pure,
    leave_crucible_pure,
    _new_target,
    sanitize_crucible_state_pure,
    set_crucible_cosmetic_pure,
    take_crucible_lesson_pure,
)
from ankiscape.logic.shop_logic import advance_shop_market_clock_pure
from ankiscape.logic_pure.logic_pure import (
    combat_max_lifepoints_pure,
    player_combat_level_pure,
)
from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    handle_crucible_answer,
)


def _player(levels: int = 60, coins: int = 5_000_000, **overrides):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for key in (
        "attack_level",
        "strength_level",
        "defense_level",
        "constitution_level",
    ):
        player[key] = levels
    player["equipment"] = {"weapon": "Mithril scimitar"}
    player["inventory"] = {"Coins": coins}
    player["carried_inventory"] = {}
    player["current_combat_target"] = "chicken"
    player["current_utility"] = "make_soft_clay"
    player["combat_encounter"] = {}
    player["activity_session"] = {"active_id": ""}
    player["combat_lifepoints"] = levels * 10
    player.update(overrides)
    return player


def _armoured_player(protect_item: bool = False):
    """Three worn pieces plus a four-Lobster carried pack: seven items at risk."""
    player = _player(prayer_level=60)
    player["equipment"] = {
        "weapon": "Mithril scimitar",
        "body": "Mithril platebody",
        "legs": "Mithril platelegs",
    }
    player["inventory"] = {"Coins": 5_000_000, "Lobster": 4}
    player["carried_inventory"] = {"chicken": {"Lobster": 4}}
    if protect_item:
        player["combat_prayer_book"] = "standard"
        player["combat_selected_prayers"] = ["protect_item"]
        player["combat_prayers_enabled"] = True
        player["combat_prayer_uptime"] = "100"
        player["combat_prayer_points"] = 600
    return player


def _play(player, seed, *, limit=200, until=None, reenter=False):
    """Play the real arena and return (player, results) after a real path.

    `until` stops on the first result the caller is looking for; `reenter` keeps
    the visit alive across a terminal death so a long ladder climb can continue
    the way a player's would.
    """
    draws = random.Random(seed).random
    results = []
    for _ in range(limit):
        player = advance_shop_market_clock_pure(player)
        player, ok, result = apply_crucible_review_pure(
            player,
            draws,
            equipment_data=EQUIPMENT_DATA,
        )
        if not ok:
            raise AssertionError(result)
        results.append(result)
        if until is not None and until(player, result):
            return player, results
        if result.get("terminal"):
            if not reenter:
                return player, results
            player, ok, info = enter_crucible_pure(player, GE_ITEM_CATALOG)
            if not ok:
                raise AssertionError(info)
    if until is not None:
        raise AssertionError("the arena never reached the condition under test")
    return player, results


def _context(player_data: dict, calls: dict) -> RuntimeActionContext:
    return RuntimeActionContext(
        player_data=player_data,
        random_random=calls["rng"],
        show_error_message=lambda title, message: calls["errors"].append(
            (title, message)
        ),
        deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
        award_skill_exp=lambda _key, amount: amount,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda *_args: None,
        check_achievements=lambda _data: calls.__setitem__("achievements", True),
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: calls.__setitem__("refresh", True),
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda message: calls["activity"].append(message),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


def _calls(seed=1):
    return {
        "rng": random.Random(seed).random,
        "errors": [],
        "xp": [],
        "activity": [],
        "saves": 0,
    }


class CrucibleDataTest(unittest.TestCase):
    def test_the_activity_enemy_and_art_are_registered(self):
        self.assertIn(CRUCIBLE_ACTIVITY_ID, UTILITY_ACTIVITY_DATA)
        self.assertIn(CRUCIBLE_COMBAT_TARGET_ID, COMBAT_ENEMY_DATA)
        self.assertIn(CRUCIBLE_SUPREME_HELM, EQUIPMENT_DATA)
        keys = {row.storage_key for row in ITEM_DEFINITIONS}
        self.assertIn(CRUCIBLE_CURRENCY, keys)
        self.assertIn(CRUCIBLE_SUPREME_HELM, keys)

        root = Path(__file__).resolve().parents[1]
        provenance = json.loads((root / "assets_provenance.json").read_text())
        for row in CRUCIBLE_ASSET_MANIFEST:
            path = str(row["output_path"])
            self.assertTrue((root / path).is_file(), path)
            self.assertLess(
                provenance[path]["timestamp"], "2012-11-20T00:00:00Z", path
            )

    def test_the_shop_prices_match_the_two_sources_that_agree_on_them(self):
        """Cache enums 5899/5900/5901 and the pinned article state the same table."""
        taunts = [row.cost for row in CRUCIBLE_TAUNTS]
        titles = [row.cost for row in CRUCIBLE_TITLES]
        self.assertEqual(taunts, [12, 12] + [36] * 8)
        self.assertEqual(titles, [12, 12] + [30] * 18)
        self.assertEqual(CRUCIBLE_SUPREME_HELM_COST, 60)
        self.assertEqual(len(CRUCIBLE_UNLOCKS), 30)
        self.assertEqual(CRUCIBLE_TAUNTS[0].display_name, "Crazy Laughing")
        self.assertEqual(CRUCIBLE_TITLES[0].display_name, "Cowardly [name]")

    def test_the_boost_caps_match_the_sourced_server_formula(self):
        self.assertEqual(
            CRUCIBLE_PVP_BOOST_CAPS,
            (
                ("attack", 5, 0.15),
                ("strength", 5, 0.15),
                ("defense", 5, 0.15),
                ("ranged", 5, 0.10),
                ("magic", 5, 0.0),
            ),
        )

    def test_the_low_gate_can_reach_the_documented_maxed_mismatch(self):
        player = _player(53)
        self.assertEqual(player_combat_level_pure(player), 60)

        ordinary = [
            _new_target(player, 1, target_number)["combat_level"]
            for target_number in range(1, 4)
        ]
        severe = _new_target(player, 1, 4)["combat_level"]

        self.assertEqual(CRUCIBLE_TARGET_LEVEL_OFFSETS[:3], (-8, 0, 8))
        self.assertEqual(ordinary, [52, 60, 68])
        self.assertEqual(severe, 138)

    def test_the_rank_ladder_is_the_clients_own_tier_list(self):
        self.assertEqual([row[0] for row in CRUCIBLE_RANKS], [0, 1, 2, 3, 4, 5])
        self.assertEqual(
            [row[1] for row in CRUCIBLE_RANKS],
            ["Rank 6", "Rank 5", "Rank 4", "Rank 3", "Rank 2", "Rank 1"],
        )
        self.assertEqual(CRUCIBLE_SUPREME_TIER, 6)
        self.assertEqual(crucible_rank_pure(0)["name"], "Unranked")
        self.assertEqual(crucible_rank_pure(0)["tier"], -1)
        self.assertEqual(crucible_rank_pure(CRUCIBLE_RANKS[-1][2])["name"], "Rank 1")
        self.assertTrue(crucible_rank_pure(CRUCIBLE_RANKS[-1][2])["top_of_ladder"])
        self.assertFalse(crucible_rank_pure(CRUCIBLE_RANKS[-1][2] - 1)["top_of_ladder"])


class CrucibleEntryGateTest(unittest.TestCase):
    def test_the_combat_gate_refuses_entry_and_names_what_is_still_open(self):
        low = _player(20)
        self.assertLess(
            player_combat_level_pure(low), CRUCIBLE_MINIMUM_COMBAT_LEVEL
        )
        _data, ok, info = enter_crucible_pure(low, GE_ITEM_CATALOG)
        self.assertFalse(ok)
        self.assertIn(str(CRUCIBLE_MINIMUM_COMBAT_LEVEL), info["reason"])
        self.assertIn("lessons", info["reason"])

    def test_a_player_under_the_gate_can_still_earn_bones_from_the_lessons(self):
        """The four lessons are the whole of the sub-gate content, so they must work."""
        player = _player(20)
        for index, lesson in enumerate(CRUCIBLE_LESSONS, start=1):
            player, ok, info = take_crucible_lesson_pure(player, lesson)
            self.assertTrue(ok, info)
            self.assertEqual(player["inventory"][CRUCIBLE_CURRENCY], index)
        _again, ok, info = take_crucible_lesson_pure(player, CRUCIBLE_LESSONS[0])
        self.assertFalse(ok)
        self.assertIn("already taken", info["reason"])
        self.assertEqual(len(player["crucible_lessons_taken"]), len(CRUCIBLE_LESSONS))

    def test_the_fee_follows_the_sourced_formula_and_falls_as_risk_rises(self):
        bare = _player(60, equipment={}, carried_inventory={})
        quote = crucible_fee_quote_pure(bare, GE_ITEM_CATALOG)
        level = player_combat_level_pure(bare)
        self.assertEqual(
            quote["expected_risk"],
            CRUCIBLE_RISK_EXPECTATION_BASE
            + (level - CRUCIBLE_MINIMUM_COMBAT_LEVEL)
            * CRUCIBLE_RISK_EXPECTATION_PER_LEVEL,
        )
        self.assertEqual(quote["abandon_component"], CRUCIBLE_ABANDONMENT_FEE)
        self.assertEqual(
            quote["total"], quote["risk_component"] + quote["abandon_component"]
        )

        risking = _player(60)
        risking["carried_inventory"] = {"chicken": {"Rune platebody": 1}}
        risked = crucible_fee_quote_pure(risking, GE_ITEM_CATALOG)
        self.assertGreater(risked["risked_value"], quote["risked_value"])
        self.assertLess(risked["risk_component"], quote["risk_component"])

    def test_the_fee_curve_preserves_the_level_60_period_anchor(self):
        player = _player(53, equipment={}, carried_inventory={})
        self.assertEqual(player_combat_level_pure(player), 60)

        quote = crucible_fee_quote_pure(player, GE_ITEM_CATALOG)

        self.assertEqual(quote["expected_risk"], 450_000)
        self.assertEqual(quote["abandon_component"], 50_000)
        self.assertEqual(quote["total"], 500_000)

    def test_entry_is_refused_when_the_pouch_cannot_cover_the_fee(self):
        broke = _player(60, inventory={"Coins": 1})
        _data, ok, info = enter_crucible_pure(broke, GE_ITEM_CATALOG)
        self.assertFalse(ok)
        self.assertIn("bounty fee", info["reason"])

    def test_entry_gates_on_other_activities_and_open_encounters(self):
        busy = _player()
        busy["activity_session"] = {"active_id": "castle_wars"}
        _data, ok, info = enter_crucible_pure(busy, GE_ITEM_CATALOG)
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])

        fighting = _player()
        fighting["combat_encounter"] = {"target_id": "chicken", "enemy_lifepoints": 4}
        _data, ok, info = enter_crucible_pure(fighting, GE_ITEM_CATALOG)
        self.assertFalse(ok)
        self.assertIn("Combat encounter", info["reason"])

    def test_entry_takes_the_fee_claims_the_session_and_clamps_boosts(self):
        player = _player()
        player["combat_current_levels"] = {"attack": 99, "strength": 99}
        before = player["inventory"]["Coins"]
        quote = crucible_fee_quote_pure(player, GE_ITEM_CATALOG)
        entered, ok, info = enter_crucible_pure(player, GE_ITEM_CATALOG)
        self.assertTrue(ok, info)
        self.assertEqual(entered["inventory"]["Coins"], before - quote["total"])
        self.assertEqual(entered["crucible_fees_paid"], quote["total"])
        self.assertEqual(
            entered["activity_session"]["active_id"], CRUCIBLE_ACTIVITY_ID
        )
        self.assertEqual(
            entered["current_combat_target"], CRUCIBLE_COMBAT_TARGET_ID
        )
        self.assertTrue(info["boosts_clamped"])
        # base 60 + 5 + int(60 * 0.15) == 74 for Attack and Strength.
        self.assertEqual(entered["combat_current_levels"]["attack"], 74)
        self.assertEqual(entered["combat_current_levels"]["strength"], 74)

        _twice, ok, info = enter_crucible_pure(entered, GE_ITEM_CATALOG)
        self.assertFalse(ok)
        self.assertIn("already in the arena", info["reason"])


class CrucibleArenaTest(unittest.TestCase):
    def test_reviews_refuse_outside_the_arena_and_do_not_advance_unproductively(self):
        _data, ok, info = apply_crucible_review_pure(_player())
        self.assertFalse(ok)
        self.assertIn("Enter the Crucible arena", info["reason"])

        entered, ok, _ = enter_crucible_pure(_player(), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        held, ok, result = apply_crucible_review_pure(
            entered, equipment_data=EQUIPMENT_DATA, productive=False
        )
        self.assertTrue(ok)
        self.assertFalse(result["advanced"])
        self.assertEqual(held["crucible"]["review"], 0)

    def test_a_kill_pays_trophy_bones_a_rank_point_and_the_targets_fee(self):
        entered, ok, _ = enter_crucible_pure(_player(99), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        coins_before = entered["inventory"]["Coins"]
        played, results = _play(
            entered, 7, limit=120, until=lambda _p, r: bool(r.get("bones"))
        )
        killed = results[-1]
        self.assertEqual(killed["bones"], CRUCIBLE_BONES_PER_KILL)
        self.assertEqual(
            played["inventory"][CRUCIBLE_CURRENCY], CRUCIBLE_BONES_PER_KILL
        )
        self.assertEqual(played["crucible_kills"], 1)
        self.assertGreater(played["crucible_fees_won"], 0)
        self.assertGreater(played["inventory"]["Coins"], coins_before)
        self.assertGreaterEqual(played["crucible_rank_points"], 1)
        # Real combat experience, not a bookkeeping award.
        self.assertTrue(any(r["combat"].get("xp_rewards") for r in results))

    def test_a_supreme_champion_event_arrives_on_its_own_cadence_and_is_safe(self):
        entered, ok, _ = enter_crucible_pure(_player(99), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        entered["shop_market_clock"]["answered_cards"] = (
            CRUCIBLE_EVENT_INTERVAL_REVIEWS - 2
        )
        played, results = _play(
            entered,
            3,
            limit=4,
            until=lambda _p, r: bool(r.get("event_active")),
        )
        # Three cards elapsed outside this visit. The world event therefore
        # arrives on review two, not after five private Crucible reviews.
        self.assertEqual(len(results), 2)
        self.assertEqual(played["shop_market_clock"]["answered_cards"], 5)
        self.assertEqual(played["crucible"]["review"], 2)
        self.assertTrue(results[-1]["event_active"])
        self.assertFalse(results[-1]["is_champion"])
        self.assertFalse(crucible_view_pure(played)["dangerous"])

        # Exactly one rank point per successful hit on the champion, and none
        # at all for a review that landed nothing.
        landed = [
            row
            for row in results
            if row["event_active"] and int(row["combat"].get("player_damage") or 0)
        ]
        missed = [
            row
            for row in results
            if row["event_active"]
            and not int(row["combat"].get("player_damage") or 0)
            and not row.get("bones")
        ]
        self.assertTrue(landed or missed)
        for row in landed:
            self.assertGreaterEqual(
                row["points_gained"], CRUCIBLE_POINTS_PER_CHAMPION_HIT
            )
        for row in missed:
            self.assertEqual(row["points_gained"], 0)

    def test_champion_selection_does_not_change_after_the_event_starts(self):
        player = _player(
            99,
            crucible_rank_points=CRUCIBLE_RANKS[-1][2] - 1,
        )
        entered, ok, _ = enter_crucible_pure(player, GE_ITEM_CATALOG)
        self.assertTrue(ok)
        entered["shop_market_clock"]["answered_cards"] = (
            CRUCIBLE_EVENT_INTERVAL_REVIEWS - 1
        )
        entered = advance_shop_market_clock_pure(entered)

        played, ok, result = apply_crucible_review_pure(
            entered,
            lambda: 0.0,
            equipment_data=EQUIPMENT_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(result["points_gained"], 1)
        self.assertTrue(result["rank"]["top_of_ladder"])
        self.assertFalse(result["is_champion"])
        self.assertFalse(crucible_view_pure(played)["is_champion"])

    def test_a_dangerous_death_keeps_three_items_and_pays_the_victor(self):
        """No gravestone, no Death's Office, and the risk fee is gone.

        `sendPVPItemsOnDeath` keeps three items on an unskulled death, so what is
        destroyed is everything past those three.
        """
        entered, ok, _ = enter_crucible_pure(_armoured_player(), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        escrow = entered["crucible"]["risk_escrow"]
        abandon = entered["crucible"]["abandon_escrow"]
        coins = entered["inventory"]["Coins"]
        played, results = _play(
            entered,
            11,
            limit=200,
            until=lambda _p, r: r.get("outcome") == "death",
        )
        died = results[-1]
        self.assertEqual(played["crucible_deaths"], 1)
        self.assertEqual(played["combat_grave"], {})
        self.assertEqual(played["death_office"], {})
        self.assertEqual(
            played["equipment"],
            {
                "weapon": "Mithril scimitar",
                "body": "Mithril platebody",
                "legs": "Mithril platelegs",
            },
        )
        self.assertEqual(played["inventory"].get("Lobster", 0), 0)
        self.assertEqual(died["fee_forfeited"], escrow)
        self.assertEqual(died["fee_refunded"], abandon)
        # The pouch is exactly the abandonment refund plus whatever fees the
        # targets this visit paid over; the risk component is gone for good.
        self.assertEqual(
            played["inventory"]["Coins"],
            coins + abandon + played["crucible_fees_won"],
        )
        self.assertEqual(played["crucible"], {})
        self.assertEqual(played["activity_session"]["active_id"], "")

    def test_protect_item_saves_nothing_extra_unlike_every_other_dangerous_area(self):
        """Both pinned revisions say Protect Item is disabled inside the Crucible.

        Elsewhere the prayer raises the kept count from three to four; here the
        arena must ignore it, so the death still keeps only the sourced three.
        """
        entered, ok, _ = enter_crucible_pure(
            _armoured_player(protect_item=True), GE_ITEM_CATALOG
        )
        self.assertTrue(ok)
        played, _results = _play(
            entered,
            11,
            limit=200,
            until=lambda _p, r: r.get("outcome") == "death",
        )
        self.assertEqual(len(played["equipment"]), 3)
        self.assertEqual(played["inventory"].get("Lobster", 0), 0)
        # The player's own prayer selection is left exactly as they set it.
        self.assertIn("protect_item", played["combat_selected_prayers"])

    def test_leaving_abandons_the_target_and_splits_the_fee_the_sourced_way(self):
        entered, ok, _ = enter_crucible_pure(_player(), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        coins = entered["inventory"]["Coins"]
        risk = entered["crucible"]["risk_escrow"]
        left, ok, info = leave_crucible_pure(entered)
        self.assertTrue(ok, info)
        self.assertEqual(info["fee_forfeited"], CRUCIBLE_ABANDONMENT_FEE)
        self.assertEqual(info["fee_refunded"], risk)
        self.assertEqual(left["inventory"]["Coins"], coins + risk)
        self.assertEqual(left["crucible_abandons"], 1)
        self.assertEqual(left["crucible"], {})
        self.assertEqual(left["current_combat_target"], "chicken")

        _again, ok, info = leave_crucible_pure(left)
        self.assertFalse(ok)
        self.assertIn("not in the Crucible arena", info["reason"])


class CrucibleRewardTest(unittest.TestCase):
    """Every purchasable row is bought with bones the arena actually paid out."""

    @classmethod
    def setUpClass(cls):
        player = _player(99, coins=50_000_000)
        for lesson in CRUCIBLE_LESSONS:
            player, ok, info = take_crucible_lesson_pure(player, lesson)
            assert ok, info
        player, ok, info = enter_crucible_pure(player, GE_ITEM_CATALOG)
        assert ok, info
        target = max(row.cost for row in CRUCIBLE_UNLOCKS) + CRUCIBLE_SUPREME_HELM_COST
        player, _results = _play(
            player,
            7,
            limit=4000,
            reenter=True,
            until=lambda p, _r: (
                p["inventory"].get(CRUCIBLE_CURRENCY, 0) >= target
                and p["crucible_supreme_champion"]
            ),
        )
        player, ok, info = leave_crucible_pure(player)
        assert ok, info
        cls.earned = player

    def test_the_arena_really_named_the_player_supreme_champion(self):
        self.assertTrue(self.earned["crucible_supreme_champion"])
        self.assertEqual(self.earned["crucible_best_tier"], CRUCIBLE_SUPREME_TIER)
        self.assertGreaterEqual(
            self.earned["crucible_rank_points"], CRUCIBLE_RANKS[-1][2]
        )
        self.assertGreater(self.earned["crucible_kills"], 0)

    def test_every_taunt_and_title_can_be_bought_with_earned_bones(self):
        for unlock in CRUCIBLE_UNLOCKS:
            player = copy.deepcopy(self.earned)
            bought, ok, info = buy_crucible_unlock_pure(player, unlock.id)
            self.assertTrue(ok, f"{unlock.id}: {info}")
            self.assertIn(unlock.id, bought["crucible_unlocks"])
            self.assertEqual(
                bought["inventory"][CRUCIBLE_CURRENCY],
                player["inventory"][CRUCIBLE_CURRENCY] - unlock.cost,
            )
            _twice, ok, info = buy_crucible_unlock_pure(bought, unlock.id)
            self.assertFalse(ok)
            self.assertIn("already own", info["reason"])

    def test_the_helm_needs_the_championship_and_then_actually_arrives(self):
        never = _player(99)
        never["inventory"] = {
            "Coins": 1_000_000,
            CRUCIBLE_CURRENCY: CRUCIBLE_SUPREME_HELM_COST,
        }
        _data, ok, info = buy_crucible_supreme_helm_pure(never)
        self.assertFalse(ok)
        self.assertIn("Supreme Champion", info["reason"])

        bought, ok, info = buy_crucible_supreme_helm_pure(
            copy.deepcopy(self.earned)
        )
        self.assertTrue(ok, info)
        self.assertEqual(bought["inventory"][CRUCIBLE_SUPREME_HELM], 1)
        self.assertEqual(
            bought["inventory"][CRUCIBLE_CURRENCY],
            self.earned["inventory"][CRUCIBLE_CURRENCY]
            - CRUCIBLE_SUPREME_HELM_COST,
        )
        _twice, ok, info = buy_crucible_supreme_helm_pure(bought)
        self.assertFalse(ok)
        self.assertIn("already own", info["reason"])

    def test_an_active_taunt_and_title_actually_appear_when_a_target_falls(self):
        """A cosmetic nobody ever sees would be a purchase that does nothing."""
        player = copy.deepcopy(self.earned)
        for unlock in (CRUCIBLE_TAUNTS[0], CRUCIBLE_TITLES[0]):
            player, ok, info = buy_crucible_unlock_pure(player, unlock.id)
            self.assertTrue(ok, info)
            player, ok, info = set_crucible_cosmetic_pure(
                player, unlock.kind, unlock.id
            )
            self.assertTrue(ok, info)
        player, ok, info = enter_crucible_pure(player, GE_ITEM_CATALOG)
        self.assertTrue(ok, info)
        played, results = _play(
            player,
            7,
            limit=400,
            reenter=True,
            until=lambda _p, r: bool(r.get("bones")),
        )
        events = " ".join(results[-1]["events"])
        self.assertIn(CRUCIBLE_TAUNTS[0].display_name, events)
        # The title is a label on the defeated target, so its [name] token is
        # replaced by whoever just fell rather than shown literally.
        self.assertIn("Cowardly Crucible target", events)
        self.assertNotIn("[name]", events)
        self.assertIn(CRUCIBLE_TAUNTS[0].display_name, played["crucible_last_result"])

    def test_a_cosmetic_cannot_be_worn_before_it_is_bought(self):
        _data, ok, info = set_crucible_cosmetic_pure(
            copy.deepcopy(self.earned), "taunt", CRUCIBLE_TAUNTS[0].id
        )
        self.assertFalse(ok)
        self.assertIn("Buy that reward", info["reason"])

        owned, ok, _ = buy_crucible_unlock_pure(
            copy.deepcopy(self.earned), CRUCIBLE_TAUNTS[0].id
        )
        self.assertTrue(ok)
        chosen, ok, info = set_crucible_cosmetic_pure(
            owned, "taunt", CRUCIBLE_TAUNTS[0].id
        )
        self.assertTrue(ok, info)
        self.assertEqual(chosen["crucible_taunt"], CRUCIBLE_TAUNTS[0].id)

        _wrong, ok, info = set_crucible_cosmetic_pure(
            owned, "title", CRUCIBLE_TAUNTS[0].id
        )
        self.assertFalse(ok)
        self.assertIn("not a death title", info["reason"])

        cleared, ok, _ = set_crucible_cosmetic_pure(chosen, "taunt", "")
        self.assertTrue(ok)
        self.assertEqual(cleared["crucible_taunt"], "")


class CrucibleViewTest(unittest.TestCase):
    def test_the_view_owns_every_flag_the_panel_renders(self):
        view = crucible_view_pure(_player(), GE_ITEM_CATALOG)
        for key in (
            "active",
            "can_enter",
            "entry_reasons",
            "combat_level",
            "minimum_combat_level",
            "bones",
            "fee",
            "rank",
            "event_active",
            "is_champion",
            "dangerous",
            "status_label",
            "entry_warning",
            "summary_text",
            "progress_value",
            "progress_maximum",
            "progress_format",
            "primary_label",
            "primary_enabled",
            "leave_visible",
            "lesson_options",
            "shop_options",
            "supreme_helm",
            "shop_controls_enabled",
            "source",
        ):
            self.assertIn(key, view)
        self.assertTrue(view["can_enter"])
        self.assertTrue(view["dangerous"])
        self.assertEqual(view["primary_label"], "Pay fee and enter")
        self.assertFalse(view["leave_visible"])
        self.assertIn("Protect Item is disabled", view["entry_warning"])
        self.assertEqual(len(view["shop_options"]), len(CRUCIBLE_UNLOCKS))
        self.assertEqual(len(view["lesson_options"]), len(CRUCIBLE_LESSONS))

    def test_the_view_reports_why_entry_is_locked_rather_than_hiding_it(self):
        view = crucible_view_pure(_player(20), GE_ITEM_CATALOG)
        self.assertFalse(view["can_enter"])
        self.assertTrue(
            any(
                str(CRUCIBLE_MINIMUM_COMBAT_LEVEL) in reason
                for reason in view["entry_reasons"]
            )
        )

    def test_no_shop_row_is_enabled_before_its_price_is_affordable(self):
        view = crucible_view_pure(_player(), GE_ITEM_CATALOG)
        self.assertEqual(view["bones"], 0)
        self.assertFalse(any(row["enabled"] for row in view["shop_options"]))
        self.assertFalse(view["supreme_helm"]["enabled"])
        self.assertIn("Supreme Champion", view["supreme_helm"]["reason"])

    def test_an_active_visit_flips_the_arena_flags(self):
        entered, ok, _ = enter_crucible_pure(_player(), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        view = crucible_view_pure(entered, GE_ITEM_CATALOG)
        self.assertTrue(view["active"])
        self.assertTrue(view["leave_visible"])
        self.assertFalse(view["can_enter"])
        self.assertFalse(view["shop_controls_enabled"])
        self.assertEqual(view["status_label"], "ACTIVE · DANGEROUS")


class CruciblePersistenceTest(unittest.TestCase):
    def test_sanitize_drops_a_session_owned_by_another_activity(self):
        entered, ok, _ = enter_crucible_pure(_player(), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        entered["activity_session"] = {"active_id": "castle_wars"}
        self.assertEqual(sanitize_crucible_state_pure(entered)["crucible"], {})

    def test_sanitize_normalizes_junk_ledgers_unlocks_and_cosmetics(self):
        state = sanitize_crucible_state_pure(
            {
                "crucible": {"visit_number": 1},
                "crucible_rank_points": -12,
                "crucible_kills": "eleven",
                "crucible_unlocks": ["taunt_1", "not_a_reward", "taunt_1"],
                "crucible_taunt": "taunt_2",
                "crucible_title": "title_1",
                "crucible_lessons_taken": ["Crucible Key", "Nonsense"],
                "crucible_best_tier": 99,
            }
        )
        self.assertEqual(state["crucible"], {})
        self.assertEqual(state["crucible_rank_points"], 0)
        self.assertEqual(state["crucible_kills"], 0)
        self.assertEqual(state["crucible_unlocks"], ("taunt_1",))
        # taunt_2 and title_1 were never bought, so neither can be active.
        self.assertEqual(state["crucible_taunt"], "")
        self.assertEqual(state["crucible_title"], "")
        self.assertEqual(state["crucible_lessons_taken"], ("Crucible Key",))
        self.assertEqual(state["crucible_best_tier"], CRUCIBLE_SUPREME_TIER)

    def test_an_older_save_migrates_without_losing_unrelated_keys(self):
        old = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        old["config_version"] = 85
        old["unrelated_future_key"] = {"keep": True}
        for key in default_crucible_state_pure():
            old.pop(key, None)
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertGreaterEqual(CURRENT_CONFIG_VERSION, 86)
        self.assertEqual(migrated["crucible"], {})
        self.assertEqual(migrated["crucible_rank_points"], 0)
        self.assertEqual(migrated["crucible_unlocks"], ())
        self.assertFalse(migrated["crucible_supreme_champion"])
        self.assertEqual(migrated["unrelated_future_key"], {"keep": True})

    def test_an_interrupted_visit_survives_a_save_and_load_round_trip(self):
        entered, ok, _ = enter_crucible_pure(_player(), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        entered, ok, _ = apply_crucible_review_pure(
            entered, random.Random(5).random, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok)
        reloaded = migrate_loaded_data(
            json.loads(json.dumps(entered)), ORE_DATA, ITEM_DEFINITIONS
        )
        self.assertEqual(reloaded["crucible"]["review"], 1)
        self.assertEqual(
            reloaded["crucible"]["risk_escrow"], entered["crucible"]["risk_escrow"]
        )
        self.assertEqual(
            reloaded["activity_session"]["active_id"], CRUCIBLE_ACTIVITY_ID
        )
        self.assertNotIn("event_reviews_remaining", reloaded["crucible"])
        self.assertNotIn("next_event_review", reloaded["crucible"])
        self.assertEqual(reloaded["crucible"]["event_card"], 0)
        self.assertFalse(reloaded["crucible"]["is_champion"])


class CrucibleCommandTest(unittest.TestCase):
    def test_the_command_router_covers_every_direct_action(self):
        player = _player(99)
        taught, ok, _ = apply_crucible_command_pure(
            player, "take_lesson", {"lesson": CRUCIBLE_LESSONS[0]}
        )
        self.assertTrue(ok)
        self.assertEqual(taught["inventory"][CRUCIBLE_CURRENCY], 1)

        stocked = copy.deepcopy(taught)
        stocked["inventory"][CRUCIBLE_CURRENCY] = 100
        stocked["crucible_supreme_champion"] = True
        bought, ok, _ = apply_crucible_command_pure(
            stocked, "buy_unlock", {"unlock_id": CRUCIBLE_TITLES[0].id}
        )
        self.assertTrue(ok)
        chosen, ok, _ = apply_crucible_command_pure(
            bought, "set_title", {"unlock_id": CRUCIBLE_TITLES[0].id}
        )
        self.assertTrue(ok)
        self.assertEqual(chosen["crucible_title"], CRUCIBLE_TITLES[0].id)
        helmed, ok, _ = apply_crucible_command_pure(chosen, "buy_supreme_helm", {})
        self.assertTrue(ok)
        self.assertEqual(helmed["inventory"][CRUCIBLE_SUPREME_HELM], 1)

        entered, ok, _ = apply_crucible_command_pure(
            helmed, "enter", {"price_catalog": GE_ITEM_CATALOG}
        )
        self.assertTrue(ok)
        self.assertTrue(entered["crucible"])
        left, ok, _ = apply_crucible_command_pure(entered, "leave", {})
        self.assertTrue(ok)
        self.assertEqual(left["crucible"], {})

        _data, ok, info = apply_crucible_command_pure(player, "nonsense", {})
        self.assertFalse(ok)
        self.assertIn("Unknown Crucible command", info["reason"])

        _data, ok, info = apply_crucible_command_pure(
            player, "set_taunt", {"unlock_id": "not_a_reward"}
        )
        self.assertFalse(ok)


class CrucibleRuntimeIntegrationTest(unittest.TestCase):
    def test_a_selected_visit_dispatches_reviews_through_the_real_runtime(self):
        player, ok, _ = enter_crucible_pure(_player(99), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        calls = _calls(3)
        ctx = _context(player, calls)
        self.assertTrue(handle_crucible_answer(ctx))
        self.assertEqual(player["crucible"]["review"], 1)
        self.assertEqual(calls["saves"], 1)
        self.assertTrue(calls["activity"])
        self.assertFalse(calls["errors"])

    def test_runtime_reads_the_shared_world_card_for_the_safe_event(self):
        player, ok, _ = enter_crucible_pure(_player(99), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        player["shop_market_clock"]["answered_cards"] = (
            CRUCIBLE_EVENT_INTERVAL_REVIEWS
        )
        calls = _calls(3)

        self.assertTrue(handle_crucible_answer(_context(player, calls)))

        view = crucible_view_pure(player)
        self.assertTrue(view["event_active"])
        self.assertFalse(view["dangerous"])
        self.assertEqual(player["crucible"]["event_card"], 5)

    def test_the_runtime_records_a_dangerous_death_as_a_failure_and_stands_down(self):
        player, ok, _ = enter_crucible_pure(_armoured_player(), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        calls = _calls(11)
        ctx = _context(player, calls)
        for _ in range(200):
            self.assertTrue(handle_crucible_answer(ctx))
            if not player["crucible"]:
                break
        else:
            raise AssertionError("the arena never produced a death")
        self.assertEqual(player["crucible_deaths"], 1)
        self.assertTrue(calls.get("deactivated"))
        self.assertEqual(player["combat_grave"], {})

    def test_an_unselected_activity_refuses_the_review_and_deactivates(self):
        player = _player()
        calls = _calls()
        ctx = _context(player, calls)
        self.assertFalse(handle_crucible_answer(ctx))
        self.assertTrue(calls["errors"])
        self.assertTrue(calls.get("deactivated"))

    def test_a_full_lifepoint_reset_never_happens_outside_the_safe_event(self):
        """A dangerous visit must not quietly heal the player between reviews."""
        player, ok, _ = enter_crucible_pure(_player(99), GE_ITEM_CATALOG)
        self.assertTrue(ok)
        maximum = combat_max_lifepoints_pure(player)
        played, results = _play(
            player,
            13,
            limit=60,
            until=lambda p, r: (
                not r.get("event_active") and p["combat_lifepoints"] < maximum
            ),
        )
        self.assertLess(played["combat_lifepoints"], maximum)
        self.assertTrue(results)


if __name__ == "__main__":
    unittest.main()
