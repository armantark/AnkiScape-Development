"""Supply steps: quest reviews that make a missing stage item from supplies the player brought.

A quest declares supply recipes, each an existing Utility row that core attaches
to the quest data. When the current stage lacks an item, the quest plans that
item's whole chain on a copy of the bank, so a recipe whose product or a later
product is held is never reached, and the review runs the plan's first recipe
for one batch. The plan treats a supply that no recipe makes as brought, so one
pass names every missing supply, and any missing supply stops the quest before
a review spends supplies on a stage it cannot finish.
"""

from ..production.utility_activity import apply_utility_activity_pure
from ..logic_pure_state import _copy_player_data_with_nested, _positive_int


def _recipes_by_product(quest_data, quest_id):
    quest = (quest_data or {}).get(quest_id) or {}
    return {recipe["utility"]["output_item"]: recipe for recipe in quest.get("supply_recipes", ())}


def _makes(blocker, recipes):
    return blocker.get("kind") == "missing_item" and blocker.get("item_name") in recipes


def _run(recipe, inventory):
    utility_id = recipe["utility_id"]
    made, _, ok, _ = apply_utility_activity_pure(utility_id, inventory, {utility_id: recipe["utility"]})
    if not ok:
        # The plan supplied every input, so a refusal is a Utility gate it does not model.
        raise ValueError(f"Supply recipe {utility_id} refused its planned inputs")
    return made


def _plan_item(inventory, recipes, item, amount, step, plan, missing):
    while _positive_int(inventory.get(item, 0), 0) < amount:
        recipe = recipes.get(item)
        if recipe is None:
            missing.append((item, amount, step))
            return {**inventory, item: amount}
        for supply, quantity in recipe["utility"]["requirements"].items():
            inventory = _plan_item(inventory, recipes, supply, quantity, recipe["step"], plan, missing)
        inventory = _run(recipe, inventory)
        plan.append(recipe)
    return inventory


def _plan_stage(player_data, recipes, blockers):
    """The recipes to run in order, and the missing supplies of each stage item the quest makes."""
    inventory = dict(player_data.get("inventory", {}) or {})
    plan, missing = [], {}
    for index, blocker in enumerate(blockers):
        if _makes(blocker, recipes):
            missing[index] = []
            inventory = _plan_item(inventory, recipes, blocker["item_name"], blocker["quantity"], "", plan, missing[index])
    return plan, missing


def supply_step_blockers_pure(player_data, quest_id, quest_data, blockers):
    """Replace a stage item the quest cannot make with each missing supply and the step it is for."""
    recipes = _recipes_by_product(quest_data, quest_id)
    if not recipes:
        return blockers
    _, missing = _plan_stage(player_data, recipes, blockers)
    inventory = player_data.get("inventory", {}) or {}
    rewritten = []
    for index, blocker in enumerate(blockers):
        supplies = missing.get(index)
        if not supplies:
            rewritten.append(blocker)
            continue
        rewritten.extend(
            dict(blocker, item_name=item, quantity=amount, owned=_positive_int(inventory.get(item, 0), 0),
                 reason=f"Needs {item} x{amount} for {step}")
            for item, amount, step in supplies
        )
    return tuple(rewritten)


def supply_step_pure(player_data, quest_id, quest_data, blockers):
    """The recipe this quest review runs, or None when the stage needs none or lacks a supply."""
    recipes = _recipes_by_product(quest_data, quest_id)
    if not blockers or not all(_makes(blocker, recipes) for blocker in blockers):
        return None
    plan, missing = _plan_stage(player_data, recipes, blockers)
    return None if any(missing.values()) else plan[0]


def apply_supply_step_pure(player_data, recipe):
    data = _copy_player_data_with_nested(player_data)
    data["inventory"] = _run(recipe, data["inventory"])
    return data


def supply_step_phase_pure(player_data, quest_id, quest_data, blockers):
    """The review notice for the supply step this review runs, or None."""
    recipe = supply_step_pure(player_data, quest_id, quest_data, blockers)
    if recipe is None:
        return None
    product = recipe["utility"]["output_item"]
    inventory = player_data.get("inventory", {}) or {}
    made = _run(recipe, inventory)[product] - _positive_int(inventory.get(product, 0), 0)
    return {"notice": f"+{made} {product}"}

