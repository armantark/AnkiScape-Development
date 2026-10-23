import copy
import unittest

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core.constants import (
    INCIDENTAL_GEM_DROP_TABLE,
    MINING_PICKAXE_DATA,
    ORE_DATA,
)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure_equipment import attach_tool_to_toolbelt_pure
from ankiscape.logic_pure.logic_pure_gathering import (
    apply_mining_action_pure,
    calculate_mining_success_probability_pure,
)
from ankiscape.runtime.runtime_actions_gathering import handle_mining_answer
from tests.test_runtime_actions import _context


class GildedPickaxeRequirementsTests(unittest.TestCase):
    def test_mining_handler_enforces_gilded_tool_boundaries(self):
        for tool_id, lower, accepted in (
            ("gilded_steel_pickaxe", 5, 6),
            ("gilded_adamant_pickaxe", 30, 31),
            ("gilded_rune_pickaxe", 40, 41),
        ):
            for level in (lower, accepted):
                with self.subTest(tool=tool_id, level=level):
                    player = default_player_data(ORE_DATA)
                    player.update(current_ore="copper", mining_level=level)
                    # Isolate ordinary ore output from strange-rock replacement.
                    player["shattered_heart"]["auto_discard"] = True
                    item_name = MINING_PICKAXE_DATA[tool_id]["display_name"]
                    player["inventory"] = {item_name: 1}
                    player["toolbelt"]["mining"] = []
                    inventory, toolbelt, attached = attach_tool_to_toolbelt_pure(
                        item_name, player["inventory"], player["toolbelt"],
                        MINING_PICKAXE_DATA, {},
                    )
                    self.assertTrue(attached)
                    self.assertEqual(inventory, {})
                    self.assertEqual(toolbelt["mining"], [tool_id])
                    player.update(inventory=inventory, toolbelt=toolbelt)
                    before_inventory = dict(inventory)
                    before_toolbelt = copy.deepcopy(toolbelt)
                    before_xp = player["mining_exp"]
                    calls = {"xp": [], "saves": 0, "errors": []}
                    ctx = _context(player, calls, (0.0, 0.5, 0.999999, 0.0))

                    if level == lower:
                        self.assertFalse(handle_mining_answer(ctx))
                        self.assertEqual(calls["errors"], [(
                            "Missing pickaxe",
                            "You need a usable pickaxe to train Mining. "
                            "Mining has been switched off.",
                        )])
                        self.assertTrue(calls["deactivated"])
                        self.assertEqual(calls["xp"], [])
                        self.assertEqual(player["mining_exp"], before_xp)
                        self.assertEqual(player["inventory"], before_inventory)
                        self.assertEqual(player["toolbelt"], before_toolbelt)

                        player["inventory"]["Bronze pickaxe"] = 1
                        inventory, toolbelt, attached = attach_tool_to_toolbelt_pure(
                            "Bronze pickaxe", player["inventory"], player["toolbelt"],
                            MINING_PICKAXE_DATA, {},
                        )
                        self.assertTrue(attached)
                        self.assertEqual(toolbelt["mining"], [tool_id, "bronze_pickaxe"])
                        player.update(inventory=inventory, toolbelt=toolbelt)
                        before_toolbelt = copy.deepcopy(toolbelt)
                        calls = {"xp": [], "saves": 0, "errors": []}
                        ctx = _context(player, calls, (0.0, 0.5, 0.999999, 0.0))

                    self.assertTrue(handle_mining_answer(ctx))
                    self.assertEqual(player["inventory"], {"Copper ore": 1})
                    self.assertEqual(player["mining_exp"] - before_xp, 17.5)
                    self.assertEqual(calls["xp"], [17.5])
                    self.assertEqual(calls["errors"], [])
                    self.assertFalse(calls.get("deactivated", False))
                    self.assertEqual(player["toolbelt"], before_toolbelt)

    def test_corrected_gilded_tools_match_plain_mining_results(self):
        for plain_id, gilded_id, level in (
            ("steel_pickaxe", "gilded_steel_pickaxe", 6),
            ("adamant_pickaxe", "gilded_adamant_pickaxe", 31),
            ("rune_pickaxe", "gilded_rune_pickaxe", 41),
        ):
            plain = MINING_PICKAXE_DATA[plain_id]
            gilded = MINING_PICKAXE_DATA[gilded_id]
            with self.subTest(tool=gilded_id):
                self.assertEqual(
                    calculate_mining_success_probability_pure(level, ORE_DATA["copper"], plain),
                    calculate_mining_success_probability_pure(level, ORE_DATA["copper"], gilded),
                )
            for action_draw in (0.0, 0.99):
                with self.subTest(tool=gilded_id, action_draw=action_draw):
                    inventory = {"Copper ore": 2, "Coins": 100}
                    results = [
                        apply_mining_action_pure(
                            "copper", dict(inventory), ORE_DATA, level, spec,
                            action_draw, 0.5, 0.999999, 0.0,
                            INCIDENTAL_GEM_DROP_TABLE,
                        )
                        for spec in (plain, gilded)
                    ]
                    self.assertEqual(results[0], results[1])
                    expected = (
                        ({"Copper ore": 3, "Coins": 100}, 17.5, True, "Copper ore", None, None)
                        if action_draw == 0.0
                        else (inventory, 0, False, None, None, None)
                    )
                    self.assertEqual(results[0], expected)


if __name__ == "__main__":
    unittest.main()
