"""Equipment keeps fixed points and reachable controls while Pets wraps Acquisition."""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu
from tests.ui_flows.test_first_cell_selection import _dark_palette, _rows
from tests.ui_flows.test_tree_text_fit import _pump
from tests.ui_flows.test_pets_visible_rows import reveal_widget, visible_rect

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPoint, QPushButton, QRect, QScrollArea, QTreeWidget, QWidget

    from tests.ui_flows.qt_text_fit import _cell_text_clipped, _view_item_option


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class EquipmentScrollBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        app = QApplication.instance()
        self.addCleanup(app.setPalette, app.palette())
        self.addCleanup(app.setFont, app.font())

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _open_equipment(self):
        dialog = self.menu._open(_main_menu._make_player_data(), current_skill="Mining")
        dialog.show()
        dialog.resize(980, 800)
        _pump()
        _main_menu._open_equipment_tab(dialog)
        return dialog

    def _assert_fixed_points_and_reachable_follower(self, dialog, scroll, points, follower, toggle):
        bar = scroll.verticalScrollBar()
        self.assertGreater(bar.maximum(), 0)
        bar.setValue(0)
        _pump()
        points_top = points.mapTo(dialog, QPoint())
        content_top = scroll.widget().mapTo(dialog, QPoint())
        bar.setValue(bar.maximum())
        _pump()
        self.assertLess(scroll.widget().mapTo(dialog, QPoint()).y(), content_top.y())
        self.assertEqual(points.mapTo(dialog, QPoint()), points_top)
        bounds = QRect(points_top, points.size())
        self.assertTrue(dialog.rect().contains(bounds), points.objectName())
        self.assertLessEqual(bounds.bottom(), scroll.mapTo(dialog, QPoint()).y())
        reveal_widget(follower)
        for widget in (follower, toggle):
            self.assertTrue(visible_rect(widget).contains(widget.rect()), widget.objectName())
        self.assertIs(QApplication.widgetAt(toggle.mapToGlobal(toggle.rect().center())), toggle)

    def test_scrolling_gear_keeps_points_fixed_and_follower_controls_reachable(self) -> None:
        app = QApplication.instance()
        for theme, palette in (("light", app.style().standardPalette()), ("dark", _dark_palette())):
            app.setPalette(palette)
            dialog = self._open_equipment()
            points = dialog.findChild(QWidget, "equipmentPointsHeader")
            follower = dialog.findChild(QWidget, "summoningFollowerPanel")
            combat = dialog.findChild(QWidget, "equipmentCombatSetupPanel")
            scroll = combat.parentWidget()
            while scroll is not None and not isinstance(scroll, QScrollArea):
                scroll = scroll.parentWidget()
            self.assertIsNotNone(scroll)
            toggle = dialog.findChild(QPushButton, "summoningPetsToggle")
            self.assertFalse(toggle.isChecked())
            for width in (720, 980):
                with self.subTest(theme=theme, width=width):
                    dialog.resize(width, 560)
                    _pump()
                    self.assertEqual(dialog.height(), 560)
                    self._assert_fixed_points_and_reachable_follower(dialog, scroll, points, follower, toggle)
            dialog.close()

    def test_wrapped_acquisition_rows_fit_the_painted_area_and_scroll_into_view_after_resize(self) -> None:
        app = QApplication.instance()
        original_font = app.font()
        for scale in (1.0, 1.5):
            font = app.font()
            font.setPointSizeF(original_font.pointSizeF() * scale)
            app.setFont(font)
            dialog = self._open_equipment()
            dialog.findChild(QPushButton, "summoningPetsToggle").click()
            _pump()
            pets = dialog.findChild(QTreeWidget, "summoningPetsLog")
            for width in (980, 720, 980):
                with self.subTest(scale=scale, width=width):
                    dialog.resize(width, 560)
                    _pump()
                    self.assertEqual(pets.height(), 210)
                    self.assertEqual(pets.verticalScrollMode(), QTreeWidget.ScrollMode.ScrollPerItem)
                    option = _view_item_option(pets)
                    for index in _rows(pets):
                        acquisition = index.siblingAtColumn(3)
                        pets.scrollTo(acquisition, QTreeWidget.ScrollHint.PositionAtTop)
                        _pump()
                        self.assertFalse(_cell_text_clipped(pets, option, acquisition), index.data())
                        self.assertTrue(pets.viewport().rect().contains(pets.visualRect(acquisition)), index.data())
                    if scale == 1.0:
                        self.assertEqual(pets.horizontalScrollBar().maximum(), 0)
                    else:
                        self.assertGreaterEqual(pets.columnWidth(3), 30 * pets.fontMetrics().averageCharWidth())
                        if width == 720:
                            self.assertGreater(pets.horizontalScrollBar().maximum(), 0)
            dialog.close()
