"""The Quests tab's list (owner, Pass 19): each quest name shows its progress in
the 2012 quest journal's colours, and the sort and filters outlast the menu."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tests.main_menu import fixtures
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _open_quests_tab

if HAS_AQT:
    from aqt.qt import QColor, QPalette

    from tests.test_main_menu_widget import QApplication, QCheckBox, QComboBox, QLabel, QPushButton, QWidget
    from tests.ui_flows.test_first_cell_selection import _dark_palette


def _luminance(colour: "QColor") -> float:
    channels = [value / 255 for value in (colour.red(), colour.green(), colour.blue())]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class QuestListViewTest(fixtures.MainMenuWidgetTest):
    def test_each_quest_name_shows_its_progress_colour_in_both_themes(self) -> None:
        pd = _make_player_data()
        pd["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        pd["quests"]["cooks_assistant"] = {"started": True, "progress": 1, "completed": False}
        pd["quests"]["the_restless_ghost"] = {"started": True, "progress": 1, "completed": False}
        pd["current_quest"] = "the_restless_ghost"
        # Hues in degrees: red not started, yellow started, green completed, cyan for the quest that runs.
        hues = {"imp_catcher": 0, "cooks_assistant": 60, "rune_mysteries": 120, "the_restless_ghost": 180}
        app = QApplication.instance()
        self.addCleanup(app.setPalette, app.palette())
        for theme, palette in (("light", app.style().standardPalette()), ("dark", _dark_palette())):
            app.setPalette(palette)
            dialog = self._open(pd, current_skill="Quests")
            _open_quests_tab(dialog)
            base = _luminance(palette.color(QPalette.ColorRole.Base))
            for quest_id, hue in hues.items():
                with self.subTest(theme=theme, quest=quest_id):
                    title = dialog.findChild(QLabel, f"questTitle_{quest_id}")
                    colour = QColor(title.styleSheet().partition("color: ")[2].rstrip(";"))
                    distance = abs(colour.hue() - hue)
                    # Nearer its own hue than the next one, which is 60 degrees away.
                    self.assertLess(min(distance, 360 - distance), 30)
                    lighter, darker = sorted((_luminance(colour), base), reverse=True)
                    # The names are bold, which reads at a contrast of 3:1 or more.
                    self.assertGreaterEqual((lighter + 0.05) / (darker + 0.05), 3)
            dialog.close()

    def test_a_quest_the_queue_starts_over_another_turns_cyan(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "cooks_assistant"

        def command(_name, payload):
            pd["current_quest"] = payload["action"]["quest_id"]
            return {"ok": True, "active": "Quests", "message": ""}

        dialog = self._open(pd, current_skill="Quests", on_action_queue_command=command)
        _open_quests_tab(dialog)
        dialog.findChild(QWidget, "questCard_the_restless_ghost").findChild(QPushButton, "queueAddButton").click()
        QApplication.processEvents()

        hues = {
            quest_id: QColor(dialog.findChild(QLabel, f"questTitle_{quest_id}").styleSheet().partition("color: ")[2].rstrip(";")).hue()
            for quest_id in ("cooks_assistant", "the_restless_ghost")
        }
        # Cyan sits at a hue of 180 degrees.
        self.assertLess(abs(hues["the_restless_ghost"] - 180), 30)
        self.assertGreaterEqual(abs(hues["cooks_assistant"] - 180), 30)
        dialog.close()

    def test_the_sort_and_filters_outlast_the_menu(self) -> None:
        from ankiscape.ui import ui_tab_quests

        config: dict = {}
        pd = _make_player_data()
        pd["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        with patch.object(ui_tab_quests, "mw", SimpleNamespace(col=SimpleNamespace(get_config=config.get, set_config=config.__setitem__))):
            dialog = self._open(pd)
            _open_quests_tab(dialog)
            dialog.findChild(QComboBox, "questSortCombo").setCurrentText("Difficulty")
            dialog.findChild(QComboBox, "questAccessFilterCombo").setCurrentText("Free quests")
            dialog.findChild(QCheckBox, "questHideCompletedCheck").setChecked(True)
            shown = dialog.findChild(QLabel, "questFilterSummaryLabel").text()
            dialog.close()

            dialog = self._open(pd)
            _open_quests_tab(dialog)
            self.assertEqual(dialog.findChild(QComboBox, "questSortCombo").currentText(), "Difficulty")
            self.assertEqual(dialog.findChild(QComboBox, "questAccessFilterCombo").currentText(), "Free quests")
            self.assertTrue(dialog.findChild(QCheckBox, "questHideCompletedCheck").isChecked())
            self.assertFalse(dialog.findChild(QCheckBox, "questHideLockedCheck").isChecked())
            self.assertEqual(dialog.findChild(QLabel, "questFilterSummaryLabel").text(), shown)
            self.assertIsNone(dialog.findChild(QWidget, "questCard_rune_mysteries"))
            dialog.close()


if __name__ == "__main__":
    unittest.main()
