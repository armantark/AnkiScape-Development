"""Resizing a collapsed Collections family must leave its descendants readable."""

from __future__ import annotations

import unittest

from tests import test_main_menu_widget as _main_menu
from tests.ui_flows import test_tree_text_fit as _text_fit

if _main_menu.HAS_AQT:
    from aqt.qt import QTreeWidget


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class CollectionsCollapsedTextFitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.flow = _text_fit.TreeTextFitTest(methodName="runTest")
        self.flow.setUp()

    def tearDown(self) -> None:
        self.flow.tearDown()

    def test_targets_stay_whole_after_resizing_with_the_drop_family_collapsed(self) -> None:
        from ankiscape.ui.ui_tab_collections import NAVIGATION_MAX_SHARE

        dialog = self.flow._tab(_main_menu._make_player_data(), "Collections", 980)
        navigation = dialog.findChild(QTreeWidget, "collectionsFamilyTree")
        for width in (720, 980, 720):
            with self.subTest(width=width):
                family = navigation.topLevelItem(1)
                family.setExpanded(False)
                dialog.resize(width, 560)
                _text_fit._pump()
                family.setExpanded(True)
                _text_fit._pump()
                rows = _text_fit._rows(navigation)
                self.assertGreater(len(rows), 100)
                self.assertIn("Flesh crawler (level 28)", [index.data() for index in rows])
                clipped = [
                    cell.data()
                    for index in rows
                    for column in (0, 1)
                    for cell in (index.siblingAtColumn(column),)
                    if navigation.sizeHintForIndex(cell).width() > navigation.visualRect(cell).width()
                ]
                self.assertEqual(clipped, [])
                self.assertLessEqual(navigation.width(), NAVIGATION_MAX_SHARE * navigation.parentWidget().width())
        dialog.close()


if __name__ == "__main__":
    unittest.main()
