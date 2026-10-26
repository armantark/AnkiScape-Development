"""Existing Bank QAction and Treasure Trails panel in light and dark themes."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.data.treasure_trails_data import TREASURE_TRAILS_EASY_STEPS
from ankiscape.logic.treasure_trails_logic import apply_treasure_trails_command_pure
from tests import test_main_menu_widget as widgets
from tests.treasure_trails import SEARCH_ROWS, finite_draws


def process_events():
    for _ in range(4):
        widgets.QApplication.processEvents()


def set_palette(app, dark):
    app.setStyle("Fusion")
    palette = app.style().standardPalette()
    if dark:
        for role, rgb in (
            ("Window", (45, 45, 45)), ("WindowText", (235, 235, 235)),
            ("Base", (30, 30, 30)), ("AlternateBase", (45, 45, 45)),
            ("Text", (235, 235, 235)), ("Button", (55, 55, 55)),
            ("ButtonText", (235, 235, 235)), ("Mid", (95, 95, 95)),
        ):
            palette.setColor(getattr(widgets.QPalette.ColorRole, role), widgets.QColor(*rgb))
    app.setPalette(palette)


def make_command(test, save, step_id):
    registry = list(TREASURE_TRAILS_EASY_STEPS)
    target_draw = (registry.index(step_id) + 0.5) / len(registry)
    draw = finite_draws((0.25, target_draw, target_draw))

    def command(action_id, payload):
        test.assertEqual((action_id, payload), ("start_from_bank", {"tier": "easy"}))
        updated, ok, info = apply_treasure_trails_command_pure(save, action_id, payload, draw)
        if ok:
            save.clear()
            save.update(updated)
        return {"ok": ok, **info}

    return command


def bank_start_action(dialog):
    menu = dialog._ankiscape_equip_menu_for("Clue scroll (easy)")
    return next(action for action in menu.actions() if action.text() == "Start trail")


def open_trail_panel(harness, dialog):
    tree = harness._open_activities(dialog)
    item = next(row for row in widgets._tree_items(tree)
                if row.data(0, widgets.Qt.ItemDataRole.UserRole) == "treasure_trail")
    tree.itemClicked.emit(item, 0)
    process_events()
    return next(panel for panel in dialog.findChildren(widgets.QWidget, "treasureTrailsPanel")
                if panel.isVisible())


def assert_bank_panel(test, step_id, text):
    # Composition avoids unittest rediscovering the harness's many test methods.
    harness = widgets.MainMenuWidgetTest(methodName="runTest")
    harness.setUp()
    dialog = None
    try:
        save = widgets._make_player_data()
        save.update(inventory={"Clue scroll (easy)": 1}, equipment={},
                    treasure_trail={}, treasure_trail_retained={},
                    activity_session={"active_id": ""})
        dialog = harness._open(save, current_skill="Activities",
                               on_treasure_trails_command=make_command(test, save, step_id))
        dialog.show()
        dialog.resize(900, 560)
        process_events()
        action = bank_start_action(dialog)
        test.assertTrue(action.isEnabled())
        test.assertEqual(action.objectName(), "startTreasureTrailAction")
        test.assertEqual(action.data(), "easy")
        action.trigger()
        process_events()
        test.assertEqual(save["treasure_trail"]["steps"], [step_id, step_id])
        panel = open_trail_panel(harness, dialog)
        label = panel.findChild(widgets.QLabel, "treasureTrailsStep")
        test.assertEqual(label.text(), text)
        test.assertTrue(label.isVisible())
        test.assertGreater(label.width(), 0)
        summary = panel.findChild(widgets.QLabel, "treasureTrailsSummary")
        test.assertEqual(summary.text(), "Following an easy trail · clue 1 of 2")
        test.assertFalse(bank_start_action(dialog).isEnabled())
    finally:
        if dialog is not None:
            dialog.close()
        harness.tearDown()
        harness.doCleanups()


@unittest.skipUnless(widgets.HAS_AQT, "requires Qt lane")
class SevenSearchPanelTest(unittest.TestCase):
    def test_bank_start_displays_each_search(self):
        widgets.MainMenuWidgetTest.setUpClass()
        app = widgets.QApplication.instance()
        original_palette = widgets.QPalette(app.palette())
        original_style = app.style().objectName()
        try:
            for dark in (False, True):
                set_palette(app, dark)
                for step_id, text in SEARCH_ROWS:
                    with self.subTest(step_id=step_id, dark=dark):
                        assert_bank_panel(self, step_id, text)
        finally:
            app.setStyle(original_style)
            app.setPalette(original_palette)
