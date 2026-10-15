"""Delivery punctuality follows successful other-target answers, inside Undo."""

import copy
import types
import unittest

from tests import test_farming_dispatch as farming
from tests.test_gnome_restaurant import _hired, _rng
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import migrate_loaded_data
from ankiscape.logic.gnome_restaurant_logic import apply_gnome_restaurant_command_pure
from ankiscape.data.gnome_restaurant_data import (
    GNOME_RESTAURANT_TIPS,
    GNOME_RESTAURANT_GOOD_TIP_GROUP,
)
from tests.test_integration_smoke import _FakeReviewer, _load_addon_as_package


class GnomeRestaurantReviewClockTests(unittest.TestCase):
    setUp = farming.TestFarmingReviewDispatch.setUp
    tearDown = farming.TestFarmingReviewDispatch.tearDown
    _configure = farming.TestFarmingReviewDispatch._configure

    def _addon(self, difficulty="hard"):
        addon = _load_addon_as_package("ankiscape_restaurant_review_clock")
        self._configure(addon)
        player = _hired()
        player["inventory"]["Toad crunchies"] = 1
        player, ok, info = apply_gnome_restaurant_command_pure(
            player, "accept_order", {"difficulty": difficulty}, _rng([0.0])
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["gnome_restaurant"]["order"]["item"], "Toad crunchies")
        addon._state.player_data = player
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
                if difficulty == "easy":
                    self.assertGreater(delivered["inventory"]["Coins"], 10)
                else:
                    good_tips = {row.id for row in GNOME_RESTAURANT_TIPS if row.group == GNOME_RESTAURANT_GOOD_TIP_GROUP}
                    self.assertTrue(set(restaurant["tips_received"]) & good_tips)
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
            before_answer = copy.deepcopy(addon._state.player_data)
            before_rng = addon.random.getstate()
            self._answer(addon, ease)
            after_answer = copy.deepcopy(addon._state.player_data)
            after_rng = addon.random.getstate()
            if ease > 1:
                self._undo(addon)
                self.assertEqual(addon._state.player_data, before_answer)
                self.assertEqual(addon.random.getstate(), before_rng)
                self._answer(addon, ease)
                self.assertEqual(addon._state.player_data, after_answer)
                self.assertEqual(addon.random.getstate(), after_rng)
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

    def test_missing_food_refuses_without_charging_delivery_window(self):
        addon = self._addon()
        addon._state.player_data["inventory"].pop("Toad crunchies")
        before = copy.deepcopy(addon._state.player_data["gnome_restaurant"])
        errors = []
        addon.show_error_message = lambda title, message: errors.append((title, message))
        self._answer(addon, 3)
        self.assertEqual(addon._state.player_data["gnome_restaurant"], before)
        self.assertEqual(errors, [(
            "Gnome Restaurant unavailable", "Cook or bank 1 Toad crunchies for this delivery."
        )])
