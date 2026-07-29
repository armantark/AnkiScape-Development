"""Which Distractions and Diversions the reviewer badge watches.

The badge is the player's notification system, so the watch list is player state
rather than a setting: ``dnd_favourites`` holds Distraction-and-Diversion
activity ids in the order the player pinned them. The primary toggle is the
Activities-tree row's context menu; the detail-card star remains as a second route.
Both commit through ``commit_direct_action`` like every other policy command.

A favourite never hides a live event. It adds a permanent line to the badge
popover so an idle Distraction can still be watched; see design-thread-queue
section 3.15.
"""
from __future__ import annotations

from typing import Any, Mapping

from ..core.constants import UTILITY_ACTIVITY_DATA
from ..data.evil_tree_data import EVIL_TREE_UTILITY_ID

DND_ACTIVITY_GROUP = "distractions_and_diversions"

# The Evil Tree is a Distraction with no UTILITY_ACTIVITY_DATA spec — it is one
# of ui.py's special activity targets — so the group scan below cannot see it,
# and it is one of the two events the owner named when he asked for this badge.
_UNREGISTERED_DND_NAMES = {EVIL_TREE_UTILITY_ID: "Evil Tree"}

DND_ACTIVITY_IDS = frozenset(
    activity_id
    for activity_id, spec in UTILITY_ACTIVITY_DATA.items()
    if str(spec.get("group", "")) == DND_ACTIVITY_GROUP
) | frozenset(_UNREGISTERED_DND_NAMES)


def dnd_activity_display_name_pure(activity_id: str) -> str:
    spec = UTILITY_ACTIVITY_DATA.get(str(activity_id), {})
    return str(
        spec.get("display_name", "")
        or _UNREGISTERED_DND_NAMES.get(str(activity_id), "")
        or activity_id
    )


def sanitize_dnd_favourites_pure(raw: Any) -> list[str]:
    """Keep known Distraction ids only, deduplicated, in pin order.

    Membership plus deduplication is the whole bound: the list can never grow
    past the number of Distractions that exist, so no separate cap is needed.
    """

    if not isinstance(raw, (list, tuple)):
        return []
    favourites: list[str] = []
    for value in raw:
        activity_id = str(value or "").strip()
        if activity_id in DND_ACTIVITY_IDS and activity_id not in favourites:
            favourites.append(activity_id)
    return favourites


def is_dnd_favourite_pure(player_data: Mapping[str, Any], activity_id: Any) -> bool:
    return str(activity_id or "") in sanitize_dnd_favourites_pure(
        player_data.get("dnd_favourites")
    )


def dnd_favourite_context_menu_view_pure(
    player_data: Mapping[str, Any], activity_id: Any, *, can_toggle: bool = True
) -> dict[str, Any]:
    """Project the one row action; non-Distractions have no menu entry."""

    target = str(activity_id or "")
    visible = target in DND_ACTIVITY_IDS
    pinned = visible and is_dnd_favourite_pure(player_data, target)
    return {
        "visible": visible,
        "enabled": visible and bool(can_toggle),
        "label": "Remove from notifications" if pinned else "Add to notifications",
    }


def dnd_favourite_detail_button_view_pure(
    player_data: Mapping[str, Any],
    activity_id: Any,
    *,
    show_detail: bool,
    can_toggle: bool = True,
) -> dict[str, Any]:
    """Project the retained detail-card star without UI-side policy."""

    target = str(activity_id or "")
    visible = bool(show_detail) and target in DND_ACTIVITY_IDS
    pinned = visible and is_dnd_favourite_pure(player_data, target)
    hint = (
        "Stop watching this Distraction on the reviewer badge"
        if pinned
        else "Watch this Distraction on the reviewer badge"
    )
    return {
        "visible": visible,
        "enabled": visible and bool(can_toggle),
        "text": "★" if pinned else "☆",
        "tooltip": hint,
    }


def toggle_dnd_favourite_pure(
    player_data: Mapping[str, Any], activity_id: Any
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Add or remove one badge line. The same click both pins and unpins."""

    data = dict(player_data)
    wanted = str(activity_id or "").strip()
    if wanted not in DND_ACTIVITY_IDS:
        return data, False, {"reason": "That activity has no Distractions badge line."}
    favourites = sanitize_dnd_favourites_pure(data.get("dnd_favourites"))
    name = dnd_activity_display_name_pure(wanted)
    if wanted in favourites:
        favourites.remove(wanted)
        message = f"{name} removed from the reviewer badge."
    else:
        favourites.append(wanted)
        message = f"{name} added to the reviewer badge."
    data["dnd_favourites"] = favourites
    return data, True, {"message": message, "favourite": wanted in favourites}
