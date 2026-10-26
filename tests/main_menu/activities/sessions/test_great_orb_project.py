from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _open_reward_target,
    _utility_row,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QMessageBox, QProgressBar, QPushButton, QScrollArea, QSpinBox, QWidget
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_great_orb_project_card_saves_buys_enters_and_leaves(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "runecrafting_level": 50,
                "great_orb_project": {
                    "tokens": 200,
                    "games_completed": 0,
                    "games_won": 0,
                    "automation_mode": "casual",
                    "doctrine": "balanced",
                    "crafting_policy": "craft_each_round",
                    "active": {},
                },
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "great_orb_project")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "greatOrbProjectPanel")
        status = _find_named_label(dialog, "greatOrbProjectStatusChip")
        summary = _find_named_label(dialog, "greatOrbProjectSummary")
        mode = panel.findChild(QComboBox, "greatOrbProjectModeCombo")
        doctrine = panel.findChild(QComboBox, "greatOrbProjectDoctrineCombo")
        crafting = panel.findChild(QComboBox, "greatOrbProjectCraftingCombo")
        reward_page = _open_reward_target(dialog, "great_orb_project")
        reward = reward_page.findChild(QComboBox, "greatOrbProjectRewardCombo")
        quantity = reward_page.findChild(QSpinBox, "greatOrbProjectRewardQuantity")
        progress = panel.findChild(QProgressBar, "greatOrbProjectProgress")
        currency = reward_page.findChild(QLabel, "greatOrbProjectCurrencyLabel")
        save = _find_named_button(dialog, "greatOrbProjectSaveButton")
        buy = reward_page.findChild(QPushButton, "greatOrbProjectBuyButton")
        primary = _find_named_button(dialog, "greatOrbProjectPrimaryButton")
        leave = _find_named_button(dialog, "greatOrbProjectLeaveButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertIn("GUILD · 0/0 matches won", status.text())
        self.assertEqual(currency.text(), "200 tokens")
        self.assertIn("Eight altar rounds", summary.text())
        self.assertTrue(progress.isHidden())
        self.assertEqual(reward.count(), 46)
        self.assertEqual(reward.iconSize().width(), 24)
        self.assertEqual(reward.iconSize().height(), 24)
        for reward_id in (
            "air_talisman",
            "mind_talisman",
            "water_talisman",
            "earth_talisman",
            "fire_talisman",
            "body_talisman",
            "cosmic_talisman",
            "chaos_talisman",
            "nature_talisman",
            "law_talisman",
            "green_runecrafter_hat",
            "green_runecrafter_robe",
            "green_runecrafter_skirt",
            "green_runecrafter_gloves",
            "blue_runecrafter_hat",
            "blue_runecrafter_robe",
            "blue_runecrafter_skirt",
            "blue_runecrafter_gloves",
            "yellow_runecrafter_hat",
            "yellow_runecrafter_robe",
            "yellow_runecrafter_skirt",
            "yellow_runecrafter_gloves",
            "master_runecrafter_hat",
            "master_runecrafter_body",
            "master_runecrafter_skirt",
            "master_runecrafter_boots",
            "runecrafting_staff",
            "runecrafting_guild_teleport",
            "air_altar_teleport",
            "mind_altar_teleport",
            "water_altar_teleport",
            "earth_altar_teleport",
            "fire_altar_teleport",
            "body_altar_teleport",
            "cosmic_altar_teleport",
            "chaos_altar_teleport",
            "astral_altar_teleport",
            "nature_altar_teleport",
            "law_altar_teleport",
            "death_altar_teleport",
            "blood_altar_teleport",
            "omni_talisman_staff",
        ):
            reward_index = reward.findData(reward_id)
            self.assertGreaterEqual(reward_index, 0)
            self.assertFalse(reward.itemIcon(reward_index).isNull())
        self.assertGreaterEqual(reward.findData("elemental_talisman"), 0)
        self.assertLess(
            reward.findData("elemental_talisman"),
            reward.findData("green_runecrafter_hat"),
        )
        self.assertLess(
            reward.findData("yellow_runecrafter_gloves"),
            reward.findData("master_runecrafter_hat"),
        )
        self.assertIn(
            "1,000 tokens",
            reward.itemText(reward.findData("green_runecrafter_robe")),
        )
        self.assertIn(
            "15,000 tokens",
            reward.itemText(reward.findData("master_runecrafter_body")),
        )
        reward.setCurrentIndex(reward.findData("omni_talisman"))
        QApplication.processEvents()
        self.assertEqual(buy.text(), "Claim")
        self.assertFalse(buy.isEnabled())
        self.assertIn("Show Elriss", buy.toolTip())

        mode.setCurrentIndex(mode.findData("advanced"))
        doctrine.setCurrentIndex(doctrine.findData("repel"))
        crafting.setCurrentIndex(crafting.findData("save_for_nature"))
        save.click()
        QApplication.processEvents()
        self.assertEqual(
            self._great_orb_project_calls[-1],
            (
                "set_great_orb_project_policy",
                {
                    "automation_mode": "advanced",
                    "doctrine": "repel",
                    "crafting_policy": "save_for_nature",
                },
            ),
        )

        reward.setCurrentIndex(reward.findData("pure_essence"))
        quantity.setValue(25)
        buy.click()
        QApplication.processEvents()
        self.assertEqual(
            self._great_orb_project_calls[-1],
            (
                "buy_great_orb_project_reward",
                {"reward_id": "pure_essence", "quantity": 25},
            ),
        )
        self.assertEqual(pd["inventory"]["Pure essence"], 25)
        self.assertEqual(currency.text(), "175 tokens")

        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._great_orb_project_calls[-1],
            (
                "enter_great_orb_project",
                {
                    "automation_mode": "advanced",
                    "doctrine": "repel",
                    "crafting_policy": "save_for_nature",
                },
            ),
        )
        self.assertEqual(pd["current_utility"], "great_orb_project")
        self.assertIn("IN MATCH", status.text())
        self.assertIn("Round 1/8", summary.text())
        self.assertEqual(progress.value(), 1)
        self.assertFalse(progress.isHidden())
        self.assertTrue(panel.findChild(QWidget, "greatOrbProjectPolicy").isHidden())
        self.assertFalse(leave.isHidden())
        self.assertTrue(
            reward_page.findChild(QWidget, "greatOrbProjectShop").isVisibleTo(dialog)
        )
        self.assertGreater(reward_page.height(), 0)
        self.assertFalse(buy.isEnabled())
        self.assertIn("between matches", buy.toolTip())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._great_orb_project_calls[-1],
            ("leave_great_orb_project", {}),
        )
        self.assertTrue(leave.isHidden())
        self.assertIn("pending tokens forfeited", summary.text())

    def test_great_orb_project_level_gate_is_visible_without_hover(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "runecrafting_level": 49,
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "great_orb_project")
        self.assertFalse(row.isDisabled())
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()
        status = _find_named_label(dialog, "greatOrbProjectStatusChip")
        summary = _find_named_label(dialog, "greatOrbProjectSummary")
        primary = _find_named_button(dialog, "greatOrbProjectPrimaryButton")
        self.assertIn("LOCKED", status.text())
        self.assertIn("Requires level 50 Runecrafting", summary.text())
        self.assertFalse(primary.isEnabled())
