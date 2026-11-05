"""Queue planning spends earlier supplies once and reconciles edits before reviews."""

import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.action_products import action_target_spec_pure
from ankiscape.core.action_queue import action_queue_pure, apply_action_queue_command
from ankiscape.core.menu_action_queue import action_supply_limit_pure, queue_add_view_pure
from tests.action_queue.test_queue_reviews import QueueProfile

TIPS = {"kind": "skill", "skill": "Smithing", "target": "forge_bronze_arrowtips"}
ARROWS = {"kind": "skill", "skill": "Fletching", "target": "bronze_arrows"}
ESSENCE = {"kind": "skill", "skill": "Mining", "target": "rune_essence"}
AIR = {"kind": "skill", "skill": "Runecrafting", "target": "craft_air_runes"}
NATURE = {"kind": "skill", "skill": "Runecrafting", "target": "craft_nature_runes"}
SUPERHEAT = {"kind": "skill", "skill": "Magic", "target": "superheat_iron_bar"}


class LookAheadTest(unittest.TestCase):
    def _save(self, entries, **bank):
        for action, _count in entries:
            self.assertIsNotNone(action_target_spec_pure(action), action)
        return {"fletching_level": 10, "smithing_level": 40, "inventory": bank,
                "action_queue": {"entries": [{"action": action, "count": count} for action, count in entries]}}

    def test_partial_supply_limits_both_inputs_and_no_supply_refuses(self):
        for entries, bank, limit in (
            ([(TIPS, 60)], {"Bronze bar": 4, "Headless arrows": 35}, 30),
            ([(TIPS, 60)], {"Bronze bar": 4, "Headless arrows": 14}, 0),
            ([(TIPS, 60)], {"Headless arrows": 60}, 0),
            ([], {"Headless arrows": 60}, 0),
        ):
            with self.subTest(entries=entries, bank=bank):
                save = self._save(entries, **bank)
                self.assertEqual(action_supply_limit_pure(save, ARROWS), limit)
                self.assertEqual(queue_add_view_pure(save, ARROWS)["enabled"], bool(limit))

    def test_one_queued_superheat_reserves_its_only_nature_rune(self):
        save = self._save([(SUPERHEAT, 1)], **{"Iron ore": 10, "Fire rune": 40, "Nature rune": 1})
        save["magic_level"] = 43
        self.assertEqual(action_supply_limit_pure(save, SUPERHEAT), 0)
        self.assertFalse(queue_add_view_pure(save, SUPERHEAT)["enabled"])
        save["inventory"]["Nature rune"] = 2
        self.assertEqual(action_supply_limit_pure(save, SUPERHEAT), 1)
        save["inventory"].update({"Staff of fire": 1, "Fire rune": 0})
        self.assertEqual(action_supply_limit_pure(save, SUPERHEAT), 1)

    def test_random_gems_and_mixed_fish_do_not_promise_each_possible_item(self):
        cases = (
            ({"kind": "skill", "skill": "Mining", "target": "gem_rocks"},
             {"kind": "skill", "skill": "Crafting", "target": "cut_sapphire"}),
            ({"kind": "skill", "skill": "Fishing", "target": "catch_shrimp_anchovies"},
             {"kind": "skill", "skill": "Cooking", "target": "cook_shrimps"}),
        )
        for producer, consumer in cases:
            with self.subTest(producer=producer):
                save = self._save([(producer, 10)])
                save.update(mining_level=40, fishing_level=40, crafting_level=40, cooking_level=40)
                self.assertEqual(action_supply_limit_pure(save, consumer), 0)
                self.assertFalse(queue_add_view_pure(save, consumer)["enabled"])

    def test_a_single_eligible_fish_and_consumed_bait_remain_plannable(self):
        fishing = {"kind": "skill", "skill": "Fishing", "target": "catch_shrimp_anchovies"}
        cooking = {"kind": "skill", "skill": "Cooking", "target": "cook_shrimps"}
        save = self._save([(fishing, 10)])
        save.update(fishing_level=1, cooking_level=1)
        self.assertEqual(action_supply_limit_pure(save, cooking), 10)
        pike = {"kind": "skill", "skill": "Fishing", "target": "catch_pike"}
        save = self._save([(pike, 5)], **{"Fishing bait": 7})
        save["fishing_level"] = 40
        self.assertEqual(action_supply_limit_pure(save, pike), 2)

    def test_a_spell_batch_counts_all_products_and_reserves_only_one_cast(self):
        kit = {"kind": "skill", "skill": "Magic", "target": "hunter_kit"}
        save = self._save([], **{"Astral rune": 4, "Earth rune": 4})
        self.assertEqual(action_supply_limit_pure(save, kit), 14)
        save["action_queue"]["entries"] = [{"action": kit, "count": 1}]
        self.assertEqual(action_supply_limit_pure(save, kit), 7)

    def test_consumers_reserve_inputs_and_progress_only_promises_what_remains(self):
        save = self._save([(TIPS, 60), (ARROWS, 45)], **{"Bronze bar": 4, "Headless arrows": 90})
        self.assertEqual(action_supply_limit_pure(save, ARROWS), 15)
        save["action_queue"]["done"] = 30
        save["inventory"].update({"Bronze bar": 2, "Bronze arrowtips": 30})
        self.assertEqual(action_supply_limit_pure(save, ARROWS), 15)


class SupplyEditTest(QueueProfile):
    def test_ten_essence_fund_ten_air_runes_and_the_queue_finishes_without_a_shortage(self):
        addon = self._queue_addon("ankiscape_supply_essence", (ESSENCE, 10), runecrafting_level=1,
                                  inventory={"Air talisman": 1}, quests={"rune_mysteries": {"completed": True}})
        save = addon._state.player_data
        self.assertEqual(action_supply_limit_pure(save, AIR), 10)
        self.assertEqual(queue_add_view_pure(save, AIR)["maximum"], 10)
        from ankiscape.core.action_queue import add_to_action_queue
        self.assertEqual(add_to_action_queue(addon, AIR, 10), "")
        with patch.object(addon.random, "random", return_value=0.5):
            for _ in range(10):
                if not self._rows(addon):
                    break
                self._answer(addon)
        self.assertEqual(self._rows(addon), [])
        self.assertEqual(save["inventory"]["Air rune"], 10)
        self.assertFalse(any("stopped" in line for line in self._log(addon)))
        self.assertEqual(self.errors, [])

    def test_removing_nature_producer_stops_the_second_unfunded_cast_at_the_edit(self):
        addon = self._queue_addon("ankiscape_supply_spell_edit", (NATURE, 1), (SUPERHEAT, 1), (SUPERHEAT, 1),
                                  magic_level=43, runecrafting_level=44,
                                  quests={"rune_mysteries": {"completed": True}},
                                  inventory={"Nature talisman": 1, "Pure essence": 1,
                                             "Iron ore": 10, "Fire rune": 40, "Nature rune": 1})
        entry = action_queue_pure(addon._state.player_data)["entries"][0]
        self.assertTrue(apply_action_queue_command(addon, "remove", {"position": 0, "entry": entry})["ok"])
        self.assertEqual(action_queue_pure(addon._state.player_data)["entries"], [{"action": SUPERHEAT, "count": 1}])
        self.assertTrue(any("Superheat Iron bar stopped" in line and "Nature rune x1" in line for line in self._log(addon)))
        for _ in range(4):
            if not self._rows(addon):
                break
            self._answer(addon)
        self.assertEqual(addon._state.player_data["inventory"]["Iron bar"], 1)
        self.assertEqual(self.errors, [])

    def test_a_whole_batch_funds_the_next_row_even_when_the_entry_count_is_smaller(self):
        shafts = {"kind": "skill", "skill": "Fletching", "target": "arrow_shafts"}
        headless = {"kind": "skill", "skill": "Fletching", "target": "headless_arrows"}
        addon = self._queue_addon("ankiscape_supply_whole_lot", (shafts, 1), (headless, 15),
                                  inventory={"Logs": 1, "Feather": 15})
        for _ in range(4):
            self._answer(addon)
            if not self._rows(addon):
                break
        bank = addon._state.player_data["inventory"]
        self.assertEqual((bank["Headless arrows"], bank.get("Arrow shafts", 0)), (15, 0))
        self.assertFalse(any("stopped" in line for line in self._log(addon)))

    def test_removing_a_producer_keeps_only_the_count_still_funded(self):
        addon = self._queue_addon("ankiscape_supply_partial_edit", (TIPS, 30), (ARROWS, 60),
                                  fletching_level=10, inventory={"Bronze bar": 2, "Headless arrows": 60, "Bronze arrowtips": 30})
        entry = action_queue_pure(addon._state.player_data)["entries"][0]
        self.assertTrue(apply_action_queue_command(addon, "remove", {"position": 0, "entry": entry})["ok"])
        self.assertEqual(action_queue_pure(addon._state.player_data)["entries"], [{"action": ARROWS, "count": 30}])
        with patch.object(addon.random, "random", return_value=0.5):
            for _ in range(4):
                self._answer(addon)
                if not self._rows(addon):
                    break
        self.assertEqual(addon._state.player_data["inventory"]["Bronze arrows"], 30)
        self.assertEqual(self._rows(addon), [])
        self.assertFalse(any("stopped" in line for line in self._log(addon)))

    def test_removing_or_moving_the_producer_stops_the_unfunded_row_at_the_edit(self):
        for command, payload in (("remove", {"position": 0}), ("move", {"position": 0, "new_index": 1})):
            with self.subTest(command=command):
                addon = self._queue_addon("ankiscape_supply_edit_" + command, (TIPS, 60), (ARROWS, 60),
                                          fletching_level=10, inventory={"Bronze bar": 4, "Headless arrows": 60})
                if command == "remove":
                    payload["entry"] = action_queue_pure(addon._state.player_data)["entries"][0]
                result = apply_action_queue_command(addon, command, payload)
                self.assertTrue(result["ok"])
                entries = action_queue_pure(addon._state.player_data)["entries"]
                self.assertFalse(any(entry["action"] == ARROWS for entry in entries))
                self.assertTrue(any("Fletching: Bronze arrows stopped" in line for line in self._log(addon)))
                self.assertEqual(self.errors, [])
