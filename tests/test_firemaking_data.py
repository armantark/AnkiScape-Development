import unittest

from firemaking_data import (
    DEFERRED_FIREMAKING_CONTENT,
    FIREMAKING_OUTPUT_ITEM_ID,
    FIREMAKING_RUNTIME_SOURCE_PATH,
    FIREMAKING_SOURCE_PATH,
    FIREMAKING_TARGETS,
    FIREMAKING_TARGETS_BY_ID,
    firemaking_deferred_content_as_dict,
    firemaking_extra_items_as_dict,
    firemaking_targets_as_dict,
)


class TestFiremakingData(unittest.TestCase):
    def test_source_backed_target_rows_are_exact(self):
        rows = [
            (target.id, target.input_item, target.source_item_id, target.level, target.base_exp, target.tradeable)
            for target in FIREMAKING_TARGETS
        ]

        self.assertEqual(
            rows,
            [
                ("logs", "Logs", 1511, 1, 40.0, True),
                ("achey_logs", "Achey tree logs", 2862, 1, 40.0, True),
                ("oak_logs", "Oak logs", 1521, 15, 60.0, True),
                ("willow_logs", "Willow logs", 1519, 30, 90.0, True),
                ("teak_logs", "Teak logs", 6333, 35, 105.0, True),
                ("arctic_pine_logs", "Arctic pine logs", 10810, 42, 125.0, True),
                ("maple_logs", "Maple logs", 1517, 45, 135.0, True),
                ("mahogany_logs", "Mahogany logs", 6332, 50, 157.5, True),
                ("eucalyptus_logs", "Eucalyptus logs", 12581, 58, 193.5, True),
                ("yew_logs", "Yew logs", 1515, 60, 202.5, True),
                ("magic_logs", "Magic logs", 1513, 75, 303.8, True),
                ("curly_root", "Curly root", 21350, 75, 161.6, True),
                ("cursed_magic_logs", "Cursed magic logs", 13567, 82, 303.8, False),
            ],
        )
        self.assertEqual(set(FIREMAKING_TARGETS_BY_ID), {row[0] for row in rows})

    def test_targets_export_runtime_shape(self):
        data = firemaking_targets_as_dict()

        self.assertEqual(data["logs"]["requirements"], {"Logs": 1})
        self.assertEqual(data["logs"]["output_item"], "Ashes")
        self.assertEqual(data["logs"]["output_qty"], 1)
        self.assertEqual(data["logs"]["low_chance"], 65)
        self.assertEqual(data["logs"]["high_chance"], 513)
        self.assertEqual(data["magic_logs"]["exp"], 303.8)
        self.assertEqual(data["curly_root"]["level"], 75)

    def test_extra_items_register_ashes_and_firemaking_inputs(self):
        extra = firemaking_extra_items_as_dict()

        self.assertEqual(extra["Ashes"]["item_id"], FIREMAKING_OUTPUT_ITEM_ID)
        self.assertEqual(extra["Ashes"]["category"], "material")
        self.assertEqual(extra["Cursed magic logs"]["tradeable"], False)
        self.assertEqual(extra["Arctic pine logs"]["category"], "log")
        self.assertIn("FiremakingAction.kt", extra["Ashes"]["source"])

    def test_source_paths_and_deferred_content_are_explicit(self):
        self.assertIn("FiremakingData.kt", FIREMAKING_SOURCE_PATH)
        self.assertIn("FiremakingAction.kt", FIREMAKING_RUNTIME_SOURCE_PATH)
        deferred = firemaking_deferred_content_as_dict()

        self.assertEqual(len(DEFERRED_FIREMAKING_CONTENT), 1)
        self.assertIn("bonfires", deferred)
        self.assertEqual(deferred["bonfires"]["status"], "deferred_2012_extension")
        self.assertIn("2012", deferred["bonfires"]["reason"])


if __name__ == "__main__":
    unittest.main()
