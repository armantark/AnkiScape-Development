from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    SimpleNamespace,
    _ADDON_DIR,
    _find_main_tabs,
    _find_named_list,
    _goto_crafting,
    _goto_smithing,
    _icon_pixels,
    _list_texts,
    _make_player_data,
    _open_achievements_tab,
    _open_collections_tab,
    _open_quests_tab,
    _open_shop_tab,
    _panel_title,
    os,
    re,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QIcon, QLabel, QMainWindow, QPushButton, QTabWidget, QTreeWidget, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_initial_panel_shows_a_gathering_skill(self) -> None:
        title = _panel_title(self.dialog)
        self.assertTrue(title.startswith("Mining"), f"unexpected initial panel: {title!r}")

    def test_skill_availability_refresh_disables_crafting_with_reason(self) -> None:
        player_data = _make_player_data()
        player_data["inventory"] = {"Wool": 1}
        dialog = self._open(player_data, current_skill="Mining")
        dialog.show()
        QApplication.processEvents()
        _goto_crafting(dialog)
        train_button = next(
            button
            for button in dialog.findChildren(QPushButton)
            if button.text() == "Train this skill" and button.isVisible()
        )

        self.assertTrue(train_button.isEnabled())

        self._ui.refresh_skill_availability(
            True, False, True, True, True, True, True
        )
        QApplication.processEvents()

        self.assertFalse(train_button.isEnabled())
        self.assertEqual(
            train_button.toolTip(),
            "Gather materials or level up to craft an item.",
        )

    def test_skill_availability_refresh_keeps_current_training_disabled(self) -> None:
        dialog = self._open(
            {**_make_player_data(), "inventory": {"Wool": 5}},
            current_skill="Crafting",
        )
        dialog.show()
        QApplication.processEvents()
        _goto_crafting(dialog)
        train_button = next(
            button
            for button in dialog.findChildren(QPushButton)
            if button.text() == "Currently training" and button.isVisible()
        )

        self.assertFalse(train_button.isEnabled())
        self.assertEqual(train_button.toolTip(), "")
        self._ui.refresh_skill_availability(
            True, True, True, True, True, True, True
        )
        QApplication.processEvents()

        self.assertFalse(train_button.isEnabled())
        self.assertEqual(train_button.toolTip(), "")

    def test_smithing_availability_recomputes_on_panel_rerender(self) -> None:
        player_data = _make_player_data()
        player_data["inventory"] = {"Copper ore": 1, "Tin ore": 1}
        dialog = self._open(player_data, current_skill="Mining")
        dialog.show()
        QApplication.processEvents()
        _goto_smithing(dialog)
        train_button = next(
            button
            for button in dialog.findChildren(QPushButton)
            if button.text() == "Train this skill" and button.isVisible()
        )
        self.assertTrue(train_button.isEnabled())

        player_data["inventory"].clear()
        _goto_crafting(dialog)
        _goto_smithing(dialog)
        rerendered_button = next(
            button
            for button in dialog.findChildren(QPushButton)
            if button.text() == "Train this skill" and button.isVisible()
        )

        self.assertFalse(rerendered_button.isEnabled())
        self.assertEqual(
            rerendered_button.toolTip(),
            "Mine ores until you can smelt a bar.",
        )

    def test_global_tabs_use_unique_semantic_icons(self) -> None:
        tabs = _find_main_tabs(self.dialog)
        expected = {
            "Skills": "skills_icon.png",
            "Shop": "shop_icon.png",
            "Grand Exchange": "grand_exchange_icon.png",
            "Quests": "quest_icon.png",
            "Bank": "bank_icon.png",
            "Equipment": "equipment_icon.png",
            "Stats": "stats_icon.png",
            "Challenges": "challenges_icon.png",
            "Achievements": "achievement_icon.png",
            "Collections": "dnd_icon.png",
            "Settings": "settings_icon.png",
        }
        rendered = {}
        for index in range(tabs.count()):
            label = tabs.tabText(index)
            icon = tabs.tabIcon(index)
            self.assertFalse(icon.isNull(), f"{label} has no tab icon")
            self.assertEqual(
                _icon_pixels(icon),
                _icon_pixels(
                    QIcon(os.path.join(_ADDON_DIR, "icon", expected[label]))
                ),
            )
            rendered[label] = _icon_pixels(icon)
        self.assertEqual(len(set(rendered.values())), len(expected))

    def test_global_tabs_follow_the_owner_settled_pass8_order(self) -> None:
        tabs = _find_main_tabs(self.dialog)
        self.assertEqual(
            [tabs.tabText(index) for index in range(tabs.count())],
            [
                "Skills",
                "Stats",
                "Bank",
                "Equipment",
                "Shop",
                "Grand Exchange",
                "Challenges",
                "Quests",
                "Achievements",
                "Collections",
                "Settings",
            ],
        )

    def test_slayer_is_management_only_and_exposes_three_live_tabs(self) -> None:
        dialog = self._open(_make_player_data())
        self._goto_slayer(dialog)

        self.assertEqual(_panel_title(dialog), "Slayer — Lv 33")
        self.assertFalse(
            any(
                button.isVisible()
                and button.text() in {"Train this skill", "Currently training"}
                for button in dialog.findChildren(QPushButton)
            )
        )
        tabs = dialog.findChild(QTabWidget, "slayerManagementTabs")
        self.assertIsNotNone(tabs)
        self.assertEqual(
            [tabs.tabText(index) for index in range(tabs.count())],
            ["Assignment", "Masters", "Rewards"],
        )
        self.assertIsNotNone(dialog.findChild(QLabel, "slayerAssignmentEmptyState"))

        tabs.setCurrentIndex(2)
        QApplication.processEvents()
        lock = dialog.findChild(QLabel, "slayerRewardsSmokingKillsLock")
        self.assertIsNotNone(lock)
        self.assertIn("Complete Smoking Kills", lock.text())

        # The master gets a chathead so the player can tell who is speaking.
        tabs.setCurrentIndex(1)
        QApplication.processEvents()
        card = dialog.findChild(QWidget, "slayerMaster_turael_spria")
        chathead = card.findChild(QLabel, "slayerMasterChathead")
        self.assertIsNotNone(chathead.pixmap())
        self.assertFalse(chathead.pixmap().isNull())

    def test_main_menu_dialog_is_deleted_when_closed(self) -> None:
        self.assertTrue(
            self.dialog.testAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        )

    def test_profile_reload_replaces_the_existing_menu_and_callback(self) -> None:
        original_mw = self._ui.mw
        window = QMainWindow()
        window.form = SimpleNamespace(menubar=window.menuBar())
        calls = []
        try:
            self._ui.mw = window
            self._ui.create_menu(lambda: calls.append("first"))
            menu = self._ui.create_menu(lambda: calls.append("second"))

            self.assertEqual(
                [action.text() for action in window.menuBar().actions()],
                ["AnkiScape"],
            )
            menu.actions()[0].trigger()
            self.assertEqual(calls, ["second"])
        finally:
            self._ui.mw = original_mw
            window.deleteLater()

    def test_achievement_tab_renders_the_cabinet_not_the_fabricated_list(self) -> None:
        """The tab is the Achievement Cabinet now.

        It used to render 168 fabricated skill-progression rows in four invented
        difficulty buckets, under a completion percentage whose denominator moved
        whenever an achievement was added — the figure the semantics contract
        forbids diary gear from consuming. This asserts the replacement: real
        regional families, real tier rewards, and no percentage anywhere.
        """
        pd = _make_player_data()
        pd["completed_achievements"] = ["First Steps", "Rune Mysteries"]
        dialog = self._open(pd)
        _open_achievements_tab(dialog)
        labels = [label.text() for label in dialog.findChildren(QLabel)]

        self.assertIn("Achievement Cabinet", labels)
        self.assertTrue(
            any(text.startswith("Varrock") for text in labels),
            "the Cabinet did not render its regional families",
        )
        self.assertTrue(
            any("Varrock armour 1" in text for text in labels),
            "the Easy Varrock tier did not name the item it hands over",
        )
        self.assertTrue(
            any(re.fullmatch(r"\d+/\d+ tasks", text) for text in labels),
            "the Cabinet did not show its fixed-denominator task total",
        )
        self.assertFalse(
            [text for text in labels if "%" in text and "Completed:" in text],
            "a moving-denominator completion percentage is back on the tab",
        )
        self.assertNotIn(
            "First Steps",
            labels,
            "a fabricated achievement row is still rendered",
        )

    def test_expensive_tabs_are_unbuilt_until_shown(self) -> None:
        """Regression guard for the deferred build: opening the menu must not
        construct the Shop, Quests, Achievements or Collections pages, while the
        tab that is actually visible (Skills) is fully rendered."""
        dialog = self._open(_make_player_data())
        tabs = _find_main_tabs(dialog)
        for label in ("Shop", "Quests", "Achievements", "Collections"):
            index = next(i for i in range(tabs.count()) if tabs.tabText(i) == label)
            page = tabs.widget(index)
            self.assertEqual(
                len(page.findChildren(QLabel)),
                0,
                f"{label} tab was built before it was shown",
            )
        self.assertTrue(_panel_title(dialog).startswith("Mining"))

    def test_refresh_of_unbuilt_tab_is_a_noop_and_later_build_shows_live_state(self) -> None:
        """A cross-tab refresh aimed at a tab nobody opened must not raise, and
        the state written in the meantime must appear once the tab is built."""
        pd = _make_player_data()
        pd["quest_points"] = 0
        dialog = self._open(pd)
        ctx = dialog._ankiscape_menu_ctx

        pd["quest_points"] = 7
        ctx.refresh("quests")
        ctx.refresh("shop")
        ctx.refresh("no_such_surface")

        _open_quests_tab(dialog)
        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn("Quest points: 7", labels)
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))

        _open_shop_tab(dialog)
        self.assertTrue(_list_texts(_find_named_list(dialog, "shopSelectionList")))

        # Both surfaces register their refresher once built, so a later refresh
        # reaches them instead of being dropped.
        self.assertIn("quests", ctx.refreshers)
        self.assertIn("shop", ctx.refreshers)
        ctx.refresh("quests")
        ctx.refresh("shop")
        QApplication.processEvents()
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))

    def test_collections_deferred_page_builds_both_settled_families(self) -> None:
        dialog = self._open(_make_player_data())
        dialog.resize(1280, 752)
        dialog.show()

        _open_collections_tab(dialog)
        for _ in range(3):
            QApplication.processEvents()

        navigation = dialog.findChild(QTreeWidget, "collectionsFamilyTree")
        detail = dialog.findChild(QWidget, "collectionsDetailPanel")
        self.assertIsNotNone(navigation)
        self.assertIsNotNone(detail)
        self.assertGreater(detail.width(), navigation.width())
        self.assertGreater(detail.x(), navigation.x())
        self.assertEqual(navigation.topLevelItemCount(), 2)
        self.assertEqual(navigation.topLevelItem(0).text(0), "Music Log")
        self.assertEqual(
            navigation.topLevelItem(1).text(0),
            "Boss/monster drop log",
        )
        navigation.setCurrentItem(navigation.topLevelItem(1))
        QApplication.processEvents()
        self.assertIsNotNone(
            dialog.findChild(QTreeWidget, "collectionsDropTargets")
        )
        self.assertRegex(
            dialog.findChild(QLabel, "collectionsGlobalTotals").text(),
            r"^Collected \d+ / \d+ overall$",
        )

    def test_stop_training_uses_the_dedicated_direct_action_callback(self) -> None:
        pd = _make_player_data()
        pd["current_utility"] = "gather_flax"
        stop_calls = []

        def stop_training():
            stop_calls.append(True)
            pd["current_utility"] = "bankstanding"
            return "Utilities"

        dialog = self._open(
            pd,
            current_skill="Mining",
            on_stop_training=stop_training,
        )
        next(
            button
            for button in dialog.findChildren(QPushButton)
            if button.text() == "Stop training"
        ).click()
        QApplication.processEvents()

        self.assertEqual(stop_calls, [True])
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(self._activity_start_calls, [])
