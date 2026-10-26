"""Header resizing must preserve readable Acquisition text and the original Pets body."""

from __future__ import annotations

import unittest

from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as _main_menu_fixtures
from tests.ui_flows import test_tree_text_fit as _text_fit

if _main_menu.HAS_AQT:
    from aqt.qt import QPoint, QPushButton, QScrollArea, QTreeWidget, QWidget, Qt
    from PyQt6.QtTest import QTest


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class PetsAcquisitionResizeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _main_menu_fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.flow = _text_fit.TreeTextFitTest(methodName="runTest")
        self.flow.setUp()

    def tearDown(self):
        self.flow.tearDown()
        self.flow.doCleanups()

    def _assert_readable_rows(self, pets):
        self.assertGreaterEqual(pets.columnWidth(3), 30 * pets.fontMetrics().averageCharWidth())
        self.assertEqual(self.flow._cut_pet_cells(pets), [])
        self.assertEqual(pets.height(), 210)
        self.assertEqual(pets.verticalScrollMode(), QTreeWidget.ScrollMode.ScrollPerItem)
        for row in _text_fit._rows(pets):
            pets.scrollTo(row, QTreeWidget.ScrollHint.PositionAtTop)
            _text_fit._pump()
            rect = pets.visualRect(row)
            self.assertGreaterEqual(rect.top(), 0, row.data())
            self.assertLess(rect.bottom(), pets.viewport().height(), row.data())

    def test_dragging_acquisition_divider_cannot_make_wrapped_rows_unreadable(self):
        self.flow._enlarge_font()
        dialog, pets = self.flow._pets_log(980)
        header = pets.header()
        pets.horizontalScrollBar().setValue(pets.horizontalScrollBar().maximum())
        _text_fit._pump()
        edge = header.sectionViewportPosition(3) + header.sectionSize(3) - 1
        start = QPoint(edge, header.height() // 2)
        end = QPoint(edge - header.sectionSize(3) + 40, start.y())
        self.assertTrue(header.viewport().rect().contains(start))
        QTest.mousePress(header.viewport(), Qt.MouseButton.LeftButton, pos=start)
        QTest.mouseMove(header.viewport(), end, 20)
        QTest.mouseRelease(header.viewport(), Qt.MouseButton.LeftButton, pos=end)
        _text_fit._pump()
        self._assert_readable_rows(pets)
        dialog.close()

    def test_direct_section_resizing_and_page_resizing_keep_the_acquisition_floor(self):
        self.flow._enlarge_font()
        dialog, pets = self.flow._pets_log(980)
        for width in (980, 720, 980):
            with self.subTest(width=width):
                dialog.resize(width, 560)
                _text_fit._pump()
                pets.header().resizeSection(3, 40)
                _text_fit._pump()
                self._assert_readable_rows(pets)
                if width == 720:
                    self.assertGreater(pets.horizontalScrollBar().maximum(), 0)
                pets.header().resizeSection(3, 600)
                _text_fit._pump()
                self.assertGreater(pets.columnWidth(3), 30 * pets.fontMetrics().averageCharWidth())
                self._assert_readable_rows(pets)
        dialog.close()

    def test_pets_body_stays_directly_in_the_follower_panel_without_an_extra_scroll_area(self):
        dialog, pets = self.flow._pets_log(980)
        body = pets.parentWidget()
        follower = dialog.findChild(QWidget, "summoningFollowerPanel")
        self.assertIs(body.parentWidget(), follower)
        self.assertEqual(body.findChildren(QScrollArea), [])
        for name in ("summoningLetOutPetButton", "summoningReleasePetButton"):
            self.assertTrue(body.isAncestorOf(dialog.findChild(QPushButton, name)))
        toggle = dialog.findChild(QPushButton, "summoningPetsToggle")
        toggle.click()
        _text_fit._pump()
        self.assertFalse(body.isVisible())
        toggle.click()
        _text_fit._pump()
        self.assertTrue(body.isVisible())
        self.assertEqual(pets.height(), 210)
        dialog.close()


if __name__ == "__main__":
    unittest.main()
