"""Pets and its actions remain together and reachable through Equipment scrolling."""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as _main_menu_fixtures
from tests.ui_flows.test_first_cell_selection import _dark_palette
from tests.ui_flows.test_tree_text_fit import _pump
from tests.ui_flows.test_pets_visible_rows import reveal_widget, visible_rect

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPoint, QPushButton, QScrollArea, QTreeWidget, QWidget


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class PetsFixedPanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu_fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu_fixtures.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _assert_pets_stay_with_the_toggle_when_gear_scrolls(self, dialog, width) -> None:
        dialog.resize(width, 560)
        _pump()
        pets = dialog.findChild(QTreeWidget, "summoningPetsLog")
        follower = dialog.findChild(QWidget, "summoningFollowerPanel")
        anchors = [dialog.findChild(QPushButton, name) for name in (
            "summoningPetsToggle", "summoningLetOutPetButton", "summoningReleasePetButton",
        )]
        anchors.append(pets)
        gear = dialog.findChild(QWidget, "equipmentCombatSetupPanel")
        scroll = gear.parentWidget()
        while scroll is not None and not isinstance(scroll, QScrollArea):
            scroll = scroll.parentWidget()
        self.assertIsNotNone(scroll)
        for widget in anchors:
            self.assertTrue(follower.isAncestorOf(widget), widget.objectName())
        self.assertEqual(pets.height(), 210)
        self.assertEqual(pets.verticalScrollMode(), QTreeWidget.ScrollMode.ScrollPerItem)
        bar = scroll.verticalScrollBar()
        self.assertGreater(bar.maximum(), 0)
        bar.setValue(0)
        _pump()
        before = [widget.mapTo(follower, QPoint()) for widget in anchors]
        points = dialog.findChild(QWidget, "equipmentPointsHeader")
        points_top = points.mapTo(dialog, QPoint())
        gear_top = gear.mapTo(dialog, QPoint())
        bar.setValue(bar.maximum())
        _pump()
        delta = gear.mapTo(dialog, QPoint()) - gear_top
        self.assertLess(delta.y(), 0)
        self.assertEqual(points.mapTo(dialog, QPoint()), points_top)
        self.assertEqual([widget.mapTo(follower, QPoint()) for widget in anchors], before)
        for widget in anchors:
            reveal_widget(widget)
            self.assertTrue(visible_rect(widget).contains(widget.rect()), widget.objectName())
            point = widget.mapToGlobal(widget.rect().center())
            hit = QApplication.widgetAt(point)
            self.assertTrue(hit is widget or widget.isAncestorOf(hit), widget.objectName())

    def test_expanded_pets_and_actions_stay_with_the_toggle_when_gear_scrolls(self) -> None:
        app = QApplication.instance()
        self.addCleanup(app.setPalette, app.palette())
        for theme, palette in (("light", app.style().standardPalette()), ("dark", _dark_palette())):
            app.setPalette(palette)
            dialog = self.menu._open(_main_menu._make_player_data(), current_skill="Mining")
            dialog.show()
            _main_menu._open_equipment_tab(dialog)
            toggle = dialog.findChild(QPushButton, "summoningPetsToggle")
            toggle.click()
            _pump()
            for width in (720, 980):
                with self.subTest(theme=theme, width=width):
                    self._assert_pets_stay_with_the_toggle_when_gear_scrolls(dialog, width)
            dialog.close()


if __name__ == "__main__":
    unittest.main()
