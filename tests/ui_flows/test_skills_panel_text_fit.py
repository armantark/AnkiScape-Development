"""Skills-tab panels keep their text whole at the 720 px minimum dialog width and wider."""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QLabel, QListWidget, QPushButton, QToolButton, QWidget

    from tests.ui_flows.qt_text_fit import clipped_text_defects

CATEGORIES = ("Combat", "Gathering", "Artisan", "Support", "Utilities", "Activities")


def _pump() -> None:
    for _ in range(30):
        QApplication.processEvents()


def _level_85_player() -> dict:
    from ankiscape.core.constants import EXP_TABLE

    player = _main_menu._make_player_data()
    for key in [key for key in player if key.endswith("_level")]:
        player[key] = 85
        player[key.replace("_level", "_exp")] = float(EXP_TABLE[84])
    return player


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class SkillsPanelTextFitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _open(self, width: int, skill: str = "Mining"):
        dialog = self.menu._open(_level_85_player(), current_skill=skill)
        dialog.show()
        dialog.resize(width, 560)
        _pump()
        return dialog

    @staticmethod
    def _select(dialog, category: str, skill: str) -> None:
        next(
            button for button in dialog.findChildren(QPushButton) if button.text() == category and button.isVisibleTo(dialog)
        ).click()
        _pump()
        selector = dialog.findChild(QListWidget, "skillListWidget")
        row = next(selector.item(i) for i in range(selector.count()) if selector.item(i).text() == skill)
        selector.setCurrentItem(row)
        selector.itemClicked.emit(row)
        _pump()

    def test_every_skill_panel_shows_its_text_whole(self) -> None:
        for width in (720, 1100):
            dialog = self._open(width)
            for category in CATEGORIES:
                selector = dialog.findChild(QListWidget, "skillListWidget")
                next(
                    button
                    for button in dialog.findChildren(QPushButton)
                    if button.text() == category and button.isVisibleTo(dialog)
                ).click()
                _pump()
                for index in range(selector.count()):
                    skill = selector.item(index).text()
                    with self.subTest(width=width, category=category, skill=skill):
                        self._select(dialog, category, skill)
                        self.assertEqual(clipped_text_defects(dialog), [])
            dialog.deleteLater()

    def test_agility_header_button_checkbox_and_search_show_in_full_at_720(self) -> None:
        dialog = self._open(720, skill="Agility")
        self._select(dialog, "Support", "Agility")
        texts = {label.text() for label in dialog.findChildren(QLabel) if label.isVisibleTo(dialog)}
        self.assertIn("Agility — Lv 85", texts)
        header = next(label for label in dialog.findChildren(QLabel) if label.text() == "Agility — Lv 85")
        train = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Currently training")
        self.assertGreaterEqual(header.width(), header.sizeHint().width())
        self.assertGreaterEqual(train.width(), train.sizeHint().width())
        pit_box = _main_menu._find_named_widget(dialog, "agilityPitAutoAcceptCheckBox")
        self.assertGreaterEqual(pit_box.height(), pit_box.heightForWidth(pit_box.width()))
        search = _main_menu._find_named_line_edit(dialog, "agilityTargetSearchInput")
        self.assertGreaterEqual(search.width(), search.fontMetrics().horizontalAdvance(search.placeholderText()))

    def test_farming_sheet_with_patches_open_shows_its_text_whole_at_720(self) -> None:
        dialog = self._open(720)
        self._select(dialog, "Gathering", "Farming")
        locations = [t for t in dialog.findChildren(QToolButton) if t.objectName().startswith("farmingLocationToggle")]
        for toggle in locations[:2]:
            toggle.click()
        _pump()
        for expand in [t for t in dialog.findChildren(QToolButton) if t.objectName().startswith("farmingPatchExpandButton")][:3]:
            expand.click()
        _pump()
        self.assertEqual(clipped_text_defects(dialog), [])


if __name__ == "__main__":
    unittest.main()
