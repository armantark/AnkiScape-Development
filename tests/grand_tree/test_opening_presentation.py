"""Normal Quests control and earned Bank cells in light and Fusion dark palettes."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, QUEST_DATA
from ankiscape.data.quest.grand_tree import QUEST_ID
from ankiscape.logic.bank_layout_logic import reconcile_bank_layout_for_player_pure
from ankiscape.logic_pure.logic_pure_quest import apply_quest_progress_pure, quest_current_stage_blockers_pure
from tests import test_main_menu_widget as menu_harness
from tests.main_menu import fixtures
from tests.grand_tree.test_opening_transactions import player_at, BARK, BOOK, SCROLL
from tests.ui_flows.test_grand_tree_message import _fusion_palette

if menu_harness.HAS_AQT:
    from aqt.qt import QApplication, QIcon, QLineEdit, QPushButton, QToolButton, QScrollArea, QWidget
    from tests.ui_flows.qt_text_fit import text_fit_defects


def pump():
    for _ in range(8):
        QApplication.processEvents()


@unittest.skipUnless(menu_harness.HAS_AQT, 'aqt/PyQt6 not installed (use .venv-qt)')
class OpeningPresentationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = fixtures.MainMenuWidgetTest(methodName='runTest')
        self.menu.setUp()

    def tearDown(self):
        self.menu.tearDown()

    def _open(self, data, dark=False, size=None):
        dialog = self.menu._open(data, current_skill='Mining')
        dialog.show()
        if size:
            dialog.resize(*size)
        pump()
        return dialog

    def _quest_button(self, dialog):
        menu_harness._open_quests_tab(dialog)
        dialog.findChild(QLineEdit, 'questSearchInput').setText('The Grand Tree')
        pump()
        return dialog.findChild(QPushButton, 'questAction_' + QUEST_ID)

    def test_unchanged_quests_control_permits_each_bundle_and_stops_at_stage_three(self):
        data = player_at()
        for boundary in range(5):
            data = reconcile_bank_layout_for_player_pure(data)
            before = copy.deepcopy(data)
            dialog = self._open(data)
            button = self._quest_button(dialog)
            self.assertIsNotNone(button)
            self.assertEqual(button.isEnabled(), boundary < 4)
            self.assertEqual(data, before)
            self.menu._quest_calls.clear()
            button.click()
            pump()
            self.assertEqual(self.menu._quest_calls, [QUEST_ID] if boundary < 4 else [])
            dialog.close()
            if boundary < 4:
                data, ok, completed = apply_quest_progress_pure(data, QUEST_ID, QUEST_DATA)
                self.assertTrue(ok)
                self.assertFalse(completed)

    def test_genuine_missing_materials_and_eligibility_disable_existing_control(self):
        cases = ((1, BARK, 'Missing Bark sample x1'), (2, BOOK, 'Missing Translation book x1'),
                 (2, SCROLL, "Missing Hazelmere's scroll x1"), (0, None, 'Requires Agility 25'))
        for boundary, missing, reason in cases:
            data = player_at(boundary)
            if missing:
                data['inventory'].pop(missing, None)
            else:
                data['agility_level'] = 24
            data = reconcile_bank_layout_for_player_pure(data)
            before = copy.deepcopy(data)
            dialog = self._open(data)
            button = self._quest_button(dialog)
            self.assertFalse(button.isEnabled())
            self.assertIn('Blocked:', button.toolTip())
            self.assertIn(reason, [row['reason'] for row in quest_current_stage_blockers_pure(data, QUEST_ID, QUEST_DATA)])
            calls = list(self.menu._quest_calls)
            button.click()
            pump()
            self.assertEqual(self.menu._quest_calls, calls)
            self.assertEqual(data, before)
            dialog.close()

    def test_bank_and_quests_rebuild_read_only_at_default_and_720_light_and_dark(self):
        app = fixtures.MainMenuWidgetTest.app
        prior_palette, prior_style = app.palette(), app.style().objectName()
        try:
            for dark in (False, True):
                app.setStyle('Fusion')
                app.setPalette(_fusion_palette(dark))
                self._assert_earned_views()
        finally:
            app.setStyle(prior_style)
            app.setPalette(prior_palette)
            pump()

    def _assert_earned_views(self):
        data = player_at()
        earned_states = []
        for _ in range(4):
            data, ok, _ = apply_quest_progress_pure(data, QUEST_ID, QUEST_DATA)
            self.assertTrue(ok)
            earned_states.append(copy.deepcopy(data))
        for data in earned_states:
            self._assert_view_rebuilds(data)

    def _assert_view_rebuilds(self, data):
        # Prepare ordinary Bank layout metadata before comparing complete rebuild states.
        data = reconcile_bank_layout_for_player_pure(data)
        before = copy.deepcopy(data)
        dialog = self._open(data)
        default = (dialog.width(), dialog.height())
        for size in (default, (720, 560)):
            dialog.resize(*size)
            pump()
            self._quest_button(dialog)
            menu_harness._expand_quest_card(dialog, QUEST_ID)
            pump()
            body = dialog.findChild(QWidget, 'questBody_' + QUEST_ID)
            self.assertEqual(text_fit_defects(body), [])
            menu_harness._open_bank_tab(dialog)
            pump()
            self._assert_bank_icons(dialog, data)
            page = dialog.findChild(QScrollArea, 'bankTabScroll')
            self.assertEqual(page.horizontalScrollBar().maximum(), 0)
            self.assertEqual(text_fit_defects(page.widget()), [])
            self.assertEqual(data, before)
        dialog.close()
        # A fresh dialog rebuild exercises the normal registry path again.
        dialog = self._open(data, size=(720, 560))
        self._quest_button(dialog)
        menu_harness._open_bank_tab(dialog)
        pump()
        self._assert_bank_icons(dialog, data)
        self.assertEqual(data, before)
        dialog.close()

    def _assert_bank_icons(self, dialog, data):
        for name in (BARK, BOOK, SCROLL):
            cell = dialog.findChild(QToolButton, 'bankGridItem::' + name)
            if data['inventory'].get(name, 0) <= 0:
                self.assertIsNone(cell)
                continue
            self.assertIsNotNone(cell)
            self.assertFalse(cell.icon().isNull())
            definition = next(row for row in ITEM_DEFINITIONS if row.display_name == name)
            expected = QIcon(definition.asset_path).pixmap(cell.iconSize()).toImage()
            self.assertEqual(cell.icon().pixmap(cell.iconSize()).toImage(), expected)
