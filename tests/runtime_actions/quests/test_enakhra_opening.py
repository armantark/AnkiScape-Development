"""Ordinary answer/Undo seam: every opening review is one saved transaction."""

import copy
import json
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.enakhra_opening import QUEST_ID, MASS_KEY, BLOCK, BASE, PROOFS
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure
from ankiscape.logic_pure.quest.enakhra import enakhra_opening_next_action_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer, run_answer_with_carried_overlay
from tests.quest_catalog.test_enakhra_opening import _player, _reload, _route
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _FakeReviewer, _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context


def _persisted(player):
    """Anki config's JSON representation, including every field and nested value."""
    return json.loads(json.dumps(player))


def _journal(player):
    return quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)


class EnakhraRuntimeTest(unittest.TestCase):
    def setUp(self):
        self.original_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_enakhra_e2e")
        addon = self.addon
        self.saved, self.messages, self.errors = [], [], []
        addon.show_error_message = lambda *args: self.errors.append(args)
        addon.save_player_data = lambda: self.saved.append(_persisted(addon._state.player_data))
        addon.check_achievements = lambda _data: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = self.messages.append
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon._state.player_data = _player()
        addon._state.current_skill = "Quests"
        addon._state.review_undo_stack.clear()
        self.random_patch = patch("random.random", return_value=0.99)
        self.time_patch = patch("time.time", return_value=1792920000.0)
        self.random_patch.start()
        self.time_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        self.random_patch.stop()
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def _undo(self):
        self.addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))

    def _reset(self, inventory, multiplier=1, live=False):
        addon = self.addon
        addon._state.player_data = _player(inventory=inventory)
        addon._state.current_skill = "Quests"
        addon._state.review_undo_stack.clear()
        addon._review_action_multiplier = lambda: multiplier
        addon._cadence_kernel_enabled = lambda: live
        self.saved.clear()
        self.messages.clear()
        self.errors.clear()

    def _assert_one_review(self, expected_action, expected_progress=1):
        addon = self.addon
        before = copy.deepcopy(addon._state.player_data)
        descriptor = enakhra_opening_next_action_pure(before)
        self.assertEqual(descriptor["action_id"], expected_action)
        saves = len(self.saved)
        notices = len(self.messages)
        _answer_review(addon)
        after = copy.deepcopy(addon._state.player_data)
        self.assertEqual(len(self.saved), saves + 1)
        self.assertEqual(self.saved[-1], _persisted(after))
        self.assertEqual(self.messages[notices:], [descriptor["notice"]])
        self.assertEqual(after["quests"][QUEST_ID]["progress"], expected_progress)
        self.assertFalse(after["quests"][QUEST_ID]["completed"])
        self.assertEqual(after["quest_points"], before["quest_points"])
        return before, after

    def test_ordinary_dispatch_saves_once_and_notices_describe_each_real_action(self):
        for action in ("offer_help", "deliver_sandstone", "deliver_sandstone", "deliver_sandstone",
                       "receive_32kg", "chisel_base", "talk_after_base", "place_base"):
            self._assert_one_review(action, 2 if action == "place_base" else 1)
        player = self.addon._state.player_data
        self.assertEqual(player[MASS_KEY], 32)
        self.assertEqual(player["inventory"].get(BASE, 0), 0)
        self.assertEqual(player["inventory"].get(BLOCK, 0), 0)
        self.assertEqual(self.errors, [])

    def test_undo_and_replay_every_partial_delivery_split_and_custody_phase_exactly(self):
        self._reset({"Sandstone (10kg)": 4, "Chisel": 1, "Coal": 1})
        actions = ("offer_help", "deliver_sandstone", "deliver_sandstone", "deliver_sandstone",
                   "split_10kg", "split_5kg", "receive_32kg", "chisel_base", "talk_after_base", "place_base")
        for action in actions:
            self._assert_undo_replay(action)
        self.assertEqual(self.addon._state.player_data["inventory"]["Chisel"], 1)
        self.assertEqual(self.addon._state.player_data["inventory"]["Coal"], 1)

    def _assert_undo_replay(self, action):
        before, after = self._assert_one_review(action, 2 if action == "place_base" else 1)
        before_journal, after_journal = _journal(before), _journal(after)
        self._undo()
        self.assertEqual(self.addon._state.player_data, before)
        self.assertEqual(_journal(self.addon._state.player_data), before_journal)
        self.assertEqual(self.saved[-1], _persisted(before))
        saves = len(self.saved)
        _answer_review(self.addon)
        self.assertEqual(len(self.saved), saves + 1)
        self.assertEqual(self.addon._state.player_data, after)
        self.assertEqual(self.saved[-1], _persisted(after))
        self.assertEqual(_journal(self.addon._state.player_data), after_journal)

    def test_undo_and_replay_two_kg_split_before_the_final_one_kg_delivery(self):
        self._reset({"Sandstone (10kg)": 3, "Sandstone (1kg)": 1})
        for action in ("offer_help", "deliver_sandstone", "deliver_sandstone", "deliver_sandstone", "deliver_sandstone"):
            self._assert_undo_replay(action)
        # Bring another ordinary block after delivering 31kg; it must be split whole.
        self.addon._state.player_data["inventory"]["Sandstone (2kg)"] = 1
        for action in ("split_2kg", "receive_32kg", "chisel_base", "talk_after_base", "place_base"):
            self._assert_undo_replay(action)

    def test_actual_answers_cadence_and_multipliers_never_combine_opening_actions(self):
        for multiplier in (1, 2, 10):
            for live in (False, True):
                with self.subTest(multiplier=multiplier, live=live):
                    self._reset({"Sandstone (10kg)": 3, "Sandstone (2kg)": 1}, multiplier, live)
                    for action in ("offer_help", "deliver_sandstone", "deliver_sandstone", "deliver_sandstone",
                                   "receive_32kg", "chisel_base", "talk_after_base", "place_base"):
                        self._assert_one_review(action, 2 if action == "place_base" else 1)
                    self.assertEqual(len(self.saved), 8)

    def test_again_and_other_activity_never_emit_or_exchange_opening_actions(self):
        for player in _route(_player(inventory={"Sandstone (10kg)": 4}))[:-1]:
            addon = self.addon
            addon._state.player_data = copy.deepcopy(player)
            addon._state.current_skill = "Quests"
            before = copy.deepcopy(player)
            addon._state.card_turned = addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 1, lambda *_args: "answered")
            for key in ("inventory", MASS_KEY, "quest_action_proofs", "quests", "toolbelt"):
                self.assertEqual(addon._state.player_data[key], before[key])
            addon._state.current_skill = "Woodcutting"
            _answer_review(addon)
            for key in (MASS_KEY, "quest_action_proofs", "quests"):
                self.assertEqual(addon._state.player_data[key], before[key])
            self.assertEqual(addon._state.player_data["inventory"].get(BASE, 0), before["inventory"].get(BASE, 0))
            self.assertEqual(addon._state.player_data["inventory"].get(BLOCK, 0), before["inventory"].get(BLOCK, 0))

    def test_reload_between_all_phases_keeps_custody_and_replays_only_next_action(self):
        for action in ("offer_help", "deliver_sandstone", "deliver_sandstone", "deliver_sandstone",
                       "receive_32kg", "chisel_base", "talk_after_base", "place_base"):
            _, after = self._assert_one_review(action, 2 if action == "place_base" else 1)
            loaded = _reload(self.saved[-1])
            self.assertEqual(loaded, _reload(_persisted(after)))
            for key in (MASS_KEY, "quests", "quest_action_proofs", "toolbelt"):
                self.assertEqual(loaded[key], after[key])
            self.assertEqual(_journal(loaded), _journal(after))
            self.assertEqual(loaded["inventory"].get(BLOCK, 0), after["inventory"].get(BLOCK, 0))
            self.assertEqual(loaded["inventory"].get(BASE, 0), after["inventory"].get(BASE, 0))
            self.addon._state.player_data = loaded

    def test_refusals_keep_gameplay_state_and_save_no_transaction_deactivating_quest(self):
        scenarios = [_route(_player())[1]]
        # Help is always runnable; the subsequent supply has a material blocker.
        scenarios[0]["inventory"] = {}
        inconsistent = _player(inventory={BASE: 1})
        scenarios.append(inconsistent)
        for player in scenarios:
            before = copy.deepcopy(player)
            calls = {"xp": [], "saves": 0, "errors": []}
            self.assertFalse(handle_quest_answer(_context(player, calls)))
            self.assertEqual(player, before)
            self.assertEqual(calls["saves"], 0)
            self.assertTrue(calls["deactivated"])
            self.assertEqual(calls["errors"][0][0], "Quest blocked")

    def test_full_carried_overlay_and_equipment_do_not_block_abstract_quest_transactions(self):
        player = _player(inventory={"Sandstone (10kg)": 4, "Coal": 1, "Chisel": 1, "Lobster": 28})
        player["carried_inventory"] = {"sandstone": {"Lobster": 28}}
        player["equipment"] = {"weapon": "Bronze sword", "body": "Bronze platebody"}
        carried = copy.deepcopy(player["carried_inventory"])
        equipment = copy.deepcopy(player["equipment"])
        calls = {"xp": [], "saves": 0, "errors": []}
        for _ in range(10):
            ctx = _context(player, calls)
            self.assertTrue(run_answer_with_carried_overlay(ctx, "quest", handle_quest_answer))
            self.assertEqual(player["carried_inventory"], carried)
            self.assertEqual(player["equipment"], equipment)
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 2)
        self.assertEqual(calls["saves"], 10)
        self.assertEqual(player["inventory"]["Coal"], 1)
