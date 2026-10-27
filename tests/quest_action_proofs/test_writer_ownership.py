from __future__ import annotations

import ast
from pathlib import Path
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.stage_cleanups import QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID
from ankiscape.data.quest_action_proof_data import QUEST_ACTION_PROOF_RULES


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


# Source-blocked stages that no runtime path can finish yet; each comment names
# its record in memory-bank/source-audits/shared-quest-action-proofs-2026-08-31.md
# (design-thread queue 3.31). Remove a triple in the change that wires its emitter.
_UNEMITTED_CLEANUP_ACTIONS = frozenset({
    # Audit: no Silvthrill-rod enchant target.
    ("in_aid_of_the_myreque", 6, "Enchant sapphire for the Myreque preparations"),
    # Audit: no quest-specific emerald preparation target.
    ("legacy_of_seergaze", 5, "Cast Enchant Level 2 Jewellery for the emerald preparations"),
})


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

    def test_every_cleanup_required_action_has_a_runtime_emitter(self):
        # A cleanup names its required action as free text, and the stage gate
        # accepts it only once a stage auto action or a proof rule records that
        # exact string; without one the stage can never be finished.
        emitted_actions = _quest_action_owners("auto_actions").keys() | {
            proof
            for _required_proofs, emitted_proofs in QUEST_ACTION_PROOF_RULES.values()
            for proof in emitted_proofs
        }

        self.maxDiff = None
        self.assertSetEqual(
            {
                (quest_id, cleanup.stage, action_id)
                for quest_id, cleanups in QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID.items()
                for cleanup in cleanups
                for action_id in cleanup.add_required_actions
                if action_id not in emitted_actions
            },
            _UNEMITTED_CLEANUP_ACTIONS,
        )


if __name__ == "__main__":
    unittest.main()
