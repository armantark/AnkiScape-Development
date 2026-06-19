"""Pure target-list row metadata for Skills-hub target lists."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Optional

try:
    from .logic_pure import (
        best_mining_pickaxe_pure,
        best_woodcutting_axe_pure,
        calculate_cooking_success_probability_pure,
        calculate_firemaking_success_probability_pure,
        calculate_fishing_success_probability_pure,
        can_chop_woodcutting_target_pure,
        firemaking_target_locked_reasons_pure,
        can_open_bird_nests_pure,
        cooking_target_locked_reasons_pure,
        crafting_target_locked_reasons_pure,
        eligible_fishing_fish_pure,
        fishing_method_locked_reasons_pure,
        fletching_target_locked_reasons_pure,
        mining_target_locked_reasons_pure,
        runecrafting_locked_reasons_pure,
        smithing_target_locked_reasons_pure,
        utility_activity_locked_reasons_pure,
    )
except Exception:
    from logic_pure import (  # type: ignore
        best_mining_pickaxe_pure,
        best_woodcutting_axe_pure,
        calculate_cooking_success_probability_pure,
        calculate_firemaking_success_probability_pure,
        calculate_fishing_success_probability_pure,
        can_chop_woodcutting_target_pure,
        firemaking_target_locked_reasons_pure,
        can_open_bird_nests_pure,
        cooking_target_locked_reasons_pure,
        crafting_target_locked_reasons_pure,
        eligible_fishing_fish_pure,
        fishing_method_locked_reasons_pure,
        fletching_target_locked_reasons_pure,
        mining_target_locked_reasons_pure,
        runecrafting_locked_reasons_pure,
        smithing_target_locked_reasons_pure,
        utility_activity_locked_reasons_pure,
    )


@dataclass(frozen=True)
class TargetRowMetadata:
    """Shared contract for one selectable flat target-list row."""

    target_id: str
    label: str
    tooltip: str
    enabled: bool = True
    current: bool = False
    icon_path: Optional[str] = None
    group: str = ""
    locked_reasons: tuple[str, ...] = ()
    sort_key: tuple[object, ...] = ()


def _material_lines(requirements: Mapping[str, int], inventory: Mapping[str, int]) -> tuple[bool, str]:
    if not requirements:
        return True, "No materials required"
    ok = True
    lines = []
    for material, amount in requirements.items():
        have = inventory.get(material, 0)
        if have < amount:
            ok = False
        lines.append(f"{material} x{amount} (you have {have})")
    return ok, "\n".join(lines)


def _indented_material_lines(requirements: Mapping[str, int], inventory: Mapping[str, int]) -> str:
    if not requirements:
        return "  No materials required"
    return "\n".join(
        f"  {material} x{amount} (you have {inventory.get(material, 0)})"
        for material, amount in requirements.items()
    )


def _smithing_tier_of(spec: Mapping[str, object]) -> str:
    if spec.get("station") == "furnace":
        return str(spec.get("output_item", "")).replace(" bar", "").strip() or "Other"
    reqs = spec.get("requirements", {}) or {}
    requirements = reqs if isinstance(reqs, Mapping) else {}
    return str(next(iter(requirements), "")).replace(" bar", "").strip() or "Other"


def smithing_target_rows(
    player_data: Mapping[str, object],
    smithing_data: Mapping[str, Mapping[str, object]],
    smithing_item_images: Mapping[str, str],
    default_target: str,
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    lvl_have = int(player_data.get("smithing_level", 1) or 1)
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    current_target = player_data.get("current_smith", default_target)

    for recipe_id, spec in smithing_data.items():
        display_name = str(spec.get("display_name", spec.get("output_item", recipe_id)))
        lvl_req = int(spec.get("level", 1) or 1)
        output_item = str(spec.get("output_item", display_name))
        output_qty = int(spec.get("output_qty", 1) or 1)
        reqs = spec.get("requirements", {}) or {}
        requirements = reqs if isinstance(reqs, Mapping) else {}
        station_word = "Smelt" if spec.get("station") == "furnace" else "Forge"
        group = _smithing_tier_of(spec)

        label = f"{display_name} (Lvl {lvl_req})"
        if output_qty > 1:
            label += f" — makes {output_qty}"

        locked_reasons = smithing_target_locked_reasons_pure(
            player_data,
            recipe_id,
            smithing_data,
            quest_unlock_rules,
        )
        tooltip = (
            f"{station_word} · requires Smithing level {lvl_req}. You have {lvl_have}.\n"
            f"Output: {output_item} x{output_qty}\n"
            f"Base XP: {spec.get('exp', 0)} per action\n"
            f"Materials:\n{_indented_material_lines(requirements, inventory)}"
        )
        if locked_reasons:
            tooltip += "\nLocked due to: " + ", ".join(locked_reasons)

        rows.append(
            TargetRowMetadata(
                target_id=recipe_id,
                label=label,
                tooltip=tooltip,
                enabled=not locked_reasons,
                current=recipe_id == current_target,
                icon_path=smithing_item_images.get(output_item),
                group=group,
                locked_reasons=locked_reasons,
                sort_key=(lvl_req, 0 if spec.get("station") == "furnace" else 1, display_name),
            )
        )
    return tuple(rows)


def crafting_target_rows(
    player_data: Mapping[str, object],
    crafting_data: Mapping[str, Mapping[str, object]],
    crafted_item_images: Mapping[str, str],
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    lvl_have = int(player_data.get("crafting_level", 1) or 1)
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    current_target = player_data.get("current_craft")

    for recipe_id, spec in crafting_data.items():
        display_name = str(spec.get("display_name", recipe_id))
        lvl_req = int(spec.get("level", 1) or 1)
        output_item = str(spec.get("output_item", display_name))
        output_qty = int(spec.get("output_qty", 1) or 1)
        reqs = spec.get("requirements", {}) or {}
        requirements = reqs if isinstance(reqs, Mapping) else {}
        group = str(spec.get("family", "other"))

        label = f"{display_name} (Lvl {lvl_req})"
        if output_qty > 1:
            label += f" — makes {output_qty}"

        locked_reasons = crafting_target_locked_reasons_pure(
            player_data,
            recipe_id,
            crafting_data,
            quest_unlock_rules,
        )
        tooltip = (
            f"Requires Crafting level {lvl_req}. You have {lvl_have}.\n"
            f"Output: {output_item} x{output_qty}\n"
            f"Base XP: {spec.get('exp', 0)} per action\n"
            f"Materials:\n{_indented_material_lines(requirements, inventory)}"
        )
        if locked_reasons:
            tooltip += "\nLocked due to: " + ", ".join(locked_reasons)

        rows.append(
            TargetRowMetadata(
                target_id=recipe_id,
                label=label,
                tooltip=tooltip,
                enabled=not locked_reasons,
                current=recipe_id == current_target,
                icon_path=crafted_item_images.get(output_item) or crafted_item_images.get(display_name),
                group=group,
                locked_reasons=locked_reasons,
                sort_key=(lvl_req, display_name),
            )
        )
    return tuple(rows)


def cooking_target_rows(
    player_data: Mapping[str, object],
    cooking_data: Mapping[str, Mapping[str, object]],
    cooking_item_images: Mapping[str, str],
    default_target: str,
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    lvl_have = int(player_data.get("cooking_level", 1) or 1)
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    current_target = player_data.get("current_cooking", default_target)

    for target_id, spec in cooking_data.items():
        display_name = str(spec.get("display_name", target_id))
        lvl_req = int(spec.get("level", 1) or 1)
        output_item = str(spec.get("output_item", display_name))
        burnt_item = str(spec.get("burnt_item", "Burnt food"))
        reqs = spec.get("requirements", {}) or {}
        requirements = reqs if isinstance(reqs, Mapping) else {}
        chance = calculate_cooking_success_probability_pure(lvl_have, spec) * 100.0
        group = str(spec.get("family", "other"))
        locked_reasons = cooking_target_locked_reasons_pure(
            player_data,
            target_id,
            cooking_data,
            quest_unlock_rules,
        )
        tooltip = (
            f"Requires Cooking level {lvl_req}. You have {lvl_have}.\n"
            f"Success output: {output_item} x1\n"
            f"Burn output: {burnt_item} x1, no XP\n"
            f"Base XP: {spec.get('exp', 0)} on success\n"
            f"Success chance: {chance:.0f}% per action\n"
            f"Materials:\n{_indented_material_lines(requirements, inventory)}"
        )
        if locked_reasons:
            tooltip += "\nLocked due to: " + ", ".join(locked_reasons)

        rows.append(
            TargetRowMetadata(
                target_id=target_id,
                label=f"{display_name} (Lvl {lvl_req})",
                tooltip=tooltip,
                enabled=not locked_reasons,
                current=target_id == current_target,
                icon_path=cooking_item_images.get(output_item),
                group=group,
                locked_reasons=locked_reasons,
                sort_key=(lvl_req, display_name),
            )
        )
    return tuple(rows)


def mining_target_rows(
    player_data: Mapping[str, object],
    ore_data: Mapping[str, Mapping[str, object]],
    ore_images: Mapping[str, str],
    gem_images: Mapping[str, str],
    pickaxe_data: Mapping[str, Mapping[str, object]],
    default_target: str,
    deferred_notes: Optional[Mapping[str, str]] = None,
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    lvl_have = int(player_data.get("mining_level", 1) or 1)
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    toolbelt = player_data.get("toolbelt", {})
    tools = toolbelt if isinstance(toolbelt, Mapping) else {}
    current_target = player_data.get("current_ore", default_target)
    best_pick = best_mining_pickaxe_pure(lvl_have, inventory, tools, pickaxe_data)
    best_pick_name = best_pick.get("display_name", "a pickaxe") if best_pick else None

    for target_id, data in ore_data.items():
        display_name = str(data.get("display_name", target_id))
        lvl_req = int(data.get("level", 1) or 1)
        output_item = data.get("output_item")
        weighted = data.get("weighted_outputs", ()) or ()
        alt_item = data.get("alternate_output_item")
        alt_level = data.get("alternate_output_level")

        label = f"{display_name} (Lvl {lvl_req})"
        if weighted:
            label += " — variable output"
        elif isinstance(alt_item, str) and isinstance(alt_level, int):
            label += f" — {alt_item} at Lvl {alt_level}+"

        icon_key = output_item or display_name
        if not output_item and weighted:
            first = weighted[0]
            icon_key = first.get("item", display_name) if isinstance(first, Mapping) else display_name
        icon_path = ore_images.get(str(icon_key)) or gem_images.get(str(icon_key))

        if weighted:
            names = ", ".join(
                str(w.get("item")) for w in weighted if isinstance(w, Mapping) and w.get("item")
            )
            output_line = f"Output: variable — {names}"
        elif isinstance(alt_item, str) and isinstance(alt_level, int):
            output_line = (
                f"Output: {output_item} x1 "
                f"(becomes {alt_item} at Mining level {alt_level}+)"
            )
        elif output_item:
            output_line = f"Output: {output_item} x1"
        else:
            output_line = "Output: none"

        tooltip = (
            f"Requires Mining level {lvl_req}. You have {lvl_have}.\n"
            f"{output_line}\n"
            f"Base XP: {data.get('exp', 0)} per ore\n"
            f"Best usable pickaxe: {best_pick_name or 'none — get a pickaxe'}"
        )
        note = data.get("notes")
        if note:
            tooltip += f"\nNote: {note}"
        deferred_note = (deferred_notes or {}).get(target_id)
        if deferred_note:
            tooltip += f"\nNote: {deferred_note}"

        locked_reasons = mining_target_locked_reasons_pure(
            player_data,
            target_id,
            ore_data,
            pickaxe_data,
            quest_unlock_rules,
        )
        enabled = not locked_reasons
        if locked_reasons:
            tooltip += "\nLocked due to: " + ", ".join(locked_reasons)

        rows.append(
            TargetRowMetadata(
                target_id=target_id,
                label=label,
                tooltip=tooltip,
                enabled=enabled,
                current=target_id == current_target,
                icon_path=icon_path,
                locked_reasons=locked_reasons,
            )
        )
    return tuple(rows)


def woodcutting_target_rows(
    player_data: Mapping[str, object],
    tree_data: Mapping[str, Mapping[str, object]],
    tree_images: Mapping[str, str],
    axe_data: Mapping[str, Mapping[str, object]],
    default_target: str,
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    lvl_have = int(player_data.get("woodcutting_level", 1) or 1)
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    toolbelt = player_data.get("toolbelt", {})
    tools = toolbelt if isinstance(toolbelt, Mapping) else {}
    current_target = player_data.get("current_tree", default_target)
    best_axe = best_woodcutting_axe_pure(lvl_have, inventory, tools, axe_data)
    best_axe_name = best_axe.get("display_name", "a hatchet") if best_axe else None

    for target_id, data in tree_data.items():
        display = str(data.get("display_name", target_id))
        output_item = data.get("output_item")
        lvl_req = int(data.get("level", 1) or 1)
        xp_only = output_item is None
        label = f"{display} (Lvl {lvl_req})"
        if xp_only:
            label += " — XP only"

        output_line = "XP only — produces no logs." if xp_only else f"Output: {output_item} x1"
        tooltip = (
            f"Requires Woodcutting level {lvl_req}. You have {lvl_have}.\n"
            f"{output_line}\n"
            f"Base XP: {data.get('exp', 0)} per chop\n"
            f"Best usable hatchet: {best_axe_name or 'none — get a hatchet'}"
        )
        enabled = can_chop_woodcutting_target_pure(lvl_have, target_id, tree_data, inventory, tools, axe_data)
        if not enabled:
            reason = []
            if lvl_have < lvl_req:
                reason.append(f"level {lvl_req}")
            if best_axe is None:
                reason.append("no usable hatchet")
            if reason:
                tooltip += "\nLocked due to: " + ", ".join(reason)

        rows.append(
            TargetRowMetadata(
                target_id=target_id,
                label=label,
                tooltip=tooltip,
                enabled=enabled,
                current=target_id == current_target,
                icon_path=tree_images.get(display),
            )
        )
    return tuple(rows)


def fletching_target_rows(
    player_data: Mapping[str, object],
    fletching_data: Mapping[str, Mapping[str, object]],
    fletched_item_images: Mapping[str, str],
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    lvl_have = int(player_data.get("fletching_level", 1) or 1)
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    current_target = player_data.get("current_fletch")

    for target_key, spec in fletching_data.items():
        display_name = str(spec.get("display_name", target_key))
        output_item = str(spec.get("output_item", display_name))
        output_qty = spec.get("output_qty", 1)
        lvl_req = int(spec.get("level", 1) or 1)
        requirements = spec.get("requirements", {})
        reqs = requirements if isinstance(requirements, Mapping) else {}
        _materials_ok, mat_text = _material_lines(reqs, inventory)
        tooltip = (
            f"Requires Fletching level {lvl_req}. You have {lvl_have}.\n"
            f"Output: {output_item} x{output_qty}\nMaterials:\n{mat_text}"
        )
        locked_reasons = fletching_target_locked_reasons_pure(
            player_data,
            target_key,
            fletching_data,
            quest_unlock_rules,
        )
        enabled = not locked_reasons
        if locked_reasons:
            tooltip += "\nLocked due to: " + ", ".join(locked_reasons)

        rows.append(
            TargetRowMetadata(
                target_id=target_key,
                label=f"{display_name} (Lvl {lvl_req})",
                tooltip=tooltip,
                enabled=enabled,
                current=target_key == current_target,
                icon_path=fletched_item_images.get(output_item),
                group=str(spec.get("group", "")),
                locked_reasons=locked_reasons,
                sort_key=tuple(spec.get("sort_key", ())),
            )
        )
    return tuple(rows)


def firemaking_target_rows(
    player_data: Mapping[str, object],
    firemaking_data: Mapping[str, Mapping[str, object]],
    firemaking_item_images: Mapping[str, str],
    default_target: str,
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    lvl_have = int(player_data.get("firemaking_level", 1) or 1)
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    current_target = player_data.get("current_firemaking", default_target)

    for target_key, spec in firemaking_data.items():
        display_name = str(spec.get("display_name", target_key))
        lvl_req = int(spec.get("level", 1) or 1)
        base_xp = spec.get("exp", 0)
        requirements = spec.get("requirements", {display_name: 1})
        reqs = requirements if isinstance(requirements, Mapping) else {}
        input_item = next(iter(reqs.keys()), display_name)
        input_qty = reqs.get(input_item, 1)
        owned = inventory.get(input_item, 0)
        output_item = str(spec.get("output_item", "Ashes"))
        output_qty = spec.get("output_qty", 1)
        chance = calculate_firemaking_success_probability_pure(lvl_have, spec)
        tooltip = (
            f"Requires Firemaking level {lvl_req}. You have {lvl_have}.\n"
            f"Base XP: {base_xp} per successful burn\n"
            f"Input: {input_item} x{input_qty} (you have {owned})\n"
            f"Output: {output_item} x{output_qty}\n"
            f"Success chance: {chance:.0%} per attempt"
        )
        locked_reasons = firemaking_target_locked_reasons_pure(
            player_data,
            target_key,
            firemaking_data,
            quest_unlock_rules,
        )
        enabled = not locked_reasons
        if not enabled:
            tooltip += "\nLocked due to: " + ", ".join(locked_reasons)

        rows.append(
            TargetRowMetadata(
                target_id=target_key,
                label=f"{display_name} (Lvl {lvl_req})",
                tooltip=tooltip,
                enabled=enabled,
                current=target_key == current_target,
                icon_path=firemaking_item_images.get(str(input_item)) or firemaking_item_images.get(output_item),
                locked_reasons=locked_reasons,
            )
        )
    return tuple(rows)


def _fishing_output_lines(fish_rows: Sequence[Mapping[str, object]]) -> str:
    return ", ".join(
        f"{fish.get('output_item')} (Lvl {fish.get('level', 1)}, {fish.get('exp', 0)} XP)"
        for fish in fish_rows
    )


def _fishing_xp_text(fish_rows: Sequence[Mapping[str, object]]) -> str:
    xp_values = [float(fish.get("exp", 0)) for fish in fish_rows]
    if not xp_values:
        return "0"
    if min(xp_values) == max(xp_values):
        return f"{xp_values[0]:g}"
    return f"{min(xp_values):g}-{max(xp_values):g}"


def _fishing_materials_text(bait_options: Sequence[str], inventory: Mapping[str, int]) -> str:
    if not bait_options:
        return "No consumable materials"
    parts = [f"{bait} x1 (you have {inventory.get(bait, 0)})" for bait in bait_options]
    return parts[0] if len(parts) == 1 else "Any of " + ", ".join(parts)


def _fishing_side_req_text(fish_rows: Sequence[Mapping[str, object]]) -> str:
    parts = []
    for fish in fish_rows:
        reqs = []
        if fish.get("strength_level"):
            reqs.append(f"Strength {fish.get('strength_level')}")
        if fish.get("agility_level"):
            reqs.append(f"Agility {fish.get('agility_level')}")
        if reqs:
            parts.append(f"{fish.get('output_item')}: " + " and ".join(reqs))
    return "; ".join(parts)


def _fishing_fish_label_name(fish: Mapping[str, object]) -> str:
    fish_id = str(fish.get("id", fish.get("output_item", ""))).strip().lower()
    if fish_id.startswith("raw_"):
        fish_id = fish_id[4:]
    return fish_id.replace("_", " ")


def _fishing_fish_aliases(fish: Mapping[str, object]) -> set[str]:
    label = _fishing_fish_label_name(fish)
    output = str(fish.get("output_item", "")).strip().lower()
    if output.startswith("raw "):
        output = output[4:]
    aliases = {label, output}
    for value in tuple(aliases):
        if value.endswith("s"):
            aliases.add(value[:-1])
    return {value for value in aliases if value}


def _ordered_fishing_label_fish(
    display_name: str,
    fish_rows: Sequence[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    if "/" not in display_name or not display_name.startswith("Catch "):
        return tuple(fish_rows)

    tokens = [part.strip().lower() for part in display_name[len("Catch "):].split("/")]
    remaining = list(fish_rows)
    ordered = []
    for token in tokens:
        match = next((fish for fish in remaining if token in _fishing_fish_aliases(fish)), None)
        if match is None:
            return tuple(fish_rows)
        ordered.append(match)
        remaining.remove(match)
    ordered.extend(remaining)
    return tuple(ordered)


def _fishing_row_label(display_name: str, fish_rows: Sequence[Mapping[str, object]], fallback_level: int) -> str:
    if len(fish_rows) <= 1:
        return f"{display_name} (Lvl {fallback_level})"

    ordered = _ordered_fishing_label_fish(display_name, fish_rows)
    parts = [
        f"{_fishing_fish_label_name(fish)} (Lvl {int(fish.get('level', fallback_level) or fallback_level)})"
        for fish in ordered
    ]
    if display_name.startswith("Catch "):
        return "Catch " + "/".join(parts)
    return f"{display_name} (" + ", ".join(parts) + ")"


def fishing_target_rows(
    player_data: Mapping[str, object],
    fishing_data: Mapping[str, Mapping[str, object]],
    fishing_item_images: Mapping[str, str],
    default_target: str,
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    lvl_have = int(player_data.get("fishing_level", 1) or 1)
    strength_have = int(player_data.get("strength_level", 1) or 1)
    agility_have = int(player_data.get("agility_level", 1) or 1)
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    current_target = player_data.get("current_fishing", default_target)

    for target_key, spec in fishing_data.items():
        display_name = str(spec.get("display_name", target_key))
        raw_fish = spec.get("fish", ())
        fish_rows = tuple(raw_fish) if isinstance(raw_fish, Sequence) else ()
        bait_options = tuple(spec.get("bait_options") or ())
        lvl_req = int(spec.get("level", 1) or 1)
        eligible = eligible_fishing_fish_pure(spec, lvl_have, strength_have, agility_have)
        icon_fish = eligible[0] if eligible else (fish_rows[0] if fish_rows else {})
        chance_lines = []
        for fish in eligible:
            chance = calculate_fishing_success_probability_pure(lvl_have, fish)
            chance_lines.append(f"{fish.get('output_item')} {chance:.0%}")
        chance_text = ", ".join(chance_lines) if chance_lines else "locked"
        tooltip = (
            f"Requires Fishing level {lvl_req}. You have {lvl_have}.\n"
            f"Outputs: {_fishing_output_lines(fish_rows)}\n"
            f"Base XP: {_fishing_xp_text(fish_rows)} per catch\n"
            f"Materials: {_fishing_materials_text(bait_options, inventory)}\n"
            f"Success chance now: {chance_text}"
        )
        side_text = _fishing_side_req_text(fish_rows)
        if side_text:
            tooltip += f"\nSide levels: {side_text}"

        locked_reasons = fishing_method_locked_reasons_pure(
            player_data,
            target_key,
            fishing_data,
            quest_unlock_rules,
        )
        enabled = not locked_reasons
        if locked_reasons:
            tooltip += "\nLocked due to: " + ", ".join(locked_reasons)

        rows.append(
            TargetRowMetadata(
                target_id=target_key,
                label=_fishing_row_label(display_name, fish_rows, lvl_req),
                tooltip=tooltip,
                enabled=enabled,
                current=target_key == current_target,
                icon_path=fishing_item_images.get(icon_fish.get("output_item")) if isinstance(icon_fish, Mapping) else None,
                locked_reasons=locked_reasons,
            )
        )
    return tuple(rows)


def utility_activity_rows(
    player_data: Mapping[str, object],
    utility_activity_data: Mapping[str, Mapping[str, object]],
    utility_item_images: Mapping[str, str],
    nest_open_tables: Mapping[str, Mapping[str, object]],
    default_activity: str,
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    current_activity = player_data.get("current_utility", default_activity)

    for activity_key, spec in utility_activity_data.items():
        label = str(spec.get("display_name", activity_key))
        batch_size = spec.get("batch_size", 1)
        activity_icon = spec.get("icon_path")
        icon_path = activity_icon if isinstance(activity_icon, str) and activity_icon else None
        openable_items = spec.get("openable_items")

        if openable_items:
            have_nests = sum(inventory.get(nest, 0) for nest in openable_items)
            tooltip = (
                f"Opens up to {batch_size} bird nests per successful card. No XP.\n"
                "Rolls source seed / ring / egg contents into your bank.\n"
                f"Bird nests held: {have_nests} (drop while Woodcutting)"
            )
            locked_reasons = utility_activity_locked_reasons_pure(
                player_data,
                activity_key,
                utility_activity_data,
                quest_unlock_rules,
            )
            enabled = can_open_bird_nests_pure(inventory, nest_open_tables) and not locked_reasons
            if not enabled and "materials" in locked_reasons:
                tooltip += "\nLocked: cut trees until a bird nest drops."
            elif not enabled:
                tooltip += "\nLocked due to: " + ", ".join(locked_reasons)
        else:
            output_item = str(spec.get("output_item", label))
            if icon_path is None:
                icon_path = utility_item_images.get(output_item)
            output_qty = spec.get("output_qty", 1)
            requirements = spec.get("requirements", {})
            reqs = requirements if isinstance(requirements, Mapping) else {}
            _, mat_text = _material_lines(reqs, inventory)
            tooltip = (
                f"Processes up to {batch_size} per successful card. No skill XP.\n"
                f"Output: {output_item} x{output_qty} per item\nMaterials:\n{mat_text}"
            )
            locked_reasons = utility_activity_locked_reasons_pure(
                player_data,
                activity_key,
                utility_activity_data,
                quest_unlock_rules,
            )
            enabled = not locked_reasons
            if not enabled:
                if locked_reasons == ("materials",):
                    tooltip += "\nLocked: gather the required materials first."
                else:
                    tooltip += "\nLocked due to: " + ", ".join(locked_reasons)

        rows.append(
            TargetRowMetadata(
                target_id=activity_key,
                label=label,
                tooltip=tooltip,
                enabled=enabled,
                current=activity_key == current_activity,
                icon_path=icon_path,
                locked_reasons=locked_reasons,
                sort_key=(label,),
            )
        )
    return tuple(rows)


def runecrafting_target_rows(
    player_data: Mapping[str, object],
    runecrafting_data: Mapping[str, Mapping[str, object]],
    runecrafting_item_images: Mapping[str, str],
    pouch_data: Mapping[str, Mapping[str, object]],
    default_target: str,
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    lvl_have = int(player_data.get("runecrafting_level", 1) or 1)
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    current_target = player_data.get("current_runecrafting", default_target)

    for target_id, spec in runecrafting_data.items():
        display_name = str(spec.get("display_name", target_id))
        lvl_req = int(spec.get("level", 1) or 1)
        kind = str(spec.get("kind", "standard"))
        output_item = str(spec.get("output_item", spec.get("input_item", display_name)))
        group = str(spec.get("group", "standard"))
        base_xp = float(spec.get("base_exp", 0.0) or 0.0)

        if kind == "standard":
            essence_items = tuple(spec.get("essence_items", ()))
            essence_text = ", ".join(f"{item} ({inventory.get(item, 0)})" for item in essence_items)
            tooltip = (
                f"Requires Runecrafting level {lvl_req}. You have {lvl_have}.\n"
                f"Output: {output_item}\n"
                f"Base XP: {base_xp:g} per essence\n"
                f"Essence: {essence_text}"
            )
        elif kind == "combination":
            component = str(spec.get("component_rune"))
            talisman = str(spec.get("consumed_talisman"))
            tooltip = (
                f"Requires Runecrafting level {lvl_req}. You have {lvl_have}.\n"
                f"Output: {output_item}\n"
                f"Base XP: {base_xp:g} per pure essence\n"
                f"Materials: Pure essence ({inventory.get('Pure essence', 0)}), "
                f"{component} ({inventory.get(component, 0)}), {talisman} ({inventory.get(talisman, 0)})"
            )
        elif kind == "tiara":
            talisman = str(spec.get("talisman_item"))
            tooltip = (
                f"Output: {output_item}\n"
                f"Base XP: {base_xp:g}\n"
                f"Materials: Tiara ({inventory.get('Tiara', 0)}), {talisman} ({inventory.get(talisman, 0)})"
            )
        else:
            input_item = str(spec.get("input_item", ""))
            tooltip = (
                f"Consumes {input_item} and stores its altar access in the Wicked hood.\n"
                f"Materials: {input_item} ({inventory.get(input_item, 0)})"
            )

        reasons = runecrafting_locked_reasons_pure(
            player_data,
            target_id,
            runecrafting_data,
            pouch_data,
            quest_unlock_rules,
        )
        if reasons:
            tooltip += "\nLocked due to: " + ", ".join(reasons)

        rows.append(
            TargetRowMetadata(
                target_id=target_id,
                label=f"{display_name} (Lvl {lvl_req})" if lvl_req > 1 else display_name,
                tooltip=tooltip,
                enabled=not reasons,
                current=target_id == current_target,
                icon_path=runecrafting_item_images.get(output_item) or runecrafting_item_images.get(str(spec.get("input_item", ""))),
                group=group,
                locked_reasons=reasons,
                sort_key=(lvl_req, display_name),
            )
        )
    return tuple(rows)
