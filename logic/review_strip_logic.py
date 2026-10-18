"""What the always-visible reviewer strip shows, and when.

Design-thread section 4.8 settles the rule: the strip shows only what is live
right now. Every enable and visibility decision therefore lives in this module,
and ``ui.py`` renders the result without deciding anything.

The native row below Anki's answer bar contains:

* the running target's real experience bars. A shooting star trains Mining and an
  Evil Tree trains Woodcutting, so those are the bars the strip must show; the
  old overlay replaced them with an activity caption, which is the complaint
  that produced this contract.
* the Grand Exchange fills drawer, whose own view lives with the Grand Exchange
  state in ``grand_exchange_logic``.
* separate persistent Distractions and Farming badges, each with its own popover.
* the retained event-log drawer for floating XP, achievements, and activity
  results that disappear before the player can read them.
"""
from __future__ import annotations

from typing import Any, Callable, Collection, Mapping

from ..core.action_registry import (
    review_action_display_names,
    review_action_handler_key,
    review_handler_target_key,
)
from ..core.constants import (
    BIRD_NEST_OPEN_TABLES,
    COOKING_ITEM_IMAGES,
    DEFAULT_UTILITY_ACTIVITY,
    FAMILIARISATION_ACTIVITY_ID,
    MINING_PICKAXE_DATA,
    exp_table_for_skill,
    QUEST_UNLOCK_RULES,
    UTILITY_ACTIVITY_DATA,
    UTILITY_ITEM_IMAGES,
    WOODCUTTING_AXE_DATA,
)
from ..core.target_metadata import utility_activity_rows
from ..data.big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID
from ..data.bork_data import BORK_ACTIVITY_ID
from ..data.circus_data import CIRCUS_ACTIVITY_ID
from ..data.court_cases_data import COURT_CASES_ACTIVITY_ID
from ..data.enchanted_key_data import ENCHANTED_KEY_ACTIVITY_ID
from ..data.evil_tree_data import EVIL_TREE_UTILITY_ID
from ..data.fish_flingers_data import (
    FISH_FLINGERS_ACTIVITY_ID,
    FISH_FLINGERS_EVENT_CATCHES,
)
from ..data.fishing_trawler_data import FISHING_TRAWLER_ACTIVITY_ID
from ..data.goblin_raids_data import GOBLIN_RAIDS_ACTIVITY_ID
from ..data.gnome_ball_data import GNOME_BALL_ACTIVITY_ID
from ..data.great_orb_project_data import GREAT_ORB_PROJECT_ACTIVITY_ID
from ..data.livid_farm_data import LIVID_FARM_ACTIVITY_ID
from ..data.mage_training_arena_data import MAGE_TRAINING_ARENA_ACTIVITY_ID
from ..data.ranging_guild_data import RANGING_GUILD_ACTIVITY_ID
from ..data.managing_miscellania_data import MANAGING_MISCELLANIA_ACTIVITY_ID
from ..data.penguin_hide_and_seek_data import PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID
from ..data.phoenix_lair_data import PHOENIX_LAIR_ACTIVITY_ID
from ..data.pyramid_plunder_data import PYRAMID_PLUNDER_ACTIVITY_ID
from ..data.shattered_heart_data import SHATTERED_HEART_ACTIVITY_ID
from ..data.shooting_star_data import SHOOTING_STAR_ACTIVITY_ID
from ..data.skeletal_horror_data import SKELETAL_HORROR_ACTIVITY_ID
from ..data.sorceress_garden_data import SORCERESS_GARDEN_ACTIVITY_ID
from ..data.tears_of_guthix_data import TEARS_OF_GUTHIX_ACTIVITY_ID
from ..data.treasure_trails_data import TREASURE_TRAILS_ACTIVITY_ID
from ..data.troll_invasion_data import TROLL_INVASION_ACTIVITY_ID
from ..data.vinesweeper_data import VINESWEEPER_ACTIVITY_ID
from ..data.werewolf_skullball_data import WEREWOLF_SKULLBALL_ACTIVITY_ID
from ..logic.big_chinchompa_logic import big_chinchompa_view_pure
from ..logic.bork_logic import bork_view_pure
from ..logic.circus_logic import circus_view_pure
from ..logic.court_cases_logic import court_cases_view_pure
from ..logic.dnd_favourites_logic import (
    DND_ACTIVITY_IDS,
    dnd_activity_display_name_pure,
    sanitize_dnd_favourites_pure,
)
from ..logic.enchanted_key_logic import enchanted_key_view_pure
from ..logic.evil_tree_logic import evil_tree_view_pure
from ..logic.farming_logic import farming_frontend_projection_pure
from ..logic.fish_flingers_logic import fish_flingers_view_pure
from ..logic.goblin_raids_logic import goblin_raids_view_pure
from ..logic.penguin_hide_and_seek_logic import penguin_view_pure
from ..logic.phoenix_lair_logic import phoenix_lair_view_pure
from ..logic.shattered_heart_logic import shattered_heart_view_pure
from ..logic.shooting_star_logic import shooting_star_view_pure
from ..logic.skeletal_horror_logic import skeletal_horror_view_pure
from ..logic.summoning_logic import familiarisation_view_pure
from ..logic.tears_of_guthix_logic import reward_skill_pure, tears_of_guthix_view_pure
from ..logic.treasure_trails_logic import treasure_trails_view_pure
from ..logic.troll_invasion_logic import troll_invasion_view_pure
from ..logic.wicked_hood_logic import bank_run_phase_label_pure
from ..logic_pure.logic_pure import (
    COMBAT_BANK_RUN_REVIEWS,
    _non_negative_int,
    best_mining_pickaxe_pure,
    best_woodcutting_axe_pure,
    compute_level_progress,
    request_combat_bank_run_now_pure,
)

# A resolved Big Chinchompa keeps reporting its outcome for this many reviews.
WORLD_EVENT_OUTCOME_REVIEWS = 10

# The strip is one compact row. Two bars is the most it can hold without
# becoming the stacked rectangle section 4.8 exists to prevent; an activity that
# trains more names the rest in its caption instead.
MAX_STRIP_XP_BARS = 2

# The owner's retention answer (design-thread 4.15): weeks of history, flat
# save size. Oldest rows trim on write once the window is full.
REVIEW_EVENT_LOG_RETAINED = 2000

# The event drawer opens on the ten newest floating notifications and expands in
# ten-row pages without discarding older emissions.
REVIEW_EVENT_LOG_DEFAULT_LIMIT = 10
REVIEW_EVENT_LOG_PAGE_SIZE = 10

# The reviewer strip is a fixed native row below Anki's answer bar. Card
# content may change what it says, but never its seat or height.
REVIEW_STRIP_HEIGHT = 128
REVIEW_STRIP_WIDTH = 684
REVIEW_BANK_RUN_LABEL = "Bank run"
REVIEW_BANK_RUN_TOOLTIP = "Deposit inventory and restock same supplies"
SIMULATED_CLOCK_TOOLTIP = "10 cards = 1 hour"
SIMULATED_CLOCK_START_HOUR = 12

# These handlers refill a target-specific carried pack. Every other registered
# review action still gets the button and spends one review on the standard
# bank trip, but has no pack to repopulate.
REVIEW_CARRIED_BANK_RUN_HANDLER_KEYS = frozenset(
    {
        "mining",
        "woodcutting",
        "fishing",
        "hunter",
        "cooking",
        "crafting",
        "fletching",
        "firemaking",
        "smithing",
        "runecrafting",
        "herblore",
        "prayer",
        "thieving",
        "agility",
        "summoning",
    }
)
REVIEW_BANK_RUN_HANDLER_KEYS = frozenset(
    handler
    for name in review_action_display_names()
    if (handler := review_action_handler_key(name)) is not None
)


def _answered_reviews_pure(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    if not isinstance(clock, Mapping):
        return 0
    try:
        return max(0, int(clock.get("answered_cards", 0) or 0))
    except (TypeError, ValueError, OverflowError):
        return 0


def simulated_clock_text_pure(player_data: Mapping[str, Any]) -> str:
    hour = (SIMULATED_CLOCK_START_HOUR + _answered_reviews_pure(player_data) // 10) % 24
    suffix = "AM" if hour < 12 else "PM"
    display_hour = hour % 12 or 12
    return f"{display_hour}:00 {suffix}"


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


def review_event_log_drawer_view_pure(
    player_data: Mapping[str, Any],
    *,
    visible_limit: int = REVIEW_EVENT_LOG_DEFAULT_LIMIT,
    expanded: bool = False,
) -> dict[str, Any]:
    """Projection for the collapsed notification drawer, newest first."""

    rows = sanitize_review_event_log_pure(player_data.get("review_event_log"))
    try:
        limit = max(
            REVIEW_EVENT_LOG_DEFAULT_LIMIT,
            int(visible_limit or REVIEW_EVENT_LOG_DEFAULT_LIMIT),
        )
    except (TypeError, ValueError, OverflowError):
        limit = REVIEW_EVENT_LOG_DEFAULT_LIMIT
    now = _answered_reviews_pure(player_data)
    visible_rows = []
    for entry in reversed(rows[-limit:]):
        reviews_ago = max(0, now - int(entry["review"]))
        unit = "review" if reviews_ago == 1 else "reviews"
        # Green and yellow belong to the Grand Exchange drawer alone, so the
        # event log stays on neutral tones.
        tone = entry["kind"] if entry["kind"] in ("xp", "achievement") else "neutral"
        visible_rows.append({
            **entry,
            "label": f"{reviews_ago} {unit} ago · {entry['text']}",
            "tone": tone,
            "foreground": {
                "xp": "#d7dde8",
                "achievement": "#8fb8ff",
                "neutral": "#ffffff",
            }[tone],
        })
    remaining = max(0, len(rows) - len(visible_rows))
    next_count = min(REVIEW_EVENT_LOG_PAGE_SIZE, remaining)
    return {
        "visible": bool(rows),
        "title": f"Event log ({len(rows)})",
        "rows": tuple(visible_rows),
        "rows_visible": bool(expanded),
        "show_more_visible": bool(expanded and remaining),
        "show_more_enabled": remaining > 0,
        "show_more_text": f"Show {next_count} more" if next_count else "",
        "next_limit": limit + next_count,
        "retained_count": len(rows),
    }


def _text(player_data: Mapping[str, Any], key: str) -> str:
    return str(player_data.get(key, "") or "")


def _mapping(player_data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    raw = player_data.get(key)
    return raw if isinstance(raw, Mapping) else {}


def _carried_request_pending(player_data: Mapping[str, Any], handler: str) -> bool:
    """A carried request names one target; the runtime spends it only on that
    target's next review, so the HUD reads it the same way."""
    target = _text(player_data, review_handler_target_key(handler) or "")
    return bool(target) and target in (
        _text(player_data, "review_bank_run_requested_target"),
        _text(player_data, "skilling_bank_run_requested"),
    )


def review_bank_run_button_view_pure(
    player_data: Mapping[str, Any], handler_key: Any, target_id: Any = None
) -> dict[str, Any]:
    """Stable button content and availability for the fixed strip."""

    handler = str(handler_key or "")
    target = str(target_id or "")
    requested_target = _text(player_data, "review_bank_run_requested_target")
    if handler == "combat":
        active = bool(player_data.get("combat_bank_run"))
    elif handler in REVIEW_CARRIED_BANK_RUN_HANDLER_KEYS:
        active = bool(player_data.get("skilling_bank_run")) or bool(
            requested_target and (not target or requested_target == target)
        )
    else:
        active = bool(_text(player_data, "review_bank_run_requested_handler"))
    return {
        "visible": True,
        "text": REVIEW_BANK_RUN_LABEL,
        "enabled": handler in REVIEW_BANK_RUN_HANDLER_KEYS and not active,
        "tooltip": REVIEW_BANK_RUN_TOOLTIP,
    }


def review_bank_run_travel_view_pure(
    player_data: Mapping[str, Any], handler_key: Any
) -> dict[str, Any]:
    """Project the active review handler's bank run for the HUD strip."""

    handler = str(handler_key or "")
    requested_handler = _text(player_data, "review_bank_run_requested_handler")
    skilling_run = _mapping(player_data, "skilling_bank_run")
    if handler == "combat":
        combat_run = _mapping(player_data, "combat_bank_run")
        remaining = min(
            _non_negative_int(combat_run.get("reviews_remaining", 0)),
            COMBAT_BANK_RUN_REVIEWS,
        )
        queued = requested_handler == handler
    elif handler in REVIEW_CARRIED_BANK_RUN_HANDLER_KEYS:
        remaining = _non_negative_int(skilling_run.get("reviews_remaining", 0))
        queued = _carried_request_pending(player_data, handler)
    elif handler and requested_handler == handler:
        remaining, queued = 0, True
    else:
        return {"active": False, "queued": False}

    kind = "combat" if handler == "combat" else "carried"
    if remaining <= 0:
        if not queued:
            return {"active": False, "queued": False}
        return {
            "active": False,
            "queued": True,
            "kind": kind,
            "label": "Queued",
            "total": 0,
            "remaining": 0,
            "percent": 0,
            "text": "Bank run queued",
        }

    if kind == "combat":
        label, total = "Banking supplies", COMBAT_BANK_RUN_REVIEWS
    else:
        label = bank_run_phase_label_pure(skilling_run)
        total = max(remaining, _non_negative_int(skilling_run.get("reviews_total", 0)))
    done = min(total - remaining, total)
    return {
        "active": True,
        "queued": False,
        "kind": kind,
        "label": label,
        "total": total,
        "remaining": remaining,
        "percent": int(round(100.0 * done / total)),
        "text": f"Bank run — {label} · {done}/{total} travel reviews",
    }


def request_review_bank_run_pure(
    player_data: Mapping[str, Any], handler_key: Any, target_id: Any
) -> tuple[dict[str, Any], bool]:
    """Queue the existing review-paced bank-run path without completing it."""

    handler = str(handler_key or "")
    target = str(target_id or "")
    if handler not in REVIEW_BANK_RUN_HANDLER_KEYS:
        return dict(player_data), False
    updated = dict(player_data)
    if handler == "combat":
        requested, ok, _reason = request_combat_bank_run_now_pure(player_data)
        return requested, ok
    elif handler in REVIEW_CARRIED_BANK_RUN_HANDLER_KEYS:
        if (
            not target
            or player_data.get("skilling_bank_run")
            or player_data.get("review_bank_run_requested_target") == target
        ):
            return updated, False
        # The carried-overlay runtime converts this one thin request into its
        # ordinary target-specific travel profile on the next successful card.
        updated["review_bank_run_requested_target"] = target
    else:
        if player_data.get("review_bank_run_requested_handler"):
            return updated, False
        updated["review_bank_run_requested_handler"] = handler
    return updated, True


def _has_usable_hatchet(player_data: Mapping[str, Any]) -> bool:
    return (
        best_woodcutting_axe_pure(
            int(player_data.get("woodcutting_level", 1) or 1),
            player_data.get("inventory", {}) or {},
            player_data.get("toolbelt", {}) or {},
            WOODCUTTING_AXE_DATA,
        )
        is not None
    )


def _has_usable_pickaxe(player_data: Mapping[str, Any]) -> bool:
    return (
        best_mining_pickaxe_pure(
            int(player_data.get("mining_level", 1) or 1),
            player_data.get("inventory", {}) or {},
            player_data.get("toolbelt", {}) or {},
            MINING_PICKAXE_DATA,
        )
        is not None
    )


def _evil_tree_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = evil_tree_view_pure(
        player_data,
        has_usable_hatchet=_has_usable_hatchet(player_data),
    )
    rows = []
    if view["active"]:
        rows.append(
            f"{view['tier_name']} · {view['location']} · "
            f"{int(view['reviews_remaining'])} reviews left"
        )
    blessing = int(view.get("blessing_reviews_remaining", 0) or 0)
    if blessing > 0:
        rows.append(f"Evil Tree blessing · {blessing} reviews left")
    return tuple(rows)


def _shooting_star_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = shooting_star_view_pure(
        player_data,
        has_usable_pickaxe=_has_usable_pickaxe(player_data),
    )
    if view["active"]:
        return (
            f"Shooting Star size {int(view['current_size'])} · "
            f"{int(view['layer_remaining']):,} layer dust left · "
            f"{int(view['dust'])}/{int(view['dust_cap'])} stardust",
        )
    if view["sprite_available"]:
        return (
            "Star sprite ready to exchange · "
            f"{int(view['sprite_reviews_remaining'])} reviews left · "
            f"{int(view['dust'])} stardust",
        )
    return ()


def _big_chinchompa_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = big_chinchompa_view_pure(player_data)
    if view["active"]:
        return (
            "Big Chinchompa · "
            f"{int(view['minutes_remaining'])} source min left · "
            f"{int(view['fullness_percent'])}% full",
        )
    try:
        resolved_ago = int(view.get("resolved_reviews_ago", -1))
    except (TypeError, ValueError):
        resolved_ago = -1
    result = str(view.get("last_result", "") or "")
    return (
        (result,)
        if result and 0 <= resolved_ago < WORLD_EVENT_OUTCOME_REVIEWS
        else ()
    )


def _fish_flingers_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = fish_flingers_view_pure(player_data)
    if view["active"]:
        return (
            f"Review {int(view['catch_number'])}/{FISH_FLINGERS_EVENT_CATCHES} · "
            f"{view['location']} · {int(view['stock'])}/{int(view['stock_max'])} stock · "
            f"{int(view['tickets'])} tickets remaining",
        )
    tickets = int(view["tickets"])
    if tickets > 0:
        return (
            f"{tickets} Fish Flingers ticket{'s' if tickets != 1 else ''} available",
        )
    return ()


def _goblin_raids_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = goblin_raids_view_pure(player_data)
    if view["active"]:
        return (f"{view['stage_label']} · {view['summary_text']}",)
    if view["raid_announced"]:
        return (
            f"Raid at {view['raid_site']} · "
            f"{int(view['raid_reviews_remaining'])} reviews left",
        )
    return ()


def _tears_of_guthix_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = tears_of_guthix_view_pure(player_data)
    if view["active"]:
        return (
            f"{int(view['tears'])} tears · {int(view['remaining_beats'])} beats left · "
            f"rewarding {view['reward_skill']['display_name']}",
        )
    if view["entry_ready"]:
        return (
            f"Entry ready · {int(view['collection_ticks'])} collection ticks · "
            f"rewarding {view['reward_skill']['display_name']}",
        )
    return ()


def _circus_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = circus_view_pure(player_data)
    remaining = int(view["remaining_count"])
    return (
        (f"{remaining} weekly performance{'s' if remaining != 1 else ''} available",)
        if remaining > 0
        else ()
    )


def _bork_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = bork_view_pure(player_data)
    if view["active"]:
        return (
            f"Bork · {int(view['lifepoints']):,} LP · "
            f"{int(view['ork_count'])} ork{'s' if int(view['ork_count']) != 1 else ''}",
        )
    if view["requirements_met"] and view["daily_ready"]:
        return ("Daily Bork encounter ready",)
    return ()


def _court_cases_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = court_cases_view_pure(player_data)
    if view["active"]:
        return (f"{view['case_name']} · {view['progress']} · {view['current_beat']}",)
    if not view["locked_reasons"]:
        return (f"{view['case_name']} · {view['current_beat']}",)
    return ()


def _enchanted_key_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = enchanted_key_view_pure(player_data)
    if view["can_review"]:
        selected = view["selected"] or {}
        return (
            f"Searching {selected.get('display_name', 'selected site')} · "
            f"{int(view['remaining'])} sites remain",
        )
    if view["requirements_met"] and not view["complete"]:
        return (f"{int(view['remaining'])} treasure sites remain · choose a site",)
    return ()


def _familiarisation_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = familiarisation_view_pure(player_data)
    if view["active"]:
        return (
            f"{int(view['segments'])}/{int(view['max_segments'])} segments · "
            f"{int(view['raw_shards'])}/{int(view['shard_cap'])} shards",
        )
    if view["awaiting_reward"]:
        return (f"Reward ready · {int(view['raw_shards'])} raw shards",)
    if view["ready"]:
        return ("Session ready to start",)
    return ()


def _penguin_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = penguin_view_pure(player_data)
    remaining = int(view["roster_count"]) - int(view["spotted_count"])
    return (
        (f"{remaining} penguins unspotted this week · {int(view['points'])}/50 points",)
        if remaining > 0
        else ()
    )


def _phoenix_lair_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = phoenix_lair_view_pure(player_data)
    if view["active"]:
        phase = str(view["phase"]).replace("_", " ").title()
        detail = str(view["current_guardian"] or view["last_result"])
        return (f"{phase} · {detail}",)
    if view["requirements_met"] and view["daily_ready"]:
        return ("Daily Phoenix Lair run ready",)
    return ()


def _shattered_heart_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = shattered_heart_view_pure(player_data)
    statuses = []
    addable = len(view["addable_pair_ids"])
    if addable:
        statuses.append(
            f"{addable} complete rock pair{'s' if addable != 1 else ''} ready to place"
        )
    replicas = len(view["replica_pair_ids_ready"])
    if replicas:
        statuses.append(
            f"{replicas} replica pair{'s' if replicas != 1 else ''} ready to add"
        )
    return tuple(statuses)


def _skeletal_horror_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = skeletal_horror_view_pure(player_data)
    if view["active"]:
        return (
            f"Phase {int(view['phase_index']) + 1} · "
            f"{int(view['lifepoints']):,} LP · "
            f"{len(view['limbs_removed'])} limbs removed",
        )
    if view["requirements_met"] and view["entry_ready"]:
        return ("Weekly Skeletal Horror entry ready",)
    return ()


def _treasure_trails_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = treasure_trails_view_pure(player_data)
    step = view["step"]
    if view["active"] and step:
        return (
            f"Clue step {int(step['number'])}/{int(step['total'])} · {step['kind']}",
        )
    caskets = sum(int(row["held"]) for row in view["caskets"])
    if caskets:
        return (f"{caskets} clue casket{'s' if caskets != 1 else ''} ready to open",)
    startable = tuple(row for row in view["clue_rows"] if row["can_start_from_bank"])
    if startable:
        return (
            f"{len(startable)} clue scroll{'s' if len(startable) != 1 else ''} ready to start",
        )
    return ()


def _troll_invasion_notification_statuses(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    view = troll_invasion_view_pure(player_data)
    if view["active"]:
        return (f"{view['summary_text']} · {view['progress_format']}",)
    if view["can_enter"]:
        return (
            f"{view['status_label'].title()} · "
            f"{str(view['selected_mode']).replace('_', ' ').title()} route ready",
        )
    return ()


DND_NOTIFICATION_STATUS_PROJECTIONS: dict[
    str, Callable[[Mapping[str, Any]], tuple[str, ...]]
] = {
    BIG_CHINCHOMPA_UTILITY_ID: _big_chinchompa_notification_statuses,
    CIRCUS_ACTIVITY_ID: _circus_notification_statuses,
    BORK_ACTIVITY_ID: _bork_notification_statuses,
    COURT_CASES_ACTIVITY_ID: _court_cases_notification_statuses,
    ENCHANTED_KEY_ACTIVITY_ID: _enchanted_key_notification_statuses,
    EVIL_TREE_UTILITY_ID: _evil_tree_notification_statuses,
    FAMILIARISATION_ACTIVITY_ID: _familiarisation_notification_statuses,
    FISH_FLINGERS_ACTIVITY_ID: _fish_flingers_notification_statuses,
    GOBLIN_RAIDS_ACTIVITY_ID: _goblin_raids_notification_statuses,
    PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID: _penguin_notification_statuses,
    PHOENIX_LAIR_ACTIVITY_ID: _phoenix_lair_notification_statuses,
    SHATTERED_HEART_ACTIVITY_ID: _shattered_heart_notification_statuses,
    SHOOTING_STAR_ACTIVITY_ID: _shooting_star_notification_statuses,
    SKELETAL_HORROR_ACTIVITY_ID: _skeletal_horror_notification_statuses,
    TEARS_OF_GUTHIX_ACTIVITY_ID: _tears_of_guthix_notification_statuses,
    TREASURE_TRAILS_ACTIVITY_ID: _treasure_trails_notification_statuses,
    TROLL_INVASION_ACTIVITY_ID: _troll_invasion_notification_statuses,
}
DND_NOTIFICATION_ACTIVITY_IDS = frozenset(DND_NOTIFICATION_STATUS_PROJECTIONS)
if DND_NOTIFICATION_ACTIVITY_IDS != DND_ACTIVITY_IDS:
    raise RuntimeError("The D&D notification table must cover the complete catalog.")


def dnd_notification_rows_pure(
    player_data: Mapping[str, Any],
    *,
    activity_ids: Collection[str] | None = None,
) -> tuple[tuple[str, str], ...]:
    """Active or actionable status rows for the requested D&D catalog slice."""

    requested = (
        DND_NOTIFICATION_STATUS_PROJECTIONS
        if activity_ids is None
        else activity_ids
    )
    rows = []
    for activity_id in requested:
        projection = DND_NOTIFICATION_STATUS_PROJECTIONS.get(activity_id)
        if projection is None:
            continue
        rows.extend((activity_id, status) for status in projection(player_data))
    return tuple(rows)


def world_event_rows_pure(
    player_data: Mapping[str, Any], *, suppress_id: str = ""
) -> tuple[tuple[str, str], ...]:
    """The review-clock events shown in the Activities hub's live strip."""

    world_event_ids = (
        EVIL_TREE_UTILITY_ID,
        SHOOTING_STAR_ACTIVITY_ID,
        BIG_CHINCHOMPA_UTILITY_ID,
    )
    return dnd_notification_rows_pure(
        player_data,
        activity_ids=tuple(
            activity_id
            for activity_id in world_event_ids
            if activity_id != suppress_id
        ),
    )


# The three world-clock Distractions exist whether or not the player asked for
# them, so selecting one is not the same as being able to train it. Every other
# activity trains the moment it is the chosen target.
_WORLD_CLOCK_LIVENESS: dict[str, Callable[[Mapping[str, Any]], bool]] = {
    EVIL_TREE_UTILITY_ID: lambda data: bool(
        evil_tree_view_pure(
            data, has_usable_hatchet=_has_usable_hatchet(data)
        )["active"]
    ),
    SHOOTING_STAR_ACTIVITY_ID: lambda data: bool(
        shooting_star_view_pure(
            data, has_usable_pickaxe=_has_usable_pickaxe(data)
        )["active"]
    ),
    BIG_CHINCHOMPA_UTILITY_ID: lambda data: bool(
        big_chinchompa_view_pure(data)["active"]
    ),
}


def activity_awards_experience_now_pure(
    player_data: Mapping[str, Any], activity_id: Any
) -> bool:
    """Whether the next review on this activity can move a skill bar at all."""

    wanted = str(activity_id or "")
    if not wanted:
        return False
    session = player_data.get("activity_session")
    open_session = str(
        session.get("active_id", "") if isinstance(session, Mapping) else ""
    )
    if open_session and open_session != wanted:
        return False
    liveness = _WORLD_CLOCK_LIVENESS.get(wanted)
    return liveness(player_data) if liveness is not None else True


def skill_xp_bar_pure(
    player_data: Mapping[str, Any], skill: str
) -> dict[str, Any]:
    """One experience bar row for a real skill, as the strip renders it."""

    level = int(player_data.get(f"{skill.lower()}_level", 1) or 1)
    exp = float(player_data.get(f"{skill.lower()}_exp", 0) or 0)
    percent, remaining, target_level = compute_level_progress(
        level,
        exp,
        exp_table_for_skill(skill),
    )
    return {
        "skill": skill,
        "level": level,
        "percent": percent,
        "remaining": remaining,
        "target_level": target_level,
    }


# The skills each activity really trains, primary first, mirroring the award
# sites in runtime/runtime_actions_activities.py — no activity spec declares
# this, so the award call is the only source of truth. An activity absent from
# the table shows no bar, which is what every activity did before this contract.
#
# Deliberately absent: the combat activities, whose skills come from the attack
# style rather than the activity, and Court Cases, the Circus, Trouble Brewing,
# Shades of Mort'ton and Troll Invasion, which pick their skill from a reward
# table or a player choice at payout. Guessing at those would put a wrong bar on
# screen, which is worse than the empty row they render today.
ACTIVITY_TRAINED_SKILLS: dict[str, tuple[str, ...]] = {
    SHOOTING_STAR_ACTIVITY_ID: ("Mining",),          # :838
    BIG_CHINCHOMPA_UTILITY_ID: ("Hunter",),          # :753
    SORCERESS_GARDEN_ACTIVITY_ID: ("Farming", "Thieving"),  # :1256, :1259
    VINESWEEPER_ACTIVITY_ID: ("Hunter",),            # :1323
    PYRAMID_PLUNDER_ACTIVITY_ID: (
        "Thieving",
        "Strength",
        "Runecrafting",
    ),                                               # :1401-1411
    WEREWOLF_SKULLBALL_ACTIVITY_ID: ("Agility",),    # :1446
    GNOME_BALL_ACTIVITY_ID: ("Agility", "Ranged"),   # :1485, :1488
    FISH_FLINGERS_ACTIVITY_ID: ("Fishing",),         # :1535
    FISHING_TRAWLER_ACTIVITY_ID: ("Fishing",),       # :1576
    GREAT_ORB_PROJECT_ACTIVITY_ID: ("Runecrafting",),  # :1619
    MANAGING_MISCELLANIA_ACTIVITY_ID: ("Woodcutting",),  # :2437
    LIVID_FARM_ACTIVITY_ID: (
        "Magic",
        "Farming",
        "Construction",
        "Crafting",
        "Agility",
    ),                                               # livid_farm_logic.py:199-205
    MAGE_TRAINING_ARENA_ACTIVITY_ID: ("Magic",),     # mage_training_arena_logic.py:604-687
    RANGING_GUILD_ACTIVITY_ID: ("Ranged",),
    "warriors_guild_attack_dummy": ("Attack",),      # warriors_guild_logic.py:262-264
    "warriors_guild_catapult": ("Defence",),         # warriors_guild_logic.py:265-267
    "warriors_guild_keg_balance": ("Strength",),     # warriors_guild_logic.py:270-277
    "warriors_guild_shot_put": ("Strength",),        # warriors_guild_logic.py:268-269
}


def _evil_tree_trained_skills(player_data: Mapping[str, Any]) -> tuple[str, ...]:
    phase = str(
        evil_tree_view_pure(
            player_data, has_usable_hatchet=_has_usable_hatchet(player_data)
        ).get("phase", "")
        or ""
    )
    if phase == "nurture":
        return ("Farming",)
    if phase == "fell":
        return ("Woodcutting", "Firemaking")
    return ("Woodcutting",)


def _tears_of_guthix_trained_skills(
    player_data: Mapping[str, Any]
) -> tuple[str, ...]:
    return (str(reward_skill_pure(player_data)["display_name"]),)


# Two families pick their skill at award time instead of declaring it, so they
# answer for themselves: the Evil Tree by phase, Tears of Guthix by whichever
# trainable skill currently has the least experience.
_DYNAMIC_TRAINED_SKILLS: dict[
    str, Callable[[Mapping[str, Any]], tuple[str, ...]]
] = {
    EVIL_TREE_UTILITY_ID: _evil_tree_trained_skills,
    TEARS_OF_GUTHIX_ACTIVITY_ID: _tears_of_guthix_trained_skills,
}


def activity_trained_skills_pure(
    player_data: Mapping[str, Any], activity_id: Any
) -> tuple[str, ...]:
    """The real skills one activity awards experience in, primary first."""

    wanted = str(activity_id or "")
    dynamic = _DYNAMIC_TRAINED_SKILLS.get(wanted)
    if dynamic is not None:
        return dynamic(player_data)
    return ACTIVITY_TRAINED_SKILLS.get(wanted, ())


def activity_xp_bars_pure(
    player_data: Mapping[str, Any], activity_id: Any
) -> dict[str, Any]:
    """The real skill bars for one running activity, plus the skills left over.

    ``bars`` is empty whenever the activity cannot award experience on the next
    review, which is how a finished shooting star takes its Mining bar away.
    """

    trained = activity_trained_skills_pure(player_data, activity_id)
    if not trained or not activity_awards_experience_now_pure(
        player_data, activity_id
    ):
        return {"bars": (), "also_trains": ()}
    return {
        "bars": tuple(
            skill_xp_bar_pure(player_data, skill)
            for skill in trained[:MAX_STRIP_XP_BARS]
        ),
        "also_trains": tuple(trained[MAX_STRIP_XP_BARS:]),
    }


def _quiet_favourite_status_pure(row: Any) -> str:
    """One line of status for a watched Distraction with no live event.

    ``utility_activity_rows`` is the only cross-family signal that exists today:
    every other status is bespoke per family. It answers "can I go and do this
    right now", which is what a watch list is for, and the popover line opens the
    activity's own surface for everything past that.
    """

    if row is None:
        return "Nothing live right now"
    if row.locked_reasons:
        return str(row.locked_reasons[0])
    if row.current:
        return "Selected as your review target"
    return "Ready — nothing live"


def review_status_badges_view_pure(
    player_data: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    """Separate persistent D&D and Farming badge projections.

    Pass 4 overrules the merged seat. Both badges remain to the left of the XP
    area, but each owns only its own rows, count, tooltip and navigation surface.
    """

    favourites = sanitize_dnd_favourites_pure(player_data.get("dnd_favourites"))
    live_by_id: dict[str, list[str]] = {}
    if favourites:
        for activity_id, text in dnd_notification_rows_pure(
            player_data, activity_ids=favourites
        ):
            live_by_id.setdefault(activity_id, []).append(text)
    metadata_favourites = [
        activity_id for activity_id in favourites if activity_id not in live_by_id
    ]
    rows_by_id: dict[str, Any] = (
        {
            row.target_id: row
            for row in utility_activity_rows(
                player_data,
                UTILITY_ACTIVITY_DATA,
                {**UTILITY_ITEM_IMAGES, **COOKING_ITEM_IMAGES},
                BIRD_NEST_OPEN_TABLES,
                DEFAULT_UTILITY_ACTIVITY,
                QUEST_UNLOCK_RULES,
            )
        }
        if metadata_favourites
        else {}
    )

    distraction_rows: list[dict[str, Any]] = []
    for activity_id in favourites:
        statuses = live_by_id.get(activity_id) or [
            _quiet_favourite_status_pure(rows_by_id.get(activity_id))
        ]
        for text in statuses:
            distraction_rows.append({
                "activity_id": activity_id,
                "name": dnd_activity_display_name_pure(activity_id),
                "status": text,
                "live": activity_id in live_by_id,
                "favourite": True,
            })
    distraction_count = sum(1 for row in distraction_rows if row["live"])
    empty_dnd_text = "Notification set is empty. Right-click any D&D to add it."
    distraction_tooltip = "\n".join(
        f"{row['name']} · {row['status']}" for row in distraction_rows
    ) or empty_dnd_text

    farming = farming_frontend_projection_pure(player_data)
    farming_rows: list[dict[str, Any]] = []
    for crop_row in farming.get("compact_rows", ()):
        farming_rows.append({
            "patch_id": str(crop_row["patch_id"]),
            "name": str(crop_row["crop_name"]),
            "status": f"{crop_row['status_label']} · {crop_row['patch_name']}",
            "live": str(crop_row["status"]) in {"ready", "diseased", "dead"},
        })
    hud = farming.get("hud", farming)
    queued = int(hud.get("queue_count", hud.get("queued_count", 0)) or 0)
    farming_count = sum(1 for row in farming_rows if row["live"])
    farming_tooltip_lines = [
        f"{row['name']} · {row['status']}" for row in farming_rows
    ]
    if queued:
        farming_tooltip_lines.append(f"{queued} Farming steps queued")

    return {
        "distractions": {
            "visible": True,
            "title": "D&D",
            "rows": tuple(distraction_rows),
            "count": distraction_count,
            "count_visible": distraction_count > 0,
            "alert": False,
            "queued_count": 0,
            "queue_visible": False,
            "tooltip": distraction_tooltip,
            "empty_text": empty_dnd_text,
            "open_full_visible": False,
        },
        "farming": {
            "visible": True,
            "title": "Farming",
            "rows": tuple(farming_rows),
            "count": farming_count,
            "count_visible": farming_count > 0,
            # A diseased or dead crop needs the player rather than merely
            # informing them, so the Farming count keeps the old "!" form.
            "alert": int(hud.get("urgent_count", 0) or 0) > 0,
            "queued_count": queued,
            "queue_visible": queued > 0,
            "tooltip": "\n".join(farming_tooltip_lines)
            or "No crops need attention.",
            "empty_text": "No crops need attention.",
            "open_full_visible": True,
        },
    }
