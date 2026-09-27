"""Offscreen Qt checks for the Dominion Tower panel.

Follows `.claude/rules/qt-offscreen-screenshots.md`: the panel is shown before
it is sized, and widget state is the evidence rather than a pixel grab. The
boundary under test is failure mode four — every enable, label and status string
here has to come from `dominion_tower_view_pure`, so a panel that re-derived a
tower rule and got it wrong would fail here rather than ship.
"""

from __future__ import annotations

import os
import random
import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

try:
    from aqt.qt import QApplication  # type: ignore

    _QT = True
except Exception:  # pragma: no cover - the non-Qt lane skips this module
    _QT = False

from ankiscape.logic.dominion_tower_logic import (
    apply_dominion_tower_command_pure,
    dominion_tower_view_pure,
)

if _QT:
    from ankiscape.ui.dominion_tower_panel import DominionTowerPanel

from tests.test_dominion_tower import _geared, _player, _twenty_quests  # noqa: E402


def _command(player, rng):
    """A real dispatcher over a real save: no fake agreeing with itself."""

    def run(action_id, payload):
        updated, ok, info = apply_dominion_tower_command_pure(
            player, action_id, payload, rng
        )
        if ok:
            player.clear()
            player.update(updated)
        return {"ok": ok, **info}

    return run


@unittest.skipUnless(_QT, "offscreen Qt lane only")
class DominionTowerPanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _panel(self, player, rng):
        panel = DominionTowerPanel(player, on_command=_command(player, rng))
        panel.show()
        panel.resize(420, 560)
        for _ in range(4):
            self.app.processEvents()
        return panel

    def test_a_locked_tower_shows_its_reasons_and_offers_only_the_face(self):
        player = _player()
        panel = self._panel(player, random.random)
        view = dominion_tower_view_pure(player)
        self.assertTrue(panel.requirements.isVisible())
        for reason in view["entry_reasons"]:
            self.assertIn(reason, panel.requirements.text())
        self.assertEqual(panel.primary_button.text(), "Talk to the Strange face")
        self.assertFalse(panel.leave_button.isVisible())
        self.assertFalse(panel.claim_box_button.isEnabled())

    def test_the_panel_follows_the_view_into_an_active_run(self):
        rng = random.Random(5).random
        player = _geared(_player(*_twenty_quests()))
        panel = self._panel(player, rng)
        panel._run_command("talk_to_face")
        panel._run_command("start_mode", {"mode": "climber"})
        view = dominion_tower_view_pure(player)
        self.assertEqual(panel.status_chip.text(), "CLIMBER")
        self.assertIn(view["encounter_name"], panel.arena_status.text())
        self.assertIn(view["engaged_name"], panel.enemy_health.format())
        self.assertEqual(panel.enemy_health.maximum(), view["engaged_max_lifepoints"])
        self.assertTrue(panel.leave_button.isVisible())
        self.assertFalse(panel.leave_button.isEnabled())
        self.assertFalse(panel.mode_combo.isEnabled())

    def test_the_spinner_buttons_track_the_view_not_a_panel_rule(self):
        rng = random.Random(5).random
        player = _geared(_player(*_twenty_quests()))
        panel = self._panel(player, rng)
        panel._run_command("talk_to_face")
        panel._run_command("start_mode", {"mode": "climber"})
        view = dominion_tower_view_pure(player)
        self.assertTrue(view["offer_row"])
        self.assertIn(view["offer_row"]["display_name"], panel.handicap_status.text())
        self.assertTrue(panel.accept_button.isEnabled())
        self.assertEqual(
            panel.respin_button.isEnabled(), bool(view["offer_row"]["can_respin"])
        )
        for _ in range(3):
            panel._run_command("nudge_handicap")
        self.assertFalse(
            dominion_tower_view_pure(player)["offer_row"]["can_nudge"]
        )
        self.assertFalse(panel.nudge_button.isEnabled())
        panel._run_command("accept_handicap")
        self.assertFalse(panel.accept_button.isEnabled())
        self.assertIn("suffered 1/22", panel.handicap_status.text())

    def test_an_unlocked_reward_without_a_credit_stays_disabled(self):
        rng = random.Random(5).random
        player = _geared(_player(*_twenty_quests()))
        state = dict(player["dominion_tower"])
        state.update(
            {
                "talked_with_face": True,
                "boss_kills": 450,
                "spectated": True,
                "reward_credits": 0,
                "credit_kill_marker": 450,
            }
        )
        player["dominion_tower"] = state
        panel = self._panel(player, rng)
        view = dominion_tower_view_pure(player)
        self.assertFalse(view["dreadnip_ready"])
        self.assertEqual(panel.reward_combo.count(), 1)
        self.assertEqual(panel.reward_combo.currentData(), "dreadnip")
        self.assertFalse(panel.claim_reward_button.isEnabled())
        _updated, ok, info = apply_dominion_tower_command_pure(
            player, "claim_reward", {"reward_id": "dreadnip"}, rng
        )
        self.assertFalse(ok)
        self.assertIn("No reward credits", info["reason"])

    def test_the_panel_fits_a_laptop_dialog_without_clipping(self):
        rng = random.Random(5).random
        player = _geared(_player(*_twenty_quests()))
        panel = self._panel(player, rng)
        panel._run_command("talk_to_face")
        panel._run_command("start_mode", {"mode": "endurance"})
        for _ in range(4):
            self.app.processEvents()
        self.assertLessEqual(panel.sizeHint().height(), 560)
        self.assertGreater(panel.width(), 0)


if __name__ == "__main__":
    unittest.main()
