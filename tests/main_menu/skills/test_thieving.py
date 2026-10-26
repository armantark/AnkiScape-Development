from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_list_with_user_role,
    _make_player_data,
    _tree_items,
    _tree_row,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QListWidget, QPushButton, QTreeWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_thieving_support_panel_metadata_selection_lock_and_casual_toggle(self) -> None:
        from ankiscape.core.target_metadata import thieving_target_rows

        targets = {
            "pickpocket_man": {
                "display_name": "Man",
                "level": 1,
                "xp": 8,
                "group": "pickpocketing",
                "coins": 3,
            },
            "vegetable_stall": {
                "display_name": "Vegetable stall",
                "level": 2,
                "xp": 10,
                "group": "stalls",
            },
            "wall_safe": {
                "display_name": "Wall safe",
                "level": 50,
                "xp": 70,
                "group": "safes",
            },
            "blackjack_menaphite_thug": {
                "display_name": "Menaphite thug",
                "level": 65,
                "xp": 137.5,
                "group": "blackjacking",
                "quest_gate": "the_feud",
                "quest_gate_label": "The Feud",
            },
        }
        player_data = _make_player_data()
        player_data["thieving_level"] = 10
        player_data["current_thieving"] = "pickpocket_man"

        rows = thieving_target_rows(player_data, targets, {}, "pickpocket_man")
        self.assertEqual(
            [row.group for row in rows],
            ["pickpocketing", "stalls", "safes", "blackjacking"],
        )
        self.assertTrue(rows[0].current)
        self.assertTrue(rows[1].enabled)
        self.assertFalse(rows[2].enabled)
        self.assertIn("Locked: Thieving level 50", rows[2].label)
        self.assertIn("Locked due to: Thieving level 50", rows[2].tooltip)

        previous = {
            "targets": self._ui.THIEVING_TARGETS,
            "labels": self._ui.THIEVING_GROUP_LABELS,
            "order": self._ui.THIEVING_GROUP_ORDER,
            "default": self._ui.DEFAULT_THIEVING_TARGET,
            "images": self._ui.THIEVING_ITEM_IMAGES,
        }
        dialog = None
        try:
            self._ui.THIEVING_TARGETS = targets
            self._ui.THIEVING_GROUP_LABELS = {
                "pickpocketing": "Pickpocketing",
                "stalls": "Stalls",
                "safes": "Safes",
                "blackjacking": "Blackjacking",
            }
            self._ui.THIEVING_GROUP_ORDER = (
                "pickpocketing",
                "stalls",
                "safes",
                "blackjacking",
            )
            self._ui.DEFAULT_THIEVING_TARGET = "pickpocket_man"
            self._ui.THIEVING_ITEM_IMAGES = {}

            dialog = self._open(player_data, current_skill="Thieving")
            dialog.show()
            QApplication.processEvents()
            support = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Support")
            self.assertTrue(support.isVisible())
            skill_list = next(
                widget
                for widget in dialog.findChildren(QListWidget)
                if "Thieving" in [widget.item(i).text() for i in range(widget.count())]
            )
            self.assertTrue(any(skill_list.item(i).text() == "Thieving" for i in range(skill_list.count())))

            target_list = _find_list_with_user_role(dialog, "pickpocket_man")
            self.assertEqual(
                target_list.currentItem().data(Qt.ItemDataRole.UserRole),
                "pickpocket_man",
            )

            locked = next(
                target_list.item(index)
                for index in range(target_list.count())
                if target_list.item(index).data(Qt.ItemDataRole.UserRole) == "wall_safe"
            )
            self.assertFalse(locked.flags() & Qt.ItemFlag.ItemIsEnabled)
            before = list(self._thieving_calls)
            target_list.itemClicked.emit(locked)
            target_list.itemActivated.emit(locked)
            QApplication.processEvents()
            self.assertEqual(self._thieving_calls, before)

            stall = next(
                target_list.item(index)
                for index in range(target_list.count())
                if target_list.item(index).data(Qt.ItemDataRole.UserRole) == "vegetable_stall"
            )
            self.assertTrue(stall.flags() & Qt.ItemFlag.ItemIsEnabled)
            target_list.itemClicked.emit(stall)
            QApplication.processEvents()
            self.assertEqual(self._thieving_calls[-1], "vegetable_stall")

            fight_back = dialog.findChild(QCheckBox, "thievingFightBackCheck")
            self.assertFalse(fight_back.isChecked())
            fight_back.click()
            QApplication.processEvents()
            self.assertEqual(self._thieving_fight_back_calls[-1], True)
            self.assertTrue(player_data["thieving_fight_back_when_caught"])
        finally:
            self._ui.THIEVING_TARGETS = previous["targets"]
            self._ui.THIEVING_GROUP_LABELS = previous["labels"]
            self._ui.THIEVING_GROUP_ORDER = previous["order"]
            self._ui.DEFAULT_THIEVING_TARGET = previous["default"]
            self._ui.THIEVING_ITEM_IMAGES = previous["images"]
            if dialog is not None:
                dialog.deleteLater()

    def test_thieving_live_npc_rows_render_portraits_instead_of_loot_icons(self) -> None:
        from ankiscape.data.thieving_data import THIEVING_NPC_TARGET_IDS

        player_data = _make_player_data()
        player_data["thieving_level"] = 99
        player_data["current_thieving"] = "pickpocket_man"
        dialog = self._open(player_data, current_skill="Thieving")
        try:
            tree = dialog.findChild(QTreeWidget, "thievingTargetTree")
            rows = {
                item.data(0, Qt.ItemDataRole.UserRole): item
                for item in _tree_items(tree)
            }
            self.assertEqual(
                set(THIEVING_NPC_TARGET_IDS),
                {target_id for target_id in THIEVING_NPC_TARGET_IDS if target_id in rows},
            )
            for target_id in THIEVING_NPC_TARGET_IDS:
                self.assertFalse(rows[target_id].icon(0).isNull(), target_id)
                self.assertEqual(
                    self._ui.THIEVING_ITEM_IMAGES[target_id],
                    self._ui.THIEVING_NPC_IMAGES[target_id],
                )
        finally:
            dialog.deleteLater()

    def test_thieving_target_change_refreshes_train_readiness(self) -> None:
        pd = _make_player_data()
        pd.update({"thieving_level": 1, "current_thieving": "wall_safe"})
        dialog = self._open(pd, current_skill="Mining")
        dialog.show()
        QApplication.processEvents()
        next(
            button for button in dialog.findChildren(QPushButton)
            if button.text() == "Support"
        ).click()
        QApplication.processEvents()
        skill_list = next(
            widget for widget in dialog.findChildren(QListWidget)
            if "Thieving" in [widget.item(i).text() for i in range(widget.count())]
        )
        skill_list.setCurrentRow(next(
            i for i in range(skill_list.count())
            if skill_list.item(i).text() == "Thieving"
        ))
        QApplication.processEvents()
        train = next(
            button for button in dialog.findChildren(QPushButton)
            if button.text() == "Train this skill" and button.isVisible()
        )
        self.assertFalse(train.isEnabled())

        tree = dialog.findChild(QTreeWidget, "thievingTargetTree")
        tree.itemClicked.emit(_tree_row(tree, "pickpocket_man"), 0)
        QApplication.processEvents()

        train = next(
            button for button in dialog.findChildren(QPushButton)
            if button.text() == "Train this skill" and button.isVisible()
        )
        self.assertTrue(train.isEnabled())
