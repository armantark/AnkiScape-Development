"""Pure Family Crest gauntlet lifecycle and Cooking equipment policy."""

from __future__ import annotations

from collections.abc import Mapping

from ..core.constants import COOKING_DATA
from ..data.cooking_gauntlets_data import (
    FAMILY_GAUNTLET_ENCHANTMENTS,
    FAMILY_GAUNTLET_ITEMS,
)
from ..logic_pure.logic_pure_production import (
    calculate_cooking_success_probability_pure,
    cooking_source_roll_chance_pure,
)
from .cadence_kernel import EMBEDDED_PROBABILITY
from .cadence_live import resolve_live_cadence_route_pure
from .cape_logic import effective_roll_level_pure


COOKING_GAUNTLETS = "Cooking gauntlets"
FAMILY_CREST_QUEST_ID = "family_crest"
GAUNTLET_REENCHANT_COST = 25_000
_VALID_COOKING_EQUIPMENT_CHOICES = frozenset({"auto", "cooking", "none"})


def default_cooking_gauntlets_state_pure() -> dict[str, object]:
    return {
        "family_gauntlet_enchantment": "",
        "cooking_equipment_choices": {},
        "cooking_equipment_swap": {},
    }


def _copy_state(player_data: Mapping[str, object]) -> dict[str, object]:
    data = dict(player_data)
    data["inventory"] = dict(player_data.get("inventory", {}) or {})
    data["equipment"] = dict(player_data.get("equipment", {}) or {})
    data["cooking_equipment_choices"] = dict(
        player_data.get("cooking_equipment_choices", {}) or {}
    )
    data["cooking_equipment_swap"] = dict(
        player_data.get("cooking_equipment_swap", {}) or {}
    )
    return data


def _quest_completed(player_data: Mapping[str, object]) -> bool:
    quests = player_data.get("quests", {}) or {}
    state = quests.get(FAMILY_CREST_QUEST_ID, {}) if isinstance(quests, Mapping) else {}
    return bool(state.get("completed", False)) if isinstance(state, Mapping) else False


def _owned_gauntlet(player_data: Mapping[str, object]) -> str:
    equipment = player_data.get("equipment", {}) or {}
    worn = equipment.get("hands") if isinstance(equipment, Mapping) else None
    if worn in FAMILY_GAUNTLET_ITEMS:
        return str(worn)
    inventory = player_data.get("inventory", {}) or {}
    if isinstance(inventory, Mapping):
        for item_name in FAMILY_GAUNTLET_ITEMS:
            try:
                if int(inventory.get(item_name, 0) or 0) > 0:
                    return item_name
            except (TypeError, ValueError, OverflowError):
                continue
    return ""


def _enchantment_for_item(item_name: str) -> str:
    return next(
        (
            enchantment
            for enchantment, enchanted_item in FAMILY_GAUNTLET_ENCHANTMENTS.items()
            if enchanted_item == item_name
        ),
        "",
    )


def sanitize_cooking_gauntlets_state_pure(
    player_data: Mapping[str, object],
) -> dict[str, object]:
    data = _copy_state(player_data)
    enchantment = str(data.get("family_gauntlet_enchantment", "") or "")
    if enchantment not in FAMILY_GAUNTLET_ENCHANTMENTS:
        enchantment = _enchantment_for_item(_owned_gauntlet(data))
        if not enchantment and _quest_completed(data):
            enchantment = "family"
    data["family_gauntlet_enchantment"] = enchantment

    choices = data.get("cooking_equipment_choices", {}) or {}
    data["cooking_equipment_choices"] = {
        str(target_id): str(choice)
        for target_id, choice in (choices.items() if isinstance(choices, Mapping) else ())
        if isinstance(target_id, str)
        and str(choice) in _VALID_COOKING_EQUIPMENT_CHOICES
        and str(choice) != "auto"
    }

    swap = data.get("cooking_equipment_swap", {}) or {}
    target_id = swap.get("target_id") if isinstance(swap, Mapping) else None
    displaced_item = swap.get("displaced_item") if isinstance(swap, Mapping) else None
    if isinstance(target_id, str) and target_id:
        data["cooking_equipment_swap"] = {
            "target_id": target_id,
            "displaced_item": displaced_item if isinstance(displaced_item, str) else "",
        }
    else:
        data["cooking_equipment_swap"] = {}
    return data


def cooking_equipment_choice_pure(
    player_data: Mapping[str, object], target_id: str
) -> str:
    choices = player_data.get("cooking_equipment_choices", {}) or {}
    choice = choices.get(target_id, "auto") if isinstance(choices, Mapping) else "auto"
    return str(choice) if str(choice) in _VALID_COOKING_EQUIPMENT_CHOICES else "auto"


def set_cooking_equipment_choice_pure(
    player_data: Mapping[str, object], target_id: str, choice: str
) -> tuple[dict[str, object], bool]:
    if not isinstance(target_id, str) or not target_id or choice not in _VALID_COOKING_EQUIPMENT_CHOICES:
        return dict(player_data), False
    data = sanitize_cooking_gauntlets_state_pure(player_data)
    choices = dict(data["cooking_equipment_choices"])
    if choice == "auto":
        choices.pop(target_id, None)
    else:
        choices[target_id] = choice
    data["cooking_equipment_choices"] = choices
    return data, True


def cooking_gauntlets_worn_pure(player_data: Mapping[str, object]) -> bool:
    equipment = player_data.get("equipment", {}) or {}
    return isinstance(equipment, Mapping) and equipment.get("hands") == COOKING_GAUNTLETS


def cooking_gauntlets_beneficial_pure(
    player_data: Mapping[str, object],
    target_id: str,
    *,
    cadence_live_enabled: bool,
) -> bool:
    """Whether the target's policy wants gauntlets: the saved Cooking choice,
    or Casual only when they raise the success chance of the active roll."""
    spec = COOKING_DATA[target_id]
    if not spec.get("cooking_gauntlet_no_burn_level"):
        return False
    if cooking_equipment_choice_pure(player_data, target_id) == "cooking":
        return True
    embedded = cadence_live_enabled and (
        resolve_live_cadence_route_pure("cooking", target_id, player_data).mode
        == EMBEDDED_PROBABILITY
    )
    success_chance = (
        cooking_source_roll_chance_pure
        if embedded
        else calculate_cooking_success_probability_pure
    )
    level = effective_roll_level_pure(
        player_data, "cooking", player_data.get("cooking_level", 1)
    )
    return success_chance(level, spec, has_cooking_gauntlets=True) > success_chance(
        level, spec
    )


def reconcile_cooking_equipment_pure(
    player_data: Mapping[str, object],
    target_id: str,
    *,
    beneficial: bool,
) -> dict[str, object]:
    """Apply target-local auto equipment without owning manual slot changes."""
    data = sanitize_cooking_gauntlets_state_pure(player_data)
    inventory = dict(data["inventory"])
    equipment = dict(data["equipment"])
    swap = dict(data["cooking_equipment_swap"])
    wants_gauntlets = beneficial and cooking_equipment_choice_pure(data, target_id) != "none"

    if swap:
        if equipment.get("hands") != COOKING_GAUNTLETS:
            swap = {}
        elif wants_gauntlets:
            swap["target_id"] = target_id
        else:
            equipment.pop("hands", None)
            inventory[COOKING_GAUNTLETS] = inventory.get(COOKING_GAUNTLETS, 0) + 1
            displaced = str(swap.get("displaced_item", "") or "")
            if displaced and int(inventory.get(displaced, 0) or 0) > 0:
                inventory[displaced] -= 1
                equipment["hands"] = displaced
            swap = {}

    if wants_gauntlets and equipment.get("hands") != COOKING_GAUNTLETS and not swap:
        if int(inventory.get(COOKING_GAUNTLETS, 0) or 0) > 0:
            displaced = str(equipment.get("hands", "") or "")
            if displaced:
                inventory[displaced] = inventory.get(displaced, 0) + 1
            inventory[COOKING_GAUNTLETS] -= 1
            equipment["hands"] = COOKING_GAUNTLETS
            swap = {"target_id": target_id, "displaced_item": displaced}

    data["inventory"] = inventory
    data["equipment"] = equipment
    data["cooking_equipment_swap"] = swap
    return data


def apply_family_gauntlet_conversion_pure(
    player_data: Mapping[str, object], source_item: str
) -> tuple[dict[str, object], bool, str]:
    if source_item not in {
        "Family gauntlets",
        "Goldsmith gauntlets",
        "Chaos gauntlets",
    }:
        return dict(player_data), False, "Choose Family, Goldsmith, or Chaos gauntlets."
    if not _quest_completed(player_data):
        return dict(player_data), False, "Complete Family Crest first."

    data = sanitize_cooking_gauntlets_state_pure(player_data)
    inventory = dict(data["inventory"])
    equipment = dict(data["equipment"])
    worn = equipment.get("hands") == source_item
    if not worn and int(inventory.get(source_item, 0) or 0) <= 0:
        return dict(player_data), False, f"You do not own {source_item}."

    cost = 0 if source_item == "Family gauntlets" else GAUNTLET_REENCHANT_COST
    if int(inventory.get("Coins", 0) or 0) < cost:
        return dict(player_data), False, f"You need {cost:,} Coins."
    inventory["Coins"] = int(inventory.get("Coins", 0) or 0) - cost
    if worn:
        equipment["hands"] = COOKING_GAUNTLETS
    else:
        inventory[source_item] = int(inventory.get(source_item, 0) or 0) - 1
        inventory[COOKING_GAUNTLETS] = int(inventory.get(COOKING_GAUNTLETS, 0) or 0) + 1
    data["inventory"] = inventory
    data["equipment"] = equipment
    data["family_gauntlet_enchantment"] = "cooking"
    data["cooking_equipment_swap"] = {}
    return data, True, (
        "Caleb enchanted the gauntlets for Cooking."
        if cost == 0
        else f"Caleb re-enchanted the gauntlets for {cost:,} Coins."
    )


def family_gauntlet_conversion_state_pure(
    player_data: Mapping[str, object], source_item: str
) -> dict[str, object]:
    eligible_item = source_item in {
        "Family gauntlets",
        "Goldsmith gauntlets",
        "Chaos gauntlets",
    }
    inventory = player_data.get("inventory", {}) or {}
    equipment = player_data.get("equipment", {}) or {}
    owned = (
        isinstance(inventory, Mapping)
        and int(inventory.get(source_item, 0) or 0) > 0
    ) or (
        isinstance(equipment, Mapping) and equipment.get("hands") == source_item
    )
    cost = 0 if source_item == "Family gauntlets" else GAUNTLET_REENCHANT_COST
    coins = int(inventory.get("Coins", 0) or 0) if isinstance(inventory, Mapping) else 0
    completed = _quest_completed(player_data)
    enabled = eligible_item and owned and completed and coins >= cost
    reason = ""
    if eligible_item and not completed:
        reason = "Complete Family Crest first."
    elif eligible_item and not owned:
        reason = f"You do not own {source_item}."
    elif eligible_item and coins < cost:
        reason = f"You need {cost:,} Coins."
    return {
        "visible": eligible_item,
        "enabled": enabled,
        "cost": cost,
        "reason": reason,
    }


def recover_family_gauntlets_pure(
    player_data: Mapping[str, object]
) -> tuple[dict[str, object], bool, str]:
    if not _quest_completed(player_data):
        return dict(player_data), False, "Complete Family Crest first."
    data = sanitize_cooking_gauntlets_state_pure(player_data)
    if _owned_gauntlet(data):
        return dict(player_data), False, "You already own a pair of Family Crest gauntlets."
    enchantment = str(data.get("family_gauntlet_enchantment", "") or "")
    item_name = FAMILY_GAUNTLET_ENCHANTMENTS.get(enchantment)
    if not item_name:
        return dict(player_data), False, "No previous gauntlet enchantment is recorded."
    inventory = dict(data["inventory"])
    inventory[item_name] = int(inventory.get(item_name, 0) or 0) + 1
    data["inventory"] = inventory
    return data, True, f"Dimintheis replaced your {item_name} for free."


def family_gauntlet_recovery_state_pure(
    player_data: Mapping[str, object]
) -> dict[str, object]:
    data = sanitize_cooking_gauntlets_state_pure(player_data)
    enchantment = str(data.get("family_gauntlet_enchantment", "") or "")
    item_name = FAMILY_GAUNTLET_ENCHANTMENTS.get(enchantment, "")
    completed = _quest_completed(data)
    owned = _owned_gauntlet(data)
    return {
        "enabled": completed and bool(item_name) and not owned,
        "item_name": item_name,
        "reason": (
            ""
            if completed and item_name and not owned
            else "You still own a Family Crest gauntlet pair."
            if owned
            else "No previous enchantment is recorded."
        ),
    }
