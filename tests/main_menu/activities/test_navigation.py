from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _FakeCol,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _open_reward_target,
    _tree_items,
    _utility_row,
    re,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QAbstractItemView, QApplication, QCheckBox, QComboBox, QLabel, QMenu, QPushButton, QStackedWidget, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_mobilising_armies_keeps_activity_controls_and_shows_spoils_in_shop(self) -> None:
        from ankiscape.logic.mobilising_armies_logic import (
            apply_mobilising_armies_command_pure,
            default_mobilising_armies_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_mobilising_armies_state_pure())
        pd["mobilising_armies_rank"] = 400
        pd["mobilising_armies_reward_credits"] = 10_000_000

        def command(action_id, payload):
            updated, ok, info = apply_mobilising_armies_command_pure(
                pd, action_id, payload, rng=lambda: 0.25
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(pd, on_mobilising_armies_command=command)
        dialog.show()
        activity_tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(activity_tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "mobilising_armies"
        )
        activity_tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "mobilisingArmiesPanel")
            if widget.isVisible()
        )
        wallet = panel.findChild(QLabel, "mobilisingArmiesRewardWallet")
        floor = panel.findChild(QComboBox, "mobilisingArmiesFloorCombo")
        prefix = panel.findChild(QComboBox, "mobilisingArmiesPrefixCombo")
        self.assertTrue(wallet.isVisibleTo(dialog))
        self.assertTrue(floor.isVisibleTo(dialog))
        self.assertTrue(prefix.isVisibleTo(dialog))
        second_floor = floor.findData("second")
        self.assertGreaterEqual(second_floor, 0)
        floor.setCurrentIndex(second_floor)

        reward_page = _open_reward_target(dialog, "mobilising_armies")
        shop_floor = reward_page.findChild(
            QComboBox, "mobilisingArmiesShopFloorCombo"
        )
        spoils = reward_page.findChild(QLabel, "mobilisingArmiesSpoilsOffer")
        view_spoils = reward_page.findChild(
            QPushButton, "mobilisingArmiesViewSpoilsButton"
        )
        self.assertEqual(shop_floor.currentData(), "second")
        self.assertEqual(spoils.text(), "No Spoils of War stall is laid out.")
        self.assertIsNone(
            reward_page.findChild(QPushButton, "mobilisingArmiesPrefixButton")
        )
        view_spoils.click()
        QApplication.processEvents()
        self.assertNotEqual(spoils.text(), "No Spoils of War stall is laid out.")
        self.assertTrue(spoils.isVisibleTo(dialog))
        dialog.close()

    def test_familiarisation_lives_in_activities_and_runs_its_session(self) -> None:
        from ankiscape.logic.summoning_logic import (
            default_summoning_state_pure,
            start_familiarisation_pure,
        )

        pd = _make_player_data()
        pd["current_utility"] = "bankstanding"
        pd["summoning_state"] = default_summoning_state_pure()
        calls = []

        def command(action_id, payload):
            calls.append((action_id, dict(payload)))
            if action_id != "start_familiarisation":
                return {"ok": False}
            updated, ok = start_familiarisation_pure(pd)
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_summoning_command=command,
        )
        dialog.show()
        tree = self._open_activities(dialog)
        row = _utility_row(tree, "familiarisation")
        tree.setCurrentItem(row)
        tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "familiarisationPanel")
        start = _find_named_button(
            dialog, "summoningStartFamiliarisationButton"
        )
        self.assertTrue(panel.isVisible())
        self.assertEqual(pd["current_utility"], "bankstanding")

        start.click()
        QApplication.processEvents()
        self.assertEqual(calls, [("start_familiarisation", {})])
        self.assertTrue(
            pd["summoning_state"]["familiarisation"]["active"]
        )
        self.assertEqual(
            "0/4 segments · 0/60 shards",
            _find_named_label(dialog, "familiarisationSummary").text(),
        )
        dialog.deleteLater()

    def test_main_menu_owns_the_simulated_world_time(self) -> None:
        pd = _make_player_data()
        pd["shop_market_clock"] = {"answered_cards": 10, "market_tick": 10}
        dialog = self._open(pd)

        clock = _find_named_label(dialog, "mainMenuSimulatedClock")
        self.assertEqual(clock.text(), "World time: 1:00 PM")
        self.assertEqual(clock.toolTip(), "Each answered card moves the world clock by 3.6 seconds times your game speed.\nOne world hour: 1,000 cards at 1x, 100 at 10x, 50 at 20x. The rest of the day passes at once when the world day ends.")

    def test_activity_and_dnd_entries_are_alphabetical(self) -> None:
        tree = self._open_activities(self.dialog)

        selection = _find_named_widget(self.dialog, "skillListWidget")
        for label in ("Minigames", "Distractions and Diversions"):
            row = next(
                selection.item(index)
                for index in range(selection.count())
                if selection.item(index).text() == label
            )
            selection.setCurrentItem(row)
            QApplication.processEvents()
            labels = [
                tree.topLevelItem(index).text(0)
                for index in range(tree.topLevelItemCount())
                if not tree.topLevelItem(index).isHidden()
            ]
            self.assertEqual(labels, sorted(labels, key=str.casefold), label)

    def test_activity_families_are_icon_rows_in_the_selection_column(self) -> None:
        tree = self._open_activities(self.dialog)
        selection = _find_named_widget(self.dialog, "skillListWidget")
        self.assertEqual(
            [selection.item(index).text() for index in range(selection.count())],
            ["Activities", "Minigames", "Distractions and Diversions"],
        )
        for index in range(selection.count()):
            self.assertFalse(selection.item(index).icon().isNull())
        dnd_row_width = (
            selection.fontMetrics().horizontalAdvance(
                "Distractions and Diversions"
            )
            + selection.iconSize().width()
            + 24
        )
        self.assertGreaterEqual(selection.viewport().width(), dnd_row_width)
        self.assertGreaterEqual(selection.parentWidget().maximumWidth(), 240)

        visible_master_ids = {
            tree.topLevelItem(index).data(0, Qt.ItemDataRole.UserRole)
            for index in range(tree.topLevelItemCount())
            if not tree.topLevelItem(index).isHidden()
        }
        self.assertIn("__utility_group__:warriors_guild", visible_master_ids)
        self.assertIn("__utility_group__:landmarks", visible_master_ids)
        self.assertNotIn("__utility_group__:minigames", visible_master_ids)
        self.assertNotIn(
            "__utility_group__:distractions_and_diversions",
            visible_master_ids,
        )

        minigames = selection.item(1)
        selection.setCurrentItem(minigames)
        QApplication.processEvents()
        visible_minigame_ids = {
            tree.topLevelItem(index).data(0, Qt.ItemDataRole.UserRole)
            for index in range(tree.topLevelItemCount())
            if not tree.topLevelItem(index).isHidden()
        }
        self.assertIn("fist_of_guthix", visible_minigame_ids)
        self.assertNotIn("__utility_group__:minigames", visible_minigame_ids)
        self.assertNotIn("shooting_stars", visible_minigame_ids)

        dnds = selection.item(2)
        selection.setCurrentItem(dnds)
        QApplication.processEvents()
        visible_dnd_ids = {
            tree.topLevelItem(index).data(0, Qt.ItemDataRole.UserRole)
            for index in range(tree.topLevelItemCount())
            if not tree.topLevelItem(index).isHidden()
        }
        self.assertIn("shooting_stars", visible_dnd_ids)
        self.assertNotIn(
            "__utility_group__:distractions_and_diversions",
            visible_dnd_ids,
        )
        self.assertNotIn("fist_of_guthix", visible_dnd_ids)

    def test_activities_panel_describes_rewards_and_no_xp_rows_truthfully(self) -> None:
        utility_tree = self._open_activities(self.dialog)
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertIn(
            "Activities contain D&Ds, minigames, and landmarks. Each row states its rewards.",
            labels,
        )
        livid_row = _utility_row(utility_tree, "livid_farm")
        self.assertIn(
            "exactly six cycles per five successful reviews",
            livid_row.toolTip(0),
        )
        selected_colors = re.findall(
            r"QTreeWidget::(?:item|branch):selected \{ background: (#[0-9a-f]{6});",
            utility_tree.styleSheet(),
        )
        self.assertEqual(len(selected_colors), 2)
        self.assertEqual(selected_colors[0], selected_colors[1])

    def test_bankstanding_describes_an_idle_no_op_without_fake_output(self) -> None:
        pd = _make_player_data()
        pd["current_utility"] = "bankstanding"
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)

        row = _utility_row(utility_tree, "bankstanding")
        self.assertIn("Nothing is produced or consumed", row.toolTip(0))
        self.assertNotIn("Output: Bankstanding", row.toolTip(0))

        hud = self._ui.ReviewHUD(None)
        hud.set_data(pd, "Utility / Activities")
        self.assertIn("idle at the Bank", hud.sub_lbl.text())
        self.assertNotIn("material prep", hud.sub_lbl.text())

    def test_activities_world_events_strip_hidden_when_no_event(self) -> None:
        dialog = self._open(_make_player_data())
        self._open_activities(dialog)

        strip = _find_named_widget(dialog, "activityWorldEventsStrip")
        self.assertFalse(strip.isVisibleTo(dialog))

    def test_activity_tree_context_menu_adds_and_removes_every_distraction(self) -> None:
        from ankiscape.data.evil_tree_data import EVIL_TREE_UTILITY_ID
        from ankiscape.logic.dnd_favourites_logic import (
            DND_ACTIVITY_IDS,
            toggle_dnd_favourite_pure,
        )

        pd = _make_player_data()

        def _favourite(activity_id):
            updated, ok, info = toggle_dnd_favourite_pure(pd, activity_id)
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, **info}

        dialog = self._open(pd, on_favourite_dnd=_favourite)
        activity_tree = self._open_activities(dialog)
        dialog.show()
        dialog.resize(1000, 560)
        for _ in range(8):
            QApplication.processEvents()
        selection = _find_named_widget(dialog, "skillListWidget")
        selection.setCurrentItem(selection.item(2))
        for _ in range(4):
            QApplication.processEvents()

        captured_menus: list[QMenu] = []
        original_menu_exec = QMenu.exec

        def _capture_menu(menu, *_args):
            captured_menus.append(menu)
            return None

        def _open_row_menu(activity_id: str) -> QMenu | None:
            row = _utility_row(activity_tree, activity_id)
            if row.isHidden():
                return None
            activity_tree.scrollToItem(
                row, QAbstractItemView.ScrollHint.PositionAtCenter
            )
            for _ in range(4):
                QApplication.processEvents()
            before = len(captured_menus)
            activity_tree.customContextMenuRequested.emit(
                activity_tree.visualItemRect(row).center()
            )
            for _ in range(4):
                QApplication.processEvents()
            return captured_menus[-1] if len(captured_menus) > before else None

        QMenu.exec = _capture_menu  # type: ignore[assignment,method-assign]
        try:
            for activity_id in sorted(DND_ACTIVITY_IDS):
                with self.subTest(activity=activity_id):
                    menu = _open_row_menu(activity_id)
                    self.assertIsNotNone(menu)
                    action = menu.actions()[0]
                    self.assertEqual(action.text(), "Add to notifications")
                    self.assertTrue(action.isEnabled())
                    action.trigger()
                    for _ in range(2):
                        QApplication.processEvents()
                    self.assertEqual(pd["dnd_favourites"], [activity_id])

                    menu = _open_row_menu(activity_id)
                    self.assertIsNotNone(menu)
                    action = menu.actions()[0]
                    self.assertEqual(action.text(), "Remove from notifications")
                    action.trigger()
                    for _ in range(2):
                        QApplication.processEvents()
                    self.assertEqual(pd["dnd_favourites"], [])

            self.assertIsNone(_open_row_menu("castle_wars"))

            evil_row = _utility_row(activity_tree, EVIL_TREE_UTILITY_ID)
            self.assertFalse(evil_row.icon(0).isNull())
            activity_tree.itemClicked.emit(evil_row, 0)
            for _ in range(4):
                QApplication.processEvents()
            self.assertFalse(
                _find_named_widget(dialog, "evilTreePanel").isHidden()
            )
            self.assertTrue(
                _find_named_widget(dialog, "activityFavouriteButton").isVisible()
            )
        finally:
            QMenu.exec = original_menu_exec  # type: ignore[assignment,method-assign]
            dialog.deleteLater()

    def test_a_distraction_surface_carries_the_reviewer_badge_pin(self) -> None:
        """Section 4.8: "There is no way to add a d&d to favorites."

        The pin sits on the Activities detail card's shared control row, so one
        widget serves all forty-odd surfaces including the five that ship as
        their own panel class.
        """
        from ankiscape.data.shooting_star_data import SHOOTING_STAR_ACTIVITY_ID
        from ankiscape.logic.dnd_favourites_logic import toggle_dnd_favourite_pure

        pd = _make_player_data()
        pd["current_utility"] = SHOOTING_STAR_ACTIVITY_ID
        pinned: list = []

        def _favourite(activity_id):
            updated, ok, info = toggle_dnd_favourite_pure(pd, activity_id)
            if ok:
                pd.update(updated)
                pinned.append(activity_id)
            return {"ok": ok, **info}

        dialog = self._open(pd, on_favourite_dnd=_favourite)
        self._open_activity_detail(dialog, SHOOTING_STAR_ACTIVITY_ID)
        dialog.resize(1000, 560)
        dialog.show()
        for _ in range(8):
            QApplication.processEvents()

        pin = _find_named_widget(dialog, "activityFavouriteButton")
        self.assertTrue(pin.isVisible())
        self.assertTrue(pin.isEnabled())
        self.assertEqual(pin.text(), "\u2606")
        self.assertIn("badge", pin.toolTip().lower())

        pin.click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(pinned, [SHOOTING_STAR_ACTIVITY_ID])
        self.assertEqual(pd["dnd_favourites"], [SHOOTING_STAR_ACTIVITY_ID])
        self.assertEqual(pin.text(), "\u2605")

        pin.click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(pd["dnd_favourites"], [])
        self.assertEqual(pin.text(), "\u2606")

        # Back on the tree there is no activity to pin, and a minigame is not a
        # Distraction, so neither carries the control.
        _find_named_button(dialog, "activityChooseAnotherButton").click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertFalse(pin.isVisible())
        dialog.deleteLater()

    def test_the_pin_is_absent_on_an_activity_the_badge_cannot_watch(self) -> None:
        from ankiscape.data.castle_wars_data import CASTLE_WARS_ACTIVITY_ID

        pd = _make_player_data()
        pd["current_utility"] = CASTLE_WARS_ACTIVITY_ID
        dialog = self._open(pd, on_favourite_dnd=lambda _id: {"ok": True})
        self._open_activity_detail(dialog, CASTLE_WARS_ACTIVITY_ID)
        dialog.resize(1000, 560)
        dialog.show()
        for _ in range(8):
            QApplication.processEvents()

        self.assertFalse(
            _find_named_widget(dialog, "activityFavouriteButton").isVisible()
        )
        dialog.deleteLater()

    def test_activity_details_replace_the_activity_tree(self) -> None:
        from ankiscape.logic.big_chinchompa_logic import (
            advance_big_chinchompa_world_clock_pure,
            default_big_chinchompa_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "hunter_level": 99,
                "current_utility": "big_chinchompa",
                "shop_market_clock": {"answered_cards": 60},
                "big_chinchompa": default_big_chinchompa_state_pure(),
            }
        )
        pd, _ = advance_big_chinchompa_world_clock_pure(pd)
        dialog = self._open(pd)
        self._open_activity_detail(dialog, "big_chinchompa")
        dialog.resize(1000, 560)
        dialog.show()
        for _ in range(8):
            QApplication.processEvents()

        details_stack = _find_named_widget(
            dialog, "utilityActivityDetailsStack"
        )
        activity_tree = _find_named_widget(dialog, "utilityActivityTree")
        choose_another = _find_named_button(
            dialog, "activityChooseAnotherButton"
        )
        big_panel = _find_named_widget(dialog, "bigChinchompaPanel")
        self.assertIsInstance(details_stack, QStackedWidget)
        self.assertEqual(details_stack.currentWidget(), big_panel)
        self.assertTrue(details_stack.isVisible())
        self.assertTrue(choose_another.isVisible())
        self.assertFalse(activity_tree.isVisible())
        self.assertGreaterEqual(activity_tree.minimumHeight(), 140)
        surface_layout = activity_tree.parentWidget().layout()
        self.assertLess(
            surface_layout.indexOf(details_stack),
            surface_layout.indexOf(activity_tree),
        )
        visible_rows = [
            child
            for child in big_panel.findChildren(
                QWidget,
                options=Qt.FindChildOption.FindDirectChildrenOnly,
            )
            if child.isVisible()
        ]
        self.assertTrue(visible_rows)
        self.assertLessEqual(
            max(child.geometry().bottom() for child in visible_rows),
            big_panel.contentsRect().bottom(),
        )

        original_height = details_stack.height()
        big_detail = _find_named_label(dialog, "bigChinchompaDetail")
        big_detail.setMinimumHeight(big_detail.sizeHint().height() + 40)
        reward_combo = dialog.findChild(
            QComboBox, "bigChinchompaRewardCombo"
        )
        reward_combo.setCurrentIndex(1)
        QApplication.processEvents()
        self.assertGreater(details_stack.height(), original_height)

        choose_another.click()
        QApplication.processEvents()
        self.assertFalse(details_stack.isVisible())
        self.assertFalse(choose_another.isVisible())
        self.assertTrue(activity_tree.isVisible())

    def test_activity_picker_scrolls_and_remembers_collapsed_groups(self) -> None:
        # The picker used to page one category at a time with a fixed height,
        # which pushed long categories off-window. It now scrolls like every
        # other grouped tree in the hub and persists per-category collapses.
        from ankiscape.ui import ui

        class _FakeMw(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self.col = _FakeCol()

        orig_mw = ui.mw
        ui.mw = _FakeMw()
        try:
            pd = _make_player_data()
            pd["current_utility"] = "fist_of_guthix"
            dialog = self._open(pd)
            activity_tree = self._open_activities(dialog)
            dialog.show()
            dialog.resize(900, 560)
            for _ in range(8):
                QApplication.processEvents()

            _find_named_button(dialog, "activityChooseAnotherButton").click()
            for _ in range(8):
                QApplication.processEvents()

            selection = _find_named_widget(dialog, "skillListWidget")
            selection.setCurrentItem(selection.item(1))
            for _ in range(8):
                QApplication.processEvents()
            top_levels = [
                activity_tree.topLevelItem(index)
                for index in range(activity_tree.topLevelItemCount())
            ]
            visible_rows = [item for item in top_levels if not item.isHidden()]
            self.assertEqual(len(visible_rows), 30)

            # Scrolling, not a fixed height: the tree keeps Qt's default max
            # height and grows a scrollbar instead of the dialog.
            self.assertEqual(
                activity_tree.verticalScrollBarPolicy(),
                Qt.ScrollBarPolicy.ScrollBarAsNeeded,
            )
            self.assertGreater(
                activity_tree.maximumHeight(), activity_tree.minimumHeight()
            )
            self.assertGreater(
                activity_tree.verticalScrollBar().maximum(), 0
            )
            tree_bottom = activity_tree.mapTo(
                dialog, activity_tree.rect().bottomRight()
            ).y()
            self.assertLessEqual(tree_bottom, dialog.contentsRect().bottom())

            current = activity_tree.currentItem()
            self.assertEqual(
                current.data(0, Qt.ItemDataRole.UserRole), "fist_of_guthix"
            )
            self.assertTrue(
                activity_tree.viewport().rect().contains(
                    activity_tree.visualItemRect(current).center()
                )
            )

            selection.setCurrentItem(selection.item(0))
            for _ in range(4):
                QApplication.processEvents()
            by_group = {
                item.data(0, Qt.ItemDataRole.UserRole): item
                for item in top_levels
                if not item.isHidden()
            }
            for group in ("warriors_guild", "landmarks"):
                header = by_group[f"__utility_group__:{group}"]
                header.setExpanded(False)
                QApplication.processEvents()
                # The old pager re-expanded the visible category on collapse.
                self.assertFalse(header.isExpanded())
            self.assertEqual(
                ui.mw.col.get_config("ankiscape_activity_collapsed_groups"),
                ["landmarks", "warriors_guild"],
            )

            dialog2 = self._open(pd)
            tree2 = self._open_activities(dialog2)
            expanded = {
                item.data(0, Qt.ItemDataRole.UserRole): item.isExpanded()
                for item in (
                    tree2.topLevelItem(index)
                    for index in range(tree2.topLevelItemCount())
                )
            }
            self.assertFalse(expanded["__utility_group__:warriors_guild"])
            self.assertFalse(expanded["__utility_group__:landmarks"])
        finally:
            ui.mw = orig_mw

    def test_activities_header_hides_duplicate_start_without_affecting_utilities(self) -> None:
        dialog = self._open(_make_player_data(), current_skill="Mining")

        def visible_buttons():
            return {button.text() for button in dialog.findChildren(QPushButton) if button.isVisibleTo(dialog)}
        self._open_activities(dialog)
        self.assertNotIn("Start activity", visible_buttons())
        self._open_utility(dialog)
        self.assertIn("Start utility", visible_buttons())

    def test_activities_show_only_the_selected_rich_detail_card(self) -> None:
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "shooting_stars",
                "mining_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "shooting_star": default_shooting_star_state_pure(),
            }
        )
        active, _ = advance_shooting_star_world_clock_pure(pd)
        dialog = self._open(active)
        activity_tree = self._open_activities(dialog)
        dialog.show()
        QApplication.processEvents()

        star_panel = _find_named_widget(dialog, "shootingStarPanel")
        big_panel = _find_named_widget(dialog, "bigChinchompaPanel")
        evil_panel = _find_named_widget(dialog, "evilTreePanel")
        details_stack = _find_named_widget(dialog, "utilityActivityDetailsStack")
        self.assertTrue(details_stack.isHidden())
        self.assertTrue(activity_tree.isVisible())

        star_row = _utility_row(activity_tree, "shooting_stars")
        activity_tree.setCurrentItem(star_row)
        activity_tree.itemActivated.emit(star_row, 0)
        QApplication.processEvents()
        self.assertTrue(star_panel.isVisible())
        self.assertFalse(big_panel.isVisible())
        self.assertFalse(evil_panel.isVisible())

        big_row = _utility_row(activity_tree, "big_chinchompa")
        activity_tree.setCurrentItem(big_row)
        activity_tree.itemActivated.emit(big_row, 0)
        QApplication.processEvents()
        self.assertFalse(star_panel.isVisible())
        self.assertTrue(big_panel.isVisible())
        self.assertFalse(evil_panel.isVisible())

    def test_utility_rows_use_activity_icon_contract(self) -> None:
        utility_tree = self._open_utility(self.dialog)
        for row in _tree_items(utility_tree):
            role = row.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(role, str) and role.startswith("__utility_group__"):
                continue
            self.assertFalse(row.icon(0).isNull(), f"{row.text(0)} should have an activity icon")

    def test_source_gathering_rows_are_enabled_and_selectable_from_utility(self) -> None:
        # gather_wool stands in for the retired scavenge_chicken_feathers
        # bridge (feathers are live NPC shop stock now).
        utility_tree = self._open_utility(self.dialog)
        self._utility_calls.clear()
        for action_id, output_item in (
            ("gather_wool", "Wool"),
            ("gather_swamp_toads", "Swamp toad"),
            ("gather_blue_dragon_scales", "Blue dragon scale"),
            ("gather_potato_cacti", "Potato cactus"),
            ("gather_black_mushrooms", "Black mushroom"),
            ("gather_doogle_leaves", "Doogle leaves"),
            ("gather_goblin_mail", "Goblin mail"),
        ):
            with self.subTest(action_id=action_id):
                row = _utility_row(utility_tree, action_id)
                self.assertTrue(row.flags() & Qt.ItemFlag.ItemIsEnabled)
                self.assertFalse(row.icon(0).isNull())
                self.assertIn("No skill XP", row.toolTip(0))
                self.assertIn(f"Output: {output_item} x1", row.toolTip(0))
                self.assertIn("No materials required", row.toolTip(0))
                utility_tree.itemClicked.emit(row, 0)
                QApplication.processEvents()

        self.assertEqual(
            self._utility_calls,
            [
                "gather_wool",
                "gather_swamp_toads",
                "gather_blue_dragon_scales",
                "gather_potato_cacti",
                "gather_black_mushrooms",
                "gather_doogle_leaves",
                "gather_goblin_mail",
            ],
        )

    def test_pick_rows_name_their_place_on_hover(self) -> None:
        utility_tree = self._open_utility(self.dialog)
        for action_id, place in (
            ("pick_cabbages", "north of Lumbridge"),
            ("pick_potatoes", "north of the Lumbridge chicken farm"),
            ("pick_onions", "Fred the Farmer's yard"),
            ("pick_redberries", "south-east of Varrock"),
            ("pick_cadava_berries", "west of the East Varrock Mine"),
            ("pick_bananas", "Musa Point"),
            ("pick_pineapples", "Brimhaven Dungeon entrance"),
        ):
            with self.subTest(action_id=action_id):
                row = _utility_row(utility_tree, action_id)
                self.assertTrue(row.flags() & Qt.ItemFlag.ItemIsEnabled)
                self.assertFalse(row.icon(0).isNull())
                self.assertIn(place, row.toolTip(0))
                self.assertIn("No skill XP", row.toolTip(0))

    def test_goblin_diplomacy_processing_rows_use_the_existing_utility_contract(self) -> None:
        utility_tree = self._open_utility(self._open(_make_player_data() | {"inventory": {"Redberries": 3, "Coins": 5}}))
        expected = {
            "aggie_make_red_dye": ("Ask Aggie to make red dye", "Redberries x3", "Coins x5", "Red dye x1"),
            "aggie_make_yellow_dye": ("Ask Aggie to make yellow dye", "Onion x2", "Coins x5", "Yellow dye x1"),
            "mix_orange_dye": ("Mix orange dye", "Red dye x1", "Yellow dye x1", "Orange dye x1"),
            "aggie_make_blue_dye": ("Ask Aggie to make blue dye", "Woad leaf x2", "Coins x5", "Blue dye x1"),
            "dye_goblin_mail_orange": ("Dye goblin mail orange", "Goblin mail x1", "Orange dye x1", "Orange goblin mail x1"),
            "dye_goblin_mail_blue": ("Dye goblin mail blue", "Goblin mail x1", "Blue dye x1", "Blue goblin mail x1"),
        }
        for action_id, (label, first_input, second_input, output) in expected.items():
            with self.subTest(action_id=action_id):
                row = _utility_row(utility_tree, action_id)
                self.assertFalse(row.icon(0).isNull())
                self.assertIn(label, row.text(0))
                self.assertNotIn("…", row.text(0))
                self.assertNotIn("...", row.text(0))
                self.assertFalse([text for text in (first_input, second_input, f"Output: {output}", "No skill XP") if text not in row.toolTip(0)])
        funded_row = _utility_row(utility_tree, "aggie_make_red_dye")
        utility_tree.itemClicked.emit(funded_row, 0)
        QApplication.processEvents()
        self.assertEqual(self._utility_calls, ["aggie_make_red_dye"])

    def test_knight_waves_and_mage_arena_rows_start_activities(self) -> None:
        knight = _make_player_data()
        knight["quests"]["kings_ransom"] = {"completed": True}
        knight.update({"defense_level": 65, "magic_level": 60})
        knight_tree = self._open_activities(self._open(knight))
        knight_tree.itemClicked.emit(_utility_row(knight_tree, "knight_waves"), 0)
        QApplication.processEvents()
        self.assertEqual(self._activity_start_calls[-1], "knight_waves")
        self.assertEqual(knight["current_utility"], "knight_waves")

        mage = _make_player_data()
        mage["magic_level"] = 60
        mage_tree = self._open_activities(self._open(mage))
        mage_tree.itemClicked.emit(_utility_row(mage_tree, "mage_arena"), 0)
        QApplication.processEvents()
        self.assertEqual(self._activity_start_calls[-1], "mage_arena")
        self.assertEqual(mage["current_utility"], "mage_arena")

    def test_mage_arena_alignment_and_attunement_rows_use_their_distinct_actions(self) -> None:
        pending = _make_player_data()
        pending["magic_level"] = 60
        pending["mage_arena"] = {
            "step": 4,
            "completed": False,
            "alignment": "",
            "attuned_spells": [],
        }
        pending_dialog = self._open(pending)
        pending_tree = self._open_activities(pending_dialog)
        alignment = _utility_row(
            pending_tree,
            "__mage_alignment__:guthix",
        )
        pending_tree.itemClicked.emit(alignment, 0)
        QApplication.processEvents()
        self.assertEqual(
            self._mage_arena_calls[-1],
            ("select_alignment", "guthix"),
        )
        self.assertEqual(pending["mage_arena"]["alignment"], "guthix")
        self.assertEqual(self._activity_start_calls[-1], "mage_arena")
        self.assertEqual(pending["current_utility"], "mage_arena")

        completed = _make_player_data()
        completed["magic_level"] = 99
        completed["inventory"] = {"Guthix staff": 1}
        completed["mage_arena"] = {
            "step": 5,
            "completed": True,
            "alignment": "saradomin",
            "attuned_spells": ["saradomin_strike"],
        }
        completed_dialog = self._open(completed)
        completed_tree = self._open_activities(completed_dialog)
        attune = _utility_row(completed_tree, "mage_arena_attune:guthix")
        self.assertTrue(attune.flags() & Qt.ItemFlag.ItemIsEnabled)
        completed_tree.itemClicked.emit(attune, 0)
        QApplication.processEvents()
        self.assertEqual(
            self._activity_start_calls[-1], "mage_arena_attune:guthix"
        )
        self.assertEqual(
            completed["current_utility"], "mage_arena_attune:guthix"
        )

        switch = _utility_row(completed_tree, "__mage_cape__:guthix")
        completed_tree.itemClicked.emit(switch, 0)
        QApplication.processEvents()
        self.assertEqual(self._mage_arena_calls[-1], ("cape", "guthix"))
        self.assertEqual(completed["mage_arena"]["alignment"], "guthix")
        self.assertNotIn(
            "claws_of_guthix",
            completed["mage_arena"]["attuned_spells"],
        )

    def test_utility_region_quest_locks_are_inert(self) -> None:
        pd = _make_player_data()
        pd["current_utility"] = "gather_lean_snails"
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)

        snails = _utility_row(utility_tree, "gather_lean_snails")
        self.assertFalse(snails.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("Priest in Peril", snails.toolTip(0))

        before = list(self._utility_calls)
        utility_tree.itemClicked.emit(snails, 0)
        QApplication.processEvents()
        self.assertEqual(self._utility_calls, before, "quest-locked utility rows must not be selectable")

        pd["quests"]["priest_in_peril"] = {"started": True, "progress": 6, "completed": True}
        unlocked_dialog = self._open(pd)
        unlocked_tree = self._open_utility(unlocked_dialog)
        self.assertTrue(_utility_row(unlocked_tree, "gather_lean_snails").flags() & Qt.ItemFlag.ItemIsEnabled)

    def test_open_bird_nests_is_a_visible_no_xp_utility_activity(self) -> None:
        utility_tree = self._open_utility(self.dialog)
        texts = [it.text(0) for it in _tree_items(utility_tree)]
        self.assertIn("Open bird nests", texts)
        nest = _utility_row(utility_tree, "open_bird_nest")
        self.assertIn("No XP", nest.toolTip(0))
        self.assertIn("bird nest", nest.toolTip(0).lower())

    def test_crystal_chest_utility_row_is_visible_key_gated_and_selectable(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Crystal key": 1}
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)
        chest = _utility_row(utility_tree, "open_crystal_chest")

        self.assertFalse(chest.isDisabled())
        self.assertFalse(chest.icon(0).isNull())
        self.assertIn("Guaranteed: Uncut dragonstone x1", chest.toolTip(0))
        self.assertIn("Possible bonus", chest.toolTip(0))
        utility_tree.itemClicked.emit(chest, 0)
        QApplication.processEvents()
        self.assertEqual(self._utility_calls[-1], "open_crystal_chest")

    def test_chivalry_gate_copy_names_knight_waves(self) -> None:
        pd = _make_player_data()
        pd["prayer_level"] = 99
        pd["defense_level"] = 99
        pd["knight_waves"] = {"completed": False}
        dialog = self._open(pd)
        self.assertIsNone(dialog.findChild(QCheckBox, "combatPrayerCheck::chivalry"))
        locked = dialog.findChild(QLabel, "combatLockedPrayersLabel")
        self.assertIn("Chivalry (Lv 60, Def 65, Knight Waves)", locked.text())
