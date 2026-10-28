"""The real Bank QAction displays every exact search in the existing panel."""

import unittest

from tests import test_main_menu_widget as menu
from tests.main_menu import fixtures
from tests.treasure_trails.test_search_catalog import (
    SEARCH_CASES, CLUE, fresh_player, search_draws, apply_treasure_trails_command_pure,
)


@unittest.skipUnless(menu.HAS_AQT, 'aqt/PyQt6 not installed (use Qt lane)')
class SearchPanelTest(unittest.TestCase):
    def test_bank_start_displays_each_exact_search(self):
        # The integrated menu suite moved MainMenuWidgetTest into fixtures.
        # Use that fixture by composition so discovery cannot collect it twice.
        fixtures.MainMenuWidgetTest.setUpClass()
        for step_id, text in SEARCH_CASES:
            with self.subTest(step_id=step_id):
                fixture = fixtures.MainMenuWidgetTest()
                try:
                    fixture.setUp()
                    self.assert_bank_search(fixture, step_id, text)
                finally:
                    fixture.tearDown()
                    fixture.doCleanups()

    def assert_bank_search(self, fixture, step_id, text):
        data = fresh_player()
        calls = []
        rng = search_draws(step_id, length=1)

        def command(action, payload):
            calls.append((action, dict(payload)))
            updated, ok, info = apply_treasure_trails_command_pure(data, action, payload, rng)
            if ok:
                data.clear()
                data.update(updated)
            return {'ok': ok, **info}

        dialog = fixture._open(data, current_skill='Activities', on_treasure_trails_command=command)
        try:
            dialog.show()
            dialog.resize(900, 560)
            self.process_events()
            tree = fixture._open_activities(dialog)
            item = next(row for row in menu._tree_items(tree)
                        if row.data(0, menu.Qt.ItemDataRole.UserRole) == 'treasure_trail')
            tree.itemClicked.emit(item, 0)
            self.process_events()
            action_menu = dialog._ankiscape_equip_menu_for(CLUE)
            action = next(row for row in action_menu.actions() if row.text() == 'Start trail')
            self.assertEqual(action.objectName(), 'startTreasureTrailAction')
            self.assertEqual(action.data(), 'easy')
            self.assertTrue(action.isEnabled())
            action.trigger()
            self.process_events()
            self.assertEqual(calls, [('start_from_bank', {'tier': 'easy'})])
            self.assertEqual(data['treasure_trail']['steps'], [step_id])
            self.assertEqual(data['treasure_trail']['index'], 0)
            tree.itemClicked.emit(item, 0)
            self.process_events()
            panel = next(widget for widget in dialog.findChildren(menu.QWidget, 'treasureTrailsPanel')
                         if widget.isVisible())
            label = panel.findChild(menu.QLabel, 'treasureTrailsStep')
            self.assertTrue(label.isVisible())
            self.assertEqual(label.text(), text)
        finally:
            dialog.close()

    def process_events(self):
        for _ in range(4):
            menu.QApplication.processEvents()
