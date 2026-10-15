"""Familiarisation survives Again and completes on the fourth successful review."""

import copy
import types
import unittest

from tests import test_farming_dispatch as farming
from tests.test_integration_smoke import _FakeReviewer, _load_addon_as_package
from tests.test_summoning_logic import (
    ORE_DATA, default_player_data, migrate_loaded_data, start_familiarisation_pure,
)


class FamiliarisationReviewTests(unittest.TestCase):
    setUp = farming.TestFarmingReviewDispatch.setUp
    tearDown = farming.TestFarmingReviewDispatch.tearDown
    _configure = farming.TestFarmingReviewDispatch._configure

    def _answer(self, addon, ease):
        addon._state.card_turned = addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), ease, lambda *_args: "answered")

    def test_real_reviews_pause_complete_undo_and_replay(self):
        addon = _load_addon_as_package("ankiscape_familiarisation_fairness")
        self._configure(addon)
        addon.show_error_message = lambda *_args: None
        data, ok = start_familiarisation_pure(default_player_data(ORE_DATA))
        self.assertTrue(ok)
        addon._state.player_data = data
        addon._state.current_skill = "Woodcutting"
        initial_cooldown = data["summoning_state"]["familiarisation"]["cooldown_reviews_remaining"]
        successes = 0
        for index, ease in enumerate((1, 2, 1, 3, 1, 4, 1), start=1):
            self._answer(addon, ease)
            successes += int(ease > 1)
            state = addon._state.player_data["summoning_state"]["familiarisation"]
            self.assertEqual(state["segments"], successes)
            self.assertEqual(state["raw_shards"], successes * 15)
            self.assertTrue(state["active"])
            self.assertFalse(state["awaiting_reward"])
            self.assertNotIn("focus", state)
            self.assertEqual(state["cooldown_reviews_remaining"], initial_cooldown - index)
        before = copy.deepcopy(addon._state.player_data)
        before_rng = addon.random.getstate()
        self._answer(addon, 3)
        completed = copy.deepcopy(addon._state.player_data)
        after_rng = addon.random.getstate()
        state = completed["summoning_state"]["familiarisation"]
        self.assertFalse(state["active"])
        self.assertTrue(state["awaiting_reward"])
        self.assertEqual((state["segments"], state["raw_shards"]), (4, 60))
        migrated = migrate_loaded_data(copy.deepcopy(completed), ORE_DATA)
        self.assertEqual(migrated["summoning_state"]["familiarisation"], state)
        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(addon.random.getstate(), before_rng)
        self._answer(addon, 3)
        self.assertEqual(addon._state.player_data, completed)
        self.assertEqual(addon.random.getstate(), after_rng)
        self._answer(addon, 1)
        self.assertEqual(addon._state.player_data["summoning_state"]["familiarisation"]["raw_shards"], 60)
