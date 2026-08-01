"""What the always-visible reviewer strip shows, and when.

Design-thread section 4.8 settles the rule: the strip shows only what is live
right now. Every enable and visibility decision therefore lives in this module,
and ``ui.py`` renders the result without deciding anything.

The cluster below or beside the review card contains:

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

from typing import Any, Callable, Mapping

from ..core.constants import (
    BIRD_NEST_OPEN_TABLES,
    COOKING_ITEM_IMAGES,
    DEFAULT_UTILITY_ACTIVITY,
    MINING_PICKAXE_DATA,
    exp_table_for_skill,
    QUEST_UNLOCK_RULES,
    UTILITY_ACTIVITY_DATA,
    UTILITY_ITEM_IMAGES,
    WOODCUTTING_AXE_DATA,
)
from ..core.target_metadata import utility_activity_rows
from ..data.big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID
from ..data.evil_tree_data import EVIL_TREE_UTILITY_ID
from ..data.fish_flingers_data import FISH_FLINGERS_ACTIVITY_ID
from ..data.fishing_trawler_data import FISHING_TRAWLER_ACTIVITY_ID
from ..data.gnome_ball_data import GNOME_BALL_ACTIVITY_ID
from ..data.great_orb_project_data import GREAT_ORB_PROJECT_ACTIVITY_ID
from ..data.livid_farm_data import LIVID_FARM_ACTIVITY_ID
from ..data.mage_training_arena_data import MAGE_TRAINING_ARENA_ACTIVITY_ID
from ..data.managing_miscellania_data import MANAGING_MISCELLANIA_ACTIVITY_ID
from ..data.pyramid_plunder_data import PYRAMID_PLUNDER_ACTIVITY_ID
from ..data.shooting_star_data import SHOOTING_STAR_ACTIVITY_ID
from ..data.sorceress_garden_data import SORCERESS_GARDEN_ACTIVITY_ID
from ..data.tears_of_guthix_data import TEARS_OF_GUTHIX_ACTIVITY_ID
from ..data.vinesweeper_data import VINESWEEPER_ACTIVITY_ID
from ..data.werewolf_skullball_data import WEREWOLF_SKULLBALL_ACTIVITY_ID
from ..logic.big_chinchompa_logic import big_chinchompa_view_pure
from ..logic.dnd_favourites_logic import (
    dnd_activity_display_name_pure,
    sanitize_dnd_favourites_pure,
)
from ..logic.evil_tree_logic import evil_tree_view_pure
from ..logic.farming_logic import farming_frontend_projection_pure
from ..logic.shooting_star_logic import shooting_star_view_pure
from ..logic.tears_of_guthix_logic import reward_skill_pure
from ..logic_pure.logic_pure import (
    best_mining_pickaxe_pure,
    best_woodcutting_axe_pure,
    compute_level_progress,
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


def _answered_reviews_pure(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    if not isinstance(clock, Mapping):
        return 0
    try:
        return max(0, int(clock.get("answered_cards", 0) or 0))
    except (TypeError, ValueError, OverflowError):
        return 0


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
        visible_rows.append({
            **entry,
            "label": f"{reviews_ago} {unit} ago · {entry['text']}",
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


def review_overlay_layout_view_pure(
    *,
    parent_size: tuple[int, int],
    content_rect: tuple[int, int, int, int] | None,
    cluster_size: tuple[int, int],
    margin: int = 8,
    gap: int = 20,
) -> dict[str, Any]:
    """Choose a card-safe dock for the complete reviewer-overlay cluster.

    The card viewport owns its rectangle. The cluster first tries the space below
    it, then either side, then above. If no outside rectangle can hold the compact
    cluster, the pure projection hides it instead of letting UI heuristics cover
    card material.
    """

    parent_w = max(0, int(parent_size[0]))
    parent_h = max(0, int(parent_size[1]))
    cluster_w = max(0, int(cluster_size[0]))
    cluster_h = max(0, int(cluster_size[1]))
    if cluster_w <= 0 or cluster_h <= 0:
        return {"visible": False, "x": margin, "y": margin, "dock": "none"}
    if content_rect is None:
        return {
            "visible": cluster_w <= parent_w - 2 * margin and cluster_h <= parent_h - 2 * margin,
            "x": max(margin, (parent_w - cluster_w) // 2),
            "y": max(margin, parent_h - cluster_h - 72),
            "dock": "review-bottom",
        }

    cx, cy, cw, ch = (int(value) for value in content_rect)
    content_left = max(0, cx)
    content_top = max(0, cy)
    content_right = min(parent_w, cx + max(0, cw))
    content_bottom = min(parent_h, cy + max(0, ch))
    candidates = (
        (
            "below",
            margin,
            content_bottom + gap,
            parent_w - 2 * margin,
            parent_h - content_bottom - gap - margin,
        ),
        (
            "right",
            content_right + gap,
            margin,
            parent_w - content_right - gap - margin,
            parent_h - 2 * margin,
        ),
        (
            "left",
            margin,
            margin,
            content_left - gap - margin,
            parent_h - 2 * margin,
        ),
        (
            "above",
            margin,
            margin,
            parent_w - 2 * margin,
            content_top - gap - margin,
        ),
    )
    for dock, zx, zy, zw, zh in candidates:
        if cluster_w <= max(0, zw) and cluster_h <= max(0, zh):
            return {
                "visible": True,
                "x": zx + max(0, (zw - cluster_w) // 2),
                "y": zy + max(0, (zh - cluster_h) // 2),
                "dock": dock,
            }
    # A scrolling card fills the viewport, so no outside rectangle exists —
    # but the bars must never vanish (2026-07-29 playtest). The cluster docks
    # over the viewport bottom and the UI injects matching bottom padding into
    # the card document, so every line, footnotes included, can scroll clear.
    return {
        "visible": True,
        "x": max(margin, (parent_w - cluster_w) // 2),
        "y": max(margin, parent_h - cluster_h - margin),
        "dock": "overlay-bottom",
    }


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


def world_event_rows_pure(
    player_data: Mapping[str, Any], *, suppress_id: str = ""
) -> tuple[tuple[str, str], ...]:
    """(activity_id, one-line summary) for every live review-clock world event.

    Shared by the Activities hub's "Live world events" strip and the reviewer
    badge so the two can never drift. Only the three events that spawn on the
    review clock without the player asking belong here; player-started sessions
    such as Fist of Guthix already have their own counters. The activity id rides
    along so a badge click can open that event's card.
    """
    rows: list[tuple[str, str]] = []
    if suppress_id != EVIL_TREE_UTILITY_ID:
        evil_view = evil_tree_view_pure(
            player_data,
            has_usable_hatchet=_has_usable_hatchet(player_data),
        )
        if evil_view["active"]:
            rows.append((
                EVIL_TREE_UTILITY_ID,
                f"{evil_view['tier_name']} · "
                f"{evil_view['location']} · "
                f"{int(evil_view['reviews_remaining'])} reviews left",
            ))
        blessing = int(evil_view.get("blessing_reviews_remaining", 0) or 0)
        if blessing > 0:
            rows.append((
                EVIL_TREE_UTILITY_ID,
                f"Evil Tree blessing · {blessing} reviews left",
            ))
    if suppress_id != SHOOTING_STAR_ACTIVITY_ID:
        star = shooting_star_view_pure(
            player_data,
            has_usable_pickaxe=_has_usable_pickaxe(player_data),
        )
        if star["active"]:
            rows.append((
                SHOOTING_STAR_ACTIVITY_ID,
                f"Shooting Star size {int(star['current_size'])} · "
                f"{int(star['layer_remaining']):,} layer dust left · "
                f"{int(star['dust'])}/{int(star['dust_cap'])} stardust",
            ))
        elif star["sprite_available"]:
            rows.append((
                SHOOTING_STAR_ACTIVITY_ID,
                "Star sprite ready to exchange · "
                f"{int(star['sprite_reviews_remaining'])} reviews left · "
                f"{int(star['dust'])} stardust",
            ))
    if suppress_id != BIG_CHINCHOMPA_UTILITY_ID:
        big = big_chinchompa_view_pure(player_data)
        if big["active"]:
            rows.append((
                BIG_CHINCHOMPA_UTILITY_ID,
                f"Big Chinchompa · "
                f"{int(big['minutes_remaining'])} source min left · "
                f"{int(big['fullness_percent'])}% full",
            ))
        else:
            # No `or -1` fallback here: the resolution card itself reports 0,
            # which is falsy, so that idiom silently swallowed the one review
            # where the outcome matters most.
            try:
                resolved_ago = int(big.get("resolved_reviews_ago", -1))
            except (TypeError, ValueError):
                resolved_ago = -1
            result = str(big.get("last_result", "") or "")
            if result and 0 <= resolved_ago < WORLD_EVENT_OUTCOME_REVIEWS:
                rows.append((BIG_CHINCHOMPA_UTILITY_ID, result))
    return tuple(rows)


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
        for activity_id, text in world_event_rows_pure(player_data):
            if activity_id in favourites:
                live_by_id.setdefault(activity_id, []).append(text)
    session = player_data.get("activity_session")
    active_session_id = str(
        session.get("active_id", "") if isinstance(session, Mapping) else ""
    )
    metadata_favourites = [
        activity_id
        for activity_id in favourites
        if activity_id not in live_by_id and activity_id != active_session_id
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
        session_active = active_session_id == activity_id
        statuses = live_by_id.get(activity_id) or [
            "Active session"
            if session_active
            else _quiet_favourite_status_pure(rows_by_id.get(activity_id))
        ]
        for text in statuses:
            distraction_rows.append({
                "activity_id": activity_id,
                "name": dnd_activity_display_name_pure(activity_id),
                "status": text,
                "live": activity_id in live_by_id or session_active,
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
