import unittest

from firemaking_data import (
    DEFERRED_FIREMAKING_CONTENT,
    FIREMAKING_OUTPUT_ITEM_ID,
    FIREMAKING_RUNTIME_SOURCE_PATH,
    FIREMAKING_SOURCE_PATH,
    FIREMAKING_TARGETS,
    FIREMAKING_TARGETS_BY_ID,
    LIGHT_SOURCE_ACTIVITIES,
    LIGHT_SOURCE_PREPARATIONS,
    LIGHT_SOURCE_PATH,
    LIGHT_SOURCE_PLUGIN_PATH,
    LIT_LIGHT_SOURCE_ITEMS,
    firemaking_deferred_content_as_dict,
    firemaking_extra_items_as_dict,
    firemaking_targets_as_dict,
    light_source_activities_as_dict,
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

    def test_light_source_rows_and_inverse_bindings_are_exact(self):
        rows = [
            (activity.id, activity.raw_item_id, activity.lit_item_id, activity.level)
            for activity in LIGHT_SOURCE_ACTIVITIES
        ]
        self.assertEqual(
            rows,
            [
                ("light_unlit_torch", 596, 594, 1),
                ("light_candle", 36, 33, 1),
                ("light_black_candle", 38, 32, 1),
                ("light_candle_lantern_4527", 4529, 4531, 4),
                ("light_candle_lantern_4532", 4532, 4534, 4),
                ("light_oil_lamp", 4522, 4524, 12),
                ("light_oil_lantern", 4537, 4539, 26),
                ("light_bug_lantern", 7051, 7053, 33),
                ("light_bullseye_lantern", 4548, 4550, 49),
                ("light_sapphire_lantern", 4701, 4702, 49),
                ("light_emerald_lantern", 9064, 9065, 49),
                ("light_mining_helmet", 5014, 5013, 65),
            ],
        )
        activities = light_source_activities_as_dict()
        self.assertEqual(len(activities), 30)
        for activity in LIGHT_SOURCE_ACTIVITIES:
            light = activities[activity.id]
            extinguish = activities[f"extinguish_{activity.id[6:]}"]
            self.assertEqual(light["requirements"], {activity.raw_item: 1})
            self.assertEqual(light["output_item"], activity.lit_item)
            self.assertEqual(light["firemaking_level"], activity.level)
            self.assertEqual(light["source_item_id"], activity.raw_item_id)
            self.assertEqual(light["output_item_id"], activity.lit_item_id)
            self.assertEqual(extinguish["requirements"], {activity.lit_item: 1})
            self.assertEqual(extinguish["output_item"], activity.raw_item)
            self.assertNotIn("firemaking_level", extinguish)
        self.assertIn("LightSource.kt", LIGHT_SOURCE_PATH)
        self.assertIn("light_source.plugin.kts", LIGHT_SOURCE_PLUGIN_PATH)
        self.assertNotIn("Lit bug lantern", LIT_LIGHT_SOURCE_ITEMS)

    def test_light_source_preparation_rows_preserve_item_states(self):
        activities = light_source_activities_as_dict()
        expected = {
            "insert_white_candle": (4527, "Candle", "Candle lantern (unlit, 4529)", 4529),
            "insert_black_candle": (4527, "Black candle", "Candle lantern (unlit, 4532)", 4532),
            "fill_oil_lamp": (4525, "Swamp tar", "Oil lamp (unlit)", 4522),
            "fill_oil_lantern": (4535, "Swamp tar", "Oil lantern (unlit)", 4537),
            "fill_bullseye_lantern": (4546, "Swamp tar", "Bullseye lantern (unlit)", 4548),
            "fill_sapphire_lantern": (4700, "Swamp tar", "Sapphire lantern (unlit)", 4701),
        }
        self.assertEqual(len(LIGHT_SOURCE_PREPARATIONS), len(expected))
        for preparation in LIGHT_SOURCE_PREPARATIONS:
            input_id, reagent, output_item, output_id = expected[preparation.id]
            row = activities[preparation.id]
            self.assertEqual(row["requirements"], {preparation.input_item: 1, reagent: 1})
            self.assertEqual(row["source_item_id"], input_id)
            self.assertEqual(row["output_item"], output_item)
            self.assertEqual(row["output_item_id"], output_id)
            self.assertNotIn("firemaking_level", row)

    def test_light_source_items_keep_canonical_ids(self):
        extra = firemaking_extra_items_as_dict()
        for activity in LIGHT_SOURCE_ACTIVITIES:
            self.assertEqual(extra[activity.raw_item]["item_id"], activity.raw_item_id)
            self.assertEqual(extra[activity.lit_item]["item_id"], activity.lit_item_id)


if __name__ == "__main__":
    unittest.main()
