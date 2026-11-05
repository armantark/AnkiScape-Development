"""Queue planning spends earlier supplies once and reconciles edits before reviews."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.action_queue import action_queue_pure, apply_action_queue_command
from ankiscape.core.menu_action_queue import action_supply_limit_pure, queue_add_view_pure
from tests.action_queue.test_queue_reviews import QueueProfile

TIPS = {"kind": "skill", "skill": "Smithing", "target": "forge_bronze_arrowtips"}
ARROWS = {"kind": "skill", "skill": "Fletching", "target": "bronze_arrows"}


class LookAheadTest(unittest.TestCase):
    def _save(self, entries, **bank):
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

    def test_consumers_reserve_inputs_and_progress_only_promises_what_remains(self):
        save = self._save([(TIPS, 60), (ARROWS, 45)], **{"Bronze bar": 4, "Headless arrows": 90})
        self.assertEqual(action_supply_limit_pure(save, ARROWS), 15)
        save["action_queue"]["done"] = 30
        save["inventory"].update({"Bronze bar": 2, "Bronze arrowtips": 30})
        self.assertEqual(action_supply_limit_pure(save, ARROWS), 15)


class SupplyEditTest(QueueProfile):
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
        for _ in range(4):
            self._answer(addon)
            if not self._rows(addon):
                break
        self.assertEqual(addon._state.player_data["inventory"]["Bronze arrows"], 30)
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
