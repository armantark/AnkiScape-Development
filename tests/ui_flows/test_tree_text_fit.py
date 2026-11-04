"""Tab trees keep every name whole at the dialog's real sizes.

The owner saw Collections family names cut short ("Boss/monste…") and the
Pets log's Acquisition text running off its edge. Both are checked at 720
and 980 logical pixels wide and 560 tall, the size Anki gives the dialog on
a laptop, by comparing each cell with the room its text needs. At a 1.5x
font each tree must give way without hiding text: the family list still
widens to its longest name, and the Pets log keeps a readable Acquisition
column and scrolls sideways.
"""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as _main_menu_fixtures
from tests.ui_flows.test_pets_visible_rows import assert_pet_rows_visible

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPushButton, QRect, QStyle, Qt, QTreeWidget, QWidget


def _pump() -> None:
    for _ in range(6):
        QApplication.processEvents()


def _rows(tree) -> list:
    rows, index = [], tree.indexFromItem(tree.topLevelItem(0))
    while index.isValid():
        rows.append(index)
        index = tree.indexBelow(index)
    return rows


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class TreeTextFitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu_fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu_fixtures.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _tab(self, player: dict, label: str, width: int):
        dialog = self.menu._open(player, current_skill="Mining")
        dialog.show()
        dialog.resize(width, 560)
        _pump()
        tabs = _main_menu._find_main_tabs(dialog)
        tabs.setCurrentIndex(next(i for i in range(tabs.count()) if tabs.tabText(i) == label))
        _pump()
        return dialog

    def _enlarge_font(self) -> None:
        """A 1.5x system font, the size at which the other columns crowd a tree."""
        app = QApplication.instance()
        self.addCleanup(app.setFont, app.font())
        font = app.font()
        font.setPointSizeF(font.pointSizeF() * 1.5)
        app.setFont(font)

    def test_every_collections_family_and_target_name_is_whole(self) -> None:
        for width in (720, 980):
            dialog = self._tab(_main_menu._make_player_data(), "Collections", width)
            navigation = dialog.findChild(QTreeWidget, "collectionsFamilyTree")
            cut = [
                index.siblingAtColumn(column).data()
                for index in _rows(navigation)
                for column in (0, 1)
                if navigation.sizeHintForIndex(index.siblingAtColumn(column)).width()
                > navigation.visualRect(index.siblingAtColumn(column)).width()
            ]
            with self.subTest(width=width):
                self.assertGreater(len(_rows(navigation)), 100)
                self.assertEqual(cut, [])
            dialog.close()

    def test_the_family_list_is_wider_than_its_longest_name_and_leaves_the_detail_pane_its_size(self) -> None:
        for width in (720, 980):
            dialog = self._tab(_main_menu._make_player_data(), "Collections", width)
            navigation = dialog.findChild(QTreeWidget, "collectionsFamilyTree")
            detail = dialog.findChild(QWidget, "collectionsDetailPanel")
            longest = max(navigation.fontMetrics().horizontalAdvance(index.data()) for index in _rows(navigation))
            with self.subTest(width=width):
                self.assertGreater(navigation.width(), longest)
                self.assertGreaterEqual(detail.width(), detail.sizeHint().width())
            dialog.close()

    def test_at_a_larger_font_the_family_list_still_shows_every_name_whole_at_720(self) -> None:
        self._enlarge_font()
        dialog = self._tab(_main_menu._make_player_data(), "Collections", 720)
        navigation = dialog.findChild(QTreeWidget, "collectionsFamilyTree")
        cut = [
            index.data()
            for index in _rows(navigation)
            if navigation.sizeHintForIndex(index).width() > navigation.visualRect(index).width()
        ]
        self.assertEqual(cut, [])
        dialog.close()

    def _pets_log(self, width: int):
        from ankiscape.logic.summoning_logic import default_summoning_state_pure

        player = _main_menu._make_player_data()
        player["summoning_state"] = default_summoning_state_pure()
        dialog = self._tab(player, "Equipment", width)
        dialog.findChild(QPushButton, "summoningPetsToggle").click()
        _pump()
        return dialog, dialog.findChild(QTreeWidget, "summoningPetsLog")

    @staticmethod
    def _cut_pet_cells(pets) -> list:
        # The style's own text margin, measured independently of the delegate under test.
        margin = 2 * (pets.style().pixelMetric(QStyle.PixelMetric.PM_FocusFrameHMargin, None, pets) + 1)
        metrics = pets.fontMetrics()
        cut = []
        for index in _rows(pets):
            for column in (0, 1, 2):
                cell = index.siblingAtColumn(column)
                if pets.sizeHintForIndex(cell).width() > pets.visualRect(cell).width():
                    cut.append(cell.data())
            acquisition = index.siblingAtColumn(3)
            room = pets.visualRect(acquisition)
            wrapped = metrics.boundingRect(
                QRect(0, 0, room.width() - margin, metrics.height() * len(acquisition.data())),
                Qt.TextFlag.TextWordWrap,
                acquisition.data(),
            )
            if wrapped.height() > room.height():
                cut.append(acquisition.data())
        return cut

    def test_the_pet_log_shows_every_acquisition_whole_without_scrolling_sideways(self) -> None:
        for width in (720, 980):
            dialog, pets = self._pets_log(width)
            with self.subTest(width=width):
                self.assertGreater(len(_rows(pets)), 40)
                self.assertLessEqual(pets.header().length(), pets.viewport().width())
                self.assertEqual(self._cut_pet_cells(pets), [])
                assert_pet_rows_visible(self, pets, _rows(pets))
            dialog.close()

    def test_at_a_larger_font_acquisition_keeps_its_floor_and_every_pet_row_scrolls_into_view(self) -> None:
        self._enlarge_font()
        dialog, pets = self._pets_log(720)
        floor = pets.itemDelegateForColumn(3).minimum_width()
        self.assertGreaterEqual(floor, 30 * pets.fontMetrics().averageCharWidth())
        self.assertGreaterEqual(pets.columnWidth(3), floor)
        # The floor is what holds here: without it the other columns would squeeze Acquisition.
        self.assertGreater(pets.header().length(), pets.viewport().width())
        self.assertEqual(self._cut_pet_cells(pets), [])
        assert_pet_rows_visible(self, pets, _rows(pets))
        dialog.close()


if __name__ == "__main__":
    unittest.main()
