from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QProgressBar, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_clan_wars_detail_offers_both_portals_and_warns_before_the_red_one(self) -> None:
        from ankiscape.data.clan_wars_data import (
            CLAN_WARS_MODES,
            CLAN_WARS_RED_MODE,
            CLAN_WARS_WHITE_MODE,
        )
        from ankiscape.logic.clan_wars_logic import (
            apply_clan_wars_command_pure,
            default_clan_wars_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_clan_wars_state_pure())
        pd.update(
            {
                "attack_level": 60,
                "strength_level": 60,
                "defense_level": 60,
                "constitution_level": 60,
                "prayer_level": 43,
                "current_combat_target": "chicken",
                "combat_encounter": {},
                "activity_session": {"active_id": ""},
            }
        )
        command_calls = []

        def clan_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_clan_wars_command_pure(
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
                on_clan_wars_command=clan_command,
            )
            dialog.show()
            QApplication.processEvents()
            tree = self._open_activities(dialog)
            item = next(
                row
                for row in _tree_items(tree)
                if row.data(0, Qt.ItemDataRole.UserRole) == "clan_wars"
            )
            tree.itemClicked.emit(item, 0)
            QApplication.processEvents()
            panel = next(
                widget
                for widget in dialog.findChildren(QWidget, "clanWarsPanel")
                if widget.isVisible()
            )
            return dialog, panel

        dialog, panel = open_panel()
        self.assertFalse(panel.findChild(QLabel, "clanWarsIcon").pixmap().isNull())
        combo = panel.findChild(QComboBox, "clanWarsModeCombo")
        self.assertEqual(combo.count(), len(CLAN_WARS_MODES))
        self.assertEqual(combo.currentData(), CLAN_WARS_WHITE_MODE)
        status = panel.findChild(QLabel, "clanWarsStatusChip")
        warning = panel.findChild(QLabel, "clanWarsWarning")
        self.assertEqual(status.text(), "SAFE")
        self.assertFalse(warning.isVisible())

        combo.setCurrentIndex(combo.findData(CLAN_WARS_RED_MODE))
        QApplication.processEvents()
        self.assertEqual(status.text(), "DANGEROUS")
        self.assertTrue(warning.isVisible())
        self.assertIn("destroyed", warning.text())

        # Declining the red-portal confirmation must not enter anything.
        original_question = self._ui.QMessageBox.question
        try:
            self._ui.QMessageBox.question = (
                lambda *a, **k: self._ui.QMessageBox.StandardButton.No
            )
            panel.findChild(QPushButton, "clanWarsPrimaryButton").click()
            QApplication.processEvents()
            self.assertEqual(command_calls, [])
            self.assertEqual(pd["clan_wars"], {})

            self._ui.QMessageBox.question = (
                lambda *a, **k: self._ui.QMessageBox.StandardButton.Yes
            )
            panel.findChild(QPushButton, "clanWarsPrimaryButton").click()
            QApplication.processEvents()
        finally:
            self._ui.QMessageBox.question = original_question
        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["clan_wars"]["mode"], CLAN_WARS_RED_MODE)
        dialog.close()

        active_dialog, active_panel = open_panel()
        self.assertEqual(
            active_panel.findChild(QLabel, "clanWarsStatusChip").text(),
            "ACTIVE · DANGEROUS",
        )
        # The dangerous portal forbids teleport escape, and the panel must show
        # that lock rather than deciding it for itself.
        teleport = active_panel.findChild(QPushButton, "clanWarsTeleportButton")
        self.assertTrue(teleport.isVisible())
        self.assertFalse(teleport.isEnabled())
        self.assertIn("forbidden", teleport.toolTip())
        self.assertTrue(
            active_panel.findChild(QPushButton, "clanWarsLeaveButton").isVisible()
        )
        active_combo = active_panel.findChild(QComboBox, "clanWarsModeCombo")
        self.assertEqual(active_combo.count(), 1)
        self.assertFalse(active_combo.isEnabled())
        progress = active_panel.findChild(QProgressBar, "clanWarsProgress")
        self.assertEqual(progress.value(), 0)
        self.assertIn("successful reviews", progress.format())
        active_dialog.close()
