from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_court_cases_detail_is_compact_and_advanced_discloses_one_choice(self) -> None:
        from ankiscape.logic.court_cases_logic import (
            apply_court_case_review_pure,
            apply_court_cases_command_pure,
        )

        pd = _make_player_data()
        pd["quests"]["kings_ransom"] = {"completed": True}
        pd["attack_level"] = 65
        pd["defense_level"] = 65
        pd["current_utility"] = "court_cases"
        command_calls = []

        def court_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_court_cases_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_court_cases_command=court_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "court_cases"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "courtCasesPanel")
            if widget.isVisible()
        )
        icon = panel.findChild(QLabel, "courtCasesIcon")
        primary = panel.findChild(QPushButton, "courtCasesPrimaryButton")
        choice = panel.findChild(QComboBox, "courtCasesTrialChoiceCombo")
        self.assertTrue(panel.isVisible())
        self.assertEqual(icon.size().width(), 28)
        self.assertFalse(icon.pixmap().isNull())
        self.assertEqual(primary.text(), "Take the case")
        self.assertFalse(choice.isVisible())
        primary.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["court_cases"]["case_id"], "mugger")
        self.assertEqual(pd["current_utility"], "court_cases")
        dialog.close()

        advanced = _make_player_data()
        advanced["quests"]["kings_ransom"] = {"completed": True}
        advanced["attack_level"] = 65
        advanced["defense_level"] = 65
        advanced, ok, _ = apply_court_cases_command_pure(
            advanced,
            "enter",
            {"role": "defence", "automation_mode": "advanced"},
        )
        self.assertTrue(ok)
        for _ in range(4):
            advanced, _ = apply_court_case_review_pure(advanced)

        def advanced_command(action_id, payload):
            nonlocal advanced
            updated, action_ok, info = apply_court_cases_command_pure(
                advanced, action_id, payload
            )
            if action_ok:
                advanced.clear()
                advanced.update(updated)
            return {
                "ok": action_ok,
                "message": info.get("reason", ""),
                **info,
            }

        advanced_dialog = self._open(
            advanced,
            current_skill="Activities",
            on_court_cases_command=advanced_command,
        )
        advanced_dialog.show()
        QApplication.processEvents()
        advanced_tree = self._open_activities(advanced_dialog)
        advanced_item = next(
            row
            for row in _tree_items(advanced_tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "court_cases"
        )
        advanced_tree.itemClicked.emit(advanced_item, 0)
        QApplication.processEvents()
        advanced_panel = next(
            widget
            for widget in advanced_dialog.findChildren(QWidget, "courtCasesPanel")
            if widget.isVisible()
        )
        advanced_choice = advanced_panel.findChild(
            QComboBox, "courtCasesTrialChoiceCombo"
        )
        self.assertTrue(advanced_choice.isVisible())
        self.assertEqual(advanced_choice.count(), 3)
        self.assertEqual(
            advanced_choice.accessibleName(), "Next courtroom action"
        )
