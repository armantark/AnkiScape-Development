"""Carried-overlay bank travel and action execution."""

from __future__ import annotations

import copy
import dataclasses

from typing import Any

from ..core.constants import FLETCHING_DATA, RUNECRAFTING_DATA, TREE_DATA
from ..data.agility_data import AGILITY_TARGETS_BY_ID
from ..data.evil_tree_data import EVIL_TREE_ELIGIBLE_BLESSING_TARGETS
from ..data.potion_data import skilling_potion_items_for_skill
from ..data.urn_data import URN_STATE_ITEM_NAMES
from ..logic import inventory_pure
from ..logic_pure.achievement_diary_events import (
    record_bank_run_diary_event_pure,
    run_bank_run_diary_callbacks_pure,
)
from ..logic.agility_travel import (
    agility_travel_profile_pure,
    apply_run_energy_credit_pure,
    scheduled_travel_reviews_pure,
)
from ..logic.summoning_logic import restore_summoning_points_pure
from ..logic.wicked_hood_logic import (
    bank_run_phase_label_pure,
    consume_wicked_hood_route_teleport_pure,
    runecrafting_route_phases_pure,
    wicked_hood_skip_active_outbound_pure,
)
from .runtime_actions_carried_requirements import (
    _BANK_RUN_TARGET_KEYS,
    _OVERLAY_STACKABLE_NAMES,
    _OVERLAY_TARGET_KEYS,
    _PROCESSING_HANDLER_KEYS,
    _agility_carried_requirement_gaps,
    _agility_casual_layout_for,
    _bank_can_supply,
    _carried_target_view,
    _pack_can_supply,
    _processing_presence_requirements_for,
    _processing_requirements_for,
    _repack_view_for_target,
    _set_carried_target_map,
    _skilling_potion_requirement_for,
    _without_urn_substitutions,
)
from .runtime_actions_context import RuntimeActionContext
from .runtime_actions_shared import _admit_live_cadence


def _try_pack_yak_winter_storage_overlay(
    player_data: dict[str, Any],
    target_id: str,
    view: dict[str, int],
    churn: int,
    capacity: int,
    *,
    advanced: bool,
    force_bank: bool,
) -> tuple[dict[str, int], int, bool]:
    """Use one carried Winter Storage scroll before an otherwise-due trip."""
    state = player_data.get("summoning_state", {}) or {}
    follower = state.get("active_follower", {}) or {}
    if (
        force_bank
        or follower.get("kind") != "familiar"
        or follower.get("entity_id") != "packyak"
        or int(state.get("special_move_points_current", 0) or 0) < 12
    ):
        return view, churn, False
    policy = (state.get("target_policies", {}) or {}).get(target_id, {}) or {}
    priority = policy.get("winter_storage_priority", ()) or ()
    if isinstance(priority, str):
        priority = (priority,)
    threshold = (
        max(
            0,
            min(
                27,
                int(policy.get("winter_storage_threshold_free_slots", 0) or 0),
            ),
        )
        if advanced
        else 0
    )
    if churn < max(1, capacity - threshold):
        return view, churn, False
    scroll_name = "Winter storage scroll"
    if int(view.get(scroll_name, 0) or 0) <= 0:
        return view, churn, False
    selected = next(
        (
            item_name
            for item_name in priority
            if isinstance(item_name, str)
            and item_name != scroll_name
            and int(view.get(item_name, 0) or 0) > 0
            and (
                item_name not in _OVERLAY_STACKABLE_NAMES
                or int(view.get(item_name, 0) or 0) == 1
            )
        ),
        None,
    )
    if selected is None:
        return view, churn, False

    updated_view = dict(view)
    updated_view[selected] = int(updated_view.get(selected, 0) or 0) - 1
    updated_view[scroll_name] = int(updated_view.get(scroll_name, 0) or 0) - 1
    updated_view = {
        item_name: amount
        for item_name, amount in updated_view.items()
        if amount > 0
    }
    inventory = dict(player_data.get("inventory", {}) or {})
    inventory[scroll_name] = max(
        0, int(inventory.get(scroll_name, 0) or 0) - 1
    )
    player_data["inventory"] = inventory
    updated_state = dict(state)
    updated_state["special_move_points_current"] = (
        int(updated_state.get("special_move_points_current", 0) or 0) - 12
    )
    updated_state["event_log"] = (
        list(updated_state.get("event_log", []))
        + [
            {
                "kind": "winter_storage",
                "target_id": target_id,
                "item": selected,
                "xp": 4.8,
            }
        ]
    )[-50:]
    player_data["summoning_state"] = updated_state
    player_data["summoning_exp"] = (
        float(player_data.get("summoning_exp", 0.0) or 0.0) + 4.8
    )
    return updated_view, max(0, churn - 1), True


def run_answer_with_carried_overlay(ctx: RuntimeActionContext, handler_key: str, handler) -> bool:
    """Run one skilling tick through the 28-slot carried overlay.

    Gathering skills fill the pack with their product (Keep) or bypass it
    entirely (Drop); the pack banks when full. Processing skills instead *draw*
    their recipe inputs from the pack: the handler only sees as much of each
    required material as the pack currently holds, so the pack — not the
    infinite bank — is what limits actions-per-trip. This is what gives the
    advanced 4x7 layout real consequence: a well-arranged pack (matching a
    recipe's true ratio) yields more actions before a bank-run than an even
    casual split.

    Before the tick, the gate decides whether this answer is spent banking
    instead of acting: churn reaching capacity (either skill), or — processing
    only — the pack running out of a required input the bank could still
    supply. On a completed bank run the pack is repacked from the bank (casual
    preset / processing split, or the advanced saved layout) rather than simply
    cleared. Handlers without carried teeth run untouched unless the player
    explicitly spends that review on a bank run.
    """
    player_data = ctx.player_data
    target_key = _OVERLAY_TARGET_KEYS.get(handler_key)
    if target_key is None:
        if (
            str(player_data.get("review_bank_run_requested_handler", "") or "")
            == handler_key
        ):
            player_data.pop("review_bank_run_requested_handler", None)
            player_data.update(restore_summoning_points_pure(player_data))
            ctx.show_activity_gain("Bank run — arrived at the bank")
            ctx.save_player_data()
            return True
        bank_target_key = _BANK_RUN_TARGET_KEYS.get(handler_key)
        target_id = (
            str(player_data.get(bank_target_key, ""))
            if bank_target_key
            else handler_key
        )
        if player_data.get("skilling_bank_run_requested") == target_id:
            player_data.pop("skilling_bank_run_requested", None)
            player_data.update(restore_summoning_points_pure(player_data))
            ctx.show_activity_gain("Bank run — arrived and ready")
            ctx.save_player_data()
        return handler(ctx)

    target_id = str(player_data.get(target_key, ""))
    evil_tree_state = player_data.get("evil_tree")
    if not isinstance(evil_tree_state, dict):
        evil_tree_state = {}
    evil_tree_overflow = bool(
        handler_key == "woodcutting"
        and target_id in EVIL_TREE_ELIGIBLE_BLESSING_TARGETS
        and int(
            evil_tree_state.get("blessing_reviews_remaining", 0) or 0
        )
        > 0
    )
    target_spec = TREE_DATA.get(target_id, {}) if handler_key == "woodcutting" else {}
    is_processing = (
        handler_key in _PROCESSING_HANDLER_KEYS
        or target_spec.get("action_type") == "processing"
    )
    is_agility = handler_key == "agility"
    # Keep/Drop is a gathering-only choice; processing always draws from (and
    # refills) its pack — there is no "drop the product" for a recipe's inputs.
    keep = True if is_processing else inventory_pure.carried_keep_for(player_data, target_id)
    view = dict((player_data.get("carried_inventory") or {}).get(target_id, {}))
    churn = (player_data.get("carried_churn") or {}).get(target_id, 0)
    bank_run = player_data.get("skilling_bank_run", {})
    manual_bank_run = (
        str(player_data.get("review_bank_run_requested_target", "") or "")
        == target_id
    )
    requested_target = player_data.get("skilling_bank_run_requested")
    skilling_bank_run_requested = requested_target == target_id
    bank_run_requested = manual_bank_run or skilling_bank_run_requested
    advanced = inventory_pure.carried_advanced_for(player_data, target_id)
    layout = (player_data.get("carried_layout") or {}).get(target_id, {})
    bank = player_data.get("inventory", {}) or {}
    casual_layout = _agility_casual_layout_for(player_data, target_id) if is_agility else {}
    # A carried bag raises the bank-run threshold for its material (fewer trips).
    owned_bags = {
        bag for bag in inventory_pure.BAG_DEFINITIONS
        if int(bank.get(bag, 0) or 0) > 0
    }
    capacity = inventory_pure.effective_carried_capacity(view, owned_bags)

    carried_materials = view if view else layout if advanced else {}
    requirements = (
        _processing_requirements_for(handler_key, player_data, carried_materials)
        if is_processing else {}
    )
    presence_requirements = (
        _processing_presence_requirements_for(handler_key, player_data)
        if is_processing else {}
    )
    consumable_requirements = (
        _skilling_potion_requirement_for(
            handler_key,
            player_data,
            target_id,
            view if view else layout if advanced else {},
            advanced=advanced,
        )
        if is_processing
        else {}
    )

    # First-ever engagement with a processing target seeds the pack for free —
    # you already "have inventory" the moment you arrive, same as gathering
    # starting empty; the review cost is only for *refilling after depletion*,
    # never for the initial load (owner: no free banking, but this isn't a trip).
    primed = target_id in (player_data.get("carried_primed_targets") or {})
    if (is_processing and requirements or is_agility) and not primed:
        view = _repack_view_for_target(
            is_processing,
            advanced,
            layout,
            bank,
            requirements,
            capacity,
            casual_layout,
            consumable_requirements,
        )
        _set_carried_target_map(player_data, "carried_primed_targets", target_id, True)
        _set_carried_target_map(player_data, "carried_inventory", target_id, view)
    elif handler_key == "hunter" and advanced and layout and not view:
        # Hunter is gathering, but target-carried passives still need the saved
        # Custom pack on the first trip rather than waiting for a bank-run cycle.
        view = _repack_view_for_target(False, True, layout, bank, {}, capacity)
        _set_carried_target_map(player_data, "carried_inventory", target_id, view)

    if is_agility and advanced:
        missing = _agility_carried_requirement_gaps(player_data, target_id, view)
        if missing:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Agility pack incomplete",
                f"Custom mode must carry or equip {', '.join(missing)} for "
                f"{AGILITY_TARGETS_BY_ID[target_id].display_name}.",
            )
            return False

    # Presence-only gates stay out of per-action packing: in default mode they
    # remain available from the bank. An advanced layout explicitly carries
    # them, however, so an emptied presence slot must trigger the normal refill
    # when the bank can restore the saved layout.
    refill_requirements = dict(requirements)
    for item_name, need in consumable_requirements.items():
        refill_requirements[item_name] = max(
            refill_requirements.get(item_name, 0), need
        )
    if advanced:
        for item_name, need in presence_requirements.items():
            refill_requirements[item_name] = max(refill_requirements.get(item_name, 0), need)
    force = bank_run_requested or bool(
        is_processing and refill_requirements
        and not _pack_can_supply(view, refill_requirements)
        and _bank_can_supply(bank, refill_requirements)
    )
    desired_agility_view = (
        _repack_view_for_target(
            False,
            advanced,
            layout,
            bank,
            {},
            capacity,
            casual_layout,
        )
        if is_agility
        else {}
    )
    if desired_agility_view:
        force = force or any(
            int(view.get(item_name, 0) or 0) <= 0 and int(bank.get(item_name, 0) or 0) > 0
            for item_name in desired_agility_view
        )

    target_altar = (
        str((RUNECRAFTING_DATA.get(target_id) or {}).get("altar_id", ""))
        if handler_key == "runecrafting"
        else ""
    )
    active_target_matches = (
        isinstance(bank_run, dict)
        and bank_run.get("target_id") in (None, target_id)
        and int(bank_run.get("reviews_remaining", 0) or 0) > 0
    )
    if target_altar and active_target_matches:
        teleported_data, pending_teleport_used = consume_wicked_hood_route_teleport_pure(
            player_data, target_altar
        )
        if pending_teleport_used:
            player_data.clear()
            player_data.update(teleported_data)
            bank_run, _outbound_removed = wicked_hood_skip_active_outbound_pure(
                bank_run
            )
            player_data["skilling_bank_run"] = bank_run
            if not bank_run:
                view = _repack_view_for_target(
                    is_processing,
                    advanced,
                    layout,
                    bank,
                    requirements,
                    capacity,
                    casual_layout,
                    consumable_requirements,
                )
                churn = 0
                force = False
                _set_carried_target_map(
                    player_data, "carried_inventory", target_id, view
                )
                _set_carried_target_map(
                    player_data, "carried_churn", target_id, churn
                )

    active_run = isinstance(bank_run, dict) and int(bank_run.get("reviews_remaining", 0) or 0) > 0
    action_ctx = ctx
    cadence_admitted = False
    cadence_profiles_present = "cadence_profiles" in player_data
    cadence_profiles_before = copy.deepcopy(player_data.get("cadence_profiles"))
    cadence_profiles_after_admission = None

    def restore_cadence_profiles_after_rejection() -> None:
        if not cadence_admitted:
            return
        if player_data.get("cadence_profiles") != cadence_profiles_after_admission:
            # A handler may own a second scheduler under the same route key
            # (Thieving stalls and wall safes). Once that scheduler advances,
            # the review was a real action attempt rather than an eligibility
            # rejection, so its cadence must survive an unsuccessful outcome.
            return
        if cadence_profiles_present:
            player_data["cadence_profiles"] = copy.deepcopy(
                cadence_profiles_before
            )
        else:
            player_data.pop("cadence_profiles", None)

    if keep and not active_run and handler_key not in {"magic", "prayer"}:
        action_ctx, cadence_admitted = _admit_live_cadence(
            ctx, handler_key, target_id
        )
        if not cadence_admitted:
            return True
        cadence_profiles_after_admission = copy.deepcopy(
            player_data.get("cadence_profiles")
        )
    winter_storage_before = None
    if keep and not active_run and not bank_run_requested:
        winter_storage_before = copy.deepcopy(player_data)
        view, churn, winter_storage_used = _try_pack_yak_winter_storage_overlay(
            player_data,
            target_id,
            view,
            int(churn or 0),
            capacity,
            advanced=advanced,
            force_bank=force,
        )
        if winter_storage_used:
            bank = player_data.get("inventory", {}) or {}
            _set_carried_target_map(
                player_data, "carried_inventory", target_id, view
            )
            _set_carried_target_map(
                player_data, "carried_churn", target_id, churn
            )
        else:
            winter_storage_before = None
    trip_due = bool(
        bank_run_requested
        or (
            keep
            and (
                active_run
                or (churn >= capacity and not evil_tree_overflow)
                or force
            )
        )
    )
    travel_profile = None
    run_energy_credit_used = 0
    reviews_cost = inventory_pure.SKILLING_BANK_RUN_REVIEWS
    route_phases = ()
    outbound_teleport_used = False
    if active_run:
        reviews_cost = max(1, int(bank_run.get("reviews_total", bank_run.get("reviews_remaining", 1)) or 1))
    elif trip_due:
        travel_profile = agility_travel_profile_pure(
            handler_key,
            target_id,
            int(player_data.get("agility_level", 1) or 1),
            view,
            player_data.get("equipment", {}),
        )
        travel_profile, run_energy_credit_used = apply_run_energy_credit_pure(
            travel_profile,
            player_data.get("agility_run_energy_credit_pct", 0),
        )
        if run_energy_credit_used:
            player_data["agility_run_energy_credit_pct"] = 0
        # The only new RNG draw happens at the moment a trip is actually due.
        scheduled_reviews = (
            scheduled_travel_reviews_pure(travel_profile, ctx.random_random())
            if travel_profile.adjusted_reviews > 0
            else 0
        )
        if target_altar:
            teleported_data, outbound_teleport_used = consume_wicked_hood_route_teleport_pure(
                player_data, target_altar
            )
            if outbound_teleport_used:
                player_data.clear()
                player_data.update(teleported_data)
            route_phases = runecrafting_route_phases_pure(
                scheduled_reviews, skip_outbound=outbound_teleport_used
            )
            reviews_cost = sum(int(phase["reviews"]) for phase in route_phases)
        else:
            reviews_cost = scheduled_reviews
        player_data["agility_last_travel"] = {
            "handler_key": handler_key,
            "target_id": target_id,
            "base_reviews": travel_profile.base_reviews,
            "adjusted_reviews": travel_profile.adjusted_reviews,
            "scheduled_reviews": scheduled_reviews,
            "charged_reviews": reviews_cost,
            "level_gain": travel_profile.level_gain,
            "weight_gain": travel_profile.weight_gain,
            "carried_weight_kg": travel_profile.carried_weight_kg,
            "effective_weight_kg": travel_profile.effective_weight_kg,
            "route_label": travel_profile.route_label,
            "source_status": travel_profile.source_status,
            "run_energy_credit_used_pct": run_energy_credit_used,
            "outbound_teleport_used": outbound_teleport_used,
        }

    if trip_due and reviews_cost <= 0:
        new_state, new_view, new_churn = {}, {}, 0
        event = {"active": True, "started": True, "completed": True, "reviews_remaining": 0, "waived": True}
        act = True
        new_view = _repack_view_for_target(
            is_processing,
            advanced,
            layout,
            bank,
            requirements,
            capacity,
            casual_layout,
            consumable_requirements,
        )
    else:
        gate_churn = min(int(churn or 0), capacity - 1) if evil_tree_overflow and not active_run else churn
        new_state, new_view, new_churn, event, act = inventory_pure.carried_bank_run_gate_pure(
            view,
            gate_churn,
            keep or bank_run_requested,
            _OVERLAY_STACKABLE_NAMES,
            target_id,
            bank_run,
            max(1, reviews_cost),
            capacity,
            force or bank_run_requested,
        )
        if evil_tree_overflow and act:
            new_churn = int(churn or 0)
        if event.get("started") and new_state:
            new_state["reviews_total"] = max(1, reviews_cost)
            new_state["route_label"] = travel_profile.route_label if travel_profile else "Running to the bank"
            if route_phases:
                new_state["route_phases"] = list(route_phases)
            if outbound_teleport_used:
                new_state["outbound_teleport_used"] = True

    if manual_bank_run and (event.get("started") or event.get("completed")):
        player_data.pop("review_bank_run_requested_target", None)
    if skilling_bank_run_requested and event.get("active"):
        player_data.pop("skilling_bank_run_requested", None)

    if event.get("completed"):
        player_data.update(restore_summoning_points_pure(player_data))
        record_bank_run_diary_event_pure(player_data, True, view)

    if not act:
        restore_cadence_profiles_after_rejection()
        if event.get("completed"):
            new_view = _repack_view_for_target(
                is_processing,
                advanced,
                layout,
                bank,
                requirements,
                capacity,
                casual_layout,
                consumable_requirements,
            )
        player_data["skilling_bank_run"] = new_state
        _set_carried_target_map(player_data, "carried_inventory", target_id, new_view)
        _set_carried_target_map(player_data, "carried_churn", target_id, new_churn)
        total = int((new_state or bank_run or {}).get("reviews_total", reviews_cost) or reviews_cost)
        remaining = int(event.get("reviews_remaining", 0) or 0)
        route_label = bank_run_phase_label_pure(new_state or bank_run)
        progress = max(1, total - remaining)
        ctx.show_activity_gain(
            f"Bank run — {route_label} · {min(progress, total)}/{total} travel reviews"
            if not event.get("completed")
            else f"Bank run — {route_label} · arrived and restocked"
        )
        run_bank_run_diary_callbacks_pure(
            bool(event.get("completed")),
            player_data,
            ctx.refresh_carried_inventory,
            ctx.check_achievements,
        )
        ctx.save_player_data()
        return True

    # Handlers that substitute carried items (urn runed -> active -> full) must
    # see the actual trip view, including a just-seeded first trip.
    _set_carried_target_map(player_data, "carried_inventory", target_id, new_view)
    if not cadence_admitted and handler_key not in {"magic", "prayer"}:
        action_ctx, cadence_admitted = _admit_live_cadence(
            ctx, handler_key, target_id
        )
        if not cadence_admitted:
            return True
        cadence_profiles_after_admission = copy.deepcopy(
            player_data.get("cadence_profiles")
        )

    if is_processing and requirements:
        # Scope the handler's input access to what the pack holds, run it, then
        # reconcile: the real bank only loses what was actually consumed, and the
        # pack is decremented by the same amount. Every other item (outputs,
        # byproducts) passes through untouched, since it was never capped.
        scoped_inventory = dict(bank)
        for item_name, need in requirements.items():
            scoped_inventory[item_name] = min(int(bank.get(item_name, 0) or 0), int(new_view.get(item_name, 0) or 0))
        carried_presence_requirements = presence_requirements if advanced else {}
        for item_name, need in carried_presence_requirements.items():
            scoped_inventory[item_name] = min(int(bank.get(item_name, 0) or 0), int(new_view.get(item_name, 0) or 0))
        scoped_potion_items = set()
        if handler_key in {"crafting", "fletching"}:
            for item_name in skilling_potion_items_for_skill(handler_key):
                scoped_potion_items.add(item_name)
                scoped_inventory.pop(item_name, None)
        for item_name, need in consumable_requirements.items():
            scoped_inventory[item_name] = min(
                int(bank.get(item_name, 0) or 0),
                int(new_view.get(item_name, 0) or 0),
            )
        scoped_alternatives = set()
        if handler_key == "fletching":
            spec = FLETCHING_DATA.get(target_id, {})
            for alternatives in spec.get("material_options", {}).values():
                if not isinstance(alternatives, (list, tuple)):
                    continue
                for option in alternatives:
                    if isinstance(option, str):
                        scoped_alternatives.add(option)
                        if option not in requirements:
                            scoped_inventory.pop(option, None)

        # While the inventory is scoped it does NOT reflect the real bank, so the
        # handler must not persist it or evaluate anything against it. Suppress the
        # handler's save, achievement check, and skill-availability refreshes for the
        # duration and fire them once afterwards against the reconciled bank.
        # Without this a save inside the handler writes the capped bank to disk,
        # achievements gated on a bank quantity see only what fits in the pack, and
        # the skill-availability UI is computed from the pack rather than the bank.
        # `deactivate_current_skill` is deliberately left live: it must still fire
        # when materials genuinely run out, and the bank-run gate above already
        # prevents the handler from ever seeing an under-supplied pack.
        deferred_achievement_check = []
        deferred_availability_refresh = []
        scoped_ctx = dataclasses.replace(
            action_ctx,
            save_player_data=lambda: None,
            check_achievements=lambda _data: deferred_achievement_check.append(True),
            refresh_skill_availability=lambda: deferred_availability_refresh.append(True),
        )
        player_data["inventory"] = scoped_inventory
        result = handler(scoped_ctx)
        if result is False and winter_storage_before is not None:
            player_data.clear()
            player_data.update(winter_storage_before)
            restore_cadence_profiles_after_rejection()
            ctx.save_player_data()
            return False
        after_scoped = player_data.get("inventory", {}) or {}
        new_view = _carried_target_view(player_data, target_id)
        reconciled = dict(after_scoped)
        for item_name in scoped_potion_items - consumable_requirements.keys():
            if item_name in bank:
                reconciled[item_name] = bank[item_name]
        for option in scoped_alternatives - requirements.keys():
            if option in bank:
                reconciled[option] = bank[option]
            else:
                reconciled.pop(option, None)
        for item_name, _need in requirements.items():
            true_before = int(bank.get(item_name, 0) or 0)
            capped_before = int(scoped_inventory.get(item_name, 0) or 0)
            after_amount = int(after_scoped.get(item_name, 0) or 0)
            consumed = max(0, capped_before - after_amount)
            reconciled[item_name] = max(0, true_before - consumed)
            if consumed > 0:
                new_view[item_name] = max(0, int(new_view.get(item_name, 0) or 0) - consumed)
        for item_name, _need in carried_presence_requirements.items():
            true_before = int(bank.get(item_name, 0) or 0)
            capped_before = int(scoped_inventory.get(item_name, 0) or 0)
            after_amount = int(after_scoped.get(item_name, 0) or 0)
            consumed = max(0, capped_before - after_amount)
            reconciled[item_name] = max(0, true_before - consumed)
            if consumed > 0:
                new_view[item_name] = max(0, int(new_view.get(item_name, 0) or 0) - consumed)
        for item_name, _need in consumable_requirements.items():
            true_before = int(bank.get(item_name, 0) or 0)
            capped_before = int(scoped_inventory.get(item_name, 0) or 0)
            after_amount = int(after_scoped.get(item_name, 0) or 0)
            consumed = max(0, capped_before - after_amount)
            reconciled[item_name] = max(0, true_before - consumed)
            if consumed > 0:
                new_view[item_name] = max(
                    0, int(new_view.get(item_name, 0) or 0) - consumed
                )
        new_view = {name: count for name, count in new_view.items() if count > 0}
        player_data["inventory"] = reconciled
        if result is not False:
            player_data["skilling_bank_run"] = new_state
            churn_delta = inventory_pure.carried_action_churn_pure(
                _without_urn_substitutions(bank),
                _without_urn_substitutions(reconciled),
                _OVERLAY_STACKABLE_NAMES,
            )
            _set_carried_target_map(player_data, "carried_inventory", target_id, new_view)
            _set_carried_target_map(player_data, "carried_churn", target_id, new_churn + churn_delta)
        # Always run against the true bank, even on a failed tick, so a suppressed
        # save can never leave the capped inventory as the last thing written.
        if deferred_achievement_check:
            ctx.check_achievements(player_data)
        if deferred_availability_refresh:
            ctx.refresh_skill_availability()
        if result is False:
            restore_cadence_profiles_after_rejection()
        ctx.save_player_data()
        return result

    inv_before = dict(bank)
    result = handler(action_ctx)
    if result is False and winter_storage_before is not None:
        player_data.clear()
        player_data.update(winter_storage_before)
        restore_cadence_profiles_after_rejection()
        ctx.save_player_data()
        return False
    if result is not False:
        player_data["skilling_bank_run"] = new_state
        inv_after = player_data.get("inventory", {}) or {}
        post_handler_view = _carried_target_view(player_data, target_id)
        gains = {
            item_name: amount
            for item_name, amount in inventory_pure.inventory_delta_gains(inv_before, inv_after).items()
            if item_name not in URN_STATE_ITEM_NAMES
        }
        if keep:
            # Keep accrues churn and folds ordinary products into the post-handler
            # pack. Urn substitutions already happened in that pack and are not
            # products, Drop targets, or churn.
            churn_delta = inventory_pure.carried_action_churn_pure(
                _without_urn_substitutions(inv_before),
                _without_urn_substitutions(inv_after),
                _OVERLAY_STACKABLE_NAMES,
            )
            overflow_items: dict[str, int] = {}
            if evil_tree_overflow:
                post_handler_view, overflow_items = (
                    inventory_pure.carried_fold_gains_with_overflow_pure(
                        post_handler_view,
                        gains,
                        _OVERLAY_STACKABLE_NAMES,
                        capacity,
                    )
                )
            else:
                post_handler_view = inventory_pure.carried_fold_gains_pure(
                    post_handler_view,
                    gains,
                    _OVERLAY_STACKABLE_NAMES,
                )
            _set_carried_target_map(player_data, "carried_inventory", target_id, post_handler_view)
            _set_carried_target_map(
                player_data,
                "carried_churn",
                target_id,
                min(capacity, new_churn + churn_delta)
                if evil_tree_overflow
                else new_churn + churn_delta,
            )
            if overflow_items:
                ctx.show_activity_gain(
                    "Evil Tree blessing: full-pack gains sent directly to the Bank"
                )
        elif gains:
            # Drop is power-gathering: ordinary gains are destroyed, while an urn's
            # carried runed/active/full substitution remains a physical carried item.
            drained = dict(inv_after)
            for item_name, gained in gains.items():
                drained[item_name] = max(0, int(drained.get(item_name, 0) or 0) - int(gained))
            player_data["inventory"] = {name: count for name, count in drained.items() if count > 0}
        ctx.save_player_data()
    else:
        restore_cadence_profiles_after_rejection()
    return result
