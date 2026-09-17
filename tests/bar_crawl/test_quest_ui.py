"""Drive Barcrawl's real quest cards through the offscreen main menu."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from tests import test_main_menu_widget as menu
from tests.bar_crawl.test_vendor_actions import BAR_CRAWL_PURCHASES
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest_data import BAR_CRAWL_ID
from ankiscape.logic.shop_logic import apply_shop_vendor_action_pure
from ankiscape.logic_pure.logic_pure import apply_quest_progress_pure, start_quest_pure


@unittest.skipUnless(menu.HAS_AQT, "requires the offscreen Qt interpreter")
class TestBarCrawlQuestUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = menu.QApplication.instance() or menu.QApplication([])

    def setUp(self):
        self.player = menu._make_player_data()
        self.player["inventory"]["Coins"] = sum(row[1] for row in BAR_CRAWL_PURCHASES)
        self.dialogs = []

    def tearDown(self):
        for dialog in self.dialogs:
            dialog.close()
            dialog.deleteLater()
        menu.QApplication.sendPostedEvents(None, menu.QEvent.Type.DeferredDelete)

    def _open(self):
        from ankiscape.ui import ui

        dialogs = self.dialogs

        class CapturingDialog(ui.QDialog):
            def exec(dialog):
                dialog.setAttribute(menu.Qt.WidgetAttribute.WA_DeleteOnClose, False)
                dialogs.append(dialog)
                return 0

        def start(quest_id):
            updated, started = start_quest_pure(self.player, quest_id, QUEST_DATA)
            self.assertTrue(started)
            self.player.update(updated)
            self.player["current_quest"] = quest_id
            return started

        with patch.object(ui, "QDialog", CapturingDialog):
            ui.show_main_menu(
                player_data=self.player,
                current_skill="Mining",
                on_save_skill=lambda skill: None,
                on_set_ore=lambda ore: None,
                on_set_tree=lambda tree: None,
                on_set_bar=lambda bar: None,
                on_set_craft=lambda craft: None,
                on_set_quest=start,
            )
        dialog = self.dialogs[-1]
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(3):
            menu.QApplication.processEvents()
        skills = menu._find_skill_list(dialog)
        row = next(i for i in range(skills.count()) if skills.item(i).text() == "Mining")
        skills.setCurrentRow(row)
        skills.itemActivated.emit(skills.item(row))
        menu.QApplication.processEvents()
        menu._open_quests_tab(dialog)
        return dialog

    def _card(self, dialog, status):
        card = dialog.findChild(menu.QWidget, "questCard_bar_crawl")
        self.assertIsNotNone(card)
        self.assertTrue(card.isVisible())
        labels = [label.text() for label in card.findChildren(menu.QLabel)]
        self.assertIn("Alfred Grimhand's Barcrawl", labels)
        self.assertIn(status, labels)
        return card

    def test_card_heading_statuses_and_metadata_filters(self):
        dialog = self._open()
        card = self._card(dialog, "Not started")
        heading = dialog.findChild(menu.QLabel, "questSection_Miniquests")
        self.assertIsNotNone(heading)
        self.assertEqual(heading.text(), "Miniquests")
        layout = card.parentWidget().layout()
        self.assertLess(layout.indexOf(heading), layout.indexOf(card))
        self.assertGreater(
            layout.indexOf(heading),
            layout.indexOf(dialog.findChild(menu.QWidget, "questCard_cooks_assistant")),
        )
        self._assert_filters(dialog, "Not started")
        dialog.findChild(menu.QComboBox, "questDifficultyFilterCombo").setCurrentText("All difficulties")
        dialog.findChild(menu.QComboBox, "questLengthFilterCombo").setCurrentText("All lengths")
        menu.QApplication.processEvents()
        card = self._card(dialog, "Not started")
        action = card.findChild(menu.QPushButton, "questAction_bar_crawl")
        self.assertEqual(action.text(), "Start quest")
        self.assertTrue(action.isEnabled())
        action.click()
        menu.QApplication.processEvents()
        self.assertTrue(self.player["quests"][BAR_CRAWL_ID]["started"])
        self._card(dialog, "Stage 0/3")

        self.player, ok, completed = apply_quest_progress_pure(self.player, BAR_CRAWL_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed)
        dialog.close()
        dialog = self._open()
        card = dialog.findChild(menu.QWidget, "questCard_bar_crawl")
        self.assertTrue(any(
            label.text().startswith("Blocked: Action required:")
            for label in card.findChildren(menu.QLabel)
        ))
        for action_id, _, _, _ in BAR_CRAWL_PURCHASES:
            self.player, result = apply_shop_vendor_action_pure(self.player, action_id)
            self.assertTrue(result["allowed"], result)
        dialog.close()
        dialog = self._open()
        card = self._card(dialog, "Stage 2/3")
        self.assertEqual(card.findChild(menu.QPushButton, "questAction_bar_crawl").text(), "Continue quest")
        self._assert_filters(dialog, "Stage 2/3")

        self.player, ok, completed = apply_quest_progress_pure(self.player, BAR_CRAWL_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed)
        dialog.close()
        dialog = self._open()
        card = self._card(dialog, "Completed")
        action = card.findChild(menu.QPushButton, "questAction_bar_crawl")
        self.assertEqual(action.text(), "Completed")
        self.assertFalse(action.isEnabled())
        self._assert_filters(dialog, "Completed")

    def _assert_filters(self, dialog, status):
        difficulty = dialog.findChild(menu.QComboBox, "questDifficultyFilterCombo")
        length = dialog.findChild(menu.QComboBox, "questLengthFilterCombo")
        for difficulty_text, length_text in (
            ("Special", "All lengths"),
            ("All difficulties", "Medium"),
            ("Special", "Medium"),
        ):
            with self.subTest(difficulty=difficulty_text, length=length_text):
                difficulty.setCurrentText(difficulty_text)
                length.setCurrentText(length_text)
                menu.QApplication.processEvents()
                self.assertEqual(difficulty.currentText(), difficulty_text)
                self.assertEqual(length.currentText(), length_text)
                self._card(dialog, status)
        difficulty.setCurrentText("Novice")
        menu.QApplication.processEvents()
        self.assertIsNone(dialog.findChild(menu.QWidget, "questCard_bar_crawl"))


if __name__ == "__main__":
    unittest.main()
