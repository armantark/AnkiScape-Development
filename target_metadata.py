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
        calculate_hunter_success_probability_pure,
        can_chop_woodcutting_target_pure,
        combat_staff_covered_runes_pure,
        combat_target_locked_reasons_pure,
        combat_target_preview_pure,
        firemaking_target_locked_reasons_pure,
        can_open_bird_nests_pure,
        cooking_target_locked_reasons_pure,
        crafting_target_locked_reasons_pure,
        eligible_fishing_fish_pure,
        fishing_method_locked_reasons_pure,
        fletching_material_requirements_pure,
        fletching_target_locked_reasons_pure,
        herblore_target_locked_reasons_pure,
        hunter_target_locked_reasons_pure,
        mining_target_locked_reasons_pure,
        red_sandstone_daily_remaining_pure,
        magic_target_locked_reasons_pure,
        prayer_target_locked_reasons_pure,
        owned_gilded_altar_access_reasons_pure,
        owned_gilded_altar_effective_burners_pure,
        owned_gilded_altar_marrentill_required_pure,
        effective_gilded_altar_multiplier_pure,
        construction_target_locked_reasons_pure,
        runecrafting_locked_reasons_pure,
        smithing_target_locked_reasons_pure,
        utility_activity_locked_reasons_pure,
        woodcutting_target_locked_reasons_pure,
    )
except Exception:
    from logic_pure import (  # type: ignore
        best_mining_pickaxe_pure,
        best_woodcutting_axe_pure,
        calculate_cooking_success_probability_pure,
        calculate_firemaking_success_probability_pure,
        calculate_fishing_success_probability_pure,
        calculate_hunter_success_probability_pure,
        can_chop_woodcutting_target_pure,
        combat_staff_covered_runes_pure,
        combat_target_locked_reasons_pure,
        combat_target_preview_pure,
        firemaking_target_locked_reasons_pure,
        can_open_bird_nests_pure,
        cooking_target_locked_reasons_pure,
        crafting_target_locked_reasons_pure,
        eligible_fishing_fish_pure,
        fishing_method_locked_reasons_pure,
        fletching_material_requirements_pure,
        fletching_target_locked_reasons_pure,
        herblore_target_locked_reasons_pure,
        hunter_target_locked_reasons_pure,
        mining_target_locked_reasons_pure,
        red_sandstone_daily_remaining_pure,
        magic_target_locked_reasons_pure,
        prayer_target_locked_reasons_pure,
        owned_gilded_altar_access_reasons_pure,
        owned_gilded_altar_effective_burners_pure,
        owned_gilded_altar_marrentill_required_pure,
        effective_gilded_altar_multiplier_pure,
        construction_target_locked_reasons_pure,
        runecrafting_locked_reasons_pure,
        smithing_target_locked_reasons_pure,
        utility_activity_locked_reasons_pure,
        woodcutting_target_locked_reasons_pure,
    )

try:
    from .logic_pure import thieving_target_locked_reasons_pure as _thieving_target_locked_reasons_pure
except ImportError:
    try:
        from logic_pure import thieving_target_locked_reasons_pure as _thieving_target_locked_reasons_pure  # type: ignore
    except ImportError:  # The Thieving logic module may land after this UI slice.
        _thieving_target_locked_reasons_pure = None

try:
    from .agility_logic import agility_target_locked_reasons_pure
except ImportError:
    from agility_logic import agility_target_locked_reasons_pure  # type: ignore

try:
    from .warriors_guild_logic import (
        sanitize_warriors_guild_state_pure,
        warriors_guild_activity_locked_reasons_pure,
    )
except ImportError:
    from warriors_guild_logic import (  # type: ignore
        sanitize_warriors_guild_state_pure,
        warriors_guild_activity_locked_reasons_pure,
    )

try:
    from .summoning_logic import (
        summoning_action_locked_reasons_pure,
        summoning_action_requirements_pure,
    )
except ImportError:
    from summoning_logic import (  # type: ignore
        summoning_action_locked_reasons_pure,
        summoning_action_requirements_pure,
    )

try:
    from .livid_farm_data import LIVID_FARM_UNLOCKS
    from .livid_farm_logic import (
        livid_farm_cycle_projection_pure,
        livid_farm_locked_reasons_pure,
        sanitize_livid_farm_state_pure,
    )
except ImportError:
    from livid_farm_data import LIVID_FARM_UNLOCKS  # type: ignore
    from livid_farm_logic import (  # type: ignore
        livid_farm_cycle_projection_pure,
        livid_farm_locked_reasons_pure,
        sanitize_livid_farm_state_pure,
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
    requires_confirmation: bool = False
    confirmation_title: str = ""
    confirmation_message: str = ""


@dataclass(frozen=True)
class TargetDetails:
    """Player-facing mechanics copied from one live target row."""

    target_id: str
    title: str
    lines: tuple[str, ...]
    enabled: bool


def target_details_from_row_pure(row: TargetRowMetadata) -> TargetDetails:
    """Build optional details without exposing provenance or inventing values."""

    lines = tuple(
        line.rstrip()
        for line in row.tooltip.splitlines()
        if line.strip() and not line.strip().startswith("Source:")
    )
    if not lines:
        lines = ("No extra mechanics to show for this target.",)
    return TargetDetails(
        target_id=row.target_id,
        title=row.label,
        lines=lines,
        enabled=row.enabled,
    )


def summoning_target_rows(
    player_data: Mapping[str, object],
    actions: Sequence[object],
    pouches_by_id: Mapping[str, object],
    item_images: Mapping[str, str],
    default_target: str,
) -> tuple[TargetRowMetadata, ...]:
    """Build the complete surface infusion and scroll-conversion selector."""

    current = str(
        player_data.get("current_summoning", default_target) or default_target
    )
    inventory = player_data.get("inventory", {})
    owned = inventory if isinstance(inventory, Mapping) else {}
    rows = []
    group_order = {"Infuse pouches": 0, "Create scrolls": 1}
    for action in actions:
        target_id = str(getattr(action, "id"))
        familiar_id = str(getattr(action, "familiar_id"))
        family = str(getattr(action, "family"))
        group = str(getattr(action, "subgroup"))
        level = int(getattr(action, "level"))
        xp = float(getattr(action, "xp"))
        output_item = str(getattr(action, "output_item"))
        output_quantity = int(getattr(action, "output_quantity"))
        reasons = tuple(
            summoning_action_locked_reasons_pure(player_data, target_id)
        )
        requirements = summoning_action_requirements_pure(
            player_data, target_id
        )
        material_lines = list(
            _indented_material_lines(requirements, owned).splitlines()
        )
        pouch = pouches_by_id.get(familiar_id)
        if (
            family == "infuse"
            and pouch is not None
            and str(getattr(pouch, "tertiary_mode", "")) == "any"
        ):
            alternatives = tuple(getattr(pouch, "tertiaries", ()))
            if len(alternatives) > 1:
                material_lines.append(
                    "  Alternative tertiary: one of " + ", ".join(alternatives)
                )
        tooltip_lines = [
            f"{group} · Summoning level {level}",
            f"Summoning XP: {xp:g} per review",
            f"Output: {output_item} x{output_quantity}",
            "Materials:",
            *material_lines,
        ]
        if reasons:
            tooltip_lines.append("Locked due to: " + ", ".join(reasons))
        label = f"{getattr(action, 'display_name')} (Lvl {level}) — {xp:g} XP"
        if reasons:
            label += f" — Locked: {reasons[0]}"
        rows.append(
            TargetRowMetadata(
                target_id=target_id,
                label=label,
                tooltip="\n".join(tooltip_lines),
                enabled=not reasons,
                current=target_id == current,
                icon_path=item_images.get(output_item),
                group=group,
                locked_reasons=reasons,
                sort_key=(
                    group_order.get(group, 99),
                    level,
                    str(getattr(action, "display_name")),
                ),
            )
        )
    return tuple(rows)


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


def _indented_material_lines(
    requirements: Mapping[str, int],
    inventory: Mapping[str, int],
    empty_text: str = "No materials required",
) -> str:
    if not requirements:
        return f"  {empty_text}"
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


def _fallback_thieving_locked_reasons(
    player_data: Mapping[str, object],
    spec: Mapping[str, object],
) -> tuple[str, ...]:
    """Keep the target surface safe while the shared runtime gate is unavailable."""

    reasons = []
    level = int(spec.get("level", spec.get("required_level", 1)) or 1)
    if int(player_data.get("thieving_level", 1) or 1) < level:
        reasons.append(f"Thieving level {level}")

    quest_id = str(spec.get("quest_gate", spec.get("required_quest", "")) or "")
    if quest_id:
        quests = player_data.get("quests", {}) or {}
        quest_state = quests.get(quest_id, {}) if isinstance(quests, Mapping) else {}
        completed = bool(quest_state.get("completed")) if isinstance(quest_state, Mapping) else bool(quest_state)
        if not completed:
            reasons.append(str(spec.get("quest_gate_label", quest_id.replace("_", " ").title())))

    if spec.get("source_blocked"):
        reasons.append(str(spec.get("source_blocked_reason", "source values are not closed")))
    return tuple(dict.fromkeys(reasons))


def thieving_target_rows(
    player_data: Mapping[str, object],
    thieving_data: Mapping[str, Mapping[str, object]],
    thieving_item_images: Mapping[str, str],
    default_target: str,
) -> tuple[TargetRowMetadata, ...]:
    """Build the grouped Thieving selector without importing Qt."""

    rows = []
    current_target = str(player_data.get("current_thieving", default_target) or default_target)
    level_have = int(player_data.get("thieving_level", 1) or 1)
    group_order = {
        group: index
        for index, group in enumerate(("pickpocketing", "stalls", "safes", "blackjacking"))
    }

    for target_id, spec in thieving_data.items():
        display_name = str(spec.get("display_name", spec.get("name", target_id)))
        level = int(spec.get("level", spec.get("required_level", 1)) or 1)
        xp = float(spec.get("xp", spec.get("exp", 0)) or 0)
        group = str(spec.get("group", spec.get("family", "pickpocketing")) or "pickpocketing")
        if _thieving_target_locked_reasons_pure is not None:
            locked_reasons = tuple(
                _thieving_target_locked_reasons_pure(player_data, target_id, thieving_data)
            )
        else:
            locked_reasons = _fallback_thieving_locked_reasons(player_data, spec)

        tooltip_lines = [
            f"{group.replace('_', ' ').title()} · Thieving level {level}. You have {level_have}.",
            f"Thieving XP: {xp:g} per successful action",
        ]
        coins = spec.get("coins")
        if coins is not None:
            tooltip_lines.append(f"Coins: {coins} per successful action")
        default_low = 20 if spec.get("kind") == "wall_safe" else 0
        default_high = 60 if spec.get("kind") == "wall_safe" else default_low
        damage_low = int(
            spec.get("damage_min", spec.get("damage", spec.get("failure_damage", default_low))) or 0
        )
        damage_high = max(
            damage_low,
            int(spec.get("damage_max", spec.get("damage", spec.get("failure_damage", default_high))) or 0),
        )
        stun = int(spec.get("stun", spec.get("stun_ticks", 0)) or 0)
        if damage_high or stun:
            failure_parts = []
            if damage_high:
                damage_text = str(damage_low) if damage_low == damage_high else f"{damage_low}–{damage_high}"
                failure_parts.append(f"{damage_text} LP damage")
            if stun:
                failure_parts.append("next review clears the stun")
            tooltip_lines.append("On failure: " + ", ".join(failure_parts))
        if locked_reasons:
            tooltip_lines.append("Locked due to: " + ", ".join(locked_reasons))

        icon_name = str(spec.get("icon_name", spec.get("output_item", display_name)))
        label = f"{display_name} (Lvl {level}) — {xp:g} XP"
        if locked_reasons:
            label += f" — Locked: {locked_reasons[0]}"
        rows.append(TargetRowMetadata(
            target_id=target_id,
            label=label,
            tooltip="\n".join(tooltip_lines),
            enabled=not locked_reasons,
            current=target_id == current_target,
            icon_path=(
                str(spec.get("asset_path"))
                if spec.get("asset_path")
                else thieving_item_images.get(target_id)
                or thieving_item_images.get(icon_name)
                or thieving_item_images.get(display_name)
            ),
            group=group,
            locked_reasons=locked_reasons,
            sort_key=(group_order.get(group, 99), level, display_name),
        ))
    return tuple(rows)


def agility_target_rows(
    player_data: Mapping[str, object],
    agility_targets: Sequence[object],
    agility_target_images: Mapping[str, str],
    default_target: str,
) -> tuple[TargetRowMetadata, ...]:
    """Build the grouped Agility selector without importing Qt."""

    rows = []
    current_target = str(player_data.get("current_agility", default_target) or default_target)
    level_have = int(player_data.get("agility_level", 1) or 1)
    group_order = {"courses": 0, "activities": 1}
    for target in agility_targets:
        target_id = str(getattr(target, "id"))
        display_name = str(getattr(target, "display_name"))
        level = int(getattr(target, "level"))
        group = str(getattr(target, "group"))
        stages = tuple(getattr(target, "stages"))
        completion_bonus = float(getattr(target, "completion_bonus"))
        lap_xp = sum(float(getattr(stage, "xp")) for stage in stages) + completion_bonus
        locked_reasons = tuple(agility_target_locked_reasons_pure(player_data, target_id))
        kind_label = "Course" if group == "courses" else "Activity"
        tooltip_lines = [
            f"{kind_label} · Agility level {level}. You have {level_have}.",
        ]
        if stages:
            tooltip_lines.append(
                f"{len(stages)} review-driven actions · {lap_xp:g} XP for a perfect ordered completion"
            )
            if any(bool(getattr(stage, "can_fail")) for stage in stages):
                tooltip_lines.append("Failures can deal LP damage or change course position; undo restores the full action.")
        else:
            tooltip_lines.append("Review-driven activity with its own persisted progress and rewards.")
        if target_id == "brimhaven_arena":
            tooltip_lines.append("Hidden-pillar chase · eight attempts · activation streak · bankable tickets")
        if target_id == "wilderness_course":
            tooltip_lines.append(
                "Wilderness risk · 1% PKer ambush after each completed lap · "
                "maximum hit 250 LP · carried food and grave rules apply"
            )
        if locked_reasons:
            tooltip_lines.append("Locked due to: " + ", ".join(locked_reasons))
        label = f"{display_name} (Lvl {level})" if level > 1 else display_name
        if locked_reasons:
            label += f" — Locked: {locked_reasons[0]}"
        rows.append(TargetRowMetadata(
            target_id=target_id,
            label=label,
            tooltip="\n".join(tooltip_lines),
            enabled=not locked_reasons,
            current=target_id == current_target,
            icon_path=agility_target_images.get(target_id),
            group=group,
            locked_reasons=locked_reasons,
            sort_key=(group_order.get(group, 99), level, display_name),
        ))
    return tuple(rows)


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
        station_word = "Smelt" if spec.get("station") == "furnace" else "Cast" if spec.get("station") == "furnace_process" else "Forge"
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
            f"Base XP: {spec.get('exp', 0):g} per action\n"
            f"Materials:\n{_indented_material_lines(requirements, inventory)}"
        )
        required_items = spec.get("required_items", {}) or {}
        if isinstance(required_items, Mapping) and required_items:
            tooltip += f"\nRequired tools:\n{_indented_material_lines(required_items, inventory)}"
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


def prayer_target_rows(
    player_data: Mapping[str, object],
    prayer_data: Mapping[str, Mapping[str, object]],
    prayer_item_images: Mapping[str, str],
    default_target: str,
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    inventory = player_data.get("inventory", {}) or {}
    current = player_data.get("current_prayer", default_target)
    group_order = {name: index for index, name in enumerate(("Bury", "Scatter", "Ectofuntus", "Gilded altar"))}
    for target_id, spec in prayer_data.items():
        material = str(spec.get("display_name", target_id))
        group = str(spec.get("group", "Prayer"))
        requirements = dict(spec.get("requirements", {}) or {})
        reasons = list(prayer_target_locked_reasons_pure(player_data, target_id, prayer_data))
        xp = float(spec.get("exp", 0) or 0)
        method_copy = group
        herb_copy = ""
        if spec.get("method") == "gilded_altar":
            mode = str(player_data.get("prayer_gilded_mode", "hosted"))
            multiplier = effective_gilded_altar_multiplier_pure(player_data, mode, target_id)
            xp = float(spec.get("base_exp", 0) or 0) * multiplier
            if mode == "owned":
                reasons.extend(owned_gilded_altar_access_reasons_pure(player_data, target_id))
                burners = owned_gilded_altar_effective_burners_pure(player_data, target_id)
                marrentill = owned_gilded_altar_marrentill_required_pure(player_data, target_id)
                method_copy = f"Gilded altar · Owned · {multiplier * 100:g}% XP · {burners}/2 burners"
                if marrentill > 0:
                    requirements["Clean marrentill"] = marrentill
                elif (player_data.get("prayer_owned_altar_stint", {}) or {}).get("target_id") == target_id:
                    herb_copy = "\nClean marrentill: burners already lit for this stint"
                else:
                    herb_copy = "\nClean marrentill: none required (0 burners)"
            else:
                method_copy = "Gilded altar · Hosted · 350% XP"
        locked_reasons = tuple(dict.fromkeys(reasons))
        tooltip = (
            f"{method_copy} · Prayer level {spec.get('level', 1)}\n"
            f"Prayer XP: {xp:g} per review\n"
            f"Materials:\n{_indented_material_lines(requirements, inventory if isinstance(inventory, Mapping) else {})}{herb_copy}"
        )
        if locked_reasons:
            tooltip += "\nLocked due to: " + ", ".join(locked_reasons)
        rows.append(TargetRowMetadata(
            target_id=target_id,
            label=f"{material} — {xp:g} XP",
            tooltip=tooltip,
            enabled=not locked_reasons,
            current=target_id == current,
            icon_path=prayer_item_images.get(material),
            group=group,
            locked_reasons=locked_reasons,
            sort_key=(group_order.get(group, 99), xp, material),
        ))
    return tuple(rows)


def construction_target_rows(
    player_data, construction_data, room_data, servant_data, nail_data,
    workbench_tiers, construction_item_images, default_target,
):
    rows = []
    inventory = player_data.get("inventory", {}) or {}
    current = player_data.get("current_construction", default_target)
    group_order = {"Build": 0, "Flatpacks": 1, "Lectern tablets": 2}
    for target_id, spec in construction_data.items():
        group = "Lectern tablets" if target_id.startswith("tablet_") else "Flatpacks" if target_id.startswith("flatpack_") else str(spec.get("room", "Build")).replace("_", " ").title()
        order_group = "Build" if not target_id.startswith(("flatpack_", "tablet_")) else group
        reasons = construction_target_locked_reasons_pure(
            player_data, target_id, construction_data, room_data, servant_data,
            nail_data, workbench_tiers,
        )
        requirements = spec.get("requirements", {}) or {}
        skill = "Magic" if target_id.startswith("tablet_") else "Construction"
        level = spec.get("magic_level", spec.get("level", 1))
        tooltip = (
            f"{group} · {skill} level {level}\n"
            f"{skill} XP: {spec.get('xp', 0):g} per build\n"
            f"Materials:\n{_indented_material_lines(requirements, inventory)}"
        )
        if reasons:
            tooltip += "\nLocked due to: " + ", ".join(reasons)
        icon_name = str(spec.get("asset_name", spec.get("output_item", spec.get("display_name", ""))))
        rows.append(TargetRowMetadata(
            target_id=target_id,
            label=f"{spec.get('display_name', target_id)} — {spec.get('xp', 0):g} XP",
            tooltip=tooltip, enabled=not reasons, current=target_id == current,
            icon_path=construction_item_images.get(icon_name), group=group,
            locked_reasons=reasons,
            sort_key=(group_order.get(order_group, 0), group, int(level or 1), str(spec.get("display_name", target_id))),
        ))
    return tuple(rows)


def magic_target_rows(
    player_data: Mapping[str, object],
    magic_data: Mapping[str, Mapping[str, object]],
    magic_item_images: Mapping[str, str],
    default_target: str,
    alch_values: Mapping[str, int],
    magic_spell_images: Mapping[str, str] | None = None,
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    current = player_data.get("current_magic", default_target)
    group_order = {name: index for index, name in enumerate((
        "Alchemy", "Teleports — Standard", "Teleports — Ancient", "Teleports — Lunar",
        "Enchant jewellery", "Enchant bolts", "Charge orbs", "Conversions",
        "Lunar skilling", "Pure casts",
    ))}
    for target_id, spec in magic_data.items():
        name = str(spec.get("display_name", target_id))
        group = str(spec.get("group", "Magic"))
        reasons = magic_target_locked_reasons_pure(player_data, target_id, magic_data, alch_values)
        runes = spec.get("rune_cost", {}) or {}
        rune_text = ", ".join(f"{rune} x{amount}" for rune, amount in runes.items()) or "None"
        tooltip = (
            f"{spec.get('spellbook', 'standard').title()} · Magic level {spec.get('level', 1)}\n"
            f"Magic XP: {spec.get('exp', 0):g} per cast\nRunes: {rune_text}"
        )
        if spec.get("destination"):
            tooltip += f"\nDestination: {spec['destination']}"
        if spec.get("leather_input"):
            tooltip += f"\nInput: {spec['leather_input']} x1–5"
        if reasons:
            tooltip += "\nLocked due to: " + ", ".join(reasons)
        icon_name = next(iter((spec.get("outputs", {}) or {})), name)
        spell_icon_path = (magic_spell_images or {}).get(target_id)
        rows.append(TargetRowMetadata(
            target_id=target_id,
            label=f"{name} — {spec.get('exp', 0):g} XP",
            tooltip=tooltip,
            enabled=not reasons,
            current=target_id == current,
            icon_path=spell_icon_path or magic_item_images.get(str(icon_name)),
            group=group,
            locked_reasons=reasons,
            sort_key=(group_order.get(group, 99), int(spec.get("level", 1) or 1), name),
        ))
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
            f"Base XP: {spec.get('exp', 0):g} per action\n"
            f"Materials:\n{_indented_material_lines(requirements, inventory)}"
        )
        byproducts = spec.get("byproducts") or {}
        if isinstance(byproducts, Mapping) and byproducts:
            returned = ", ".join(f"{name} x{qty}" for name, qty in byproducts.items())
            tooltip += f"\nAlso returns: {returned}"
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
        has_level_requirement = not bool(spec.get("source_no_level_requirement"))
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
        level_line = f"Requires Cooking level {lvl_req}. You have {lvl_have}.\n" if has_level_requirement else "No Cooking level requirement.\n"
        if spec.get("source_always_succeeds"):
            failure_line = "Cannot burn or fail.\n"
        else:
            failure_line = f"Burn output: {burnt_item} x1, no XP\n" if burnt_item else "Failure consumes the input, no XP\n"
        if spec.get("output_quantity_model") == "cheese_wheel_slices":
            output_line = f"Success output: {output_item} x5-35 (one Slice-all action)\n"
            xp_line = f"Base XP: {spec.get('xp_per_output', 0):g} per slice\n"
        else:
            output_line = f"Success output: {output_item} x{int(spec.get('output_qty', 1) or 1)}\n"
            xp_line = f"Base XP: {spec.get('exp', 0):g} on success\n"
        tooltip = (
            level_line
            + output_line
            + failure_line
            + xp_line
            + f"Success chance: {chance:.0f}% per action\n"
            + f"Materials:\n{_indented_material_lines(requirements, inventory)}"
        )
        byproducts = spec.get("byproducts")
        if isinstance(byproducts, Mapping) and byproducts:
            returned = ", ".join(f"{name} x{qty}" for name, qty in byproducts.items())
            tooltip += f"\nAlso returns: {returned}"
        if locked_reasons:
            tooltip += "\nLocked due to: " + ", ".join(locked_reasons)

        rows.append(
            TargetRowMetadata(
                target_id=target_id,
                label=f"{display_name} (Lvl {lvl_req})" if has_level_requirement else display_name,
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
            f"Base XP: {data.get('exp', 0):g} per ore\n"
            f"Best usable pickaxe: {best_pick_name or 'none — get a pickaxe'}"
        )
        note = data.get("notes")
        if note:
            tooltip += f"\nNote: {note}"
        if target_id == "red_sandstone":
            tooltip += (
                "\nReview-day allowance: "
                f"{red_sandstone_daily_remaining_pure(player_data)} of 50 remaining"
            )
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
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
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
        processing = data.get("action_type") == "processing"
        xp_only = output_item is None
        label = f"{display} (Lvl {lvl_req})"
        if xp_only:
            label += " — XP only"

        output_qty = max(1, int(data.get("output_quantity", 1) or 1))
        output_line = (
            "XP only — produces no logs."
            if xp_only
            else f"Output: {output_item} x{output_qty}"
        )
        if processing:
            requirements = data.get("requirements", {})
            requirement_lines = (
                _indented_material_lines(requirements, inventory)
                if isinstance(requirements, Mapping)
                else "  None"
            )
            tooltip = (
                f"Requires Woodcutting level {lvl_req}. You have {lvl_have}.\n"
                f"Materials:\n{requirement_lines}\n"
                f"{output_line}\n"
                f"Base XP: {data.get('exp', 0):g} per split"
            )
        else:
            tooltip = (
                f"Requires Woodcutting level {lvl_req}. You have {lvl_have}.\n"
                f"{output_line}\n"
                f"Base XP: {data.get('exp', 0):g} per chop\n"
                f"Best usable hatchet: {best_axe_name or 'none — get a hatchet'}"
            )
        locked_reasons = woodcutting_target_locked_reasons_pure(
            player_data,
            target_id,
            tree_data,
            axe_data,
            quest_unlock_rules,
        )
        if locked_reasons:
            tooltip += "\nLocked due to: " + ", ".join(locked_reasons)

        rows.append(
            TargetRowMetadata(
                target_id=target_id,
                label=label,
                tooltip=tooltip,
                enabled=not locked_reasons,
                current=target_id == current_target,
                icon_path=tree_images.get(display),
                locked_reasons=locked_reasons,
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
        reqs = fletching_material_requirements_pure(target_key, inventory, fletching_data)
        if reqs is None:
            reqs = requirements if isinstance(requirements, Mapping) else {}
        _materials_ok, mat_text = _material_lines(reqs, inventory)
        tooltip = (
            f"Requires Fletching level {lvl_req}. You have {lvl_have}.\n"
            f"Output: {output_item} x{output_qty}\nMaterials:\n{mat_text}"
        )
        required_items = spec.get("required_items", {}) or {}
        if isinstance(required_items, Mapping) and required_items:
            tooltip += f"\nRequired tools:\n{_indented_material_lines(required_items, inventory)}"
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


def herblore_target_rows(
    player_data: Mapping[str, object],
    herblore_data: Mapping[str, Mapping[str, object]],
    herblore_item_images: Mapping[str, str],
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    lvl_have = int(player_data.get("herblore_level", 1) or 1)
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    current_target = player_data.get("current_herblore")

    for target_key, spec in herblore_data.items():
        display_name = str(spec.get("display_name", target_key))
        output_item = str(spec.get("output_item", display_name))
        output_qty = spec.get("output_qty", 1)
        lvl_req = int(spec.get("level", 1) or 1)
        base_xp = spec.get("exp", 0)
        requirements = spec.get("requirements", {})
        reqs = requirements if isinstance(requirements, Mapping) else {}
        byproducts = spec.get("byproducts", {})
        byproduct_map = byproducts if isinstance(byproducts, Mapping) else {}
        output_lines = [f"Output: {output_item} x{output_qty}"]
        output_lines.extend(f"Byproduct: {item} x{amount}" for item, amount in byproduct_map.items())
        output_text = "\n".join(output_lines)
        _materials_ok, mat_text = _material_lines(reqs, inventory)
        tooltip = (
            f"Requires Herblore level {lvl_req}. You have {lvl_have}.\n"
            f"Base XP: {base_xp:g} per action\n"
            f"{output_text}\nMaterials:\n{mat_text}"
        )
        locked_reasons = herblore_target_locked_reasons_pure(
            player_data,
            target_key,
            herblore_data,
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
                icon_path=herblore_item_images.get(output_item),
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
            f"Base XP: {base_xp:g} per successful burn\n"
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


def _hunter_output_text(outputs: Mapping[str, object]) -> str:
    if not outputs:
        return "none"
    return ", ".join(f"{item_name} x{amount}" for item_name, amount in outputs.items())


def hunter_target_rows(
    player_data: Mapping[str, object],
    hunter_data: Mapping[str, Mapping[str, object]],
    hunter_item_images: Mapping[str, str],
    default_target: str,
    quest_unlock_rules: Sequence[Mapping[str, object]] = (),
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    lvl_have = int(player_data.get("hunter_level", 1) or 1)
    inv = player_data.get("inventory", {})
    inventory = inv if isinstance(inv, Mapping) else {}
    current_target = player_data.get("current_hunter", default_target)

    for target_key, spec in hunter_data.items():
        display_name = str(spec.get("display_name", target_key))
        lvl_req = int(spec.get("level", 1) or 1)
        requirements = spec.get("requirements", {})
        reqs = requirements if isinstance(requirements, Mapping) else {}
        tools_raw = spec.get("tools", {})
        tools = tools_raw if isinstance(tools_raw, Mapping) else {}
        outputs_raw = spec.get("outputs", {})
        outputs = outputs_raw if isinstance(outputs_raw, Mapping) else {}
        primary_output = str(spec.get("primary_output", spec.get("output_item", display_name)))
        chance = calculate_hunter_success_probability_pure(lvl_have, spec)
        locked_reasons = hunter_target_locked_reasons_pure(
            player_data,
            target_key,
            hunter_data,
            quest_unlock_rules,
        )
        tooltip = (
            f"Requires Hunter level {lvl_req}. You have {lvl_have}.\n"
            f"Outputs: {_hunter_output_text(outputs)}\n"
            f"Base XP: {spec.get('exp', 0):g} per successful catch\n"
            f"Success chance: {chance:.0%} per attempt\n"
            f"Materials:\n{_indented_material_lines(reqs, inventory)}\n"
            f"Reusable tools:\n{_indented_material_lines(tools, inventory, 'No reusable tools required')}"
        )
        side_requirements = spec.get("skill_requirements", {})
        if isinstance(side_requirements, Mapping) and side_requirements:
            tooltip += "\nSide levels: " + ", ".join(
                f"{str(skill).replace('_', ' ').title()} {int(level)}"
                for skill, level in side_requirements.items()
            )
        xp_rewards = spec.get("xp_rewards", ())
        if isinstance(xp_rewards, (tuple, list)) and len(xp_rewards) > 1:
            tooltip += "\nXP rewards: " + ", ".join(
                f"{str(reward.get('skill_id', '')).title()} {float(reward.get('amount', 0)):g}"
                for reward in xp_rewards if isinstance(reward, Mapping)
            )
        notes = spec.get("notes")
        if notes:
            tooltip += f"\nNote: {notes}"
        if locked_reasons:
            tooltip += "\nLocked due to: " + ", ".join(locked_reasons)

        rows.append(
            TargetRowMetadata(
                target_id=target_key,
                label=f"{display_name} (Lvl {lvl_req})",
                tooltip=tooltip,
                enabled=not locked_reasons,
                current=target_key == current_target,
                icon_path=hunter_item_images.get(primary_output),
                group=str(spec.get("group", "")),
                locked_reasons=locked_reasons,
                sort_key=tuple(spec.get("sort_key", (lvl_req, display_name))),
            )
        )
    return tuple(rows)


def _combat_drop_summary(enemy: Mapping[str, object]) -> str:
    def _quantity_text(slot: Mapping[str, object]) -> str:
        quantity_range = slot.get("quantity_range")
        if isinstance(quantity_range, (tuple, list)) and len(quantity_range) >= 2:
            try:
                low = int(quantity_range[0] or 0)
                high = int(quantity_range[1] or 0)
            except (TypeError, ValueError):
                low = high = 0
            if low > 0 and high >= low:
                return f"{low}-{high}"
        return str(max(1, int(slot.get("quantity", 1) or 1)))

    drops_raw = enemy.get("drops", {})
    drops = drops_raw if isinstance(drops_raw, Mapping) else {}
    guaranteed = []
    for item_name, quantity in drops.get("guaranteed", ()) or ():
        if isinstance(item_name, str):
            guaranteed.append(f"{item_name} x{max(1, int(quantity or 1))}")
    table_lines = []
    for table in drops.get("tables", ()) or ():
        if not isinstance(table, Mapping):
            continue
        table_name = str(table.get("name", "Roll"))
        total = int(table.get("total", 0) or 0)
        slots = []
        for slot in table.get("slots", ()) or ():
            if not isinstance(slot, Mapping):
                continue
            item_name = slot.get("item")
            slot_count = int(slot.get("slots", 0) or 0)
            if isinstance(item_name, str) and total > 0 and slot_count > 0:
                slots.append(f"{item_name} x{_quantity_text(slot)} ({slot_count}/{total})")
                continue
            nested_table = slot.get("table")
            if isinstance(nested_table, Mapping) and total > 0 and slot_count > 0:
                nested_name = str(nested_table.get("name", "Nested"))
                slots.append(f"{nested_name} table ({slot_count}/{total})")
        if slots:
            table_lines.append(f"{table_name}: " + ", ".join(slots))
    parts = []
    if guaranteed:
        parts.append("Guaranteed: " + ", ".join(guaranteed))
    parts.extend(table_lines)
    return "\n".join(parts) if parts else "No item drops"


def _combat_food_summary(player_data: Mapping[str, object], target_id: str) -> str:
    def _count(value: object) -> int:
        if isinstance(value, bool):
            return 0
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0

    auto_food = player_data.get("combat_auto_eat_food", ()) or ()
    loadout_raw = player_data.get("combat_supply_loadout", {}) or {}
    loadout = loadout_raw if isinstance(loadout_raw, Mapping) else {}
    food_raw = loadout.get("food", {}) if isinstance(loadout, Mapping) else {}
    food_loadout = food_raw if isinstance(food_raw, Mapping) else {}
    inventory_raw = player_data.get("inventory", {}) or {}
    inventory = inventory_raw if isinstance(inventory_raw, Mapping) else {}
    encounter_raw = player_data.get("combat_encounter", {}) or {}
    active_encounter = isinstance(encounter_raw, Mapping) and encounter_raw.get("target_id") == target_id
    parts = []
    for item_name in auto_food:
        if not isinstance(item_name, str):
            continue
        loaded = _count(food_loadout.get(item_name, 0))
        banked = 0 if active_encounter else _count(inventory.get(item_name, 0))
        if loaded or banked:
            if active_encounter:
                parts.append(f"{item_name} x{loaded} loaded")
            else:
                parts.append(f"{item_name} x{loaded} loaded + {banked} bank")
    return ", ".join(parts) if parts else "No configured food loaded"


def _combat_ammo_summary(player_data: Mapping[str, object], target_id: str, ammo_name: object) -> str:
    if not isinstance(ammo_name, str) or not ammo_name:
        return ""

    def _count(value: object) -> int:
        if isinstance(value, bool):
            return 0
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0

    loadout_raw = player_data.get("combat_supply_loadout", {}) or {}
    loadout = loadout_raw if isinstance(loadout_raw, Mapping) else {}
    ammo_raw = loadout.get("ammo", {}) if isinstance(loadout, Mapping) else {}
    ammo_loadout = ammo_raw if isinstance(ammo_raw, Mapping) else {}
    inventory_raw = player_data.get("inventory", {}) or {}
    inventory = inventory_raw if isinstance(inventory_raw, Mapping) else {}
    encounter_raw = player_data.get("combat_encounter", {}) or {}
    active_encounter = isinstance(encounter_raw, Mapping) and encounter_raw.get("target_id") == target_id
    loaded = _count(ammo_loadout.get(ammo_name, 0))
    banked = 0 if active_encounter else _count(inventory.get(ammo_name, 0))
    if active_encounter:
        return f"Ammo: {ammo_name} x{loaded} loaded\n"
    return f"Ammo: {ammo_name} x{loaded} loaded + {banked} bank\n"


def _combat_rune_summary(
    player_data: Mapping[str, object],
    target_id: str,
    spell_name: object,
    rune_cost: object,
) -> str:
    if not isinstance(spell_name, str) or not spell_name:
        return ""
    costs = rune_cost if isinstance(rune_cost, Mapping) else {}
    if not costs:
        return f"Spell: {spell_name}\n"

    def _count(value: object) -> int:
        if isinstance(value, bool):
            return 0
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0

    loadout_raw = player_data.get("combat_supply_loadout", {}) or {}
    loadout = loadout_raw if isinstance(loadout_raw, Mapping) else {}
    runes_raw = loadout.get("runes", {}) if isinstance(loadout, Mapping) else {}
    rune_loadout = runes_raw if isinstance(runes_raw, Mapping) else {}
    inventory_raw = player_data.get("inventory", {}) or {}
    inventory = inventory_raw if isinstance(inventory_raw, Mapping) else {}
    encounter_raw = player_data.get("combat_encounter", {}) or {}
    active_encounter = isinstance(encounter_raw, Mapping) and encounter_raw.get("target_id") == target_id
    covered_runes = combat_staff_covered_runes_pure(player_data)
    lines = [f"Spell: {spell_name}"]
    for rune_name, amount in costs.items():
        if not isinstance(rune_name, str):
            continue
        loaded = _count(rune_loadout.get(rune_name, 0))
        banked = 0 if active_encounter else _count(inventory.get(rune_name, 0))
        required = _count(amount)
        staff_name = covered_runes.get(rune_name)
        if isinstance(staff_name, str):
            lines.append(f"Rune: {rune_name} x{required}; covered by {staff_name}")
            continue
        if active_encounter:
            lines.append(f"Rune: {rune_name} x{required}; {loaded} loaded")
        else:
            lines.append(f"Rune: {rune_name} x{required}; {loaded} loaded + {banked} bank")
    return "\n".join(lines) + "\n"


def combat_target_rows(
    player_data: Mapping[str, object],
    combat_enemy_data: Mapping[str, Mapping[str, object]],
    combat_item_images: Mapping[str, str],
    equipment_data: Mapping[str, object],
    default_target: str,
    combat_enemy_images: Mapping[str, str] | None = None,
) -> tuple[TargetRowMetadata, ...]:
    rows = []
    current_target = player_data.get("current_combat_target", default_target)
    enemy_images = combat_enemy_images or {}
    encounter_raw = player_data.get("combat_encounter", {}) or {}
    encounter_target = encounter_raw.get("target_id") if isinstance(encounter_raw, Mapping) else None

    for target_id, enemy in combat_enemy_data.items():
        if enemy.get("encounter_only") and encounter_target != target_id:
            continue
        if enemy.get("warriors_guild_spawn_only"):
            guild_state = sanitize_warriors_guild_state_pure(
                player_data.get("warriors_guild")
            )
            if (
                not guild_state["cyclossus_pending"]
                and current_target != target_id
            ):
                continue
        display_name = str(enemy.get("display_name", target_id))
        level = int(enemy.get("level", 1) or 1)
        attack_style = str(enemy.get("attack_style", "melee") or "melee")
        attack_style_label = {
            "melee": "Melee",
            "ranged": "Ranged",
            "magic": "Magic",
            "magic_melee": "Magic-based melee",
        }.get(attack_style, attack_style.replace("_", " ").title())
        stats_raw = enemy.get("stats", {})
        stats = stats_raw if isinstance(stats_raw, Mapping) else {}
        preview = combat_target_preview_pure(player_data, target_id, combat_enemy_data, equipment_data)
        locked_reasons = combat_target_locked_reasons_pure(
            player_data,
            target_id,
            combat_enemy_data,
            equipment_data=equipment_data,
        )
        if locked_reasons:
            requires_confirmation = False
            confirmation_title = ""
            confirmation_message = ""
            tooltip = (
                f"{display_name} · combat level {level}\n"
                f"Locked due to: {', '.join(locked_reasons)}\n"
                f"Source: {enemy.get('source', '')}"
            )
        else:
            risk_band = str(preview.get("risk_band", "Unknown"))
            wilderness = preview.get("wilderness_risk", {}) or {}
            wilderness = wilderness if isinstance(wilderness, Mapping) else {}
            requires_confirmation = bool(wilderness) or risk_band == "Death possible"
            confirmation_title = (
                "Confirm Wilderness combat"
                if wilderness
                else "Confirm dangerous combat"
                if requires_confirmation
                else ""
            )
            confirmation_message = ""
            confirmation_line = ""
            if wilderness:
                kept_items = tuple(wilderness.get("kept_items", ()) or ())
                lost_items = tuple(wilderness.get("lost_items", ()) or ())
                kept_text = ", ".join(kept_items) if kept_items else "nothing"
                lost_text = ", ".join(lost_items) if lost_items else "nothing"
                dragonfire = preview.get("dragonfire", {}) or {}
                dragonfire_warning = (
                    f" Current dragonfire protection: "
                    f"{dragonfire.get('state', 'None')} "
                    f"(maximum {int(dragonfire.get('max_hit', 0) or 0)} LP)."
                    if isinstance(dragonfire, Mapping) and dragonfire
                    else ""
                )
                confirmation_message = (
                    f"{display_name} is in the Wilderness. Each successful review "
                    f"has a {float(wilderness.get('ambush_chance', 0.0) or 0.0):.0%} "
                    f"PKer-ambush risk with a {int(wilderness.get('max_hit', 0) or 0)} "
                    f"LP maximum hit. A fatal ambush creates no grave.{dragonfire_warning} "
                    f"Kept: {kept_text}. Lost: {lost_text}. Select this target anyway?"
                )
                confirmation_line = "Wilderness risk confirmation required before selecting this target.\n"
            elif requires_confirmation:
                confirmation_message = (
                    f"{display_name} is marked Death possible at your current lifepoints "
                    f"without loaded or banked food. Select this target anyway?"
                )
                confirmation_line = "Confirmation required before selecting this target.\n"
            wilderness_line = ""
            if wilderness:
                kept_items = tuple(wilderness.get("kept_items", ()) or ())
                lost_items = tuple(wilderness.get("lost_items", ()) or ())
                wilderness_line = (
                    f"Wilderness: {float(wilderness.get('ambush_chance', 0.0) or 0.0):.0%} "
                    f"PKer ambush per successful review · maximum hit "
                    f"{int(wilderness.get('max_hit', 0) or 0)} LP · "
                    f"keep {len(kept_items)} equipped · lose {len(lost_items)} · no grave\n"
                )
            poison_line = ""
            poison_damage = int(preview.get("poison_damage", 0) or 0)
            poison_chance = float(preview.get("poison_chance", 0.0) or 0.0)
            if poison_damage > 0 and poison_chance > 0.0:
                poison_line = f"Poison: {poison_damage} LP initial · {poison_chance:.0%} attack chance\n"
            protection_warning = str(preview.get("protection_warning", "") or "")
            protection_line = f"Protection: {protection_warning}\n" if protection_warning else ""
            dragonfire = preview.get("dragonfire", {}) or {}
            dragonfire_line = ""
            if isinstance(dragonfire, Mapping) and dragonfire:
                dragonfire_line = (
                    f"Dragonfire: {dragonfire.get('state', 'None')} protection · "
                    f"maximum hit {int(dragonfire.get('max_hit', 0) or 0)} LP · "
                    f"{int(dragonfire.get('chance_numerator', 1) or 1)}/"
                    f"{int(dragonfire.get('chance_denominator', 1) or 1)} attacks\n"
                )
            weakening = preview.get("weakening_equipment", {}) or {}
            weakening_line = ""
            if isinstance(weakening, Mapping) and weakening:
                accuracy_reduction = max(
                    0,
                    round(
                        (
                            1.0
                            - float(
                                weakening.get(
                                    "enemy_accuracy_multiplier", 1.0
                                )
                            )
                        )
                        * 100
                    ),
                )
                damage_reduction = max(
                    0,
                    round(
                        (
                            1.0
                            - float(
                                weakening.get(
                                    "enemy_damage_multiplier", 1.0
                                )
                            )
                        )
                        * 100
                    ),
                )
                weakening_line = (
                    f"Weakness: {weakening.get('display_name', 'special equipment')} "
                    f"{'equipped' if weakening.get('active') else 'not equipped'} · "
                    f"enemy accuracy -{accuracy_reduction}% · "
                    f"max hit -{damage_reduction}%\n"
                )
            finisher = preview.get("finisher", {}) or {}
            finisher_line = ""
            if isinstance(finisher, Mapping) and finisher.get("required"):
                if finisher.get("charged"):
                    finisher_supply = (
                        f"{finisher.get('charges', 0)} spray charges + "
                        f"{finisher.get('reloads', 0)} canister reloads"
                    )
                else:
                    finisher_supply = f"{finisher.get('item_count', 0)} loaded"
                finisher_line = (
                    f"Finisher: {finisher.get('action_label')} at "
                    f"1–{finisher.get('threshold_lifepoints', 0)} LP · "
                    f"{finisher_supply}\n"
                )
            hazard = preview.get("environmental_hazard", {}) or {}
            hazard_line = ""
            if isinstance(hazard, Mapping) and hazard:
                hazard_line = (
                    f"{hazard.get('display_name', 'Environmental hazard')}: "
                    "1 Waterskin dose per Combat review · "
                    f"{hazard.get('loaded', 0)} loaded + "
                    f"{hazard.get('banked', 0)} bank\n"
                )
            interaction_note = str(enemy.get("interaction_note", "") or "")
            interaction_line = (
                f"Encounter: {interaction_note}\n" if interaction_note else ""
            )
            tooltip = (
                f"{display_name} · combat level {level}\n"
                f"State: {preview.get('state', 'Ready')} · risk: {risk_band}\n"
                f"{confirmation_line}"
                f"{interaction_line}"
                f"Enemy attack: {attack_style_label}\n"
                f"Accuracy: {float(preview.get('accuracy', 0.0) or 0.0):.0%}\n"
                f"Your max hit: {preview.get('player_max_hit', 0)} LP\n"
                f"Your LP: {preview.get('player_lifepoints', 0)}/{preview.get('player_max_lifepoints', 0)}\n"
                f"Enemy LP: {preview.get('enemy_lifepoints', 0)}/{preview.get('enemy_max_lifepoints', stats.get('hitpoints', 0))}\n"
                f"Enemy max hit: {preview.get('enemy_max_hit', 0)} LP\n"
                f"{wilderness_line}"
                f"{dragonfire_line}"
                f"{protection_line}"
                f"{weakening_line}"
                f"{finisher_line}"
                f"{hazard_line}"
                f"{poison_line}"
                f"Food: {_combat_food_summary(player_data, target_id)}\n"
                f"{_combat_ammo_summary(player_data, target_id, preview.get('ammo'))}"
                f"{_combat_rune_summary(player_data, target_id, preview.get('spell'), preview.get('runes'))}"
                f"Drops:\n  {_combat_drop_summary(enemy).replace(chr(10), chr(10) + '  ')}\n"
                f"Source: {enemy.get('source', '')}"
            )

        rows.append(
            TargetRowMetadata(
                target_id=target_id,
                label=f"{display_name} (Lvl {level})",
                tooltip=tooltip,
                enabled=not locked_reasons,
                current=target_id == current_target,
                icon_path=enemy_images.get(target_id) or enemy_images.get(display_name),
                group=str(enemy.get("group", "Combat")),
                locked_reasons=locked_reasons,
                sort_key=(level, display_name),
                requires_confirmation=requires_confirmation,
                confirmation_title=confirmation_title,
                confirmation_message=confirmation_message,
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

        if spec.get("livid_farm_activity"):
            state = sanitize_livid_farm_state_pure(
                player_data.get("livid_farm")
            )
            projection = livid_farm_cycle_projection_pure(
                player_data,
                state["farm_routine"],
            )
            locked_reasons = livid_farm_locked_reasons_pure(player_data)
            enabled = not locked_reasons
            next_unlock = next(
                (
                    (name, threshold)
                    for unlock_id, name, threshold in LIVID_FARM_UNLOCKS
                    if unlock_id not in set(state["unlocked_spells"])
                ),
                None,
            )
            next_text = (
                f"{next_unlock[0]} at {next_unlock[1]:,} lifetime Produce"
                if next_unlock
                else "All Livid Farm spells unlocked"
            )
            rune_text = ", ".join(
                f"{name} x{amount}"
                for name, amount in projection["rune_cost"].items()
            )
            tooltip = (
                "One complete five-round source cycle per cadence emission; "
                "exactly six cycles per five successful reviews.\n"
                f"Routine: {state['farm_routine'].title()} · "
                f"{int(projection['points']):,} Produce per cycle\n"
                f"Wallet: {int(state['produce_points']):,} · "
                f"Lifetime: {int(state['lifetime_produce_points']):,} · "
                f"Cycles: {int(state['cycles_completed']):,}\n"
                f"Next: {next_text}\n"
                f"Runes per cycle after staff substitutions: {rune_text or 'None'}"
            )
            if locked_reasons:
                tooltip += "\nLocked due to: " + ", ".join(locked_reasons)
            tooltip += f"\nSource: {spec.get('source', '')}"
        elif spec.get("warriors_guild_activity"):
            state = sanitize_warriors_guild_state_pure(
                player_data.get("warriors_guild")
            )
            token_key = str(spec.get("token_key", ""))
            token_count = int(state["tokens"].get(token_key, 0) or 0)
            locked_reasons = warriors_guild_activity_locked_reasons_pure(
                player_data,
                activity_key,
            )
            enabled = not locked_reasons or state["automation_mode"] == "casual"
            tooltip = (
                f"{spec.get('summary', label)}\n"
                f"{token_key.title()} tokens: {token_count}\n"
                "Casual rotates automatically; Advanced runs this exact activity.\n"
                f"Source: {spec.get('source', '')}"
            )
            if locked_reasons:
                tooltip += "\nLocked due to: " + ", ".join(locked_reasons)
        elif openable_items:
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
        elif spec.get("no_op"):
            tooltip = (
                "Stand at the Bank. Nothing is produced or consumed; no skill XP.\n"
                "Grand Exchange offers advance once per answered card, just as "
                "with every activity."
            )
            locked_reasons = utility_activity_locked_reasons_pure(
                player_data,
                activity_key,
                utility_activity_data,
                quest_unlock_rules,
            )
            enabled = not locked_reasons
            if not enabled:
                tooltip += "\nLocked due to: " + ", ".join(locked_reasons)
        else:
            outputs_raw = spec.get("outputs", {})
            outputs = outputs_raw if isinstance(outputs_raw, Mapping) else {}
            if outputs:
                icon_item = str(spec.get("icon_item", next(iter(outputs))))
                if icon_path is None:
                    icon_path = utility_item_images.get(icon_item)
                output_text = "Outputs: " + ", ".join(f"{item} x{amount}" for item, amount in outputs.items())
            else:
                output_item = str(spec.get("output_item", label))
                if icon_path is None:
                    icon_path = utility_item_images.get(output_item)
                output_qty = spec.get("output_qty", 1)
                output_text = f"Output: {output_item} x{output_qty} per item"
            requirements = spec.get("requirements", {})
            reqs = requirements if isinstance(requirements, Mapping) else {}
            _, mat_text = _material_lines(reqs, inventory)
            any_requirements = spec.get("any_requirements")
            if isinstance(any_requirements, (list, tuple, set)) and any_requirements:
                names = [str(item_name) for item_name in any_requirements]
                mat_text += "\nOne of: " + ", ".join(
                    f"{name} ({int(inventory.get(name, 0) or 0)})"
                    for name in names
                )
            run_text = (
                "Runs once, then switches off. No skill XP."
                if spec.get("deactivate_after_run")
                else f"Processes up to {batch_size} per successful card. No skill XP."
            )
            tooltip = (
                f"{run_text}\n"
                f"{output_text}\nMaterials:\n{mat_text}"
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
