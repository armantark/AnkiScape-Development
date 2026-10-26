from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _icon_pixels, _make_player_data, os, patch, replace
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QIcon, QLabel, QListWidget, QPushButton, QTabWidget, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_slayer_master_card_matches_turael_or_spria(self) -> None:
        for completed, display_name, filename in (
            (False, "Turael", "turael_chathead.png"),
            (True, "Spria", "spria_chathead.png"),
        ):
            with self.subTest(display_name=display_name):
                data = _make_player_data()
                data["quests"]["while_guthix_sleeps"] = {
                    "started": completed,
                    "progress": 1 if completed else 0,
                    "completed": completed,
                }
                dialog = self._open(data)
                self._goto_slayer(dialog)
                tabs = dialog.findChild(QTabWidget, "slayerManagementTabs")
                tabs.setCurrentIndex(1)
                QApplication.processEvents()

                card = dialog.findChild(QWidget, "slayerMaster_turael_spria")
                chathead = card.findChild(QLabel, "slayerMasterChathead")
                self.assertIn(display_name, [label.text() for label in card.findChildren(QLabel)])
                self.assertIsNotNone(chathead.pixmap())
                expected = self._ui._pixel_path_icon(
                    os.path.join(self._ui.current_dir, "activityicons", filename), 48
                )
                self.assertIsNotNone(expected)
                self.assertEqual(
                    _icon_pixels(QIcon(chathead.pixmap()), 48),
                    _icon_pixels(expected, 48),
                )

    def test_slayer_assignment_chathead_matches_every_displayable_master(self) -> None:
        from ankiscape.data.slayer_data import (
            CHAELDAR_MASTER,
            DURADEL_MASTER,
            MAZCHNA_MASTER,
            SLAYER_MASTERS_BY_ID,
            SUMONA_MASTER,
            TURAEL_MASTER,
            VANNAKA_MASTER,
        )

        cases = (
            (TURAEL_MASTER, {}, "Turael", "turael_chathead.png"),
            (
                TURAEL_MASTER,
                {"started": True, "progress": 1, "completed": True},
                "Spria",
                "spria_chathead.png",
            ),
            (MAZCHNA_MASTER, {}, "Mazchna", "mazchna_chathead.png"),
            (
                MAZCHNA_MASTER,
                {"started": True, "progress": 1, "completed": False},
                "Achtryn",
                "achtryn_chathead.png",
            ),
            (VANNAKA_MASTER, {}, "Vannaka", "vannaka_chathead.png"),
            (CHAELDAR_MASTER, {}, "Chaeldar", "chaeldar_chathead.png"),
            (SUMONA_MASTER, {}, "Sumona", "sumona_chathead.png"),
            (DURADEL_MASTER, {}, "Duradel", "duradel_chathead.png"),
            (
                DURADEL_MASTER,
                {"started": True, "progress": 1, "completed": True},
                "Lapalok",
                "lapalok_chathead.png",
            ),
        )
        for master, wgs_state, display_name, filename in cases:
            with self.subTest(display_name=display_name):
                data = _make_player_data()
                if wgs_state:
                    data["quests"]["while_guthix_sleeps"] = wgs_state
                data["slayer_assignment"] = {
                    "master_id": master.id,
                    "family_id": master.assignments[0].id,
                    "initial_count": 1,
                    "remaining": 1,
                }
                live_master = replace(master, runtime_enabled=True)
                with patch.dict(
                    SLAYER_MASTERS_BY_ID, {master.id: live_master}
                ):
                    dialog = self._open(data)
                    self._goto_slayer(dialog)

                chathead = dialog.findChild(QLabel, "slayerAssignmentChathead")
                progress = dialog.findChild(QLabel, "slayerAssignmentProgress")
                self.assertIn(f"assigned by {display_name}", progress.text())
                self.assertIsNotNone(chathead.pixmap())
                expected = self._ui._pixel_path_icon(
                    os.path.join(self._ui.current_dir, "activityicons", filename), 48
                )
                self.assertIsNotNone(expected)
                self.assertEqual(
                    _icon_pixels(QIcon(chathead.pixmap()), 48),
                    _icon_pixels(expected, 48),
                )

    def test_slayer_assignment_without_period_art_has_no_fallback_face(self) -> None:
        from ankiscape.data.slayer_data import SLAYER_MASTERS_BY_ID, TURAEL_MASTER

        data = _make_player_data()
        data["slayer_assignment"] = {
            "master_id": "turael_spria",
            "family_id": "bats",
            "initial_count": 1,
            "remaining": 1,
        }
        without_art = replace(TURAEL_MASTER, chathead_asset_path="")
        with patch.dict(SLAYER_MASTERS_BY_ID, {TURAEL_MASTER.id: without_art}):
            dialog = self._open(data)
            self._goto_slayer(dialog)

        chathead = dialog.findChild(QLabel, "slayerAssignmentChathead")
        progress = dialog.findChild(QLabel, "slayerAssignmentProgress")
        self.assertIn("assigned by Turael", progress.text())
        self.assertTrue(chathead.pixmap() is None or chathead.pixmap().isNull())

    def test_slayer_assignment_action_rerenders_as_active_task(self) -> None:
        dialog = self._open(_make_player_data())
        self._goto_slayer(dialog)

        dialog.findChild(QPushButton, "slayerGetAssignmentButton").click()
        QApplication.processEvents()

        self.assertEqual(
            self._slayer_command_calls[-1],
            ("get_assignment", {"master_id": "turael_spria"}),
        )
        progress = dialog.findChild(QLabel, "slayerAssignmentProgress")
        self.assertIsNotNone(progress)
        self.assertIn("remaining", progress.text())
        self.assertIsNotNone(dialog.findChild(QPushButton, "slayerOpenCombatButton"))

    def test_slayer_open_in_combat_enables_and_composes_task_filter(self) -> None:
        data = _make_player_data()
        data["slayer_assignment"] = {
            "master_id": "turael_spria",
            "family_id": "bats",
            "initial_count": 15,
            "remaining": 15,
        }
        dialog = self._open(data)
        self._goto_slayer(dialog)

        dialog.findChild(QPushButton, "slayerOpenCombatButton").click()
        QApplication.processEvents()

        checkbox = dialog.findChild(QCheckBox, "slayerTaskOnlyCheckBox")
        self.assertIsNotNone(checkbox)
        self.assertTrue(checkbox.isChecked())
        self.assertEqual(
            self._slayer_command_calls[-1],
            ("set_combat_filter", {"enabled": True}),
        )
        tree = dialog.findChild(QListWidget, "combatTargetTree")
        roles = {
            tree.item(index).data(Qt.ItemDataRole.UserRole)
            for index in range(tree.count())
        }
        self.assertIn("giant_bat", roles)
        self.assertNotIn("black_bear", roles)
        giant_bat = next(
            tree.item(index)
            for index in range(tree.count())
            if tree.item(index).data(Qt.ItemDataRole.UserRole) == "giant_bat"
        )
        from ankiscape.core.constants import COMBAT_ENEMY_IMAGES

        self.assertEqual(
            _icon_pixels(giant_bat.icon()),
            _icon_pixels(
                self._ui._pixel_path_icon(
                    COMBAT_ENEMY_IMAGES["giant_bat"],
                    28,
                )
            ),
        )

    def test_slayer_task_filter_empty_state_explains_recovery(self) -> None:
        data = _make_player_data()
        data["slayer_combat_filter"] = True
        dialog = self._open(data, current_skill="Combat")

        tree = dialog.findChild(QListWidget, "combatTargetTree")
        self.assertIsNotNone(tree)
        empty_rows = [
            tree.item(index).text()
            for index in range(tree.count())
            if not tree.item(index).data(Qt.ItemDataRole.UserRole)
        ]
        self.assertTrue(
            any(
                "Untick the filter" in text and "get a new task" in text
                for text in empty_rows
            )
        )
