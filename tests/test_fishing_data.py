import unittest

from fishing_data import (
    DEFERRED_FISHING_CONTENT,
    FISHING_BAIT_SHOP_SOURCE_PATH,
    FISHING_METHODS,
    FISHING_METHODS_BY_ID,
    FISHING_SPOT_SOURCE_PATH,
    FISHING_TOOL_SOURCE_PATH,
    FISHING_FISH,
    FISH_BY_ID,
    deferred_fishing_content_as_dict,
    fishing_extra_items_as_dict,
    fishing_fish_as_dict,
    fishing_methods_as_dict,
    fishing_output_items,
)


class TestFishingData(unittest.TestCase):
    def test_source_fish_rows_are_exact(self):
        rows = [
            (
                fish.id,
                fish.output_item,
                fish.source_item_id,
                fish.level,
                fish.min_chance,
                fish.max_chance,
                fish.base_exp,
                fish.strength_level,
                fish.agility_level,
            )
            for fish in FISHING_FISH
        ]

        self.assertEqual(
            rows,
            [
                ("crayfish", "Raw crayfish", 13435, 1, 58, 256, 10.0, None, None),
                ("shrimp", "Raw shrimps", 317, 1, 48, 256, 10.0, None, None),
                ("sardine", "Raw sardine", 327, 5, 32, 192, 20.0, None, None),
                ("herring", "Raw herring", 345, 10, 24, 128, 30.0, None, None),
                ("anchovies", "Raw anchovies", 321, 15, 24, 128, 40.0, None, None),
                ("mackerel", "Raw mackerel", 353, 16, 5, 65, 20.0, None, None),
                ("cod", "Raw cod", 341, 23, 4, 55, 45.0, None, None),
                ("bass", "Raw bass", 363, 46, 3, 40, 100.0, None, None),
                ("trout", "Raw trout", 335, 20, 32, 192, 50.0, None, None),
                ("pike", "Raw pike", 349, 25, 16, 96, 60.0, None, None),
                ("salmon", "Raw salmon", 331, 30, 16, 96, 70.0, None, None),
                ("tuna", "Raw tuna", 359, 35, 4, 48, 80.0, None, None),
                ("swordfish", "Raw swordfish", 371, 50, 4, 48, 100.0, None, None),
                ("lobster", "Raw lobster", 377, 40, 6, 95, 90.0, None, None),
                ("shark", "Raw shark", 383, 76, 3, 40, 110.0, None, None),
                ("leaping_trout", "Leaping trout", 11328, 48, 20, 40, 50.0, 15, 15),
                ("leaping_salmon", "Leaping salmon", 11330, 58, 30, 75, 70.0, 30, 30),
                ("leaping_sturgeon", "Leaping sturgeon", 11332, 70, 25, 70, 90.0, 45, 45),
                ("raw_karambwan", "Raw karambwan", 3142, 65, 5, 160, 50.0, None, None),
                ("rainbow_fish", "Raw rainbow fish", 10138, 38, 8, 64, 80.0, None, None),
                ("monkfish", "Raw monkfish", 7944, 62, 48, 90, 120.0, None, None),
                ("karambwanji", "Raw karambwanji", 3150, 5, 100, 256, 5.0, None, None),
                ("slimy_eel", "Slimy eel", 3379, 38, 10, 80, 65.0, None, None),
                ("cave_eel", "Raw cave eel", 5001, 28, 10, 80, 80.0, None, None),
                ("lava_eel", "Raw lava eel", 2148, 53, 16, 96, 60.0, None, None),
                ("frog_spawn", "Frog spawn", 5004, 33, 16, 96, 75.0, None, None),
                ("cavefish", "Raw cavefish", 15264, 85, 5, 17, 300.0, None, None),
                ("rocktail", "Raw rocktail", 15270, 90, 5, 15, 380.0, None, None),
            ],
        )
        self.assertEqual(set(FISH_BY_ID), {row[0] for row in rows})

    def test_methods_are_unique_bound_fishing_spot_behaviors(self):
        rows = [
            (method.id, method.display_name, method.source_tool, method.fish_ids, method.bait_items, method.source_spots)
            for method in FISHING_METHODS
        ]

        self.assertEqual(
            rows,
            [
                ("catch_crayfish", "Catch crayfish", "CRAYFISH_CAGE", ("crayfish",), (), ("CRAYFISH_CAGE",)),
                ("catch_shrimp_anchovies", "Catch shrimp/anchovies", "SMALL_FISHING_NET", ("anchovies", "shrimp"), (), ("NET_AND_BAIT",)),
                ("catch_sardine_herring", "Catch sardine/herring", "FISHING_ROD_SEA", ("sardine", "herring"), ("Fishing bait",), ("NET_AND_BAIT",)),
                ("catch_pike", "Catch pike", "FISHING_ROD_RIVER", ("pike",), ("Fishing bait",), ("LURE_AND_BAIT",)),
                ("catch_trout_salmon", "Catch trout/salmon", "FLY_FISHING_ROD", ("salmon", "trout"), ("Feather",), ("LURE_AND_BAIT",)),
                ("catch_mackerel_cod_bass", "Catch mackerel/cod/bass", "BIG_FISHING_NET", ("mackerel", "cod", "bass"), (), ("NET_HARPOON",)),
                ("catch_sharks", "Catch sharks", "HARPOON_SHARK", ("shark",), (), ("NET_HARPOON",)),
                ("catch_lobsters", "Catch lobsters", "LOBSTER_POT", ("lobster",), (), ("CAGE_AND_HARPOON",)),
                ("catch_tuna_swordfish", "Catch tuna/swordfish", "HARPOON_NON_SHARK", ("tuna", "swordfish"), (), ("CAGE_AND_HARPOON", "HAPOON_FISHING")),
                ("catch_cavefish", "Catch cavefish", "FISHING_ROD_CAVEFISH", ("cavefish",), ("Fishing bait",), ("FISHING_ROD_CAVEFISH",)),
                ("catch_rocktail", "Catch rocktail", "FISHING_ROD_ROCKTAIL", ("rocktail",), ("Living minerals",), ("FISHING_ROD_ROCKTAIL",)),
                ("catch_monkfish", "Catch monkfish", "MONKFISH_NET", ("monkfish",), (), ("SMALL_FISHING_NET_MONKFISH",)),
                ("catch_karambwan", "Catch karambwan", "KARAMBWAN_VESSEL", ("raw_karambwan",), (), ("KARAMBWAN",)),
                ("catch_slimy_eel", "Catch slimy eel", "MORTMYRE_ROD", ("slimy_eel",), ("Fishing bait",), ("MORTMYRE_ROD",)),
                ("catch_leaping_fish", "Catch leaping fish", "BARBARIAN_ROD", ("leaping_trout", "leaping_salmon", "leaping_sturgeon"), ("Feather", "Fishing bait", "Fish offcuts", "Roe", "Caviar"), ("BARBARIAN_ROD",)),
            ],
        )
        self.assertEqual(set(FISHING_METHODS_BY_ID), {row[0] for row in rows})

    def test_methods_export_runtime_shape(self):
        data = fishing_methods_as_dict()

        self.assertEqual(data["catch_crayfish"]["level"], 1)
        self.assertEqual(data["catch_crayfish"]["fish"][0]["output_item"], "Raw crayfish")
        self.assertEqual(data["catch_shrimp_anchovies"]["fish_ids"], ("anchovies", "shrimp"))
        self.assertEqual(data["catch_sardine_herring"]["requirements"], {"Fishing bait": 1})
        self.assertEqual(data["catch_leaping_fish"]["bait_options"], ("Feather", "Fishing bait", "Fish offcuts", "Roe", "Caviar"))
        self.assertEqual(data["catch_leaping_fish"]["fish"][0]["strength_level"], 15)

    def test_output_items_and_extra_materials_are_registered(self):
        self.assertIn("Raw crayfish", fishing_output_items())
        self.assertIn("Raw shark", fishing_output_items())
        self.assertIn("Leaping sturgeon", fishing_output_items())
        self.assertNotIn("Raw rainbow fish", fishing_output_items())

        extra = fishing_extra_items_as_dict()
        self.assertEqual(extra["Fishing bait"]["item_id"], 313)
        self.assertEqual(extra["Living minerals"]["item_id"], 15263)
        self.assertIn("lumbridge_fishing_supplies.plugin.kts", extra["Fishing bait"]["source"])

    def test_source_paths_and_unbound_rows_are_explicit(self):
        self.assertIn("Fish.kt", FISHING_FISH[0].source)
        self.assertIn("FishingTool.kt", FISHING_TOOL_SOURCE_PATH)
        self.assertIn("FishingSpot.kt", FISHING_SPOT_SOURCE_PATH)
        self.assertIn("lumbridge_fishing_supplies.plugin.kts", FISHING_BAIT_SHOP_SOURCE_PATH)
        self.assertIn("rainbow_fish", deferred_fishing_content_as_dict())
        self.assertGreaterEqual(len(DEFERRED_FISHING_CONTENT), 4)
        self.assertIn("cave_eel", fishing_fish_as_dict())


if __name__ == "__main__":
    unittest.main()
