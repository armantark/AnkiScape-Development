import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core import constants
from ankiscape.core.constants import ITEM_DEFINITIONS, QUEST_DATA
from ankiscape.data import combat_data, shop_data, vinesweeper_data
from ankiscape.logic import shop_logic
from ankiscape.logic_pure.logic_pure import (
    combat_target_locked_reasons_pure,
    target_unlock_locked_reasons_pure,
)
from tools.audit_item_reachability import (
    _claim_item_sources,
    _close_actions,
    _close_quest_reachability,
    _item_option_groups,
    _quest_completion_sets,
    _quest_stage_sources,
    _stage_satisfiability,
    build_reachability_report,
)


class TestItemReachabilityAudit(unittest.TestCase):
    def test_item_option_groups_parse_live_nested_mapping_shape(self):
        self.assertEqual(
            _item_option_groups(
                (
                    ({"Bronze hatchet": 1}, {"Iron hatchet": 1}),
                    ({"Earth talisman": 1}, {"Omni-talisman": 1}),
                )
            ),
            (
                {"Bronze hatchet": 1, "Iron hatchet": 1},
                {"Earth talisman": 1, "Omni-talisman": 1},
            ),
        )

    def test_item_option_groups_parse_dataclass_pair_shape(self):
        self.assertEqual(
            _item_option_groups(
                (
                    (("Bronze hatchet", 1), ("Iron hatchet", 1)),
                    (("Earth talisman", 1), ("Omni-talisman", 1)),
                )
            ),
            (
                {"Bronze hatchet": 1, "Iron hatchet": 1},
                {"Earth talisman": 1, "Omni-talisman": 1},
            ),
        )

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

    def test_lost_city_shamus_action_has_a_runtime_emitter(self):
        report = build_reachability_report()
        missing_actions = {
            action
            for row in report["blocked_quest_stage_products"]
            if row["quest_id"] == "lost_city"
            for action in row["missing_required_actions"]
        }

        self.assertNotIn("Find Shamus in the Lumbridge Swamp tree", missing_actions)

    def test_waterfall_quest_dialogue_and_tomb_actions_have_runtime_emitters(self):
        report = build_reachability_report()
        missing_actions = {
            action
            for row in report["blocked_quest_stage_products"]
            if row["quest_id"] == "waterfall_quest"
            for action in row["missing_required_actions"]
        }

        self.assertEqual(
            missing_actions,
            set(),
            "Waterfall Quest still blocks on a specific action",
        )

    def test_lost_tribe_has_no_blocked_stage_products(self):
        report = build_reachability_report()
        blocked_quest_ids = {
            row["quest_id"]
            for row in report["blocked_quest_stage_products"]
        }

        self.assertNotIn("the_lost_tribe", blocked_quest_ids)

    def test_gertrudes_cat_dialogue_actions_have_runtime_emitters(self):
        report = build_reachability_report()
        missing_actions = {
            action
            for row in report["blocked_quest_stage_products"]
            if row["quest_id"] == "gertrudes_cat"
            for action in row["missing_required_actions"]
        }

        self.assertEqual(
            missing_actions,
            set(),
            "Gertrude's Cat still blocks on a specific action",
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

    def test_the_golem_throne_claim_requires_reachable_chisel_and_hammer(self):
        claim_id = "the_golem_thammarons_throne_gems"
        claim_data = {claim_id: constants.CLAIM_DATA[claim_id]}
        args = (
            claim_data,
            {"the_golem"},
            {"Ruby", "Emerald", "Sapphire"},
            {"runecrafting": 1},
        )

        blocked_sources, blocked_counts = _claim_item_sources(
            *args,
            {"Chisel": 1},
            set(),
        )
        sources, counts = _claim_item_sources(
            *args,
            {"Chisel": 1, "Hammer": 1},
            set(),
        )

        self.assertEqual(blocked_sources, {})
        self.assertEqual(blocked_counts, {})
        self.assertEqual(
            sources,
            {
                "Ruby": {f"claim:{claim_id}"},
                "Emerald": {f"claim:{claim_id}"},
                "Sapphire": {f"claim:{claim_id}"},
            },
        )
        self.assertEqual(counts, {"Ruby": 2, "Emerald": 2, "Sapphire": 2})

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

    def test_conditional_source_closure_unlocks_a_further_quest(self):
        quest_data = {
            "source_gate": {
                "display_name": "Source Gate",
                "rewards": {},
                "stage_requirements": (),
            },
            "consumer": {
                "display_name": "Consumer",
                "rewards": {"Final reward": 1},
                "stage_requirements": (
                    {"stage": 1, "required_inventory": {"Gated drop": 1}},
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
            {"Gated drop", "Final reward"},
            lambda _encounter: True,
            conditional_seed_sources=(
                {
                    "id": "combat:gated_target",
                    "items": {"Gated drop"},
                    "repeatable_items": {"Gated drop"},
                    "is_accessible": lambda completable, _startable, _reachable, _progress: (
                        "source_gate" in completable
                    ),
                },
            ),
        )

        self.assertEqual(completed, {"source_gate", "consumer"})
        self.assertEqual(seed_sources["Gated drop"], {"combat:gated_target"})
        self.assertEqual(seed_sources["Final reward"], {"quest:consumer"})

    def test_utility_runtime_gates_participate_in_the_fixed_point(self):
        action_data = {
            "quest_gated_utility": {
                "status": "implemented",
                "quest_requirements": ("missing_utility_quest",),
                "outputs": {"Quest-gated utility marker": 1},
            },
            "level_gated_utility": {
                "status": "implemented",
                "skill_requirements": {"magic": 1000},
                "outputs": {"Level-gated utility marker": 1},
            },
            "option_gated_utility": {
                "status": "implemented",
                "required_item_options": (("Missing option A", "Missing option B"),),
                "outputs": {"Option-gated utility marker": 1},
            },
            "any_gated_utility": {
                "status": "implemented",
                "any_requirements": ("Missing dose A", "Missing dose B"),
                "outputs": {"Any-gated utility marker": 1},
            },
        }

        with patch.dict(constants.UTILITY_ACTIVITY_DATA, action_data):
            report = build_reachability_report()

        for marker in (
            "Quest-gated utility marker",
            "Level-gated utility marker",
            "Option-gated utility marker",
            "Any-gated utility marker",
        ):
            with self.subTest(marker=marker):
                self.assertIsNone(report["routes"].get(marker))

    def test_utility_material_options_accept_a_reachable_alternative(self):
        action_data = {
            "utility_alternative_input": {
                "status": "implemented",
                "outputs": {"Reachable utility alternative": 1},
            },
            "utility_material_options": {
                "status": "implemented",
                "requirements": {"Placeholder material": 1},
                "material_options": {
                    "Placeholder material": ("Missing material", "Reachable utility alternative"),
                },
                "outputs": {"Utility material option marker": 1},
            },
        }

        with patch.dict(constants.UTILITY_ACTIVITY_DATA, action_data):
            report = build_reachability_report()

        self.assertEqual(
            report["routes"].get("Utility material option marker"),
            "Utility:utility_material_options",
        )

    def test_utility_gate_probe_has_reachable_materials(self):
        report = build_reachability_report()

        self.assertEqual(
            report["routes"].get("Bullseye lantern (lit)"),
            "Utility:light_bullseye_lantern",
        )
        self.assertNotIn(
            "Utility:light_bullseye_lantern",
            {row["id"] for row in report["unresolved_actions"]},
        )

    def test_repeatable_stage_does_not_require_its_consumed_item(self):
        gate = _stage_satisfiability(
            {
                "stage": 1,
                "consumed_inventory": {"Clean snake weed": 1},
                "produced_inventory": {"Grimy snake weed": 1},
                "repeatable_until_consumed": True,
            },
            {},
            set(),
            set(),
            set(),
            lambda _encounter: True,
        )

        self.assertEqual(gate["missing_required_items"], {})

    def test_raw_started_action_gate_opens_when_quest_can_start(self):
        quest_data = {
            "started_gate_test": {
                "display_name": "Started Gate Test",
                "stage_requirements": (
                    {"stage": 1, "required_actions": ("Impossible action",)},
                ),
            },
            "started_gate_consumer": {
                "display_name": "Started Gate Consumer",
                "rewards": {"Wimpy feather": 1},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "required_inventory": {"Started gate marker": 1},
                    },
                ),
            },
        }
        action_data = {
            "started_gate_test_action": {
                "status": "implemented",
                "quest_gate": "started_gate_test",
                "quest_gate_state": "started",
                "outputs": {"Started gate marker": 1},
            },
            "completed_gate_test_action": {
                "status": "implemented",
                "quest_gate": "started_gate_test",
                "quest_gate_state": "completed",
                "outputs": {"Completed gate marker": 1},
            },
        }

        with (
            patch.dict(constants.QUEST_DATA, quest_data),
            patch.dict(constants.UTILITY_ACTIVITY_DATA, action_data),
        ):
            report = build_reachability_report()

        self.assertEqual(
            report["routes"].get("Started gate marker"),
            "Utility:started_gate_test_action",
        )
        self.assertIsNone(report["routes"].get("Completed gate marker"))
        self.assertEqual(
            report["routes"].get("Wimpy feather"),
            "quest:started_gate_consumer",
        )

    def test_runtime_source_gates_follow_repaired_quest_closure(self):
        gated_targets = {
            "gorak": {
                "stats": {"hitpoints": 1},
                "drops": {"guaranteed": (("Gorak claws", 1),)},
                "quest_gate": "a_fairy_tale_ii_cure_a_queen",
                "quest_gate_state": "started",
                "quest_gate_label": "Reach stage 5 of A Fairy Tale II - Cure a Queen",
            },
            "suqah": {
                "stats": {"hitpoints": 1},
                "drops": {"guaranteed": (("Suqah tooth", 1),)},
                "quest_gate": "lunar_diplomacy",
                "quest_gate_state": "started",
                "quest_gate_label": "Start Lunar Diplomacy",
            },
            "glacor": {
                "stats": {"hitpoints": 1},
                "drops": {"guaranteed": (("Shards of armadyl", 1),)},
                "quest_gate": "ritual_of_the_mahjarrat",
                "quest_gate_label": "Complete Ritual of the Mahjarrat",
            },
        }
        expected_locks = {
            "gorak": ("Reach stage 5 of A Fairy Tale II - Cure a Queen",),
            "suqah": ("Start Lunar Diplomacy",),
            "glacor": ("Complete Ritual of the Mahjarrat",),
        }
        for target_id, locks in expected_locks.items():
            with self.subTest(target=target_id):
                self.assertEqual(
                    combat_target_locked_reasons_pure(
                        {},
                        target_id,
                        gated_targets,
                    ),
                    locks,
                )

        baba_yaga = shop_data.SHOP_DATA["baba_yagas_magic_shop_afterquest"]
        self.assertEqual(
            shop_logic.shop_access_lock_reason_pure({"quests": {}}, baba_yaga),
            "Requires Lunar Diplomacy",
        )

        with patch.dict(combat_data.COMBAT_ENEMY_DATA, gated_targets):
            report = build_reachability_report()

        expected_routes = {
            "Gorak claws": "combat:gorak",
            "Suqah tooth": "combat:suqah",
            "Shards of armadyl": None,
        }
        for item_name, expected_route in expected_routes.items():
            with self.subTest(item=item_name):
                self.assertEqual(report["routes"].get(item_name), expected_route)
        self.assertEqual(
            report["routes"].get("Astral rune"),
            "quest:lunar_diplomacy",
        )

    def test_inaccessible_shop_services_stay_blocked_with_reachable_inputs(self):
        input_source = {
            "service_gate_test_inputs": {
                "status": "implemented",
                "outputs": {
                    "Potion flask": 1,
                    "Attack potion (3)": 1,
                    "Attack flask (3)": 1,
                },
            },
        }
        generic_service = {
            "test_quest_locked_conversion": {
                "id": "test_quest_locked_conversion",
                "visibility": "visible",
                "action_type": "item_conversion",
                "inputs": ({"item_name": "Coins", "quantity": 1},),
                "outputs": ({"item_name": "Locked service marker", "quantity": 1},),
                "price": 0,
                "access": {
                    "kind": "quest",
                    "quest_id": "as_a_first_resort",
                    "label": "As a First Resort",
                },
            },
        }

        with (
            patch.dict(constants.UTILITY_ACTIVITY_DATA, input_source),
            patch.dict(shop_data.SHOP_SERVICES, generic_service),
        ):
            report = build_reachability_report()

        self.assertIn("Potion flask", report["routes"])
        self.assertIn("Attack potion (3)", report["routes"])
        self.assertIn("Attack flask (3)", report["routes"])
        self.assertIsNone(report["routes"].get("Attack flask (6)"))
        self.assertIsNone(report["routes"].get("Locked service marker"))
        unresolved = {
            action["id"]: action
            for action in report["unresolved_actions"]
        }
        for action_id in (
            "Shop service:teplin_fill_potion_flasks:Attack potion",
            "Shop service:teplin_decant_flasks_to_vials:Attack potion",
            "Shop service:test_quest_locked_conversion",
        ):
            with self.subTest(action=action_id):
                self.assertEqual(unresolved[action_id]["missing"], [])

    def test_numeric_shop_service_gate_opens_at_reachable_partial_stage(self):
        quest_data = {
            "service_progress_test": {
                "display_name": "Service Progress Test",
                "stages": 5,
                "stage_requirements": (
                    {"stage": 5, "required_actions": ("Impossible action",)},
                ),
            },
        }
        service = {
            "test_progress_locked_conversion": {
                "id": "test_progress_locked_conversion",
                "visibility": "visible",
                "action_type": "item_conversion",
                "inputs": ({"item_name": "Coins", "quantity": 1},),
                "outputs": (
                    {"item_name": "Progress service marker", "quantity": 1},
                ),
                "price": 0,
                "access": {
                    "kind": "quest",
                    "quest_id": "service_progress_test",
                    "stage": 5,
                    "label": "Service Progress Test stage 5",
                },
            },
        }

        with (
            patch.dict(constants.QUEST_DATA, quest_data),
            patch.dict(shop_data.SHOP_SERVICES, service),
        ):
            report = build_reachability_report()

        self.assertEqual(
            report["routes"].get("Progress service marker"),
            "Shop service:test_progress_locked_conversion",
        )

    def test_named_encounter_only_targets_do_not_seed_drops(self):
        target_ids = (
            "menaphite_thug",
            "cockroach_soldier",
            "temple_trekking_ambush",
            "troll_invasion_wave_front",
        )
        marker_by_target = {
            target_id: f"Encounter-only marker: {target_id}"
            for target_id in target_ids
        }
        encounter_targets = {
            target_id: {
                **combat_data.COMBAT_ENEMY_DATA[target_id],
                "drops": {
                    "guaranteed": ((marker_by_target[target_id], 1),),
                },
            }
            for target_id in target_ids
        }

        with patch.dict(
            combat_data.COMBAT_ENEMY_DATA,
            encounter_targets,
            clear=True,
        ):
            report = build_reachability_report()

        for target_id, marker in marker_by_target.items():
            with self.subTest(target=target_id):
                self.assertIsNone(report["routes"].get(marker))

    def test_combat_sources_use_every_runtime_access_gate(self):
        gated_fields = {
            "encounter": {"encounter_only": True},
            "slayer": {"required_slayer_level": 1000},
            "skill": {"skill_requirements": {"agility": 1000}},
            "item": {"required_items": {"Missing combat key": 1}},
            "item_option": {
                "required_item_options": (("Missing option A", "Missing option B"),),
            },
            "finisher": {
                "finisher": {
                    "item": "Missing finisher",
                    "threshold_lifepoints": 1,
                    "consume": True,
                },
            },
            "quest": {"required_quest": "missing_combat_quest"},
            "start_equipment": {
                "start_equipment": {
                    "slot": "head",
                    "items": ("Missing combat helmet",),
                },
            },
            "hazard": {
                "environmental_hazard": {
                    "display_name": "Test hazard",
                    "dose_items": ("Missing hazard dose",),
                },
            },
            "restricted_weapon": {
                "restricted_weapon": {
                    "melee_weapons": ("Missing restricted weapon",),
                },
            },
            "warriors_guild": {
                "warriors_guild_gate": True,
                "warriors_guild_target": "cyclossus",
            },
        }
        targets = {
            target_id: {
                "display_name": target_id.title(),
                "stats": {"hitpoints": 1},
                "drops": {"guaranteed": ((f"{target_id} marker", 1),)},
                **fields,
            }
            for target_id, fields in gated_fields.items()
        }
        targets["open"] = {
            "display_name": "Open",
            "stats": {"hitpoints": 1},
            "drops": {"guaranteed": (("open marker", 1),)},
        }

        with patch.dict(combat_data.COMBAT_ENEMY_DATA, targets, clear=True):
            report = build_reachability_report()

        for target_id in gated_fields:
            with self.subTest(target=target_id):
                self.assertIsNone(report["routes"].get(f"{target_id} marker"))
        self.assertEqual(report["routes"].get("open marker"), "combat:open")

    def test_warriors_guild_progression_unlocks_defender_drops(self):
        report = build_reachability_report()

        for defender in (
            "Bronze defender",
            "Iron defender",
            "Steel defender",
            "Black defender",
            "Mithril defender",
            "Adamant defender",
            "Rune defender",
        ):
            with self.subTest(defender=defender):
                self.assertEqual(report["routes"].get(defender), "combat:cyclops")
        self.assertEqual(
            report["routes"].get("Cyclopean helmet"),
            "combat:cyclossus",
        )
        self.assertEqual(
            report["routes"].get("Dragon defender"),
            "combat:cyclossus",
        )

    def test_combat_sources_accept_runtime_finisher_loadout_variants(self):
        input_source = {
            "finisher_gate_test_inputs": {
                "status": "implemented",
                "outputs": {
                    "Simple finisher": 1,
                    "Worn finisher": 1,
                    "Empty finisher": 1,
                    "Finisher reload": 1,
                },
            },
        }
        targets = {
            "simple_finisher": {
                "stats": {"hitpoints": 1},
                "finisher": {
                    "item": "Simple finisher",
                    "threshold_lifepoints": 1,
                    "consume": True,
                },
                "drops": {"guaranteed": (("simple finisher marker", 1),)},
            },
            "worn_finisher": {
                "stats": {"hitpoints": 1},
                "finisher": {
                    "item": "Worn finisher",
                    "threshold_lifepoints": 1,
                    "must_be_worn": True,
                },
                "drops": {"guaranteed": (("worn finisher marker", 1),)},
            },
            "reloadable_finisher": {
                "stats": {"hitpoints": 1},
                "finisher": {
                    "item": "Reloadable finisher",
                    "threshold_lifepoints": 1,
                    "charge_items": (("Charged finisher", 10),),
                    "empty_item": "Empty finisher",
                    "reload_item": "Finisher reload",
                    "reload_charges": 10,
                },
                "drops": {"guaranteed": (("reloadable finisher marker", 1),)},
            },
        }

        with (
            patch.dict(constants.UTILITY_ACTIVITY_DATA, input_source),
            patch.dict(combat_data.COMBAT_ENEMY_DATA, targets, clear=True),
        ):
            report = build_reachability_report()

        for marker in (
            "simple finisher marker",
            "worn finisher marker",
            "reloadable finisher marker",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, report["routes"])

    def test_combat_sources_accept_runtime_equipment_and_hazard_loadouts(self):
        input_source = {
            "combat_gate_test_inputs": {
                "status": "implemented",
                "outputs": {
                    "Required combat helmet": 1,
                    "Waterskin (4)": 1,
                    "Magic shortbow": 1,
                    "Broad arrows": 1,
                    "Slayer's staff": 1,
                    "Mind rune": 4,
                    "Death rune": 1,
                },
            },
        }
        targets = {
            "start_equipment": {
                "stats": {"hitpoints": 1},
                "start_equipment": {
                    "slot": "head",
                    "items": ("Required combat helmet",),
                },
                "drops": {"guaranteed": (("start equipment marker", 1),)},
            },
            "environmental_hazard": {
                "stats": {"hitpoints": 1},
                "environmental_hazard": {
                    "display_name": "Desert heat",
                    "dose_items": ("Waterskin (4)",),
                },
                "drops": {"guaranteed": (("hazard marker", 1),)},
            },
            "ranged_restriction": {
                "stats": {"hitpoints": 1},
                "restricted_weapon": {
                    "melee_weapons": ("Missing spear",),
                    "ranged_ammunition": ("Broad arrows",),
                },
                "drops": {"guaranteed": (("ranged restriction marker", 1),)},
            },
            "magic_restriction": {
                "stats": {"hitpoints": 1},
                "restricted_weapon": {
                    "melee_weapons": ("Missing spear",),
                    "magic_spells": ("magic_dart",),
                },
                "drops": {"guaranteed": (("magic restriction marker", 1),)},
            },
        }

        with (
            patch.dict(constants.UTILITY_ACTIVITY_DATA, input_source),
            patch.dict(combat_data.COMBAT_ENEMY_DATA, targets, clear=True),
        ):
            report = build_reachability_report()

        for marker in (
            "start equipment marker",
            "hazard marker",
            "ranged restriction marker",
            "magic restriction marker",
        ):
            with self.subTest(marker=marker):
                self.assertIsNotNone(report["routes"].get(marker))

    def test_rune_essence_to_rune_dust_chain_remains_reachable(self):
        registered_items = {
            definition.storage_key for definition in ITEM_DEFINITIONS
        }
        _blocked, completed, _startable, _proofs = _close_quest_reachability(
            (),
            {},
            {},
            set(),
            {"rune_mysteries": QUEST_DATA["rune_mysteries"]},
            registered_items,
            lambda _encounter: True,
        )
        report = build_reachability_report()
        locked_player = {"quests": {}}
        unlocked_player = {
            "quests": {
                "rune_mysteries": {"started": True, "completed": True},
            },
        }

        self.assertEqual(completed, {"rune_mysteries"})
        self.assertEqual(
            target_unlock_locked_reasons_pure(
                locked_player,
                "mining",
                "rune_essence",
                constants.QUEST_UNLOCK_RULES,
            ),
            ("Rune Mysteries",),
        )
        self.assertEqual(
            target_unlock_locked_reasons_pure(
                unlocked_player,
                "mining",
                "rune_essence",
                constants.QUEST_UNLOCK_RULES,
            ),
            (),
        )
        self.assertNotIn(
            "Mining:rune_essence",
            {action["id"] for action in report["unresolved_actions"]},
        )
        self.assertIn("Rune essence", report["routes"])
        self.assertEqual(report["routes"].get("Rune shards"), "Utility:make_rune_shards")
        self.assertEqual(report["routes"].get("Rune dust"), "Utility:grind_rune_shards")

    def test_unlock_target_alias_uses_the_canonical_runtime_gate(self):
        report = build_reachability_report()

        self.assertIsNone(report["routes"].get("Death talisman staff"))
        self.assertIn(
            "Runecrafting:bind_death_talisman_staff",
            {action["id"] for action in report["unresolved_actions"]},
        )

    def test_magic_sources_use_runtime_state_gates(self):
        unavailable_target = {
            "runtime_unavailable_test": {
                "id": "runtime_unavailable_test",
                "display_name": "Runtime unavailable test",
                "status": "implemented",
                "level": 1,
                "consumer_unavailable": "Runtime consumer unavailable",
                "outputs": {"Unavailable Magic marker": 1},
            },
        }

        with patch.dict(constants.MAGIC_DATA, unavailable_target):
            report = build_reachability_report()

        self.assertIsNone(report["routes"].get("Digsite pendant (5)"))
        self.assertEqual(report["routes"].get("Peach"), "Magic:bones_to_peaches")
        self.assertIsNone(report["routes"].get("Unavailable Magic marker"))

    def test_report_matches_player_finishable_quest_baseline(self):
        report = build_reachability_report()

        self.assertEqual(report["action_count"], 1663)
        self.assertEqual(report["reachable_item_count"], 2302)
        self.assertEqual(report["routes"].get("Living water"), "quest-stage:druidic_ritual:2")
        self.assertEqual(report["routes"].get("Wandering wyrmwood"), "quest-stage:druidic_ritual:3")
        self.assertEqual(report["routes"].get("Stone fish"), "quest-stage:druidic_ritual:4")
        self.assertEqual(report["routes"].get("Black prism"), "quest:zogre_flesh_eaters")
        self.assertNotIn("Relicym's balm", report["routes"])
        self.assertEqual(report["routes"].get("Stone scales"), "quest-stage:druidic_ritual:5")
        self.assertEqual(report["routes"].get("Ourg bones"), "quest-combat:zogre_flesh_eaters:zogre_flesh_eaters_slash_bash_111")
        self.assertEqual(
            report["routes"].get("Ointment of imbalance"),
            "quest-stage:druidic_ritual:6",
        )
        self.assertTrue(
            {"Combat Training Camp", "Coin", "Law Rune"}.isdisjoint(report["routes"])
        )
        self.assertEqual(report["orphan_input_count"], 165)
        self.assertEqual(report["root_orphan_count"], 32)
        self.assertEqual(report["cascade_orphan_count"], 133)
        self.assertEqual(report["unresolved_action_count"], 252)
        self.assertEqual(report["seed_item_count"], 1217)
        self.assertEqual(report["completable_quest_count"], 52)
        self.assertIn("Use the rotten apple to sabotage the mourner food stores", report["earned_quest_action_proofs"])
        self.assertEqual(len(report["blocked_quest_stage_products"]), 138)
        blocked_quest_ids = {row["quest_id"] for row in report["blocked_quest_stage_products"]}
        self.assertEqual(
            {
                "clock_tower",
                "deadliest_catch",
                "gertrudes_cat",
                "goblin_diplomacy",
                "icthlarins_little_helper",
                "lost_city",
                "monks_friend",
                "smoking_kills",
                "some_like_it_cold",
                "song_from_the_depths",
                "the_restless_ghost",
                "tribal_totem",
                "wolf_whistle",
            }
            & blocked_quest_ids,
            set(),
        )
        self.assertNotIn("the_lost_tribe", blocked_quest_ids)
        self.assertNotIn("zogre_flesh_eaters", blocked_quest_ids)
        orphan_items = {row["item"] for row in report["orphan_inputs"]}
        quest_reward_items = {
            item
            for quest in QUEST_DATA.values()
            for item in quest.get("rewards", {})
        }
        self.assertEqual(
            orphan_items & quest_reward_items,
            {"Blood talisman", "Jade vine seed"},
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

        # The stage actions are emitted now, so the branch is granted by
        # resolving Lost City stage 4 and Cinnamon's real grind resolves with it.
        self.assertNotIn("lost_city", action_completable)
        self.assertNotIn("Dramen branch", sources)
        self.assertEqual(report["routes"].get("Dramen branch"), "quest-stage:lost_city:4")
        self.assertEqual(report["routes"].get("Cinnamon"), "Utility:grind_dramen_branch")
        self.assertNotIn(
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
