"""The retained event log behind every floating review notification.

Floating XP, achievements and activity results disappear before the player can
read them, so each one is also written to the save here; the reviewer strip's
drawer lists them.
"""
from __future__ import annotations

from typing import Any, Mapping

from ..logic.pace.world_clock import answered_cards_pure as _answered_reviews_pure

# The owner's retention answer (design-thread 4.15): weeks of history, flat
# save size. Oldest rows trim on write once the window is full.
REVIEW_EVENT_LOG_RETAINED = 2000


def sanitize_review_event_log_pure(value: Any) -> list[dict[str, Any]]:
    """Normalize the retained floating-notification history, oldest first."""

    if not isinstance(value, (list, tuple)):
        return []
    rows: list[dict[str, Any]] = []
    for raw in value:
        if not isinstance(raw, Mapping):
            continue
        text = str(raw.get("text", "") or "").strip()
        if not text:
            continue
        try:
            review = max(0, int(raw.get("review", 0) or 0))
        except (TypeError, ValueError, OverflowError):
            review = 0
        kind = str(raw.get("kind", "activity") or "activity")[:32]
        rows.append({"review": review, "kind": kind, "text": text[:500]})
    return rows


def record_review_event_pure(
    player_data: Mapping[str, Any], kind: str, text: str
) -> dict[str, Any]:
    """Append one emitted floating notification through the shared save seam."""

    message = str(text or "").strip()
    if not message:
        return dict(player_data)
    updated = dict(player_data)
    rows = sanitize_review_event_log_pure(player_data.get("review_event_log"))
    rows.append({
        "review": _answered_reviews_pure(player_data),
        "kind": str(kind or "activity")[:32],
        "text": message[:500],
    })
    # 4.15 answer 2: the drawer expands through everything retained, but the
    # save keeps a large bounded window rather than growing forever.
    updated["review_event_log"] = rows[-REVIEW_EVENT_LOG_RETAINED:]
    return updated
