"""The Bank tool belt panel shows the 2012 belt tools a player never carries."""

from __future__ import annotations

import unittest
from unittest import mock

from tests import test_main_menu_widget as _main_menu
from tests.test_main_menu_widget import HAS_AQT, _bank_grid_texts, _list_texts, _make_player_data, _open_bank_tab

if HAS_AQT:
    from aqt.qt import QApplication, QListWidget, QMenu, QPushButton, Qt, QWidget


def _chips(group) -> list:
    return [
        chip
        for chip in group.findChildren(QWidget)
        if chip.objectName().startswith("toolBeltTool::") and not chip.isHidden()
    ]


def _plain(group) -> str:
    return " ".join(str(chip.property("toolName")) for chip in _chips(group))


def _pump() -> None:
    for _ in range(4):
        QApplication.processEvents()


def _greyed_tools(group) -> set[str]:
    """Tool names the group draws greyed, waiting for an Add-to-toolbelt action."""
    return {str(chip.property("toolName")) for chip in _chips(group) if chip.property("greyed")}


def _belt_group_labels(dialog) -> dict:
    grid = dialog.findChild(QWidget, "toolBeltAlwaysPanel").layout()
    return {
        grid.itemAtPosition(row, 0).widget().text(): grid.itemAtPosition(row, 1).widget()
        for row in range(grid.rowCount())
    }


class _FakeCol:
    def __init__(self) -> None:
        self.config: dict = {}

    def get_config(self, key, default=None):
        return self.config.get(key, default)

    def set_config(self, key, value):
        self.config[key] = value


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

    def _open_bank(self, data, **extra):
        dialog = self.menu._open(data, current_skill="Mining", **extra)
        dialog.show()
        dialog.resize(900, 560)
        QApplication.processEvents()
        _open_bank_tab(dialog)
        _pump()
        return dialog

    def _open_with_belt_backend(self, data):
        from ankiscape.core.constants import MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA
        from ankiscape.logic_pure.logic_pure_equipment import put_tool_on_belt_pure

        def attach(item_name: str) -> bool:
            updated, changed = put_tool_on_belt_pure(data, item_name, MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA)
            data.update(updated)
            return changed

        return self._open_bank(data, on_attach_tool=attach)

    def _right_click_tool(self, group, tool_name: str):
        """Right-click ``tool_name`` in the group and return the menu Qt would show."""
        shown: list = []
        chip = next(chip for chip in _chips(group) if chip.property("toolName") == tool_name)
        with mock.patch.object(QMenu, "exec", lambda menu, *_args: shown.append(menu)):
            if chip.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu:
                chip.customContextMenuRequested.emit(chip.rect().center())
            _pump()
        return shown[-1] if shown else None

    def test_bank_lists_belt_tools_by_group_and_fits_the_owner_window(self) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        data = _make_player_data()
        data["toolbelt"] = {}
        dialog = self._open_bank(data)

        gear_rows = _list_texts(dialog.findChild(QListWidget, "gearList"))
        self.assertEqual(gear_rows, ["No pickaxe or hatchet attached."])
        groups = _belt_group_labels(dialog)
        self.assertEqual(list(groups), ["General", "Fishing", "Crafting", "Farming"])
        self.assertIn("Fishing rod", _plain(groups["Fishing"]))
        self.assertIn("Spade", _plain(groups["Farming"]))
        self.assertNotIn("Bronze pickaxe", _plain(groups["General"]))
        self.assertEqual(groups["Fishing"].toolTip(), "Always on your tool belt.")
        # Only the two quest moulds a new 2012 account lacked start greyed.
        self.assertEqual(_greyed_tools(groups["Crafting"]), {"Ammo mould", "Chain link mould"})
        self.assertEqual(_greyed_tools(groups["General"]), set())
        self.assertEqual(text_fit_defects(dialog.findChild(QWidget, "toolbeltPanel")), [])

    def test_collapsed_panel_stays_collapsed_when_the_bank_reopens(self) -> None:
        ui = self.menu._ui

        class _FakeMw(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self.col = _FakeCol()

        orig_mw = ui.mw
        ui.mw = _FakeMw()
        try:
            data = _make_player_data()
            dialog = self._open_bank(data)
            header = dialog.findChild(QPushButton, "toolbeltHeader")
            self.assertTrue(dialog.findChild(QListWidget, "gearList").isVisible())

            header.click()
            _pump()
            self.assertFalse(dialog.findChild(QListWidget, "gearList").isVisible())
            self.assertFalse(dialog.findChild(QWidget, "toolBeltAlwaysPanel").isVisible())
            dialog.close()

            reopened = self._open_bank(data)
            self.assertFalse(reopened.findChild(QPushButton, "toolbeltHeader").isChecked())
            self.assertFalse(reopened.findChild(QListWidget, "gearList").isVisible())

            reopened.findChild(QPushButton, "toolbeltHeader").click()
            _pump()
            self.assertTrue(reopened.findChild(QWidget, "toolBeltAlwaysPanel").isVisible())
            reopened.close()
            self.assertTrue(self._open_bank(data).findChild(QListWidget, "gearList").isVisible())
        finally:
            ui.mw = orig_mw

    def test_adding_chain_link_mould_uses_the_bank_copy_and_ungreys_it(self) -> None:
        data = _make_player_data()
        data["inventory"] = {"Chain link mould": 1, "Logs": 3}
        dialog = self._open_with_belt_backend(data)
        crafting = _belt_group_labels(dialog)["Crafting"]
        self.assertIn("Chain link mould x1", _bank_grid_texts(dialog))

        # A tool already on the belt offers nothing to add.
        self.assertIsNone(self._right_click_tool(crafting, "Holy mould"))
        menu = self._right_click_tool(crafting, "Chain link mould")
        action = menu.actions()[0]
        self.assertEqual(action.text(), "Add to tool belt")
        self.assertTrue(action.isEnabled())
        action.trigger()
        _pump()

        self.assertNotIn("Chain link mould", data["inventory"])
        self.assertEqual(data["toolbelt_added"], ["Chain link mould"])
        self.assertNotIn("Chain link mould x1", _bank_grid_texts(dialog))
        self.assertIn("Logs x3", _bank_grid_texts(dialog))
        self.assertEqual(_greyed_tools(crafting), {"Ammo mould"})
        self.assertIsNone(self._right_click_tool(crafting, "Chain link mould"))

        # The added mould survives a fresh dialog built from the saved data.
        reopened = self._open_bank(data)
        self.assertEqual(_greyed_tools(_belt_group_labels(reopened)["Crafting"]), {"Ammo mould"})

    def test_ammo_mould_waits_for_dwarf_cannon_and_a_bank_copy(self) -> None:
        data = _make_player_data()
        data["inventory"] = {"Ammo mould": 1}
        dialog = self._open_with_belt_backend(data)
        crafting = _belt_group_labels(dialog)["Crafting"]

        menu = self._right_click_tool(crafting, "Ammo mould")
        action = menu.actions()[0]
        self.assertIn("Dwarf Cannon", action.text())
        self.assertFalse(action.isEnabled())
        action.trigger()
        _pump()
        self.assertEqual(data["inventory"], {"Ammo mould": 1})
        self.assertNotIn("toolbelt_added", data)

        data["quests"]["dwarf_cannon"] = {"started": True, "completed": True, "progress": 13}
        data["inventory"] = {}
        crafting = _belt_group_labels(self._open_with_belt_backend(data))["Crafting"]
        action = self._right_click_tool(crafting, "Ammo mould").actions()[0]
        self.assertIn("in your Bank", action.text())
        self.assertFalse(action.isEnabled())

        data["inventory"] = {"Ammo mould": 2}
        crafting = _belt_group_labels(self._open_with_belt_backend(data))["Crafting"]
        action = self._right_click_tool(crafting, "Ammo mould").actions()[0]
        self.assertTrue(action.isEnabled())
        action.trigger()
        _pump()
        self.assertEqual(data["inventory"], {"Ammo mould": 1})
        self.assertEqual(data["toolbelt_added"], ["Ammo mould"])
        self.assertEqual(_greyed_tools(crafting), {"Chain link mould"})


if __name__ == "__main__":
    unittest.main()
