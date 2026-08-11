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
            report["routes"]["Blue dragon scale"],
            "Utility:gather_blue_dragon_scales",
        )
        self.assertEqual(
            report["routes"]["Dragon scale dust"],
            "Utility:grind_blue_dragon_scale",
        )
        self.assertEqual(
            report["routes"]["Potato cactus"],
            "Utility:gather_potato_cacti",
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
            report["routes"]["Fellstalk seed"],
            "Thieving:pickpocket_master_farmer",
        )
        self.assertEqual(
            report["routes"]["Cured yak-hide"],
            "Shop service:thakkrad_cure_yak_hide",
        )
        self.assertEqual(
            report["routes"]["Black mushroom"],
            "Utility:gather_black_mushrooms",
        )
        self.assertEqual(
            report["routes"]["Black mushroom ink"],
            "Utility:grind_black_mushroom",
        )
        self.assertEqual(
            report["routes"]["Dramen branch"],
            "quest-stage:lost_city:4",
        )
        self.assertEqual(
            report["routes"]["Pendant of lucien"],
            "quest-start:temple_of_ikov",
        )
        self.assertEqual(
            report["routes"]["Cinnamon"],
            "Utility:grind_dramen_branch",
        )
        self.assertEqual(
            report["routes"]["Unholy mould"],
            "combat:chaos_druid",
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
        self.assertEqual(
            report["routes"]["Barley malt"],
            "Cooking:malt_barley",
        )
        self.assertEqual(
            report["routes"]["Ale yeast"],
            "Shop service:blandebir_fill_ale_yeast",
        )
        self.assertEqual(
            report["routes"]["Arctic pine logs"],
            "Woodcutting:arctic_pine",
        )
        self.assertEqual(
            report["routes"]["Eucalyptus logs"],
            "Woodcutting:eucalyptus",
        )
        self.assertNotIn(
            "Activity:shooting_stars:exchange",
            {action["id"] for action in report["unresolved_actions"]},
        )
        self.assertNotIn("Bird's nest", {row["item"] for row in report["orphan_inputs"]})

        self.assertEqual(
            report["routes"]["Long kebbit spike"],
            "Hunter:track_razor_backed_kebbit",
        )
        self.assertEqual(
            report["routes"]["Living minerals"],
            "Mining:living_rock_remains",
        )
        self.assertEqual(
            [
                row for row in report["orphan_inputs"]
                if row["item"] == "Long kebbit spike"
            ],
            [],
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
            "Barley malt",
            "Ale yeast",
            "Arctic pine logs",
            "Eucalyptus logs",
            "Black mushroom",
            "Black mushroom ink",
            "Dramen branch",
            "Cinnamon",
            "Unholy mould",
        ):
            self.assertNotIn(item_name, orphan_items)

    def test_habitat_vine_herb_chain_is_reachable(self):
        report = build_reachability_report()
        orphan_items = {row["item"] for row in report["orphan_inputs"]}
        cases = (
            ("erzille", "Erzille"),
            ("ugune", "Ugune"),
            ("argway", "Argway"),
            ("shengo", "Shengo"),
            ("samaden", "Samaden"),
        )

        for crop_id, herb_name in cases:
            with self.subTest(herb=herb_name):
                expected_routes = {
                    f"{herb_name} seed": "Hunter:catch_carrion_jadinko",
                    f"Grimy {herb_name.lower()}": f"Farming:{crop_id}",
                    f"Clean {herb_name.lower()}": f"Herblore:clean_{crop_id}",
                    f"{herb_name} potion (unf)": f"Herblore:unf_{crop_id}",
                }
                for item_name, route in expected_routes.items():
                    self.assertEqual(report["routes"].get(item_name), route)
                    self.assertNotIn(item_name, orphan_items)

        expected_vine_routes = {
            "Aquatic vine": "Hunter:catch_aquatic_jadinko",
            "Draconic vine": "Hunter:catch_draconic_jadinko",
            "Marble vine": "Hunter:catch_igneous_jadinko",
            "Oily vine": "Hunter:catch_amphibious_jadinko",
            "Saradomin vine": "Hunter:catch_saradomin_jadinko",
            "Zamorak vine": "Hunter:catch_zamorak_jadinko",
        }
        for item_name, route in expected_vine_routes.items():
            self.assertEqual(report["routes"].get(item_name), route)
            self.assertNotIn(item_name, orphan_items)

        unresolved_actions = {row["id"] for row in report["unresolved_actions"]}
        self.assertTrue(
            {
                "Hunter:catch_carrion_jadinko",
                *(f"Farming:{crop_id}" for crop_id, _herb_name in cases),
                *expected_vine_routes.values(),
            }.isdisjoint(unresolved_actions)
        )
        self.assertLessEqual(report["unresolved_action_count"], 85)

    def test_root_orphan_leverage_is_transitive_and_deterministically_ranked(self):
        report = build_reachability_report()
        rows = report["root_orphan_leverage"]
        root_orphans = {
            row["item"]
            for row in report["orphan_inputs"]
            if row["kind"] == "root"
        }

        self.assertEqual({row["item"] for row in rows}, root_orphans)
        self.assertEqual(
            rows,
            sorted(
                rows,
                key=lambda row: (
                    -row["newly_reachable_item_count"],
                    -row["newly_unblocked_action_count"],
                    row["item"],
                ),
            ),
        )
        for row in rows:
            with self.subTest(item=row["item"]):
                self.assertIn(row["item"], row["newly_reachable_items"])
                self.assertEqual(
                    row["newly_reachable_item_count"],
                    len(row["newly_reachable_items"]),
                )
                self.assertGreaterEqual(row["newly_unblocked_action_count"], 0)


if __name__ == "__main__":
    unittest.main()
