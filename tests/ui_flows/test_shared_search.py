"""Real catalog widgets use the same typo tolerance and quest ranking."""

import os
from pathlib import Path
import unittest

from tests import test_main_menu_widget as menu_tests

if menu_tests.HAS_AQT:
    from aqt.qt import QApplication, QComboBox, QLineEdit, QLabel, QListWidget, Qt, QToolButton, QTreeWidget, QWidget
    from tests.ui_flows.qt_text_fit import text_fit_defects


def pump():
    for _ in range(6):
        QApplication.processEvents()


@unittest.skipUnless(menu_tests.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class SharedSearchWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        menu_tests.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = menu_tests.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self):
        self.menu.tearDown()

    def capture(self, dialog, name, root=None):
        pump()
        folder = os.environ.get("SEARCH_EVIDENCE_DIR")
        if folder:
            path = Path(folder)
            path.mkdir(parents=True, exist_ok=True)
            self.assertTrue(dialog.grab().save(str(path / f"{name}.png")))
        self.assertEqual(text_fit_defects(root or dialog), [])

    def open(self, skill="Mining", **extra):
        data = menu_tests._make_player_data()
        data["inventory"] = {"Tiara": 2, "Air tiara": 1, "Logs": 3}
        dialog = self.menu._open(data, current_skill=skill, **extra)
        dialog.show()
        dialog.resize(720, 560)
        pump()
        return dialog, data

    def test_tara_finds_crafting_and_runecrafting_without_changing_target(self):
        for skill in ("Crafting", "Runecrafting"):
            with self.subTest(skill=skill):
                dialog, data = self.open(skill)
                before = dict(data)
                search = dialog.findChild(QLineEdit, f"{skill.lower()}TargetSearchInput")
                search.setText("tara")
                self.capture(dialog, skill.lower())
                selector = dialog.findChild(QListWidget, f"{skill.lower()}TargetTree")
                if selector is not None:
                    names = [selector.item(i).text() for i in range(selector.count())]
                else:
                    tree = dialog.findChild(QTreeWidget, f"{skill.lower()}TargetTree")
                    names = [item.text(0) for item in tree.findItems(
                        "*", Qt.MatchFlag.MatchWildcard | Qt.MatchFlag.MatchRecursive
                    )]
                self.assertTrue(any("tiara" in name.casefold() for name in names), names)
                self.assertEqual(data, before)
                dialog.close()

    def test_quests_rank_name_first_and_keep_sort_inside_metadata_tier(self):
        dialog, _ = self.open()
        menu_tests._open_quests_tab(dialog)
        search = dialog.findChild(QLineEdit, "questSearchInput")
        search.setText("Stolen Hearts")
        self.capture(dialog, "quests")
        sort = dialog.findChild(QComboBox, "questSortCombo")
        for mode in ("Release Order", "Difficulty", "Length"):
            sort.setCurrentText(mode)
            pump()
            found = [w.objectName().removeprefix("questCard_") for w in dialog.findChildren(QWidget)
                     if w.objectName().startswith("questCard_")]
            self.assertEqual(found[0], "stolen_hearts")
            search.clear()
            pump()
            unfiltered = [w.objectName().removeprefix("questCard_") for w in dialog.findChildren(QWidget)
                          if w.objectName().startswith("questCard_")]
            self.assertEqual(found[1:], [key for key in unfiltered if key in found[1:]])
            search.setText("Stolen Hearts")
            pump()

    def test_quest_search_preserves_one_heading_per_section(self):
        from ankiscape.core.constants import QUEST_DATA
        from ankiscape.ui.ui_tab_quests import _quest_match_rank

        dialog, _ = self.open()
        menu_tests._open_quests_tab(dialog)
        search = dialog.findChild(QLineEdit, "questSearchInput")
        for query in ("the", "mogre"):
            search.setText(query)
            pump()
            headings = [label.text() for label in dialog.findChildren(QLabel)
                        if label.objectName().startswith("questSection_")]
            self.assertEqual(headings, ["Quests", "Miniquests"], query)
            cards = [w.objectName().removeprefix("questCard_") for w in dialog.findChildren(QWidget)
                     if w.objectName().startswith("questCard_")]
            sections = [bool(QUEST_DATA[key].get("miniquest")) for key in cards]
            self.assertEqual(sections, sorted(sections))
            for miniquest in (False, True):
                ranks = [_quest_match_rank(query, (key, QUEST_DATA[key])) for key in cards
                         if bool(QUEST_DATA[key].get("miniquest")) == miniquest]
                self.assertEqual(ranks, sorted(ranks))
            self.capture(dialog, f"quests-{query}")

    def test_bank_and_shop_accept_the_same_missing_letter(self):
        dialog, _ = self.open()
        menu_tests._open_bank_tab(dialog)
        dialog.findChild(QLineEdit, "bankSearchInput").setText("tara")
        self.capture(dialog, "bank")
        names = [w.objectName() for w in dialog.findChildren(QToolButton)
                 if w.objectName().startswith("bankGridItem::")]
        self.assertIn("bankGridItem::Tiara", names)
        self.assertNotIn("bankGridItem::Logs", names)
        menu_tests._open_shop_tab(dialog)
        dialog.findChild(QLineEdit, "shopSearchInput").setText("tara")
        self.capture(dialog, "shop")
        stock = dialog.findChild(QListWidget, "shopSelectionList")
        self.assertTrue(any("tiara" in stock.item(i).text().casefold() for i in range(stock.count())))

    def test_exchange_accepts_missing_letter_through_real_projection(self):
        from ankiscape.logic.grand_exchange_logic import ge_frontend_projection_pure

        from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG

        data = menu_tests._make_player_data()
        dialog, _ = self.open(get_ge_projection=lambda: ge_frontend_projection_pure(data, item_catalog=GE_ITEM_CATALOG))
        menu_tests._open_ge_tab(dialog)
        dialog.findChild(QLineEdit, "geItemSearchInput").setText("tara")
        rows = dialog.findChild(QListWidget, "geItemList")
        self.capture(dialog, "exchange", rows.parentWidget())
        self.assertTrue(any("tiara" in rows.item(i).text().casefold() for i in range(rows.count())))


if __name__ == "__main__":
    unittest.main()
