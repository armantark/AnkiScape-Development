"""Existing quest widgets show truthful, wrapping Hazeel branch journals."""

import copy
import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as _menu_fixtures
from tests.quest_catalog.hazeel_helpers import started_player, shared_player, branch_player, complete_opening, review
from ankiscape.core.constants import QUEST_DATA
from ankiscape.logic.bank_layout_logic import reconcile_bank_layout_for_player_pure
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure
from ankiscape.data.quest.hazeel_opening import VALVE_CONTEXT, ENDPOINT_SENTENCES

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QLabel, QLineEdit, QScrollArea, QPushButton, QWidget, QPoint
    from tests.ui_flows.qt_text_fit import text_fit_defects
    from tests.ui_flows.test_first_cell_selection import _dark_palette

QUEST_ID = 'hazeel_cult'


def _pump():
    for _ in range(6):
        QApplication.processEvents()


def _presented_player(player):
    # Menu construction reconciles Bank presentation for new inventory items.
    # Normalize that existing presentation before taking the journal snapshot.
    return reconcile_bank_layout_for_player_pure(player)


def _journal_cases():
    for branch in ('carnillean', 'hazeel'):
        yield branch, 'selected', _presented_player(branch_player(branch))
        yield branch, 'intermediate', _presented_player(review(branch_player(branch)))
        yield branch, 'endpoint', _presented_player(complete_opening(branch))
        # Explicit legacy save with no new earned endpoint.
        player = branch_player(branch)
        player['quests'][QUEST_ID]['progress'] = 3
        yield branch, 'legacy', _presented_player(player)


@unittest.skipUnless(_main_menu.HAS_AQT, 'aqt/PyQt6 not installed (use .venv-qt)')
class HazeelOpeningUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _menu_fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = _menu_fixtures.MainMenuWidgetTest(methodName='runTest')
        self.menu.setUp()
        self.old_style = QApplication.style().objectName()
        self.old_palette = QApplication.palette()

    def tearDown(self):
        self.menu.tearDown()
        QApplication.setStyle(self.old_style)
        QApplication.setPalette(self.old_palette)

    def _open(self, player, size=None):
        dialog = self.menu._open(player)
        dialog.show()
        if size:
            dialog.resize(*size)
        _pump()
        _main_menu._open_quests_tab(dialog)
        dialog.findChild(QLineEdit, 'questSearchInput').setText('Hazeel Cult')
        _pump()
        _main_menu._expand_quest_card(dialog, QUEST_ID)
        _pump()
        return dialog

    def test_choice_buttons_wait_for_clivet_briefing(self):
        unstarted = _main_menu._make_player_data()
        unstarted['current_quest'] = QUEST_ID
        for player in (unstarted, started_player(), review(started_player())):
            dialog = self._open(player)
            labels = [label.text() for label in dialog.findChildren(QLabel)]
            self.assertNotIn("Choose path: Ceril Carnillean or Hazeel's cult", labels)
            self.assertIsNone(dialog.findChild(QPushButton, 'questChoice_hazeel_cult_side_with_hazeel_s_cult'))
            action = dialog.findChild(QPushButton, 'questAction_hazeel_cult')
            self.assertIsNotNone(action)
            self.assertTrue(action.isEnabled())
            dialog.close()
        dialog = self._open(shared_player())
        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Choose path: Ceril Carnillean or Hazeel's cult", labels)
        action = dialog.findChild(QPushButton, 'questAction_hazeel_cult')
        self.assertFalse(action.isEnabled())
        self.assertIn("Hazeel's cult", action.toolTip())
        for suffix, label, route in (('ceril_carnillean', 'Ceril Carnillean', 'Side with Ceril Carnillean'),
                                      ('hazeel_s_cult', "Hazeel's cult", "Side with Hazeel's cult")):
            button = dialog.findChild(QPushButton, 'questChoice_hazeel_cult_side_with_' + suffix)
            self.assertIsNotNone(button)
            self.assertEqual(button.text(), label)
            button.click()
            _pump()
            self.assertEqual(self.menu._quest_choice_calls[-1], (QUEST_ID, route))

    def test_both_first_journals_render_truthfully_without_mutation(self):
        for branch, phase, player in _journal_cases():
            with self.subTest(branch=branch, phase=phase):
                before = copy.deepcopy(player)
                dialog = self._open(player)
                texts = [label.text() for label in dialog.findChildren(QLabel)]
                row = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)[0]
                for line in row['lines']:
                    self.assertIn(line, texts)
                self.assertFalse(row['completed'])
                if phase != 'legacy':
                    for context in VALVE_CONTEXT:
                        self.assertIn(context, texts)
                        self.assertNotIn('<s>' + context + '</s>', texts)
                if phase == 'endpoint':
                    self.assertIn(ENDPOINT_SENTENCES[branch], texts)
                    self.assertNotIn('<s>' + ENDPOINT_SENTENCES[branch] + '</s>', texts)
                if phase == 'legacy':
                    self.assertIn('I have already progressed beyond this opening.', texts)
                self.assertEqual(player, before)
                dialog.close()

    def _assert_fit(self, player, size):
        before = copy.deepcopy(player)
        dialog = self._open(player, size)
        page = dialog.findChild(QWidget, 'questSearchInputBar').parentWidget()
        self.assertEqual(text_fit_defects(page), [])
        scrolls = [scroll for scroll in page.findChildren(QScrollArea) if scroll.isVisibleTo(page)]
        self.assertTrue(scrolls)
        for scroll in scrolls:
            self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
            self.assertEqual(text_fit_defects(scroll.widget()), [])
        scroll = scrolls[0]
        labels = {label.text(): label for label in scroll.widget().findChildren(QLabel)}
        for line in quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)[0]['lines']:
            label = labels[line]
            self.assertTrue(label.wordWrap())
            self.assertIn('palette(text)', label.styleSheet())
        self.assertGreater(scroll.verticalScrollBar().maximum(), 0)
        last = labels[quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)[0]['lines'][-1]]
        scroll.ensureWidgetVisible(last)
        _pump()
        self.assertTrue(scroll.viewport().rect().intersects(last.rect().translated(last.mapTo(scroll.viewport(), QPoint(0,0)))))
        self.assertEqual(player, before)
        dialog.close()

    def test_hazeel_journal_fits_laptop_sizes(self):
        QApplication.setStyle('Fusion')
        for dark in (False, True):
            QApplication.setPalette(_dark_palette() if dark else QApplication.style().standardPalette())
            for size in (None, (900,560), (720,560)):
                for branch, phase, player in _journal_cases():
                    with self.subTest(dark=dark, size=size, branch=branch, phase=phase):
                        self._assert_fit(player, size)
