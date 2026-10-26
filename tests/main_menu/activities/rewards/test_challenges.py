from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _open_challenges_tab
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QPushButton, QWidget
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_a_finished_hand_in_without_its_items_shows_the_reason_and_stays_disabled(self) -> None:
        from ankiscape.data.daily_challenges_data import DAILY_CHALLENGE_DATA
        from ankiscape.logic.daily_challenges_logic import (
            default_daily_challenges_state_pure,
        )

        spec = DAILY_CHALLENGE_DATA["cooking_chicken"]
        pd = _make_player_data()
        pd.update(default_daily_challenges_state_pure())
        pd["inventory"] = {}
        pd["daily_challenges"] = [
            {
                "instance_id": "cooking_chicken-1",
                "challenge_id": "cooking_chicken",
                "day": 1,
                "progress": int(spec["required"]),
                "credited": {"Cooked chicken": int(spec["required"])},
            }
        ]

        dialog = self._open(
            pd,
            current_skill="Mining",
            on_daily_challenges_command=lambda *_args: {"ok": True},
        )
        dialog.show()
        QApplication.processEvents()
        _open_challenges_tab(dialog)
        page = dialog.findChild(QWidget, "challengesTab")
        claim = page.findChild(QPushButton, "challengeClaimButton")
        self.assertFalse(claim.isEnabled())
        self.assertIn("3 Cooked chicken", claim.toolTip())
        dialog.close()
