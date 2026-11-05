from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QPushButton, QTreeWidget, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_construction_house_sheet_and_locked_click_guard(self) -> None:
        pd = _make_player_data()
        pd.update({
            "construction_level": 99, "construction_exp": 0,
            "house_owned": True, "house_rooms_bought": {"garden": True, "parlour": True},
            "house_servant": "", "house_built_flags": {}, "house_style": "basic_wood",
            "current_construction": "crude_wooden_chair", "inventory": {},
        })
        dialog = self._open(pd, current_skill="Construction")
        self.assertIsNotNone(dialog.findChild(QLabel, "constructionHouseSummary"))
        self.assertIsNotNone(dialog.findChild(QWidget, "constructionHouseRoomView"))
        tree = dialog.findChild(QTreeWidget, "constructionTargetTree")
        self.assertIsNotNone(tree)
        # No staircase room is bought; the Bank alone would only make a row plan-only.
        locked = next(item for item in _tree_items(tree) if item.data(0, Qt.ItemDataRole.UserRole) == "oak_staircase")
        self.assertTrue(locked.isDisabled())
        before = list(self._construction_calls)
        tree.itemClicked.emit(locked, 0)
        QApplication.processEvents()
        self.assertEqual(self._construction_calls, before)

    def test_construction_house_purchase_refreshes_the_sheet(self) -> None:
        pd = _make_player_data()
        pd.update({
            "construction_level": 99,
            "house_owned": False,
            "house_rooms_bought": {},
            "inventory": {"Coins": 1_000},
        })
        dialog = self._open(pd, current_skill="Construction")
        dialog.findChild(QPushButton, "constructionPurchaseHouseButton").click()
        QApplication.processEvents()

        self.assertTrue(pd["house_owned"])
        self.assertIsNone(dialog.findChild(QPushButton, "constructionPurchaseHouseButton"))
        self.assertIn("House · 2 rooms", dialog.findChild(QLabel, "constructionHouseSummary").text())
