from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_main_tabs,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _find_stats_button,
    _make_player_data,
    _open_reward_target,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QColor, QComboBox, QLabel, QPalette, QProgressBar, QScrollArea, QToolButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_stats_tab_uses_period_three_column_grid_with_dungeoneering(self) -> None:
        stats_grid = self.dialog.findChild(QWidget, "statsSkillGrid")
        selector_scroll = self.dialog.findChild(QScrollArea, "statsSkillSelectorScroll")
        total_level = self.dialog.findChild(QLabel, "statsTotalLevel")
        self.assertIsNotNone(stats_grid)
        self.assertIsNotNone(selector_scroll)
        self.assertIsNotNone(total_level)
        self.assertEqual(selector_scroll.horizontalScrollBarPolicy(), Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        buttons = [
            button
            for button in stats_grid.findChildren(QToolButton)
            if button.objectName().startswith("statsSkillButton_")
        ]
        self.assertEqual(len(buttons), 25)
        positions = {
            button.accessibleName().split(",", 1)[0]: stats_grid.layout().getItemPosition(
                stats_grid.layout().indexOf(button)
            )[:2]
            for button in buttons
        }
        self.assertEqual(positions["Attack"], (0, 0))
        self.assertEqual(positions["Constitution"], (0, 1))
        self.assertEqual(positions["Mining"], (0, 2))
        self.assertEqual(positions["Summoning"], (7, 2))
        self.assertEqual(positions["Dungeoneering"], (8, 0))
        self.assertEqual(total_level.text(), "Total level: 569")

        dungeoneering = _find_stats_button(self.dialog, "dungeoneering")
        self.assertFalse(dungeoneering.icon().isNull())
        dungeoneering.click()
        QApplication.processEvents()
        labels = [label.text() for label in self.dialog.findChildren(QLabel)]
        self.assertIn("Dungeoneering Stats", labels)
        self.assertIn("Current / Base Level:", labels)
        progress_bar = self.dialog.findChild(QProgressBar, "statsSkillProgress")
        metrics = self.dialog.findChild(QWidget, "statsSkillMetrics")
        self.assertIsNotNone(progress_bar)
        self.assertIsNotNone(metrics)
        self.assertEqual(progress_bar.maximumWidth(), 320)
        self.assertEqual(metrics.maximumWidth(), 520)

    def test_dungeoneering_skill_surface_drives_entry_routing_and_abandon_at_laptop_height(self) -> None:
        from ankiscape.logic.dungeoneering_logic import (
            apply_dungeoneering_command_pure,
            default_dungeoneering_state_pure,
            record_dungeon_drop_pure,
        )

        original_palette = QApplication.palette()
        original_style = QApplication.style().objectName()
        dark = QPalette(original_palette)
        dark.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        dark.setColor(QPalette.ColorRole.WindowText, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        dark.setColor(QPalette.ColorRole.Text, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
        dark.setColor(QPalette.ColorRole.ButtonText, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Mid, QColor(95, 95, 95))
        QApplication.setStyle("Fusion")
        QApplication.setPalette(dark)
        dialog = None
        try:
            pd = _make_player_data()
            pd["dungeoneering_level"] = 11
            pd["dungeoneering_exp"] = 0.0
            pd["dungeoneering"] = default_dungeoneering_state_pure()
            calls = []

            def command(action_id, payload):
                calls.append((action_id, dict(payload)))
                updated, ok, info = apply_dungeoneering_command_pure(
                    pd,
                    action_id,
                    payload,
                )
                if ok:
                    pd.clear()
                    pd.update(updated)
                return {
                    "ok": ok,
                    "message": info.get("reason", info.get("message", "")),
                    **info,
                }

            dialog = self._open(
                pd,
                current_skill="Dungeoneering",
                initial_skill="Dungeoneering",
                on_dungeoneering_command=command,
            )
            dialog.show()
            for _ in range(4):
                QApplication.processEvents()

            panel = _find_named_widget(dialog, "dungeoneeringPanel")
            status = _find_named_label(dialog, "dungeoneeringStatusChip")
            summary = _find_named_label(dialog, "dungeoneeringSummary")
            projection = _find_named_label(dialog, "dungeoneeringProjection")
            economy = _find_named_label(dialog, "dungeoneeringEconomySummary")
            bind_summary = _find_named_label(dialog, "dungeoneeringBindSummary")
            automation = _find_named_label(dialog, "dungeoneeringAutomationSummary")
            token_summary = _find_named_label(dialog, "dungeoneeringTokenSummary")
            kinship_detail = _find_named_label(dialog, "dungeoneeringKinshipDetail")
            reward_detail = _find_named_label(dialog, "dungeoneeringRewardDetail")
            coal_bag_summary = _find_named_label(
                dialog,
                "dungeoneeringCoalBagSummary",
            )
            primary = _find_named_button(dialog, "dungeoneeringPrimaryButton")
            abandon = _find_named_button(dialog, "dungeoneeringAbandonButton")
            kinship_upgrade = _find_named_button(
                dialog,
                "dungeoneeringKinshipUpgradeButton",
            )
            reward_buy = _find_named_button(
                dialog,
                "dungeoneeringRewardBuyButton",
            )
            fill_bank = _find_named_button(
                dialog,
                "dungeoneeringCoalBagFillBankButton",
            )
            floor = panel.findChild(QComboBox, "dungeoneeringFloorCombo")
            size = _find_named_label(dialog, "dungeoneeringSizeLabel")
            complexity = panel.findChild(
                QComboBox,
                "dungeoneeringComplexityCombo",
            )
            mode = panel.findChild(QComboBox, "dungeoneeringModeCombo")
            resources = panel.findChild(
                QComboBox,
                "dungeoneeringResourcePolicyCombo",
            )
            bind_loadout = panel.findChild(
                QComboBox,
                "dungeoneeringBindLoadoutCombo",
            )
            kinship = panel.findChild(
                QComboBox,
                "dungeoneeringKinshipCombo",
            )
            kinship_row = _find_named_widget(
                dialog,
                "dungeoneeringKinshipRow",
            )
            rewards = dialog.findChild(
                QComboBox,
                "dungeoneeringRewardCombo",
            )
            reward_trader_row = _find_named_widget(
                dialog,
                "dungeoneeringRewardTraderRow",
            )
            coal_bag_row = _find_named_widget(
                dialog,
                "dungeoneeringCoalBagRow",
            )
            bind_config_row = _find_named_widget(
                dialog,
                "dungeoneeringBindConfigRow",
            )
            bind_item = panel.findChild(
                QComboBox,
                "dungeoneeringBindItemCombo",
            )
            bind_item_button = _find_named_button(
                dialog,
                "dungeoneeringBindItemButton",
            )
            route = panel.findChild(QComboBox, "dungeoneeringRouteCombo")
            smuggler = panel.findChild(QComboBox, "dungeoneeringSmugglerCombo")
            smuggler_row = _find_named_widget(dialog, "dungeoneeringSmugglerRow")
            bind_row = _find_named_widget(dialog, "dungeoneeringBindOfferRow")
            bind_item_action = _find_named_button(
                dialog,
                "dungeoneeringBindButton",
            )
            self.assertIsNone(panel.findChild(QScrollArea))
            self.assertEqual(status.text(), "READY")
            self.assertEqual(floor.count(), 6)
            self.assertEqual(size.text(), "Small")
            self.assertEqual(complexity.count(), 2)
            self.assertEqual(resources.count(), 3)
            self.assertEqual(bind_loadout.count(), 3)
            self.assertEqual(kinship.count(), 12)
            self.assertEqual(rewards.count(), 42)
            self.assertIn("balance", token_summary.text())
            self.assertIn("No automated-floor effect", kinship_detail.text())
            lamp_index = rewards.findData("dungeoneering_xp_lamp")
            rewards.setCurrentIndex(lamp_index)
            QApplication.processEvents()
            self.assertIn("not purchasable yet", rewards.currentText())
            self.assertIn("not purchasable yet", reward_detail.text())
            self.assertFalse(reward_buy.isEnabled())
            self.assertTrue(coal_bag_row.isHidden())

            pd["dungeoneering_level"] = 35
            pd["mining_level"] = 35
            pd["dungeoneering"]["tokens"] = 10_000
            pd["inventory"]["Coal"] = 30
            panel._ankiscape_refresh_dungeoneering()
            QApplication.processEvents()
            kinship.setCurrentIndex(kinship.findData("gatherer"))
            QApplication.processEvents()
            self.assertEqual(
                calls[-1],
                ("select_kinship_class", {"class_id": "gatherer"}),
            )
            self.assertIn("Buy tier 1", kinship_detail.text())
            self.assertEqual(kinship_upgrade.text(), "Upgrade to tier 1 · 135")
            self.assertTrue(kinship_upgrade.isEnabled())
            kinship_upgrade.click()
            QApplication.processEvents()
            self.assertEqual(calls[-1][0], "upgrade_kinship_class")
            self.assertEqual(
                pd["dungeoneering"]["kinship_tiers"]["gatherer"],
                1,
            )
            self.assertEqual(pd["dungeoneering"]["tokens"], 9_865)
            self.assertIn("Live at 20%", kinship_detail.text())

            rewards.setCurrentIndex(rewards.findData("coal_bag"))
            QApplication.processEvents()
            self.assertIn("4,000 tokens", rewards.currentText())
            self.assertIn("Dungeoneering 35, Mining 35", reward_detail.text())
            self.assertTrue(reward_buy.isEnabled())
            reward_buy.click()
            QApplication.processEvents()
            self.assertTrue(pd["dungeoneering"]["coal_bag_owned"])
            self.assertEqual(pd["dungeoneering"]["tokens"], 5_865)
            self.assertFalse(coal_bag_row.isHidden())
            self.assertEqual(coal_bag_summary.text(), "Coal bag · 0/27 Coal")
            self.assertTrue(fill_bank.isEnabled())
            fill_bank.click()
            QApplication.processEvents()
            self.assertEqual(pd["dungeoneering"]["coal_bag_coal"], 27)
            self.assertEqual(pd["inventory"]["Coal"], 3)
            self.assertEqual(coal_bag_summary.text(), "Coal bag · 27/27 Coal")
            self.assertIn("4,135 spent", token_summary.text())
            self.assertTrue(bind_loadout.isEnabled())
            self.assertTrue(abandon.isHidden())
            self.assertTrue(projection.isHidden())
            self.assertTrue(economy.isHidden())
            self.assertTrue(automation.isHidden())
            self.assertTrue(smuggler_row.isHidden())
            self.assertTrue(bind_row.isHidden())
            self.assertTrue(bind_config_row.isHidden())
            self.assertFalse(kinship_row.isHidden())
            self.assertFalse(reward_trader_row.isHidden())
            self.assertFalse(coal_bag_row.isHidden())
            self.assertLessEqual(
                panel.parentWidget().mapTo(dialog, panel.parentWidget().rect().bottomRight()).y(),
                dialog.contentsRect().bottom(),
            )

            floor.setCurrentIndex(floor.findData(6))
            complexity.setCurrentIndex(complexity.findData(6))
            mode.setCurrentIndex(mode.findData("advanced"))
            QApplication.processEvents()
            self.assertEqual(
                calls[-1],
                ("set_policy", {"automation_mode": "advanced"}),
            )
            resources.setCurrentIndex(resources.findData("gather_only"))
            QApplication.processEvents()
            self.assertEqual(
                calls[-1],
                ("set_resource_policy", {"resource_policy": "gather_only"}),
            )
            bind_loadout.setCurrentIndex(bind_loadout.findData(1))
            QApplication.processEvents()
            self.assertEqual(
                calls[-1],
                ("select_bind_loadout", {"loadout_index": 1}),
            )
            primary.click()
            QApplication.processEvents()
            self.assertEqual(calls[-1][0], "enter")
            self.assertEqual(calls[-1][1]["floor"], 6)
            self.assertEqual(calls[-1][1]["complexity"], 6)
            self.assertTrue(pd["dungeoneering"]["active"])
            self.assertEqual(pd["dungeoneering"]["active_bind_loadout"], 1)
            self.assertEqual(status.text(), "ACTIVE")
            self.assertFalse(bind_loadout.isEnabled())
            self.assertFalse(route.isHidden())
            self.assertTrue(route.isEnabled())
            self.assertGreater(route.count(), 0)
            self.assertFalse(abandon.isHidden())
            self.assertFalse(projection.isHidden())
            self.assertFalse(economy.isHidden())
            self.assertFalse(automation.isHidden())
            self.assertFalse(smuggler_row.isHidden())
            self.assertTrue(bind_row.isHidden())
            self.assertTrue(bind_config_row.isHidden())
            self.assertTrue(kinship_row.isHidden())
            self.assertFalse(reward_trader_row.isHidden())
            self.assertFalse(reward_detail.isHidden())
            self.assertTrue(coal_bag_row.isHidden())

            reward_page = _open_reward_target(dialog, "dungeoneering")
            self.assertTrue(reward_trader_row.isVisibleTo(dialog))
            self.assertTrue(reward_detail.isVisibleTo(dialog))
            self.assertGreater(reward_page.height(), 0)
            self.assertFalse(reward_buy.isEnabled())
            self.assertIn("between dungeons", reward_buy.toolTip())
            tabs = _find_main_tabs(dialog)
            tabs.setCurrentIndex(
                next(
                    index
                    for index in range(tabs.count())
                    if tabs.tabText(index) == "Skills"
                )
            )
            QApplication.processEvents()

            self.assertGreater(smuggler.count(), 0)
            self.assertLess(smuggler.count(), 86)
            self.assertEqual(smuggler.findData("novite_rapier"), -1)
            self.assertIn("session coins", economy.text())
            self.assertIn("reachable from live floor goods", economy.text())
            self.assertIn("Binds 0/2", bind_summary.text())
            self.assertIn("eat Heim crab", automation.text())
            self.assertIn("projected", summary.text())

            updated, ok, info = record_dungeon_drop_pure(
                pd,
                "Eligible blade",
                equipment_slot="weapon",
            )
            self.assertTrue(ok, info)
            pd.clear()
            pd.update(updated)
            panel._ankiscape_refresh_dungeoneering()
            QApplication.processEvents()
            self.assertFalse(bind_row.isHidden())
            self.assertEqual(status.text(), "CHOICE")
            bind_item_action.click()
            QApplication.processEvents()
            self.assertEqual(
                calls[-1],
                ("resolve_bind_offer", {"choice": "bind"}),
            )
            self.assertTrue(bind_row.isHidden())

            route.setCurrentIndex(-1)
            route.setCurrentIndex(0)
            QApplication.processEvents()
            self.assertEqual(calls[-1][0], "select_route")
            self.assertEqual(
                pd["dungeoneering"]["selected_room_id"],
                route.currentData(),
            )

            dialog.resize(900, 560)
            for _ in range(6):
                QApplication.processEvents()
            self.assertLessEqual(
                panel.parentWidget().mapTo(dialog, panel.parentWidget().rect().bottomRight()).y(),
                dialog.contentsRect().bottom(),
            )
            self.assertGreater(panel.height(), 0)
            self.assertGreater(route.width(), 0)

            abandon.click()
            QApplication.processEvents()
            self.assertEqual(calls[-1], ("abandon", {}))
            self.assertFalse(pd["dungeoneering"]["active"])
            self.assertEqual(status.text(), "READY")
            self.assertTrue(abandon.isHidden())
            self.assertTrue(economy.isHidden())
            self.assertTrue(smuggler_row.isHidden())
            self.assertFalse(kinship_row.isHidden())
            self.assertFalse(reward_trader_row.isHidden())
            self.assertFalse(coal_bag_row.isHidden())
            self.assertFalse(bind_config_row.isHidden())
            self.assertEqual(bind_item.count(), 1)
            self.assertEqual(bind_item.currentData(), "Eligible blade")

            bind_loadout.setCurrentIndex(bind_loadout.findData(2))
            QApplication.processEvents()
            self.assertEqual(
                calls[-1],
                ("select_bind_loadout", {"loadout_index": 2}),
            )
            self.assertEqual(bind_item_button.text(), "Add to loadout")
            bind_item_button.click()
            QApplication.processEvents()
            self.assertEqual(
                calls[-1],
                (
                    "set_bind_loadout",
                    {
                        "loadout_index": 2,
                        "item_names": ["Eligible blade"],
                    },
                ),
            )
            self.assertEqual(
                pd["dungeoneering"]["bind_loadouts"][2],
                ["Eligible blade"],
            )
            self.assertLessEqual(
                panel.parentWidget().mapTo(dialog, panel.parentWidget().rect().bottomRight()).y(),
                dialog.contentsRect().bottom(),
            )
        finally:
            if dialog is not None:
                dialog.deleteLater()
            QApplication.setPalette(original_palette)
            QApplication.setStyle(original_style)
