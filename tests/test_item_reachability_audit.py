import unittest

from tools.audit_item_reachability import build_reachability_report


class TestItemReachabilityAudit(unittest.TestCase):
    def test_report_is_deterministic_and_accounts_for_live_action_inputs(self):
        report = build_reachability_report()
        self.assertEqual(report["schema_version"], 1)
        self.assertGreater(report["action_count"], 700)
        self.assertEqual(report["orphan_input_count"], len(report["orphan_inputs"]))
        self.assertEqual(
            report["orphan_input_count"],
            report["root_orphan_count"] + report["cascade_orphan_count"],
        )
        self.assertEqual(
            [row["item"] for row in report["orphan_inputs"]],
            sorted(row["item"] for row in report["orphan_inputs"]),
        )
        self.assertIn("Logs", report["routes"])
        self.assertIn("Bronze bar", report["routes"])
        self.assertIn("Crushed nest", report["routes"])
        self.assertEqual(report["routes"]["Air orb"], "Magic:charge_air_orb")
        self.assertEqual(report["routes"]["Wine of zamorak"], "Magic:telegrab_wine_of_zamorak")
        self.assertEqual(report["routes"]["Ecto-token"], "Prayer:ectofuntus_impious_ashes")
        self.assertEqual(report["routes"]["Juju vial"], "Item action:open:Juju vial pack")
        self.assertEqual(report["routes"]["Sweetcorn"], "Farming:sweetcorn")
        self.assertEqual(report["routes"]["Strawberry"], "Farming:strawberry")
        self.assertEqual(report["routes"]["Watermelon"], "Farming:watermelon")
        self.assertEqual(report["routes"]["Jangerberries"], "Farming:jangerberry")
        self.assertEqual(
            report["routes"]["Morchella mushroom"],
            "Farming:morchella",
        )
        self.assertEqual(
            report["routes"]["Papaya sapling"],
            "Farming:sapling:papaya",
        )
        self.assertEqual(report["routes"]["Papaya fruit"], "Farming:papaya")
        self.assertEqual(
            report["routes"]["Fungicide spray 9"],
            "Combat finisher:mutated_zygomite_level_74:Fungicide spray 10",
        )
        self.assertEqual(
            report["routes"]["Fungicide spray 0"],
            "Combat finisher:mutated_zygomite_level_74:Fungicide spray 1",
        )
        self.assertEqual(
            report["routes"]["Fungicide"],
            "combat:mutated_zygomite_level_74",
        )
        self.assertEqual(report["routes"]["Desert goat horn"], "combat:goat")
        self.assertEqual(
            report["routes"]["Swamp toad"],
            "Utility:gather_swamp_toads",
        )
        self.assertEqual(
            report["routes"]["Wimpy feather"],
            "Hunter:catch_wimpy_bird",
        )
        self.assertEqual(
            report["routes"]["Toad's legs"],
            "Utility:remove_swamp_toad_legs",
        )
        self.assertEqual(
            report["routes"]["Fish offcuts"],
            "Cooking:gut_leaping_trout",
        )
        self.assertEqual(
            report["routes"]["Willow branch"],
            "Farming:willow",
        )
        self.assertEqual(
            report["routes"]["Nasturtium seed"],
            "Utility:managing_miscellania",
        )
        self.assertEqual(
            report["routes"]["Redberry seed"],
            "Utility:managing_miscellania",
        )
        self.assertEqual(
            report["routes"]["Cadavaberry seed"],
            "Utility:managing_miscellania",
        )
        self.assertEqual(
            report["routes"]["Stardust"],
            "Activity:shooting_stars:mine",
        )
        self.assertEqual(
            report["routes"]["Fist of guthix token"],
            "Activity:fist_of_guthix:match",
        )
        self.assertEqual(
            report["routes"]["Combat hood 100"],
            "Activity:fist_of_guthix:buy:combat_hood",
        )
        self.assertEqual(
            report["routes"]["Combat hood 0"],
            "Activity:fist_of_guthix:uncharge:combat_hood",
        )
        self.assertEqual(
            report["routes"]["Bronze gauntlets"],
            "Activity:fist_of_guthix:buy:bronze_gauntlets",
        )
        self.assertEqual(
            report["routes"]["Summer sq'irkjuice"],
            "Activity:sorceress_garden:harvest",
        )
        self.assertEqual(
            report["routes"]["Jewelled diamond statuette"],
            "Activity:pyramid_plunder:loot",
        )
        self.assertEqual(
            report["routes"]["Sceptre of the gods"],
            "Activity:pyramid_plunder:loot",
        )
        self.assertNotIn(
            "Activity:shooting_stars:exchange",
            {action["id"] for action in report["unresolved_actions"]},
        )
        self.assertNotIn("Bird's nest", {row["item"] for row in report["orphan_inputs"]})

        long_kebbit_spike = next(
            row for row in report["orphan_inputs"]
            if row["item"] == "Long kebbit spike"
        )
        self.assertEqual(
            long_kebbit_spike["consumers"],
            [
                "Fletching:fletch_long_kebbit_bolts",
                "Shop service:leon_fletch_long_kebbit_bolts",
            ],
        )

        self.assertEqual(
            report["routes"]["Agility potion (4)"],
            "Shop service:bob_barter_decant_four:Agility potion",
        )
        self.assertEqual(
            report["routes"]["Attack flask (6)"],
            "Shop service:teplin_fill_potion_flasks:Attack potion",
        )
        self.assertEqual(
            report["routes"]["Attack flask (3)"],
            "Item action:consume:Attack flask (4)",
        )
        self.assertNotIn(
            "Shop service:teplin_decant_flasks_to_vials:Attack potion",
            {action["id"] for action in report["unresolved_actions"]},
        )

        orphan_items = {row["item"] for row in report["orphan_inputs"]}
        for item_name in (
            "Candle lantern (empty)",
            "Candle lantern (unlit, 4529)",
            "Oil lamp (empty)",
            "Oil lamp (unlit)",
            "Oil lantern (empty)",
            "Oil lantern (unlit)",
            "Bullseye lantern (unf)",
            "Bullseye lantern (empty)",
            "Bullseye lantern (unlit)",
            "Sapphire lantern (empty)",
            "Sapphire lantern (unlit)",
            "Mining helmet (unlit)",
            "Air orb",
            "Water orb",
            "Earth orb",
            "Fire orb",
            "Wine of zamorak",
        ):
            self.assertNotIn(item_name, orphan_items)


if __name__ == "__main__":
    unittest.main()
