"""A card that a danger stop ends early says why at the end of its last line.

Plan 2.1 shows the stop reason in the card's existing feedback lines, in the
copy model's words (owner Q8). These cards run through the review dispatcher of
a freshly loaded add-on.
"""

import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.runtime.runtime_actions_context import stop_card
from tests.test_fight_caves import _combat_result, _entered
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package

PACKAGE = "ankiscape_danger_stop_feedback"
# Every reason Part G records except the Thieving stun, which has its own line.
DANGER_STOPS = {
    "died": "Ended early: you died",
    "fled": "Ended early: you fled",
    "low_lp_no_food": "Ended early: low LP, no food",
    "poison_started": "Ended early: new poison",
    "prayer_empty": "Ended early: prayer ran out",
    "familiar_ended": "Ended early: familiar ran out",
    "void_shifter": "Ended early: Void shifter",
    "out_of_ammo": "Ended early: out of ammo",
    "out_of_runes": "Ended early: out of runes",
    "bank_trip": "Ended early: bank trip",
    "slayer_task_complete": "Ended early: Slayer task done",
}


def _card(*lines, stop_reason="", xp=0):
    """A Combat handler that shows ``lines``, gains ``xp`` and ends the card for ``stop_reason``."""

    def handler(ctx):
        for line in lines:
            ctx.show_activity_gain(line)
        if xp:
            ctx.player_data["attack_exp"] += xp
            ctx.show_exp(xp)
        if stop_reason:
            stop_card(ctx, stop_reason)
        return True

    return handler


class DangerStopFeedbackTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package(PACKAGE)
        for name in ("level_up_check", "check_achievements", "save_player_data", "_refresh_skill_availability"):
            setattr(self.addon, name, lambda *_args: None)
        self.addon.show_error_message = lambda _title, message: self.fail(message)
        self.addon._advance_world_events_after_review = lambda: None
        self.addon._save_player_data_if_anki_ready = lambda: None
        self.addon._remember_review_award_snapshot = lambda _before: None
        self.addon._review_action_multiplier = lambda: 10

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def answer(self, player, skill, handler=None):
        """The review log's activity lines after one successful card."""
        self.addon._state.player_data = player
        self.addon._state.current_skill = skill
        self.addon._state.exp_awarded = False
        if handler is None:
            self.addon.on_good_answer()
        else:
            with patch.object(self.addon, "_registered_answer_handler", lambda _skill: handler):
                self.addon.on_good_answer()
        log = self.addon._state.player_data.get("review_event_log", ())
        return [row["text"] for row in log if row["kind"] == "activity"]

    def answer_combat_card(self, handler):
        return self.answer(default_player_data(ORE_DATA, ITEM_DEFINITIONS), "Combat", handler)

    def test_each_danger_stop_ends_the_cards_last_line_with_its_reason(self):
        for reason, text in DANGER_STOPS.items():
            with self.subTest(reason):
                lines = self.answer_combat_card(_card("First line", "Last line", stop_reason=reason))
                self.assertEqual(lines, [f"Last line · {text}"])

    def test_with_xp_every_line_is_logged_and_only_the_last_carries_the_reason(self):
        lines = self.answer_combat_card(_card("First line", "Last line", stop_reason="died", xp=50))
        self.assertEqual(lines, ["First line", "Last line · Ended early: you died"])

    def test_a_stun_a_planned_boundary_or_a_card_without_lines_gets_no_reason(self):
        for reason in ("stun", "kill", "wave_completed"):
            with self.subTest(reason):
                self.assertEqual(self.answer_combat_card(_card("Last line", stop_reason=reason)), ["Last line"])
        self.assertEqual(self.answer_combat_card(_card(stop_reason="died", xp=50)), [])

    def test_repeated_item_gains_keep_their_total_before_the_reason(self):
        lines = self.answer_combat_card(_card("+1 Flax", "+1 Flax", "+1 Flax", stop_reason="bank_trip"))
        self.assertEqual(lines, ["+3 Flax · Ended early: bank trip"])

    def test_a_fight_caves_death_at_speed_ten_says_why_the_card_ended(self):
        caves = sys.modules[f"{PACKAGE}.logic.fight_caves_logic"]
        with patch.object(caves, "apply_combat_burst_pure", side_effect=_combat_result(died=True)):
            lines = self.answer(_entered(), "Utility / Activities")
        # The switch to Bankstanding is logged first; the card's own last line says why it ended.
        self.assertTrue(lines[-1].startswith("Safe defeat on wave 1"), lines)
        self.assertTrue(lines[-1].endswith(" · Ended early: you died"), lines)
        self.assertEqual([line for line in lines if "Ended early" in line], lines[-1:])


if __name__ == "__main__":
    unittest.main()
