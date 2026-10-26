from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _find_named_line_edit,
    _find_named_list,
    _list_texts,
    _open_first_shop,
    _open_shop_tab,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLineEdit, QSpinBox, QTabWidget, QToolButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_shop_icons_render_for_stock_search_sell_and_services(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        dialog = self._open(fixtures["fixture_player_data"])
        _open_shop_tab(dialog)
        _open_first_shop(dialog)

        stock_buttons = [
            button for button in dialog.findChildren(QToolButton)
            if button.property("shopRowId")
        ]
        self.assertTrue(any(not button.icon().isNull() for button in stock_buttons), "live stock tiles should use item icons")
        self.assertTrue(
            any(button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextUnderIcon for button in stock_buttons),
            "stock tile icons should render above the text",
        )

        sell_list = _find_named_list(dialog, "shopSellInventoryList")
        beer_item = next(
            sell_list.item(i)
            for i in range(sell_list.count())
            if sell_list.item(i).data(Qt.ItemDataRole.UserRole) == "Beer"
        )
        self.assertFalse(beer_item.icon().isNull(), "sell rows should use inventory item icons")

        search = _find_named_line_edit(dialog, "shopSearchInput")
        search.setText("Red blossom seed")
        QApplication.processEvents()
        selector = _find_named_list(dialog, "shopSelectionList")
        seed_item = next(
            selector.item(i)
            for i in range(selector.count())
            if "Red blossom seed" in selector.item(i).text()
        )
        self.assertFalse(seed_item.icon().isNull(), "item-first search rows should use shop item icons")

        service_list = _find_named_list(dialog, "shopServiceList")
        kebab_item = next(
            service_list.item(i)
            for i in range(service_list.count())
            if "kebab" in service_list.item(i).text().lower()
        )
        self.assertFalse(kebab_item.icon().isNull(), "vendor rows should use output item icons")

    def test_shop_service_providers_browse_as_their_own_selector_entries(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures
        from ankiscape.data.shop_data import SHOP_VENDOR_ACTIONS

        fixtures = build_shop_frontend_fixtures()
        action_id = fixtures["vendor_action_transaction"]["action_id"]
        provider = str(SHOP_VENDOR_ACTIONS[action_id]["provider"])
        dialog = self._open(fixtures["fixture_player_data"])
        _open_shop_tab(dialog)

        selector = _find_named_list(dialog, "shopSelectionList")
        provider_item = None
        for index in range(selector.count()):
            payload = selector.item(index).data(Qt.ItemDataRole.UserRole)
            if isinstance(payload, dict) and payload.get("kind") == "provider" and payload.get("provider") == provider:
                provider_item = selector.item(index)
                break
        self.assertIsNotNone(provider_item, f"provider row for {provider!r} missing from browse list")
        selector.setCurrentItem(provider_item)
        QApplication.processEvents()

        # Provider mode shows only that provider's services; the shop-only
        # panels (stock/transaction) stay hidden.
        title = _find_named_label(dialog, "shopDetailTitle")
        self.assertEqual(title.text(), provider)
        services_panel = dialog.findChild(QWidget, "shopServicesPanel")
        self.assertTrue(services_panel.isVisibleTo(dialog))
        mode_tabs = dialog.findChild(QTabWidget, "shopModeTabs")
        self.assertFalse(mode_tabs.isVisibleTo(dialog))
        service_list = _find_named_list(dialog, "shopServiceList")
        for index in range(service_list.count()):
            payload = service_list.item(index).data(Qt.ItemDataRole.UserRole)
            self.assertIsInstance(payload, dict)
            source_kind = payload.get("kind")
            row_id = payload.get("id")
            self.assertEqual(source_kind, "vendor_action")
            self.assertEqual(str(SHOP_VENDOR_ACTIONS[row_id]["provider"]), provider)

    def test_thakkrad_service_renders_and_cures_yak_hide(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

        pd = build_shop_frontend_fixtures()["fixture_player_data"]
        pd["inventory"].update({"Coins": 10, "Yak-hide": 2})
        pd["quests"] = {
            "the_fremennik_isles": {
                "started": True,
                "progress": 5,
                "completed": False,
            }
        }
        dialog = self._open(pd)
        _open_shop_tab(dialog)

        selector = _find_named_list(dialog, "shopSelectionList")
        provider_item = next(
            selector.item(index)
            for index in range(selector.count())
            if (
                isinstance(
                    selector.item(index).data(Qt.ItemDataRole.UserRole), dict
                )
                and selector.item(index).data(Qt.ItemDataRole.UserRole).get(
                    "provider"
                )
                == "Thakkrad Sigmundson"
            )
        )
        selector.setCurrentItem(provider_item)
        QApplication.processEvents()

        service_list = _find_named_list(dialog, "shopServiceList")
        service_item = next(
            service_list.item(index)
            for index in range(service_list.count())
            if service_list.item(index).data(Qt.ItemDataRole.UserRole).get("id")
            == "thakkrad_cure_yak_hide"
        )
        service_list.setCurrentItem(service_item)
        QApplication.processEvents()

        self.assertFalse(service_item.icon().isNull())
        self.assertIn(
            "1 × Yak-hide + 5 Coins → 1 × Cured yak-hide",
            service_item.text(),
        )
        quantity = dialog.findChild(QSpinBox, "shopServiceQuantitySpin")
        quantity.setValue(2)
        QApplication.processEvents()
        preview = _find_named_label(dialog, "shopServicePreviewLabel")
        self.assertIn("10 Coins", preview.text())
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), preview.text())
        use_button.click()
        QApplication.processEvents()

        self.assertEqual(pd["inventory"]["Coins"], 0)
        self.assertEqual(pd["inventory"]["Yak-hide"], 0)
        self.assertEqual(pd["inventory"]["Cured yak-hide"], 2)

    def test_shop_service_and_vendor_actions_apply_and_feed_global_history(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures
        from ankiscape.data.shop_data import SHOP_SERVICES, SHOP_VENDOR_ACTIONS

        fixtures = build_shop_frontend_fixtures()
        pd = fixtures["fixture_player_data"]
        pd["inventory"].update({"Agility potion (1)": 4, "Agility potion (3)": 4})
        pd["inventory"].update(
            {
                "Potion flask": 1,
                "Attack potion (3)": 2,
                "Attack flask (2)": 1,
            }
        )
        pd["quests"] = {
            "as_a_first_resort": {"completed": True},
            "the_giant_dwarf": {"started": True, "completed": False},
        }
        pd["summoning_level"] = 99
        pd["fletching_exp"] = 1234.5
        pd["inventory"]["Pack yak pouch"] = 3
        pd["inventory"]["Long kebbit spike"] = 2
        pd["inventory"]["Empty pot"] = 2
        vendor_action_id = fixtures["vendor_action_transaction"]["action_id"]
        dialog = self._open(pd)
        _open_shop_tab(dialog)

        selector = _find_named_list(dialog, "shopSelectionList")
        service_list = _find_named_list(dialog, "shopServiceList")

        def _select_service_row(row_id: str) -> QListWidgetItem:
            source = SHOP_SERVICES if row_id in SHOP_SERVICES else SHOP_VENDOR_ACTIONS
            provider = str(source[row_id]["provider"])
            provider_item = next(
                selector.item(index)
                for index in range(selector.count())
                if (
                    isinstance(selector.item(index).data(Qt.ItemDataRole.UserRole), dict)
                    and selector.item(index).data(Qt.ItemDataRole.UserRole).get("kind") == "provider"
                    and selector.item(index).data(Qt.ItemDataRole.UserRole).get("provider") == provider
                )
            )
            selector.setCurrentItem(provider_item)
            QApplication.processEvents()
            for index in range(service_list.count()):
                item = service_list.item(index)
                payload = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(payload, dict) and payload.get("id") == row_id:
                    service_list.setCurrentItem(item)
                    QApplication.processEvents()
                    return item
            raise AssertionError(f"service/vendor row {row_id!r} not found")

        bob_item = _select_service_row("bob_barter_decant_four")
        self.assertFalse(bob_item.icon().isNull())
        dose_spin = dialog.findChild(QSpinBox, "shopServiceQuantitySpin")
        self.assertIsNotNone(dose_spin)
        self.assertTrue(dose_spin.isVisibleTo(dialog))
        self.assertEqual((dose_spin.minimum(), dose_spin.maximum()), (2, 4))
        dose_spin.setValue(3)
        QApplication.processEvents()
        preview_label = _find_named_label(dialog, "shopServicePreviewLabel")
        self.assertIn("16 doses", preview_label.text())
        self.assertIn("3-dose vials", preview_label.text())
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), preview_label.text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Agility potion (1)"], 1)
        self.assertEqual(pd["inventory"]["Agility potion (3)"], 5)
        self.assertEqual(pd["inventory"].get("Agility potion (4)", 0), 0)
        self.assertEqual(pd["inventory"]["Vial"], 2)

        teplin_fill = _select_service_row("teplin_fill_potion_flasks")
        self.assertFalse(teplin_fill.icon().isNull())
        self.assertIn("Free", teplin_fill.text())
        self.assertNotIn("+ 0 Coins", teplin_fill.text())
        self.assertEqual(service_list.maximumHeight(), 96)
        self.assertFalse(dose_spin.isVisibleTo(dialog))
        preview_label = _find_named_label(dialog, "shopServicePreviewLabel")
        self.assertIn("6 doses", preview_label.text())
        self.assertIn("1 empty Potion flask", preview_label.text())
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), preview_label.text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Potion flask"], 0)
        self.assertEqual(pd["inventory"]["Attack potion (3)"], 0)
        self.assertEqual(pd["inventory"]["Attack flask (2)"], 1)
        self.assertEqual(pd["inventory"]["Attack flask (6)"], 1)
        self.assertEqual(pd["inventory"]["Vial"], 4)

        teplin_decant = _select_service_row(
            "teplin_decant_flasks_to_vials"
        )
        self.assertFalse(teplin_decant.icon().isNull())
        self.assertFalse(dose_spin.isVisibleTo(dialog))
        preview_label = _find_named_label(dialog, "shopServicePreviewLabel")
        self.assertIn("2 doses", preview_label.text())
        self.assertIn("1 vial for free", preview_label.text())
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), preview_label.text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Attack flask (2)"], 0)
        self.assertEqual(pd["inventory"]["Attack flask (6)"], 1)
        self.assertEqual(pd["inventory"]["Attack potion (2)"], 1)

        _select_service_row("bartender_sell_beer_glass")
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        before_glass = pd["inventory"]["Beer glass"]
        before_coins = pd["inventory"]["Coins"]
        self.assertTrue(use_button.isEnabled(), _find_named_label(dialog, "shopServicePreviewLabel").text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Beer glass"], before_glass - 1)
        self.assertGreater(pd["inventory"]["Coins"], before_coins)

        service_list = _find_named_list(dialog, "shopServiceList")
        _select_service_row(vendor_action_id)
        vendor_output = SHOP_VENDOR_ACTIONS[vendor_action_id]["outputs"][0]
        vendor_output_name = vendor_output["item_name"]
        vendor_output_quantity = int(vendor_output["quantity"])
        before_vendor_output = pd["inventory"].get(vendor_output_name, 0)
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), _find_named_label(dialog, "shopServicePreviewLabel").text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"].get(vendor_output_name, 0), before_vendor_output + vendor_output_quantity)

        _select_service_row("bogrog_exchange_packyak")
        dose_spin = dialog.findChild(QSpinBox, "shopServiceQuantitySpin")
        self.assertTrue(dose_spin.isVisibleTo(dialog))
        dose_spin.setValue(2)
        QApplication.processEvents()
        before_shards = pd["inventory"].get("Spirit shards", 0)
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(
            use_button.isEnabled(),
            _find_named_label(dialog, "shopServicePreviewLabel").text(),
        )
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Pack yak pouch"], 1)
        self.assertEqual(
            pd["inventory"]["Spirit shards"],
            before_shards + (2 * 148),
        )

        leon_item = _select_service_row("leon_fletch_long_kebbit_bolts")
        self.assertFalse(leon_item.icon().isNull())
        self.assertNotIn("Service:", leon_item.text())
        self.assertNotIn("· Leon", leon_item.text())
        self.assertIn(
            "1 × Long kebbit spike + 40 Coins → 6 × Long kebbit bolts",
            leon_item.text(),
        )
        quantity_spin = dialog.findChild(QSpinBox, "shopServiceQuantitySpin")
        self.assertTrue(quantity_spin.isVisibleTo(dialog))
        quantity_spin.setValue(2)
        QApplication.processEvents()
        preview_label = _find_named_label(dialog, "shopServicePreviewLabel")
        self.assertIn("80 Coins", preview_label.text())
        self.assertIn(
            "Long kebbit spike: 2 owned, 2 needed",
            preview_label.text(),
        )
        before_coins = pd["inventory"]["Coins"]
        before_fletching_exp = pd["fletching_exp"]
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), preview_label.text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Coins"], before_coins - 80)
        self.assertEqual(pd["inventory"]["Long kebbit spike"], 0)
        self.assertEqual(pd["inventory"]["Long kebbit bolts"], 12)
        self.assertEqual(pd["fletching_exp"], before_fletching_exp)

        blandebir_item = _select_service_row("blandebir_fill_ale_yeast")
        self.assertFalse(blandebir_item.icon().isNull())
        self.assertNotIn("· Blandebir", blandebir_item.text())
        self.assertIn(
            "1 × Empty pot + 25 Coins → 1 × Ale yeast",
            blandebir_item.text(),
        )
        quantity_spin = dialog.findChild(QSpinBox, "shopServiceQuantitySpin")
        self.assertTrue(quantity_spin.isVisibleTo(dialog))
        quantity_spin.setValue(2)
        QApplication.processEvents()
        preview_label = _find_named_label(dialog, "shopServicePreviewLabel")
        self.assertIn("50 Coins", preview_label.text())
        self.assertIn("Empty pot: 2 owned, 2 needed", preview_label.text())
        before_coins = pd["inventory"]["Coins"]
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), preview_label.text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Coins"], before_coins - 50)
        self.assertEqual(pd["inventory"]["Empty pot"], 0)
        self.assertEqual(pd["inventory"]["Ale yeast"], 2)

        global_button = _find_named_button(dialog, "shopGlobalHistoryButton")
        global_button.click()
        QApplication.processEvents()
        global_history = _find_named_list(dialog, "shopGlobalHistoryList")
        history_texts = _list_texts(global_history)
        self.assertTrue(any("Completed" in text for text in history_texts), history_texts)

        search = dialog.findChild(QLineEdit, "shopSearchInput")
        search.setText("Teplin")
        QApplication.processEvents()
        search_rows = _list_texts(
            _find_named_list(dialog, "shopSelectionList")
        )
        self.assertEqual(len(search_rows), 2)
        self.assertTrue(all("Free" in text for text in search_rows))
        self.assertTrue(all("0 Coins" not in text for text in search_rows))
