"""Pure target-list row metadata for Skills-hub flat target lists."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Optional

try:
    from .logic_pure import (
        best_mining_pickaxe_pure,
        best_woodcutting_axe_pure,
        calculate_firemaking_success_probability_pure,
        calculate_fishing_success_probability_pure,
        can_burn_firemaking_target_pure,
        can_chop_woodcutting_target_pure,
        can_fish_method_pure,
        can_fletch_item_pure,
        can_mine_target_pure,
        can_open_bird_nests_pure,
        can_perform_utility_activity_pure,
        eligible_fishing_fish_pure,
        has_fishing_bait_pure,
    )
except Exception:
    from logic_pure import (  # type: ignore
        best_mining_pickaxe_pure,
        best_woodcutting_axe_pure,
        calculate_firemaking_success_probability_pure,
        calculate_fishing_success_probability_pure,
        can_burn_firemaking_target_pure,
        can_chop_woodcutting_target_pure,
        can_fish_method_pure,
        can_fletch_item_pure,
        can_mine_target_pure,
        can_open_bird_nests_pure,
        can_perform_utility_activity_pure,
        eligible_fishing_fish_pure,
        has_fishing_bait_pure,
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


def mining_target_rows(
    player_data: Mapping[str, object],
    ore_data: Mapping[str, Mapping[str, object]],
    ore_images: Mapping[str, str],
    gem_images: Mapping[str, str],
    pickaxe_data: Mapping[str, Mapping[str, object]],
    default_target: str,
    deferred_notes: Optional[Mapping[str, str]] = None,
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

        enabled = can_mine_target_pure(lvl_have, target_id, ore_data, inventory, tools, pickaxe_data)
        if not enabled:
            reason = []
            if lvl_have < lvl_req:
                reason.append(f"level {lvl_req}")
            if best_pick is None:
                reason.append("no usable pickaxe")
            if reason:
                tooltip += "\nLocked due to: " + ", ".join(reason)

        rows.append(
            TargetRowMetadata(
                target_id=target_id,
                label=label,
                tooltip=tooltip,
                enabled=enabled,
                current=target_id == current_target,
                icon_path=icon_path,
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
        materials_ok, mat_text = _material_lines(reqs, inventory)
        tooltip = (
            f"Requires Fletching level {lvl_req}. You have {lvl_have}.\n"
            f"Output: {output_item} x{output_qty}\nMaterials:\n{mat_text}"
        )
        enabled = can_fletch_item_pure(lvl_have, inventory, target_key, fletching_data)
        if not enabled:
            reason = []
            if lvl_have < lvl_req:
                reason.append(f"level {lvl_req}")
            if not materials_ok:
                reason.append("materials")
            if reason:
                tooltip += "\nLocked due to: " + ", ".join(reason)

        rows.append(
            TargetRowMetadata(
                target_id=target_key,
                label=f"{display_name} (Lvl {lvl_req})",
                tooltip=tooltip,
                enabled=enabled,
                current=target_key == current_target,
                icon_path=fletched_item_images.get(output_item),
            )
        )
    return tuple(rows)


def firemaking_target_rows(
    player_data: Mapping[str, object],
    firemaking_data: Mapping[str, Mapping[str, object]],
    firemaking_item_images: Mapping[str, str],
    default_target: str,
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
        enabled = can_burn_firemaking_target_pure(lvl_have, inventory, target_key, firemaking_data)
        if not enabled:
            reason = []
            if lvl_have < lvl_req:
                reason.append(f"level {lvl_req}")
            if owned < input_qty:
                reason.append("materials")
            if reason:
                tooltip += "\nLocked due to: " + ", ".join(reason)

        rows.append(
            TargetRowMetadata(
                target_id=target_key,
                label=f"{display_name} (Lvl {lvl_req})",
                tooltip=tooltip,
                enabled=enabled,
                current=target_key == current_target,
                icon_path=firemaking_item_images.get(str(input_item)) or firemaking_item_images.get(output_item),
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


def fishing_target_rows(
    player_data: Mapping[str, object],
    fishing_data: Mapping[str, Mapping[str, object]],
    fishing_item_images: Mapping[str, str],
    default_target: str,
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

        enabled = can_fish_method_pure(lvl_have, inventory, target_key, fishing_data, strength_have, agility_have)
        if not enabled:
            reason = []
            if lvl_have < lvl_req:
                reason.append(f"level {lvl_req}")
            if not has_fishing_bait_pure(inventory, spec):
                reason.append("materials")
            if lvl_have >= lvl_req and not eligible:
                reason.append("side levels")
            if reason:
                tooltip += "\nLocked due to: " + ", ".join(reason)

        rows.append(
            TargetRowMetadata(
                target_id=target_key,
                label=f"{display_name} (Lvl {lvl_req})",
                tooltip=tooltip,
                enabled=enabled,
                current=target_key == current_target,
                icon_path=fishing_item_images.get(icon_fish.get("output_item")) if isinstance(icon_fish, Mapping) else None,
            )
        )
    return tuple(rows)


def utility_activity_rows(
    player_data: Mapping[str, object],
    utility_activity_data: Mapping[str, Mapping[str, object]],
    utility_item_images: Mapping[str, str],
    nest_open_tables: Mapping[str, Mapping[str, object]],
    default_activity: str,
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
            enabled = can_open_bird_nests_pure(inventory, nest_open_tables)
            if not enabled:
                tooltip += "\nLocked: cut trees until a bird nest drops."
        else:
            output_item = str(spec.get("output_item", label))
            if icon_path is None:
                icon_path = utility_item_images.get(output_item)
            output_qty = spec.get("output_qty", 1)
            requirements = spec.get("requirements", {})
            reqs = requirements if isinstance(requirements, Mapping) else {}
            _, mat_text = _material_lines(reqs, inventory)
            tooltip = (
                f"Processes up to {batch_size} per successful card. No Crafting XP.\n"
                f"Output: {output_item} x{output_qty} per item\nMaterials:\n{mat_text}"
            )
            enabled = can_perform_utility_activity_pure(inventory, activity_key, utility_activity_data)
            if not enabled:
                tooltip += "\nLocked: gather the required materials first."

        rows.append(
            TargetRowMetadata(
                target_id=activity_key,
                label=label,
                tooltip=tooltip,
                enabled=enabled,
                current=activity_key == current_activity,
                icon_path=icon_path,
            )
        )
    return tuple(rows)
