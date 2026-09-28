"""An altar teleport settles a finished bank trip before the next action."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic.achievement_diary_logic import refresh_achievement_diaries_pure
from ankiscape.logic.wicked_hood_logic import (
    default_wicked_hood_state_pure,
    runecrafting_route_phases_pure,
)
from ankiscape.runtime.runtime_actions import (
    handle_runecrafting_answer,
    run_answer_with_carried_overlay,
)
from tests.test_runtime_actions import _context


TARGET = "craft_air_runes"
BANK_DEED = "burthorpe_period_bank_on_it"


def _arrival_context():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    hood = default_wicked_hood_state_pure()
    hood.update(fed_altars=["air"], pending_altar_teleport="air")
    player.update(
        inventory={"Rune essence": 56, "Air rune": 28},
        equipment={"head": "Wicked hood"},
        current_runecrafting=TARGET,
        summoning_level=52,
        wicked_hood=hood,
        carried_inventory={TARGET: {"Air rune": 28}},
        carried_churn={TARGET: 28},
        carried_primed_targets={TARGET: True},
        skilling_bank_run={
            "target_id": TARGET, "reviews_total": 20, "reviews_remaining": 5,
            "route_phases": list(runecrafting_route_phases_pure(20)),
        },
    )
    player["summoning_state"]["summoning_points_current"] = 7
    player["quests"]["rune_mysteries"]["completed"] = True
    player.pop("skilling_bank_run_requested")
    ctx = _context(player, random_values=[0.99] * 128)
    observations = {"refreshes": [], "checks": [], "saves": []}

    def check(data):
        updated, _newly = refresh_achievement_diaries_pure(data)
        data.update(updated)
        observations["checks"].append(copy.deepcopy(data))

    ctx.check_achievements = check
    ctx.refresh_carried_inventory = lambda: observations["refreshes"].append(copy.deepcopy(player))
    ctx.save_player_data = lambda: observations["saves"].append(copy.deepcopy(player))
    return ctx, observations


class TeleportArrivalSettlementTest(unittest.TestCase):
    def test_teleport_arrival_settles_before_runecrafting_and_spends_requests(self):
        for request in (None, "review_bank_run_requested_target", "skilling_bank_run_requested"):
            with self.subTest(request=request):
                ctx, seen = _arrival_context()
                player = ctx.player_data
                if request:
                    player[request] = TARGET
                self.assertTrue(run_answer_with_carried_overlay(ctx, "runecrafting", handle_runecrafting_answer))
                self.assertEqual(player["summoning_state"]["summoning_points_current"], 52)
                self.assertIn(BANK_DEED, player["achievement_diaries"]["completed_tasks"])
                self.assertNotIn("review_bank_run_requested_target", player)
                self.assertNotIn("skilling_bank_run_requested", player)
                self.assertEqual(player["skilling_bank_run"], {})
                self.assertEqual(player["wicked_hood"]["pending_altar_teleport"], "")
                self.assertEqual(player["inventory"], {"Rune essence": 28, "Air rune": 56})
                self.assertEqual(len(seen["refreshes"]), 1)
                self.assertEqual(seen["refreshes"][0]["carried_churn"].get(TARGET, 0), 0)
                self.assertEqual(seen["checks"][0]["inventory"]["Rune essence"], 56)
                self.assertIn(BANK_DEED, seen["saves"][0]["achievement_diaries"]["completed_tasks"])

    def test_arrival_preserves_same_review_crafting_with_live_cadence(self):
        ctx, seen = _arrival_context()
        player = ctx.player_data
        ctx.cadence_live_enabled = True
        self.assertTrue(run_answer_with_carried_overlay(ctx, "runecrafting", handle_runecrafting_answer))
        self.assertEqual(player["inventory"], {"Rune essence": 28, "Air rune": 56})
        self.assertEqual(seen["saves"][-1]["summoning_state"]["summoning_points_current"], 52)
        self.assertIn(BANK_DEED, seen["saves"][-1]["achievement_diaries"]["completed_tasks"])
        self.assertEqual(len(seen["refreshes"]), 1)

    def test_arrival_persists_when_the_real_handler_has_no_essence(self):
        ctx, seen = _arrival_context()
        ctx.player_data["inventory"].pop("Rune essence")
        self.assertFalse(run_answer_with_carried_overlay(ctx, "runecrafting", handle_runecrafting_answer))
        saved = seen["saves"][-1]
        self.assertEqual(saved["summoning_state"]["summoning_points_current"], 52)
        self.assertIn(BANK_DEED, saved["achievement_diaries"]["completed_tasks"])
        self.assertEqual(saved["skilling_bank_run"], {})

    def test_arrival_diary_coins_survive_same_review_crafting(self):
        ctx, seen = _arrival_context()
        player = ctx.player_data
        player["conquest_games_won"] = 1
        self.assertTrue(run_answer_with_carried_overlay(ctx, "runecrafting", handle_runecrafting_answer))
        arrival = seen["checks"][0]
        self.assertIn("miscellaneous_miscellaneous_conquest", arrival["achievement_diaries"]["completed_tasks"])
        coins = arrival["inventory"].get("Coins", 0)
        self.assertGreater(coins, 0)
        self.assertEqual(player["inventory"].get("Coins", 0), coins)
        self.assertEqual(seen["saves"][-1]["inventory"].get("Coins", 0), coins)

    def test_newly_loaded_essence_does_not_count_as_a_deposit(self):
        for carried in ({}, {"Coins": 100}):
            with self.subTest(carried=carried):
                ctx, seen = _arrival_context()
                ctx.player_data["carried_inventory"][TARGET] = carried
                self.assertTrue(run_answer_with_carried_overlay(ctx, "runecrafting", handle_runecrafting_answer))
                self.assertNotIn(BANK_DEED, ctx.player_data["achievement_diaries"]["completed_tasks"])
                self.assertEqual(seen["saves"][-1]["summoning_state"]["summoning_points_current"], 52)

    def test_teleport_with_travel_remaining_does_not_settle_arrival(self):
        ctx, seen = _arrival_context()
        player = ctx.player_data
        player["skilling_bank_run"]["reviews_remaining"] = 15
        self.assertTrue(run_answer_with_carried_overlay(ctx, "runecrafting", handle_runecrafting_answer))
        self.assertEqual(player["skilling_bank_run"]["reviews_remaining"], 4)
        self.assertEqual(player["summoning_state"]["summoning_points_current"], 7)
        self.assertNotIn(BANK_DEED, player["achievement_diaries"]["completed_tasks"])
        self.assertEqual(seen["checks"], [])
        self.assertEqual(seen["refreshes"], [])
        self.assertEqual(player["inventory"]["Rune essence"], 56)
