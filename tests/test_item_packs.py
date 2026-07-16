import unittest

from logic_pure import apply_item_pack_open_pure
from pack_data import ITEM_PACK_DATA
from shop_data import SHOP_DATA


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


if __name__ == "__main__":
    unittest.main()
