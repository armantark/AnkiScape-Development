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
    AgilityTravelProfile,
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
    _processing_consumable_requirements_for,
    _processing_presence_requirements_for,
    _processing_requirements_for,
    _repack_view_for_target,
    _set_carried_target_map,
    _without_urn_substitutions,
)
from .runtime_actions_context import RuntimeActionContext
from .runtime_actions_shared import _admit_live_cadence


_WINTER_STORAGE_SCROLL = "Winter storage scroll"


def _winter_storage_candidate(view: dict[str, int], item_name: Any) -> bool:
    """Whether a Pack yak can bank this carried item: stackables only as a lone one."""
    if not isinstance(item_name, str) or item_name == _WINTER_STORAGE_SCROLL:
        return False
    count = int(view.get(item_name, 0) or 0)
    return count > 0 and (item_name not in _OVERLAY_STACKABLE_NAMES or count == 1)


def _winter_storage_selection(
    state: dict[str, Any],
    target_id: str,
    view: dict[str, int],
    churn: int,
    capacity: int,
    *,
    advanced: bool,
) -> str | None:
    """The highest-priority carried item to bank once the pack is full enough."""
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
        return None
    if int(view.get(_WINTER_STORAGE_SCROLL, 0) or 0) <= 0:
        return None
    return next(
        (item_name for item_name in priority if _winter_storage_candidate(view, item_name)),
        None,
    )


def _spend_winter_storage(
    player_data: dict[str, Any],
    state: dict[str, Any],
    target_id: str,
    view: dict[str, int],
    selected: str,
) -> dict[str, int]:
    """Bank ``selected`` with one scroll and 12 special points; return the pack."""
    updated_view = dict(view)
    updated_view[selected] = int(updated_view.get(selected, 0) or 0) - 1
    updated_view[_WINTER_STORAGE_SCROLL] = (
        int(updated_view.get(_WINTER_STORAGE_SCROLL, 0) or 0) - 1
    )
    updated_view = {
        item_name: amount
        for item_name, amount in updated_view.items()
        if amount > 0
    }
    inventory = dict(player_data.get("inventory", {}) or {})
    inventory[_WINTER_STORAGE_SCROLL] = max(
        0, int(inventory.get(_WINTER_STORAGE_SCROLL, 0) or 0) - 1
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
    return updated_view


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
    selected = _winter_storage_selection(
        state, target_id, view, churn, capacity, advanced=advanced
    )
    if selected is None:
        return view, churn, False
    updated_view = _spend_winter_storage(player_data, state, target_id, view, selected)
    return updated_view, max(0, churn - 1), True


def _fletching_material_options(target_id: str) -> set[str]:
    options: set[str] = set()
    spec = FLETCHING_DATA.get(target_id, {})
    for alternatives in spec.get("material_options", {}).values():
        if isinstance(alternatives, (list, tuple)):
            options.update(option for option in alternatives if isinstance(option, str))
    return options


def _scope_processing_inventory(
    bank: dict[str, Any],
    pack: dict[str, int],
    handler_key: str,
    target_id: str,
    requirements: dict[str, int],
    carried_presence_requirements: dict[str, int],
    consumable_requirements: dict[str, int],
) -> tuple[dict[str, Any], set[str], set[str]]:
    """The bank as a processing handler sees it, with carried inputs capped at the pack.

    Skilling potions and Fletching material alternatives the pack does not
    carry are hidden, so the handler cannot draw them from the bank; the two
    hidden sets are returned for reconciliation to restore afterwards.
    """
    scoped = dict(bank)
    for item_name in (*requirements, *carried_presence_requirements):
        scoped[item_name] = min(int(bank.get(item_name, 0) or 0), int(pack.get(item_name, 0) or 0))
    potion_items = (
        set(skilling_potion_items_for_skill(handler_key))
        if handler_key in {"crafting", "fletching"}
        else set()
    )
    for item_name in potion_items:
        scoped.pop(item_name, None)
    # A carried potion is scoped after the hiding above, so it stays visible.
    for item_name in consumable_requirements:
        scoped[item_name] = min(int(bank.get(item_name, 0) or 0), int(pack.get(item_name, 0) or 0))
    hidden_alternatives = (
        _fletching_material_options(target_id) - requirements.keys()
        if handler_key == "fletching"
        else set()
    )
    for item_name in hidden_alternatives:
        scoped.pop(item_name, None)
    return scoped, potion_items - consumable_requirements.keys(), hidden_alternatives


def _reconcile_processing_inventory(
    bank: dict[str, Any],
    scoped_inventory: dict[str, Any],
    after_scoped: dict[str, Any],
    carried_view: dict[str, int],
    required_items: tuple[str, ...],
    hidden_potions: set[str],
    hidden_alternatives: set[str],
) -> tuple[dict[str, Any], dict[str, int]]:
    reconciled = dict(after_scoped)
    view = dict(carried_view)
    for item_name in hidden_potions:
        if item_name in bank:
            reconciled[item_name] = bank[item_name]
    for item_name in hidden_alternatives:
        if item_name in bank:
            reconciled[item_name] = bank[item_name]
        else:
            reconciled.pop(item_name, None)
    # Categories may share a key: each occurrence still consumes carried stock.
    for item_name in required_items:
        true_before = int(bank.get(item_name, 0) or 0)
        capped_before = int(scoped_inventory.get(item_name, 0) or 0)
        after_amount = int(after_scoped.get(item_name, 0) or 0)
        consumed = max(0, capped_before - after_amount)
        reconciled[item_name] = max(0, true_before - consumed)
        if consumed > 0:
            view[item_name] = max(0, int(view.get(item_name, 0) or 0) - consumed)
    return reconciled, {name: count for name, count in view.items() if count > 0}


def _fold_keep_gains_and_write_carried(
    player_data, target_id, post_handler_view, gains,
    new_churn, churn_delta, capacity, evil_tree_overflow,
):
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
    return overflow_items


def _processing_refill_due(
    view: dict[str, int],
    bank: dict[str, Any],
    requirements: dict[str, int],
    consumable_requirements: dict[str, int],
    presence_requirements: dict[str, int],
    *,
    advanced: bool,
) -> bool:
    """Whether a short processing pack must bank because the bank can refill it."""
    refill_requirements = dict(requirements)
    for item_name, need in consumable_requirements.items():
        refill_requirements[item_name] = max(
            refill_requirements.get(item_name, 0), need
        )
    # Presence-only gates stay out of per-action packing: in default mode they
    # remain available from the bank. An advanced layout explicitly carries
    # them, however, so an emptied presence slot must trigger the normal refill
    # when the bank can restore the saved layout.
    if advanced:
        for item_name, need in presence_requirements.items():
            refill_requirements[item_name] = max(refill_requirements.get(item_name, 0), need)
    return bool(
        refill_requirements
        and not _pack_can_supply(view, refill_requirements)
        and _bank_can_supply(bank, refill_requirements)
    )


def _initialize_due_bank_trip(
    ctx: RuntimeActionContext,
    handler_key: str,
    target_id: str,
    view: dict[str, int],
    target_altar: str,
) -> tuple[AgilityTravelProfile, int, tuple[dict[str, Any], ...], bool]:
    player_data = ctx.player_data
    route_phases = ()
    outbound_teleport_used = False
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
    return travel_profile, reviews_cost, route_phases, outbound_teleport_used


def _settle_bank_run_requests(
    player_data: dict[str, Any],
    view: dict[str, int],
    event: dict[str, Any],
    *,
    manual_bank_run: bool,
    skilling_bank_run_requested: bool,
) -> None:
    """Spend the requests this trip answers; an arrival restores summoning and records the diary run."""
    if manual_bank_run and (event.get("started") or event.get("completed")):
        player_data.pop("review_bank_run_requested_target", None)
    if skilling_bank_run_requested and event.get("active"):
        player_data.pop("skilling_bank_run_requested", None)
    if event.get("completed"):
        player_data.update(restore_summoning_points_pure(player_data))
        record_bank_run_diary_event_pure(player_data, True, view)


def _spend_review_on_bank_trip(
    ctx: RuntimeActionContext,
    target_id: str,
    bank_run: Any,
    new_state: dict[str, Any],
    new_view: dict[str, int],
    new_churn: int,
    event: dict[str, Any],
    reviews_cost: int,
) -> None:
    """Save a review spent travelling to or from the bank and report the trip's progress."""
    player_data = ctx.player_data
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


def _run_without_carried_overlay(ctx: RuntimeActionContext, handler_key: str, handler) -> bool:
    """Run a handler that carries no pack.

    A bank run requested for the handler spends the review; one requested for
    its target arrives before the handler runs.
    """
    player_data = ctx.player_data
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


@dataclasses.dataclass(frozen=True)
class _TargetPack:
    """One target's carried pack for this review: its kind, room, layouts and recipe."""

    handler_key: str
    target_id: str
    is_processing: bool
    advanced: bool
    layout: dict[str, int]
    bank: dict[str, Any]
    capacity: int
    casual_layout: dict[str, int]
    requirements: dict[str, int]
    presence_requirements: dict[str, int]
    consumable_requirements: dict[str, int]

    def repack(self) -> dict[str, int]:
        """The pack a bank visit restocks from the bank."""
        return _repack_view_for_target(
            self.is_processing,
            self.advanced,
            self.layout,
            self.bank,
            self.requirements,
            self.capacity,
            self.casual_layout,
            self.consumable_requirements,
        )


def _describe_target_pack(
    player_data: dict[str, Any], handler_key: str, target_id: str, view: dict[str, int]
) -> _TargetPack:
    """Describe the pack from its saved ``view``, before this review primes or restocks it."""
    target_spec = TREE_DATA.get(target_id, {}) if handler_key == "woodcutting" else {}
    is_processing = (
        handler_key in _PROCESSING_HANDLER_KEYS
        or target_spec.get("action_type") == "processing"
    )
    advanced = inventory_pure.carried_advanced_for(player_data, target_id)
    layout = (player_data.get("carried_layout") or {}).get(target_id, {})
    bank = player_data.get("inventory", {}) or {}
    # A carried bag raises the bank-run threshold for its material (fewer trips).
    owned_bags = {
        bag for bag in inventory_pure.BAG_DEFINITIONS
        if int(bank.get(bag, 0) or 0) > 0
    }
    carried_materials = view if view else layout if advanced else {}
    return _TargetPack(
        handler_key=handler_key,
        target_id=target_id,
        is_processing=is_processing,
        advanced=advanced,
        layout=layout,
        bank=bank,
        capacity=inventory_pure.effective_carried_capacity(view, owned_bags),
        casual_layout=(
            _agility_casual_layout_for(player_data, target_id) if handler_key == "agility" else {}
        ),
        requirements=(
            _processing_requirements_for(handler_key, player_data, carried_materials)
            if is_processing else {}
        ),
        presence_requirements=(
            _processing_presence_requirements_for(handler_key, player_data)
            if is_processing else {}
        ),
        consumable_requirements=(
            _processing_consumable_requirements_for(
                handler_key, player_data, target_id, carried_materials, advanced=advanced
            )
            if is_processing
            else {}
        ),
    )


def _prime_first_trip(
    player_data: dict[str, Any], pack: _TargetPack, view: dict[str, int]
) -> dict[str, int]:
    """Load the pack for its first trip to this target and return the view to use.

    First-ever engagement with a processing target seeds the pack for free —
    you already "have inventory" the moment you arrive, same as gathering
    starting empty; the review cost is only for *refilling after depletion*,
    never for the initial load (owner: no free banking, but this isn't a trip).
    """
    target_id = pack.target_id
    primed = target_id in (player_data.get("carried_primed_targets") or {})
    if (pack.is_processing and pack.requirements or pack.handler_key == "agility") and not primed:
        view = pack.repack()
        _set_carried_target_map(player_data, "carried_primed_targets", target_id, True)
        _set_carried_target_map(player_data, "carried_inventory", target_id, view)
    elif pack.handler_key == "hunter" and pack.advanced and pack.layout and not view:
        # Hunter is gathering, but target-carried passives still need the saved
        # Custom pack on the first trip rather than waiting for a bank-run cycle.
        view = pack.repack()
        _set_carried_target_map(player_data, "carried_inventory", target_id, view)
    return view


def _teleport_past_outbound_leg(
    player_data: dict[str, Any], pack: _TargetPack, bank_run: Any, target_altar: str
) -> tuple[Any, dict[str, int] | None]:
    """Spend a pending Wicked hood altar teleport on this target's active trip.

    The teleport removes the trip's outbound leg. Returns the trip that remains
    and, when nothing remains, the pack restocked from the bank.
    """
    active_target_matches = (
        isinstance(bank_run, dict)
        and bank_run.get("target_id") in (None, pack.target_id)
        and int(bank_run.get("reviews_remaining", 0) or 0) > 0
    )
    if not active_target_matches:
        return bank_run, None
    teleported_data, pending_teleport_used = consume_wicked_hood_route_teleport_pure(
        player_data, target_altar
    )
    if not pending_teleport_used:
        return bank_run, None
    player_data.clear()
    player_data.update(teleported_data)
    bank_run, _outbound_removed = wicked_hood_skip_active_outbound_pure(bank_run)
    player_data["skilling_bank_run"] = bank_run
    if bank_run:
        return bank_run, None
    view = pack.repack()
    _set_carried_target_map(player_data, "carried_inventory", pack.target_id, view)
    _set_carried_target_map(player_data, "carried_churn", pack.target_id, 0)
    return bank_run, view


def _run_processing_tick(
    ctx: RuntimeActionContext,
    action_ctx: RuntimeActionContext,
    handler,
    pack: _TargetPack,
    new_state: dict[str, Any],
    new_view: dict[str, int],
    new_churn: int,
    *,
    winter_storage_before: dict[str, Any] | None,
    restore_cadence,
) -> bool:
    """Run a processing handler against the bank capped at what the pack holds.

    Scope the handler's input access to what the pack holds, run it, then
    reconcile: the real bank only loses what was actually consumed, and the
    pack is decremented by the same amount. Every other item (outputs,
    byproducts) passes through untouched, since it was never capped.
    """
    player_data = ctx.player_data
    bank = pack.bank
    carried_presence_requirements = pack.presence_requirements if pack.advanced else {}
    scoped_inventory, hidden_potions, hidden_alternatives = (
        _scope_processing_inventory(
            bank,
            new_view,
            pack.handler_key,
            pack.target_id,
            pack.requirements,
            carried_presence_requirements,
            pack.consumable_requirements,
        )
    )

    # While the inventory is scoped it does NOT reflect the real bank, so the
    # handler must not persist it or evaluate anything against it. Suppress the
    # handler's save, achievement check, and skill-availability refreshes for the
    # duration and fire them once afterwards against the reconciled bank.
    # Without this a save inside the handler writes the capped bank to disk,
    # achievements gated on a bank quantity see only what fits in the pack, and
    # the skill-availability UI is computed from the pack rather than the bank.
    # `deactivate_current_skill` is deliberately left live: it must still fire
    # when materials genuinely run out, and the bank-run gate already prevents
    # the handler from ever seeing an under-supplied pack.
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
        restore_cadence()
        ctx.save_player_data()
        return False
    after_scoped = player_data.get("inventory", {}) or {}
    new_view = _carried_target_view(player_data, pack.target_id)
    reconciled, new_view = _reconcile_processing_inventory(
        bank,
        scoped_inventory,
        after_scoped,
        new_view,
        (*pack.requirements, *carried_presence_requirements, *pack.consumable_requirements),
        hidden_potions,
        hidden_alternatives,
    )
    player_data["inventory"] = reconciled
    if result is not False:
        player_data["skilling_bank_run"] = new_state
        churn_delta = inventory_pure.carried_action_churn_pure(
            _without_urn_substitutions(bank),
            _without_urn_substitutions(reconciled),
            _OVERLAY_STACKABLE_NAMES,
        )
        _set_carried_target_map(player_data, "carried_inventory", pack.target_id, new_view)
        _set_carried_target_map(player_data, "carried_churn", pack.target_id, new_churn + churn_delta)
    # Always run against the true bank, even on a failed tick, so a suppressed
    # save can never leave the capped inventory as the last thing written.
    if deferred_achievement_check:
        ctx.check_achievements(player_data)
    if deferred_availability_refresh:
        ctx.refresh_skill_availability()
    if result is False:
        restore_cadence()
    ctx.save_player_data()
    return result


class _CadenceAdmission:
    """One review's live-cadence admission, undone if the review turns out ineligible."""

    def __init__(self, ctx: RuntimeActionContext, handler_key: str, target_id: str) -> None:
        self._ctx = ctx
        self._handler_key = handler_key
        self._target_id = target_id
        self.action_ctx = ctx
        self._admitted = False
        self._profiles_present = "cadence_profiles" in ctx.player_data
        self._profiles_before = copy.deepcopy(ctx.player_data.get("cadence_profiles"))
        self._profiles_after_admission = None

    def admit(self) -> bool:
        """Admit the review once; Magic and Prayer never wait on live cadence."""
        if self._admitted or self._handler_key in {"magic", "prayer"}:
            return True
        self.action_ctx, self._admitted = _admit_live_cadence(
            self._ctx, self._handler_key, self._target_id
        )
        if self._admitted:
            self._profiles_after_admission = copy.deepcopy(
                self._ctx.player_data.get("cadence_profiles")
            )
        return self._admitted

    def restore_after_rejection(self) -> None:
        player_data = self._ctx.player_data
        if not self._admitted:
            return
        if player_data.get("cadence_profiles") != self._profiles_after_admission:
            # A handler may own a second scheduler under the same route key
            # (Thieving stalls and wall safes). Once that scheduler advances,
            # the review was a real action attempt rather than an eligibility
            # rejection, so its cadence must survive an unsuccessful outcome.
            return
        if self._profiles_present:
            player_data["cadence_profiles"] = copy.deepcopy(self._profiles_before)
        else:
            player_data.pop("cadence_profiles", None)


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
        return _run_without_carried_overlay(ctx, handler_key, handler)

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
    view = dict((player_data.get("carried_inventory") or {}).get(target_id, {}))
    pack = _describe_target_pack(player_data, handler_key, target_id, view)
    is_agility = handler_key == "agility"
    # Keep/Drop is a gathering-only choice; processing always draws from (and
    # refills) its pack — there is no "drop the product" for a recipe's inputs.
    keep = True if pack.is_processing else inventory_pure.carried_keep_for(player_data, target_id)
    churn = (player_data.get("carried_churn") or {}).get(target_id, 0)
    bank_run = player_data.get("skilling_bank_run", {})
    manual_bank_run = (
        str(player_data.get("review_bank_run_requested_target", "") or "")
        == target_id
    )
    requested_target = player_data.get("skilling_bank_run_requested")
    skilling_bank_run_requested = requested_target == target_id
    bank_run_requested = manual_bank_run or skilling_bank_run_requested
    capacity = pack.capacity
    view = _prime_first_trip(player_data, pack, view)

    if is_agility and pack.advanced:
        missing = _agility_carried_requirement_gaps(player_data, target_id, view)
        if missing:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Agility pack incomplete",
                f"Custom mode must carry or equip {', '.join(missing)} for "
                f"{AGILITY_TARGETS_BY_ID[target_id].display_name}.",
            )
            return False

    force = bank_run_requested or (
        pack.is_processing
        and _processing_refill_due(
            view,
            pack.bank,
            pack.requirements,
            pack.consumable_requirements,
            pack.presence_requirements,
            advanced=pack.advanced,
        )
    )
    desired_agility_view = pack.repack() if is_agility else {}
    if desired_agility_view:
        force = force or any(
            int(view.get(item_name, 0) or 0) <= 0 and int(pack.bank.get(item_name, 0) or 0) > 0
            for item_name in desired_agility_view
        )

    target_altar = (
        str((RUNECRAFTING_DATA.get(target_id) or {}).get("altar_id", ""))
        if handler_key == "runecrafting"
        else ""
    )
    if target_altar:
        bank_run, restocked_view = _teleport_past_outbound_leg(player_data, pack, bank_run, target_altar)
        if restocked_view is not None:
            view, churn, force = restocked_view, 0, False

    active_run = isinstance(bank_run, dict) and int(bank_run.get("reviews_remaining", 0) or 0) > 0
    cadence = _CadenceAdmission(ctx, handler_key, target_id)
    if keep and not active_run and not cadence.admit():
        return True
    winter_storage_before = None
    if keep and not active_run and not bank_run_requested:
        winter_storage_before = copy.deepcopy(player_data)
        view, churn, winter_storage_used = _try_pack_yak_winter_storage_overlay(
            player_data,
            target_id,
            view,
            int(churn or 0),
            capacity,
            advanced=pack.advanced,
            force_bank=force,
        )
        if winter_storage_used:
            pack = dataclasses.replace(pack, bank=player_data.get("inventory", {}) or {})
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
    reviews_cost = inventory_pure.SKILLING_BANK_RUN_REVIEWS
    route_phases = ()
    outbound_teleport_used = False
    if active_run:
        reviews_cost = max(1, int(bank_run.get("reviews_total", bank_run.get("reviews_remaining", 1)) or 1))
    elif trip_due:
        travel_profile, reviews_cost, route_phases, outbound_teleport_used = (
            _initialize_due_bank_trip(ctx, handler_key, target_id, view, target_altar)
        )

    if trip_due and reviews_cost <= 0:
        new_state, new_view, new_churn = {}, {}, 0
        event = {"active": True, "started": True, "completed": True, "reviews_remaining": 0, "waived": True}
        act = True
        new_view = pack.repack()
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

    _settle_bank_run_requests(
        player_data,
        view,
        event,
        manual_bank_run=manual_bank_run,
        skilling_bank_run_requested=skilling_bank_run_requested,
    )

    if not act:
        cadence.restore_after_rejection()
        if event.get("completed"):
            new_view = pack.repack()
        _spend_review_on_bank_trip(
            ctx, target_id, bank_run, new_state, new_view, new_churn, event, reviews_cost
        )
        return True

    # Handlers that substitute carried items (urn runed -> active -> full) must
    # see the actual trip view, including a just-seeded first trip.
    _set_carried_target_map(player_data, "carried_inventory", target_id, new_view)
    if not cadence.admit():
        return True

    if pack.is_processing and pack.requirements:
        return _run_processing_tick(
            ctx,
            cadence.action_ctx,
            handler,
            pack,
            new_state,
            new_view,
            new_churn,
            winter_storage_before=winter_storage_before,
            restore_cadence=cadence.restore_after_rejection,
        )

    inv_before = dict(pack.bank)
    result = handler(cadence.action_ctx)
    if result is False and winter_storage_before is not None:
        player_data.clear()
        player_data.update(winter_storage_before)
        cadence.restore_after_rejection()
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
            overflow_items = _fold_keep_gains_and_write_carried(
                player_data, target_id, post_handler_view, gains,
                new_churn, churn_delta, capacity, evil_tree_overflow,
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
        cadence.restore_after_rejection()
    return result
