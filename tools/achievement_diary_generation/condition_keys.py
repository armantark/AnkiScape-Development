"""Condition key resolution for generated diary rows.

A condition whose key names nothing the runtime writes reads zero forever, so
the row can never complete. That failure is silent: the panel renders an
honest-looking 0/1. ``resolve_condition_key`` is the check that turns it into
a generation failure, and ``tests/test_achievement_diaries.py`` runs the same
check over the shipped catalog so a hand-edit cannot slip past it either.
"""

from __future__ import annotations

import ast
import functools
from pathlib import Path

from ankiscape.data.quest_data import quests_as_dict
from ankiscape.logic_pure.shop_diary_transactions import shop_diary_transaction_counter_key_pure
from tools.achievement_diary_ledger import resolve_named_counter, resolve_special_counter

ROOT = Path(__file__).resolve().parents[2]
QUEST_DATA = quests_as_dict()

# Where each skill's action ids come from. A skill absent here is refused rather
# than waved through, because "no registry" must never read as "anything goes".
_SKILL_ACTION_REGISTRIES = {
    "agility": ("ankiscape.core.constants", "AGILITY_TARGETS_BY_ID"),
    "construction": ("ankiscape.core.constants", "CONSTRUCTION_DATA"),
    "cooking": ("ankiscape.core.constants", "COOKING_DATA"),
    "crafting": ("ankiscape.core.constants", "CRAFTING_DATA"),
    "firemaking": ("ankiscape.core.constants", "FIREMAKING_DATA"),
    "fishing": ("ankiscape.core.constants", "FISHING_DATA"),
    "fletching": ("ankiscape.core.constants", "FLETCHING_DATA"),
    "herblore": ("ankiscape.core.constants", "HERBLORE_DATA"),
    "hunter": ("ankiscape.core.constants", "HUNTER_DATA"),
    "magic": ("ankiscape.core.constants", "MAGIC_DATA"),
    "mining": ("ankiscape.core.constants", "ORE_DATA"),
    "prayer": ("ankiscape.core.constants", "PRAYER_DATA"),
    "runecrafting": ("ankiscape.core.constants", "RUNECRAFTING_DATA"),
    "smithing": ("ankiscape.core.constants", "SMITHING_DATA"),
    "summoning": ("ankiscape.data.summoning_data", "SUMMONING_ACTIONS_BY_ID"),
    "thieving": ("ankiscape.data.thieving_data", "THIEVING_TARGETS"),
    "utility": ("ankiscape.core.constants", "UTILITY_ACTIVITY_DATA"),
    "woodcutting": ("ankiscape.core.constants", "TREE_DATA"),
}

# Where the ledger is written from. Activity runtimes record actions whose ids
# are literals rather than rows of a skill's target table, so the registries
# above are unioned with every literal pair these files actually emit.
_LEDGER_WRITE_SITES = ("runtime", "logic")
_LEDGER_WRITE_CALLS = ("_record_action", "record_achievement_progress_pure")


def _import_attr(module_name: str, attribute: str):
    import importlib

    return getattr(importlib.import_module(module_name), attribute)


def _parsed_sources(paths):
    """Syntax trees of ``paths``, skipping any file that does not parse."""

    for path in paths:
        try:
            yield ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue


def _string_assignments(tree: ast.Module):
    """``(name, literal)`` for every top-level ``NAME = "literal"`` in ``tree``."""

    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Constant):
            continue
        if isinstance(node.value.value, str):
            yield from (
                (target.id, node.value.value)
                for target in node.targets
                if isinstance(target, ast.Name)
            )


@functools.lru_cache(maxsize=1)
def _module_level_strings() -> dict:
    """Every ``NAME = "literal"`` in the add-on, for resolving action-id names.

    Activity runtimes pass constants such as ``SHOOTING_STAR_ACTIVITY_ID``
    rather than a bare string, and those constants are the action id.
    """

    found: dict[str, set] = {}
    add_on_sources = (
        path
        for path in ROOT.rglob("*.py")
        if not {".git", "__pycache__", "tests"}.intersection(path.parts)
    )
    for tree in _parsed_sources(add_on_sources):
        for name, literal in _string_assignments(tree):
            found.setdefault(name, set()).add(literal)
    return found


def _literal_strings(node: ast.AST) -> set:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.Name):
        return set(_module_level_strings().get(node.id, ()))
    return set()


def _ledger_write_calls(tree: ast.Module):
    """Every ledger write in ``tree``; its skill id and action id are arguments 1 and 2."""

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and len(node.args) >= 3:
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name in _LEDGER_WRITE_CALLS:
                yield node


@functools.lru_cache(maxsize=1)
def _emitted_ledger_actions() -> dict:
    """``skill id -> action ids`` the runtime can actually record."""

    emitted = {
        skill_id: set(_import_attr(module_name, attribute))
        for skill_id, (module_name, attribute) in _SKILL_ACTION_REGISTRIES.items()
    }
    write_site_sources = (
        path for directory in _LEDGER_WRITE_SITES for path in (ROOT / directory).rglob("*.py")
    )
    for tree in _parsed_sources(write_site_sources):
        for call in _ledger_write_calls(tree):
            for skill_id in _literal_strings(call.args[1]):
                emitted.setdefault(skill_id, set()).update(_literal_strings(call.args[2]))
    return emitted


@functools.lru_cache(maxsize=1)
def _emitted_ledger_outputs() -> dict:
    """``skill id -> output item names`` the ledger can hold under that skill."""

    from ankiscape.core.storage_pure import _achievement_seed_items

    emitted = {
        skill_id: set(items) for skill_id, items in _achievement_seed_items().items()
    }
    for skill_id, (module_name, attribute) in _SKILL_ACTION_REGISTRIES.items():
        bucket = emitted.setdefault(skill_id, set())
        for spec in _import_attr(module_name, attribute).values():
            source = spec if isinstance(spec, dict) else vars(spec)
            if source.get("output_item"):
                bucket.add(str(source["output_item"]))
            bucket.update(str(name) for name in (source.get("outputs") or {}))
    return emitted


@functools.lru_cache(maxsize=1)
def _default_save() -> dict:
    from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
    from ankiscape.core.storage_pure import default_player_data

    return default_player_data(ORE_DATA, ITEM_DEFINITIONS)


def _resolve_ledger_key(kind: str, key: str) -> str:
    skill_id, separator, action_id = key.partition(":")
    if not separator or not skill_id or not action_id:
        return f"{kind} key {key!r} is not '<skill id>:<id>'"
    registry = (
        _emitted_ledger_outputs() if kind == "ledger_output" else _emitted_ledger_actions()
    )
    if skill_id not in registry:
        return (
            f"{kind} key {key!r} names skill {skill_id!r}, which has no registry;"
            " add it to _SKILL_ACTION_REGISTRIES before shipping a row under it"
        )
    if action_id not in registry[skill_id]:
        return f"{kind} key {key!r} is never recorded under skill {skill_id!r}"
    return ""


def _resolve_ledger_action_family(key: str) -> str:
    skill_id, separator, family_id = key.partition(":")
    if not separator or not skill_id or not family_id:
        return f"ledger_action_family key {key!r} is not '<skill id>:<family id>'"
    registry_spec = _SKILL_ACTION_REGISTRIES.get(skill_id)
    if registry_spec is None:
        return f"ledger_action_family key {key!r} names no registered skill"
    actions = _import_attr(*registry_spec)
    matches = [
        action_id
        for action_id, action in actions.items()
        if getattr(action, "family", None) == family_id
    ]
    if not matches:
        return f"ledger_action_family key {key!r} matches no recorded actions"
    emitted = _emitted_ledger_actions().get(skill_id, set())
    missing = sorted(set(matches) - emitted)
    if missing:
        return f"ledger_action_family key {key!r} includes actions never recorded: {missing}"
    return ""


def _resolve_shop_transaction(key: str) -> str:
    transaction_type, separator, remainder = key.partition("|")
    shop_id, row_separator, row_id = remainder.partition("|")
    if not separator or not row_separator:
        return f"shop_transaction key {key!r} is not '<type>|<shop id>|<row id>'"
    if not shop_diary_transaction_counter_key_pure(transaction_type, shop_id, row_id):
        return f"shop_transaction key {key!r} is not recorded by the narrow diary seam"
    return ""


def _resolve_save_path(kind: str, key: str) -> str:
    node = _default_save()
    parts = key.split(".")
    for index, part in enumerate(parts):
        if not isinstance(node, dict):
            return f"{kind} key {key!r} walks through a non-mapping at {part!r}"
        if part not in node:
            if index == len(parts) - 1:
                return ""  # an absent per-key leaf is the zero case, not a typo
            return f"{kind} key {key!r} has no {part!r} in a default save"
        node = node[part]
    return ""


_resolve_state_path = functools.partial(_resolve_save_path, "state_equals")


def _resolve_combat_kill(key: str) -> str:
    from ankiscape.core.constants import COMBAT_ENEMY_DATA

    return "" if key in COMBAT_ENEMY_DATA else f"combat_kill key {key!r} names no enemy"


def _resolve_hold_item(key: str) -> str:
    from ankiscape.core.constants import ITEM_DEFINITIONS

    names = {row.storage_key for row in ITEM_DEFINITIONS}
    return "" if key in names else f"hold_item key {key!r} names no item"


def _resolve_equipped_item(key: str) -> str:
    from ankiscape.core.constants import EQUIPMENT_DATA

    slot, separator, item_name = key.partition("|")
    item = EQUIPMENT_DATA.get(item_name)
    if not separator or item is None:
        return f"equipped_item key {key!r} names no equipment item"
    if item.slot != slot:
        return f"equipped_item key {key!r} uses slot {slot!r}, expected {item.slot!r}"
    return ""


def _resolve_derived_value(key: str) -> str:
    registry = _import_attr(
        "ankiscape.logic.achievement_diary_derived", "DIARY_DERIVED_VALUES"
    )
    ceilings = _import_attr(
        "ankiscape.logic.achievement_diary_derived", "DIARY_DERIVED_VALUE_CEILINGS"
    )
    if key not in registry:
        return f"derived_value {key!r} is not in DIARY_DERIVED_VALUES"
    if key not in ceilings:
        return f"derived_value {key!r} has no DIARY_DERIVED_VALUE_CEILINGS entry"
    return ""


def _resolve_quest(key: str) -> str:
    return "" if key in QUEST_DATA else f"quest key {key!r} names no shipped quest"


def _resolve_skill_level(key: str) -> str:
    get_skill = _import_attr("ankiscape.core.skill_registry", "get_skill")
    return "" if get_skill(key) else f"skill_level key {key!r} names no skill"


def _resolve_counter(key: str) -> str:
    if (error := resolve_named_counter(key)) is not None:
        return error

    if (error := resolve_special_counter(key, _resolve_ledger_key, _resolve_state_path, QUEST_DATA)) is not None:
        return error

    parts = key.split(".")
    if parts[:2] == ["fight_caves", "kill_counts"]:
        if len(parts) != 3 or parts[2] != "ket_zek":
            return f"counter key {key!r} names no recorded Fight Caves variant"
        return ""
    # The ledger is reachable as a dotted path too, and a fresh save carries no
    # per-skill record, so route those through the ledger registries instead of
    # the save walk below.
    if parts[:2] == ["achievement_progress", "skills"] and len(parts) == 5:
        bucket = {"actions": "ledger_action", "outputs": "ledger_output"}.get(parts[3])
        if bucket is None:
            return f"counter key {key!r} names no ledger bucket"
        return _resolve_ledger_key(bucket, f"{parts[2]}:{parts[4]}")
    return _resolve_save_path("counter", key)


# A kind absent here has no key of its own to check; ``any_of`` resolves each
# alternative as its own condition.
_CONDITION_KEY_RESOLVERS = {
    "ledger_action": functools.partial(_resolve_ledger_key, "ledger_action"),
    "ledger_output": functools.partial(_resolve_ledger_key, "ledger_output"),
    "ledger_action_family": _resolve_ledger_action_family,
    "combat_kill": _resolve_combat_kill,
    "shop_transaction": _resolve_shop_transaction,
    "state_equals": _resolve_state_path,
    "hold_item": _resolve_hold_item,
    "equipped_item": _resolve_equipped_item,
    "derived_value": _resolve_derived_value,
    "quest": _resolve_quest,
    "skill_level": _resolve_skill_level,
    "counter": _resolve_counter,
}


def resolve_condition_key(kind: str, key: str, expected=None) -> str:
    """Return an error describing why ``key`` reads nothing, or ``""``."""

    if kind == "state_equals" and expected is None:
        return f"state_equals key {key!r} has no expected value"
    resolver = _CONDITION_KEY_RESOLVERS.get(kind)
    return resolver(key) if resolver else ""
