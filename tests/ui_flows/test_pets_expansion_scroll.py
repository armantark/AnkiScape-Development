"""Equipment's existing scrollbar reaches expanded Pets, actions, and gear."""

from __future__ import annotations

import unittest
from itertools import product

from tests import test_main_menu_widget as _main_menu
from tests.ui_flows.test_first_cell_selection import _dark_palette, _player
from tests.ui_flows.test_pets_visible_rows import reveal_widget, visible_rect
from tests.ui_flows.test_tree_text_fit import _pump

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPoint, QPushButton, QScrollArea, QTreeWidget, QWidget


def _scroll_ancestor(widget):
    parent = widget.parentWidget()
    while parent is not None and not isinstance(parent, QScrollArea):
        parent = parent.parentWidget()
    return parent


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class PetsExpansionScrollTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        app = QApplication.instance()
        self.addCleanup(app.setPalette, app.palette())
        self.addCleanup(app.setFont, app.font())

    def tearDown(self):
        self.menu.tearDown()

    def _open(self, width):
        dialog = self.menu._open(_player(), current_skill="Mining")
        dialog.show()
        dialog.resize(width, 560)
        _main_menu._open_equipment_tab(dialog)
        _pump()
        return dialog

    def _assert_reachable_controls(self, dialog):
        pets = dialog.findChild(QTreeWidget, "summoningPetsLog")
        pets_scroll = _scroll_ancestor(pets)
        gear = dialog.findChild(QWidget, "equipmentCombatSetupPanel")
        gear_scroll = _scroll_ancestor(gear)
        self.assertIsNotNone(pets_scroll)
        self.assertIsNotNone(gear_scroll)
        self.assertIs(pets_scroll, gear_scroll)
        anchors = [dialog.findChild(QWidget, name) for name in (
            "equipmentPointsHeader", "summoningFollowerSummary",
            "summoningFamiliarPicker", "summoningPetsToggle",
        )]
        points = anchors[0]
        before = points.mapTo(dialog, QPoint())
        bar = gear_scroll.verticalScrollBar()
        self.assertGreater(bar.maximum(), 0)
        bar.setValue(0)
        _pump()
        content_top = gear.mapTo(dialog, QPoint())
        bar.setValue(bar.maximum())
        _pump()
        self.assertLess(gear.mapTo(dialog, QPoint()).y(), content_top.y())
        self.assertEqual(points.mapTo(dialog, QPoint()), before)
        for widget in anchors:
            reveal_widget(widget)
            self.assertTrue(visible_rect(widget).contains(widget.rect()), widget.objectName())
            hit = QApplication.widgetAt(widget.mapToGlobal(widget.rect().center()))
            self.assertTrue(hit is widget or widget.isAncestorOf(hit), widget.objectName())
        for name in ("summoningLetOutPetButton", "summoningReleasePetButton"):
            button = dialog.findChild(QPushButton, name)
            reveal_widget(button)
            self.assertTrue(visible_rect(button).contains(button.rect()), name)
            self.assertIs(QApplication.widgetAt(button.mapToGlobal(button.rect().center())), button)
        self.assertEqual(pets.height(), 210)
        self.assertEqual(pets.verticalScrollMode(), QTreeWidget.ScrollMode.ScrollPerItem)

    def test_existing_equipment_scroll_reaches_pets_and_controls_with_fixed_points(self):
        app = QApplication.instance()
        original_font = app.font()
        themes = (("light", app.style().standardPalette()), ("dark", _dark_palette()))
        for (theme, palette), scale, width in product(themes, (1.0, 1.5), (720, 980)):
            app.setPalette(palette)
            font = app.font()
            font.setPointSizeF(original_font.pointSizeF() * scale)
            app.setFont(font)
            dialog = self._open(width)
            dialog.findChild(QPushButton, "summoningPetsToggle").click()
            _pump()
            with self.subTest(theme=theme, scale=scale, width=width):
                self.assertEqual((dialog.width(), dialog.height()), (width, 560))
                self._assert_reachable_controls(dialog)
            dialog.close()

    def test_collapsing_pets_restores_the_original_gear_space(self):
        for width in (720, 980):
            dialog = self._open(width)
            gear_scroll = _scroll_ancestor(dialog.findChild(QWidget, "equipmentCombatSetupPanel"))
            follower = dialog.findChild(QWidget, "summoningFollowerPanel")
            bar = gear_scroll.verticalScrollBar()
            bar.setValue(0)
            _pump()
            before = (gear_scroll.geometry(), follower.geometry(), bar.maximum())
            toggle = dialog.findChild(QPushButton, "summoningPetsToggle")
            pets = dialog.findChild(QTreeWidget, "summoningPetsLog")
            with self.subTest(width=width):
                self.assertFalse(pets.isVisible())
                toggle.click()
                _pump()
                self.assertTrue(pets.isVisible())
                self.assertEqual(gear_scroll.geometry(), before[0])
                self.assertGreater(bar.maximum(), before[2])
                reveal_widget(toggle)
                self.assertIs(QApplication.widgetAt(toggle.mapToGlobal(toggle.rect().center())), toggle)
                toggle.click()
                bar.setValue(0)
                _pump()
                self.assertFalse(pets.isVisible())
                self.assertEqual((gear_scroll.geometry(), follower.geometry(), bar.maximum()), before)
            dialog.close()
