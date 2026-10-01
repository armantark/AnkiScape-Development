"""Flat Skills target lists show each row's short name and keep the lock reason
and the extra catches in the tooltip and the Details panel (ruling 4.29.8)."""

from __future__ import annotations

import unittest

from tests import test_main_menu_widget as _main_menu
from tests.test_main_menu_widget import HAS_AQT, _find_named_line_edit, _make_player_data

if HAS_AQT:
    from aqt.qt import QApplication, QLabel, QListWidget, QRect, QStyle, QStyleOptionViewItem, Qt, QTextBrowser, QToolButton, QWidget


def _level_85_player() -> dict:
    from ankiscape.core.constants import EXP_TABLE

    data = _make_player_data()
    for key in [key for key in data if key.endswith("_level")]:
        data[key] = 85
        data[key.replace("_level", "_exp")] = float(EXP_TABLE[84])
    return data


def _rows(target_list) -> dict:
    return {
        target_list.item(i).data(Qt.ItemDataRole.UserRole): target_list.item(i)
        for i in range(target_list.count())
    }


def _row_fits(target_list, item) -> bool:
    """The row's text, wrapped at the width it is painted in, fits the row."""
    option = QStyleOptionViewItem()
    target_list.initViewItemOption(option)
    target_list.itemDelegate().initStyleOption(option, target_list.indexFromItem(item))
    option.rect = target_list.visualItemRect(item)
    text_rect = target_list.style().subElementRect(QStyle.SubElement.SE_ItemViewItemText, option, target_list)
    needed = option.fontMetrics.boundingRect(
        QRect(0, 0, text_rect.width(), 10_000), int(Qt.TextFlag.TextWordWrap.value), item.text()
    )
    return needed.width() <= text_rect.width() and needed.height() <= text_rect.height()


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class FlatTargetRowsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _open(self, skill: str, size: tuple[int, int]):
        dialog = self.menu._open(_level_85_player(), current_skill=skill.title())
        dialog.show()
        dialog.resize(*size)
        for _ in range(6):
            QApplication.processEvents()
        return dialog, dialog.findChild(QListWidget, f"{skill}TargetTree")

    def _assert_every_row_fits(self, target_list) -> None:
        self.assertEqual(target_list.horizontalScrollBar().maximum(), 0)
        for item in _rows(target_list).values():
            self.assertTrue(_row_fits(target_list, item), item.text())

    def test_a_quest_locked_course_shows_its_name_and_keeps_the_reason_in_tooltip_and_details(self) -> None:
        for size in ((720, 560), (900, 560)):
            with self.subTest(size=size):
                dialog, courses = self._open("agility", size)
                dorgesh = _rows(courses)["dorgesh_kaan"]
                self.assertFalse(dorgesh.flags() & Qt.ItemFlag.ItemIsEnabled)
                self.assertEqual(dorgesh.text(), "Dorgesh-Kaan Agility Course (Lvl 80)")
                self.assertIn("Locked due to: Death To The Dorgeshuun", dorgesh.toolTip())
                self._assert_every_row_fits(courses)

                # Clicking a locked row fills Details with its blockers.
                courses.itemClicked.emit(dorgesh)
                dialog.findChild(QToolButton, "targetDetailsToggle").setChecked(True)
                QApplication.processEvents()
                panel = dialog.findChild(QWidget, "targetDetailsPanel")
                texts = [label.text() for label in panel.findChildren(QLabel)]
                texts += [browser.toPlainText() for browser in panel.findChildren(QTextBrowser)]
                self.assertTrue(any("Death To The Dorgeshuun" in text for text in texts), texts)
                dialog.deleteLater()

    def test_fishing_spots_fold_extra_catches_and_stay_short_after_a_click_or_a_search(self) -> None:
        dialog, spots = self._open("fishing", (720, 560))
        rows = _rows(spots)
        leaping = rows["catch_leaping_fish"]
        self.assertFalse(leaping.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertEqual(leaping.text(), "Catch leaping trout (Lvl 48) +2 more")
        self.assertIn("Leaping salmon", leaping.toolTip())
        self.assertIn("Leaping sturgeon", leaping.toolTip())
        self.assertIn("Locked due to: materials, side levels, Barbarian Fishing", leaping.toolTip())
        # Two spots share their catches and differ only by place.
        self.assertEqual(rows["catch_cave_eel"].text(), "Catch slimy eel (Lvl 28) +1 more (Lumbridge Swamp Caves)")
        self.assertEqual(rows["catch_slimy_eel"].text(), "Catch slimy eel (Lvl 28) +1 more (Mort Myre)")
        self._assert_every_row_fits(spots)

        tuna = rows["catch_tuna_swordfish"]
        self.assertTrue(tuna.flags() & Qt.ItemFlag.ItemIsEnabled)
        spots.itemClicked.emit(tuna)
        QApplication.processEvents()
        self.assertEqual(tuna.text(), "✓ Catch tuna (Lvl 35) +1 more")
        self.assertEqual(leaping.text(), "Catch leaping trout (Lvl 48) +2 more")

        # A catch named only in the full label is still found by search.
        _find_named_line_edit(dialog, "fishingTargetSearchInput").setText("sturgeon")
        QApplication.processEvents()
        found = dialog.findChild(QListWidget, "fishingTargetTree")
        self.assertEqual([item.text() for item in _rows(found).values()], ["Catch leaping trout (Lvl 48) +2 more"])
        dialog.deleteLater()


if __name__ == "__main__":
    unittest.main()
