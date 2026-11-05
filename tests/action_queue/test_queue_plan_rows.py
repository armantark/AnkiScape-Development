"""One click plans a row that lacks only what its run uses up; Start waits for those items.

The owner's cases (Pass 21): a click on Unfired bowl with no Soft clay left Add
on the old target, and Bronze arrows stayed grey with Smithing arrowtips queued
first. The flows click the real menu and answer through the real review handler;
the census asks the real row builders of every skill.
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core import constants as c, target_metadata as rows_of
from ankiscape.core.action_products import action_target_spec_pure
from ankiscape.core.menu_action_queue import pick_can_start_pure, plan_rows_pure
from ankiscape.core.storage_pure import default_player_data
from ankiscape.core.tool_belt import without_belt_tools
from ankiscape.data import construction_data as house, summoning_data as summoning
from ankiscape.data.agility_data import AGILITY_TARGETS
from ankiscape.data.thieving_data import THIEVING_TARGETS
from tests.action_queue.test_queue_target_clicks import TargetClickFlow
from tests.test_main_menu_widget import HAS_AQT, _find_list_with_user_role

if HAS_AQT:
    from aqt.qt import QLabel, QListWidget, Qt
    from PyQt6.QtTest import QTest

_ARROWTIPS = {"kind": "skill", "skill": "Smithing", "target": "forge_bronze_arrowtips"}
_SAPPHIRE = {"kind": "skill", "skill": "Crafting", "target": "cut_sapphire"}
_BOWL = {"kind": "skill", "skill": "Crafting", "target": "form_bowl_unfired"}
_PLANKS = {"kind": "utility", "utility_id": "convert_logs_to_planks"}


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class PlanRowClickTest(TargetClickFlow):
    def _plan_addon(self, name, *entries, **save):
        return self._capture_menus(self._queue_addon(f"ankiscape_plan_rows_{name}", *entries, **save))

    def _press_header(self, dialog):
        QTest.mouseClick(self._header(dialog), Qt.MouseButton.LeftButton)
        self._settle()

    def _show_supply_change(self, addon):
        addon.update_review_hud(addon._state.player_data, addon._state.current_skill)
        self._settle()

    def test_arrows_after_queued_arrowtips_take_one_click_the_promised_count_and_become_real(self):
        addon = self._plan_addon(
            "arrows", (_ARROWTIPS, 840), fletching_level=10, current_fletch="arrow_shafts",
            inventory={"Bronze bar": 56, "Headless arrows": 840},
        )
        save = addon._state.player_data
        dialog = self._menu(addon, "Fletching")

        tree, row = self._click_row(dialog, "bronze_arrows")

        self.assertEqual(tree.selectedItems(), [row])
        self.assertEqual((self._count(dialog).value(), self._count(dialog).suffix()), (840, " Bronze arrows"))
        self.assertEqual(
            self._visible(dialog, QLabel, "queueMaterials").text().replace(" ", " "),
            "Headless arrows: 840 in Bank · Bronze arrowtips: 0 in Bank, 840 from entry 1",
        )
        self.assertEqual((self._header(dialog).text(), self._header(dialog).isEnabled()), ("Train this skill", False))

        self._press_header(dialog)
        self.assertEqual((save["current_fletch"], addon._state.current_skill), ("arrow_shafts", "Smithing"))

        self._add(dialog)
        self.assertEqual(
            self._queue_lines(addon),
            [("Smithing: Bronze arrowtips", "current", 0), ("Fletching: Bronze arrows", "waiting", 0)],
        )
        self.assertEqual(save["current_fletch"], "arrow_shafts")

        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
            # The first arrowtips are in the Bank, so Start now offers the pick.
            self._settle()
            self.assertTrue(self._header(dialog).isEnabled())
            for _ in range(30):
                if not self._queue_lines(addon):
                    break
                self._answer(addon)

        self.assertEqual(self.errors, [])
        self.assertEqual(self._queue_lines(addon), [])
        self.assertEqual((save["inventory"]["Bronze arrows"], save["inventory"].get("Bronze arrowtips", 0)), (840, 0))

    def test_a_bowl_without_clay_takes_one_click_during_a_running_entry_and_start_waits_for_clay(self):
        addon = self._plan_addon("bowl", (_SAPPHIRE, 100), crafting_level=20, inventory={"Uncut sapphire": 100})
        save = addon._state.player_data
        dialog = self._menu(addon, "Crafting")
        self.assertEqual(self._header(dialog).text(), "Currently training")

        self._click_row(dialog, "form_bowl_unfired")

        self.assertEqual((self._count(dialog).value(), self._count(dialog).suffix()), (1, " Bowl (unfired)"))
        self.assertEqual((self._header(dialog).text(), self._header(dialog).isEnabled()), ("Train this skill", False))
        # The off button keeps none of the green it wore while it read "Currently training".
        self.assertNotIn("76, 175, 80", self._header(dialog).styleSheet())
        self._add(dialog)
        self.assertEqual(save["action_queue"]["entries"][1], {"action": _BOWL, "count": 1})
        self.assertEqual(save["current_craft"], "cut_sapphire")

        save["inventory"]["Soft clay"] = 5
        self._show_supply_change(addon)
        self._start_ahead_of_queue(dialog)
        self.assertEqual(save["current_craft"], "form_bowl_unfired")

    def test_a_row_without_inputs_keeps_the_saved_target_when_nothing_runs_it(self):
        addon = self._plan_addon("idle", crafting_level=20, current_craft="cut_sapphire", inventory={})
        save = addon._state.player_data
        dialog = self._menu(addon, "Crafting")

        tree, row = self._click_row(dialog, "form_bowl_unfired")
        self.assertEqual(tree.selectedItems(), [row])
        self.assertEqual(self._count(dialog).suffix(), " Bowl (unfired)")
        self.assertFalse(self._header(dialog).isEnabled())
        self._press_header(dialog)
        self.assertEqual((save["current_craft"], addon._state.current_skill), ("cut_sapphire", "Utilities"))

        # A row of a level the player lacks still ignores the click, and Add stays on the pick.
        self._click_row(dialog, "cut_dragonstone")
        self.assertEqual(self._count(dialog).suffix(), " Bowl (unfired)")

    def test_a_flat_list_row_without_inputs_reads_dim_and_takes_one_click(self):
        addon = self._plan_addon("flat", firemaking_level=1, current_firemaking="logs", inventory={"Oak logs": 1})
        save = addon._state.player_data
        dialog = self._menu(addon, "Firemaking")
        target_list = _find_list_with_user_role(dialog, "logs")
        self.assertIsInstance(target_list, QListWidget)
        rows = {target_list.item(i).data(Qt.ItemDataRole.UserRole): target_list.item(i) for i in range(target_list.count())}

        self.assertTrue(rows["logs"].flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertLess(rows["logs"].foreground().color().alpha(), 255)
        self.assertFalse(rows["oak_logs"].flags() & Qt.ItemFlag.ItemIsEnabled, "Oak logs need a higher level")

        save["current_firemaking"] = "oak_logs"
        QTest.mouseClick(target_list.viewport(), Qt.MouseButton.LeftButton, pos=target_list.visualItemRect(rows["logs"]).center())
        self._settle()
        self.assertEqual(target_list.selectedItems(), [rows["logs"]])
        self.assertEqual(self._count(dialog).suffix(), " Ashes")
        self.assertEqual(save["current_firemaking"], "oak_logs")
        self.assertFalse(self._header(dialog).isEnabled())

    def test_a_plank_conversion_without_logs_takes_one_click_and_start_utility_waits(self):
        addon = self._plan_addon("planks", inventory={})
        save = addon._state.player_data
        dialog = self._menu(addon, "Utilities")

        tree, row = self._click_row(dialog, "convert_logs_to_planks")

        self.assertEqual((tree.selectedItems(), tree.property("heldPick")), ([row], True))
        self.assertEqual(self._count(dialog).suffix(), " Plank")
        self.assertEqual((self._header(dialog).text(), self._header(dialog).isEnabled()), ("Start utility", False))
        self.assertEqual(save["current_utility"], "bankstanding")

        save["inventory"].update({"Logs": 2, "Coins": 200})
        self._show_supply_change(addon)
        self.assertEqual(self._count(dialog).value(), 2)
        self._start_ahead_of_queue(dialog)
        self.assertEqual(save["current_utility"], _PLANKS["utility_id"])

    def test_prayer_starts_a_pick_once_its_bones_exist_with_none_for_the_saved_target(self):
        addon = self._plan_addon("prayer", current_prayer="bury_bones", inventory={})
        save = addon._state.player_data
        addon._state.current_skill = "Prayer"
        addon._on_main_menu()
        dialog = self.opened[-1]
        self.addCleanup(dialog.close)
        dialog.show()
        dialog.resize(900, 560)
        self._settle()

        self._click_row(dialog, "bury_big_bones")
        self.assertEqual(save["current_prayer"], "bury_bones")

        save["inventory"]["Big bones"] = 3
        self._show_supply_change(addon)
        self._start_ahead_of_queue(dialog)
        self.assertEqual(save["current_prayer"], "bury_big_bones")


def _save(level, *, quests=True, **fields):
    save = default_player_data(c.ORE_DATA, c.ITEM_DEFINITIONS)
    save.update({key: level for key in save if key.endswith("_level")})
    save.update(inventory={}, house_owned=True, house_rooms_bought={room: True for room in house.ROOM_DATA}, **fields)
    if quests:
        save["quests"] = {
            quest: {"completed": True, "started": True, "progress": spec["stages"]} for quest, spec in c.QUEST_DATA.items()
        }
    return save


_RULES = c.QUEST_UNLOCK_RULES
# The real target-row builder of every skill panel; each takes the save and returns that panel's rows.
_PANELS = {
    "Smithing": lambda save: rows_of.smithing_target_rows(save, c.SMITHING_DATA, {}, "", _RULES),
    "Crafting": lambda save: rows_of.crafting_target_rows(save, c.CRAFTING_DATA, {}, _RULES),
    "Fletching": lambda save: rows_of.fletching_target_rows(save, c.FLETCHING_DATA, {}, _RULES),
    "Herblore": lambda save: rows_of.herblore_target_rows(save, c.HERBLORE_DATA, {}, _RULES),
    "Cooking": lambda save: rows_of.cooking_target_rows(save, c.COOKING_DATA, {}, "", _RULES),
    "Firemaking": lambda save: rows_of.firemaking_target_rows(save, c.FIREMAKING_DATA, {}, "", _RULES),
    "Fishing": lambda save: rows_of.fishing_target_rows(save, c.FISHING_DATA, {}, "", _RULES),
    "Hunter": lambda save: rows_of.hunter_target_rows(save, c.HUNTER_DATA, {}, "", _RULES),
    "Woodcutting": lambda save: rows_of.woodcutting_target_rows(save, c.TREE_DATA, {}, c.WOODCUTTING_AXE_DATA, "", _RULES),
    "Prayer": lambda save: rows_of.prayer_target_rows(save, c.PRAYER_DATA, {}, ""),
    "Runecrafting": lambda save: rows_of.runecrafting_target_rows(save, c.RUNECRAFTING_DATA, {}, c.RUNECRAFTING_POUCH_DATA, "", _RULES),
    "Magic": lambda save: rows_of.magic_target_rows(save, c.MAGIC_DATA, {}, "", c.ALCH_VALUES),
    "Construction": lambda save: rows_of.construction_target_rows(
        save, house.CONSTRUCTION_DATA, house.ROOM_DATA, house.SERVANT_DATA, house.NAIL_DATA, house.WORKBENCH_TIERS, {}, ""
    ),
    "Summoning": lambda save: rows_of.summoning_target_rows(save, summoning.SUMMONING_ACTIONS, summoning.SUMMONING_POUCHES_BY_ID, {}, ""),
    "Utilities": lambda save: tuple(
        row
        for row in rows_of.utility_activity_rows(
            save, c.UTILITY_ACTIVITY_DATA, {}, c.BIRD_NEST_OPEN_TABLES, c.DEFAULT_UTILITY_ACTIVITY, _RULES
        )
        if c.UTILITY_ACTIVITY_DATA[row.target_id].get("surface") == c.UTILITY_SURFACE_ID
    ),
}
_NO_INPUT_PANELS = {
    "Mining": lambda save: rows_of.mining_target_rows(save, c.ORE_DATA, {}, {}, c.MINING_PICKAXE_DATA, "", None, _RULES),
    "Thieving": lambda save: rows_of.thieving_target_rows(save, THIEVING_TARGETS, {}, ""),
    "Agility": lambda save: rows_of.agility_target_rows(save, AGILITY_TARGETS, {}, ""),
    "Combat": lambda save: rows_of.combat_target_rows(save, c.COMBAT_ENEMY_DATA, {}, c.EQUIPMENT_ITEM_DATA, ""),
}


class PlanRowCensusTest(unittest.TestCase):
    def _planned(self, panels, save):
        return {surface: plan_rows_pure(save, surface, build(save)) for surface, build in panels.items()}

    def test_every_skill_with_a_consumed_input_plans_and_no_other_skill_does(self):
        save = _save(99)
        for surface, rows in self._planned(_PANELS, save).items():
            with self.subTest(surface):
                self.assertTrue(any(row.plan_only for row in rows))
        for surface, rows in self._planned(_NO_INPUT_PANELS, save).items():
            with self.subTest(surface):
                self.assertFalse(any(row.plan_only for row in rows))

    def test_start_follows_the_row_in_every_skill(self):
        save = _save(99)
        for surface, rows in self._planned(_PANELS, save).items():
            for row in rows:
                with self.subTest(surface=surface, row=row.target_id):
                    self.assertEqual(pick_can_start_pure(save, surface, row.target_id), row.enabled)

    def test_a_level_lock_still_locks_the_row_in_every_skill(self):
        save = _save(1)
        for surface, rows in self._planned(_PANELS, save).items():
            levelled = [row for row in rows if any("level" in reason.lower() for reason in row.locked_reasons)]
            with self.subTest(surface):
                # Bones and Utilities have no level of their own to lack at level 1.
                if surface not in {"Prayer", "Utilities"}:
                    self.assertTrue(levelled)
                self.assertEqual([row.target_id for row in levelled if row.plan_only], [])

    def test_a_quest_lock_still_locks_the_row(self):
        done = {
            surface: {row.target_id: set(row.locked_reasons) for row in build(_save(99))} for surface, build in _PANELS.items()
        }
        questless = _save(99, quests=False)
        gated = 0
        for surface, rows in self._planned(_PANELS, questless).items():
            for row in rows:
                if set(row.locked_reasons) - done[surface][row.target_id]:
                    gated += 1
                    with self.subTest(surface=surface, row=row.target_id):
                        self.assertFalse(row.plan_only)
        self.assertGreater(gated, 100)

    def test_a_missing_tool_still_locks_the_row_until_the_tool_exists(self):
        save = _save(99)
        checked = 0
        for surface, rows in self._planned(_PANELS, save).items():
            if surface not in {"Smithing", "Crafting", "Fletching", "Cooking", "Hunter"}:
                continue
            for row in rows:
                spec = action_target_spec_pure({"kind": "skill", "skill": surface, "target": row.target_id})
                if without_belt_tools(save, {**(spec.get("required_items") or {}), **(spec.get("tools") or {})}):
                    checked += 1
                    with self.subTest(surface=surface, row=row.target_id):
                        self.assertFalse(row.plan_only)
        self.assertGreater(checked, 20)

        net = next(row for row in self._planned(_PANELS, {**save, "inventory": {"Butterfly net": 1}})["Hunter"] if row.target_id == "catch_ruby_harvest")
        self.assertTrue(net.plan_only)

    def test_altar_and_house_access_still_lock_the_row(self):
        save = _save(99)
        planned = self._planned(_PANELS, save)
        for surface, wall in (("Runecrafting", "altar access"), ("Construction", "Build the required workbench tier")):
            walled = [row for row in planned[surface] if wall in row.locked_reasons]
            with self.subTest(surface):
                self.assertTrue(walled)
                self.assertEqual([row.target_id for row in walled if row.plan_only], [])
        no_room = plan_rows_pure({**save, "house_rooms_bought": {}}, "Construction", _PANELS["Construction"]({**save, "house_rooms_bought": {}}))
        self.assertFalse(next(row for row in no_room if row.target_id == "oak_staircase").plan_only)


if __name__ == "__main__":
    unittest.main()
