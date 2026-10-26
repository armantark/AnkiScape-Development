from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _open_reward_target, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QProgressBar, QPushButton, QSize, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_trouble_brewing_detail_enters_selects_and_buys_reward(self) -> None:
        from ankiscape.logic.trouble_brewing_logic import apply_trouble_brewing_command_pure

        pd = _make_player_data()
        pd["cooking_level"] = 40
        pd["quests"]["cabin_fever"]["completed"] = True
        pd["trouble_brewing_pieces_of_eight"] = 50
        command_calls = []

        def trouble_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_trouble_brewing_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_trouble_brewing_command=trouble_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "trouble_brewing"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "troubleBrewingPanel")
            if widget.isVisible()
        )
        icon = panel.findChild(QLabel, "troubleBrewingIcon")
        mode = panel.findChild(QComboBox, "troubleBrewingModeCombo")
        duty = panel.findChild(QComboBox, "troubleBrewingDutyCombo")
        primary = panel.findChild(QPushButton, "troubleBrewingPrimaryButton")
        progress = panel.findChild(QProgressBar, "troubleBrewingProgress")

        self.assertFalse(icon.pixmap().isNull())
        self.assertFalse(progress.isVisible())
        self.assertFalse(duty.isEnabled())
        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertTrue(duty.isEnabled())
        duty.setCurrentIndex(duty.findData("sabotage"))
        primary.click()
        QApplication.processEvents()

        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "trouble_brewing")
        self.assertEqual(pd["trouble_brewing"]["duty"], "sabotage")
        self.assertTrue(progress.isVisible())
        self.assertEqual(primary.text(), "Active for reviews")
        self.assertFalse(panel.findChild(QWidget, "troubleBrewingSavePlanButton").isEnabled())

        pd["trouble_brewing"] = {}
        pd["activity_session"] = {"active_id": ""}
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        reward_page = _open_reward_target(dialog, "trouble_brewing")
        reward_combo = reward_page.findChild(
            QComboBox, "troubleBrewingRewardCombo"
        )
        self.assertEqual(reward_combo.count(), 31)
        self.assertTrue(
            all(
                reward_combo.itemText(index).endswith(" PoE")
                for index in range(reward_combo.count())
            )
        )
        self.assertTrue(
            all(
                not reward_combo.itemIcon(index).isNull()
                for index in range(reward_combo.count())
            )
        )
        self.assertEqual(reward_combo.iconSize(), QSize(24, 24))
        the_stuff_index = reward_combo.findData("the_stuff")
        self.assertIn(
            "greatly improves the chance of mature ale",
            reward_combo.itemData(
                the_stuff_index, Qt.ItemDataRole.ToolTipRole
            ),
        )
        red_rum_index = reward_combo.findData("red_rum")
        self.assertEqual(
            reward_combo.itemData(red_rum_index, Qt.ItemDataRole.ToolTipRole),
            "One-use teleport to Trouble Brewing.",
        )
        medium_clue_index = reward_combo.findData("medium_clue")
        self.assertIn(
            "Awards one medium clue if you hold no clue scroll.",
            reward_combo.itemData(
                medium_clue_index, Qt.ItemDataRole.ToolTipRole
            ),
        )
        self.assertIn(
            "Need 4,950 more Pieces of Eight.",
            reward_combo.itemData(
                medium_clue_index, Qt.ItemDataRole.ToolTipRole
            ),
        )
        reward_combo.setCurrentIndex(
            reward_combo.findData("blue_tricorn_hat")
        )
        QApplication.processEvents()
        buy = reward_page.findChild(QPushButton, "troubleBrewingBuyButton")
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "buy_reward")
        self.assertEqual(pd["inventory"]["Blue tricorn hat"], 1)
        self.assertEqual(pd["trouble_brewing_pieces_of_eight"], 0)
        dialog.close()

    def test_trouble_brewing_medium_clue_service_renders_and_blocks_a_second_clue(self) -> None:
        from ankiscape.logic.trouble_brewing_logic import apply_trouble_brewing_command_pure

        pd = _make_player_data()
        pd["trouble_brewing_pieces_of_eight"] = 5_000

        def trouble_command(action_id, payload):
            updated, ok, info = apply_trouble_brewing_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_trouble_brewing_command=trouble_command,
        )
        dialog.show()
        QApplication.processEvents()
        reward_page = _open_reward_target(dialog, "trouble_brewing")
        reward_combo = reward_page.findChild(
            QComboBox, "troubleBrewingRewardCombo"
        )
        reward_combo.setCurrentIndex(reward_combo.findData("medium_clue"))
        QApplication.processEvents()
        buy = reward_page.findChild(QPushButton, "troubleBrewingBuyButton")
        self.assertFalse(reward_combo.itemIcon(reward_combo.currentIndex()).isNull())
        self.assertEqual(
            reward_combo.toolTip(),
            "Awards one medium clue if you hold no clue scroll.",
        )
        self.assertTrue(buy.isEnabled())

        buy.click()
        QApplication.processEvents()

        self.assertEqual(pd["inventory"]["Clue scroll (medium)"], 1)
        self.assertEqual(pd["trouble_brewing_pieces_of_eight"], 0)
        self.assertFalse(buy.isEnabled())
        self.assertIn("already have a clue scroll", reward_combo.toolTip())
        self.assertIn("clue held", reward_combo.currentText())
        self.assertIn("already have a clue scroll", buy.toolTip())
        dialog.close()
