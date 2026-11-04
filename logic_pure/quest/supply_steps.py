"""Supply steps: quest reviews that make a missing stage item from supplies the player brought.

A quest declares Utility, Herblore or local recipes attached to its data. When
the current stage lacks an item, the quest plans its whole chain on a bank copy.
A recipe whose product or a later product is held is never reached, and the
review runs the plan's first recipe
for one batch. The plan treats a supply that no recipe makes as brought, so one
pass names every missing supply, and any missing supply stops the quest before
a review spends supplies on a stage it cannot finish.
"""

from .completion_rewards import _apply_quest_xp_rewards
from .skill_levels import skill_level_requirement_reason_pure
from .stage_items import _has_quest_tool
from ..production.utility_activity import apply_utility_activity_pure
from ..logic_pure_state import _copy_player_data_with_nested, _positive_int


def _recipes_by_product(quest_data, quest_id):
    quest = (quest_data or {}).get(quest_id) or {}
    return {recipe["action"]["output_item"]: recipe for recipe in quest.get("supply_recipes", ())}


def _supply_options(blockers, recipes):
    """A held alternative already passed; prepare the first declared quest product."""
    rows = []
    for blocker in blockers:
        options = blocker.get("options", ()) if blocker.get("kind") == "missing_item_option" else ()
        option = next((row for row in options if row["item_name"] in recipes), None)
        rows.append(dict(blocker, kind="missing_item", **option) if option else blocker)
    return tuple(rows)


def _makes(blocker, recipes):
    return blocker.get("kind") == "missing_item" and blocker.get("item_name") in recipes


def _run(recipe, inventory):
    made, _, ok, _ = apply_utility_activity_pure("supply", inventory, {"supply": recipe["action"]})
    if not ok:
        raise ValueError(f"Supply recipe {recipe['step']} refused its planned inputs")
    return made


def _recipe_blockers(player_data, recipe, stage):
    action = recipe["action"]
    reasons = [reason for requirement in action.get("required_skills", ())
               if (reason := skill_level_requirement_reason_pure(player_data, requirement))]
    reasons.extend(f"Needs {tool} x{amount} for {recipe['step']}"
                   for tool, amount in action.get("required_tools", {}).items()
                   if not _has_quest_tool(player_data, tool, amount))
    return tuple(dict(stage=stage, kind="supply_requirement", reason=reason, source=action.get("source", ""))
                 for reason in reasons)


def _plan_stage(player_data, recipes, blockers):
    """The recipes to run in order, and the missing supplies of each stage item the quest makes."""
    inventory = dict(player_data.get("inventory", {}) or {})
    plan = []

    def plan_item(item, amount, step):
        """Plan ``amount`` of ``item`` on the bank copy; the supplies it lacks that no recipe makes."""
        nonlocal inventory
        missing = []
        while _positive_int(inventory.get(item, 0), 0) < amount:
            recipe = recipes.get(item)
            if recipe is None:
                inventory = {**inventory, item: amount}
                return [(item, amount, step)]
            for supply, quantity in recipe["action"]["requirements"].items():
                missing += plan_item(supply, quantity, recipe["step"])
            inventory = _run(recipe, inventory)
            plan.append(recipe)
        return missing

    missing = {
        index: plan_item(blocker["item_name"], blocker["quantity"], "")
        for index, blocker in enumerate(blockers)
        if _makes(blocker, recipes)
    }
    return plan, missing


def supply_step_blockers_pure(player_data, quest_id, quest_data, blockers):
    """Replace a stage item the quest cannot make with each missing supply and the step it is for."""
    recipes = _recipes_by_product(quest_data, quest_id)
    if not recipes:
        return blockers
    blockers = _supply_options(blockers, recipes)
    plan, missing = _plan_stage(player_data, recipes, blockers)
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
    for recipe in plan:
        rewritten.extend(_recipe_blockers(player_data, recipe, blockers[0]["stage"]))
    return tuple({row["reason"]: row for row in rewritten}.values())


def supply_step_pure(player_data, quest_id, quest_data, blockers):
    """The recipe this quest review runs, or None when the stage needs none or lacks a supply."""
    recipes = _recipes_by_product(quest_data, quest_id)
    blockers = _supply_options(blockers, recipes)
    if not blockers or not all(_makes(blocker, recipes) for blocker in blockers):
        return None
    plan, missing = _plan_stage(player_data, recipes, blockers)
    if any(missing.values()) or any(_recipe_blockers(player_data, recipe, 0) for recipe in plan):
        return None
    return plan[0]


def apply_supply_step_pure(player_data, recipe):
    data = _copy_player_data_with_nested(player_data)
    data["inventory"] = _run(recipe, data["inventory"])
    _apply_quest_xp_rewards(data, recipe["action"])
    return data


def supply_step_phase_pure(player_data, quest_id, quest_data, blockers):
    """The review notice for the supply step this review runs, or None."""
    recipe = supply_step_pure(player_data, quest_id, quest_data, blockers)
    if recipe is None:
        return None
    product = recipe["action"]["output_item"]
    inventory = player_data.get("inventory", {}) or {}
    made = _run(recipe, inventory)[product] - _positive_int(inventory.get(product, 0), 0)
    return {"notice": f"+{made} {product}", "xp_rewards": recipe["action"].get("xp_rewards", ())}
