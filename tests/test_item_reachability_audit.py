import unittest

from tools.audit_item_reachability import (
    _quest_stage_sources,
    build_reachability_report,
)


class TestItemReachabilityAudit(unittest.TestCase):
    def test_quest_stage_products_require_emitted_actions(self):
        quest_data = {
            "blocked": {
                "display_name": "Blocked Quest",
                "stage_requirements": (
                    {
                        "stage": 1,
                        "required_actions": ("Do the inert thing",),
                        "produced_inventory": {"Blocked product": 1},
                    },
                ),
            },
            "emitted": {
                "display_name": "Emitted Quest",
                "stage_requirements": (
                    {"stage": 1, "auto_actions": ("Do the emitted thing",)},
                    {
                        "stage": 2,
                        "required_actions": ("Do the emitted thing",),
                        "produced_inventory": {"Reachable product": 1},
                        "combat_encounters": (
                            {
                                "encounter_id": "reachable_fight",
                                "guaranteed_drops": {"Reachable combat product": 1},
                            },
                        ),
                    },
                ),
            },
            "variants": {
                "display_name": "Variant Quest",
                "stage_requirements": (
                    {
                        "stage": 1,
                        "variant": "left",
                        "auto_actions": ("Left-only action",),
                    },
                    {
                        "stage": 2,
                        "variant": "right",
                        "required_actions": ("Left-only action",),
                        "produced_inventory": {"Cross-variant product": 1},
                    },
                ),
            },
        }

        sources, blocked = _quest_stage_sources(
            quest_data,
            {
                "Blocked product",
                "Reachable product",
                "Reachable combat product",
                "Cross-variant product",
            },
        )

        self.assertNotIn("Blocked product", sources)
        self.assertNotIn("Cross-variant product", sources)
        self.assertEqual(sources["Reachable product"], {"quest-stage:emitted:2"})
        self.assertEqual(
            sources["Reachable combat product"],
            {"quest-combat:emitted:reachable_fight"},
        )
        self.assertEqual(
            blocked,
            [
                {
                    "quest_id": "blocked",
                    "quest": "Blocked Quest",
                    "stage": 1,
                    "products": ["Blocked product"],
                    "combat_products": {},
                    "blocked_combat_products": {},
                    "required_actions": ["Do the inert thing"],
                    "missing_required_actions": ["Do the inert thing"],
                },
                {
                    "quest_id": "variants",
                    "quest": "Variant Quest",
                    "stage": 2,
                    "products": ["Cross-variant product"],
                    "combat_products": {},
                    "blocked_combat_products": {},
                    "required_actions": ["Left-only action"],
                    "missing_required_actions": ["Left-only action"],
                },
            ],
        )

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
        self.assertNotIn("Dramen branch", report["routes"])
        self.assertEqual(
            report["routes"]["Pendant of lucien"],
            "quest-start:temple_of_ikov",
        )
        self.assertNotIn("Cinnamon", report["routes"])
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
        self.assertEqual(
            report["routes"]["Curly root"],
            "Woodcutting:curly_jade_root",
        )
        self.assertNotIn(
            "Activity:shooting_stars:exchange",
            {action["id"] for action in report["unresolved_actions"]},
        )
        self.assertNotIn("Bird's nest", {row["item"] for row in report["orphan_inputs"]})

        self.assertEqual(
            report["routes"]["Polar kebbit fur"],
            "Hunter:catch_polar_kebbit",
        )
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

        self.assertEqual(
            report["routes"]["Dragon impling jar"],
            "Hunter:catch_dragon_impling_puro_puro",
        )
        self.assertEqual(
            report["routes"]["Dragon arrowtips"],
            "Item action:loot:Dragon impling jar",
        )
        self.assertEqual(
            report["routes"]["Dragon dart tip"],
            "Item action:loot:Dragon impling jar",
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
            "Curly root",
            "Black mushroom",
            "Black mushroom ink",
            "Unholy mould",
        ):
            self.assertNotIn(item_name, orphan_items)

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
