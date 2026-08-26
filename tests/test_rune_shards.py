import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    ITEM_DEFINITIONS,
    MINING_PICKAXE_DATA,
    ORE_DATA,
    QUEST_DATA,
    QUEST_UNLOCK_RULES,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.grind_source_data import grind_source_activities_as_dict
from ankiscape.logic.shop_logic import apply_shop_buy_pure, apply_shop_sell_pure
from ankiscape.logic_pure.logic_pure import (
    apply_mining_action_pure,
    apply_quest_progress_pure,
    apply_utility_activity_pure,
    best_mining_pickaxe_pure,
    mining_target_locked_reasons_pure,
    start_quest_pure,
)


class RuneShardChainTests(unittest.TestCase):
    def test_make_rune_shards_source_row_is_exact(self):
        self.assertEqual(
            grind_source_activities_as_dict(),
            {
                "make_rune_shards": {
                    "display_name": "Make rune shards",
                    "requirements": {"Rune essence": 1},
                    "material_options": {
                        "Rune essence": ("Rune essence", "Pure essence")
                    },
                    "required_item_options": (("Chisel", "Hammer"),),
                    "output_item": "Rune shards",
                    "output_qty": 1,
                    "batch_size": 1,
                    "group": "input_preparation",
                    "source": "https://runescape.wiki/w/Rune_shards?oldid=6407335",
                }
            },
        )

    def test_make_rune_shards_accepts_each_essence_and_tool_but_neither_missing(self):
        actual = []
        for essence, tool in (
            ("Rune essence", "Chisel"),
            ("Rune essence", "Hammer"),
            ("Pure essence", "Chisel"),
            ("Pure essence", "Hammer"),
            ("Rune essence", None),
            (None, "Chisel"),
        ):
            inventory = {}
            if essence:
                inventory[essence] = 1
            if tool:
                inventory[tool] = 1
            result, exp, ok, processed = apply_utility_activity_pure(
                "make_rune_shards", inventory, UTILITY_ACTIVITY_DATA
            )
            actual.append(
                (
                    essence,
                    tool,
                    ok,
                    exp,
                    processed,
                    result.get(essence, 0) if essence else 0,
                    result.get(tool, 0) if tool else 0,
                    result.get("Rune shards", 0),
                    result is inventory,
                )
            )

        self.assertEqual(
            actual,
            [
                ("Rune essence", "Chisel", True, 0, 1, 0, 1, 1, False),
                ("Rune essence", "Hammer", True, 0, 1, 0, 1, 1, False),
                ("Pure essence", "Chisel", True, 0, 1, 0, 1, 1, False),
                ("Pure essence", "Hammer", True, 0, 1, 0, 1, 1, False),
                ("Rune essence", None, False, 0, 0, 1, 0, 0, True),
                (None, "Chisel", False, 0, 0, 0, 1, 0, True),
            ],
        )

    def test_fresh_player_reaches_rune_dust_through_real_kernels(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        pickaxe = best_mining_pickaxe_pure(
            player["mining_level"],
            player["inventory"],
            player["toolbelt"],
            MINING_PICKAXE_DATA,
        )
        initial_essence_locks = mining_target_locked_reasons_pure(
            player,
            "rune_essence",
            ORE_DATA,
            MINING_PICKAXE_DATA,
            QUEST_UNLOCK_RULES,
        )

        clay_exp = 0.0
        for _ in range(27):
            inventory, exp, ok, output_item, _gem, _extra = apply_mining_action_pure(
                "clay",
                player["inventory"],
                ORE_DATA,
                player["mining_level"],
                pickaxe,
                0.0,
                0.0,
                1.0,
                0.0,
            )
            if not ok or output_item != "Clay":
                self.fail("fresh player failed to mine Clay")
            player["inventory"] = inventory
            clay_exp += exp

        player, clay_sale = apply_shop_sell_pure(
            player, "general_store", "Clay", 27
        )
        tool_purchases = []
        for row_id in ("general_store:8:1755", "general_store:9:2347"):
            player, purchase = apply_shop_buy_pure(
                player, "general_store", row_id, 1
            )
            tool_purchases.append(
                (purchase["allowed"], purchase["item_name"], purchase["total_price"])
            )

        player, started = start_quest_pure(player, "rune_mysteries", QUEST_DATA)
        quest_progress = []
        for _ in range(5):
            player, progressed, _completed_now = apply_quest_progress_pure(
                player, "rune_mysteries", QUEST_DATA
            )
            if not progressed:
                self.fail("Rune Mysteries stalled before completion")
            quest_progress.append(player["quests"]["rune_mysteries"]["progress"])

        essence_locks = mining_target_locked_reasons_pure(
            player,
            "rune_essence",
            ORE_DATA,
            MINING_PICKAXE_DATA,
            QUEST_UNLOCK_RULES,
        )
        inventory, essence_exp, essence_ok, essence_item, _gem, _extra = (
            apply_mining_action_pure(
                "rune_essence",
                player["inventory"],
                ORE_DATA,
                player["mining_level"],
                pickaxe,
                0.0,
                0.0,
                1.0,
                0.0,
            )
        )
        player["inventory"] = inventory
        inventory, make_exp, made, made_count = apply_utility_activity_pure(
            "make_rune_shards", player["inventory"], UTILITY_ACTIVITY_DATA
        )
        player["inventory"] = inventory
        inventory, grind_exp, ground, ground_count = apply_utility_activity_pure(
            "grind_rune_shards", player["inventory"], UTILITY_ACTIVITY_DATA
        )
        player["inventory"] = inventory

        self.assertEqual(
            {
                "clay": (player["inventory"]["Clay"], clay_exp),
                "sale": (
                    clay_sale["allowed"],
                    clay_sale["quantity"],
                    clay_sale["total_price"],
                ),
                "purchases": tool_purchases,
                "tools": (
                    player["inventory"]["Chisel"],
                    player["inventory"]["Hammer"],
                    player["inventory"]["Coins"],
                ),
                "quest_started": started,
                "quest_progress": quest_progress,
                "quest_actions": tuple(
                    player["quest_stage_actions"]["rune_mysteries"]
                ),
                "quest_completed": player["quests"]["rune_mysteries"]["completed"],
                "essence_locks": (initial_essence_locks, essence_locks),
                "essence": (essence_ok, essence_item, essence_exp),
                "make": (made, make_exp, made_count),
                "grind": (ground, grind_exp, ground_count),
                "chain_inventory": (
                    player["inventory"]["Rune essence"],
                    player["inventory"]["Rune shards"],
                    player["inventory"]["Rune dust"],
                ),
            },
            {
                "clay": (0, 135.0),
                "sale": (True, 27, 27),
                "purchases": [
                    (True, "Chisel", 14),
                    (True, "Hammer", 13),
                ],
                "tools": (1, 1, 0),
                "quest_started": True,
                "quest_progress": [2, 3, 4, 5, 6],
                "quest_actions": (
                    "Deliver the strange talisman to Sedridor",
                    "Deliver Sedridor's package to Aubury",
                    "Return Aubury's research notes to Sedridor",
                ),
                "quest_completed": True,
                "essence_locks": (("Rune Mysteries",), ()),
                "essence": (True, "Rune essence", 5.0),
                "make": (True, 0, 1),
                "grind": (True, 0, 1),
                "chain_inventory": (0, 0, 1),
            },
        )


if __name__ == "__main__":
    unittest.main()
