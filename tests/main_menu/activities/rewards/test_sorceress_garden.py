from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_widget,
    _make_player_data,
    _utility_row,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QScrollArea
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_sorceress_garden_card_introduction_gates_and_compact_policies(self) -> None:
        from ankiscape.logic.sorceress_garden_logic import default_sorceress_garden_state_pure

        pd = _make_player_data()
        pd["thieving_level"] = 65
        pd["quests"]["diamond_in_the_rough"]["completed"] = True
        pd["sorceress_garden"] = default_sorceress_garden_state_pure()
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "sorceress_garden")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        details = _find_named_widget(dialog, "utilityActivityDetailsStack")
        panel = _find_named_widget(dialog, "sorceressGardenPanel")
        primary = _find_named_button(dialog, "sorceressGardenPrimaryButton")
        self.assertEqual(details.currentWidget(), panel)
        self.assertEqual(primary.text(), "Talk to Osman")
        self.assertIsNone(panel.findChild(QScrollArea))

        primary.click()
        QApplication.processEvents()
        self.assertTrue(pd["sorceress_garden"]["introduced"])
        season = panel.findChild(QComboBox, "sorceressGardenSeason")
        harvest = panel.findChild(QComboBox, "sorceressGardenHarvest")
        juice = panel.findChild(QComboBox, "sorceressGardenJuice")
        season.setCurrentIndex(season.findData("summer"))
        harvest.setCurrentIndex(harvest.findData("alternate"))
        juice.setCurrentIndex(juice.findData("keep"))
        QApplication.processEvents()
        self.assertEqual(pd["sorceress_garden"]["season_id"], "summer")
        self.assertEqual(pd["sorceress_garden"]["harvest_mode"], "alternate")
        self.assertEqual(pd["sorceress_garden"]["juice_mode"], "keep")

        harvest.setCurrentIndex(harvest.findData("herbs"))
        QApplication.processEvents()
        self.assertFalse(juice.isHidden())
        self.assertFalse(juice.isEnabled())
        harvest.setCurrentIndex(harvest.findData("alternate"))
        QApplication.processEvents()
        self.assertTrue(juice.isEnabled())

        primary.click()
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "sorceress_garden")
        self.assertEqual(self._activity_start_calls[-1], "sorceress_garden")
        self.assertEqual(primary.text(), "Active for reviews")
