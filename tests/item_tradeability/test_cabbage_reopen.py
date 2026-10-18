"""Utility consumption must save the same carried views that reopen restores."""

import copy
import json
import random
import sys
import types
import unittest
from unittest.mock import patch

from tests import test_integration_smoke as runtime_fixture


def _typed(value):
    if isinstance(value, dict):
        return type(value), {(type(key), key): _typed(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value), tuple(_typed(item) for item in value)
    return type(value), value


class CabbageReopenTest(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(sys.modules))
        self.addCleanup(random.setstate, random.getstate())
        random.seed(1965)
        runtime_fixture._install_runtime_fakes()
        self.collection = runtime_fixture._DummyCol()
        self.collection.set_config = lambda key, value: self.collection._store.__setitem__(
            key, json.loads(json.dumps(value))
        )
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(self.collection)
        self.addon = runtime_fixture._load_addon_as_package("ankiscape_cabbage_reopen")
        addon = self.addon
        addon.ui.update_menu_visibility = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _exp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        player, _skill = addon.storage_load_player_data()
        player.update(
            inventory={"Cabbage": 29, "Pie shell": 3, "Tomato": 3, "Onion": 3,
                       "Coins": 17, "Logs": 2},
            carried_inventory={"tree": {"Cabbage": 28}, "oak": {"Logs": 2}},
            carried_layout={"tree": {"Cabbage": 28}, "oak": {"Logs": 2}},
            carried_advanced_targets={"tree": True, "oak": True},
            skilling_bank_run_requested="",
            current_utility="make_soft_clay",
            shop_market_clock={"answered_cards": 19, "market_tick": 19},
        )
        addon._state.player_data, addon._state.current_skill = player, "Woodcutting"
        addon.check_achievements(player)
        addon.save_player_data()
        addon.load_player_data()
        addon.save_player_data()

    def packet(self):
        return copy.deepcopy({
            "player": self.addon._state.player_data,
            "skill": self.addon._state.current_skill,
            "config": self.collection._store,
            "rng": random.getstate(),
        })

    def assert_packet_equal(self, expected):
        for field, actual in self.packet().items():
            with self.subTest(field=field):
                self.assertEqual(_typed(actual), _typed(expected[field]))

    def answer_good(self):
        addon = self.addon
        addon.on_card_did_show(None)
        addon.on_show_answer(None)
        addon.on_answer_card(runtime_fixture._FakeReviewer(), 3,
                             lambda _self, _ease: "answered")

    def test_consumption_reconciles_inactive_packs_before_save_and_restores_on_undo(self):
        addon = self.addon
        before = self.packet()
        self.assertTrue(addon._set_value("current_utility", "assemble_garden_pie"))
        target_selected = self.packet()
        self.assertTrue(addon.start_activity_for_reviews("assemble_garden_pie"))
        selected = self.packet()
        self.answer_good()

        for player in (addon._state.player_data,
                       self.collection.get_config("ankiscape_player_data")):
            self.assertEqual(player["inventory"]["Cabbage"], 26)
            self.assertEqual(player["inventory"]["Raw garden pie"], 3)
            self.assertEqual(player["carried_inventory"]["tree"], {"Cabbage": 26})
            self.assertEqual(player["carried_layout"], before["player"]["carried_layout"])
            self.assertEqual(player["carried_inventory"]["oak"], {"Logs": 2})
        consumed = self.packet()
        self.assertEqual(consumed["skill"], "Utilities")
        self.assertEqual(consumed["config"]["ankiscape_current_skill"], "Utilities")
        self.assertNotEqual(consumed["rng"], selected["rng"])
        loaded, skill = addon.storage_load_player_data()
        self.assertEqual(_typed(loaded), _typed(consumed["player"]))
        self.assertEqual(skill, "Utilities")
        self.assert_packet_equal(consumed)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assert_packet_equal(selected)
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assert_packet_equal(target_selected)
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assert_packet_equal(before)

        self.assertTrue(addon._set_value("current_utility", "assemble_garden_pie"))
        self.assertTrue(addon.start_activity_for_reviews("assemble_garden_pie"))
        self.assert_packet_equal(selected)
        self.answer_good()
        self.assert_packet_equal(consumed)
        addon.load_player_data()
        self.assert_packet_equal(consumed)
