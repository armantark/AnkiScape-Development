"""Material edges for normal actions and quest-owned supply recipes."""

from typing import Any, Mapping

from ...data.mining_data import MINING_PICKAXES
from ...data.woodcutting_data import WOODCUTTING_AXES


def requirements(spec: Mapping[str, Any], _names) -> tuple[set[str], tuple[set[str], ...]]:
    required = (
        _names(spec.get("required_tools"))
        | _names(spec.get("requirements"))
        | _names(spec.get("required_items"))
        | _names(spec.get("tools"))
        | _names(spec.get("rune_cost"))
    )
    alternatives: list[set[str]] = []
    material_options = spec.get("material_options", {}) or {}
    if isinstance(material_options, Mapping):
        for material, options in material_options.items():
            option_names = _names(options)
            if material in required and option_names:
                required.remove(material)
                alternatives.append(option_names)
    for option_group in spec.get("required_item_options", ()) or ():
        option_names = _names(option_group)
        if option_names:
            alternatives.append(option_names)
    for key in ("any_requirements", "essence_items", "bait_options", "reachability_inputs"):
        options = _names(spec.get(key))
        if options:
            alternatives.append(options)
    return required, tuple(alternatives)


def quest_supply_actions(quest_data):
    # A generic quest tool is a family of alternatives, not a nonexistent item.
    return {
        f"{quest_id}:{index}": dict(
            recipe["action"], quest_gate=quest_id, quest_gate_state="started",
            material_options={
                "Pickaxe": tuple(tool.display_name for tool in MINING_PICKAXES),
                "Hatchet": tuple(axe.display_name for axe in WOODCUTTING_AXES),
            },
        )
        for quest_id, quest in quest_data.items()
        for index, recipe in enumerate(quest.get("supply_recipes", ()))
    }
