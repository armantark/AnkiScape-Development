"""Shop selection state and Sawmill discovery through the real main menu."""

import unittest

from tests import test_main_menu_widget as menu
from tests.main_menu import fixtures

if menu.HAS_AQT:
    from aqt.qt import QApplication, QSpinBox, QToolButton, Qt
    from PyQt6.QtTest import QTest


@unittest.skipUnless(menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class ShopSelectionTest(fixtures.MainMenuWidgetTest):
    def _shop(self):
        pd = menu._make_player_data()
        pd["inventory"]["Coins"] = 1_000_000
        dialog = self._open(pd)
        menu._open_shop_tab(dialog)
        dialog.show()
        dialog.resize(900, 560)
        self._pump()
        return dialog, pd

    def _pump(self):
        for _ in range(4):
            QApplication.processEvents()

    def _click_result(self, selector, **identity):
        item = next(
            selector.item(i) for i in range(selector.count())
            if all((selector.item(i).data(Qt.ItemDataRole.UserRole) or {}).get(key) == value
                   for key, value in identity.items())
        )
        selector.scrollToItem(item)
        self._pump()
        QTest.mouseClick(selector.viewport(), Qt.MouseButton.LeftButton,
                         pos=selector.visualItemRect(item).center())
        self._pump()

    def test_changed_query_scrolls_both_lists_to_top_but_purchase_and_stock_refresh_keep_position(self):
        dialog, pd = self._shop()
        search = menu._find_named_line_edit(dialog, "shopSearchInput")
        normal = menu._find_named_list(dialog, "shopSelectionList")
        rewards = menu._find_named_list(dialog, "rewardShopTargetList")
        self._click_result(normal, shop_id="bobs_brilliant_axes")
        search.setText("a")
        self._pump()
        bars = [selector.verticalScrollBar() for selector in (normal, rewards)]
        for bar in bars:
            self.assertGreater(bar.maximum(), 0)
            bar.setValue(bar.maximum())
        search.setText("e")
        self._pump()
        self.assertEqual([bar.value() for bar in bars], [0, 0])

        search.clear()
        self._pump()
        for bar in bars:
            bar.setValue(bar.maximum())
        positions = [bar.value() for bar in bars]
        before = pd["inventory"].get("Bronze hatchet", 0)
        menu._find_named_button(dialog, "shopTransactionButton").click()
        self._pump()
        self.assertEqual(pd["inventory"]["Bronze hatchet"], before + 1)
        self.assertEqual([bar.value() for bar in bars], positions)

        tabs = menu._find_main_tabs(dialog)
        tabs.setCurrentIndex(0)
        self._pump()
        menu._open_shop_tab(dialog)
        self._pump()
        self.assertEqual([bar.value() for bar in bars], positions)

    def test_purchase_quantity_follows_shop_and_row_by_tile_and_search(self):
        dialog, pd = self._shop()
        selector = menu._find_named_list(dialog, "shopSelectionList")
        self._click_result(selector, shop_id="bobs_brilliant_axes")
        quantity = dialog.findChild(QSpinBox, "shopCustomQuantitySpin")
        quantity.setValue(50)
        tile = next(button for button in dialog.findChildren(QToolButton)
                    if button.property("shopRowId") and button.text() == "Iron hatchet")
        tile.click()
        self._pump()
        self.assertEqual(quantity.value(), 1)
        quantity.setValue(7)
        tile = next(button for button in dialog.findChildren(QToolButton)
                    if button.property("shopRowId") and button.text() == "Iron hatchet")
        tile.click()
        self._pump()
        self.assertEqual(quantity.value(), 7)

        search = menu._find_named_line_edit(dialog, "shopSearchInput")
        search.setText("hatchet")
        self._pump()
        self.assertEqual(quantity.value(), 7)
        self._click_result(selector, shop_id="bobs_brilliant_axes", item_name="Bronze hatchet")
        self.assertEqual(quantity.value(), 1)
        self._click_result(selector, shop_id="bobs_brilliant_axes", item_name="Iron hatchet")
        quantity.setValue(3)
        before = pd["inventory"].get("Iron hatchet", 0)
        menu._find_named_button(dialog, "shopTransactionButton").click()
        self._pump()
        self.assertEqual(pd["inventory"]["Iron hatchet"], before + 3)
        self.assertEqual(quantity.value(), 3)
        self.assertEqual(selector.currentItem().data(Qt.ItemDataRole.UserRole)["item_name"], "Iron hatchet")
        self._click_result(selector, shop_id="bobs_brilliant_axes", item_name="Iron hatchet")
        self.assertEqual(quantity.value(), 3)
        search.setText("Bronze hatchet")
        self._pump()
        self._click_result(selector, shop_id="will_woodcut_shop", item_name="Bronze hatchet")
        self.assertEqual(quantity.value(), 1)

    def test_sawmill_and_plank_queries_find_all_four_stable_utility_ids(self):
        dialog = self._open(menu._make_player_data())
        tree = self._open_utility(dialog)
        search = menu._find_named_line_edit(tree.parentWidget(), "utilityActivityTargetSearchInput")
        expected = {
            "convert_logs_to_planks": "Sawmill: Plank",
            "convert_oak_logs_to_oak_planks": "Sawmill: Oak plank",
            "convert_teak_logs_to_teak_planks": "Sawmill: Teak plank",
            "convert_mahogany_logs_to_mahogany_planks": "Sawmill: Mahogany plank",
        }
        for query in ("sawmill", "plank"):
            with self.subTest(query=query):
                search.setText(query)
                self._pump()
                shown = {item.data(0, Qt.ItemDataRole.UserRole): item.text(0)
                         for item in menu._tree_items(tree)
                         if not item.childCount() and not item.isHidden()}
                for utility_id, label in expected.items():
                    self.assertIn(utility_id, shown)
                    self.assertIn(label, shown[utility_id])
