import os
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    CRAFTING_DATA,
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.data.crystal_chest_data import (
    CRYSTAL_CHEST_REWARDS,
    CRYSTAL_CHEST_RING_IMPROVEMENT_CHANCE,
    CRYSTAL_CHEST_TOTAL_WEIGHT,
)
from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
from ankiscape.logic_pure.logic_pure import (
    apply_crafting_pure,
    apply_crystal_chest_pure,
    crystal_chest_reward_for_roll_pure,
    equip_item_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer


def _context(player_data, calls, random_values):
    rolls = iter(random_values)
    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: next(rolls),
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda _reason=None: calls.__setitem__("deactivated", True),
        award_skill_exp=lambda _key, amount: amount,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda *_args: None,
        check_achievements=lambda _data: None,
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: None,
        show_exp=lambda _amount: None,
        show_activity_gain=lambda text: calls["activity"].append(text),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


class CrystalChestTest(unittest.TestCase):
    def test_measured_table_item_identities_and_equippable_ring_are_live(self):
        self.assertEqual(sum(row.weight for row in CRYSTAL_CHEST_REWARDS), CRYSTAL_CHEST_TOTAL_WEIGHT)
        self.assertTrue(all(dict(row.outputs).get("Uncut dragonstone") == 1 for row in CRYSTAL_CHEST_REWARDS))
        self.assertEqual(dict(CRYSTAL_CHEST_REWARDS[2].outputs)["Steam rune"], 10)
        self.assertEqual(dict(CRYSTAL_CHEST_REWARDS[3].outputs)["Rune bar"], 3)
        self.assertGreater(
            CRYSTAL_CHEST_REWARDS[3].value_rank,
            CRYSTAL_CHEST_REWARDS[-1].value_rank,
        )

        definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        expected = {
            "Tooth half of a key": 985,
            "Loop half of a key": 987,
            "Crystal key": 989,
            "Uncut dragonstone": 1631,
            "Ring of wealth": 2572,
        }
        for item_name, item_id in expected.items():
            with self.subTest(item_name=item_name):
                definition = definitions[item_name]
                self.assertEqual(definition.source_item_id, item_id)
                self.assertFalse(definition.stackable)
                self.assertTrue(os.path.exists(definition.asset_path or ""))

        inventory, equipment, equipped = equip_item_pure(
            "Ring of wealth",
            {"Ring of wealth": 1},
            {},
            EQUIPMENT_DATA,
        )
        self.assertTrue(equipped)
        self.assertEqual(inventory["Ring of wealth"], 0)
        self.assertEqual(equipment["ring"], "Ring of wealth")
        self.assertEqual(GE_ITEM_CATALOG["Crystal key"]["guide_price"], 24_786)
        self.assertEqual(GE_ITEM_CATALOG["Crystal key"]["buy_limit"], 100)

    def test_key_combination_and_chest_boundaries_preserve_every_input(self):
        inventory, xp, combined = apply_crafting_pure(
            "combine_crystal_key",
            {"Tooth half of a key": 1, "Loop half of a key": 1},
            CRAFTING_DATA,
        )
        self.assertTrue(combined)
        self.assertEqual(xp, 0.0)
        self.assertEqual(
            inventory,
            {"Tooth half of a key": 0, "Loop half of a key": 0, "Crystal key": 1},
        )

        expected_rows = (
            (0.0, "spinach_roll"),
            (0.3969, "dragonstone_only"),
            (0.5641, "runes"),
            (1.0, "rune_platelegs"),
        )
        for roll, reward_id in expected_rows:
            with self.subTest(roll=roll):
                self.assertEqual(
                    crystal_chest_reward_for_roll_pure(CRYSTAL_CHEST_REWARDS, roll).id,
                    reward_id,
                )

        empty, ok, reward_id, outputs, improved = apply_crystal_chest_pure(
            {}, CRYSTAL_CHEST_REWARDS, 0.0
        )
        self.assertFalse(ok)
        self.assertEqual((empty, reward_id, outputs, improved), ({}, "", {}, False))

    def test_ring_of_wealth_placeholder_keeps_the_better_of_two_reward_rolls(self):
        inventory, ok, reward_id, outputs, improved = apply_crystal_chest_pure(
            {"Crystal key": 1},
            CRYSTAL_CHEST_REWARDS,
            0.4,
            ring_of_wealth=True,
            wealth_trigger_roll=0.0,
            wealth_reward_roll=1.0,
            wealth_improvement_chance=CRYSTAL_CHEST_RING_IMPROVEMENT_CHANCE,
        )
        self.assertTrue(ok)
        self.assertTrue(improved)
        self.assertEqual(reward_id, "rune_platelegs")
        self.assertEqual(outputs, {"Uncut dragonstone": 1, "Rune platelegs": 1})
        self.assertEqual(inventory["Crystal key"], 0)

    def test_runtime_consumes_one_key_records_outputs_and_reports_ring_improvement(self):
        calls = {"errors": [], "saves": 0, "activity": []}
        player_data = {
            "current_utility": "open_crystal_chest",
            "inventory": {"Crystal key": 1},
            "equipment": {"ring": "Ring of wealth"},
            "completed_achievements": [],
        }

        self.assertTrue(
            handle_utility_answer(
                _context(player_data, calls, (0.4, 0.0, 1.0))
            )
        )

        self.assertEqual(
            player_data["inventory"],
            {"Crystal key": 0, "Uncut dragonstone": 1, "Rune platelegs": 1},
        )
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertIn("Ring of Wealth improved the roll", calls["activity"][-1])
        telemetry = player_data["action_telemetry"]["actions"]["utility:open_crystal_chest"]
        self.assertEqual(
            telemetry["outputs"],
            {"Uncut dragonstone": 1, "Rune platelegs": 1},
        )

        plain_calls = {"errors": [], "saves": 0, "activity": []}
        plain_player = {
            "current_utility": "open_crystal_chest",
            "inventory": {"Crystal key": 1},
            "equipment": {},
            "completed_achievements": [],
        }
        self.assertTrue(
            handle_utility_answer(_context(plain_player, plain_calls, (0.4,)))
        )
        self.assertNotIn("Ring of Wealth improved", plain_calls["activity"][-1])

    def test_utility_contract_consumes_one_key_and_guarantees_a_dragonstone(self):
        spec = UTILITY_ACTIVITY_DATA["open_crystal_chest"]
        self.assertEqual(spec["requirements"], {"Crystal key": 1})
        self.assertEqual(spec["output_item"], "Uncut dragonstone")
        self.assertEqual(spec["batch_size"], 1)
        self.assertEqual(spec["surface"], "utilities")


if __name__ == "__main__":
    unittest.main()
