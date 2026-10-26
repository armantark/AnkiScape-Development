import unittest
from unittest.mock import patch
import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core import constants
from ankiscape.data import combat_data, shop_data
from ankiscape.logic import shop_logic
from ankiscape.logic_pure.logic_pure import combat_target_locked_reasons_pure
from tools.audit_item_reachability import _close_quest_reachability, _stage_satisfiability, build_reachability_report
from tests.reachability.live_report import live_reachability_report


class TestItemReachabilityAudit(unittest.TestCase):
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
        report = live_reachability_report()

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
