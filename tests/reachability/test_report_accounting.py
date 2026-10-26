import unittest
from unittest.mock import patch
import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core import constants
from ankiscape.data import vinesweeper_data
from tools.audit_item_reachability import build_reachability_report
from tests.reachability.live_report import live_reachability_report


class TestItemReachabilityAudit(unittest.TestCase):
    def test_report_is_deterministic_and_accounts_for_live_action_inputs(self):
        report = live_reachability_report()
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
        self.assertIsNone(report["routes"].get("Wimpy feather"))
        self.assertIn(
            "Hunter:catch_wimpy_bird",
            {action["id"] for action in report["unresolved_actions"]},
        )
        self.assertEqual(
            report["routes"]["Toad's legs"],
            "Utility:remove_swamp_toad_legs",
        )
        self.assertIsNone(report["routes"].get("Fish offcuts"))
        self.assertIn(
            "Cooking:gut_leaping_trout",
            {action["id"] for action in report["unresolved_actions"]},
        )
        self.assertEqual(
            report["routes"]["Willow branch"],
            "Farming:willow",
        )
        self.assertEqual(
            report["routes"]["Nasturtium seed"],
            "Thieving:pickpocket_master_farmer",
        )
        self.assertEqual(
            report["routes"]["Redberry seed"],
            "Thieving:pickpocket_master_farmer",
        )
        self.assertEqual(
            report["routes"]["Cadavaberry seed"],
            "Thieving:pickpocket_master_farmer",
        )
        self.assertEqual(
            report["routes"]["Fellstalk seed"],
            "Thieving:pickpocket_master_farmer",
        )
        self.assertNotIn("Cured yak-hide", report["routes"])
        self.assertEqual(
            report["routes"]["Black mushroom"],
            "Utility:gather_black_mushrooms",
        )
        self.assertEqual(
            report["routes"]["Black mushroom ink"],
            "Utility:grind_black_mushroom",
        )
        self.assertEqual(
            report["routes"]["Doogle leaves"],
            "Utility:gather_doogle_leaves",
        )
        self.assertEqual(
            report["routes"]["Red dye"],
            "Utility:aggie_make_red_dye",
        )
        self.assertEqual(
            report["routes"]["Yellow dye"],
            "Utility:aggie_make_yellow_dye",
        )
        self.assertEqual(
            report["routes"]["Orange dye"],
            "Utility:mix_orange_dye",
        )
        self.assertEqual(
            report["routes"]["Blue dye"],
            "Utility:aggie_make_blue_dye",
        )
        self.assertEqual(
            report["routes"]["Orange goblin mail"],
            "Utility:dye_goblin_mail_orange",
        )
        self.assertEqual(
            report["routes"]["Blue goblin mail"],
            "Utility:dye_goblin_mail_blue",
        )
        self.assertEqual(
            report["routes"]["Doogle sardine"],
            "quest-stage:gertrudes_cat:5",
        )
        self.assertEqual(
            report["routes"]["Kitten"],
            "quest:gertrudes_cat",
        )
        self.assertEqual(
            report["routes"]["Dramen branch"],
            "quest-stage:lost_city:4",
        )
        self.assertEqual(
            report["routes"]["Pendant of lucien"],
            "quest-start:temple_of_ikov",
        )
        self.assertEqual(report["routes"]["Cinnamon"], "Utility:grind_dramen_branch")
        self.assertEqual(
            report["routes"]["Unholy mould"],
            "combat:chaos_druid",
        )
        self.assertEqual(
            report["routes"]["Snake hide"],
            "combat:bush_snake",
        )
        self.assertEqual(
            report["routes"]["Stardust"],
            "Activity:shooting_stars:mine",
        )

        self.assertEqual(report["routes"]["Fist of guthix token"], "Activity:fist_of_guthix:match")
        self.assertEqual(report["routes"]["Combat hood 100"], "Activity:fist_of_guthix:buy:combat_hood")
        self.assertEqual(report["routes"]["Combat hood 0"], "Activity:fist_of_guthix:uncharge:combat_hood")
        self.assertEqual(report["routes"]["Bronze gauntlets"], "Activity:fist_of_guthix:buy:bronze_gauntlets")
        self.assertEqual(report["routes"]["Vinesweeper point"], "Activity:vinesweeper:operation")
        self.assertEqual(report["routes"]["Wergali seed"], "Activity:vinesweeper:buy:wergali_seed")
        self.assertEqual(report["routes"]["Compost potion (4)"], "Activity:vinesweeper:buy:compost_potion_4")
        self.assertEqual(report["routes"]["Compost potion (3)"], "Utility:use_compost_potion:Compost potion (4)")
        self.assertEqual(report["routes"]["Compost potion (1)"], "Utility:use_compost_potion:Compost potion (2)")
        self.assertEqual(report["routes"]["Spirit seed"], "Activity:vinesweeper:buy:spirit_tree_seed")
        self.assertNotIn("Flag", report["routes"])
        reward_items = {
            reward.item_name for reward in vinesweeper_data.VINESWEEPER_REWARDS
            if reward.id != "flag"
        }
        self.assertTrue(reward_items <= report["routes"].keys())
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
            report["routes"].get("Arctic pine logs"),
            "Woodcutting:arctic_pine",
        )
        self.assertNotIn(
            "Woodcutting:arctic_pine",
            {action["id"] for action in report["unresolved_actions"]},
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
            report["routes"]["Lergberry seed"],
            "Hunter:track_shadow_jadinko",
        )
        self.assertEqual(
            report["routes"]["Kalferberry seed"],
            "Hunter:track_shadow_jadinko",
        )
        self.assertEqual(
            report["routes"]["Kalferberry"],
            "Farming:kalferberry",
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
        self.assertIsNone(report["routes"].get("Attack flask (6)"))
        self.assertIsNone(report["routes"].get("Attack flask (3)"))
        self.assertTrue(
            {
                "Shop service:teplin_fill_potion_flasks:Attack potion",
                "Shop service:teplin_decant_flasks_to_vials:Attack potion",
            }.issubset(
                {action["id"] for action in report["unresolved_actions"]}
            )
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
        self.assertIn("Mining helmet (unlit)", orphan_items)
        self.assertNotIn("Arctic pine logs", orphan_items)
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
            "Air orb",
            "Water orb",
            "Earth orb",
            "Fire orb",
            "Wine of zamorak",
            "Barley malt",
            "Ale yeast",
            "Eucalyptus logs",
            "Curly root",
            "Black mushroom",
            "Black mushroom ink",
            "Unholy mould",
            "Snake hide",
            "Snakeskin",
            "Snakeskin bandana",
            "Snakeskin body",
            "Snakeskin boots",
            "Snakeskin chaps",
            "Snakeskin vambraces",
        ):
            self.assertNotIn(item_name, orphan_items)

    def test_habitat_vine_herb_chain_is_reachable(self):
        report = live_reachability_report()
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
                seed_route = (
                    "Hunter:catch_common_jadinko"
                    if herb_name == "Erzille"
                    else "Hunter:track_shadow_jadinko"
                )
                expected_routes = {
                    f"{herb_name} seed": seed_route,
                    f"Grimy {herb_name.lower()}": f"Farming:{crop_id}",
                    f"Clean {herb_name.lower()}": f"Herblore:clean_{crop_id}",
                    f"{herb_name} potion (unf)": f"Herblore:unf_{crop_id}",
                }
                for item_name, route in expected_routes.items():
                    self.assertEqual(report["routes"].get(item_name), route)
                    self.assertNotIn(item_name, orphan_items)

        expected_jadinko_routes = {
            "Shadow vine": "Hunter:track_shadow_jadinko",
            "Corrupt vine": "Hunter:track_diseased_jadinko",
            "Striped vine": "Hunter:track_camouflaged_jadinko",
            "Withered vine": "Hunter:catch_common_jadinko",
            "Marble vine": "Hunter:catch_igneous_jadinko",
            "Plant teeth": "Hunter:catch_cannibal_jadinko",
            "Aquatic vine": "Hunter:catch_aquatic_jadinko",
            "Oily vine": "Hunter:catch_amphibious_jadinko",
            "Pungent vine": "Hunter:catch_carrion_jadinko",
            "Draconic vine": "Hunter:catch_draconic_jadinko",
            "Guthix vine": "Hunter:catch_guthix_jadinko",
            "Saradomin vine": "Hunter:catch_saradomin_jadinko",
            "Zamorak vine": "Hunter:catch_zamorak_jadinko",
        }
        for item_name, route in expected_jadinko_routes.items():
            self.assertEqual(report["routes"].get(item_name), route)
            self.assertNotIn(item_name, orphan_items)

        unresolved_actions = {row["id"] for row in report["unresolved_actions"]}
        self.assertTrue(
            {
                *(f"Farming:{crop_id}" for crop_id, _herb_name in cases),
                *expected_jadinko_routes.values(),
            }.isdisjoint(unresolved_actions)
        )

    def test_root_orphan_leverage_does_not_bypass_inactive_action_gates(self):
        gated_action = {
            "root_leverage_gate_test": {
                "status": "implemented",
                "quest_gate": "unreachable_gate_test",
                "requirements": {"Gate-only orphan": 1},
                "outputs": {"Gate-only output": 1},
            },
        }

        with patch.dict(constants.UTILITY_ACTIVITY_DATA, gated_action):
            report = build_reachability_report()

        row = next(
            row
            for row in report["root_orphan_leverage"]
            if row["item"] == "Gate-only orphan"
        )
        self.assertEqual(row["newly_reachable_items"], ["Gate-only orphan"])
        self.assertEqual(row["newly_reachable_item_count"], 1)
        self.assertEqual(row["newly_unblocked_action_count"], 0)

    def test_root_orphan_leverage_is_transitive_and_deterministically_ranked(self):
        report = live_reachability_report()
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
