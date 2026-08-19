import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic_pure.logic_pure import (
    apply_impling_jar_open_pure,
    apply_item_pack_open_pure,
)
from ankiscape.data.impling_jar_data import IMPLING_JAR_DATA
from ankiscape.data.pack_data import ITEM_PACK_DATA
from ankiscape.data.shop_data import SHOP_DATA


class ItemPackTests(unittest.TestCase):
    def test_every_live_shop_pack_has_exact_sourced_contents(self):
        sold_pack_names = {
            row["item_name"]
            for shop in SHOP_DATA.values()
            for row in shop.get("stock", ())
            if row.get("disposition") == "live" and row.get("item_name", "").endswith(" pack")
        }
        self.assertEqual(sold_pack_names, set(ITEM_PACK_DATA))
        self.assertEqual(
            {name: (spec["content_item"], spec["content_quantity"]) for name, spec in ITEM_PACK_DATA.items()},
            {
                "Vial pack": ("Vial", 50),
                "Vial of water pack": ("Vial of water", 50),
                "Eye of newt pack": ("Eye of newt", 50),
                "Empty sack pack": ("Empty sack", 50),
                "Basket pack": ("Basket", 50),
                "Juju vial pack": ("Juju vial", 50),
                "Raw bird meat pack": ("Raw bird meat", 50),
                "Spirit shard pack": ("Spirit shards", 5000),
            },
        )

    def test_open_one_and_open_all_preserve_exact_quantities(self):
        inventory = {"Vial pack": 3, "Vial": 2}

        opened_one, result = apply_item_pack_open_pure(inventory, "Vial pack", open_all=False)
        self.assertTrue(result["allowed"])
        self.assertEqual(opened_one, {"Vial pack": 2, "Vial": 52})
        self.assertEqual(result["packs_opened"], 1)

        opened_all, result = apply_item_pack_open_pure(inventory, "Vial pack", open_all=True)
        self.assertTrue(result["allowed"])
        self.assertEqual(opened_all, {"Vial": 152})
        self.assertEqual(result["packs_opened"], 3)

    def test_unknown_or_missing_pack_is_a_noop(self):
        inventory = {"Vial pack": 0, "Coins": 5}
        for item_name in ("Vial pack", "Mystery pack"):
            with self.subTest(item_name=item_name):
                updated, result = apply_item_pack_open_pure(inventory, item_name, open_all=True)
                self.assertFalse(result["allowed"])
                self.assertEqual(updated, inventory)
                self.assertIsNot(updated, inventory)

    def test_dragon_impling_jar_preserves_sourced_reward_probabilities(self):
        rewards = IMPLING_JAR_DATA["Dragon impling jar"]
        by_item = {reward.item: reward for reward in rewards}
        self.assertEqual(sum(reward.weight for reward in rewards), 6_700_000)
        self.assertEqual(
            (by_item["Dragon dart tip"].minimum, by_item["Dragon dart tip"].maximum),
            (105, 350),
        )
        self.assertEqual(
            (by_item["Dragon arrowtips"].minimum, by_item["Dragon arrowtips"].maximum),
            (100, 500),
        )
        self.assertEqual(by_item["Dragon dart tip"].weight, 803_531)
        self.assertEqual(by_item["Dragon arrowtips"].weight, 803_531)
        self.assertEqual(by_item["Dragon bolt tips"].weight, 803_531)
        self.assertEqual(by_item["Snapdragon seed"].weight, 25_000)
        self.assertEqual(by_item["Summer pie"].weight, 25_000)
        self.assertEqual(by_item["Death tiara"].weight, 12_500)
        self.assertEqual(by_item[""].weight, 2_007_447)
        self.assertNotIn("Mystic robe bottom (blue)", by_item)
        self.assertNotIn("Dragon arrow", by_item)
        self.assertNotIn("Dragon dart", by_item)

    def test_dragon_impling_jar_loots_component_quantity_boundaries(self):
        original = {"Dragon impling jar": 2, "Dragon dart tip": 4}
        rolls = iter((2_700_000 / 6_700_000, 0.999999999))
        updated, result = apply_impling_jar_open_pure(
            original,
            "Dragon impling jar",
            rng=lambda: next(rolls),
        )
        self.assertEqual(original, {"Dragon impling jar": 2, "Dragon dart tip": 4})
        self.assertEqual(updated, {"Dragon impling jar": 1, "Dragon dart tip": 354})
        self.assertEqual(result["reward_item"], "Dragon dart tip")
        self.assertEqual(result["reward_quantity"], 350)

        rolls = iter((3_500_000 / 6_700_000, 0.0))
        updated, result = apply_impling_jar_open_pure(
            {"Dragon impling jar": 1},
            "Dragon impling jar",
            rng=lambda: next(rolls),
        )
        self.assertEqual(updated, {"Dragon arrowtips": 100})
        self.assertEqual(result["reward_item"], "Dragon arrowtips")

    def test_dragon_impling_jar_can_resolve_to_an_unregistered_reward(self):
        updated, result = apply_impling_jar_open_pure(
            {"Dragon impling jar": 1},
            "Dragon impling jar",
            rng=lambda: 0.999999999,
        )
        self.assertEqual(updated, {})
        self.assertEqual(result["reward_item"], "")
        self.assertEqual(result["reward_quantity"], 0)

    def test_impling_jar_bad_rows_are_isolated_from_valid_rewards(self):
        rewards = IMPLING_JAR_DATA["Dragon impling jar"]
        mutated = rewards[0].__class__("Broken reward", 5, 1, 99_999)
        fallback = rewards[0].__class__("Dragon arrowtips", 100, 500, 1)
        IMPLING_JAR_DATA["Dragon impling jar"] = (mutated, fallback)
        self.addCleanup(IMPLING_JAR_DATA.__setitem__, "Dragon impling jar", rewards)

        updated, result = apply_impling_jar_open_pure(
            {"Dragon impling jar": 1},
            "Dragon impling jar",
            rng=lambda: 0.0,
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(updated, {"Dragon arrowtips": 100})


if __name__ == "__main__":
    unittest.main()
