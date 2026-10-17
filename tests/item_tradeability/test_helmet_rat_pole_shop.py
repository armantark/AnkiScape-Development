"""The ordinary Shop controls enforce the period item trade flags."""
import copy
import unittest

from tests import test_main_menu_widget as menu_fixture

if menu_fixture.HAS_AQT:
    from aqt.qt import QApplication, QTabWidget, Qt


@unittest.skipUnless(menu_fixture.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class HelmetRatPoleShopTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        menu_fixture.MainMenuWidgetTest.setUpClass()

    def test_shop_controls_refuse_lit_helmet_and_rat_pole_but_sell_unlit_helmet(self):
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data
        from ankiscape.logic.shop_logic import SHOP_DATA

        menu = menu_fixture.MainMenuWidgetTest(methodName="runTest")
        menu.setUp()
        self.addCleanup(menu.tearDown)
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["inventory"].update({"Mining helmet (lit)": 1, "Mining helmet (unlit)": 1, "Rat pole": 3})
        dialog = menu._open(player)
        menu_fixture._open_shop_tab(dialog)
        dialog.show()
        dialog.resize(900, 560)
        QApplication.processEvents()
        shop_id = next(shop["id"] for shop in SHOP_DATA.values()
                       if shop["visibility"] == "visible" and shop["general_store"] and not shop.get("required_quests"))
        selector = menu_fixture._find_named_list(dialog, "shopSelectionList")
        row = next(selector.item(i) for i in range(selector.count())
                   if (selector.item(i).data(Qt.ItemDataRole.UserRole) or {}).get("shop_id") == shop_id)
        selector.setCurrentItem(row)
        dialog.findChild(QTabWidget, "shopModeTabs").setCurrentIndex(1)
        QApplication.processEvents()
        items = menu_fixture._find_named_list(dialog, "shopSellInventoryList")
        button = menu_fixture._find_named_button(dialog, "shopTransactionButton")
        preview = menu_fixture._find_named_label(dialog, "shopPreviewLabel")
        for name in ("Mining helmet (lit)", "Rat pole"):
            item = next(items.item(i) for i in range(items.count())
                        if items.item(i).data(Qt.ItemDataRole.UserRole) == name)
            items.setCurrentItem(item)
            QApplication.processEvents()
            self.assertEqual(preview.text(), "Item not tradeable")
            self.assertFalse(button.isEnabled())
            before = copy.deepcopy(player)
            button.click()
            self.assertEqual(player, before)
        item = next(items.item(i) for i in range(items.count())
                    if items.item(i).data(Qt.ItemDataRole.UserRole) == "Mining helmet (unlit)")
        items.setCurrentItem(item)
        QApplication.processEvents()
        self.assertEqual(preview.text(), "Sell 1 x Mining helmet (unlit) for 270 Coins. You have 1 x Mining helmet (unlit).")
        self.assertTrue(button.isEnabled())
        button.click()
        QApplication.processEvents()
        self.assertEqual(player["inventory"]["Mining helmet (unlit)"], 0)
        self.assertEqual(player["inventory"]["Coins"], 270)
        self.assertEqual(player["inventory"]["Mining helmet (lit)"], 1)
        self.assertEqual(player["inventory"]["Rat pole"], 3)
