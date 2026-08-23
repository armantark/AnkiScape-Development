import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core import constants
from ankiscape.core.constants import ITEM_DEFINITIONS, QUEST_DATA
from tools.audit_item_reachability import (
    _close_actions,
    _close_quest_reachability,
    _quest_completion_sets,
    _quest_stage_sources,
    build_reachability_report,
)


class TestItemReachabilityAudit(unittest.TestCase):
    def test_blocked_quest_stage_hard_stops_all_later_products(self):
        quest_data = {
            "blocked": {
                "display_name": "Blocked Quest",
                "stage_requirements": (
                    {
                        "stage": 1,
                        "required_actions": ("Do the inert thing",),
                        "produced_inventory": {"Blocked product": 1},
                    },
                    {
                        "stage": 5,
                        "produced_inventory": {"Later product": 1},
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

        sources, blocked, completable = _quest_stage_sources(
            quest_data,
            {
                "Blocked product",
                "Later product",
                "Reachable product",
                "Reachable combat product",
                "Cross-variant product",
            },
        )

        self.assertNotIn("Blocked product", sources)
        self.assertNotIn("Later product", sources)
        self.assertNotIn("Cross-variant product", sources)
        self.assertEqual(completable, {"emitted", "variants"})
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
                    "variant": "",
                    "products": ["Blocked product"],
                    "combat_products": {},
                    "blocked_combat_products": {},
                    "required_actions": ["Do the inert thing"],
                    "missing_required_actions": ["Do the inert thing"],
                    "missing_required_routes": [],
                    "missing_required_items": [],
                    "missing_required_tools": [],
                    "missing_item_alternatives": [],
                    "blocked_combat_encounters": [],
                },
                {
                    "quest_id": "variants",
                    "quest": "Variant Quest",
                    "stage": 2,
                    "variant": "right",
                    "products": ["Cross-variant product"],
                    "combat_products": {},
                    "blocked_combat_products": {},
                    "required_actions": ["Left-only action"],
                    "missing_required_actions": ["Left-only action"],
                    "missing_required_routes": [],
                    "missing_required_items": [],
                    "missing_required_tools": [],
                    "missing_item_alternatives": [],
                    "blocked_combat_encounters": [],
                },
            ],
        )

    def test_unreachable_required_item_stops_later_stage_products(self):
        quest_data = {
            "q": {
                "display_name": "Item Blocked Quest",
                "stage_requirements": (
                    {
                        "stage": 1,
                        "required_inventory": {"Unreachable key": 1},
                        "produced_inventory": {"Blocked stage product": 1},
                    },
                    {"stage": 2, "produced_inventory": {"Later product": 1}},
                ),
            },
        }

        sources, blocked, completable = _quest_stage_sources(
            quest_data,
            {"Blocked stage product", "Later product"},
            reachable_items={"Reachable item"},
        )

        self.assertEqual(sources, {})
        self.assertEqual(completable, set())
        self.assertEqual(blocked[0]["missing_required_items"], ["Unreachable key"])

    def test_unreachable_route_seeds_neither_products_nor_completion_rewards(self):
        quest_data = {
            "q": {
                "display_name": "Route Blocked Quest",
                "point_reward": 1,
                "rewards": {"Completion reward": 1},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "required_routes": ("Reach the sealed chamber",),
                        "produced_inventory": {"Route product": 1},
                    },
                ),
            },
        }

        sources, blocked, action_completable = _quest_stage_sources(
            quest_data,
            {"Route product", "Completion reward"},
        )
        completed, _ = _quest_completion_sets(quest_data, action_completable)

        self.assertEqual(sources, {})
        self.assertEqual(completed, set())
        self.assertEqual(blocked[0]["missing_required_routes"], ["Reach the sealed chamber"])

    def test_unsatisfiable_combat_without_registered_drops_blocks_quest(self):
        quest_data = {
            "q": {
                "display_name": "No Drop Combat Quest",
                "point_reward": 1,
                "rewards": {"Completion reward": 1},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "produced_inventory": {"Stage product": 1},
                        "combat_encounters": ({"encounter_id": "impossible_fight"},),
                    },
                ),
            },
        }

        sources, blocked, action_completable = _quest_stage_sources(
            quest_data,
            {"Stage product", "Completion reward"},
            combat_encounter_satisfiable=lambda _encounter: False,
        )
        completed, _ = _quest_completion_sets(quest_data, action_completable)

        self.assertEqual(sources, {})
        self.assertEqual(completed, set())
        self.assertEqual(blocked[0]["blocked_combat_encounters"], ["impossible_fight"])
        self.assertEqual(blocked[0]["blocked_combat_products"], {})

    def test_interleaved_variants_accept_the_completable_branch(self):
        quest_data = {
            "q": {
                "display_name": "Interleaved Variant Quest",
                "stage_requirements": (
                    {
                        "stage": 1,
                        "variant": "blocked",
                        "required_inventory": {"Unreachable branch key": 1},
                        "auto_actions": ("Blocked branch action",),
                    },
                    {
                        "stage": 2,
                        "required_actions": ("Shared action",),
                        "produced_inventory": {"Shared product": 1},
                    },
                    {
                        "stage": 1,
                        "variant": "open",
                        "auto_actions": ("Shared action",),
                    },
                ),
            },
        }

        sources, _blocked, completable = _quest_stage_sources(
            quest_data,
            {"Shared product"},
        )

        self.assertEqual(completable, {"q"})
        self.assertEqual(sources["Shared product"], {"quest-stage:q:2"})

    def test_cross_quest_fixed_point_unlocks_a_later_quest_stage(self):
        quest_data = {
            "supplier": {
                "display_name": "Supplier",
                "rewards": {"Quest key": 1},
                "stage_requirements": (),
            },
            "consumer": {
                "display_name": "Consumer",
                "rewards": {"Final reward": 1},
                "stage_requirements": (
                    {"stage": 1, "required_inventory": {"Quest key": 1}},
                ),
            },
        }
        seed_sources = {}

        _blocked, completed, _startable = _close_quest_reachability(
            (),
            seed_sources,
            {},
            set(),
            quest_data,
            {"Quest key", "Final reward"},
            lambda _encounter: True,
        )

        self.assertEqual(completed, {"supplier", "consumer"})
        self.assertEqual(seed_sources["Quest key"], {"quest:supplier"})
        self.assertEqual(seed_sources["Final reward"], {"quest:consumer"})

    def test_finite_quantity_does_not_satisfy_a_larger_quest_gate(self):
        quest_data = {
            "q": {
                "display_name": "Quantity Quest",
                "stage_requirements": (
                    {
                        "stage": 1,
                        "required_inventory": {"Finite token": 2},
                        "produced_inventory": {"Blocked product": 1},
                    },
                ),
            },
        }

        sources, blocked, completable = _quest_stage_sources(
            quest_data,
            {"Blocked product"},
            reachable_items={"Finite token"},
            finite_item_counts={"Finite token": 1},
        )

        self.assertEqual(sources, {})
        self.assertEqual(completable, set())
        self.assertEqual(blocked[0]["missing_required_items"], ["Finite token"])

    def test_repeatable_quantity_satisfies_a_larger_quest_gate(self):
        quest_data = {
            "q": {
                "display_name": "Repeatable Quantity Quest",
                "stage_requirements": (
                    {
                        "stage": 1,
                        "consumed_inventory": {"Repeatable token": 50},
                        "produced_inventory": {"Product": 1},
                    },
                ),
            },
        }

        sources, blocked, completable = _quest_stage_sources(
            quest_data,
            {"Product"},
            reachable_items={"Repeatable token"},
            repeatable_items={"Repeatable token"},
        )

        self.assertEqual(blocked, [])
        self.assertEqual(completable, {"q"})
        self.assertEqual(sources["Product"], {"quest-stage:q:1"})

    def test_mutually_exclusive_branch_products_are_not_pooled(self):
        quest_data = {
            "q": {
                "display_name": "Branch Product Quest",
                "stage_requirements": (
                    {"stage": 1, "variant": "left", "produced_inventory": {"Left token": 1}},
                    {"stage": 1, "variant": "right", "produced_inventory": {"Right token": 1}},
                ),
            },
        }

        sources, _blocked, completable = _quest_stage_sources(
            quest_data,
            {"Left token", "Right token"},
        )

        self.assertEqual(completable, {"q"})
        self.assertEqual(sources, {})

    def test_branch_only_items_are_reachable_without_cross_branch_conjunctions(self):
        quest_data = {
            "q": {
                "display_name": "Branch Product Quest",
                "stage_requirements": (
                    {"stage": 1, "variant": "left", "produced_inventory": {"Left token": 1}},
                    {"stage": 1, "variant": "right", "produced_inventory": {"Right token": 1}},
                ),
            },
        }
        actions = (
            {
                "id": "needs-both",
                "required": {"Left token", "Right token"},
                "alternatives": (),
                "outputs": {"Pooled product"},
            },
        )
        seed_sources = {}
        scenario_sources = []

        _blocked, completed, _startable = _close_quest_reachability(
            actions,
            seed_sources,
            {},
            set(),
            quest_data,
            {"Left token", "Right token", "Pooled product"},
            lambda _encounter: True,
            scenario_sources_out=scenario_sources,
        )
        scenario_reachable = [
            _close_actions(actions, sources)[0]
            for sources in scenario_sources
        ]
        reachable = set.union(*scenario_reachable)

        self.assertEqual(completed, {"q"})
        self.assertEqual(reachable, {"Left token", "Right token"})
        self.assertNotIn("Pooled product", reachable)
        self.assertEqual(
            {frozenset(items) for items in scenario_reachable},
            {frozenset({"Left token"}), frozenset({"Right token"})},
        )

    def test_globally_completed_quests_are_existential_across_branch_scenarios(self):
        quest_data = {
            "q": {
                "display_name": "One Viable Branch Quest",
                "rewards": {"Completion reward": 1},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "variant": "blocked",
                        "required_inventory": {"Unreachable key": 1},
                    },
                    {"stage": 1, "variant": "open"},
                ),
            },
        }
        seed_sources = {}

        _blocked, completed, _startable = _close_quest_reachability(
            (),
            seed_sources,
            {},
            set(),
            quest_data,
            {"Completion reward"},
            lambda _encounter: True,
        )

        self.assertEqual(completed, {"q"})
        self.assertEqual(seed_sources["Completion reward"], {"quest:q"})

    def test_choice_route_is_not_available_before_its_declared_stage(self):
        quest_data = {
            "q": {
                "display_name": "Late Choice Quest",
                "choices": (
                    {
                        "stage": 99,
                        "options": ({"route_id": "Late route"},),
                    },
                ),
                "stage_requirements": (
                    {
                        "stage": 1,
                        "variant": "late",
                        "required_routes": ("Late route",),
                        "produced_inventory": {"Impossible early product": 1},
                    },
                ),
            },
        }

        sources, blocked, completable = _quest_stage_sources(
            quest_data,
            {"Impossible early product"},
        )

        self.assertEqual(sources, {})
        self.assertEqual(completable, set())
        self.assertEqual(blocked[0]["missing_required_routes"], ["Late route"])

    def test_unsatisfiable_combat_blocks_stage_and_completion_rewards(self):
        quest_data = {
            "q": {
                "display_name": "Combat Blocked Quest",
                "point_reward": 1,
                "rewards": {"Completion reward": 1},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "produced_inventory": {"Stage product": 1},
                        "combat_encounters": (
                            {
                                "encounter_id": "impossible_fight",
                                "guaranteed_drops": {"Combat product": 1},
                            },
                        ),
                    },
                ),
            },
        }

        sources, blocked, action_completable = _quest_stage_sources(
            quest_data,
            {"Stage product", "Combat product", "Completion reward"},
            combat_encounter_satisfiable=lambda _encounter: False,
        )
        completed, _ = _quest_completion_sets(
            quest_data,
            action_completable,
        )
        seeded_rewards = {
            item
            for quest_id in completed
            for item in quest_data[quest_id].get("rewards", {})
        }

        self.assertEqual(action_completable, set())
        self.assertEqual(completed, set())
        self.assertNotIn("Stage product", sources)
        self.assertNotIn("Combat product", sources)
        self.assertNotIn("Completion reward", seeded_rewards)
        self.assertEqual(
            blocked[0]["blocked_combat_products"],
            {"impossible_fight": ["Combat product"]},
        )

    def test_shield_of_arrav_reaches_all_stage_products(self):
        report = build_reachability_report()

        self.assertFalse(
            [
                row
                for row in report["blocked_quest_stage_products"]
                if row["quest_id"] == "shield_of_arrav"
            ]
        )
        for item in (
            "Shield of Arrav book",
            "Intel report",
            "Weapon store key",
            "Phoenix crossbow",
            "Broken shield (Phoenix half)",
            "Broken shield (Black Arm half)",
            "Half certificate (Phoenix)",
            "Half certificate (Black Arm)",
            "Certificate",
        ):
            self.assertIn(item, report["routes"])

    def test_uncompletable_prerequisite_blocks_quest_completion_and_seeding(self):
        quest_data = {
            "blocked": {
                "display_name": "Blocked Quest",
                "point_reward": 5,
                "rewards": {"Blocked reward": 1},
                "start_inventory": {"Blocked start item": 1},
                "stage_requirements": (
                    {"stage": 1, "required_actions": ("Missing action",)},
                ),
            },
            "dependent": {
                "display_name": "Dependent Quest",
                "point_reward": 2,
                "rewards": {"Dependent reward": 1},
                "start_inventory": {"Dependent start item": 1},
                "required_quests": (
                    {"quest_id": "blocked", "display_name": "Blocked Quest"},
                ),
                "stage_requirements": (),
            },
            "quest_point_gated": {
                "display_name": "Quest Point Gated",
                "point_reward": 1,
                "required_quest_points": 5,
                "stage_requirements": (),
            },
            "completable": {
                "display_name": "Completable Quest",
                "point_reward": 3,
                "stage_requirements": (),
            },
        }

        _, _, action_completable = _quest_stage_sources(quest_data, set())
        completed, startable = _quest_completion_sets(
            quest_data,
            action_completable,
        )

        self.assertEqual(action_completable, {"dependent", "quest_point_gated", "completable"})
        self.assertEqual(completed, {"completable"})
        self.assertEqual(startable, {"blocked", "completable"})
        self.assertNotIn("dependent", startable)
        self.assertNotIn("quest_point_gated", startable)

    def test_wicked_hood_claim_is_reachable_after_rune_mysteries(self):
        report = build_reachability_report()

        self.assertEqual(report["routes"].get("Wicked hood"), "claim:wicked_hood")
        self.assertFalse(
            [
                row
                for row in report["blocked_quest_stage_products"]
                if row["quest_id"] == "rune_mysteries"
            ]
        )

    def test_a_souls_bane_rage_action_has_a_runtime_emitter(self):
        report = build_reachability_report()
        missing_actions = {
            action
            for row in report["blocked_quest_stage_products"]
            if row["quest_id"] == "a_souls_bane"
            for action in row["missing_required_actions"]
        }

        self.assertNotIn("Fill the rage meter with an anger weapon", missing_actions)

    def test_dealing_with_scabaras_bronze_action_has_a_runtime_emitter(self):
        report = build_reachability_report()
        missing_actions = {
            action
            for row in report["blocked_quest_stage_products"]
            if row["quest_id"] == "dealing_with_scabaras"
            for action in row["missing_required_actions"]
        }

        self.assertNotIn(
            "Prepare bronze equipment for the High Priest's tests",
            missing_actions,
        )

    def test_diamond_in_the_rough_claim_items_require_reachable_quest_and_level_gates(self):
        report = build_reachability_report()

        self.assertEqual(
            {
                item: report["routes"].get(item)
                for item in ("Apmeken mask", "Ankh", "Scabaras mask", "Was")
            },
            {
                "Apmeken mask": "claim:diamond_in_the_rough_apmeken_tomb",
                "Ankh": "claim:diamond_in_the_rough_apmeken_tomb",
                "Scabaras mask": "claim:diamond_in_the_rough_scabaras_tomb",
                "Was": "claim:diamond_in_the_rough_scabaras_tomb",
            },
        )

    def test_unreachable_claim_level_does_not_seed_item(self):
        constructed_claim = {
            "unreachable_level_item": {
                "claim_type": "skill_reward",
                "items": (("Jade vine seed", 1),),
                "required_quest": "diamond_in_the_rough",
                "xp_amount": 1,
                "skill_options": ("mining",),
                "minimum_level": 100,
            },
        }

        with patch.dict(constants.CLAIM_DATA, constructed_claim):
            report = build_reachability_report()

        self.assertIsNone(report["routes"].get("Jade vine seed"))

    def test_report_matches_player_finishable_quest_baseline(self):
        report = build_reachability_report()

        self.assertEqual(report["action_count"], 1599)
        self.assertEqual(report["reachable_item_count"], 2390)
        self.assertEqual(report["orphan_input_count"], 38)
        self.assertEqual(report["root_orphan_count"], 34)
        self.assertEqual(report["cascade_orphan_count"], 4)
        self.assertEqual(report["unresolved_action_count"], 37)
        self.assertEqual(report["seed_item_count"], 1143)
        self.assertFalse(
            [
                row
                for row in report["blocked_quest_stage_products"]
                if row["quest_id"] == "clock_tower"
            ]
        )
        self.assertFalse(
            [
                row
                for row in report["blocked_quest_stage_products"]
                if row["quest_id"] == "deadliest_catch"
            ]
        )
        orphan_items = {row["item"] for row in report["orphan_inputs"]}
        quest_reward_items = {
            item
            for quest in QUEST_DATA.values()
            for item in quest.get("rewards", {})
        }
        self.assertEqual(
            orphan_items & quest_reward_items,
            {"Blood talisman", "Jade vine seed", "Magic secateurs"},
        )

    def test_lost_city_branch_and_cinnamon_require_the_real_quest_chain(self):
        registered_items = {
            definition.storage_key for definition in ITEM_DEFINITIONS
        }
        sources, _, action_completable = _quest_stage_sources(
            QUEST_DATA,
            registered_items,
        )
        report = build_reachability_report()

        self.assertNotIn("lost_city", action_completable)
        self.assertNotIn("Dramen branch", sources)
        self.assertNotIn("Dramen branch", report["routes"])
        self.assertNotIn("Cinnamon", report["routes"])
        self.assertIn(
            "Utility:grind_dramen_branch",
            {action["id"] for action in report["unresolved_actions"]},
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
