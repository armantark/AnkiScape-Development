"""A death or flee that ends a card early says so on the line that reports it.

Plan 2.2 shows the stop reason in the card's existing feedback line; owner Q8
gives the words to the copy model, so the lines end with its placeholders.
"""

import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.runtime import runtime_actions_activities_encounters as encounters
from tests.pace.test_combat_danger_stops import answer_combat
from tests.test_combat_logic import _player
from tests.test_fight_caves import _combat_result, _entered
from tests.test_runtime_actions import _context


def answer_fight_caves(**combat):
    calls = {"xp": [], "saves": 0, "errors": []}
    ctx = _context(_entered(), calls, review_action_multiplier=10)
    ctx.cadence_live_enabled = True
    with patch("ankiscape.logic.fight_caves_logic.apply_combat_burst_pure", side_effect=_combat_result(**combat)):
        encounters._handle_fight_caves_answer(ctx)
    return ctx.card.stop_reason, calls["activity"][-1]


class DangerStopFeedbackTests(unittest.TestCase):
    def test_a_combat_death_or_flee_line_ends_with_its_stop_text(self):
        died, died_calls, _ok = answer_combat(hits=((False, 0), (True, 100)))
        fled, fled_calls, _ok = answer_combat(_player(combat_auto_flee=True), hits=((True, 1), (True, 65)))
        self.assertEqual((died.card.stop_reason, fled.card.stop_reason), ("died", "fled"))
        self.assertTrue(died_calls["activity"][-1].startswith("☠ YOU DIED"))
        self.assertTrue(died_calls["activity"][-1].endswith("; gear moved to grave · <<COPY:danger_stop_died>>"))
        self.assertTrue(fled_calls["activity"][-1].endswith(" · <<COPY:danger_stop_fled>>"))

    def test_an_activity_death_carries_the_stop_text_and_a_kill_does_not(self):
        died_reason, died_line = answer_fight_caves(died=True)
        kill_reason, kill_line = answer_fight_caves(killed=True)
        self.assertEqual((died_reason, kill_reason), ("died", "kill"))
        self.assertTrue(died_line.endswith(" · <<COPY:danger_stop_died>>"))
        self.assertNotIn("<<COPY:", kill_line)


if __name__ == "__main__":
    unittest.main()
