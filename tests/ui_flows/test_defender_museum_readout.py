"""The real Quests card projects the Museum claim before, after and across Undo."""

import copy
import random
import sys
import types
import unittest
from unittest.mock import patch

from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as _main_menu_fixtures
from tests.quest_catalog.defender_museum_fixture import (
    CLAIM_REASON, DEFENDER, LEVELS, PREREQUISITES, ready_defender_player, typed_snapshot,
)

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QColor, QLabel, QLineEdit, QPalette, QPushButton, QScrollArea, QWidget
    from tests.ui_flows.qt_text_fit import text_fit_defects


def _pump():
    for _ in range(6):
        QApplication.processEvents()


def _claim_and_undo_states(check):
    from tests.test_integration_smoke import _DummyCol
    from tests.test_undo_seam_museum import _load_addon, _wire_museum

    check.addCleanup(random.setstate, random.getstate())
    with patch.dict(sys.modules):
        addon = _load_addon()
        _initial, command = _wire_museum(addon, _DummyCol())
        addon._state.player_data = ready_defender_player()
        before = copy.deepcopy(addon._state.player_data)
        result = command("claim_quest_stories", {})
        check.assertTrue(result["ok"])
        claimed = copy.deepcopy(addon._state.player_data)
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        undone = copy.deepcopy(addon._state.player_data)
        check.assertEqual(typed_snapshot(undone), typed_snapshot(before))
        return before, claimed, undone


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class DefenderMuseumReadoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _main_menu_fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = _main_menu_fixtures.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        self.old_palette = QApplication.palette()
        self.old_style = QApplication.style().objectName()

    def tearDown(self):
        self.menu.tearDown()
        QApplication.setStyle(self.old_style)
        QApplication.setPalette(self.old_palette)

    def _palette(self, dark):
        QApplication.setStyle("Fusion")
        palette = QApplication.style().standardPalette()
        if dark:
            for role, color in (
                ("Window", "#282828"), ("Base", "#181818"), ("AlternateBase", "#303030"),
                ("Button", "#303030"), ("Text", "#eeeeee"), ("WindowText", "#eeeeee"),
                ("ButtonText", "#eeeeee"), ("Mid", "#080808"),
                ("Highlight", "#2a82da"), ("HighlightedText", "#ffffff"),
            ):
                palette.setColor(getattr(QPalette.ColorRole, role), QColor(color))
        QApplication.setPalette(palette)

    def _open_card(self, player, size):
        dialog = self.menu._open(copy.deepcopy(player), current_skill="Mining")
        dialog.show()
        if size is not None:
            dialog.resize(*size)
        _pump()
        _main_menu._open_quests_tab(dialog)
        dialog.findChild(QLineEdit, "questSearchInput").setText("Defender of Varrock")
        _pump()
        _main_menu._expand_quest_card(dialog, DEFENDER)
        _pump()
        return dialog, dialog.findChild(QWidget, f"questCard_{DEFENDER}")

    def _assert_card(self, player, size, lock):
        dialog, card = self._open_card(player, size)
        try:
            requirement = next(label for label in card.findChildren(QLabel)
                               if label.text().startswith("Requires:"))
            for text in (CLAIM_REASON, *(name for _qid, name in PREREQUISITES),
                         *(f"{skill.title()} {level}" for skill, level in LEVELS)):
                self.assertIn(text, requirement.text())
            self.assertTrue(requirement.wordWrap())
            self.assertLessEqual(requirement.heightForWidth(requirement.width()), requirement.height())
            action = card.findChild(QPushButton, f"questAction_{DEFENDER}")
            status = card.findChild(QLabel, f"questStatus_{DEFENDER}")
            self.assertEqual(action.isEnabled(), not bool(lock))
            # Unstarted cards say "Not started"; their existing header and title
            # tooltips expose the canonical lock beside the disabled action.
            self.assertEqual(status.text(), "Not started")
            title = next(label for label in card.findChildren(QLabel)
                         if label.text() == "Defender of Varrock")
            if lock:
                self.assertIn(lock, title.toolTip())
                self.assertIn(lock, action.parentWidget().toolTip())
                self.assertIn(lock, action.toolTip())
            if lock != CLAIM_REASON:
                self.assertNotIn(CLAIM_REASON, title.toolTip())
                self.assertNotIn(CLAIM_REASON, action.toolTip())
            page = dialog.findChild(QWidget, "questSearchInputBar").parentWidget()
            self.assertEqual(text_fit_defects(card), [])
            for scroll in page.findChildren(QScrollArea):
                if scroll.isVisibleTo(page):
                    self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
                    self.assertLessEqual(card.width(), scroll.viewport().width())
        finally:
            dialog.close()
            _pump()

    def _assert_palette_readout(self, dark):
        self._palette(dark)
        before, claimed, undone = _claim_and_undo_states(self)
        garden_missing = copy.deepcopy(claimed)
        garden_missing["quests"].pop("garden_of_tranquillity")
        for size in (None, (720, 560)):
            for label, player, lock in (
                ("unclaimed", before, CLAIM_REASON), ("claimed", claimed, ""),
                ("undone", undone, CLAIM_REASON),
                ("garden", garden_missing, "Garden of Tranquillity"),
            ):
                with self.subTest(dark=dark, size=size, state=label):
                    self._assert_card(player, size, lock)

    def test_light_requirements_lock_claim_and_undo(self):
        self._assert_palette_readout(False)

    def test_fusion_dark_requirements_lock_claim_and_undo(self):
        self._assert_palette_readout(True)
