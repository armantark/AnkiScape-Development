"""The real Bank and Equipment menus operate the hood and explain command refusals."""

import copy
import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as main

if main.HAS_AQT:
    from aqt.qt import QApplication, QPoint
    from ankiscape.logic.wicked_hood_logic import apply_wicked_hood_command_pure
    from tests.ui_flows.qt_text_fit import text_fit_defects


def _pump():
    for _ in range(6):
        QApplication.processEvents()


@unittest.skipUnless(main.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class WickedHoodMenuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        main.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.harness = main.MainMenuWidgetTest(methodName="runTest")
        self.harness.setUp()

    def tearDown(self):
        self.harness.tearDown()

    def _open(self, worn=False, unfed=False):
        player = main._make_player_data()
        player["inventory"] = {} if worn else {"Wicked hood": 1}
        player["inventory"]["Rune essence"] = 100
        player["equipment"] = {"head": "Wicked hood"} if worn else {}
        player["runecrafting_level"] = 1
        player["quests"]["rune_mysteries"] = {"completed": True}
        player["claims"]["wicked_hood"] = {"claimed": True}
        player["wicked_hood"] = {"fed_altars": ["air", "nature", "death"]}
        if unfed:
            player["wicked_hood"] = {}
            player["inventory"].update({"Air talisman": 2, "Air tiara": 1, "Tiara": 1})

        def command(action, payload):
            updated, ok, info = apply_wicked_hood_command_pure(copy.deepcopy(player), action, payload)
            if ok:
                player.clear()
                player.update(updated)
            return {"ok": ok, **info}

        dialog = self.harness._open(player, on_wicked_hood_command=command)
        dialog.show()
        dialog.resize(720, 560)
        _pump()
        return player, dialog

    def _menu(self, dialog, worn=False):
        return dialog._ankiscape_unequip_menu_for("head") if worn else dialog._ankiscape_equip_menu_for("Wicked hood")

    def test_talisman_menu_feeds_once_and_unlocks_the_hood_menu(self):
        player, dialog = self._open(unfed=True)
        main._open_bank_tab(dialog)
        _pump()
        menu = dialog._ankiscape_equip_menu_for("Air talisman")
        menu.popup(dialog.mapToGlobal(QPoint(20, 80)))
        _pump()
        self._assert_menu_fits(menu)
        self.assertEqual(text_fit_defects(dialog), [])
        feed = next(a for a in menu.actions() if a.text() == "Feed to Wicked hood")
        self.assertTrue(feed.isEnabled())
        feed.trigger()
        self.assertEqual(player["inventory"]["Air talisman"], 1)
        hood_menu = self._menu(dialog)
        teleports = next(a.menu() for a in hood_menu.actions() if a.text().startswith("Teleport"))
        self.assertEqual([a.text() for a in teleports.actions()], ["Air altar"])
        for item in ("Air talisman", "Air tiara"):
            repeated = dialog._ankiscape_equip_menu_for(item)
            action = next(a for a in repeated.actions() if a.text() == "Feed to Wicked hood")
            self.assertFalse(action.isEnabled())
            self.assertIn("already been fed", action.toolTip())
        unsupported = dialog._ankiscape_equip_menu_for("Tiara")
        self.assertNotIn("Feed to Wicked hood", [a.text() for a in unsupported.actions()])
        menu.close()

    def test_tiara_menu_and_removed_target_group(self):
        player, dialog = self._open(unfed=True)
        menu = dialog._ankiscape_equip_menu_for("Air tiara")
        next(a for a in menu.actions() if a.text() == "Feed to Wicked hood").trigger()
        self.assertEqual(player["inventory"]["Air tiara"], 0)
        tree = main._goto_runecrafting(dialog)
        self.assertNotIn("Hood feeding", [tree.topLevelItem(i).text(0) for i in range(tree.topLevelItemCount())])

    def test_auto_target_is_selectable_before_the_first_pack(self):
        _, dialog = self._open()
        tree = main._goto_runecrafting(dialog)
        row = main._tree_row(tree, "craft_air_runes")
        self.assertFalse(row.isDisabled())
        tree.itemClicked.emit(row, 0)
        _pump()
        self.assertEqual(self.harness._runecrafting_calls[-1], "craft_air_runes")

    def test_bank_and_worn_menus_withdraw_and_keep_command_reasons(self):
        for worn in (False, True):
            with self.subTest(worn=worn):
                player, dialog = self._open(worn)
                before = copy.deepcopy(player)
                menu = self._menu(dialog, worn)
                self.assertEqual(player, before, "Building the menu must not execute a command")
                essence = next(a for a in menu.actions() if a.text().startswith("Withdraw essence"))
                self.assertEqual(essence.text(), "Withdraw essence (100 left)")
                essence.trigger()
                self.assertEqual(player["carried_inventory"]["craft_air_runes"]["Rune essence"], 28)
                self.assertEqual(player["wicked_hood"]["essence_remaining"], 72)
                menu = self._menu(dialog, worn)
                essence = next(a for a in menu.actions() if a.text().startswith("Withdraw essence"))
                self.assertFalse(essence.isEnabled())
                self.assertEqual(essence.toolTip(), "No carried-pack space or essence allowance remains.")
                dialog.close()

    def test_fed_submenus_show_quantities_and_level_refusals(self):
        player, dialog = self._open()
        menu = self._menu(dialog)
        runes = next(a.menu() for a in menu.actions() if a.text().startswith("Withdraw runes"))
        self.assertEqual([a.text() for a in runes.actions()], ["Air rune ×100", "Nature rune ×5", "Death rune ×5"])
        teleports = next(a.menu() for a in menu.actions() if a.text().startswith("Teleport"))
        nature = next(a for a in teleports.actions() if a.data() == "nature")
        self.assertFalse(nature.isEnabled())
        self.assertIn("44", nature.text())
        self.assertEqual(nature.toolTip(), "Requires level 44 Runecrafting.")

    def test_quest_locked_teleport_reports_quest_reason(self):
        player, dialog = self._open()
        player["runecrafting_level"] = 99
        menu = self._menu(dialog)
        teleports = next(a.menu() for a in menu.actions() if a.text().startswith("Teleport"))
        death = next(a for a in teleports.actions() if a.data() == "death")
        self.assertFalse(death.isEnabled())
        self.assertIn("Mourning", death.toolTip())

    def test_rune_withdrawal_and_teleport_spend_allowances(self):
        player, dialog = self._open()
        menu = self._menu(dialog)
        runes = next(a.menu() for a in menu.actions() if a.text().startswith("Withdraw runes"))
        runes.actions()[0].trigger()
        self.assertEqual(player["inventory"]["Air rune"], 100)
        menu = self._menu(dialog)
        runes = next(a.menu() for a in menu.actions() if a.text().startswith("Withdraw runes"))
        self.assertFalse(runes.actions()[0].isEnabled())
        self.assertEqual(runes.actions()[0].toolTip(), "No rune withdrawals remain this review day.")
        teleports = next(a.menu() for a in menu.actions() if a.text().startswith("Teleport"))
        next(a for a in teleports.actions() if a.data() == "air").trigger()
        self.assertEqual(player["wicked_hood"]["pending_altar_teleport"], "air")
        self.assertEqual(player["wicked_hood"]["teleports_remaining"], 1)
        menu = self._menu(dialog)
        teleports = next(a.menu() for a in menu.actions() if a.text().startswith("Teleport"))
        self.assertTrue(all(not a.isEnabled() for a in teleports.actions()))
        self.assertEqual(teleports.actions()[0].toolTip(), "A teleport to Air altar is already queued.")

    def _assert_menu_fits(self, menu):
        self.assertEqual(text_fit_defects(menu), [])
        for action in menu.actions():
            if not action.isSeparator():
                self.assertGreaterEqual(menu.actionGeometry(action).width(), menu.fontMetrics().horizontalAdvance(action.text()))

    def test_menus_fit_at_owner_size(self):
        for worn in (False, True):
            _, dialog = self._open(worn)
            if worn:
                main._open_equipment_tab(dialog)
            else:
                main._open_bank_tab(dialog)
            _pump()
            menu = self._menu(dialog, worn)
            menu.popup(dialog.mapToGlobal(QPoint(20, 80)))
            _pump()
            self._assert_menu_fits(menu)
            for action in menu.actions():
                submenu = action.menu()
                if submenu is None or not action.text().startswith(("Withdraw runes", "Teleport")):
                    continue
                submenu.popup(menu.mapToGlobal(QPoint(menu.width(), 0)))
                _pump()
                self._assert_menu_fits(submenu)
                submenu.close()
            menu.close()
            dialog.close()
