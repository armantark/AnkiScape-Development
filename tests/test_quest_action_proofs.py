from __future__ import annotations

import ast
import copy
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
import ankiscape.core.storage_pure as storage_pure
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
            "config_version": 121,
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
        self.assertNotIn("quest_stage_actions", migrated)

    def test_v122_proofs_survive_upgrade_and_legacy_stage_actions_are_dropped(self):
        current = {
            "config_version": 122,
            "quest_stage_actions": {"biohazard": [BIOHAZARD_CAULDRON_ACTION]},
            "quest_action_proofs": ["proof-b", "proof-a", "proof-b", None],
        }

        migrated = migrate_loaded_data(current, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["quest_action_proofs"], ["proof-a", "proof-b"])
        self.assertNotIn("quest_stage_actions", migrated)

    def test_retired_proof_is_subtracted_and_no_longer_satisfies_a_gate(self):
        current = {
            "config_version": 122,
            "quest_action_proofs": [MOURNER_FOOD_STORES_PROOF, "surviving proof"],
        }
        with patch.object(
            storage_pure,
            "RETIRED_QUEST_ACTION_PROOFS",
            {MOURNER_FOOD_STORES_PROOF},
        ):
            migrated = migrate_loaded_data(current, ORE_DATA, ITEM_DEFINITIONS)
        target_id = "target_quest"
        migrated["quests"][target_id] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        quest_data = {
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

        self.assertEqual(migrated["quest_action_proofs"], ["surviving proof"])
        self.assertEqual(
            tuple(
                blocker.get("action_id")
                for blocker in quest_current_stage_blockers_pure(
                    migrated,
                    target_id,
                    quest_data,
                )
                if blocker["kind"] == "required_action"
            ),
            (MOURNER_FOOD_STORES_PROOF,),
        )

    def test_next_config_bump_retires_current_version_proofs(self):
        current = {
            "config_version": CURRENT_CONFIG_VERSION,
            "quest_action_proofs": [MOURNER_FOOD_STORES_PROOF, "surviving proof"],
        }
        with patch.multiple(
            storage_pure,
            CURRENT_CONFIG_VERSION=CURRENT_CONFIG_VERSION + 1,
            RETIRED_QUEST_ACTION_PROOFS={MOURNER_FOOD_STORES_PROOF},
        ):
            migrated = migrate_loaded_data(current, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION + 1)
        self.assertEqual(migrated["quest_action_proofs"], ["surviving proof"])


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
            "quest_action_proofs": [],
            "quest_route_states": {},
            "pending_skill_exp_rewards": {},
        }
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


def _quest_action_owners(field):
    owners = {}
    for quest_id, quest in QUEST_DATA.items():
        for requirement in quest.get("stage_requirements", ()):
            for action_id in requirement.get(field, ()):
                owners.setdefault(action_id, set()).add(quest_id)
    return owners


def _production_store_sites(root):
    proof_call_sites = set()
    proof_mention_counts = {}
    retired_write_sites = set()
    retired_mention_counts = {}
    for path in _production_python_paths(root):
        source = path.read_text(encoding="utf-8")
        relative_path = str(path.relative_to(root))
        proof_count = source.count("quest_action_proofs")
        if proof_count:
            proof_call_sites.update(_proof_calls_in_source(path, root, source))
            proof_mention_counts[relative_path] = proof_count
        retired_count = source.count("quest_stage_actions")
        if retired_count:
            retired_write_sites.update(_retired_store_write_sites(path, root, source))
            retired_mention_counts[relative_path] = retired_count
    return proof_call_sites, proof_mention_counts, retired_write_sites, retired_mention_counts


_MUTATING_METHOD_NAMES = {
    "add",
    "append",
    "clear",
    "difference_update",
    "discard",
    "extend",
    "insert",
    "intersection_update",
    "pop",
    "popitem",
    "remove",
    "reverse",
    "setdefault",
    "sort",
    "symmetric_difference_update",
    "update",
}


def _has_string_key(node, key):
    return isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) and node.slice.value == key


def _references_retired_store(node, aliases):
    if isinstance(node, ast.Name) and node.id in aliases:
        return True
    if any(_has_string_key(child, "quest_stage_actions") for child in ast.walk(node)):
        return True
    return any(
        isinstance(child, ast.Call)
        and isinstance(child.func, ast.Attribute)
        and child.func.attr in {"get", "pop", "setdefault"}
        and child.args
        and isinstance(child.args[0], ast.Constant)
        and child.args[0].value == "quest_stage_actions"
        for child in ast.walk(node)
    )


def _assigned_names(target):
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        return {name for item in target.elts for name in _assigned_names(item)}
    return set()


def _retired_store_aliases_from_assignment(node, aliases):
    if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
        return set()
    if not _references_retired_store(node.value, aliases):
        return set()
    targets = node.targets if isinstance(node, ast.Assign) else (node.target,)
    return {name for target in targets for name in _assigned_names(target)}


def _retired_store_aliases(tree):
    aliases = set()
    while True:
        discovered = set()
        for node in ast.walk(tree):
            discovered.update(_retired_store_aliases_from_assignment(node, aliases))
        if discovered <= aliases:
            return aliases
        aliases.update(discovered)


def _target_writes_retired_store(target, aliases, augmented=False):
    return (
        _has_string_key(target, "quest_stage_actions")
        or isinstance(target, (ast.Subscript, ast.Attribute))
        and _references_retired_store(target.value, aliases)
        or augmented
        and isinstance(target, ast.Name)
        and target.id in aliases
    )


def _dict_has_string_key(node, key):
    return isinstance(node, ast.Dict) and any(
        isinstance(item, ast.Constant) and item.value == key
        for item in node.keys
    )


def _retired_store_mutation(node, aliases):
    if not isinstance(node.func, ast.Attribute):
        return ""
    method = node.func.attr
    if method in _MUTATING_METHOD_NAMES and _references_retired_store(node.func.value, aliases):
        return method
    if (
        method == "setdefault"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == "quest_stage_actions"
    ):
        return method
    if method == "update" and (
        any(keyword.arg == "quest_stage_actions" for keyword in node.keywords)
        or any(_dict_has_string_key(argument, "quest_stage_actions") for argument in node.args)
    ):
        return method
    return ""


class _RetiredStoreWriteVisitor(ast.NodeVisitor):
    def __init__(self, relative_path, function_names, aliases):
        self.relative_path = relative_path
        self.function_names = function_names
        self.aliases = aliases
        self.sites = set()

    def _record(self, node, operation):
        self.sites.add(
            (
                self.relative_path,
                self.function_names.get(node, "<module>"),
                node.lineno,
                operation,
            )
        )

    def _visit_assignment(self, node, targets, augmented=False):
        if any(
            _target_writes_retired_store(target, self.aliases, augmented)
            for target in targets
        ):
            self._record(node, "assignment")
        self.generic_visit(node)

    def visit_Assign(self, node):
        self._visit_assignment(node, node.targets)

    def visit_AnnAssign(self, node):
        self._visit_assignment(node, (node.target,))

    def visit_AugAssign(self, node):
        self._visit_assignment(node, (node.target,), augmented=True)

    def visit_Call(self, node):
        operation = _retired_store_mutation(node, self.aliases)
        if operation:
            self._record(node, operation)
        self.generic_visit(node)


def _retired_store_write_sites(path, root, source):
    tree = ast.parse(source, filename=str(path))
    visitor = _RetiredStoreWriteVisitor(
        str(path.relative_to(root)),
        _function_names_by_node(tree),
        _retired_store_aliases(tree),
    )
    visitor.visit(tree)
    return visitor.sites


class TestQuestActionProofWriterOwnership(unittest.TestCase):
    def test_retired_store_census_detects_assignments_and_mutation_methods(self):
        root = Path("/synthetic")
        source = """def write(data):
    data["quest_stage_actions"] = {}
    data.setdefault("quest_stage_actions", {})
    actions = data.get("quest_stage_actions", {})
    popped = data.pop("quest_stage_actions", {})
    actions["quest"] = []
    popped["quest"] = []
    actions.update({"quest": ["action"]})
    data["quest_stage_actions"]["quest"].append("action")
"""

        self.assertEqual(
            _retired_store_write_sites(root / "writer.py", root, source),
            {
                ("writer.py", "write", 2, "assignment"),
                ("writer.py", "write", 3, "setdefault"),
                ("writer.py", "write", 6, "assignment"),
                ("writer.py", "write", 7, "assignment"),
                ("writer.py", "write", 8, "update"),
                ("writer.py", "write", 9, "append"),
            },
        )

    def test_catalog_action_ids_are_safe_for_global_proofs(self):
        auto_action_owners = _quest_action_owners("auto_actions")
        required_action_owners = _quest_action_owners("required_actions")

        self.assertEqual(len(auto_action_owners), 538)
        self.assertEqual(
            {
                action_id: tuple(sorted(owners))
                for action_id, owners in auto_action_owners.items()
                if len(owners) != 1
            },
            {},
        )
        self.assertEqual(
            {
                (action_id, auto_quest, required_quest)
                for action_id in auto_action_owners.keys() & required_action_owners.keys()
                for auto_quest in auto_action_owners[action_id]
                for required_quest in required_action_owners[action_id]
                if auto_quest != required_quest
            },
            set(),
        )

    def test_production_proof_writers_are_genuine_action_seams(self):
        call_sites, mention_counts, retired_writes, retired_mentions = _production_store_sites(
            Path(__file__).resolve().parents[1]
        )

        self.assertEqual(
            call_sites,
            {
                ("logic/shop_logic.py", "apply_shop_buy_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic/shop_logic.py", "_apply_service_like", "record_runtime_quest_action_proofs_pure"),
                ("logic/shop_logic.py", "rollback_shop_event_pure", "retract_shop_event_quest_action_proofs_pure"),
                ("logic_pure/logic_pure_quest.py", "_consume_quest_current_stage_items", "record_quest_stage_action_proofs_pure"),
                ("runtime/runtime_actions_shared.py", "_record_action", "record_runtime_quest_action_proofs_pure"),
            },
        )
        self.assertEqual(
            mention_counts,
            {
                "core/storage_pure.py": 8,
                "logic/shop_logic.py": 6,
                "logic_pure/logic_pure_quest.py": 1,
                "logic_pure/logic_pure_state.py": 5,
                "logic_pure/quest_action_proofs.py": 24,
                "runtime/runtime_actions_shared.py": 3,
            },
        )
        self.assertEqual(retired_writes, set())
        self.assertEqual(retired_mentions, {"core/storage_pure.py": 1})


if __name__ == "__main__":
    unittest.main()
