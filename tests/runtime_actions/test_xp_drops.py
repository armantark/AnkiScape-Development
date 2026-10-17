"""Review XP drops carry fractional totals without changing the awards."""

import copy
import sys
import types
import unittest

from tests.test_combat_logic import _player
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)


class ReviewXpDropsTest(unittest.TestCase):
    def setUp(self):
        self.original_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_xp_drops")
        self.popup = []
        self.addon.mw = _DummyMW(_DummyCol({"ankiscape_popups_enabled": False}))
        sys.modules["aqt"].mw = self.addon.mw
        sys.modules[f"{self.addon.__name__}.core.storage"].mw = self.addon.mw
        self.addon.mw.exp_popup = types.SimpleNamespace(
            show_exp=lambda amount: self.popup.append(amount.display_text),
            show_text=lambda text: self.popup.append(text),
        )
        self.addon.show_error_message = lambda title, text: self.fail(f"{title}: {text}")

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def _answer(self):
        state = self.addon._state
        state.card_turned = state.answer_shown = True
        state.exp_awarded = False
        self.assertEqual(
            self.addon.on_answer_card(_FakeReviewer(), 4, lambda *_args: "answered"),
            "answered",
        )

    def _xp_events(self):
        return [
            row["text"] for row in self.addon._state.player_data["review_event_log"]
            if row["kind"] == "xp"
        ]

    def test_four_bury_reviews_carry_halves_and_undo_replays_the_same_drop(self):
        addon = self.addon
        addon._state.current_skill = "Prayer"
        addon._state.player_data = {
            "inventory": {"Bones": 4},
            "prayer_level": 1,
            "prayer_exp": 0.0,
            "current_prayer": "bury_bones",
            "completed_achievements": [],
        }
        for _ in range(4):
            self._answer()
        expected = [f"+{amount} XP · Prayer" for amount in (4, 5, 4, 5)]
        self.assertEqual(self.popup, expected)
        self.assertEqual(self._xp_events(), expected)
        self.assertEqual(addon._state.player_data["prayer_exp"], 18.0)
        self.assertEqual(addon.mw.col.get_config("ankiscape_player_data")["prayer_exp"], 18.0)
        self.assertEqual(addon._state.player_data["inventory"]["Bones"], 0)
        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data["prayer_exp"], 13.5)
        self._answer()
        self.assertEqual(self.popup[-1], expected[-1])
        self.assertEqual(self._xp_events(), expected)
        self.assertEqual(addon._state.player_data["prayer_exp"], 18.0)

    def _finish_giant_rat(self, attack_exp, constitution_exp):
        addon = self.addon
        addon._state.current_skill = "Combat"
        addon._state.player_data = _player(
            inventory={}, current_combat_target="giant_rat",
            attack_exp=attack_exp, constitution_exp=constitution_exp,
            combat_encounter={
                "target_id": "giant_rat", "enemy_lifepoints": 2,
                "player_attack_ticks_remaining": 5, "enemy_attack_ticks_remaining": 100,
            },
        )
        # A guaranteed hit on the last tick leaves exactly two LP to reward.
        rolls = iter((0.0, 0.999999) * 100)
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls, 0.5)
        self.addCleanup(setattr, addon.random, "random", original_random)
        before = copy.deepcopy(addon._state.player_data)
        self._answer()
        self.assertAlmostEqual(addon._state.player_data["attack_exp"] - before["attack_exp"], 0.8)

    def test_combat_fraction_without_a_whole_number_crossing_has_no_xp_drop(self):
        self._finish_giant_rat(0.0, 0.0)
        self.assertEqual(self._xp_events(), [])
        self.assertFalse(any("XP" in text for text in self.popup), self.popup)

    def test_combat_crossings_keep_the_same_multi_skill_popup_and_log(self):
        self._finish_giant_rat(0.7, 0.9)
        expected = "Attack +1 XP · Constitution +1 XP"
        self.assertEqual(self._xp_events(), [expected])
        self.assertIn(expected, self.popup)

    def test_combat_omits_attack_when_only_constitution_crosses(self):
        self._finish_giant_rat(0.0, 0.9)
        expected = "+1 XP · Constitution"
        self.assertEqual(self._xp_events(), [expected])
        self.assertIn(expected, self.popup)

    def test_multiple_awards_update_one_drop_before_the_level_up(self):
        addon = self.addon
        addon._state.player_data = {
            "attack_exp": 82.0, "attack_level": 1,
            "constitution_exp": 0.0, "constitution_level": 10,
        }
        addon._state.current_skill = "Combat"
        addon._begin_review_feedback_context()
        for key, amount, name in (("attack_exp", 1.0, "Attack"), ("constitution_exp", 1.3, "Constitution")):
            addon._show_exp(addon._award_skill_exp(key, amount))
            addon.level_up_check(name, addon._state.player_data)
        addon._finish_review_feedback_context()
        self.assertEqual(self._xp_events(), self.popup)
        self.assertEqual(self.popup, ["Attack +1 XP · Constitution +1 XP"])
        self.assertEqual(addon._state.player_data["review_event_log"][0]["kind"], "xp")


class WholeNumberXpBreakdownTest(unittest.TestCase):
    def test_totals_carry_fractional_xp_and_omit_unchanged_skills(self):
        from ankiscape.core.xp_drops import whole_number_xp_breakdown

        before = {"prayer_exp": 4.5, "attack_exp": 0.0, "constitution_exp": 9.9}
        after = {"prayer_exp": 9.0, "attack_exp": 0.8, "constitution_exp": 10.1}
        original = copy.deepcopy((before, after))
        self.assertEqual(
            whole_number_xp_breakdown(before, after),
            [("Prayer", 5), ("Constitution", 1)],
        )
        self.assertEqual((before, after), original)
        self.assertEqual(whole_number_xp_breakdown(after, after), [])


if __name__ == "__main__":
    unittest.main()
