"""Familiarisation survives Again and completes on the fourth successful review."""

import copy
import types
import unittest

from tests import test_farming_dispatch as farming
from tests.test_integration_smoke import _FakeReviewer, _load_addon_as_package
from ankiscape.logic.summoning_logic import (
    CARGO_RECLAIM_REVIEWS, familiar_storage_transfer_pure, summon_familiar_pure,
)
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
        data = default_player_data(ORE_DATA)
        data["summoning_level"] = 99
        data["summoning_state"]["summoning_points_current"] = 99
        data["inventory"].update({"Pack yak pouch": 1, "Raw shark": 2})
        data, ok, _ = summon_familiar_pure(data, "packyak")
        self.assertTrue(ok)
        data, ok = familiar_storage_transfer_pure(data, "Raw shark", 2, to_familiar=True)
        self.assertTrue(ok)
        summoning = data["summoning_state"]
        summoning["active_follower"]["remaining_reviews"] = 2
        summoning["special_move_points_current"] = 0
        summoning["special_move_recharge_residual"] = 44
        summoning["triple_charm_reviews_remaining"] = 3
        summoning["cargo_events"] = [{
            "event_id": 1, "familiar_id": "packyak", "items": {"Coal": 1},
            "remaining_reviews": 1, "source": "dismissal",
        }]
        summoning["cargo_next_event_id"] = 2
        data, ok = start_familiarisation_pure(data)
        self.assertTrue(ok)
        addon._state.player_data = data
        addon._state.current_skill = "Woodcutting"
        initial_cooldown = data["summoning_state"]["familiarisation"]["cooldown_reviews_remaining"]
        successes = 0
        for index, ease in enumerate((1, 2, 1, 3, 1, 4, 1), start=1):
            before_answer = copy.deepcopy(addon._state.player_data)
            rng_before_answer = addon.random.getstate()
            self._answer(addon, ease)
            after_answer = copy.deepcopy(addon._state.player_data)
            rng_after_answer = addon.random.getstate()
            if index <= 2:
                addon._on_state_did_undo(types.SimpleNamespace(
                    operation="Answer Card",
                    changes=types.SimpleNamespace(study_queues=True, card=True),
                ))
                self.assertEqual(addon._state.player_data, before_answer)
                self.assertEqual(addon.random.getstate(), rng_before_answer)
                self._answer(addon, ease)
                self.assertEqual(addon._state.player_data, after_answer)
                self.assertEqual(addon.random.getstate(), rng_after_answer)
            clocks = addon._state.player_data["summoning_state"]
            self.assertEqual(clocks["special_move_points_current"], 15)
            self.assertEqual(clocks["special_move_recharge_residual"], (44 + index * 6) % 50)
            self.assertEqual(clocks["triple_charm_reviews_remaining"], max(0, 3 - index))
            if index == 1:
                self.assertEqual(clocks["active_follower"]["remaining_reviews"], 1)
                self.assertEqual(clocks["active_follower"]["storage"], {"Raw shark": 2})
                self.assertEqual(clocks["cargo_events"], [])
            else:
                self.assertEqual(clocks["active_follower"], {})
                deadline = CARGO_RECLAIM_REVIEWS - (index - 2)
                expected_cargo = [{
                    "event_id": 2, "familiar_id": "packyak", "items": {"Raw shark": 2},
                    "remaining_reviews": deadline, "source": "expiry",
                }] if deadline > 0 else []
                self.assertEqual(clocks["cargo_events"], expected_cargo)
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
