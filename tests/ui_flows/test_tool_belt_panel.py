"""The Bank tool belt panel shows the 2012 belt tools a player never carries."""

from __future__ import annotations

import unittest

from tests import test_main_menu_widget as _main_menu
from tests.test_main_menu_widget import HAS_AQT, _list_texts, _make_player_data, _open_bank_tab

if HAS_AQT:
    from aqt.qt import QApplication, QListWidget, QTextDocumentFragment, QWidget


def _plain(label) -> str:
    return QTextDocumentFragment.fromHtml(label.text()).toPlainText().replace("\xa0", " ")


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class ToolBeltPanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def test_bank_lists_belt_tools_by_group_and_fits_the_owner_window(self) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        data = _make_player_data()
        data["toolbelt"] = {}
        dialog = self.menu._open(data, current_skill="Mining")
        dialog.show()
        dialog.resize(900, 560)
        QApplication.processEvents()
        _open_bank_tab(dialog)
        for _ in range(4):
            QApplication.processEvents()

        gear_rows = _list_texts(dialog.findChild(QListWidget, "gearList"))
        self.assertEqual(gear_rows, ["Toolbelt", "No pickaxe or hatchet attached."])
        grid = dialog.findChild(QWidget, "toolBeltAlwaysPanel").layout()
        groups = {
            grid.itemAtPosition(row, 0).widget().text(): grid.itemAtPosition(row, 1).widget()
            for row in range(grid.rowCount())
        }
        self.assertEqual(list(groups), ["General", "Fishing", "Crafting", "Farming"])
        self.assertIn("Fishing rod", _plain(groups["Fishing"]))
        self.assertIn("Spade", _plain(groups["Farming"]))
        self.assertNotIn("Bronze pickaxe", _plain(groups["General"]))
        self.assertEqual(groups["Fishing"].toolTip(), "Always on your tool belt.")
        self.assertEqual(text_fit_defects(dialog.findChild(QWidget, "toolbeltPanel")), [])


if __name__ == "__main__":
    unittest.main()
