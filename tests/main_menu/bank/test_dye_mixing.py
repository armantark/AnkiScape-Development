"""Dye Utilities and the Bank menu share recipes and one undoable pair per click."""

import copy
import sys
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import UTILITY_ACTIVITY_DATA
from ankiscape.logic_pure.logic_pure import apply_utility_activity_pure
from tests import test_direct_action_undo_seam as undo
from tests import test_main_menu_widget as main
from tests.main_menu import fixtures

if main.HAS_AQT:
    from aqt.qt import QApplication, QLineEdit


class DyeMixingLogicTest(unittest.TestCase):
    def test_green_and_purple_utilities_make_one_dye_without_xp(self):
        for activity_id, inputs, output in (
            ("mix_green_dye", {"Blue dye": 1, "Yellow dye": 1}, "Green dye"),
            ("mix_purple_dye", {"Blue dye": 1, "Red dye": 1}, "Purple dye"),
        ):
            with self.subTest(activity_id=activity_id):
                spec = UTILITY_ACTIVITY_DATA[activity_id]
                self.assertEqual(spec["requirements"], inputs)
                self.assertEqual(
                    spec["group"], UTILITY_ACTIVITY_DATA["mix_orange_dye"]["group"]
                )
                self.assertIn("5953125", spec["source"])
                inventory = {item: 3 for item in inputs}
                updated, xp, ok, count = apply_utility_activity_pure(
                    activity_id, inventory, UTILITY_ACTIVITY_DATA
                )
                self.assertEqual((xp, ok, count), (0, True, 1))
                self.assertEqual(updated, {**{item: 2 for item in inputs}, output: 1})
                self.assertEqual(inventory, {item: 3 for item in inputs})

    def test_bank_mixes_one_pair_from_the_utility_rows_and_refuses_missing_inputs(self):
        from ankiscape.core.menu_bank_items import dye_mix_options_pure, mix_dye_pure

        for recipe_id in ("mix_orange_dye", "mix_green_dye", "mix_purple_dye"):
            spec = UTILITY_ACTIVITY_DATA[recipe_id]
            inputs = spec["requirements"]
            for selected in inputs:
                with self.subTest(recipe=recipe_id, selected=selected):
                    player = {"inventory": {item: 2 for item in inputs}, "crafting_exp": 17}
                    original = copy.deepcopy(player)
                    choices = dye_mix_options_pure(player, selected)
                    self.assertEqual([row["activity_id"] for row in choices], [recipe_id])
                    updated, ok = mix_dye_pure(player, choices[0]["activity_id"])
                    self.assertTrue(ok)
                    self.assertEqual(
                        updated["inventory"],
                        {**{item: 1 for item in inputs}, spec["output_item"]: 1},
                    )
                    self.assertEqual(updated["crafting_exp"], 17)
                    self.assertEqual(player, original)
                    player["inventory"][selected] = 0
                    self.assertEqual(dye_mix_options_pure(player, selected), ())
                    self.assertEqual(mix_dye_pure(player, recipe_id), (player, False))
        player = {"inventory": {"Red dye": 1, "Goblin mail": 1, "Orange dye": 1}}
        self.assertEqual(dye_mix_options_pure(player, "Orange dye"), ())
        self.assertEqual(mix_dye_pure(player, "dye_goblin_mail_orange"), (player, False))


@unittest.skipUnless(main.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class DyeMixingMenuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.seam = undo.DirectActionUndoSeamTest(methodName="runTest")
        # Keep the runtime package for lazy imports, but restore real Qt for widgets.
        modules = dict(sys.modules)
        self.seam.setUp()
        runtime = {
            name: value for name, value in sys.modules.items()
            if name.startswith("ankiscape_undo_seam")
        }
        sys.modules.clear()
        sys.modules.update(modules)
        sys.modules.update(runtime)
        self.menu = fixtures.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self):
        self.menu.tearDown()
        self.seam.tearDown()

    def test_bank_mix_menu_lists_partners_clicks_once_and_undo_restores_both(self):
        from ankiscape.core.menu_bank_items import mix_dye

        addon = self.seam.addon
        player = main._make_player_data()
        player["inventory"] = {"Red dye": 1, "Yellow dye": 1, "Blue dye": 1}
        addon._state.player_data = player
        dialog = self.menu._open(player, on_mix_dye=lambda recipe: mix_dye(addon, recipe))
        main._open_bank_tab(dialog)
        menu = dialog._ankiscape_equip_menu_for("Red dye")
        mixes = next(
            action.menu() for action in menu.actions() if action.text() == "Mix with"
        )
        self.assertEqual([action.text() for action in mixes.actions()], [
            "Yellow dye → Orange dye", "Blue dye → Purple dye",
        ])
        mixes.actions()[0].trigger()
        QApplication.processEvents()
        self.assertEqual(player["inventory"], {
            "Red dye": 0, "Yellow dye": 0, "Blue dye": 1, "Orange dye": 1,
        })
        self.assertEqual(self.seam.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(self.seam.saves), 1)
        self.assertFalse(mix_dye(addon, "mix_orange_dye"))
        self.assertEqual(len(self.seam.collection.entries), 1)
        addon._on_state_did_undo(type("Changes", (), {"operation": "AnkiScape direct action"})())
        self.assertEqual(player["inventory"], {"Red dye": 1, "Yellow dye": 1, "Blue dye": 1})
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        player["inventory"] = {"Red dye": 2, "Yellow dye": 0, "Orange dye": 1}
        for item in ("Red dye", "Orange dye"):
            absent = dialog._ankiscape_equip_menu_for(item)
            self.assertNotIn("Mix with", [action.text() for action in absent.actions()])

    def test_utilities_dye_search_shows_all_three_mixes_with_inputs_and_icons(self):
        player = main._make_player_data()
        player["inventory"] = {"Red dye": 2, "Yellow dye": 2, "Blue dye": 2}
        dialog = self.menu._open(player)
        tree = self.menu._open_utility(dialog)
        search = dialog.findChild(QLineEdit, "utilityActivityTargetSearchInput")
        search.setText("dye")
        QApplication.processEvents()
        for recipe in ("mix_orange_dye", "mix_green_dye", "mix_purple_dye"):
            row = main._utility_row(tree, recipe)
            self.assertFalse(row.isHidden())
            self.assertFalse(row.icon(0).isNull())
            self.assertIn(UTILITY_ACTIVITY_DATA[recipe]["display_name"], row.text(0))
            for item in UTILITY_ACTIVITY_DATA[recipe]["requirements"]:
                self.assertIn(f"{item} x1", row.toolTip(0))
