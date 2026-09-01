from __future__ import annotations

import ast
import copy
import sys
from pathlib import Path
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.quest_action_proof_data import (
    BIOHAZARD_CAULDRON_ACTION,
    DO_NO_EVIL_MAMULET_MOULD_PROOF,
    FREMENNIK_ISLES_YAK_HIDE_PROOF,
    MOURNER_FOOD_STORES_PROOF,
    THAKKRAD_CURED_YAK_HIDE_PROOF,
)
from ankiscape.logic.shop_logic import apply_shop_buy_pure, apply_shop_service_pure, rollback_shop_event_pure
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure,
    quest_current_stage_blockers_pure,
)
from ankiscape.logic_pure.quest_action_proofs import (
    quest_action_proof_completed_pure,
    quest_action_proofs_for_reachable_events_pure,
    record_quest_stage_action_proofs_pure,
    record_runtime_quest_action_proofs_pure,
    sanitize_quest_action_proofs_pure,
)
from ankiscape.runtime.runtime_actions import handle_crafting_answer
from ankiscape.tools.quest_action_proof_reachability import reachable_quest_action_proof_events
from tests.test_combat_quest_gate import _answer_review, _maxed_player_for_quest
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context


class TestQuestActionProofStore(unittest.TestCase):
    def test_store_is_unique_global_membership(self):
        player = {"quest_action_proofs": ["proof-b", "proof-a", "proof-b", 7]}

        self.assertEqual(
            sanitize_quest_action_proofs_pure(player["quest_action_proofs"]),
            ["proof-a", "proof-b"],
        )
        self.assertTrue(quest_action_proof_completed_pure(player, "proof-a"))
        self.assertFalse(quest_action_proof_completed_pure(player, "proof-c"))
        self.assertFalse(
            record_runtime_quest_action_proofs_pure(
                player,
                "crafting",
                "unmapped_target",
            )
        )

    def test_runtime_bindings_are_idempotent_and_support_genuine_sequences(self):
        player = {"quest_action_proofs": []}

        self.assertFalse(
            record_runtime_quest_action_proofs_pure(
                player,
                "crafting",
                "leather_yakhide_armour_10824",
            )
        )
        self.assertEqual(player["quest_action_proofs"], [])
        self.assertTrue(
            record_runtime_quest_action_proofs_pure(
                player,
                "shop_service",
                "thakkrad_cure_yak_hide",
            )
        )
        self.assertTrue(
            record_runtime_quest_action_proofs_pure(
                player,
                "crafting",
                "leather_yakhide_armour_10824",
            )
        )
        self.assertFalse(
            record_runtime_quest_action_proofs_pure(
                player,
                "crafting",
                "leather_yakhide_armour_10824",
            )
        )
        self.assertEqual(
            player["quest_action_proofs"],
            sorted((THAKKRAD_CURED_YAK_HIDE_PROOF, FREMENNIK_ISLES_YAK_HIDE_PROOF)),
        )

    def test_reachability_sources_obey_the_same_multi_step_rules(self):
        crafting_only = quest_action_proofs_for_reachable_events_pure(
            (),
            {("crafting", "leather_yakhide_armour_10824")},
        )
        self.assertNotIn(FREMENNIK_ISLES_YAK_HIDE_PROOF, crafting_only)

        reachable = quest_action_proofs_for_reachable_events_pure(
            (),
            {
                ("shop_buy", "hamabs_crafting_emporium:3:4020"),
                ("shop_service", "thakkrad_cure_yak_hide"),
                ("crafting", "leather_yakhide_armour_10824"),
            },
        )
        self.assertIn(DO_NO_EVIL_MAMULET_MOULD_PROOF, reachable)
        self.assertIn(FREMENNIK_ISLES_YAK_HIDE_PROOF, reachable)

        wrong_row = reachable_quest_action_proof_events(
            (),
            (),
            {"Ring mould": {"shop:hamabs_crafting_emporium"}},
        )
        self.assertNotIn(("shop_buy", "hamabs_crafting_emporium:3:4020"), wrong_row)
        exact_row = reachable_quest_action_proof_events(
            (),
            (),
            {"M'amulet mould": {"shop:hamabs_crafting_emporium"}},
        )
        self.assertIn(("shop_buy", "hamabs_crafting_emporium:3:4020"), exact_row)

    def test_quest_stage_action_records_exact_and_cross_quest_proofs(self):
        player = {"quest_action_proofs": []}

        changed = record_quest_stage_action_proofs_pure(
            player,
            "biohazard",
            (BIOHAZARD_CAULDRON_ACTION,),
        )

        self.assertTrue(changed)
        self.assertEqual(
            player["quest_action_proofs"],
            sorted((BIOHAZARD_CAULDRON_ACTION, MOURNER_FOOD_STORES_PROOF)),
        )

    def test_old_saves_start_empty_without_telemetry_inventory_or_local_backfill(self):
        legacy = {
            "config_version": CURRENT_CONFIG_VERSION - 1,
            "inventory": {"M'amulet mould": 1, "Cured yak-hide": 2},
            "action_telemetry": {
                "by_action": {
                    "crafting:leather_yakhide_armour": {"successes": 99},
                },
            },
            "quest_stage_actions": {
                "biohazard": [BIOHAZARD_CAULDRON_ACTION],
            },
            "quest_action_proofs": [
                DO_NO_EVIL_MAMULET_MOULD_PROOF,
                MOURNER_FOOD_STORES_PROOF,
            ],
        }

        migrated = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["quest_action_proofs"], [])
        self.assertEqual(
            migrated["quest_stage_actions"]["biohazard"],
            [BIOHAZARD_CAULDRON_ACTION],
        )

    def test_current_save_proofs_are_sanitized_and_preserved(self):
        current = {
            "config_version": CURRENT_CONFIG_VERSION,
            "quest_action_proofs": ["proof-b", "proof-a", "proof-b", None],
        }

        migrated = migrate_loaded_data(current, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["quest_action_proofs"], ["proof-a", "proof-b"])


class TestQuestActionProofIntegration(unittest.TestCase):
    def test_pure_quest_flow_reads_a_proof_earned_by_another_quest(self):
        source_id = "biohazard"
        target_id = "target_quest"
        quest_data = {
            source_id: {
                "stages": 1,
                "point_reward": 0,
                "rewards": {},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "auto_actions": (BIOHAZARD_CAULDRON_ACTION,),
                        "source": "test source",
                    },
                ),
            },
            target_id: {
                "stages": 1,
                "point_reward": 0,
                "rewards": {},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "required_actions": (MOURNER_FOOD_STORES_PROOF,),
                        "source": "test source",
                    },
                ),
            },
        }
        player = {
            "inventory": {},
            "quests": {
                source_id: {"started": True, "progress": 1, "completed": False},
                target_id: {"started": True, "progress": 1, "completed": False},
            },
            "quest_points": 0,
            "quest_stage_actions": {},
            "quest_action_proofs": [],
            "quest_route_states": {},
            "pending_skill_exp_rewards": {},
        }
        player["quest_stage_actions"] = {target_id: [MOURNER_FOOD_STORES_PROOF]}
        self.assertEqual(
            tuple(
                blocker["kind"]
                for blocker in quest_current_stage_blockers_pure(
                    player,
                    target_id,
                    quest_data,
                )
            ),
            ("required_action",),
        )

        player, progressed, _completed = apply_quest_progress_pure(
            player,
            source_id,
            quest_data,
        )
        self.assertTrue(progressed)
        self.assertEqual(player["current_quest"], source_id)
        self.assertIn(MOURNER_FOOD_STORES_PROOF, player["quest_action_proofs"])
        self.assertEqual(
            quest_current_stage_blockers_pure(player, target_id, quest_data),
            (),
        )

        player, progressed, completed = apply_quest_progress_pure(
            player,
            target_id,
            quest_data,
        )
        self.assertTrue(progressed)
        self.assertTrue(completed)

    def test_shop_purchase_proves_recovery_only_after_a_successful_buy(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        denied, result = apply_shop_buy_pure(
            player,
            "hamabs_crafting_emporium",
            "hamabs_crafting_emporium:3:4020",
        )
        self.assertFalse(result["allowed"])
        self.assertNotIn(
            DO_NO_EVIL_MAMULET_MOULD_PROOF,
            denied["quest_action_proofs"],
        )

        player["inventory"]["Coins"] = 10_000
        player["quests"]["monkey_madness"] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        bought, result = apply_shop_buy_pure(
            player,
            "hamabs_crafting_emporium",
            "hamabs_crafting_emporium:3:4020",
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(bought["inventory"]["M'amulet mould"], 1)
        self.assertIn(
            DO_NO_EVIL_MAMULET_MOULD_PROOF,
            bought["quest_action_proofs"],
        )

    def test_shop_purchase_rollback_retracts_its_proof(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["inventory"]["Coins"] = 10_000
        player["quests"]["monkey_madness"] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        bought, buy = apply_shop_buy_pure(
            player,
            "hamabs_crafting_emporium",
            "hamabs_crafting_emporium:3:4020",
        )
        self.assertTrue(buy["allowed"])
        self.assertIn(DO_NO_EVIL_MAMULET_MOULD_PROOF, bought["quest_action_proofs"])

        restored, rollback = rollback_shop_event_pure(bought, buy["event_id"])

        self.assertTrue(rollback["allowed"])
        self.assertEqual(restored["inventory"]["M'amulet mould"], 0)
        self.assertEqual(restored["inventory"]["Coins"], 10_000)
        self.assertNotIn(DO_NO_EVIL_MAMULET_MOULD_PROOF, restored["quest_action_proofs"])

    def test_yak_hide_proof_requires_service_then_real_crafting(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["the_fremennik_isles"] = {
            "started": True,
            "progress": 5,
            "completed": False,
        }
        player["inventory"].update({"Yak-hide": 1, "Thread": 1, "Coins": 100})
        player["crafting_level"] = 99

        player, service = apply_shop_service_pure(
            player,
            "thakkrad_cure_yak_hide",
        )
        self.assertTrue(service["allowed"])
        self.assertIn(THAKKRAD_CURED_YAK_HIDE_PROOF, player["quest_action_proofs"])
        self.assertNotIn(FREMENNIK_ISLES_YAK_HIDE_PROOF, player["quest_action_proofs"])

        player["current_craft"] = "leather_yakhide_armour_10824"
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertTrue(handle_crafting_answer(_context(player, calls, [0.0])))
        self.assertEqual(calls["saves"], 1)
        self.assertIn(FREMENNIK_ISLES_YAK_HIDE_PROOF, player["quest_action_proofs"])

        inventory_only = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        inventory_only["inventory"].update({"Cured yak-hide": 1, "Thread": 1})
        inventory_only["crafting_level"] = 99
        inventory_only["current_craft"] = "leather_yakhide_armour_10824"
        self.assertTrue(handle_crafting_answer(_context(inventory_only, random_values=[0.0])))
        self.assertNotIn(
            FREMENNIK_ISLES_YAK_HIDE_PROOF,
            inventory_only["quest_action_proofs"],
        )


class TestQuestActionProofReviewFlow(unittest.TestCase):
    def setUp(self) -> None:
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_real_review_action_satisfies_another_quests_global_requirement(self):
        addon = _load_addon_as_package("ankiscape_quest_action_proof_e2e")
        saved = []
        errors = []
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: saved.append(copy.deepcopy(addon.player_data))
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: errors.append((title, message))

        player = _maxed_player_for_quest("biohazard")
        player["quests"]["biohazard"] = {
            "started": True,
            "progress": 7,
            "completed": False,
        }
        player["quests"]["mournings_end_part_i"] = {
            "started": True,
            "progress": 5,
            "completed": False,
        }
        player["inventory"]["Rotten apple"] = 1
        player["inventory"]["Sieve"] = 1
        player["current_quest"] = "biohazard"
        before = quest_current_stage_blockers_pure(
            player,
            "mournings_end_part_i",
            QUEST_DATA,
        )
        self.assertIn(
            MOURNER_FOOD_STORES_PROOF,
            {blocker.get("action_id") for blocker in before},
        )
        addon.player_data = player
        addon.current_skill = "Quests"
        addon._REVIEW_UNDO_STACK.clear()

        _answer_review(addon)

        self.assertFalse(errors)
        self.assertEqual(addon.player_data["current_quest"], "biohazard")
        self.assertIn(MOURNER_FOOD_STORES_PROOF, addon.player_data["quest_action_proofs"])
        self.assertEqual(len(saved), 1)
        self.assertIn(MOURNER_FOOD_STORES_PROOF, saved[0]["quest_action_proofs"])
        after = quest_current_stage_blockers_pure(
            addon.player_data,
            "mournings_end_part_i",
            QUEST_DATA,
        )
        self.assertNotIn(
            MOURNER_FOOD_STORES_PROOF,
            {blocker.get("action_id") for blocker in after},
        )
        self.assertIn(
            "Complete Mourning's End Part I stage 5 objective",
            {blocker.get("action_id") for blocker in after},
        )


_PROOF_RECORDER_NAMES = {
    "record_runtime_quest_action_proofs_pure",
    "record_quest_stage_action_proofs_pure",
    "retract_shop_event_quest_action_proofs_pure",
}


def _function_names_by_node(tree):
    names = {}
    for function in ast.walk(tree):
        if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for node in ast.walk(function):
                names[node] = function.name
    return names


def _called_name(node):
    return node.func.id if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) else ""


def _proof_calls_in_source(path, root, source):
    tree = ast.parse(source, filename=str(path))
    function_names = _function_names_by_node(tree)
    relative_path = str(path.relative_to(root))
    return {
        (relative_path, function_names.get(node, "<module>"), _called_name(node))
        for node in ast.walk(tree)
        if _called_name(node) in _PROOF_RECORDER_NAMES
    }


def _production_python_paths(root):
    yield root / "__init__.py"
    for directory in ("core", "logic", "logic_pure", "runtime", "ui", "data", "generated"):
        yield from sorted((root / directory).rglob("*.py"))


def _production_proof_sites(root):
    call_sites = set()
    mention_counts = {}
    for path in _production_python_paths(root):
        source = path.read_text(encoding="utf-8")
        count = source.count("quest_action_proofs")
        if count:
            call_sites.update(_proof_calls_in_source(path, root, source))
            mention_counts[str(path.relative_to(root))] = count
    return call_sites, mention_counts


class TestQuestActionProofWriterOwnership(unittest.TestCase):
    def test_production_proof_writers_are_genuine_action_seams(self):
        call_sites, mention_counts = _production_proof_sites(
            Path(__file__).resolve().parents[1]
        )

        self.assertEqual(
            call_sites,
            {
                ("logic/shop_logic.py", "apply_shop_buy_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic/shop_logic.py", "_apply_service_like", "record_runtime_quest_action_proofs_pure"),
                ("logic/shop_logic.py", "rollback_shop_event_pure", "retract_shop_event_quest_action_proofs_pure"),
                ("logic_pure/logic_pure_quest.py", "_mark_quest_stage_actions", "record_quest_stage_action_proofs_pure"),
                ("runtime/runtime_actions_shared.py", "_record_action", "record_runtime_quest_action_proofs_pure"),
            },
        )
        self.assertEqual(
            mention_counts,
            {
                "core/storage_pure.py": 6,
                "logic/shop_logic.py": 6,
                "logic_pure/logic_pure_quest.py": 1,
                "logic_pure/logic_pure_state.py": 5,
                "logic_pure/quest_action_proofs.py": 24,
                "runtime/runtime_actions_shared.py": 3,
            },
        )


if __name__ == "__main__":
    unittest.main()
