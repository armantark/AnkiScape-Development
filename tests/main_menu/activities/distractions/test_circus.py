from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QListWidget, QModelIndex, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_circus_detail_starts_a_performance_and_exposes_advanced_routine(self) -> None:
        from ankiscape.logic.circus_logic import apply_circus_command_pure

        pd = _make_player_data()
        pd["current_utility"] = "bankstanding"
        command_calls = []

        def circus_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_circus_command_pure(pd, action_id, payload)
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_circus_command=circus_command,
        )
        dialog.show()
        QApplication.processEvents()
        panel = self._open_circus_panel(dialog)
        self.assertEqual(pd["current_utility"], "bankstanding")
        icon = panel.findChild(QLabel, "circusIcon")
        performance = panel.findChild(QComboBox, "circusPerformanceCombo")
        strategy = panel.findChild(QComboBox, "circusStrategyCombo")
        mode = panel.findChild(QComboBox, "circusAutomationMode")
        primary = panel.findChild(QPushButton, "circusPrimaryButton")
        self.assertEqual(primary.text(), "Start activity")
        executing_queue = panel.findChild(QListWidget, "circusExecutingQueue")
        non_executing_queue = panel.findChild(QListWidget, "circusNonExecutingQueue")
        move_to_non_executing = panel.findChild(
            QPushButton, "circusMoveToNonExecutingButton"
        )
        move_to_executing = panel.findChild(
            QPushButton, "circusMoveToExecutingButton"
        )
        edit = panel.findChild(QPushButton, "circusEditRoutineButton")
        status = panel.findChild(QLabel, "circusStatusChip")
        reward_icons = [
            widget
            for widget in panel.findChildren(QLabel)
            if widget.objectName().startswith("circusRewardIcon::")
        ]

        self.assertEqual(icon.size().width(), 28)
        self.assertFalse(icon.pixmap().isNull())
        self.assertEqual(performance.count(), 3)
        self.assertEqual(performance.findData("fire_breathing"), -1)
        self.assertEqual(performance.findData("flaming_poi"), -1)
        self.assertEqual(performance.findData("thieving"), -1)
        self.assertEqual(len(reward_icons), 5)
        self.assertEqual(executing_queue.item(0).data(Qt.ItemDataRole.UserRole), "agility")
        self.assertEqual(non_executing_queue.count(), 2)
        self.assertTrue(all(not widget.pixmap().isNull() for widget in reward_icons))
        self.assertTrue(panel.findChild(QWidget, "circusReward::acrobat").isVisible())
        self.assertFalse(panel.findChild(QWidget, "circusReward::firemaker").isVisible())
        self.assertFalse(edit.isVisible())
        self.assertEqual(status.text(), "3 left this answered-card week")

        pd["quests"]["the_firemakers_curse"] = {"completed": True}
        pd["quests"]["some_like_it_cold"] = {"completed": True}
        panel = self._open_circus_panel(dialog)
        performance = panel.findChild(QComboBox, "circusPerformanceCombo")
        strategy = panel.findChild(QComboBox, "circusStrategyCombo")
        mode = panel.findChild(QComboBox, "circusAutomationMode")
        primary = panel.findChild(QPushButton, "circusPrimaryButton")
        executing_queue = panel.findChild(QListWidget, "circusExecutingQueue")
        non_executing_queue = panel.findChild(QListWidget, "circusNonExecutingQueue")
        move_to_non_executing = panel.findChild(
            QPushButton, "circusMoveToNonExecutingButton"
        )
        move_to_executing = panel.findChild(
            QPushButton, "circusMoveToExecutingButton"
        )
        edit = panel.findChild(QPushButton, "circusEditRoutineButton")
        self.assertEqual(performance.count(), 6)
        self.assertEqual(non_executing_queue.count(), 5)

        performance.setCurrentIndex(performance.findData("fire_breathing"))
        QApplication.processEvents()
        self.assertFalse(panel.findChild(QWidget, "circusReward::acrobat").isVisible())
        self.assertTrue(panel.findChild(QWidget, "circusReward::firemaker").isVisible())

        performance.setCurrentIndex(performance.findData("magic"))
        magic_row = non_executing_queue.findItems(
            "Magic", Qt.MatchFlag.MatchContains
        )[0]
        non_executing_queue.setCurrentItem(magic_row)
        move_to_executing.click()
        before_reorder = [
            executing_queue.item(index).data(Qt.ItemDataRole.UserRole)
            for index in range(executing_queue.count())
        ]
        source_row = before_reorder.index("magic")
        destination_row = 1 if source_row == 0 else 0
        self.assertTrue(
            executing_queue.model().moveRows(
                QModelIndex(), source_row, 1, QModelIndex(), destination_row
            )
        )
        QApplication.processEvents()
        reordered = [
            executing_queue.item(index).data(Qt.ItemDataRole.UserRole)
            for index in range(executing_queue.count())
        ]
        self.assertNotEqual(reordered, before_reorder)
        self.assertEqual(command_calls[-1][0], "set_queue")
        executing_queue.setCurrentItem(
            executing_queue.findItems("Agility", Qt.MatchFlag.MatchContains)[0]
        )
        move_to_non_executing.click()
        self.assertEqual(
            executing_queue.item(0).data(Qt.ItemDataRole.UserRole), "magic"
        )
        strategy.setCurrentIndex(strategy.findData("max_xp"))
        primary.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "start_activity")
        self.assertEqual(self._activity_start_calls[-1], "big_top_bonanza")
        self.assertEqual(pd["current_utility"], "big_top_bonanza")
        self.assertEqual(pd["circus"]["selected_performance"], "magic")
        self.assertEqual(pd["circus"]["strategies"]["magic"], "max_xp")

        from ankiscape.data.circus_data import CIRCUS_PERFORMANCES

        pd["circus"]["performance_queue"] = {
            "executing": ["magic", "agility"],
            "non_executing": ["ranged", "fire_breathing", "flaming_poi", "thieving"],
        }
        pd["circus"]["session"] = {
            "active_performance": "magic",
            "routine": [
                trick.id for trick in CIRCUS_PERFORMANCES["magic"].tricks[:10]
            ],
            "trick_index": 3,
            "payout_tier_mask": 0,
            "score": 120,
            "success_count": 3,
            "attempted_ids": [],
        }
        performance.setCurrentIndex(performance.findData("agility"))
        performance.setCurrentIndex(performance.findData("magic"))
        QApplication.processEvents()
        detail = panel.findChild(QLabel, "circusDetail")
        self.assertIn(
            "Magic spell casting · trick 4 of 10 · 3 successes · next: Agility",
            detail.text(),
        )

        pd["circus"]["used_week_by_performance"]["magic"] = 0
        performance.setCurrentIndex(performance.findData("agility"))
        performance.setCurrentIndex(performance.findData("magic"))
        QApplication.processEvents()
        self.assertIn("done this week", performance.currentText())
        self.assertFalse(primary.isEnabled())
        self.assertFalse(panel.findChild(QPushButton, "circusAbandonButton").isEnabled())

        performance.setCurrentIndex(performance.findData("agility"))
        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertTrue(edit.isVisible())
        before_dialog_count = len(self._captured)
        edit.click()
        QApplication.processEvents()
        self.assertEqual(len(self._captured), before_dialog_count + 1)
        routine_dialog = self._captured[-1]
        routine_combos = [
            combo
            for combo in routine_dialog.findChildren(QComboBox)
            if combo.objectName().startswith("circusRoutineTrick::")
        ]
        self.assertEqual(len(routine_combos), 10)
        self.assertEqual(routine_combos[0].findData(""), -1)
        self.assertGreaterEqual(routine_combos[1].findData(""), 0)
        dialog.close()

    def test_circus_hidden_executing_act_survives_queue_save_and_start(self) -> None:
        from ankiscape.logic.circus_logic import (
            apply_circus_command_pure,
            default_circus_state_pure,
        )

        pd = _make_player_data()
        pd["current_utility"] = "bankstanding"
        pd["circus"] = default_circus_state_pure()
        pd["circus"]["performance_queue"] = {
            "executing": ["agility", "fire_breathing"],
            "non_executing": [
                "magic",
                "ranged",
                "flaming_poi",
                "thieving",
            ],
        }
        command_calls = []

        def circus_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_circus_command_pure(pd, action_id, payload)
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_circus_command=circus_command,
        )
        dialog.show()
        QApplication.processEvents()
        panel = self._open_circus_panel(dialog)
        performance = panel.findChild(QComboBox, "circusPerformanceCombo")
        primary = panel.findChild(QPushButton, "circusPrimaryButton")
        executing_queue = panel.findChild(QListWidget, "circusExecutingQueue")
        non_executing_queue = panel.findChild(QListWidget, "circusNonExecutingQueue")
        move_to_executing = panel.findChild(
            QPushButton, "circusMoveToExecutingButton"
        )

        def assert_hidden_act_preserved() -> None:
            self.assertIn(
                "fire_breathing",
                pd["circus"]["performance_queue"]["executing"],
            )
            self.assertEqual(
                executing_queue.findItems(
                    "Fire-breathing", Qt.MatchFlag.MatchContains
                ),
                [],
            )

        self.assertEqual(performance.findData("fire_breathing"), -1)
        self.assertEqual(executing_queue.count(), 1)
        self.assertEqual(
            executing_queue.item(0).data(Qt.ItemDataRole.UserRole), "agility"
        )

        magic_row = non_executing_queue.findItems(
            "Magic", Qt.MatchFlag.MatchContains
        )[0]
        non_executing_queue.setCurrentItem(magic_row)
        move_to_executing.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "set_queue")
        assert_hidden_act_preserved()

        primary.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "start_activity")
        assert_hidden_act_preserved()

    def test_circus_hidden_saved_selection_falls_back_and_persists(self) -> None:
        from ankiscape.logic.circus_logic import default_circus_state_pure

        pd = _make_player_data()
        pd["circus"] = default_circus_state_pure()
        pd["circus"]["selected_performance"] = "fire_breathing"
        saves = []

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_save_player_data=lambda: saves.append(True),
        )
        dialog.show()
        QApplication.processEvents()
        panel = self._open_circus_panel(dialog)
        performance = panel.findChild(QComboBox, "circusPerformanceCombo")

        self.assertEqual(performance.currentData(), "magic")
        self.assertEqual(pd["circus"]["selected_performance"], "magic")
        self.assertEqual(saves, [True])
