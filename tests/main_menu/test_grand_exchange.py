from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_main_tabs,
    _list_texts,
    _make_player_data,
    _open_bank_tab,
    _open_ge_tab,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QComboBox, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QSpinBox, QTest, QToolButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def _open_ge_slot_offers(self, saved=None):
        import json
        from ankiscape.core.storage_pure import migrate_loaded_data
        from ankiscape.logic.grand_exchange_logic import (
            apply_ge_frontend_action_pure,
            ge_frontend_projection_pure,
            place_ge_offer_pure,
        )

        catalog = {
            name: {"guide_price": 100, "buy_limit": 25_000, "tradeable": True, "exchangeable": True}
            for name in ("Logs", "Coal", "Iron ore")
        }
        player = _make_player_data()
        player["inventory"] = {"Coins": 10_000}
        if saved is None:
            for name in catalog:
                player, info = place_ge_offer_pure(
                    player, side="buy", item_name=name, quantity=3,
                    unit_price=100, item_spec=catalog[name],
                )
                self.assertTrue(info["ok"], info)
            middle = player["ge_player_orders"][1]
            middle.update(
                remaining_quantity=0, completed_quantity=3, escrow_coins=0,
                collectible_items=3, status="complete",
            )
            # Old saves stored only the compact list, with no slot numbers.
            for order in player["ge_player_orders"]:
                order.pop("slot", None)
        else:
            player = saved
        player = migrate_loaded_data(json.loads(json.dumps(player)), {})
        calls = []

        def projection():
            return ge_frontend_projection_pure(player, item_catalog=catalog)

        def action(action_id, payload):
            calls.append((action_id, dict(payload)))
            updated, info = apply_ge_frontend_action_pure(
                player, action_id, payload, item_catalog=catalog,
            )
            if info.get("ok") and action_id != "preview_offer":
                player.clear()
                player.update(updated)
            return {**info, "projection": projection()}

        dialog = self._open(player, get_ge_projection=projection, on_ge_action=action)
        _open_ge_tab(dialog)
        return dialog, player, calls

    def test_grand_exchange_old_save_keeps_offer_positions(self) -> None:
        dialog, player, _calls = self._open_ge_slot_offers()
        for index, name in enumerate(("Logs", "Coal", "Iron ore"), 1):
            slot = dialog.findChild(QToolButton, f"geOfferSlot{index}")
            self.assertIn(f"BUY · {name}", slot.text())
            self.assertEqual(slot.property("geOrderId"), index)
        self.assertEqual(player["inventory"]["Coins"], 9_100)
        dialog.deleteLater()

    def test_grand_exchange_claim_keeps_slots_and_new_offer_fills_gap(self) -> None:
        dialog, player, calls = self._open_ge_slot_offers()
        slots = [dialog.findChild(QToolButton, f"geOfferSlot{i}") for i in range(1, 4)]
        before = [slot.text() for slot in slots]
        QTest.mouseClick(slots[1], Qt.MouseButton.LeftButton)
        QTest.mouseClick(
            dialog.findChild(QPushButton, "geCollectOfferButton"), Qt.MouseButton.LeftButton,
        )
        QApplication.processEvents()
        self.assertEqual(calls[-1], ("collect_offer", {"order_id": 2}))
        self.assertEqual(player["inventory"]["Coal"], 3)
        self.assertEqual(slots[0].text(), before[0])
        self.assertIn("Empty offer", slots[1].text())
        self.assertEqual(slots[2].text(), before[2])

        dialog.deleteLater()
        dialog, player, calls = self._open_ge_slot_offers(player)
        slots = [dialog.findChild(QToolButton, f"geOfferSlot{i}") for i in range(1, 4)]
        self.assertIn("Empty offer", slots[1].text())
        self.assertEqual(slots[2].property("geOrderId"), 3)
        items = dialog.findChild(QListWidget, "geItemList")
        row = next(i for i in range(items.count()) if
                   items.item(i).data(Qt.ItemDataRole.UserRole)["item_name"] == "Logs")
        items.setCurrentRow(row)
        items.itemClicked.emit(items.item(row))
        QTest.mouseClick(
            dialog.findChild(QPushButton, "geSubmitOfferButton"), Qt.MouseButton.LeftButton,
        )
        QApplication.processEvents()
        self.assertEqual(calls[-1][0], "place_offer")
        self.assertEqual([slot.property("geOrderId") for slot in slots], [1, 4, 3])
        self.assertEqual(slots[0].text(), before[0])
        self.assertEqual(slots[2].text(), before[2])
        dialog.deleteLater()

    def test_initial_global_tab_can_focus_the_grand_exchange(self) -> None:
        dialog = self._open(
            _make_player_data(),
            current_skill="Mining",
            initial_global_tab="Grand Exchange",
        )
        tabs = _find_main_tabs(dialog)
        self.assertEqual(tabs.tabText(tabs.currentIndex()), "Grand Exchange")

    def test_grand_exchange_active_slot_enters_edit_mode_and_loads_order_values(self) -> None:
        dialog, _player, _calls = self._open_ge_with_active_buy_offer()

        dialog.findChild(QToolButton, "geOfferSlot1").click()
        QApplication.processEvents()

        self.assertEqual(
            dialog.findChild(QPushButton, "geSubmitOfferButton").text(),
            "Edit order",
        )
        self.assertEqual(dialog.findChild(QSpinBox, "geOfferPriceSpin").value(), 1_234)
        self.assertEqual(dialog.findChild(QSpinBox, "geOfferQuantitySpin").value(), 7)

        item_list = dialog.findChild(QListWidget, "geItemList")
        item_list.itemClicked.emit(item_list.currentItem())
        QApplication.processEvents()
        self.assertEqual(
            dialog.findChild(QPushButton, "geSubmitOfferButton").text(),
            "Place buy offer",
        )
        dialog.deleteLater()

    def test_grand_exchange_slot_text_includes_submitted_unit_price(self) -> None:
        dialog, _player, _calls = self._open_ge_with_active_buy_offer()

        self.assertIn(
            "· 1,234 Coins\n",
            dialog.findChild(QToolButton, "geOfferSlot1").text(),
        )
        dialog.deleteLater()

    def test_grand_exchange_reclicking_current_item_resets_guide_price(self) -> None:
        dialog, _player, _calls = self._open_ge_with_active_buy_offer()
        item_list = dialog.findChild(QListWidget, "geItemList")
        item_list.setCurrentRow(0)
        QApplication.processEvents()
        price = dialog.findChild(QSpinBox, "geOfferPriceSpin")
        price.setValue(777)

        item_list.itemClicked.emit(item_list.currentItem())
        QApplication.processEvents()

        self.assertEqual(price.value(), 200)
        dialog.deleteLater()

    def test_grand_exchange_slot_selection_dispatches_remainder_edit_in_one_click(self) -> None:
        dialog, player, calls = self._open_ge_with_active_buy_offer()
        dialog.findChild(QToolButton, "geOfferSlot1").click()
        dialog.findChild(QSpinBox, "geOfferQuantitySpin").setValue(3)
        dialog.findChild(QSpinBox, "geOfferPriceSpin").setValue(300)

        dialog.findChild(QPushButton, "geSubmitOfferButton").click()
        QApplication.processEvents()

        self.assertEqual(calls[-1][0], "edit_offer")
        self.assertEqual(player["ge_player_orders"][0]["remaining_quantity"], 3)
        self.assertEqual(player["ge_player_orders"][0]["submitted_unit_price"], 300)
        dialog.deleteLater()

    def test_grand_exchange_tab_renders_period_six_slots_and_routes_an_offer(self) -> None:
        from ankiscape.logic.grand_exchange_logic import (
            GE_SLOT_COUNT,
            apply_ge_frontend_action_pure,
            ge_frontend_projection_pure,
        )

        player = _make_player_data()
        player["inventory"] = {"Coins": 10_000, "Logs": 20}
        catalog = {
            "Logs": {
                "guide_price": 100,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "logs",
            },
            "Coal": {
                "guide_price": 200,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "ore",
            },
        }
        calls = []

        def projection():
            return ge_frontend_projection_pure(player, item_catalog=catalog)

        def action(action_id, payload):
            calls.append((action_id, dict(payload)))
            updated, info = apply_ge_frontend_action_pure(
                player,
                action_id,
                payload,
                item_catalog=catalog,
            )
            if info.get("ok") and action_id != "preview_offer":
                player.clear()
                player.update(updated)
            return {**info, "projection": projection()}

        dialog = self._open(
            player,
            get_ge_projection=projection,
            on_ge_action=action,
        )
        _open_ge_tab(dialog)

        slots = [
            dialog.findChild(QToolButton, f"geOfferSlot{index}")
            for index in range(1, GE_SLOT_COUNT + 1)
        ]
        self.assertTrue(all(slot is not None for slot in slots))
        slots_grid = dialog.findChild(QWidget, "geOfferSlots").layout()
        self.assertEqual(
            [
                slots_grid.getItemPosition(slots_grid.indexOf(slot))[:2]
                for slot in slots
            ],
            [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)],
        )
        self.assertIsNone(
            dialog.findChild(QToolButton, f"geOfferSlot{GE_SLOT_COUNT + 1}")
        )
        self.assertIsNone(
            dialog.findChild(QPushButton, "gePriceMinus20Button")
        )
        self.assertIsNone(
            dialog.findChild(QPushButton, "gePricePlus20Button")
        )
        self.assertTrue(all("Empty offer" in slot.text() for slot in slots))
        self.assertEqual(
            dialog.findChild(QLabel, "geCoinBalanceLabel").text(),
            "10,000 Coins",
        )
        self.assertIn(
            "guide price",
            dialog.findChild(QSpinBox, "geLowPricePercentSpin").toolTip(),
        )
        self.assertIn(
            "guide price",
            dialog.findChild(QSpinBox, "geHighPriceMultiplierSpin").toolTip(),
        )

        dialog.findChild(QToolButton, "geOfferSafetyToggle").click()
        dialog.findChild(QSpinBox, "geHighValueConfirmationSpin").setValue(
            500_000
        )
        dialog.findChild(QSpinBox, "geLowPricePercentSpin").setValue(20)
        dialog.findChild(QSpinBox, "geHighPriceMultiplierSpin").setValue(5)
        dialog.findChild(QPushButton, "geApplyOfferSafetyButton").click()
        QApplication.processEvents()
        self.assertEqual(
            player["ge_settings"],
            {
                "high_value_confirmation": 500_000,
                "low_price_multiplier": 0.2,
                "high_price_multiplier": 5.0,
            },
        )

        item_list = dialog.findChild(QListWidget, "geItemList")
        self.assertIsNotNone(item_list)
        self.assertEqual(item_list.count(), 2)
        self.assertTrue(all("Coins" in text for text in _list_texts(item_list)))
        search = dialog.findChild(QLineEdit, "geItemSearchInput")
        search.setText("no such exchange item")
        QApplication.processEvents()
        self.assertEqual(
            item_list.item(0).text(),
            "No exchangeable items match your search.",
        )
        search.clear()
        QApplication.processEvents()
        logs_row = next(
            index
            for index in range(item_list.count())
            if item_list.item(index).data(Qt.ItemDataRole.UserRole)["item_name"]
            == "Logs"
        )
        item_list.setCurrentRow(logs_row)
        QApplication.processEvents()
        self.assertIn(
            "Buy limit per 40 cards: 25,000",
            dialog.findChild(QLabel, "geSelectedItemMeta").text(),
        )
        dialog.findChild(QPushButton, "gePricePlus5Button").click()
        self.assertEqual(
            dialog.findChild(QSpinBox, "geOfferPriceSpin").value(),
            105,
        )
        dialog.findChild(QPushButton, "geSubmitOfferButton").click()
        QApplication.processEvents()

        self.assertEqual(
            [action_id for action_id, _payload in calls[-2:]],
            ["preview_offer", "place_offer"],
        )
        self.assertIn("BUY · Logs", slots[0].text())
        self.assertEqual(player["inventory"]["Coins"], 9_895)

        slots[0].click()
        dialog.findChild(QPushButton, "geEditOfferButton").click()
        dialog.findChild(QSpinBox, "geOfferQuantitySpin").setValue(2)
        dialog.findChild(QPushButton, "gePriceMinus5Button").click()
        dialog.findChild(QPushButton, "geSubmitOfferButton").click()
        QApplication.processEvents()

        self.assertEqual(calls[-1][0], "edit_offer")
        self.assertEqual(
            player["ge_player_orders"][0]["remaining_quantity"],
            2,
        )
        # -5% compounds off the price showing in the spin box (105 from the
        # earlier +5%), not off the guide price. 105 * 95 / 100 truncates to 99,
        # so a round trip does NOT return to the guide price of 100 — that is
        # the period client's behaviour, and the Guide button is the exact reset
        # it provides for precisely this reason.
        self.assertEqual(
            player["ge_player_orders"][0]["submitted_unit_price"],
            99,
        )
        self.assertIn("0/2 filled", slots[0].text())

        coal_row = next(
            index
            for index in range(item_list.count())
            if item_list.item(index).data(Qt.ItemDataRole.UserRole)["item_name"]
            == "Coal"
        )
        item_list.setCurrentRow(coal_row)
        QApplication.processEvents()
        self.assertFalse(slots[0].isChecked())
        self.assertFalse(
            dialog.findChild(QPushButton, "geCancelOfferButton").isEnabled()
        )
        self.assertIn(
            "Select an occupied slot",
            dialog.findChild(QLabel, "geOrderDetailLabel").text(),
        )

        side = dialog.findChild(QComboBox, "geOfferSideCombo")
        side.setCurrentIndex(side.findData("sell"))
        QApplication.processEvents()
        self.assertEqual(item_list.count(), 1)
        self.assertEqual(
            item_list.item(0).data(Qt.ItemDataRole.UserRole)["item_name"],
            "Logs",
        )
        dialog.deleteLater()

    def test_grand_exchange_empty_sell_side_names_the_owned_item_state(self) -> None:
        from ankiscape.logic.grand_exchange_logic import ge_frontend_projection_pure

        player = _make_player_data()
        player["inventory"] = {"Coins": 1_000}
        catalog = {
            "Logs": {
                "guide_price": 100,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "logs",
            }
        }
        dialog = self._open(
            player,
            get_ge_projection=lambda: ge_frontend_projection_pure(
                player,
                item_catalog=catalog,
            ),
            on_ge_action=lambda _action_id, _payload: {"ok": False},
        )
        _open_ge_tab(dialog)

        side = dialog.findChild(QComboBox, "geOfferSideCombo")
        side.setCurrentIndex(side.findData("sell"))
        QApplication.processEvents()

        item_list = dialog.findChild(QListWidget, "geItemList")
        self.assertEqual(item_list.count(), 1)
        self.assertEqual(
            item_list.item(0).text(),
            "You own nothing exchangeable to sell.",
        )
        dialog.deleteLater()

    def test_grand_exchange_sell_all_and_bank_quantities_and_compounding_nudges(
        self,
    ) -> None:
        from ankiscape.logic.grand_exchange_logic import ge_frontend_projection_pure

        player = _make_player_data()
        player["inventory"] = {"Coins": 10_000, "Logs": 137}
        catalog = {
            "Logs": {
                "guide_price": 100,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "logs",
            },
            "Coal": {
                "guide_price": 200,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "ore",
            },
        }
        dialog = self._open(
            player,
            get_ge_projection=lambda: ge_frontend_projection_pure(
                player,
                item_catalog=catalog,
            ),
            on_ge_action=lambda _action_id, _payload: {"ok": True},
        )
        _open_ge_tab(dialog)

        item_list = dialog.findChild(QListWidget, "geItemList")
        texts = _list_texts(item_list)
        # The Bank tab's bare x{n} token, and nothing at all for unowned rows.
        self.assertTrue(any(text.endswith("·  x137") for text in texts))
        self.assertFalse(any("x0" in text for text in texts))

        sell_all = dialog.findChild(QPushButton, "geSellAllButton")
        quantity = dialog.findChild(QSpinBox, "geOfferQuantitySpin")
        price = dialog.findChild(QSpinBox, "geOfferPriceSpin")
        # isHidden rather than isVisible: the test dialog is never shown.
        self.assertTrue(sell_all.isHidden())

        side = dialog.findChild(QComboBox, "geOfferSideCombo")
        side.setCurrentIndex(side.findData("sell"))
        QApplication.processEvents()
        self.assertFalse(sell_all.isHidden())

        logs_row = next(
            index
            for index in range(item_list.count())
            if item_list.item(index).data(Qt.ItemDataRole.UserRole)["item_name"]
            == "Logs"
        )
        item_list.setCurrentRow(logs_row)
        QApplication.processEvents()
        self.assertEqual(quantity.value(), 1)
        sell_all.click()
        self.assertEqual(quantity.value(), 137)
        self.assertIn(
            "Bank: 137",
            dialog.findChild(QLabel, "geSelectedItemMeta").text(),
        )

        # Regression: the nudges used to recompute from the guide price, so a
        # second click never moved the price.
        plus = dialog.findChild(QPushButton, "gePricePlus5Button")
        self.assertEqual(price.value(), 100)
        plus.click()
        self.assertEqual(price.value(), 105)
        plus.click()
        self.assertEqual(price.value(), 110)
        dialog.findChild(QPushButton, "geGuidePriceButton").click()
        self.assertEqual(price.value(), 100)

        # At a few gp the percentage truncates to no movement, so the period
        # script's forced one-coin step is what keeps the button live.
        price.setValue(1)
        plus.click()
        self.assertEqual(price.value(), 2)
        minus = dialog.findChild(QPushButton, "gePriceMinus5Button")
        minus.click()
        self.assertEqual(price.value(), 1)
        minus.click()
        self.assertEqual(price.value(), 1)

        # Truncation toward zero, not round-to-nearest. These two prices are
        # where the distinction shows: round-half-up gives 35 and 20. The
        # arithmetic is client script 4112, recovered by disassembly — see
        # memory-bank/source-audits/ge-offer-price-controls-2026-07-24.md.
        price.setValue(33)
        plus.click()
        self.assertEqual(price.value(), 34)
        price.setValue(21)
        minus.click()
        self.assertEqual(price.value(), 19)

        # The up-button saturates past the period overflow boundary rather than
        # wrapping. The spin box ceiling is the same 32-bit maximum.
        price.setValue(2_045_222_521)
        plus.click()
        self.assertEqual(price.value(), 2_147_483_647)
        dialog.deleteLater()

    def test_grand_exchange_tab_no_longer_carries_the_fill_log_drawer(self) -> None:
        """The drawer moved under the reviewer experience bars.

        Design-thread section 4.8: "I wanted it to be under the xp bar box. It
        should be a drawer." Its rows, ordering and two tones are pinned against
        their new home in tests/test_review_strip.py; what matters here is that
        the tab does not keep a second copy reporting the same log.
        """
        from ankiscape.logic.grand_exchange_logic import ge_frontend_projection_pure

        player = _make_player_data()
        player["inventory"] = {"Coins": 10_000}
        player["shop_market_clock"] = {"answered_cards": 12, "market_tick": 12}
        player["ge_fill_log"] = [
            {
                "card": 10,
                "side": "sell",
                "item_name": "Logs",
                "completed_quantity": 3,
                "original_quantity": 10,
            },
        ]
        catalog = {
            "Logs": {
                "guide_price": 100,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "logs",
            }
        }
        dialog = self._open(
            player,
            get_ge_projection=lambda: ge_frontend_projection_pure(
                player,
                item_catalog=catalog,
            ),
            on_ge_action=lambda _action_id, _payload: {"ok": True},
        )
        _open_ge_tab(dialog)

        self.assertIsNone(dialog.findChild(QToolButton, "geFillLogToggle"))
        self.assertIsNone(dialog.findChild(QListWidget, "geFillLogList"))
        # The projection still carries the log, because the reviewer drawer and
        # any future surface read the same ordered rows.
        self.assertTrue(
            ge_frontend_projection_pure(player, item_catalog=catalog)["fill_log"]
        )
        dialog.deleteLater()

    def test_settings_toggle_deirons_permanently_and_unlocks_ge(self) -> None:
        from ankiscape.logic.grand_exchange_logic import (
            apply_ge_frontend_action_pure,
            choose_ironman_mode_pure,
            ge_frontend_projection_pure,
        )

        starting_player = _make_player_data()
        starting_player["ironman_account_type"] = "unselected"
        player, chosen = choose_ironman_mode_pure(starting_player, True)
        self.assertTrue(chosen["ok"])
        player["inventory"] = {"Coins": 1_000}
        catalog = {
            "Logs": {
                "guide_price": 100,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "logs",
            }
        }
        calls = []

        def projection():
            return ge_frontend_projection_pure(player, item_catalog=catalog)

        def action(action_id, payload):
            calls.append((action_id, dict(payload)))
            updated, info = apply_ge_frontend_action_pure(
                player,
                action_id,
                payload,
                item_catalog=catalog,
            )
            if info.get("ok"):
                player.clear()
                player.update(updated)
            return {**info, "projection": projection()}

        dialog = self._open(
            player,
            get_ge_projection=projection,
            on_ge_action=action,
        )
        _open_ge_tab(dialog)
        self.assertIsNone(dialog.findChild(QCheckBox, "geIronmanToggle"))
        self.assertFalse(dialog.findChild(QListWidget, "geItemList").isEnabled())

        toggle = dialog.findChild(QCheckBox, "settingsIronmanToggle")
        self.assertTrue(toggle.isChecked())
        original_question = self._ui.QMessageBox.question
        try:
            self._ui.QMessageBox.question = (
                lambda *a, **k: self._ui.QMessageBox.StandardButton.Yes
            )
            toggle.setChecked(False)
            QApplication.processEvents()
        finally:
            self._ui.QMessageBox.question = original_question

        self.assertEqual(calls[-1], ("set_ironman", {"enabled": False}))
        self.assertFalse(player["ironman_mode"])
        self.assertEqual(player["ironman_account_type"], "regular")
        self.assertFalse(toggle.isEnabled())
        self.assertTrue(dialog.findChild(QListWidget, "geItemList").isEnabled())
        self.assertIn(
            "never become Ironman",
            dialog.findChild(QLabel, "settingsIronmanHelp").text(),
        )
        dialog.deleteLater()

    def test_first_ge_open_records_regular_choice_permanently(self) -> None:
        from ankiscape.logic.grand_exchange_logic import (
            apply_ge_frontend_action_pure,
            ge_frontend_projection_pure,
        )

        player = _make_player_data()
        player["ironman_account_type"] = "unselected"
        catalog = {}
        calls = []

        def projection():
            return ge_frontend_projection_pure(player, item_catalog=catalog)

        def action(action_id, payload):
            calls.append((action_id, dict(payload)))
            updated, info = apply_ge_frontend_action_pure(
                player, action_id, payload, item_catalog=catalog
            )
            if info.get("ok"):
                player.clear()
                player.update(updated)
            return {**info, "projection": projection()}

        dialog = self._open(
            player,
            get_ge_projection=projection,
            on_ge_action=action,
        )
        original_exec = self._ui.QMessageBox.exec
        try:
            def choose_regular(prompt):
                prompt.button(QMessageBox.StandardButton.No).click()
                return prompt.result()

            self._ui.QMessageBox.exec = choose_regular
            _open_ge_tab(dialog)
        finally:
            self._ui.QMessageBox.exec = original_exec

        self.assertEqual(calls, [("choose_ironman", {"enabled": False})])
        self.assertEqual(player["ironman_account_type"], "regular")
        tabs = _find_main_tabs(dialog)
        tabs.setCurrentIndex(
            next(i for i in range(tabs.count()) if tabs.tabText(i) == "Settings")
        )
        QApplication.processEvents()
        self.assertFalse(
            dialog.findChild(QCheckBox, "settingsIronmanToggle").isEnabled()
        )
        self.assertIn(
            "never become Ironman",
            dialog.findChild(QLabel, "settingsIronmanHelp").text(),
        )
        dialog.deleteLater()

    def test_first_ge_open_defers_without_recording_on_cancel_escape_or_close(self) -> None:
        from ankiscape.logic.grand_exchange_logic import ge_frontend_projection_pure

        for exit_route in ("button", "escape", "close"):
            with self.subTest(exit_route=exit_route):
                player = _make_player_data()
                player["ironman_account_type"] = "unselected"
                calls = []
                prompt_count = 0

                def projection():
                    return ge_frontend_projection_pure(player, item_catalog={})

                def action(action_id, payload):
                    calls.append((action_id, dict(payload)))
                    return {"ok": True, "projection": projection()}

                dialog = self._open(
                    player,
                    get_ge_projection=projection,
                    on_ge_action=action,
                )
                dialog.show()
                dialog.resize(900, 560)
                for _ in range(4):
                    QApplication.processEvents()

                original_exec = self._ui.QMessageBox.exec
                original_question = self._ui.QMessageBox.question
                try:
                    def defer_choice(prompt):
                        nonlocal prompt_count
                        prompt_count += 1
                        prompt.show()
                        prompt.resize(420, 220)
                        for _ in range(4):
                            QApplication.processEvents()
                        decide_later = prompt.button(QMessageBox.StandardButton.Cancel)
                        self.assertEqual(decide_later.text(), "Decide later")
                        self.assertIs(prompt.escapeButton(), decide_later)
                        if exit_route == "button":
                            decide_later.click()
                        elif exit_route == "escape":
                            QTest.keyClick(prompt, Qt.Key.Key_Escape)
                        else:
                            prompt.close()
                        for _ in range(4):
                            QApplication.processEvents()
                        return prompt.result()

                    self._ui.QMessageBox.exec = defer_choice
                    self._ui.QMessageBox.question = (
                        lambda *args, **kwargs: QMessageBox.StandardButton.No
                    )
                    _open_ge_tab(dialog)
                    self.assertEqual(calls, [])
                    self.assertEqual(player["ironman_account_type"], "unselected")
                    self.assertNotEqual(
                        _find_main_tabs(dialog).tabText(
                            _find_main_tabs(dialog).currentIndex()
                        ),
                        "Grand Exchange",
                    )
                    _open_ge_tab(dialog)
                finally:
                    self._ui.QMessageBox.exec = original_exec
                    self._ui.QMessageBox.question = original_question

                self.assertEqual(prompt_count, 2)
                self.assertEqual(calls, [])
                self.assertEqual(player["ironman_account_type"], "unselected")
                dialog.deleteLater()

    def test_bank_opens_the_shared_grand_exchange(self) -> None:
        player = _make_player_data()
        dialog = self._open(player)
        _open_bank_tab(dialog)
        tabs = _find_main_tabs(dialog)
        original_question = self._ui.QMessageBox.question
        try:
            self._ui.QMessageBox.question = (
                lambda *a, **k: self._ui.QMessageBox.StandardButton.No
            )
            dialog.findChild(QPushButton, "bankGrandExchangeButton").click()
            QApplication.processEvents()
        finally:
            self._ui.QMessageBox.question = original_question

        self.assertEqual(tabs.tabText(tabs.currentIndex()), "Grand Exchange")
        self.assertEqual(
            sum(
                1
                for index in range(tabs.count())
                if tabs.tabText(index) == "Grand Exchange"
            ),
            1,
        )
        dialog.deleteLater()
