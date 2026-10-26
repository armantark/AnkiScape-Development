from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QColor, QComboBox, QLabel, QPalette, QPushButton, QStackedWidget, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_conquest_paginated_card_is_live_and_compact_at_short_height(self) -> None:
        from ankiscape.logic.conquest_logic import apply_conquest_command_pure

        pd = _make_player_data()
        pd.update(
            {
                "attack_level": 40,
                "strength_level": 40,
                "defense_level": 40,
                "constitution_level": 40,
                "ranged_level": 40,
                "magic_level": 40,
                "prayer_level": 40,
                "summoning_level": 1,
                "activity_session": {"active_id": ""},
                "combat_encounter": {},
                "pest_control_commendations": 150,
            }
        )
        command_calls = []

        def conquest_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_conquest_command_pure(
                pd, action_id, payload, lambda: 0.25
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_conquest_command=conquest_command,
        )
        original_palette = self.app.palette()
        dark = QPalette(original_palette)
        dark.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        dark.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        dark.setColor(QPalette.ColorRole.Text, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.WindowText, QColor(235, 235, 235))
        self.app.setPalette(dark)
        try:
            dialog.show()
            dialog.resize(900, 700)
            for _ in range(4):
                QApplication.processEvents()
            tree = self._open_activities(dialog)
            item = next(
                row
                for row in _tree_items(tree)
                if row.data(0, Qt.ItemDataRole.UserRole) == "conquest"
            )
            tree.itemClicked.emit(item, 0)
            for _ in range(4):
                QApplication.processEvents()
            panel = next(
                widget
                for widget in dialog.findChildren(QWidget, "conquestPanel")
                if widget.isVisible()
            )
            self.assertFalse(
                panel.findChild(QLabel, "conquestIcon").pixmap().isNull()
            )
            self.assertEqual(
                panel.findChild(QLabel, "conquestPageLabel").text(),
                "Overview · 1/3",
            )
            default_grab = dialog.grab()
            self.assertFalse(default_grab.isNull())

            mode = panel.findChild(QComboBox, "conquestMode")
            mode.setCurrentIndex(mode.findData("advanced"))
            panel.findChild(QPushButton, "conquestNextPage").click()
            QApplication.processEvents()
            self.assertEqual(
                panel.findChild(QLabel, "conquestPageLabel").text(),
                "Squad · 2/3",
            )
            panel.findChild(QPushButton, "conquestNextPage").click()
            QApplication.processEvents()
            self.assertEqual(
                panel.findChild(QLabel, "conquestPageLabel").text(),
                "Commands · 3/3",
            )
            self.assertEqual(
                len(
                    [
                        checkbox
                        for checkbox in panel.findChildren(QCheckBox)
                        if checkbox.objectName().startswith("conquestCommand_")
                    ]
                ),
                9,
            )

            dialog.resize(760, 560)
            for _ in range(5):
                QApplication.processEvents()
            pages = panel.findChild(QStackedWidget, "conquestPages")
            pager = panel.findChild(
                QPushButton, "conquestPreviousPage"
            ).parentWidget()
            self.assertLessEqual(pages.geometry().bottom(), pager.geometry().top())
            self.assertLessEqual(panel.width(), dialog.width())
            short_grab = dialog.grab()
            self.assertFalse(short_grab.isNull())

            panel.findChild(QPushButton, "conquestPrimaryButton").click()
            QApplication.processEvents()
            self.assertEqual(command_calls[-1][0], "enter")
            self.assertEqual(pd["activity_session"], {"active_id": "conquest"})
            self.assertEqual(pd["current_utility"], "conquest")
            self.assertTrue(
                panel.findChild(QPushButton, "conquestResignButton").isVisible()
            )
        finally:
            self.app.setPalette(original_palette)
            dialog.close()
