"""Real catalog widgets use the same typo tolerance and quest ranking."""

import os
from pathlib import Path
import unittest

from tests import test_main_menu_widget as menu_tests
from tests.main_menu import fixtures as test_main_menu_widget_behavior

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
        test_main_menu_widget_behavior.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = test_main_menu_widget_behavior.MainMenuWidgetTest(methodName="runTest")
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
        extra.setdefault("on_ge_action", lambda *_args: {"ok": True})
        dialog = self.menu._open(data, current_skill=skill, **extra)
        dialog.show()
        dialog.resize(720, 560)
        pump()
        return dialog, data

    def check_phrase_selection(self, search):
        from ankiscape.ui.ui import SearchLineEdit

        self.assertIsInstance(search, SearchLineEdit, search.objectName())
        self.assertTrue(search.isEnabled(), search.objectName())
        phrase = "Stolen Hearts and bat bones"
        search.setText(phrase)
        pump()
        menu_tests.QTest.mouseDClick(search, Qt.MouseButton.LeftButton)
        self.assertEqual(search.selectedText(), phrase, search.objectName())
        menu_tests.QTest.keyClick(search, Qt.Key.Key_Backspace)
        self.assertEqual(search.text(), "")

    def test_double_click_selects_the_phrase_in_all_search_boxes(self):
        skills = (
            "Mining", "Woodcutting", "Smithing", "Crafting", "Fletching",
            "Herblore", "Summoning", "Prayer", "Construction", "Magic",
            "Firemaking", "Fishing", "Hunter", "Cooking", "Runecrafting",
            "Thieving", "Agility", "Combat",
        )
        for skill in skills:
            with self.subTest(skill=skill):
                dialog, _ = self.open(skill)
                search = dialog.findChild(QLineEdit, f"{skill.lower()}TargetSearchInput")
                self.check_phrase_selection(search)
                dialog.close()
        dialog, _ = self.open()
        for surface in (self.menu._open_utility, self.menu._open_activities):
            surface(dialog)
            search = dialog.findChild(QLineEdit, "utilityActivityTargetSearchInput")
            self.check_phrase_selection(search)
        tabs = menu_tests._find_main_tabs(dialog)
        found = set()
        for index in range(tabs.count()):
            tabs.setCurrentIndex(index)
            pump()
            searches = [search for search in dialog.findChildren(QLineEdit)
                        if search.isVisible() and "search" in search.objectName().casefold()]
            for search in searches:
                found.add(search.objectName())
                self.check_phrase_selection(search)
        self.assertTrue({
            "questSearchInput", "shopSearchInput", "geItemSearchInput",
            "cabinetSearch", "bankSearchInput", "collectionsSearch",
        } <= found, found)
        dialog.findChild(QToolButton, "mainMenuHelpButton").click()
        self.check_phrase_selection(dialog.findChild(QLineEdit, "helpSearch"))

    def test_search_box_census_has_no_plain_line_edits(self):
        from ankiscape.ui.ui import SearchLineEdit

        dialog, _ = self.open()
        tabs = menu_tests._find_main_tabs(dialog)
        for index in range(tabs.count()):
            tabs.setCurrentIndex(index)
            pump()
        searches = [search for search in dialog.findChildren(QLineEdit)
                    if "search" in search.objectName().casefold()]
        self.assertTrue(searches)
        for search in searches:
            self.assertIsInstance(search, SearchLineEdit, search.objectName())

    def test_combat_matches_names_groups_and_only_logged_drops(self):
        dialog, data = self.open("Combat")
        search = dialog.findChild(QLineEdit, "combatTargetSearchInput")
        search.setText("bat")
        pump()
        rows = dialog.findChild(QListWidget, "combatTargetTree")
        self.assertEqual({rows.item(i).text() for i in range(rows.count())},
                         {"Giant bat (Lvl\xa027)", "Guard (battleaxe) (Lvl\xa021)"})
        search.setText("cockatrice mirror")
        pump()
        rows = dialog.findChild(QListWidget, "combatTargetTree")
        self.assertEqual(rows.item(0).text(), "No combat targets match this search.")
        self.assertNotIn("current_combat_target", data)
        self.assertEqual(self.menu._combat_calls, [])
        dialog.close()
        data["combat_observed_drops"] = {
            "chicken": {"Feather": {"times_seen": 1, "quantity_seen": 5}}
        }
        dialog = self.menu._open(data, current_skill="Combat")
        search = dialog.findChild(QLineEdit, "combatTargetSearchInput")
        search.setText("feather")
        pump()
        rows = dialog.findChild(QListWidget, "combatTargetTree")
        self.assertEqual([rows.item(i).data(Qt.ItemDataRole.UserRole)
                          for i in range(rows.count())], ["chicken"])
        search.setText("animals")
        pump()
        rows = dialog.findChild(QListWidget, "combatTargetTree")
        matches = {rows.item(i).data(Qt.ItemDataRole.UserRole) for i in range(rows.count())}
        self.assertIn("black_bear", matches)
        self.assertNotIn("guard_battleaxe", matches)

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

    def test_target_level_labels_do_not_split(self):
        for skill in ("Combat", "Mining", "Woodcutting", "Crafting", "Fishing"):
            with self.subTest(skill=skill):
                dialog, _ = self.open(skill)
                selector = dialog.findChild(QListWidget, f"{skill.lower()}TargetTree")
                if selector is not None:
                    labels = [selector.item(i).text() for i in range(selector.count())]
                else:
                    tree = dialog.findChild(QTreeWidget, f"{skill.lower()}TargetTree")
                    labels = [item.text(0) for item in tree.findItems(
                        "*", Qt.MatchFlag.MatchWildcard | Qt.MatchFlag.MatchRecursive)]
                levels = [label for label in labels if "(Lvl" in label]
                self.assertTrue(levels)
                for label in levels:
                    self.assertNotIn("(Lvl ", label)
                    self.assertIn("(Lvl\xa0", label)
                dialog.close()

    def test_exchange_search_hint_is_minimal(self):
        dialog, _ = self.open()
        menu_tests._open_ge_tab(dialog)
        search = dialog.findChild(QLineEdit, "geItemSearchInput")
        self.assertEqual(search.placeholderText(), "Search exchangeable items")


if __name__ == "__main__":
    unittest.main()
