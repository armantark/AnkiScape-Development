import unittest
import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from tools.audit_item_reachability import _close_actions, _close_quest_reachability, _quest_completion_sets, _quest_stage_sources
from tests.reachability.live_report import live_reachability_report


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

        _blocked, completed, _startable, _proofs = _close_quest_reachability(
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

        _blocked, completed, _startable, _proofs = _close_quest_reachability(
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

        _blocked, completed, _startable, _proofs = _close_quest_reachability(
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
        report = live_reachability_report()

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
