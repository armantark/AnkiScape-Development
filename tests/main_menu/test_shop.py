from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_main_tabs,
    _find_named_button,
    _find_named_label,
    _find_named_line_edit,
    _find_named_list,
    _list_texts,
    _make_player_data,
    _open_achievements_tab,
    _open_first_shop,
    _open_shop_tab,
    copy,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QPushButton, QScrollArea, QTabWidget, QToolButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_shop_tab_renders_and_keeps_hidden_reward_shops_out_of_browse_and_search(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        hidden_name = fixtures["hidden_reward_shop"]["display_name"]
        dialog = self._open(fixtures["fixture_player_data"])
        _open_shop_tab(dialog)

        selector = _find_named_list(dialog, "shopSelectionList")
        self.assertTrue(selector.count(), "shop selector did not render visible shops")
        self.assertFalse(any(hidden_name in text for text in _list_texts(selector)))

        search = _find_named_line_edit(dialog, "shopSearchInput")
        search.setText("Stardust")
        QApplication.processEvents()
        self.assertFalse(any(hidden_name in text for text in _list_texts(selector)))
        self.assertIn("No visible shop", selector.item(0).text())

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn("Services", labels)

    def test_shop_opens_browse_first_and_detail_is_collapsible(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures
        from ankiscape.logic.shop_logic import shop_view_model_pure

        fixtures = build_shop_frontend_fixtures()
        player_data = fixtures["fixture_player_data"]
        dialog = self._open(player_data)
        _open_shop_tab(dialog)

        shell = dialog.findChild(QWidget, "shopDetailShell")
        selector = _find_named_list(dialog, "shopSelectionList")
        title = _find_named_label(dialog, "shopDetailTitle")

        # No default shop: the detail panel stays closed until a shop is clicked.
        self.assertIsNotNone(shell)
        self.assertFalse(shell.isVisibleTo(dialog))
        self.assertIsNone(selector.currentItem())

        _open_first_shop(dialog)
        first_payload = selector.item(0).data(Qt.ItemDataRole.UserRole)
        self.assertEqual(first_payload.get("kind"), "shop")
        opened_view = shop_view_model_pure(player_data, first_payload["shop_id"])
        self.assertTrue(shell.isVisibleTo(dialog))
        self.assertEqual(title.text(), opened_view["display_name"])
        buy_button = _find_named_button(dialog, "shopTransactionButton")
        self.assertTrue(buy_button.isEnabled(), _find_named_label(dialog, "shopPreviewLabel").text())

        # Shops never advertise the global services; those belong to providers.
        services_panel = dialog.findChild(QWidget, "shopServicesPanel")
        self.assertIsNotNone(services_panel)
        self.assertFalse(services_panel.isVisibleTo(dialog))

        # The collapse control returns the space to the shop list.
        collapse = next(
            button for button in dialog.findChildren(QToolButton)
            if button.objectName() == "shopDetailCollapseButton"
        )
        collapse.click()
        QApplication.processEvents()
        self.assertFalse(shell.isVisibleTo(dialog))
        self.assertIsNone(selector.currentItem())

    def test_shop_stock_tooltips_show_player_requirements_without_source_metadata(self) -> None:
        dialog = self._open(_make_player_data())
        _open_shop_tab(dialog)
        selector = _find_named_list(dialog, "shopSelectionList")
        white_knight_shop = next(
            selector.item(index)
            for index in range(selector.count())
            if (selector.item(index).data(Qt.ItemDataRole.UserRole) or {}).get("shop_id")
            == "white_knight_armory"
        )
        selector.setCurrentItem(white_knight_shop)
        QApplication.processEvents()

        scimitar = next(
            button
            for button in dialog.findChildren(QToolButton)
            if button.objectName().startswith("shopStockTile_")
            and button.text() == "White scimitar"
        )
        tooltip = scimitar.toolTip()
        self.assertIn("Equip: level 10 Attack", tooltip)
        self.assertNotIn("Darkan Shop.java", tooltip)
        self.assertNotIn("Darkan shop JSON", tooltip)
        self.assertNotIn("source", tooltip.casefold())

        dialog.deleteLater()

    def test_shop_browse_splits_normal_and_reward_targets_left_to_right(self) -> None:
        pd = _make_player_data()
        dialog = self._open(pd)
        dialog.show()
        dialog.resize(900, 560)
        _open_shop_tab(dialog)
        for _ in range(3):
            QApplication.processEvents()

        normal = _find_named_list(dialog, "shopSelectionList")
        rewards = _find_named_list(dialog, "rewardShopTargetList")
        normal_x = normal.mapTo(dialog, normal.rect().topLeft()).x()
        rewards_x = rewards.mapTo(dialog, rewards.rect().topLeft()).x()
        self.assertLess(normal_x, rewards_x)

        expected = {
            "Brimhaven tickets · Pirate Jackie the Fruit",
            "Advanced courses · the Agile worker",
            "Skillcapes · the skill masters",
            "Agility Pyramid · Simon Templeton",
            "Big Chinchompa rewards",
            "Fist of Guthix · Reggie",
            "Penguin Hide and Seek rewards",
            "Vinesweeper · Mrs Winkin",
            "Flash Powder Factory",
            "Fish Flingers reward shop",
            "Great Orb Project · Wizard Elriss",
            "Trouble Brewing rewards",
            "Castle Wars ticket shop",
            "Pest Control rewards",
            "Soul Wars rewards",
            "Barbarian Assault rewards",
            "Stealing Creation reward tools",
            "Dungeoneering rewards trader",
            "The Crucible · Trophy bones",
            "Troll Invasion reward books",
            "Mobilising Armies · Officer Tower",
            "Mage Training Arena rewards",
        }
        self.assertEqual(set(_list_texts(rewards)), expected)
        self.assertFalse(any("_" in text for text in _list_texts(rewards)))

    def test_skillcape_shop_consumes_the_pure_visibility_gate(self) -> None:
        pd = _make_player_data()
        pd["mining_level"] = 33
        pd["inventory"]["Coins"] = 500_000
        dialog = self._open(pd)
        dialog.show()
        _open_shop_tab(dialog)
        rewards = _find_named_list(dialog, "rewardShopTargetList")
        target = next(
            rewards.item(index)
            for index in range(rewards.count())
            if rewards.item(index).data(Qt.ItemDataRole.UserRole).get("target_id")
            == "skill_masters"
        )
        rewards.setCurrentItem(target)
        QApplication.processEvents()
        reward_page = dialog.findChild(QWidget, "shopAgilityRewardsPanel")
        from ankiscape.logic.cape_logic import cape_view_pure

        hidden_skill_ids = {
            row["cape_id"]
            for row in cape_view_pure(pd)["skillcapes"]
            if not row["show_in_shop"]
        }
        visible_skill_buttons = [
            button
            for button in reward_page.findChildren(QPushButton)
            if button.objectName().removeprefix("shopCapeButton_")
            in hidden_skill_ids
        ]
        self.assertEqual(visible_skill_buttons, [])
        dialog.close()

    def test_reward_targets_open_only_their_interface_beside_inventory(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Coins": 123_456, "Agility arena ticket": 10}
        dialog = self._open(pd, current_skill="Agility")
        dialog.show()
        dialog.resize(900, 560)
        _open_shop_tab(dialog)
        for _ in range(3):
            QApplication.processEvents()

        rewards = _find_named_list(dialog, "rewardShopTargetList")

        def select(target_id: str) -> None:
            item = next(
                rewards.item(index)
                for index in range(rewards.count())
                if (
                    isinstance(
                        rewards.item(index).data(Qt.ItemDataRole.UserRole), dict
                    )
                    and rewards.item(index).data(Qt.ItemDataRole.UserRole).get(
                        "target_id"
                    )
                    == target_id
                )
            )
            rewards.setCurrentItem(item)
            QApplication.processEvents()

        select("brimhaven_tickets")
        panel = dialog.findChild(QWidget, "rewardShopTargetPanel")
        inventory = _find_named_list(dialog, "rewardShopInventoryList")
        self.assertTrue(panel.isVisibleTo(dialog))
        self.assertTrue(
            dialog.findChild(QLabel, "shopBrimhavenSectionLabel").isVisibleTo(dialog)
        )
        self.assertFalse(
            dialog.findChild(QLabel, "shopAgileSectionLabel").isVisibleTo(dialog)
        )
        self.assertFalse(
            dialog.findChild(QLabel, "shopAgilityCapeSectionLabel").isVisibleTo(dialog)
        )
        self.assertFalse(
            dialog.findChild(QLabel, "shopNamedBuyersSectionLabel").isVisibleTo(dialog)
        )
        self.assertTrue(any("Coins x123,456" == text for text in _list_texts(inventory)))

        select("fish_flingers")
        fish_page = dialog.findChild(QWidget, "rewardShopPage_fish_flingers")
        fish_shop = dialog.findChild(QWidget, "fishFlingersRewardShop")
        self.assertTrue(fish_page.isVisibleTo(dialog))
        self.assertTrue(fish_shop.isVisibleTo(dialog))
        self.assertFalse(
            dialog.findChild(QWidget, "shopAgilityRewardsPanel").isVisibleTo(dialog)
        )

        wallet_labels = {
            "brimhaven_tickets": "shopBrimhavenSectionLabelBalance",
            "agile_worker": "shopAgileSectionLabelBalance",
            "skill_masters": "shopAgilityCapeSectionLabelBalance",
            "simon_templeton": "shopNamedBuyersSectionLabelBalance",
            "big_chinchompa": "bigChinchompaRewardWallet",
            "fist_of_guthix": "fistOfGuthixRewardWallet",
            "penguin_hide_and_seek": "penguinRewardWallet",
            "vinesweeper": "vinesweeperRewardWallet",
            "flash_powder_factory": "flashPowderFactoryPoints",
            "fish_flingers": "fishFlingersCurrencyChip",
            "great_orb_project": "greatOrbProjectCurrencyLabel",
            "trouble_brewing": "troubleBrewingWallet",
            "castle_wars": "castleWarsShopWallet",
            "pest_control": "pestControlRewardWallet",
            "soul_wars": "soulWarsRewardWallet",
            "barbarian_assault": "barbarianAssaultRewardWallet",
            "stealing_creation": "stealingCreationRewardWallet",
            "dungeoneering": "dungeoneeringTokenSummary",
            "crucible": "crucibleRewardWallet",
            "troll_invasion": "trollInvasionRewardWallet",
            "mobilising_armies": "mobilisingArmiesShopWallet",
            "mage_training_arena": "mageTrainingArenaShopWallet",
        }
        for target_id, object_name in wallet_labels.items():
            select(target_id)
            wallet = dialog.findChild(QLabel, object_name)
            self.assertIsNotNone(wallet, target_id)
            self.assertTrue(wallet.isVisibleTo(dialog), target_id)
            self.assertTrue(wallet.text().strip(), target_id)

        lower_scroll = dialog.findChild(QScrollArea, "shopLowerScroll")
        reward_scroll = dialog.findChild(QScrollArea, "rewardShopInterfaceScroll")
        self.assertFalse(lower_scroll.isVisibleTo(dialog))
        self.assertGreaterEqual(reward_scroll.viewport().height(), 150)
        self.assertEqual(reward_scroll.horizontalScrollBar().maximum(), 0)
        dialog.resize(760, 520)
        select("big_chinchompa")
        for _ in range(3):
            QApplication.processEvents()
        self.assertEqual(reward_scroll.horizontalScrollBar().maximum(), 0)

        _open_first_shop(dialog)
        self.assertFalse(panel.isVisibleTo(dialog))

    def test_reward_controls_have_one_owner_and_move_out_of_activities(self) -> None:
        dialog = self._open(_make_player_data())
        self._open_activities(dialog)
        fish_shops = dialog.findChildren(QWidget, "fishFlingersRewardShop")
        self.assertEqual(len(fish_shops), 1)
        live_shop = fish_shops[0]
        self.assertEqual(live_shop.parentWidget().objectName(), "rewardShopStagingHost")
        self.assertFalse(live_shop.isVisibleTo(dialog))

        _open_shop_tab(dialog)
        QApplication.processEvents()

        shop_page = dialog.findChild(QWidget, "rewardShopPage_fish_flingers")
        self.assertIsNotNone(shop_page)
        self.assertIs(shop_page.findChild(QWidget, "fishFlingersRewardShop"), live_shop)
        self.assertEqual(
            len(dialog.findChildren(QWidget, "fishFlingersRewardShop")), 1
        )

    def test_returning_to_shop_refreshes_rehomed_reward_controls(self) -> None:
        from ankiscape.logic.big_chinchompa_logic import (
            default_big_chinchompa_state_pure,
        )

        pd = _make_player_data()
        pd["hunter_level"] = 99
        pd["big_chinchompa"] = default_big_chinchompa_state_pure()
        pd["big_chinchompa"]["competence_points"] = 5
        dialog = self._open(pd)
        _open_shop_tab(dialog)
        rewards = _find_named_list(dialog, "rewardShopTargetList")
        target = next(
            rewards.item(index)
            for index in range(rewards.count())
            if rewards.item(index).data(Qt.ItemDataRole.UserRole).get("target_id")
            == "big_chinchompa"
        )
        rewards.setCurrentItem(target)
        QApplication.processEvents()
        buy = next(
            button
            for button in dialog.findChildren(QPushButton, "bigChinchompaRewardBuyButton")
            if button.isVisibleTo(dialog)
        )
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["big_chinchompa"]["competence_points"], 1)
        self.assertFalse(buy.isEnabled())
        self.assertIn("you have 1", buy.toolTip())

        tabs = _find_main_tabs(dialog)
        skills_index = next(
            index for index in range(tabs.count()) if tabs.tabText(index) == "Skills"
        )
        shop_index = next(
            index for index in range(tabs.count()) if tabs.tabText(index) == "Shop"
        )
        tabs.setCurrentIndex(skills_index)
        QApplication.processEvents()
        visible_activity_buys = [
            button
            for button in dialog.findChildren(
                QPushButton, "bigChinchompaRewardBuyButton"
            )
            if button.isVisibleTo(dialog)
        ]
        self.assertEqual(visible_activity_buys, [])
        tabs.setCurrentIndex(shop_index)
        QApplication.processEvents()

        self.assertFalse(buy.isEnabled())
        self.assertIn("you have 1", buy.toolTip())

    def test_shop_preview_uses_current_player_currency_state(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        pd = fixtures["fixture_player_data"]
        pd["inventory"]["Coins"] = 0
        dialog = self._open(pd)
        _open_shop_tab(dialog)
        _open_first_shop(dialog)

        meta = _find_named_label(dialog, "shopDetailMeta")
        preview = _find_named_label(dialog, "shopPreviewLabel")
        buy_button = _find_named_button(dialog, "shopTransactionButton")

        self.assertIn("Coins: 0 owned", meta.text())
        self.assertIn("Need", preview.text())
        self.assertIn("you have 0", preview.text())
        self.assertFalse(buy_button.isEnabled())

    def test_shop_locked_currency_search_names_backend_reason_and_cannot_be_selected(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        locked_view = fixtures["locked_read_only_shop"]
        locked_row = locked_view["rows"][0]
        dialog = self._open(fixtures["fixture_player_data"])
        _open_shop_tab(dialog)

        search = _find_named_line_edit(dialog, "shopSearchInput")
        search.setText(locked_row["item_name"])
        QApplication.processEvents()
        selector = _find_named_list(dialog, "shopSelectionList")
        locked_item = None
        for index in range(selector.count()):
            item = selector.item(index)
            payload = item.data(Qt.ItemDataRole.UserRole)
            if (
                isinstance(payload, dict)
                and payload.get("kind") == "stock"
                and payload.get("shop_id") == locked_view["shop_id"]
                and payload.get("row_id") == locked_row["id"]
            ):
                locked_item = item
                break
        self.assertIsNotNone(locked_item, "locked search did not render stock-source comparison rows")
        self.assertIn("Currency not implemented", locked_item.text())
        self.assertNotIn("currency_not_implemented", locked_item.text())
        self.assertFalse(locked_item.flags() & Qt.ItemFlag.ItemIsEnabled)
        selector.itemClicked.emit(locked_item)
        QApplication.processEvents()

        self.assertEqual(_find_named_label(dialog, "shopPreviewLabel").text(), "No stock row selected.")
        self.assertFalse(_find_named_button(dialog, "shopTransactionButton").isEnabled())

    def test_shop_live_stock_buy_updates_inventory_and_history(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        pd = fixtures["fixture_player_data"]
        live_view = fixtures["normal_coin_stock_shop"]
        live_row = next(row for row in live_view["rows"] if row["can_buy"])
        saved = []
        achievement_checks = []
        dialog = self._open(
            pd,
            on_check_achievements=lambda data: achievement_checks.append(copy.deepcopy(data["inventory"])),
            on_save_player_data=lambda: saved.append(copy.deepcopy(pd)),
        )
        _open_shop_tab(dialog)

        search = _find_named_line_edit(dialog, "shopSearchInput")
        search.setText(live_row["item_name"])
        QApplication.processEvents()
        selector = _find_named_list(dialog, "shopSelectionList")
        target = None
        for index in range(selector.count()):
            item = selector.item(index)
            payload = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(payload, dict) and payload.get("shop_id") == live_view["shop_id"] and payload.get("row_id") == live_row["id"]:
                target = item
                break
        self.assertIsNotNone(target, "live stock row was not selectable from item search")
        selector.setCurrentItem(target)
        QApplication.processEvents()

        before_item = pd["inventory"].get(live_row["item_name"], 0)
        before_coins = pd["inventory"]["Coins"]
        button = _find_named_button(dialog, "shopTransactionButton")
        self.assertTrue(button.isEnabled(), _find_named_label(dialog, "shopPreviewLabel").text())
        button.click()
        QApplication.processEvents()

        self.assertEqual(pd["inventory"].get(live_row["item_name"], 0), before_item + 1)
        self.assertEqual(pd["inventory"]["Coins"], before_coins - int(live_row["buy_price"]))
        history_texts = _list_texts(_find_named_list(dialog, "shopLocalHistoryList"))
        self.assertTrue(any(text.startswith("Bought 1 x") for text in history_texts), history_texts)
        self.assertEqual(len(saved), 1)
        self.assertEqual(achievement_checks, [pd["inventory"]])
        self.assertEqual(saved[0]["inventory"], pd["inventory"])
        self.assertEqual(saved[0]["shop_events"], pd["shop_events"])

    def test_shop_tzhaar_onyx_row_uses_tokkul_wallet_and_live_purchase(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

        pd = build_shop_frontend_fixtures()["fixture_player_data"]
        pd["inventory"].update({"Tokkul": 2_700_000, "Uncut onyx": 0})
        dialog = self._open(pd)
        _open_shop_tab(dialog)

        search = _find_named_line_edit(dialog, "shopSearchInput")
        search.setText("Uncut onyx")
        QApplication.processEvents()
        selector = _find_named_list(dialog, "shopSelectionList")
        target = next(
            selector.item(index)
            for index in range(selector.count())
            if isinstance(selector.item(index).data(Qt.ItemDataRole.UserRole), dict)
            and selector.item(index).data(Qt.ItemDataRole.UserRole).get("shop_id")
            == "tzhaarhurleks_ore_and_gem_store"
            and selector.item(index).data(Qt.ItemDataRole.UserRole).get("row_id")
            == "tzhaarhurleks_ore_and_gem_store:5:6571"
        )
        selector.setCurrentItem(target)
        QApplication.processEvents()

        self.assertIn("Tokkul: 2,700,000 owned", _find_named_label(dialog, "shopDetailMeta").text())
        button = _find_named_button(dialog, "shopTransactionButton")
        self.assertTrue(button.isEnabled(), _find_named_label(dialog, "shopPreviewLabel").text())
        button.click()
        QApplication.processEvents()

        self.assertEqual(pd["inventory"]["Tokkul"], 0)
        self.assertEqual(pd["inventory"]["Uncut onyx"], 1)

    def test_shop_general_store_sell_creates_temporary_stock(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        pd = fixtures["fixture_player_data"]
        general_shop_id = fixtures["player_sold_stock"]["shop_id"]
        dialog = self._open(pd)
        _open_shop_tab(dialog)

        selector = _find_named_list(dialog, "shopSelectionList")
        general_item = None
        for index in range(selector.count()):
            item = selector.item(index)
            payload = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(payload, dict) and payload.get("shop_id") == general_shop_id:
                general_item = item
                break
        self.assertIsNotNone(general_item, "visible general store was not present in browsing")
        selector.setCurrentItem(general_item)
        QApplication.processEvents()

        mode_tabs = dialog.findChild(QTabWidget, "shopModeTabs")
        self.assertIsNotNone(mode_tabs)
        mode_tabs.setCurrentIndex(1)
        QApplication.processEvents()
        sell_list = _find_named_list(dialog, "shopSellInventoryList")
        beer_item = next(
            sell_list.item(i)
            for i in range(sell_list.count())
            if sell_list.item(i).data(Qt.ItemDataRole.UserRole) == "Beer"
        )
        sell_list.setCurrentItem(beer_item)
        QApplication.processEvents()
        before_beer = pd["inventory"]["Beer"]
        before_coins = pd["inventory"]["Coins"]
        button = _find_named_button(dialog, "shopTransactionButton")
        self.assertTrue(button.isEnabled(), _find_named_label(dialog, "shopPreviewLabel").text())
        button.click()
        QApplication.processEvents()

        self.assertEqual(pd["inventory"]["Beer"], before_beer - 1)
        self.assertGreater(pd["inventory"]["Coins"], before_coins)
        mode_tabs.setCurrentIndex(0)
        QApplication.processEvents()
        stock_buttons = [
            button for button in dialog.findChildren(QToolButton)
            if button.property("shopRowId") and "Beer" in button.text()
        ]
        self.assertTrue(stock_buttons, "player-sold Beer did not appear as temporary shop stock")

    def test_all_skillcape_purchases_live_in_the_shop_target(self) -> None:
        from ankiscape.logic.achievement_diary_logic import (
            apply_achievement_diary_command_pure,
        )

        pd = _make_player_data()
        pd["mining_level"] = 99
        pd["inventory"] = {"Coins": 99_000}

        def diary_command(action_id, payload):
            updated, ok, info = apply_achievement_diary_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, **info}

        dialog = self._open(
            pd,
            current_skill="Mining",
            on_achievement_diary_command=diary_command,
        )
        dialog.show()
        _open_shop_tab(dialog)
        QApplication.processEvents()
        rewards = _find_named_list(dialog, "rewardShopTargetList")
        skillcapes = next(
            rewards.item(index)
            for index in range(rewards.count())
            if rewards.item(index).data(Qt.ItemDataRole.UserRole).get("target_id")
            == "skill_masters"
        )
        rewards.setCurrentItem(skillcapes)
        QApplication.processEvents()

        buy = _find_named_button(dialog, "shopCapeButton_mining")
        self.assertTrue(buy.isVisibleTo(dialog))
        self.assertTrue(buy.isEnabled())

        _open_achievements_tab(dialog)
        cabinet_purchase_buttons = [
            button
            for button in dialog.findChildren(QPushButton)
            if button.objectName().startswith("cabinetCapeBuy_")
        ]
        self.assertEqual(cabinet_purchase_buttons, [])
        _open_shop_tab(dialog)
        rewards = _find_named_list(dialog, "rewardShopTargetList")
        skillcapes = next(
            rewards.item(index)
            for index in range(rewards.count())
            if rewards.item(index).data(Qt.ItemDataRole.UserRole).get("target_id")
            == "skill_masters"
        )
        rewards.setCurrentItem(skillcapes)
        QApplication.processEvents()
        buy = _find_named_button(dialog, "shopCapeButton_mining")

        buy.click()
        QApplication.processEvents()

        self.assertEqual(pd["inventory"]["Mining cape"], 1)
        self.assertEqual(pd["inventory"]["Mining hood"], 1)
        self.assertEqual(pd["inventory"].get("Coins", 0), 0)
