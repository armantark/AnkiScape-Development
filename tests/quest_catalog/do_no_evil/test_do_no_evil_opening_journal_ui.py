"""Do No Evil's authored opening fits the existing journal without save effects."""

import copy
import json
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.logic_pure.logic_pure_quest import quest_current_stage_blockers_pure
from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as _main_menu_fixtures
from tests.quest_catalog.do_no_evil.test_do_no_evil_opening_journal import (
    EXPECTED_OPENING, QUEST_ID, _original_journals, _player,
)

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QColor, QLabel, QLineEdit, QPalette, QPoint, QPushButton, QScrollArea, QWidget

    from tests.ui_flows.qt_text_fit import text_fit_defects


def _pump():
    for _ in range(6):
        QApplication.processEvents()


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
class TestDoNoEvilOpeningJournalUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _main_menu_fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = _main_menu_fixtures.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        self.save_player_calls = []
        self.save_skill_calls = []

    def tearDown(self):
        self.menu.tearDown()

    def _open(self, player):
        dialog = self.menu._open(
            player, current_skill="Mining",
            on_save_player_data=lambda *args: self.save_player_calls.append(args),
            on_save_skill=lambda *args: self.save_skill_calls.append(args),
        )
        dialog.show()
        _pump()
        return dialog

    def _search(self, dialog):
        dialog.findChild(QLineEdit, "questSearchInput").setText("Do No Evil")
        _pump()

    def _expand(self, dialog):
        _main_menu._expand_quest_card(dialog, QUEST_ID)
        _pump()

    def _display(self, dialog):
        _main_menu._open_quests_tab(dialog)
        self._search(dialog)
        self._expand(dialog)

    def _assert_journal(self, dialog, progress):
        body = dialog.findChild(QWidget, "questBody_do_no_evil")
        self.assertIsNotNone(body)
        layout = body.layout()
        labels = [layout.itemAt(index).widget() for index in range(layout.count())
                  if isinstance(layout.itemAt(index).widget(), QLabel)]
        texts = [label.text() for label in labels]
        first = texts.index("Stage 1")
        journal = labels[first:]
        expected = ["Stage 1", *EXPECTED_OPENING]
        if progress == 2:
            expected = ["Stage 1", *(f"<s>{line}</s>" for line in EXPECTED_OPENING),
                        "Stage 2", *_original_journals()[2]]
        self.assertEqual([label.text() for label in journal], expected)
        lines = [label for label in journal if not label.text().startswith("Stage ")]
        return body, lines

    def _assert_fit(self, dialog, progress):
        body, lines = self._assert_journal(dialog, progress)
        self.assertTrue(body.isVisible())
        self.assertEqual(text_fit_defects(body), [])
        for label in lines:
            self.assertTrue(label.wordWrap(), label.text())
            self.assertGreaterEqual(label.width(), label.minimumSizeHint().width(), label.text())
            self.assertGreaterEqual(label.height(), label.heightForWidth(label.width()), label.text())
        page = dialog.findChild(QWidget, "questSearchInputBar").parentWidget()
        scroll = page.findChild(QScrollArea)
        self.assertIsNotNone(scroll)
        self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
        scroll.ensureWidgetVisible(lines[-1], 0, 0)
        _pump()
        final_top = lines[-1].mapTo(scroll.viewport(), QPoint(0, 0)).y()
        self.assertGreaterEqual(final_top, 0)
        self.assertLessEqual(final_top + lines[-1].height(), scroll.viewport().height())
        if progress == 2:
            self.assertGreater(scroll.verticalScrollBar().maximum(), 0)

    def test_opening_and_adjacent_journal_wrap(self):
        old_palette = QApplication.palette()
        old_style = QApplication.style().objectName()
        try:
            QApplication.setStyle("Fusion")
            light = QApplication.style().standardPalette()
            for dark in (False, True):
                QApplication.setPalette(_dark_palette() if dark else light)
                for progress in (1, 2):
                    dialog = self._open(_player(progress=progress))
                    self._display(dialog)
                    with self.subTest(dark=dark, progress=progress, size="default"):
                        self._assert_fit(dialog, progress)
                    dialog.resize(720, 560)
                    _pump()
                    with self.subTest(dark=dark, progress=progress, size="720x560"):
                        self.assertEqual((dialog.width(), dialog.height()), (720, 560))
                        self._assert_fit(dialog, progress)
                    dialog.close()
                    _pump()
        finally:
            QApplication.setStyle(old_style)
            QApplication.setPalette(old_palette)
            _pump()

    def _snapshot(self, player):
        return copy.deepcopy((
            player, QUEST_DATA, quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA),
            self.menu._quest_calls, self.menu._quest_choice_calls, self.menu._claim_calls,
            self.save_player_calls, self.save_skill_calls,
        ))

    def _check_operation(self, operation, player, before):
        operation()
        _pump()
        self.assertEqual(self._snapshot(player), before)
        self.assertEqual(player["quest_action_proofs"], [])

    def _assert_reopen_read_only(self, player, progress):
        dialog = self._open(player)
        # Exclude generic initialization, snapshot before the first Quests visit.
        before = self._snapshot(player)
        self._check_operation(lambda: _main_menu._open_quests_tab(dialog), player, before)
        self._check_operation(lambda: self._search(dialog), player, before)
        self._check_operation(lambda: self._expand(dialog), player, before)
        self._assert_journal(dialog, progress)
        toggle = dialog.findChild(QPushButton, "questToggle_do_no_evil")
        self._check_operation(toggle.click, player, before)
        self.assertTrue(dialog.findChild(QWidget, "questBody_do_no_evil").isHidden())
        self._check_operation(toggle.click, player, before)
        self._check_operation(lambda: dialog._ankiscape_menu_ctx.refresh("quests"), player, before)
        self._check_operation(lambda: self._search(dialog), player, before)
        self._check_operation(lambda: self._expand(dialog), player, before)
        self._assert_journal(dialog, progress)
        self._check_operation(dialog.close, player, before)
        reopened = self._open(player)
        self.assertEqual(self._snapshot(player), before)
        self._check_operation(lambda: self._display(reopened), player, before)
        self._assert_journal(reopened, progress)
        self._check_operation(reopened.close, player, before)

    def test_journal_expansion_refresh_and_reopen_are_read_only(self):
        for progress in (1, 2):
            player = _player(progress=progress)
            with self.subTest(progress=progress, save="in-memory"):
                self._assert_reopen_read_only(player, progress)
            reopened_save = json.loads(json.dumps(player))
            with self.subTest(progress=progress, save="JSON-reopened"):
                self._assert_reopen_read_only(reopened_save, progress)


if __name__ == "__main__":
    unittest.main()
