"""Delivery punctuality follows successful other-target answers, inside Undo."""

import copy
import types
import unittest

from tests import test_farming_dispatch as farming
from tests.test_gnome_restaurant import ITEM_DEFINITIONS, ORE_DATA, _deliverable, _on_job, migrate_loaded_data
from tests.test_integration_smoke import _FakeReviewer, _load_addon_as_package


class GnomeRestaurantReviewClockTests(unittest.TestCase):
    setUp = farming.TestFarmingReviewDispatch.setUp
    tearDown = farming.TestFarmingReviewDispatch.tearDown
    _configure = farming.TestFarmingReviewDispatch._configure

    def _addon(self, difficulty="hard"):
        addon = _load_addon_as_package("ankiscape_restaurant_review_clock")
        self._configure(addon)
        addon.show_error_message = lambda *_args: None
        addon._state.player_data = _deliverable(_on_job(difficulty))
        addon._state.current_skill = "Utilities"
        addon.random.seed(17)
        return addon

    def _answer(self, addon, ease):
        addon._state.card_turned = addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), ease, lambda *_args: "answered")

    def _undo(self, addon):
        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))

    def test_again_then_prebanked_delivery_undo_and_reanswer(self):
        for difficulty in ("easy", "hard"):
            with self.subTest(difficulty=difficulty):
                addon = self._addon(difficulty)
                before = copy.deepcopy(addon._state.player_data)
                self._answer(addon, 1)
                paused = addon._state.player_data
                self.assertEqual(paused["gnome_restaurant"]["order"], before["gnome_restaurant"]["order"])
                self.assertEqual(paused["inventory"], before["inventory"])
                self.assertEqual(paused["gnome_restaurant"]["points"], 0)
                saved = copy.deepcopy(paused)
                before_rng = addon.random.getstate()
                self._answer(addon, 3)
                delivered = copy.deepcopy(addon._state.player_data)
                after_rng = addon.random.getstate()
                restaurant = delivered["gnome_restaurant"]
                self.assertEqual(restaurant["deliveries"][difficulty], 1)
                self.assertGreater(restaurant["points"], 0)
                self.assertEqual(restaurant["order"]["minutes_left"], 6 if difficulty == "easy" else 11)
                self._undo(addon)
                self.assertEqual(addon._state.player_data, saved)
                self.assertEqual(addon.random.getstate(), before_rng)
                self._answer(addon, 3)
                self.assertEqual(addon._state.player_data, delivered)
                self.assertEqual(addon.random.getstate(), after_rng)

    def test_other_target_success_spends_window_and_again_pauses(self):
        addon = self._addon()
        addon._state.current_skill = "Woodcutting"
        before = copy.deepcopy(addon._state.player_data)
        for ease, minutes in ((1, 11), (2, 5), (1, 5), (4, 0), (3, 0)):
            self._answer(addon, ease)
            order = addon._state.player_data["gnome_restaurant"]["order"]
            self.assertEqual(order["minutes_left"], minutes)
            self.assertEqual(order["customer"], before["gnome_restaurant"]["order"]["customer"])
            self.assertEqual(addon._state.player_data["gnome_restaurant"]["points"], 0)
        migrated = migrate_loaded_data(
            copy.deepcopy(addon._state.player_data), ORE_DATA, ITEM_DEFINITIONS
        )
        self.assertEqual(migrated["gnome_restaurant"]["order"], order)

    def test_farming_preemption_is_another_target_even_with_delivery_selected(self):
        addon = self._addon()
        addon._state.player_data["farm_queue"] = [{"kind": "plant", "patch_id": "invalid"}]
        self._answer(addon, 3)
        self.assertEqual(addon._state.player_data["gnome_restaurant"]["order"]["minutes_left"], 5)
        self.assertEqual(addon._state.player_data["gnome_restaurant"]["deliveries"]["hard"], 0)
