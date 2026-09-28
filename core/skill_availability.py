"""The save fields the menu's skill availability reads, so it recomputes only when one changes."""

from collections.abc import Mapping

from .constants import (
    COOKING_DATA,
    CRAFTING_DATA,
    FIREMAKING_DATA,
    FLETCHING_DATA,
    HUNTER_DATA,
    QUEST_UNLOCK_RULES,
    RUNECRAFTING_DATA,
    SMITHING_DATA,
)


def _material_option_names(material_options) -> set[str]:
    names = set()
    for name, alternatives in material_options.items():
        names.add(str(name))
        if isinstance(alternatives, (tuple, list, set)):
            names.update(str(alternative) for alternative in alternatives)
    return names


def _spec_requirement_item_names(spec) -> set[str]:
    names = set()
    for key in ("requirements", "required_items", "tools"):
        values = spec.get(key, {})
        if isinstance(values, Mapping):
            names.update(str(name) for name in values)
    material_options = spec.get("material_options", {})
    if isinstance(material_options, Mapping):
        names |= _material_option_names(material_options)
    return names


def _catalog_requirement_item_names(*catalogs) -> set[str]:
    names = set()
    for catalog in catalogs:
        for spec in catalog.values():
            if isinstance(spec, Mapping):
                names |= _spec_requirement_item_names(spec)
    return names


def _runecrafting_item_names(spec) -> set[str]:
    names = set()
    for key in ("component_rune", "consumed_talisman", "input_item", "talisman_item"):
        item_name = spec.get(key)
        if isinstance(item_name, str) and item_name:
            names.add(item_name)
    names.update(str(item_name) for item_name in spec.get("essence_items", ()) or ())
    return names


def _inventory_names() -> tuple[str, ...]:
    names = _catalog_requirement_item_names(
        SMITHING_DATA,
        CRAFTING_DATA,
        FLETCHING_DATA,
        FIREMAKING_DATA,
        HUNTER_DATA,
        COOKING_DATA,
    )
    for spec in RUNECRAFTING_DATA.values():
        names |= _runecrafting_item_names(spec)
    names.update({"Pure essence", "Tiara", "Wicked hood"})
    return tuple(sorted(names))


def _level_keys() -> tuple[str, ...]:
    keys = {
        "smithing_level",
        "crafting_level",
        "fletching_level",
        "firemaking_level",
        "hunter_level",
        "cooking_level",
        "runecrafting_level",
    }
    for spec in HUNTER_DATA.values():
        requirements = spec.get("skill_requirements", {})
        if isinstance(requirements, Mapping):
            keys.update(f"{skill_id}_level" for skill_id in requirements)
    return tuple(sorted(keys))


def _unlock_requirements():
    skill_ids = {"crafting", "fletching", "firemaking", "hunter", "cooking", "runecrafting"}
    for rule in QUEST_UNLOCK_RULES:
        if not isinstance(rule, Mapping) or rule.get("skill_id") not in skill_ids:
            continue
        for requirement in rule.get("requirements", ()) or ():
            if isinstance(requirement, Mapping):
                yield requirement


def _unlock_requirement_ids(field, always=()) -> tuple[str, ...]:
    ids = set(always)
    for requirement in _unlock_requirements():
        value = requirement.get(field)
        if isinstance(value, str) and value:
            ids.add(value)
    return tuple(sorted(ids))


_INVENTORY_NAMES = _inventory_names()
_LEVEL_KEYS = _level_keys()
_QUEST_IDS = _unlock_requirement_ids("quest_id", always=("rune_mysteries",))
_ABILITY_IDS = _unlock_requirement_ids("ability_id")


def _freeze(value):
    if isinstance(value, Mapping):
        return tuple(sorted((str(key), _freeze(item)) for key, item in value.items()))
    if isinstance(value, (tuple, list, set)):
        return tuple(_freeze(item) for item in value)
    return value


def _quest_progress(quests) -> tuple:
    rows = []
    for quest_id in _QUEST_IDS:
        progress = quests.get(quest_id, {}) or {}
        rows.append((quest_id, bool(progress.get("started")), bool(progress.get("completed"))))
    return tuple(rows)


def _carried_wicked_hoods(player_data, current_runecrafting: str):
    carried = player_data.get("carried_inventory", {}) or {}
    carried_view = carried.get(current_runecrafting, {}) if isinstance(carried, Mapping) else {}
    return carried_view.get("Wicked hood", 0) if isinstance(carried_view, Mapping) else 0


def skill_availability_fingerprint(player_data) -> tuple:
    inventory = player_data.get("inventory", {}) or {}
    quests = player_data.get("quests", {}) or {}
    abilities = player_data.get("unlocked_abilities", ()) or ()
    current_runecrafting = str(player_data.get("current_runecrafting", "") or "")
    carried_hoods = _carried_wicked_hoods(player_data, current_runecrafting)
    equipment = player_data.get("equipment", {}) or {}
    return (
        tuple((key, player_data.get(key, 1)) for key in _LEVEL_KEYS),
        _freeze(player_data.get("skilling_current_levels", {})),
        tuple((name, inventory.get(name, 0)) for name in _INVENTORY_NAMES),
        _quest_progress(quests),
        tuple((ability_id, ability_id in abilities) for ability_id in _ABILITY_IDS),
        bool(player_data.get("magic_imbue_active", False)),
        equipment.get("head") if isinstance(equipment, Mapping) else None,
        _freeze(player_data.get("wicked_hood", {})),
        current_runecrafting,
        carried_hoods,
    )
