"""The product of an action: the item its queue entry counts and its XP popup shows.

A review's item changes list everything it moved, loot, drunk potions and
emptied vials included. The product is the item the player picked the action
for, read from the action's target data, so "+1 Vial" from a potion or a
fight's loot never reaches the popup or a queue count.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .constants import QUEST_UNLOCK_RULES, UTILITY_ACTIVITY_DATA
from .skill_registry import get_skill
from .skill_guide_locks import target_lock_reasons_pure
from ..data.construction_data import NAIL_DATA
from ..logic.summoning_logic import summoning_action_requirements_pure
from ..logic_pure.logic_pure_gathering import eligible_fishing_fish_pure
from ..logic_pure.logic_pure_runecrafting import _runecrafting_multiplier_info
from ..logic_pure.logic_pure_production import utility_activity_locked_reasons_pure
from ..logic_pure.logic_pure_magic import effective_magic_rune_cost_pure, magic_used_items_pure
from ..logic.cadence_coverage import FOREGROUND_ROUTE_TABLES


def spec_field_pure(spec: Any, name: str) -> Any:
    """One field of a target's data row, which is a mapping for some skills and a record for others."""
    return spec.get(name) if isinstance(spec, Mapping) else getattr(spec, name, None)


def action_target_spec_pure(action: Mapping[str, Any]) -> Any:
    """The data row of a skill or combat action's target; None for other kinds."""
    if action.get("kind") == "combat":
        return FOREGROUND_ROUTE_TABLES["combat"].get(action.get("target"))
    skill = get_skill(str(action.get("skill") or "")) if action.get("kind") == "skill" else None
    if skill is None:
        return None
    return FOREGROUND_ROUTE_TABLES.get(skill.review_handler_key or "", {}).get(action.get("target"))


def action_product_items_pure(action: Mapping[str, Any]) -> tuple[str, ...]:
    """The items an action makes; empty for fights, quests and actions that make none."""
    if action.get("kind") == "utility":
        # A minigame's ``outputs`` lists its reward shop, not what one review makes.
        spec = UTILITY_ACTIVITY_DATA.get(action.get("utility_id"), {})
        return _item_names((spec.get("output_item"),))
    spec = action_target_spec_pure(action) if action.get("kind") == "skill" else None
    if spec is None:
        return ()
    names = [spec_field_pure(spec, "output_item")]
    if spec_field_pure(spec, "alternate_output_level"):
        # Mining's level-gated second product: Rune essence becomes Pure essence.
        names.append(spec_field_pure(spec, "alternate_output_item"))
    names += [spec_field_pure(row, "item") for row in spec_field_pure(spec, "weighted_outputs") or ()]
    names += [spec_field_pure(fish, "output_item") for fish in spec_field_pure(spec, "fish") or ()]
    if not any(names):
        names += list(spec_field_pure(spec, "outputs") or ())
    return _item_names(names)


def action_used_input_pure(action: Mapping[str, Any]) -> str:
    """The one item an action that makes nothing uses up, such as Bones for burying; empty otherwise.

    The player plans such an action by that item ("bury 100 bones"), so its
    queue entry counts it instead of reviews.
    """
    needs = tuple(_requirements(action))
    return needs[0] if len(needs) == 1 and not action_product_items_pure(action) else ""


def action_use_size_pure(action: Mapping[str, Any]) -> int:
    """How many of its used input one run of the action uses up; 0 for an action that counts no input."""
    used = action_used_input_pure(action)
    return int(_requirements(action)[used]) if used else 0


def _requirements(action: Mapping[str, Any]) -> Mapping[str, Any]:
    if action.get("kind") == "utility":
        spec = UTILITY_ACTIVITY_DATA.get(action.get("utility_id"), {})
    elif action.get("kind") == "skill":
        spec = action_target_spec_pure(action)
    else:
        return {}
    return (spec_field_pure(spec, "requirements") or {}) if spec else {}


def product_gains_pure(action: Mapping[str, Any], changes: Mapping[str, int]) -> dict[str, int]:
    """The review's gains of the action's product items, from its item changes."""
    products = action_product_items_pure(action)
    return {item: count for item, count in changes.items() if item in products and count > 0}


def _item_names(values: Iterable[Any]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if isinstance(value, str) and value))


_PLANNED_STOCK = 2_147_483_647
_Stock = list[dict[tuple[str, ...], int]]


def _inputs_and_yield(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> tuple[dict[str, tuple[str, ...]], dict[str, int], int]:
    """What one run uses, as alternatives per input and an amount, and the products it makes."""
    spec = (UTILITY_ACTIVITY_DATA.get(action["utility_id"], {}) if action["kind"] == "utility" else action_target_spec_pure(action))
    made = sum(_batch_products(player_data, action).values()) or 1
    if action.get("skill") == "Summoning":
        needs = summoning_action_requirements_pure(player_data, str(action["target"]))
        return {item: (item,) for item in needs}, needs, made
    if essence := spec_field_pure(spec, "essence_items"):
        return {"essence": tuple(essence)}, {"essence": 1}, made
    needs = dict(spec_field_pure(spec, "requirements") or {})
    for item, amount in effective_magic_rune_cost_pure(player_data, spec_field_pure(spec, "rune_cost")).items():
        needs[item] = needs.get(item, 0) + amount
    options = {"Nails": tuple(NAIL_DATA), **dict(spec_field_pure(spec, "material_options") or {})}
    for field in ("bait_options", "any_requirements", "openable_items"):
        if choices := spec_field_pure(spec, field):
            needs.setdefault(choices[0], 1)
            options[choices[0]] = tuple(choices)
    return {item: tuple(options.get(item) or (item,)) for item in needs}, needs, made


def _used_items(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> set[str]:
    """Every item a run of the action can use up; never a tool, an access item or a wage, so those locks stay."""
    alternatives, _needs, _made = _inputs_and_yield(player_data, action)
    items = {item for options in alternatives.values() for item in options}
    spec = (UTILITY_ACTIVITY_DATA.get(action["utility_id"], {}) if action["kind"] == "utility" else action_target_spec_pure(action))
    if rune := spec_field_pure(spec, "component_rune"):
        items.update(("Pure essence", rune, spec_field_pure(spec, "consumed_talisman")))
    if action.get("skill") == "Magic":
        items.update(magic_used_items_pure(spec))
    if "Nails" in items:
        items.update(NAIL_DATA)
    return items


def _action_locks(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> tuple[str, ...]:
    """What the action's target row says locks it now; empty for an action no row list locks."""
    if action.get("kind") == "skill":
        return target_lock_reasons_pure(player_data, get_skill(action["skill"]).id, action["target"])
    if action.get("utility_id") in UTILITY_ACTIVITY_DATA:
        return utility_activity_locked_reasons_pure(
            player_data, action["utility_id"], UTILITY_ACTIVITY_DATA, QUEST_UNLOCK_RULES
        )
    return ()


def _spend_stock(stock: _Stock, items: tuple[str, ...], amount: int) -> None:
    for bank in stock:
        for products in bank:
            if set(products) <= set(items):
                used = min(amount, bank[products])
                bank[products] -= used
                amount -= used


def _stock_count(stock: _Stock, items: tuple[str, ...]) -> int:
    # A random product can fund a recipe only if that recipe accepts every outcome.
    return sum(count for bank in stock for products, count in bank.items() if set(products) <= set(items))


def _planned_products(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> tuple[str, ...]:
    spec = action_target_spec_pure(action)
    if level := spec_field_pure(spec, "alternate_output_level"):
        skill = get_skill(action["skill"])
        item = "alternate_output_item" if int(player_data.get(f"{skill.id}_level") or 1) >= level else "output_item"
        return _item_names((spec_field_pure(spec, item),))
    if spec_field_pure(spec, "fish"):
        fish = eligible_fishing_fish_pure(
            spec, int(player_data.get("fishing_level") or 1),
            int(player_data.get("strength_level") or 1), int(player_data.get("agility_level") or 1),
        )
        return _item_names(spec_field_pure(row, "output_item") for row in fish)
    return action_product_items_pure(action)


def _batch_products(player_data: Mapping[str, Any], action: Mapping[str, Any]) -> dict[tuple[str, ...], int]:
    """One paid batch: alternatives share a count, simultaneous products keep their quantities."""
    products = _planned_products(player_data, action)
    if not products:
        return {}
    spec = (UTILITY_ACTIVITY_DATA.get(action["utility_id"], {}) if action["kind"] == "utility" else action_target_spec_pure(action))
    outputs = spec_field_pure(spec, "outputs")
    if isinstance(outputs, Mapping) and not spec_field_pure(spec, "output_item"):
        return {(item,): amount for item, amount in outputs.items()}
    made = int(spec_field_pure(spec, "output_qty") or spec_field_pure(spec, "output_quantity") or 1)
    if spec_field_pure(spec, "essence_items"):
        made = _runecrafting_multiplier_info(spec, int(player_data.get("runecrafting_level") or 1))[0]
    return {products: made}


def _project_entry(player_data: Mapping[str, Any], stock: _Stock, entry: Mapping[str, Any], done: int) -> dict[tuple[str, ...], int]:
    action = entry["action"]
    unit = _supply_unit(action)
    if entry["count"] is None or unit not in {"items", "uses"}:
        return {}
    remaining = max(0, entry["count"] - done)
    alternatives, needs, made = _inputs_and_yield(player_data, action)
    runs = (remaining + made - 1) // made if unit == "items" else remaining
    if needs:
        runs = min(runs, *(_stock_count(stock, alternatives[item]) // max(1, int(amount)) for item, amount in needs.items()))
        for item, amount in needs.items():
            _spend_stock(stock, alternatives[item], runs * int(amount))
    # A requested count may end inside a batch; the queue keeps the paid-for batch whole.
    return {products: runs * amount for products, amount in _batch_products(player_data, action).items()}


def _projected_stock(player_data: Mapping[str, Any], queue: Mapping[str, Any]) -> _Stock:
    """Reserve inputs in queue order; each remaining output retains its entry number."""
    stock = [{(item,): count for item, count in (player_data.get("inventory") or {}).items()}]
    for position, entry in enumerate(queue["entries"]):
        stock.append(_project_entry(player_data, stock, entry, queue["done"] if position == 0 else 0))
    return stock


def _supply_count(player_data: Mapping[str, Any], items: tuple[str, ...], queue: Mapping[str, Any]) -> int:
    return _stock_count(_projected_stock(player_data, queue), items)


def queue_plan_refusal_pure(player_data: Mapping[str, Any], action: Mapping[str, Any], queue: Mapping[str, Any]) -> str:
    """Keep consumable-only locks until earlier entries really supply a runnable batch."""
    unlimited = {**(player_data.get("inventory") or {}), **dict.fromkeys(_used_items(player_data, action), _PLANNED_STOCK)}
    if _action_locks({**player_data, "inventory": unlimited}, action):
        return ""
    stock = _projected_stock(player_data, queue)
    alternatives, _needs, _made = _inputs_and_yield(player_data, action)
    projected = {}
    for bank in stock:
        for products, count in bank.items():
            if len(products) == 1 or any(set(products) <= set(items) for items in alternatives.values()):
                item = products[0]
                projected[item] = projected.get(item, 0) + count
    reasons = _action_locks({**player_data, "inventory": projected}, action)
    return "Requires: " + ", ".join(reasons) if reasons else ""


def action_supply_limit_pure(player_data: Mapping[str, Any], action: Mapping[str, Any], queue: Mapping[str, Any]) -> int | None:
    """The most of the entry's unit the Bank and earlier entries supply inputs for; None when no Bank item limits it.

    An entry that counts reviews has no such limit: one review can use several
    inputs, so its count in reviews is unknown.
    """
    unit = _supply_unit(action)
    if unit not in {"items", "uses"}:
        return None
    alternatives, needs, made = _inputs_and_yield(player_data, action)
    if not needs:
        return None
    if unit == "uses":
        return sum(_supply_count(player_data, items, queue) for items in alternatives.values())
    return min(
        _supply_count(player_data, alternatives[need], queue) // max(1, int(amount)) for need, amount in needs.items()
    ) * made


def _supply_unit(action: Mapping[str, Any]) -> str:
    if action_product_items_pure(action):
        return "items"
    return "uses" if action_used_input_pure(action) else "reviews"


def funded_queue_entry_pure(player_data, entry, queue, progress):
    """Reconcile an edited entry to its funded remainder, or return its existing stop reason."""
    reason = queue_plan_refusal_pure(player_data, entry["action"], queue)
    if reason:
        return None, reason
    limit = action_supply_limit_pure(player_data, entry["action"], queue)
    if limit is None or entry["count"] is None:
        return entry, ""
    count = min(entry["count"], progress + limit)
    return ({**entry, "count": count}, "") if count > progress else (None, "Requires: materials")
