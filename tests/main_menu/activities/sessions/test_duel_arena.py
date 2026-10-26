from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QLabel, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_duel_arena_detail_configures_rules_and_shows_active_and_result_state(self) -> None:
        from ankiscape.logic.duel_arena_logic import (
            apply_duel_arena_command_pure,
            apply_duel_arena_review_pure,
            default_duel_arena_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_duel_arena_state_pure())
        pd.update(
            {
                "attack_level": 60,
                "strength_level": 60,
                "defense_level": 60,
                "constitution_level": 60,
                "ranged_level": 40,
                "magic_level": 40,
                "prayer_level": 43,
                "summoning_level": 1,
                "current_combat_target": "chicken",
                "combat_encounter": {},
                "activity_session": {"active_id": ""},
            }
        )
        command_calls = []

        def duel_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_duel_arena_command_pure(
                pd,
                action_id,
                payload,
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def open_panel():
            dialog = self._open(
                pd,
                current_skill="Activities",
                on_duel_arena_command=duel_command,
            )
            dialog.show()
            QApplication.processEvents()
            tree = self._open_activities(dialog)
            item = next(
                row
                for row in _tree_items(tree)
                if row.data(0, Qt.ItemDataRole.UserRole) == "duel_arena"
            )
            tree.itemClicked.emit(item, 0)
            QApplication.processEvents()
            panel = next(
                widget
                for widget in dialog.findChildren(QWidget, "duelArenaPanel")
                if widget.isVisible()
            )
            return dialog, panel

        dialog, panel = open_panel()
        self.assertFalse(panel.findChild(QLabel, "duelArenaIcon").pixmap().isNull())
        cap_claim = panel.findChild(QPushButton, "duelArenaClaimCap")
        self.assertTrue(cap_claim.isVisible())
        cap_claim.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "claim_cap")
        self.assertEqual(pd["inventory"]["Duellist's cap (tier 1)"], 1)
        self.assertFalse(cap_claim.isVisible())
        checks = panel.findChildren(QCheckBox)
        self.assertEqual(
            len([check for check in checks if check.objectName().startswith("duelArenaRule_")]),
            11,
        )
        panel.findChild(QCheckBox, "duelArenaRule_no_food").setChecked(True)
        panel.findChild(QCheckBox, "duelArenaRule_no_prayer").setChecked(True)
        panel.findChild(QCheckBox, "duelArenaRule_no_forfeit").setChecked(True)
        panel.findChild(QPushButton, "duelArenaSaveRules").click()
        QApplication.processEvents()
        self.assertEqual(
            command_calls[-1],
            (
                "set_rules",
                {"rule_ids": ["no_forfeit", "no_food", "no_prayer"]},
            ),
        )
        panel.findChild(QPushButton, "duelArenaPrimary").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "duel_arena")
        self.assertIn(
            "score 0-0",
            panel.findChild(QLabel, "duelArenaSummary").text(),
        )
        self.assertEqual(
            panel.findChild(QLabel, "duelArenaStatusChip").text(),
            "DUEL ACTIVE",
        )
        self.assertFalse(
            panel.findChild(QPushButton, "duelArenaAbandon").isVisible()
        )
        dialog.close()

        for _ in range(3):
            updated, ok, result = apply_duel_arena_review_pure(pd, lambda: 0.0)
            self.assertTrue(ok)
            pd.clear()
            pd.update(updated)
        self.assertEqual(result["outcome"], "win")

        result_dialog, result_panel = open_panel()
        self.assertIn(
            "Duel won",
            result_panel.findChild(QLabel, "duelArenaSummary").text(),
        )
        self.assertIn(
            "1 wins",
            result_panel.findChild(QLabel, "duelArenaCapProgress").text(),
        )
        result_dialog.close()
