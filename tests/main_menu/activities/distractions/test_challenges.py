from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _open_challenges_tab
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QPushButton, QTreeWidget, QWidget
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_challenges_tab_renders_the_queue_and_routes_every_command(self) -> None:
        from ankiscape.data.daily_challenges_data import (
            DAILY_CHALLENGE_ACTIVE_LIMIT,
            DAILY_CHALLENGE_DATA,
        )
        from ankiscape.logic.daily_challenges_logic import (
            apply_daily_challenges_command_pure,
            default_daily_challenges_state_pure,
        )

        spec = DAILY_CHALLENGE_DATA["mining_copper_ore"]
        pd = _make_player_data()
        pd.update(default_daily_challenges_state_pure())
        pd["mining_level"] = 99
        pd["mining_exp"] = 0.0
        pd["inventory"] = {"Copper ore": int(spec["required"])}
        pd["daily_challenges"] = [
            {
                "instance_id": "mining_copper_ore-1",
                "challenge_id": "mining_copper_ore",
                "day": 1,
                "progress": int(spec["required"]),
                "credited": {"Copper ore": int(spec["required"])},
            }
        ]
        command_calls = []

        def challenges_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_daily_challenges_command_pure(
                pd, action_id, payload, {"Copper ore": 8}
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Mining",
            on_daily_challenges_command=challenges_command,
        )
        dialog.show()
        QApplication.processEvents()
        _open_challenges_tab(dialog)
        page = dialog.findChild(QWidget, "challengesTab")
        summary = page.findChild(QLabel, "challengeSummaryLabel")
        self.assertIn(f"1/{DAILY_CHALLENGE_ACTIVE_LIMIT} slots", summary.text())

        tree = page.findChild(QTreeWidget, "challengeTree")
        self.assertEqual(tree.topLevelItemCount(), 1)
        self.assertEqual(
            tree.topLevelItem(0).text(2), f"{int(spec['required'])}/{int(spec['required'])}"
        )

        page.findChild(QPushButton, "challengePinButton").click()
        QApplication.processEvents()
        self.assertEqual(
            command_calls[-1], ("pin", {"instance_id": "mining_copper_ore-1"})
        )
        self.assertIn("(pinned)", tree.topLevelItem(0).text(0))

        claim = page.findChild(QPushButton, "challengeClaimButton")
        self.assertTrue(claim.isEnabled())
        claim.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "claim")
        self.assertEqual(tree.topLevelItemCount(), 0)
        self.assertEqual(pd["mining_exp"], float(spec["reward_xp"]))

        bag = page.findChild(QPushButton, "challengeBagButton")
        self.assertTrue(bag.isEnabled())
        bag.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "open_bag")
        self.assertEqual(pd["inventory"]["Coins"], int(spec["required"]) * 8)
        self.assertFalse(bag.isEnabled())
        dialog.close()
