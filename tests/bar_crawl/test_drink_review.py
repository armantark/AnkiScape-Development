"""Accepted visits, refusals and reviewer Undo share one drink transaction."""
from __future__ import annotations

import copy
import random
import sys
import types
import unittest
from unittest.mock import Mock, patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure import apply_quest_progress_pure, quest_current_stage_pure
from ankiscape.runtime.runtime_actions_quest import handle_quest_answer
from tests.bar_crawl.test_drink_effects import EXPECTED_50, level_player
from tests.bar_crawl.test_quest_route import BAR_ROUTE
from tests.test_runtime_actions import _context


def started_player(stage):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(level_player())
    player["current_quest"] = "bar_crawl"
    player["quests"]["bar_crawl"] = {"started": True, "progress": stage, "completed": False}
    player["inventory"] = {"Barcrawl card": 1, "Coins": BAR_ROUTE[stage - 2][2] if 2 <= stage <= 11 else 0}
    return player


def review(player, draw=0.999999):
    calls = {"xp": [], "saves": 0, "errors": []}
    ctx = _context(player, calls)
    ctx.random_random = Mock(return_value=draw)
    ok = handle_quest_answer(ctx)
    return ok, calls, ctx.random_random


def effect_state(player):
    return {key: copy.deepcopy(value) for key, value in player.items()
            if key.startswith("combat_") or key.endswith(("_level", "_exp")) or key == "equipment"}


class TestDrinkReview(unittest.TestCase):
    def test_each_visit_applies_exact_effect_payment_proof_stage_and_one_save(self):
        for stage, (name, bar, price) in enumerate(BAR_ROUTE, 2):
            with self.subTest(stage=stage):
                player = started_player(stage)
                before = copy.deepcopy(player)
                ok, calls, rng = review(player)
                self.assertTrue(ok)
                expected = effect_state(before)
                expected["combat_current_levels"] = EXPECTED_50[stage - 2]
                expected["combat_prayer_points"] = 440 if stage == 4 else 500
                expected["combat_lifepoints"] = {2: 480, 3: 453, 6: 350, 10: 300}.get(stage, 500)
                self.assertEqual(effect_state(player), expected)
                self.assertEqual(player["inventory"], {"Barcrawl card": 1, "Coins": 0})
                self.assertEqual(player["quest_action_proofs"], [f"Drink {name} at {bar}"])
                self.assertEqual(quest_current_stage_pure(player, "bar_crawl", QUEST_DATA), stage + 1)
                self.assertEqual(calls["saves"], 1)
                self.assertEqual(calls["errors"], [])
                self.assertEqual(rng.call_count, int(stage in (2, 3, 6, 10)))
                self.assertEqual(before["inventory"]["Coins"], price)

    def test_every_visit_refuses_missing_card_or_insufficient_coins_without_any_effect(self):
        for stage in range(2, 12):
            for missing in ("Coins", "Barcrawl card"):
                with self.subTest(stage=stage, missing=missing):
                    player = started_player(stage)
                    player["inventory"][missing] -= 1
                    before = copy.deepcopy(player)
                    ok, calls, rng = review(player)
                    self.assertFalse(ok)
                    self.assertEqual(player, before)
                    self.assertEqual(calls["saves"], 0)
                    rng.assert_not_called()

    def test_card_receipt_guard_return_completed_and_other_quest_do_not_drink(self):
        for stage in (1, 12, 13):
            with self.subTest(stage=stage):
                player = started_player(stage)
                if stage == 1:
                    del player["inventory"]["Barcrawl card"]
                if stage == 13:
                    player["quests"]["bar_crawl"]["completed"] = True
                before = effect_state(player)
                ok, calls, rng = review(player)
                self.assertEqual(ok, stage != 13)
                self.assertEqual(effect_state(player), before)
                rng.assert_not_called()
                self.assertEqual(calls["saves"], int(stage != 13))
                if stage == 1:
                    self.assertEqual(player["inventory"]["Barcrawl card"], 1)
                if stage == 12:
                    self.assertTrue(player["quests"]["bar_crawl"]["completed"])
        player = started_player(2)
        player["current_quest"] = "rune_mysteries"
        player["inventory"]["Air talisman"] = 1
        player["quests"]["rune_mysteries"] = {"started": True, "progress": 1, "completed": False}
        before = effect_state(player)
        ok, calls, rng = review(player)
        self.assertTrue(ok)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(effect_state(player), before)
        rng.assert_not_called()

    def test_unavailable_quest_and_rejected_progress_do_not_drink(self):
        for guard in ("can_start_quest_pure", "apply_quest_progress_pure"):
            with self.subTest(guard=guard):
                player = started_player(2)
                before = copy.deepcopy(player)
                result = False if guard == "can_start_quest_pure" else (player, False, False, None)
                with patch(f"ankiscape.runtime.runtime_actions_quest.{guard}", return_value=result):
                    ok, calls, rng = review(player)
                self.assertFalse(ok)
                self.assertEqual(player, before)
                self.assertEqual(calls["saves"], 0)
                rng.assert_not_called()

    def test_next_visit_does_not_replay_gutrot_and_generic_progress_has_no_effect(self):
        player = started_player(2)
        player["inventory"]["Coins"] = 60
        self.assertTrue(review(player)[0])
        currents = copy.deepcopy(player["combat_current_levels"])
        ok, calls, rng = review(player)
        self.assertTrue(ok)
        self.assertEqual(player["combat_current_levels"], currents)
        self.assertEqual(player["combat_lifepoints"], 433)
        rng.assert_called_once_with()
        player = started_player(2)
        before = effect_state(player)
        updated, ok, _ = apply_quest_progress_pure(player, "bar_crawl", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(effect_state(updated), before)


class TestDrinkReviewUndo(unittest.TestCase):
    def setUp(self):
        from tests.test_integration_smoke import _install_runtime_fakes
        original_modules = dict(sys.modules)

        def restore_modules():
            sys.modules.clear()
            sys.modules.update(original_modules)

        self.addCleanup(restore_modules)
        self.addCleanup(random.setstate, random.getstate())
        _install_runtime_fakes()

    def test_gutrot_review_undo_restores_complete_player_and_random_state_and_replays(self):
        from tests.test_integration_smoke import _FakeReviewer, _load_addon_as_package
        addon = _load_addon_as_package("ankiscape_barcrawl_drink_undo")
        addon.level_up_check = lambda *_: None
        addon.check_achievements = lambda *_: None
        addon.save_player_data = Mock()
        addon.update_review_hud = lambda *_: None
        addon._show_exp = lambda *_: None
        addon._show_activity_gain = lambda *_: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda title, message: self.fail(f"{title}: {message}")
        addon._state.player_data = started_player(2)
        addon._state.current_skill = "Quests"
        addon._state.review_undo_stack.clear()
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        random.seed(42)
        before_random = random.getstate()
        before_player = copy.deepcopy(addon._state.player_data)
        self.assertEqual(addon.on_answer_card(_FakeReviewer(), 4, lambda *_: "answered"), "answered")
        result = copy.deepcopy(addon._state.player_data)
        after_random = random.getstate()
        self.assertEqual(result["combat_lifepoints"], 487)
        self.assertEqual(result["combat_current_levels"], {"attack": 42, "defense": 43, "strength": 43, "smithing": 44})
        self.assertEqual(result["inventory"]["Coins"], 0)
        self.assertEqual(result["quest_action_proofs"], ["Drink Uncle Humphrey's Gutrot at Blue Moon Inn"])
        self.assertEqual(result["quests"]["bar_crawl"]["progress"], 3)
        self.assertEqual(result["combat_recovery_progress"], before_player["combat_recovery_progress"])
        self.assertEqual(result["combat_rest_reviews"], before_player["combat_rest_reviews"])
        self.assertNotEqual(after_random, before_random)
        self.assertEqual(len(addon._state.review_undo_stack), 1)
        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before_player)
        self.assertEqual(random.getstate(), before_random)
        self.assertEqual(addon._state.review_undo_stack, [])
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda *_: "answered")
        self.assertEqual(addon._state.player_data, result)
        self.assertEqual(random.getstate(), after_random)
