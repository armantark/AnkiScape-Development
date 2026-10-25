"""Desert Treasure's restored supply list stays readable and read-only in Quests."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import quest_current_stage_blockers_pure
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QColor, QLabel, QLineEdit, QPalette, QPushButton, QScrollArea, QWidget

    from tests.ui_flows.qt_text_fit import text_fit_defects


QUEST_ID = "desert_treasure"
EXPECTED_SUPPLIES = (
    "6 Steel bars", "12 Magic logs", "6 Molten glass", "1 Charcoal",
    "1 Blood rune", "1 Ashes", "1 Bones",
)
SUPPLY_INVENTORY = {
    "Steel bar": 6, "Magic logs": 12, "Molten glass": 6, "Charcoal": 1,
    "Blood rune": 1, "Ashes": 1, "Bones": 1,
}


def _pump():
    for _ in range(6):
        QApplication.processEvents()


def _player(banked=False):
    # Disposable display fixtures, without acquisition or performed-deed credit.
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["quests"][QUEST_ID] = {"started": True, "progress": 1, "completed": False}
    player["quest_action_proofs"] = {}
    if banked:
        player["inventory"].update(SUPPLY_INVENTORY)
    return player


def _dark_palette():
    dark = QPalette()
    for role, rgb in (
        ("Window", (45, 45, 45)), ("WindowText", (235, 235, 235)),
        ("Base", (30, 30, 30)), ("AlternateBase", (45, 45, 45)),
        ("Text", (235, 235, 235)), ("Button", (55, 55, 55)),
        ("ButtonText", (235, 235, 235)), ("Mid", (95, 95, 95)),
    ):
        dark.setColor(getattr(QPalette.ColorRole, role), QColor(*rgb))
    return dark


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class TestDesertTreasureMirrorJournalUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        raw = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        original = tuple(raw["journal_stages"][0]["journal"])
        self.expected_journal = original[:6] + EXPECTED_SUPPLIES + original[6:]

    def tearDown(self):
        self.menu.tearDown()

    def _open(self, player):
        dialog = self.menu._open(player, current_skill="Mining")
        dialog.show()
        _pump()
        return dialog

    def _display_journal(self, dialog):
        _main_menu._open_quests_tab(dialog)
        dialog.findChild(QLineEdit, "questSearchInput").setText("Desert Treasure")
        _pump()
        _main_menu._expand_quest_card(dialog, QUEST_ID)
        _pump()
        self._assert_journal(dialog)

    def _assert_journal(self, dialog):
        body = dialog.findChild(QWidget, "questBody_desert_treasure")
        self.assertIsNotNone(body)
        layout = body.layout()
        labels = [layout.itemAt(index).widget() for index in range(layout.count())
                  if isinstance(layout.itemAt(index).widget(), QLabel)]
        texts = [label.text() for label in labels]
        stage_index = texts.index("Stage 1")
        journal = labels[stage_index + 1:]
        self.assertEqual(tuple(label.text() for label in journal), self.expected_journal)
        self.assertEqual(len(journal), 16)
        self.assertEqual(tuple(label.text() for label in journal[6:13]), EXPECTED_SUPPLIES)
        for label in journal:
            self.assertTrue(label.wordWrap(), label.text())
        return body, journal

    def _assert_fit(self, dialog):
        body, journal = self._assert_journal(dialog)
        self.assertTrue(body.isVisible())
        self.assertEqual(text_fit_defects(body), [])
        for label in journal:
            self.assertLessEqual(label.heightForWidth(label.width()), label.height(), label.text())
        page = dialog.findChild(QWidget, "questSearchInputBar").parentWidget()
        scroll = page.findChild(QScrollArea)
        self.assertIsNotNone(scroll)
        self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)

    def test_supply_order_and_wrapping(self):
        old_palette = QApplication.palette()
        old_style = QApplication.style().objectName()
        try:
            for dark in (False, True):
                if dark:
                    QApplication.setStyle("Fusion")
                    QApplication.setPalette(_dark_palette())
                dialog = self._open(_player())
                self._display_journal(dialog)
                with self.subTest(dark=dark, size="default"):
                    self._assert_fit(dialog)
                dialog.resize(720, 560)
                _pump()
                with self.subTest(dark=dark, size="720x560"):
                    self.assertEqual((dialog.width(), dialog.height()), (720, 560))
                    self._assert_fit(dialog)
                dialog.close()
                _pump()
        finally:
            QApplication.setStyle(old_style)
            QApplication.setPalette(old_palette)
            _pump()

    def _snapshot(self, player):
        return copy.deepcopy((
            player, quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA),
            self.menu._quest_calls, self.menu._quest_choice_calls, self.menu._claim_calls,
        ))

    def _assert_read_only(self, player, before):
        self.assertEqual(self._snapshot(player), before)

    def _assert_reopening_read_only(self, player):
        dialog = self._open(player)
        # Generic menu initialization precedes the snapshot and first Quests open.
        before = self._snapshot(player)
        self._display_journal(dialog)
        self._assert_read_only(player, before)

        dialog.findChild(QPushButton, "questToggle_desert_treasure").click()
        _pump()
        body, _ = self._assert_journal(dialog)
        self.assertTrue(body.isHidden())
        self._assert_read_only(player, before)
        self._display_journal(dialog)
        self._assert_read_only(player, before)

        dialog._ankiscape_menu_ctx.refresh("quests")
        _pump()
        self._display_journal(dialog)
        self._assert_read_only(player, before)
        dialog.close()
        _pump()
        self._assert_read_only(player, before)
        reopened = self._open(player)
        self._assert_read_only(player, before)
        self._display_journal(reopened)
        self._assert_read_only(player, before)
        reopened.close()
        _pump()
        self._assert_read_only(player, before)

    def test_open_and_refresh_are_read_only(self):
        for banked in (False, True):
            with self.subTest(banked=banked):
                self._assert_reopening_read_only(_player(banked))


if __name__ == "__main__":
    unittest.main()
