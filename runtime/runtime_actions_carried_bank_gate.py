"""The carried overlay's pre-action bank-gate translation for one skilling review."""

from __future__ import annotations

from typing import Any

from ..logic import inventory_pure
from ..logic.agility_travel import AgilityTravelProfile
from .runtime_actions_carried_requirements import _OVERLAY_STACKABLE_NAMES, _TargetPack


def _carried_bank_gate_transition(
    pack: _TargetPack,
    view: dict[str, int],
    churn: int,
    keep: bool,
    bank_run_requested: bool,
    capacity: int,
    force: bool,
    bank_run: Any,
    target_id: str,
    evil_tree_overflow: bool,
    active_run: bool,
    reviews_cost: int,
    trip_due: bool,
    travel_profile: AgilityTravelProfile | None,
    route_phases: tuple[dict[str, Any], ...],
    outbound_teleport_used: bool,
) -> tuple[dict[str, Any], dict[str, int], int, dict[str, Any], bool]:
    """Preserve gate objects when a new trip needs route metadata."""
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
        _carried_bank_gate_started_route_metadata(
            new_state, event, reviews_cost, travel_profile, route_phases, outbound_teleport_used
        )
    return new_state, new_view, new_churn, event, act


def _carried_bank_gate_started_route_metadata(
    new_state: dict[str, Any],
    event: dict[str, Any],
    reviews_cost: int,
    travel_profile: AgilityTravelProfile | None,
    route_phases: tuple[dict[str, Any], ...],
    outbound_teleport_used: bool,
) -> None:
    """Record the started trip's route metadata on the gate's new state."""
    if event.get("started") and new_state:
        new_state["reviews_total"] = max(1, reviews_cost)
        new_state["route_label"] = travel_profile.route_label if travel_profile else "Running to the bank"
        if route_phases:
            new_state["route_phases"] = list(route_phases)
        if outbound_teleport_used:
            new_state["outbound_teleport_used"] = True