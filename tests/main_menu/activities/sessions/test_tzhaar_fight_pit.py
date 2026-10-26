from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_tzhaar_fight_pit_detail_routes_policy_entry_and_active_state(self) -> None:
        from ankiscape.logic.tzhaar_fight_pit_logic import (
            apply_tzhaar_fight_pit_command_pure,
            default_tzhaar_fight_pit_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_tzhaar_fight_pit_state_pure())
        pd.update(
            {
                "attack_level": 60,
                "strength_level": 60,
                "defense_level": 60,
                "constitution_level": 60,
                "current_combat_target": "chicken",
                "combat_encounter": {},
                "activity_session": {"active_id": ""},
            }
        )
        command_calls = []

        def fight_pit_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_tzhaar_fight_pit_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_tzhaar_fight_pit_command=fight_pit_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "tzhaar_fight_pit"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "fightPitPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "fightPitIcon").pixmap().isNull())
        policy = panel.findChild(QComboBox, "fightPitPolicy")
        policy.setCurrentIndex(policy.findData("aggressive"))
        panel.findChild(QPushButton, "fightPitSavePlan").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1], ("set_policy", {"policy": "aggressive"}))
        panel.findChild(QPushButton, "fightPitPrimary").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "tzhaar_fight_pit")
        self.assertEqual(pd["tzhaar_fight_pit"]["policy"], "aggressive")
        self.assertIn("3 rivals remain", panel.findChild(QLabel, "fightPitSummary").text())
        dialog.close()
