"""How a carried bank trip settles its arrival: the requests the trip answers,
and a Wicked hood altar teleport that skips the outbound leg and settles the
trip as a walked arrival does."""

from __future__ import annotations

import dataclasses

from typing import Any

from ..logic.summoning_logic import restore_summoning_points_pure
from ..logic.wicked_hood_logic import (
    consume_wicked_hood_route_teleport_pure,
    wicked_hood_skip_active_outbound_pure,
)
from ..logic_pure.achievement_diary_events import (
    record_bank_run_diary_event_pure,
    run_bank_run_diary_callbacks_pure,
)
from .runtime_actions_carried_requirements import _TargetPack, _set_carried_target_map
from .runtime_actions_context import RuntimeActionContext


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
        player_data.update(restore_summoning_points_pure(player_data)[0])
        record_bank_run_diary_event_pure(player_data, True, view)


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


def _settle_teleport_arrival(
    ctx: RuntimeActionContext,
    pack: _TargetPack,
    view: dict[str, int],
    *,
    manual_bank_run: bool,
    skilling_bank_run_requested: bool,
) -> _TargetPack:
    """Settle a trip the teleport finished as a walked arrival does, from the carried-in ``view``."""
    player_data = ctx.player_data
    _settle_bank_run_requests(
        player_data, view, {"active": True, "completed": True},
        manual_bank_run=manual_bank_run, skilling_bank_run_requested=skilling_bank_run_requested,
    )
    run_bank_run_diary_callbacks_pure(True, player_data, ctx.refresh_carried_inventory, ctx.check_achievements)
    # Saved before the review acts, so a held or rejected action keeps the arrival.
    ctx.save_player_data()
    # Diary rewards replace the bank dict, and the handler's gains are measured against the pack's bank.
    return dataclasses.replace(pack, bank=player_data.get("inventory", {}) or {})
