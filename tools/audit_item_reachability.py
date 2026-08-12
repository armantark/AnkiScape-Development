#!/usr/bin/env python3
"""Audit whether live AnkiScape action inputs have an acquisition route.

This is deliberately a reachability audit, not a claim that every route has
full historical fidelity. It treats live shops, Combat drops, quest-granted
items and rewards, gathering outputs, and zero-input actions as source nodes,
then closes over the current action graph. The JSON output is stable enough for
tests and later completion-audit tooling.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _names(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value} if value else set()
    if isinstance(value, Mapping):
        return {str(name) for name in value if isinstance(name, str) and name}
    if isinstance(value, (tuple, list, set)):
        names: set[str] = set()
        for entry in value:
            if isinstance(entry, str):
                names.add(entry)
            elif isinstance(entry, Mapping):
                names.update(_names(entry.get("item") or entry.get("item_name") or entry.get("output_item")))
            elif isinstance(entry, (tuple, list)) and entry and isinstance(entry[0], str):
                names.add(entry[0])
        return names
    return set()


def _outputs(spec: Mapping[str, Any]) -> set[str]:
    outputs = _names(spec.get("outputs")) | _names(spec.get("byproducts"))
    outputs |= _names(spec.get("output_item")) | _names(spec.get("alternate_output_item"))
    outputs |= _names(spec.get("byproduct_item"))
    for fish in spec.get("fish", ()) or ():
        if isinstance(fish, Mapping):
            outputs |= _names(fish.get("output_item"))
    for weighted in spec.get("weighted_outputs", ()) or ():
        if isinstance(weighted, Mapping):
            outputs |= _names(weighted.get("item") or weighted.get("output_item"))
        elif isinstance(weighted, (tuple, list)) and weighted and isinstance(weighted[0], str):
            outputs.add(weighted[0])
    return outputs


def _requirements(spec: Mapping[str, Any]) -> tuple[set[str], tuple[set[str], ...]]:
    required = (
        _names(spec.get("requirements"))
        | _names(spec.get("required_items"))
        | _names(spec.get("tools"))
        | _names(spec.get("rune_cost"))
    )
    alternatives: list[set[str]] = []
    essence = _names(spec.get("essence_items"))
    if essence:
        alternatives.append(essence)
    bait = _names(spec.get("bait_options"))
    if bait:
        alternatives.append(bait)
    reachability_inputs = _names(spec.get("reachability_inputs"))
    if reachability_inputs:
        alternatives.append(reachability_inputs)
    return required, tuple(alternatives)


def _drop_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in {"item", "item_name", "output_item"}:
                names |= _names(child)
            else:
                names |= _drop_names(child)
    elif isinstance(value, (tuple, list, set)):
        if value and isinstance(value, (tuple, list)) and isinstance(value[0], str):
            names.add(value[0])
        else:
            for child in value:
                names |= _drop_names(child)
    return names


import pkg_alias  # noqa: F401  (installs the ankiscape package alias)


def _close_actions(
    actions: Iterable[Mapping[str, Any]],
    seed_sources: Mapping[str, set[str]],
) -> tuple[set[str], dict[str, str], list[Mapping[str, Any]]]:
    reachable = set(seed_sources)
    route = {item: sorted(sources)[0] for item, sources in seed_sources.items()}
    unresolved = list(actions)
    changed = True
    while changed:
        changed = False
        remaining: list[Mapping[str, Any]] = []
        for action in unresolved:
            required_ok = action["required"].issubset(reachable)
            alternatives_ok = all(
                bool(group & reachable) for group in action["alternatives"]
            )
            if required_ok and alternatives_ok:
                for item in action["outputs"]:
                    if item not in reachable:
                        reachable.add(item)
                        route[item] = action["id"]
                        changed = True
            else:
                remaining.append(action)
        unresolved = remaining
    return reachable, route, unresolved


def _quest_stage_sources(
    quest_data: Mapping[str, Mapping[str, Any]],
    registered_items: set[str],
    *,
    combat_encounter_satisfiable: Callable[[Mapping[str, Any]], bool] | None = None,
) -> tuple[dict[str, set[str]], list[dict[str, Any]]]:
    sources: dict[str, set[str]] = defaultdict(set)
    blocked: list[dict[str, Any]] = []
    combat_encounter_satisfiable = combat_encounter_satisfiable or (lambda _encounter: True)
    for quest_id, quest in quest_data.items():
        mandatory_actions: set[str] = set()
        variant_actions: dict[str, set[str]] = defaultdict(set)
        for stage in quest.get("stage_requirements", ()) or ():
            if not isinstance(stage, Mapping):
                continue
            variant = str(stage.get("variant", "") or "")
            emitted_actions = mandatory_actions | variant_actions[variant] if variant else (
                mandatory_actions | set().union(*variant_actions.values())
                if variant_actions
                else mandatory_actions
            )
            required_actions = _names(stage.get("required_actions"))
            products = _names(stage.get("produced_inventory")) & registered_items
            combat_products: dict[str, set[str]] = {}
            blocked_combat_products: dict[str, set[str]] = {}
            for encounter in stage.get("combat_encounters", ()) or ():
                if not isinstance(encounter, Mapping):
                    continue
                encounter_id = str(encounter.get("encounter_id", "unknown"))
                guaranteed_drops = _names(encounter.get("guaranteed_drops")) & registered_items
                if not guaranteed_drops:
                    continue
                combat_products[encounter_id] = guaranteed_drops
                if not combat_encounter_satisfiable(encounter):
                    blocked_combat_products[encounter_id] = guaranteed_drops
            missing_actions = required_actions - emitted_actions
            stage_id = stage.get("stage", "unknown")
            if (missing_actions and (products or combat_products)) or blocked_combat_products:
                blocked.append(
                    {
                        "quest_id": quest_id,
                        "quest": str(quest.get("display_name", quest_id)),
                        "stage": stage_id,
                        "products": sorted(products) if missing_actions else [],
                        "combat_products": {
                            encounter_id: sorted(items)
                            for encounter_id, items in sorted(combat_products.items())
                        } if missing_actions else {},
                        "blocked_combat_products": {
                            encounter_id: sorted(items)
                            for encounter_id, items in sorted(blocked_combat_products.items())
                        },
                        "required_actions": sorted(required_actions),
                        "missing_required_actions": sorted(missing_actions),
                    }
                )
            if missing_actions:
                continue
            for item in products:
                sources[item].add(f"quest-stage:{quest_id}:{stage_id}")
            for encounter_id, items in combat_products.items():
                if encounter_id in blocked_combat_products:
                    continue
                for item in items:
                    sources[item].add(f"quest-combat:{quest_id}:{encounter_id}")
            auto_actions = _names(stage.get("auto_actions"))
            if variant:
                variant_actions[variant].update(auto_actions)
            else:
                mandatory_actions.update(auto_actions)
    return sources, blocked


def _rank_root_orphans(
    root_orphans: Iterable[str],
    actions: Iterable[Mapping[str, Any]],
    seed_sources: Mapping[str, set[str]],
    baseline_reachable: set[str],
    baseline_unresolved_count: int,
) -> list[dict[str, Any]]:
    rows = []
    for item in root_orphans:
        candidate_sources = dict(seed_sources)
        candidate_sources[item] = {f"candidate:{item}"}
        reachable, _route, unresolved = _close_actions(actions, candidate_sources)
        newly_reachable = sorted(reachable - baseline_reachable)
        rows.append(
            {
                "item": item,
                "newly_reachable_item_count": len(newly_reachable),
                "newly_unblocked_action_count": (
                    baseline_unresolved_count - len(unresolved)
                ),
                "newly_reachable_items": newly_reachable,
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -row["newly_reachable_item_count"],
            -row["newly_unblocked_action_count"],
            row["item"],
        ),
    )


def build_reachability_report() -> dict[str, Any]:
    from ankiscape.data import combat_data
    from ankiscape.core import constants
    from ankiscape.data import farming_data
    from ankiscape.data import fist_of_guthix_data
    from ankiscape.data import pack_data
    from ankiscape.data import pyramid_plunder_data
    from ankiscape.data import shooting_star_data
    from ankiscape.data import shop_data
    from ankiscape.data.impling_jar_data import IMPLING_JAR_DATA
    from ankiscape.logic import shop_logic
    from ankiscape.data import sorceress_garden_data
    from ankiscape.data import thieving_data
    from ankiscape.data import woodcutting_data
    from ankiscape.logic_pure.logic_pure import (
        player_combat_level_pure,
        quest_combat_encounter_has_stats_pure,
    )

    registered_items = {definition.storage_key for definition in constants.ITEM_DEFINITIONS}
    maximum_combat_level = player_combat_level_pure(
        {
            "attack_level": 99,
            "defense_level": 99,
            "strength_level": 99,
            "constitution_level": 99,
            "prayer_level": 99,
            "ranged_level": 99,
            "magic_level": 99,
            "summoning_level": 99,
        }
    )

    def quest_combat_source_satisfiable(encounter: Mapping[str, Any]) -> bool:
        configs = encounter.get("npc_configs", {}) or {}
        minimum_combat = int(configs.get("minimum_player_combat", encounter.get("level", 0)) or 0)
        # Model the runtime with battle support enabled and a normal maxed player.
        return (
            quest_combat_encounter_has_stats_pure(encounter)
            and minimum_combat <= maximum_combat_level
        )

    action_tables = {
        "Mining": constants.ORE_DATA,
        "Woodcutting": constants.TREE_DATA,
        "Fishing": constants.FISHING_DATA,
        "Smithing": constants.SMITHING_DATA,
        "Crafting": constants.CRAFTING_DATA,
        "Fletching": constants.FLETCHING_DATA,
        "Firemaking": constants.FIREMAKING_DATA,
        "Cooking": constants.COOKING_DATA,
        "Runecrafting": constants.RUNECRAFTING_DATA,
        "Hunter": constants.HUNTER_DATA,
        "Herblore": constants.HERBLORE_DATA,
        "Magic": constants.MAGIC_DATA,
        "Prayer": constants.PRAYER_DATA,
        "Utility": constants.UTILITY_ACTIVITY_DATA,
    }

    actions: list[dict[str, Any]] = []
    consumers: dict[str, set[str]] = defaultdict(set)
    producers: dict[str, set[str]] = defaultdict(set)
    for family, table in action_tables.items():
        for action_id, raw_spec in table.items():
            if not isinstance(raw_spec, Mapping) or raw_spec.get("status", "implemented") != "implemented":
                continue
            required, alternatives = _requirements(raw_spec)
            outputs = _outputs(raw_spec)
            if not outputs:
                continue
            key = f"{family}:{action_id}"
            actions.append({"id": key, "required": required, "alternatives": alternatives, "outputs": outputs})
            for item in required | set().union(*alternatives) if alternatives else required:
                consumers[item].add(key)
            for item in outputs:
                producers[item].add(key)

    for crop_id, (seed, seedling, sapling) in farming_data.SAPLING_RECIPES.items():
        crop = farming_data.FARMING_CROPS_BY_ID[crop_id]
        if not crop.runnable:
            continue
        required = {seed, "Plant pot", "Gardening trowel"}
        alternatives = ({"Watering can", "Watering can (8)"},)
        outputs = {seedling, sapling}
        key = f"Farming:sapling:{crop_id}"
        actions.append(
            {
                "id": key,
                "required": required,
                "alternatives": alternatives,
                "outputs": outputs,
            }
        )
        for item in required | alternatives[0]:
            consumers[item].add(key)
        for item in outputs:
            producers[item].add(key)

    hatchets = {axe.display_name for axe in woodcutting_data.WOODCUTTING_AXES}
    for crop in farming_data.FARMING_CROPS:
        if not crop.runnable:
            continue
        plant_tool = (
            "Spade"
            if crop.patch_type in {"tree", "fruit_tree", "calquat", "spirit_tree"}
            else "Seed dibber"
        )
        required = {crop.seed_item, "Rake", plant_tool}
        alternatives: tuple[set[str], ...] = ()
        if crop.id == "willow":
            alternatives = ({"Secateurs", "Magic secateurs"},)
        elif crop.harvest_tool:
            required.add(crop.harvest_tool)
        if crop.output_item:
            key = f"Farming:{crop.id}"
            outputs = {crop.output_item}
            actions.append(
                {
                    "id": key,
                    "required": required,
                    "alternatives": alternatives,
                    "outputs": outputs,
                }
            )
            for item in required | set().union(*alternatives) if alternatives else required:
                consumers[item].add(key)
            producers[crop.output_item].add(key)
        if crop.root_item:
            key = f"Farming:clear:{crop.id}"
            root_requirements = required | {"Spade"}
            alternatives = (hatchets,)
            actions.append(
                {
                    "id": key,
                    "required": root_requirements,
                    "alternatives": alternatives,
                    "outputs": {crop.root_item},
                }
            )
            for item in root_requirements | hatchets:
                consumers[item].add(key)
            producers[crop.root_item].add(key)

    for target_id, spec in thieving_data.THIEVING_TARGETS.items():
        if spec.get("source_blocked"):
            continue
        outputs = _names(spec.get("guaranteed")) | _names(spec.get("loot"))
        if not outputs:
            continue
        alternatives: tuple[set[str], ...] = ()
        required_items_any = _names(spec.get("required_items_any"))
        if required_items_any:
            alternatives = (required_items_any,)
        key = f"Thieving:{target_id}"
        actions.append(
            {
                "id": key,
                "required": set(),
                "alternatives": alternatives,
                "outputs": outputs,
            }
        )
        for item in set().union(*alternatives) if alternatives else ():
            consumers[item].add(key)
        for item in outputs:
            producers[item].add(key)

    star_mining_key = "Activity:shooting_stars:mine"
    actions.append(
        {
            "id": star_mining_key,
            "required": set(),
            "alternatives": (),
            "outputs": {shooting_star_data.SHOOTING_STAR_STARDUST},
        }
    )
    producers[shooting_star_data.SHOOTING_STAR_STARDUST].add(
        star_mining_key
    )

    star_exchange_key = "Activity:shooting_stars:exchange"
    star_exchange_outputs = set(
        shooting_star_data.SHOOTING_STAR_REWARD_MAXIMA
    )
    actions.append(
        {
            "id": star_exchange_key,
            "required": {shooting_star_data.SHOOTING_STAR_STARDUST},
            "alternatives": (),
            "outputs": star_exchange_outputs,
        }
    )
    consumers[shooting_star_data.SHOOTING_STAR_STARDUST].add(
        star_exchange_key
    )
    for item in star_exchange_outputs:
        producers[item].add(star_exchange_key)

    fog_match_key = "Activity:fist_of_guthix:match"
    fog_token = "Fist of guthix token"
    actions.append(
        {
            "id": fog_match_key,
            "required": set(),
            "alternatives": (),
            "outputs": {fog_token},
        }
    )
    producers[fog_token].add(fog_match_key)
    for reward_id, reward in fist_of_guthix_data.FIST_OF_GUTHIX_REWARDS.items():
        family = fist_of_guthix_data.FIST_OF_GUTHIX_CONDITION_DATA[
            reward["family_id"]
        ]
        names_by_percent = family["names_by_percent"]
        charged = names_by_percent[max(names_by_percent)]
        spent = names_by_percent[min(names_by_percent)]
        buy_key = f"Activity:fist_of_guthix:buy:{reward_id}"
        actions.append(
            {
                "id": buy_key,
                "required": {fog_token},
                "alternatives": (),
                "outputs": {charged},
            }
        )
        consumers[fog_token].add(buy_key)
        producers[charged].add(buy_key)
        uncharge_key = f"Activity:fist_of_guthix:uncharge:{reward_id}"
        actions.append(
            {
                "id": uncharge_key,
                "required": {charged},
                "alternatives": (),
                "outputs": {spent},
            }
        )
        consumers[charged].add(uncharge_key)
        producers[spent].add(uncharge_key)
        recharge_key = f"Activity:fist_of_guthix:recharge:{reward_id}"
        actions.append(
            {
                "id": recharge_key,
                "required": {spent, fog_token},
                "alternatives": (),
                "outputs": {charged},
            }
        )
        consumers[spent].add(recharge_key)
        consumers[fog_token].add(recharge_key)
        producers[charged].add(recharge_key)
        ordered_names = [
            names_by_percent[percent]
            for percent in sorted(names_by_percent, reverse=True)
        ]
        for current, remainder in zip(ordered_names, ordered_names[1:]):
            degrade_key = (
                f"Activity:fist_of_guthix:degrade:{reward_id}:{current}"
            )
            actions.append(
                {
                    "id": degrade_key,
                    "required": {current},
                    "alternatives": (),
                    "outputs": {remainder},
                }
            )
            consumers[current].add(degrade_key)
            producers[remainder].add(degrade_key)

    garden_key = "Activity:sorceress_garden:harvest"
    garden_outputs = set(sorceress_garden_data.SORCERESS_GARDEN_HERB_POOL)
    garden_outputs.update(
        season.fruit
        for season in sorceress_garden_data.SORCERESS_GARDEN_SEASONS
    )
    garden_outputs.update(
        season.juice
        for season in sorceress_garden_data.SORCERESS_GARDEN_SEASONS
    )
    actions.append(
        {
            "id": garden_key,
            "required": set(),
            "alternatives": (),
            "outputs": garden_outputs,
        }
    )
    for item in garden_outputs:
        producers[item].add(garden_key)

    pyramid_key = "Activity:pyramid_plunder:loot"
    pyramid_outputs = {
        *pyramid_plunder_data.PYRAMID_PLUNDER_ARTIFACT_VALUES,
        *pyramid_plunder_data.PYRAMID_PLUNDER_BLACK_IBIS,
        *pyramid_plunder_data.PYRAMID_PLUNDER_PHARAOH_SCEPTRES,
        "Sceptre of the gods",
    }
    actions.append(
        {
            "id": pyramid_key,
            "required": set(),
            "alternatives": (),
            "outputs": pyramid_outputs,
        }
    )
    for item in pyramid_outputs:
        producers[item].add(pyramid_key)

    for item_name, spec in constants.CONSUMABLE_DATA.items():
        if not isinstance(spec, Mapping):
            continue
        leaves = _names(spec.get("leaves"))
        if not leaves:
            continue
        key = f"Item action:consume:{item_name}"
        actions.append({"id": key, "required": {item_name}, "alternatives": (), "outputs": leaves})
        consumers[item_name].add(key)
        for item in leaves:
            producers[item].add(key)

    for item_name, spec in pack_data.ITEM_PACK_DATA.items():
        content_item = str(spec["content_item"])
        key = f"Item action:open:{item_name}"
        actions.append({"id": key, "required": {item_name}, "alternatives": (), "outputs": {content_item}})
        consumers[item_name].add(key)
        producers[content_item].add(key)

    for item_name, rewards in IMPLING_JAR_DATA.items():
        outputs = {
            reward.item
            for reward in rewards
            if reward.item and int(reward.weight) > 0
        }
        if not outputs:
            continue
        key = f"Item action:loot:{item_name}"
        actions.append({"id": key, "required": {item_name}, "alternatives": (), "outputs": outputs})
        consumers[item_name].add(key)
        for output in outputs:
            producers[output].add(key)

    bob = shop_data.SHOP_SERVICES.get("bob_barter_decant_four", {})
    if bob.get("visibility") == "visible" and bob.get("action_type") == "decant_potions_to_dose":
        for base in shop_logic.DECANTABLE_FOUR_DOSE_POTION_BASES:
            # Reachability is quantity-free: a repeatable three-dose recipe can
            # supply enough copies for Bob to produce every lower/four-dose
            # remainder state while preserving the exact runtime dose math.
            required = {f"{base} (3)"}
            outputs = {f"{base} ({dose})" for dose in (1, 2, 4)} | {"Vial"}
            key = f"Shop service:bob_barter_decant_four:{base}"
            actions.append({"id": key, "required": required, "alternatives": (), "outputs": outputs})
            for item in required:
                consumers[item].add(key)
            for item in outputs:
                producers[item].add(key)

    teplin_fill = shop_data.SHOP_SERVICES.get(
        "teplin_fill_potion_flasks", {}
    )
    teplin_decant = shop_data.SHOP_SERVICES.get(
        "teplin_decant_flasks_to_vials", {}
    )
    if (
        teplin_fill.get("visibility") == "visible"
        and teplin_fill.get("action_type") == "fill_potion_flasks"
        and teplin_decant.get("visibility") == "visible"
        and teplin_decant.get("action_type") == "decant_flasks_to_vials"
    ):
        for base in shop_logic.DECANTABLE_FLASK_POTION_BASES:
            fill_required = {f"{base} (3)", "Potion flask"}
            fill_output = {shop_logic.potion_flask_name(base, 6)}
            fill_key = f"Shop service:teplin_fill_potion_flasks:{base}"
            actions.append(
                {
                    "id": fill_key,
                    "required": fill_required,
                    "alternatives": (),
                    "outputs": fill_output,
                }
            )
            for item in fill_required:
                consumers[item].add(fill_key)
            for item in fill_output:
                producers[item].add(fill_key)

            decant_required = {shop_logic.potion_flask_name(base, 3)}
            decant_outputs = {
                f"{base} ({dose})"
                for dose in (1, 2, 4)
            }
            decant_key = (
                f"Shop service:teplin_decant_flasks_to_vials:{base}"
            )
            actions.append(
                {
                    "id": decant_key,
                    "required": decant_required,
                    "alternatives": (),
                    "outputs": decant_outputs,
                }
            )
            for item in decant_required:
                consumers[item].add(decant_key)
            for item in decant_outputs:
                producers[item].add(decant_key)

    for service_id, service in shop_data.SHOP_SERVICES.items():
        if (
            service.get("visibility") != "visible"
            or service.get("action_type") != "item_conversion"
        ):
            continue
        required = _names(service.get("inputs"))
        if int(service.get("price", 0) or 0) > 0:
            required.add(str(service.get("currency_item_name", "Coins")))
        outputs = _names(service.get("outputs"))
        if not outputs:
            continue
        key = f"Shop service:{service_id}"
        actions.append(
            {
                "id": key,
                "required": required,
                "alternatives": (),
                "outputs": outputs,
            }
        )
        for item in required:
            consumers[item].add(key)
        for item in outputs:
            producers[item].add(key)

    seen_charge_families: set[tuple[tuple[tuple[str, int], ...], str, str]] = set()
    for enemy_id, enemy in combat_data.COMBAT_ENEMY_DATA.items():
        finisher = enemy.get("finisher", {})
        if not isinstance(finisher, Mapping):
            continue
        charge_items = tuple(
            (str(row[0]), int(row[1]))
            for row in finisher.get("charge_items", ()) or ()
            if isinstance(row, (tuple, list))
            and len(row) >= 2
            and isinstance(row[0], str)
        )
        empty_item = str(finisher.get("empty_item", "") or "")
        reload_item = str(finisher.get("reload_item", "") or "")
        family = (charge_items, empty_item, reload_item)
        if not charge_items or family in seen_charge_families:
            continue
        seen_charge_families.add(family)
        ordered_states = [item for item, _charges in charge_items]
        if empty_item:
            ordered_states.append(empty_item)
        for current, remainder in zip(ordered_states, ordered_states[1:]):
            key = f"Combat finisher:{enemy_id}:{current}"
            actions.append(
                {
                    "id": key,
                    "required": {current},
                    "alternatives": (),
                    "outputs": {remainder},
                }
            )
            consumers[current].add(key)
            producers[remainder].add(key)
        if empty_item and reload_item:
            key = f"Combat refill:{enemy_id}"
            full_item = charge_items[0][0]
            actions.append(
                {
                    "id": key,
                    "required": {empty_item, reload_item},
                    "alternatives": (),
                    "outputs": {full_item},
                }
            )
            consumers[empty_item].add(key)
            consumers[reload_item].add(key)
            producers[full_item].add(key)

    seed_sources: dict[str, set[str]] = defaultdict(set)
    for shop_id, shop in shop_data.SHOP_DATA.items():
        if shop.get("visibility") != "visible" or not shop.get("currency_implemented"):
            continue
        for row in shop.get("stock", ()) or ():
            if row.get("disposition") == "live" and int(row.get("default_quantity", 0) or 0) > 0:
                name = row.get("item_name")
                if isinstance(name, str) and name:
                    seed_sources[name].add(f"shop:{shop_id}")

    for enemy_id, enemy in combat_data.COMBAT_ENEMY_DATA.items():
        for item in _drop_names(enemy.get("drops", {})):
            seed_sources[item].add(f"combat:{enemy_id}")

    for row in constants.BIRD_NEST_DROP_TABLE:
        for item in _names(row.get("item")):
            seed_sources[item].add("woodcutting:bird_nest_roll")

    for quest_id, quest in constants.QUEST_DATA.items():
        for item in _names(quest.get("rewards")) & registered_items:
            seed_sources[item].add(f"quest:{quest_id}")
        for item in _names(quest.get("start_inventory")) & registered_items:
            seed_sources[item].add(f"quest-start:{quest_id}")
    quest_stage_sources, blocked_quest_stage_products = _quest_stage_sources(
        constants.QUEST_DATA,
        registered_items,
        combat_encounter_satisfiable=quest_combat_source_satisfiable,
    )
    for item, sources in quest_stage_sources.items():
        seed_sources[item].update(sources)

    for table in woodcutting_data.BIRD_NEST_OPEN_TABLES:
        table_spec = vars(table)
        input_item = table_spec["input_item"]
        outputs = _names(table_spec.get("guaranteed_item"))
        outputs |= {
            roll.item
            for roll in table_spec.get("rolls", ())
            if isinstance(getattr(roll, "item", None), str)
        }
        key = f"Item action:open:{input_item}"
        actions.append({"id": key, "required": {input_item}, "alternatives": (), "outputs": outputs})
        consumers[input_item].add(key)
        for item in outputs:
            producers[item].add(key)

    reachable, route, unresolved = _close_actions(actions, seed_sources)

    consumed = set(consumers)
    orphan_inputs = sorted(consumed - reachable)
    root_orphans = [item for item in orphan_inputs if not producers.get(item)]
    cascade_orphans = [item for item in orphan_inputs if producers.get(item)]
    unresolved_actions = []
    for action in unresolved:
        missing = sorted(action["required"] - reachable)
        missing_alternatives = [sorted(group) for group in action["alternatives"] if not group & reachable]
        unresolved_actions.append(
            {
                "id": action["id"],
                "missing": missing,
                "missing_alternatives": missing_alternatives,
                "outputs": sorted(action["outputs"]),
            }
        )
    root_orphan_leverage = _rank_root_orphans(
        root_orphans,
        actions,
        seed_sources,
        reachable,
        len(unresolved),
    )

    return {
        "schema_version": 1,
        "action_count": len(actions),
        "seed_item_count": len(seed_sources),
        "reachable_item_count": len(reachable),
        "consumed_item_count": len(consumed),
        "orphan_input_count": len(orphan_inputs),
        "root_orphan_count": len(root_orphans),
        "cascade_orphan_count": len(cascade_orphans),
        "unresolved_action_count": len(unresolved_actions),
        "orphan_inputs": [
            {
                "item": item,
                "kind": "cascade" if producers.get(item) else "root",
                "consumers": sorted(consumers[item]),
                "known_producers": sorted(producers.get(item, ())),
            }
            for item in orphan_inputs
        ],
        "root_orphan_leverage": root_orphan_leverage,
        "blocked_quest_stage_products": blocked_quest_stage_products,
        "unresolved_actions": sorted(unresolved_actions, key=lambda row: row["id"]),
        "routes": {item: route[item] for item in sorted(route)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit the full machine-readable report.")
    parser.add_argument(
        "--rank-roots",
        type=int,
        metavar="N",
        help="Print the N root acquisitions with the largest transitive item gain.",
    )
    args = parser.parse_args()
    report = build_reachability_report()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.rank_roots is not None:
        limit = max(args.rank_roots, 0)
        print(
            f"{report['action_count']} actions; {report['reachable_item_count']} reachable items; "
            f"{report['orphan_input_count']} orphan inputs; {report['unresolved_action_count']} blocked actions"
        )
        for row in report["root_orphan_leverage"][:limit]:
            print(
                f"- {row['item']}: +{row['newly_reachable_item_count']} items; "
                f"+{row['newly_unblocked_action_count']} actions"
            )
    else:
        print(
            f"{report['action_count']} actions; {report['reachable_item_count']} reachable items; "
            f"{report['orphan_input_count']} orphan inputs; {report['unresolved_action_count']} blocked actions"
        )
        for row in report["orphan_inputs"]:
            print(f"- {row['item']}: {', '.join(row['consumers'][:4])}")
    return 1 if report["orphan_input_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
