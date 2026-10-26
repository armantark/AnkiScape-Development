"""Pet actions accept real clicks through the short Equipment window."""

from __future__ import annotations

from itertools import product
import unittest
from unittest.mock import patch

from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as _main_menu_fixtures
from tests.ui_flows.test_first_cell_selection import _dark_palette, _player
from tests.ui_flows.test_pets_visible_rows import reveal_widget, visible_rect
from tests.ui_flows.test_tree_text_fit import _pump

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QMessageBox, QPushButton, Qt, QTreeWidget
    from PyQt6.QtTest import QTest


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class PetsActionReachabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _main_menu_fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = _main_menu_fixtures.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        app = QApplication.instance()
        self.addCleanup(app.setFont, app.font())
        self.addCleanup(app.setPalette, app.palette())

    def tearDown(self):
        self.menu.tearDown()

    def _click_visible(self, widget):
        reveal_widget(widget)
        _pump()
        self.assertTrue(visible_rect(widget).contains(widget.rect()),
                        f"{widget.objectName()}: visible={visible_rect(widget)}, rect={widget.rect()}")
        self.assertIs(QApplication.widgetAt(widget.mapToGlobal(widget.rect().center())), widget)
        QTest.mouseClick(widget, Qt.MouseButton.LeftButton)
        _pump()

    def _select_cat(self, pets):
        item = next(pets.topLevelItem(i) for i in range(pets.topLevelItemCount())
                    if pets.topLevelItem(i).text(0) == "Cat")
        cell = pets.indexFromItem(item, 3)
        pets.scrollTo(cell, QTreeWidget.ScrollHint.PositionAtTop)
        _pump()
        reveal_widget(pets.viewport(), pets.visualRect(cell))
        room = pets.visualRect(cell)
        self.assertTrue(visible_rect(pets.viewport()).contains(room))
        self.assertIs(QApplication.widgetAt(pets.viewport().mapToGlobal(room.center())), pets.viewport())
        QTest.mouseClick(pets.viewport(), Qt.MouseButton.LeftButton, pos=room.center())
        _pump()
        self.assertEqual(pets.selectionModel().selectedIndexes(), [pets.indexFromItem(item)])

    def test_every_pet_action_accepts_clicks_at_both_fonts_sizes_and_themes(self):
        from ankiscape.logic.pet_logic import acquire_pet_pure

        player, ok, instance_id = acquire_pet_pure(_player(), "cat")
        self.assertTrue(ok)
        player["summoning_level"] = 72
        player["inventory"] = {"Phoenix egg": 1, "Cracked phoenix egg": 1}
        app = QApplication.instance()
        original_font = app.font()
        themes = (("light", app.style().standardPalette()), ("dark", _dark_palette()))
        for (theme, palette), scale, width in product(themes, (1.0, 1.5), (720, 980)):
            with self.subTest(theme=theme, scale=scale, width=width):
                app.setPalette(palette)
                font = app.font()
                font.setPointSizeF(original_font.pointSizeF() * scale)
                app.setFont(font)
                calls = []
                dialog = self.menu._open(
                    player, current_skill="Mining",
                    on_summoning_command=lambda action, payload: calls.append((action, payload)) or {"ok": True},
                )
                try:
                    dialog.show()
                    dialog.resize(width, 560)
                    _main_menu._open_equipment_tab(dialog)
                    _pump()
                    self.assertEqual((dialog.width(), dialog.height()), (width, 560))
                    self._click_visible(dialog.findChild(QPushButton, "summoningPetsToggle"))
                    pets = dialog.findChild(QTreeWidget, "summoningPetsLog")
                    actions = (
                        ("summoningLetOutPetButton", "let_out_pet", {"instance_id": instance_id}),
                        ("summoningReleasePetButton", "release_pet", {"instance_id": instance_id}),
                        ("summoningHatchCutePhoenixButton", "hatch_phoenix_egg", {"item_name": "Phoenix egg"}),
                        ("summoningHatchMeanPhoenixButton", "hatch_phoenix_egg", {"item_name": "Cracked phoenix egg"}),
                    )
                    for name, action, payload in actions:
                        self._select_cat(pets)
                        button = dialog.findChild(QPushButton, name)
                        self.assertTrue(button.isEnabled(), name)
                        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
                            self._click_visible(button)
                        self.assertEqual(calls[-1], (action, payload))
                    self.assertEqual(len(calls), len(actions))
                    self.assertEqual(pets.height(), 210)
                    self.assertEqual(pets.verticalScrollMode(), QTreeWidget.ScrollMode.ScrollPerItem)
                finally:
                    dialog.close()


if __name__ == "__main__":
    unittest.main()
